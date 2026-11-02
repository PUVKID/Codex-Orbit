"""네트워크로 대략적인 지역과 현재 기온을 비동기 조회합니다."""
import json
import math
import re
import time
from collections import OrderedDict
from urllib.parse import urlencode

from PySide6.QtCore import QObject, QTimer, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest


# 행정안전부 시도 안내의 영문 표기와 공식 한글 지명을 대응합니다.
# 출처: https://www.mois.go.kr/eng/sub/a03/citiesProvinces/screen.do
_KOREAN_REGIONS = {
    'seoul': '서울특별시', 'busan': '부산광역시', 'daegu': '대구광역시',
    'incheon': '인천광역시', 'gwangju': '광주광역시', 'daejeon': '대전광역시',
    'ulsan': '울산광역시', 'sejong': '세종특별자치시', 'gyeonggi': '경기도',
    'gangwon': '강원특별자치도', 'chungcheongbuk': '충청북도', 'chungcheongnam': '충청남도',
    'jeollabuk': '전북특별자치도', 'jeonbuk': '전북특별자치도', 'jeollanam': '전라남도',
    'gyeongsangbuk': '경상북도', 'gyeongsangnam': '경상남도', 'jeju': '제주특별자치도',
}
_COUNTRIES = {'US': '미국', 'JP': '일본', 'CN': '중국', 'GB': '영국', 'DE': '독일',
              'FR': '프랑스', 'CA': '캐나다', 'AU': '호주', 'SG': '싱가포르', 'TW': '대만'}


def localized_region(data, language='ko'):
    """검색 전 임시 표시에는 검증된 국내 사전 또는 실제 원문 지명을 사용합니다."""
    if language not in ('ko', 'en'):
        raise ValueError('지원 언어는 ko 또는 en입니다.')
    def clean(value):
        return ''.join(c for c in value if c.isprintable()).strip()[:80] if isinstance(value, str) else ''
    city, region, country = clean(data.get('city')), clean(data.get('region')), clean(data.get('country'))
    original = ' · '.join(dict.fromkeys(v for v in (city, region, country) if v))
    code = clean(data.get('country_code')).upper()
    if not original:
        return ('위치 정보 없음' if language == 'ko' else 'Location unavailable'), ''
    if language == 'en':
        return original, original
    if code and code != 'KR':
        label = ' · '.join(dict.fromkeys(v for v in (city, region, _COUNTRIES.get(code, country)) if v))
        return label or original, original
    def korean(value, is_city=False):
        if re.search('[가-힣]', value):
            return value
        if code != 'KR':
            return ''
        key = value.casefold()
        for suffix in (' special self-governing province', ' special self-governing city',
                       ' metropolitan city', ' province', ' special city', '-do', '-si'):
            key = key.removesuffix(suffix)
        if is_city and key == 'suwon':
            return '수원시'
        if is_city and key == 'gwangju':
            # 동명 도시이므로 확인된 시도 없이 광주광역시로 확정하지 않습니다.
            confirmed_region = korean(region)
            if confirmed_region == '경기도':
                return '광주시'
            if confirmed_region == '광주광역시':
                return '광주광역시'
            return ''
        return _KOREAN_REGIONS.get(key, '')
    label = ' · '.join(dict.fromkeys(v for v in (korean(region) or region, korean(city, True) or city, country) if v))
    return label or original, original


def select_geocoded_region(location, data):
    """동일 국가이면서 IP 추정 좌표에서30km 이내인 가장 가까운 검색 결과만 수락합니다."""
    rows = data.get('results')
    if not isinstance(rows, list) or len(rows) > 10:
        return None
    code = location.get('country_code', '')
    if not isinstance(code, str) or not re.fullmatch('[A-Z]{2}', code):
        return None
    def valid(value, low, high):
        return type(value) in (int, float) and low <= value <= high and math.isfinite(value)
    latitude, longitude = location.get('latitude'), location.get('longitude')
    if not valid(latitude, -90, 90) or not valid(longitude, -180, 180):
        return None
    closest = None
    for row in rows:
        if not isinstance(row, dict) or row.get('country_code') != code:
            continue
        lat, lon = row.get('latitude'), row.get('longitude')
        name = row.get('name')
        if not isinstance(name, str) or not name.strip() or not valid(lat, -90, 90) or not valid(lon, -180, 180):
            continue
        delta_lat, delta_lon = math.radians(lat-latitude), math.radians(lon-longitude)
        arc = math.sin(delta_lat/2)**2 + math.cos(math.radians(lat))*math.cos(math.radians(latitude))*math.sin(delta_lon/2)**2
        distance = 6371 * 2 * math.asin(math.sqrt(min(1, max(0, arc))))
        if distance > 30 or (closest is not None and distance >= closest[0]):
            continue
        labels = []
        for value in (name, row.get('admin1'), row.get('country')):
            if isinstance(value, str):
                value = ''.join(c for c in value if c.isprintable()).strip()[:80]
                if value and value.casefold() not in [v.casefold() for v in labels]:
                    labels.append(value)
        closest = distance, ' · '.join(labels)
    return closest[1] if closest else None


class WeatherClient(QObject):
    changed = Signal(dict)
    LIMIT = 65536
    TIMEOUT_MS = 8000
    INTERVAL_MS = 300000

    def __init__(self, parent=None, language='ko'):
        super().__init__(parent)
        if language not in ('ko', 'en'):
            raise ValueError('지원 언어는 ko 또는 en입니다.')
        self.language = language
        self.manager = QNetworkAccessManager(self)
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(self.INTERVAL_MS)
        self.poll_timer.timeout.connect(self.refresh)
        self.age_timer = QTimer(self)
        self.age_timer.setInterval(10000)
        self.age_timer.timeout.connect(self._check_age)
        self.deadline = QTimer(self)
        self.deadline.setSingleShot(True)
        self.deadline.timeout.connect(self._timeout)
        self.snapshot = {'temperature': None, 'region': '', 'checked_at': None,
                         'status': '기온 조회 준비', 'stale': True, 'busy': False, 'observed_at': None,
                         'region_original': '', 'language': language, 'region_source': 'ipwho.is · 원문'}
        self.reply = None
        self.closed = False
        self.last_success = None
        self.source_age_at_success = None
        self._region = ''
        self._region_original = ''
        self._region_source = 'ipwho.is · 원문'
        self._location = None
        self._region_cache = OrderedDict()
        self._generation = 0
        self._stage = ''

    def _guard(self, callback):
        generation = self._generation
        def accept(data):
            if not self.closed and generation == self._generation:
                callback(data)
        return accept

    def _abort_request(self):
        self.deadline.stop()
        reply, self.reply = self.reply, None
        if reply is not None:
            reply.abort()
            reply.deleteLater()
        self._stage = ''

    def set_language(self, language):
        if language not in ('ko', 'en'):
            raise ValueError('지원 언어는 ko 또는 en입니다.')
        if self.closed or language == self.language:
            return
        was_busy = self.snapshot['busy']
        self.language = language
        self._generation += 1
        self._abort_request()
        if self._location is not None:
            self._region, self._region_original = localized_region(self._location, language)
            self._region_source = 'ipwho.is · 원문 또는 국내 사전'
            self._publish(region=self._region, region_original=self._region_original,
                          language=language, region_source=self._region_source, busy=False)
            if was_busy or self.snapshot['temperature'] is None:
                self._request_weather()
            else:
                self._lookup_region()
        else:
            self._publish(language=language)
            if was_busy or self.poll_timer.isActive():
                self.refresh()

    def _publish(self, **changes):
        if self.closed:
            return
        self.snapshot = {**self.snapshot, **changes}
        self.changed.emit(dict(self.snapshot))

    def start(self):
        if self.closed or self.poll_timer.isActive():
            return
        self.poll_timer.start()
        self.age_timer.start()
        self.refresh()

    def refresh(self):
        if self.closed or self.reply is not None:
            return False
        self._publish(busy=True, status='기온 조회 중')
        self._generation += 1
        self._stage = 'location'
        self._get('https://ipwho.is/', self._guard(self._location_done))
        return True

    def _get(self, url, callback):
        request = QNetworkRequest(QUrl(url))
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute,
                             QNetworkRequest.RedirectPolicy.ManualRedirectPolicy)
        request.setRawHeader(b'Accept', b'application/json')
        self.reply = self.manager.get(request)
        reply = self.reply
        reply.setReadBufferSize(self.LIMIT + 1)
        reply.downloadProgress.connect(lambda received, total: self._check_size(reply, received, total))
        reply.finished.connect(lambda: self._finish(reply, callback))
        self.deadline.start(self.TIMEOUT_MS)

    def _check_size(self, reply, received, total):
        if reply is self.reply and (received > self.LIMIT or total > self.LIMIT):
            self._fail('기온 조회 응답이 너무 큽니다')

    def _finish(self, reply, callback):
        if reply is not self.reply or self.closed:
            reply.deleteLater()
            return
        self.deadline.stop()
        self.reply = None
        if reply.error() != QNetworkReply.NetworkError.NoError:
            reply.deleteLater()
            self._request_failed('위치 또는 기온 네트워크 조회 실패')
            return
        raw = bytes(reply.read(self.LIMIT + 1))
        reply.deleteLater()
        if len(raw) > self.LIMIT:
            self._request_failed('기온 조회 응답이 너무 큽니다')
            return
        try:
            data = json.loads(raw.decode('utf-8'))
            if not isinstance(data, dict):
                raise ValueError('응답 형식')
            callback(data)
        except (ValueError, TypeError, UnicodeError, KeyError, OverflowError):
            self._request_failed('위치 또는 기온 응답을 확인할 수 없습니다')

    @staticmethod
    def _valid_number(value, low, high):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and low <= value <= high and math.isfinite(value)

    def _location_done(self, data):
        if self.closed:
            return
        if data.get('success') is not True:
            self._publish(busy=False, stale=True, status='네트워크 위치를 확인할 수 없습니다')
            return
        latitude, longitude = data.get('latitude'), data.get('longitude')
        if not self._valid_number(latitude, -90, 90) or not self._valid_number(longitude, -180, 180):
            raise ValueError('위치 범위')
        # IP 자체는 복사하지 않으며 좌표는 현재 요청 문맥과 유한 메모리 캐시에만 둡니다.
        self._location = {key: data[key] for key in ('city', 'region', 'country', 'country_code', 'latitude', 'longitude') if key in data}
        for key in ('city', 'region', 'country', 'country_code'):
            value = self._location.get(key)
            self._location[key] = ''.join(c for c in value if c.isprintable()).strip()[:80] if isinstance(value, str) else ''
        self._location['country_code'] = self._location['country_code'].upper()
        self._region, self._region_original = localized_region(self._location, self.language)
        self._region_source = 'ipwho.is · 원문 또는 국내 사전'
        self._request_weather()

    def _request_weather(self):
        latitude, longitude = self._location['latitude'], self._location['longitude']
        query = urlencode({'latitude': latitude, 'longitude': longitude, 'current': 'temperature_2m',
                           'temperature_unit': 'celsius', 'timeformat': 'unixtime'})
        self._stage = 'weather'
        self._publish(busy=True, status='기온 조회 중')
        self._get('https://api.open-meteo.com/v1/forecast?' + query, self._guard(self._weather_done))

    def _cache_key(self):
        return tuple(self._location.get(key, '') for key in ('city', 'region', 'country_code')) + (
            round(self._location['latitude'], 2), round(self._location['longitude'], 2), self.language)

    def _lookup_region(self):
        if self.closed or self._location is None:
            return
        key = self._cache_key()
        if key in self._region_cache:
            self._region_cache.move_to_end(key)
            self._region, self._region_source = self._region_cache[key]
            self._publish(region=self._region, region_source=self._region_source)
            self._stage = ''
            return
        city, code = self._location.get('city'), self._location.get('country_code')
        if len(city) < 2 or not re.fullmatch('[A-Z]{2}', code):
            self._stage = ''
            return
        query = urlencode({'name': city, 'count': 10, 'language': self.language, 'countryCode': code})
        self._stage = 'geocode'
        self._get('https://geocoding-api.open-meteo.com/v1/search?' + query, self._guard(self._geocode_done))

    def _geocode_done(self, data):
        if self.closed or self._location is None:
            return
        label = select_geocoded_region(self._location, data)
        self._stage = ''
        if label:
            self._region = label
            self._region_source = 'Open-Meteo Geocoding · GeoNames'
            key = self._cache_key()
            self._region_cache[key] = (label, self._region_source)
            self._region_cache.move_to_end(key)
            while len(self._region_cache) > 16:
                self._region_cache.popitem(last=False)
            self._publish(region=label, region_source=self._region_source, busy=False)
        else:
            self._publish(region=self._region, region_source='ipwho.is · 지명 검색 미일치 · 원문 보존', busy=False)

    def _request_failed(self, message):
        if self._stage == 'geocode':
            self._stage = ''
            self._publish(busy=False, region_source='ipwho.is · 지역 번역 실패 · 원문 보존')
        else:
            self._stage = ''
            self._publish(busy=False, stale=True, status=message)

    def _weather_done(self, data):
        if self.closed:
            return
        current = data.get('current')
        temperature = current.get('temperature_2m') if isinstance(current, dict) else None
        if not self._valid_number(temperature, -100, 70):
            raise ValueError('기온 범위')
        observed = current.get('time')
        now = time.time()
        if not self._valid_number(observed, 0, now + 300):
            raise ValueError('기온 제공 시각')
        stale = now - observed > 900
        self.last_success = time.monotonic() if not stale else None
        self.source_age_at_success = max(0, now - observed) if not stale else None
        self._publish(temperature=float(temperature), region=self._region, region_original=self._region_original,
                      language=self.language, region_source=self._region_source,
                      checked_at=now, observed_at=observed,
                      busy=False, stale=stale, status='기온 제공 자료 지연 · 이전 값' if stale else '기온 조회 완료')
        self._lookup_region()

    def _check_age(self):
        if self.last_success is None or self.snapshot['stale']:
            return
        elapsed = max(0, time.monotonic() - self.last_success)
        source_age = self.source_age_at_success + elapsed
        if source_age > 900:
            self._publish(stale=True, status='기온 제공 자료 지연 · 이전 값')
        elif elapsed > 600:
            self._publish(stale=True, status='기온 조회 지연 · 이전 값')

    def _fail(self, message):
        self.deadline.stop()
        reply, self.reply = self.reply, None
        if reply is not None:
            reply.abort()
            reply.deleteLater()
        self._request_failed(message)

    def _timeout(self):
        self._fail('위치 또는 기온 조회 시간 초과')

    def close(self):
        if self.closed:
            return
        self.closed = True
        self._generation += 1
        self.poll_timer.stop()
        self.age_timer.stop()
        self.deadline.stop()
        reply, self.reply = self.reply, None
        if reply is not None:
            reply.abort()
            reply.deleteLater()
        self._location = None
        self._region_cache.clear()
