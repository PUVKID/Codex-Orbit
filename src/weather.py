"""네트워크로 대략적인 지역과 현재 기온을 비동기 조회합니다."""
import json
import math
import re
import time
from datetime import datetime, timedelta, timezone
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


def _region_identity(value, code):
    """확인된 시도 별칭만 대응하며 서로 다른 행정구역을 거리로 합치지 않습니다."""
    if not isinstance(value, str):
        return ''
    key = ' '.join(value.casefold().split())
    if code == 'KR':
        if value in _KOREAN_REGIONS.values():
            return value
        for suffix in (' special self-governing province', ' special self-governing city',
                       ' metropolitan city', ' province', ' special city', '-do', '-si'):
            key = key.removesuffix(suffix)
        return _KOREAN_REGIONS.get(key, key)
    return key


def _selected_geocoded_region(location, data):
    """동일 국가·확인된 시도와 30km 거리 조건을 만족하는 후보만 반환합니다."""
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
        expected_region = _region_identity(location.get('region'), code)
        if expected_region and expected_region != _region_identity(row.get('admin1'), code):
            continue
        lat, lon = row.get('latitude'), row.get('longitude')
        name = row.get('name')
        if not isinstance(name, str) or not name.strip() or not valid(lat, -90, 90) or not valid(lon, -180, 180):
            continue
        expected_name = location.get('city')
        # 영문 이름이 모두 있는 경우에는 가까운 다른 도시를 번역 후보로 사용하지 않습니다.
        if (isinstance(expected_name, str) and expected_name and expected_name.isascii() and name.isascii()
                and ' '.join(expected_name.casefold().split()) != ' '.join(name.casefold().split())):
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
        closest = distance, ' · '.join(labels), row
    return closest


def select_geocoded_region(location, data):
    """기존 지역 표시 선택 정책을 유지합니다."""
    selected = _selected_geocoded_region(location, data)
    return selected[1] if selected else None


def select_geocoded_city_ref(location, data):
    """좌표 근접만으로 도시를 확정하지 않고 같은 이름·국가의 식별자만 보존합니다."""
    selected = _selected_geocoded_region(location, data)
    if not selected:
        return None
    row = selected[2]
    def identity(value):
        return ' '.join(value.casefold().split()) if isinstance(value, str) else ''
    name, expected = identity(row.get('name')), identity(location.get('city'))
    identifier = row.get('id')
    if not name or name != expected or type(identifier) is not int or identifier <= 0:
        return None
    return dict(provider='geonames',geonames_id=identifier,country_code=location['country_code'],
                confidence='estimated',provenance='ipwho.is + Open-Meteo / GeoNames')


_WEATHER_LABELS = {
    0: ('맑음', 'Clear'), 1: ('대체로 맑음', 'Mainly clear'), 2: ('구름 조금', 'Partly cloudy'),
    3: ('흐림', 'Overcast'), 45: ('안개', 'Fog'), 48: ('얼음 안개', 'Rime fog'),
    51: ('약한 이슬비', 'Light drizzle'), 53: ('이슬비', 'Drizzle'), 55: ('강한 이슬비', 'Dense drizzle'),
    56: ('어는 이슬비', 'Freezing drizzle'), 57: ('어는 이슬비', 'Freezing drizzle'),
    61: ('약한 비', 'Light rain'), 63: ('비', 'Rain'), 65: ('강한 비', 'Heavy rain'),
    66: ('어는 비', 'Freezing rain'), 67: ('강한 어는 비', 'Heavy freezing rain'),
    71: ('약한 눈', 'Light snow'), 73: ('눈', 'Snow'), 75: ('강한 눈', 'Heavy snow'),
    77: ('싸락눈', 'Snow grains'), 80: ('약한 소나기', 'Light showers'), 81: ('소나기', 'Showers'),
    82: ('강한 소나기', 'Heavy showers'), 85: ('눈 소나기', 'Snow showers'), 86: ('강한 눈 소나기', 'Heavy snow showers'),
    95: ('뇌우', 'Thunderstorm'), 96: ('우박 동반 뇌우', 'Thunderstorm with hail'),
    97: ('강한 뇌우', 'Heavy thunderstorm'), 99: ('강한 우박 동반 뇌우', 'Heavy thunderstorm with hail'),
}


def weather_description(code, language='ko'):
    """Open-Meteo의 현재 WMO 코드만 해석하며 모르는 값을 맑음으로 대체하지 않습니다."""
    if language not in ('ko', 'en'):
        raise ValueError('지원 언어는 ko 또는 en입니다.')
    labels = _WEATHER_LABELS.get(code) if type(code) is int else None
    return labels[language == 'en'] if labels else ('날씨 미확인' if language == 'ko' else 'Weather unknown')


def weather_sun_time(stamp, offset):
    """컴퓨터 시간대 대신 선택 도시 응답의 검증된 시차로 일출·일몰을 표시합니다."""
    if (type(stamp) not in (int, float) or not math.isfinite(stamp) or stamp <= 0
            or type(offset) is not int or not -86400 < offset < 86400):
        return '—'
    try:
        return datetime.fromtimestamp(stamp, timezone(timedelta(seconds=offset))).strftime('%H:%M')
    except (ValueError, OverflowError, OSError):
        return '—'


def normalize_city(value):
    """직접 고른 공개 도시의 필수 이름·국가·유한 좌표만 수락합니다."""
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError('도시 정보 형식')
    result = {}
    for key in ('name', 'admin1', 'country', 'country_code'):
        raw = value.get(key, '')
        if not isinstance(raw, str) or len(raw) > 160 or any(not c.isprintable() for c in raw):
            raise ValueError('도시 이름 형식')
        result[key] = raw.strip()[:80]
    result['country_code'] = result['country_code'].upper()
    if not result['name'] or not re.fullmatch('[A-Z]{2}', result['country_code']):
        raise ValueError('도시 이름 또는 국가 코드')
    for key, low, high in (('latitude', -90, 90), ('longitude', -180, 180)):
        number = value.get(key)
        if type(number) not in (int, float) or not math.isfinite(number) or not low <= number <= high:
            raise ValueError('도시 좌표 범위')
        result[key] = float(number)
    if type(value.get('id')) is int and value['id'] > 0:
        result['id'] = value['id']
    if type(value.get('admin1_id')) is int and value['admin1_id'] > 0:
        result['admin1_id'] = value['admin1_id']
    display = value.get('display_name')
    if display is not None:
        if not isinstance(display, str) or len(display) > 640 or any(not c.isprintable() for c in display):
            raise ValueError('선택 위치 이름 형식')
        result['display_name'] = display.strip()[:320]
    address = value.get('address')
    if address is not None:
        if not isinstance(address, dict):
            raise ValueError('선택 위치 주소 형식')
        result['address'] = {}
        for key in ('city', 'district', 'neighbourhood', 'road', 'house_number', 'postcode', 'state', 'country'):
            text = address.get(key)
            if text is not None:
                if not isinstance(text, str) or len(text) > 160 or any(not c.isprintable() for c in text):
                    raise ValueError('선택 위치 주소 구성 형식')
                if text.strip():
                    result['address'][key] = text.strip()[:80]
    return result


def parse_city_results(data):
    """여러 동명 도시를 구분해 선택하도록 최대 열 개의 검증된 후보를 반환합니다."""
    if not isinstance(data, dict) or data.get('error'):
        raise ValueError('도시 검색 응답')
    rows = data.get('results', [])
    if not isinstance(rows, list) or len(rows) > 10:
        raise ValueError('도시 검색 개수')
    result, seen = [], set()
    for row in rows:
        try:
            city = normalize_city(row)
        except ValueError:
            continue
        if city is None:
            continue
        key = (city['name'], city['country_code'], city['latitude'], city['longitude'])
        if key not in seen:
            seen.add(key)
            result.append(city)
    return result


class CitySearchClient(QObject):
    """사용자가 입력한 도시만 검색하며 기온 요청과 별도 수명으로 동작합니다."""
    results = Signal(list)
    failed = Signal(str)
    LIMIT = 65536
    TIMEOUT_MS = 8000

    def __init__(self, parent=None, language='ko'):
        super().__init__(parent)
        if language not in ('ko', 'en'):
            raise ValueError('지원 언어는 ko 또는 en입니다.')
        self.language = language
        self.manager = QNetworkAccessManager(self)
        self.reply = None
        self.closed = False
        self.deadline = QTimer(self)
        self.deadline.setSingleShot(True)
        self.deadline.timeout.connect(self._timeout)

    def _cancel(self):
        self.deadline.stop()
        reply, self.reply = self.reply, None
        if reply is not None:
            reply.abort()
            reply.deleteLater()

    def set_language(self, language):
        if language not in ('ko', 'en'):
            raise ValueError('지원 언어는 ko 또는 en입니다.')
        if language != self.language:
            self._cancel()
            self.language = language

    def search(self, query):
        if self.closed:
            return False
        self._cancel()
        if not isinstance(query, str) or not 2 <= len(query.strip()) <= 80 or any(not c.isprintable() for c in query):
            self.failed.emit('도시 이름을 두 글자 이상 입력해 주세요.')
            return False
        request = QNetworkRequest(QUrl(self._search_url(query.strip())))
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute,
                             QNetworkRequest.RedirectPolicy.ManualRedirectPolicy)
        request.setRawHeader(b'Accept', b'application/json')
        request.setRawHeader(b'User-Agent', b'CodexOrbit/3.3 (https://github.com/PUVKID/Codex-Orbit)')
        reply = self.manager.get(request)
        self.reply = reply
        reply.setReadBufferSize(self.LIMIT + 1)
        reply.downloadProgress.connect(lambda received, total: self._size(reply, received, total))
        reply.finished.connect(lambda: self._finish(reply))
        self.deadline.start(self.TIMEOUT_MS)
        return True

    def _search_url(self, query):
        return 'https://geocoding-api.open-meteo.com/v1/search?' + urlencode(dict(name=query, count=10, language=self.language))

    def _parse_response(self, data):
        return parse_city_results(data)

    def _size(self, reply, received, total):
        if reply is self.reply and (received > self.LIMIT or total > self.LIMIT):
            self._cancel()
            if not self.closed:
                self.failed.emit('도시 검색 응답이 너무 큽니다.')

    def _finish(self, reply):
        if self.closed or reply is not self.reply:
            reply.deleteLater()
            return
        self.deadline.stop()
        self.reply = None
        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                raise ValueError('network')
            raw = bytes(reply.read(self.LIMIT + 1))
            if len(raw) > self.LIMIT:
                raise ValueError('size')
            cities = self._parse_response(json.loads(raw.decode('utf-8')))
        except (ValueError, TypeError, UnicodeError, OverflowError):
            self.failed.emit('도시를 찾지 못했습니다. 인터넷 연결과 이름을 확인해 주세요.')
        else:
            self.results.emit(cities)
        finally:
            reply.deleteLater()

    def _timeout(self):
        self._cancel()
        if not self.closed:
            self.failed.emit('도시 검색이 늦어지고 있습니다. 다시 검색해 주세요.')

    def close(self):
        self.closed = True
        self._cancel()


def parse_place_results(data):
    """공개 지도 제공자가 반환한 지점과 주소 구성만 사용하며 상세 주소를 추정하지 않습니다."""
    rows = data.get('features') if isinstance(data, dict) else None
    if not isinstance(rows, list) or len(rows) > 10:
        raise ValueError('장소 검색 응답')
    results, seen = [], set()
    for item in rows:
        if not isinstance(item, dict):
            continue
        props, geometry = item.get('properties'), item.get('geometry')
        if not isinstance(props, dict) or not isinstance(geometry, dict) or geometry.get('type') != 'Point':
            continue
        coordinates = geometry.get('coordinates')
        if not isinstance(coordinates, list) or len(coordinates) != 2:
            continue
        address = {}
        keys = {'city': 'city', 'district': 'district', 'locality': 'neighbourhood', 'street': 'road',
                'housenumber': 'house_number', 'postcode': 'postcode', 'state': 'state', 'country': 'country'}
        for original, key in keys.items():
            if props.get(original) is not None:
                address[key] = props[original]
        name = props.get('name') or props.get('street') or props.get('city')
        labels = [name] + [props.get(key) for key in ('housenumber', 'street', 'locality', 'district', 'city', 'state', 'postcode', 'country')]
        display = ' · '.join(dict.fromkeys(value.strip() for value in labels if isinstance(value, str) and value.strip()))
        try:
            value = normalize_city(dict(name=name, admin1=props.get('state', ''), country=props.get('country', ''),
                                        country_code=props.get('countrycode', ''), latitude=coordinates[1], longitude=coordinates[0],
                                        display_name=display, address=address))
        except ValueError:
            continue
        key = (value['name'], value['latitude'], value['longitude'])
        if key not in seen:
            seen.add(key)
            results.append(value)
    return results


class PlaceSearchClient(CitySearchClient):
    """명시적인 장소 검색에만 공개 Photon/OSM을 사용합니다. 자동 추적이나 주소 역추정은 하지 않습니다."""
    _last_request_at = 0.0

    def __init__(self, parent=None, language='ko'):
        super().__init__(parent, language)
        self._cache = OrderedDict()
        self._pending_key = None
        self._country = None

    def set_country(self, country_code):
        if country_code is not None and (not isinstance(country_code, str) or not re.fullmatch('[A-Za-z]{2}', country_code)):
            raise ValueError('국가 코드 형식')
        self._cancel()
        self._country = country_code.upper() if country_code else None

    def search(self, query):
        if self.closed:
            return False
        if not isinstance(query, str) or not 2 <= len(query.strip()) <= 80 or any(not c.isprintable() for c in query):
            return super().search(query)
        key = (query.strip(), self.language, self._country)
        self._cancel()
        if key in self._cache:
            self._cache.move_to_end(key)
            self.results.emit([normalize_city(item) for item in self._cache[key]])
            return True
        now = time.monotonic()
        if now - PlaceSearchClient._last_request_at < 1.0:
            self.failed.emit('검색은 1초 뒤에 다시 해 주세요.')
            return False
        PlaceSearchClient._last_request_at = now
        self._pending_key = key
        return super().search(query)

    def _search_url(self, query):
        params = dict(q=query, limit=5, lang=self.language)
        if self._country:
            params['countrycode'] = self._country
        return 'https://photon.komoot.io/api/?' + urlencode(params)

    def _parse_response(self, data):
        rows = parse_place_results(data)
        if self._pending_key is not None:
            self._cache[self._pending_key] = [normalize_city(item) for item in rows]
            self._cache.move_to_end(self._pending_key)
            while len(self._cache) > 16:
                self._cache.popitem(last=False)
        return rows

    def close(self):
        super().close()
        self._cache.clear()
        self._pending_key = None


class WeatherClient(QObject):
    changed = Signal(dict)
    LIMIT = 65536
    TIMEOUT_MS = 8000
    INTERVAL_MS = 300000

    def __init__(self, parent=None, language='ko', location_override=None):
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
        self._city_ref = None
        self._region_cache = OrderedDict()
        self._generation = 0
        self._stage = ''
        self.location_override = normalize_city(location_override)
        self.snapshot.update(humidity=None, precipitation=None, precipitation_interval_seconds=None, weather_code=None, sunrise=None, sunset=None, timezone='', utc_offset_seconds=None, country_code='', city_ref=None)
        self.snapshot['location_mode'] = 'manual' if self.location_override else 'automatic'
        if self.location_override:
            self._configure_override()
            self.snapshot.update(region=self._region, region_original=self._region_original, region_source=self._region_source, country_code=self.location_override['country_code'], city_ref=self._city_ref)

    def _configure_override(self):
        city = self.location_override
        self._location = dict(city=city['name'], region=city['admin1'], country=city['country'],
                              country_code=city['country_code'], latitude=city['latitude'], longitude=city['longitude'])
        self._region, self._region_original = localized_region(self._location, self.language)
        if city.get('display_name'):
            self._region = self._region_original = city['display_name']
        self._region_source = '사용자 선택 지점 · Photon / OpenStreetMap' if city.get('display_name') or city.get('address') else '사용자 지정 도시 · Open-Meteo / GeoNames'
        identifier=city.get('id')
        self._city_ref = (dict(provider='geonames',geonames_id=identifier,country_code=city['country_code'],
                               confidence='selected',provenance='Open-Meteo / GeoNames')
                          if type(identifier) is int and identifier > 0 and not city.get('display_name') and not city.get('address') else None)

    def set_location_override(self, value):
        city = normalize_city(value)
        if self.closed or city == self.location_override:
            return False
        self._generation += 1
        self._abort_request()
        self.location_override = city
        self._location = None
        self._city_ref = None
        self._region = self._region_original = ''
        self._region_cache.clear()
        self.last_success = self.source_age_at_success = None
        self._region_source = 'ipwho.is · 원문' if city is None else '사용자 지정 도시 · Open-Meteo / GeoNames'
        if city:
            self._configure_override()
        self._publish(temperature=None, humidity=None, precipitation=None, precipitation_interval_seconds=None, weather_code=None, sunrise=None, sunset=None, timezone='',
                      utc_offset_seconds=None, checked_at=None, observed_at=None, stale=True, busy=False,
                      region=self._region, region_original=self._region_original, region_source=self._region_source,
                      location_mode='manual' if city else 'automatic', country_code=city['country_code'] if city else '', city_ref=self._city_ref)
        self.refresh()
        return True

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
        if self.location_override is not None:
            self._configure_override()
            self._publish(language=language, region=self._region, region_original=self._region_original,
                          region_source=self._region_source, busy=False, location_mode='manual')
            if was_busy or self.snapshot['temperature'] is None:
                self._request_weather()
            return
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
        if self.location_override is not None:
            self._configure_override()
            self._request_weather()
            return True
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
        previous_location = self._location
        # IP 자체는 복사하지 않으며 좌표는 현재 요청 문맥과 유한 메모리 캐시에만 둡니다.
        self._location = {key: data[key] for key in ('city', 'region', 'country', 'country_code', 'latitude', 'longitude') if key in data}
        for key in ('city', 'region', 'country', 'country_code'):
            value = self._location.get(key)
            self._location[key] = ''.join(c for c in value if c.isprintable()).strip()[:80] if isinstance(value, str) else ''
        self._location['country_code'] = self._location['country_code'].upper()
        self._region, self._region_original = localized_region(self._location, self.language)
        self._region_source = 'ipwho.is · 원문 또는 국내 사전'
        fields = ('latitude', 'longitude', 'country_code', 'city', 'region')
        changed_location = previous_location is None or any(previous_location.get(key) != self._location.get(key) for key in fields)
        cleared = {}
        if changed_location:
            # 새 지역 이름 아래에 이전 지역의 기상·시차가 잠깐이라도 남지 않게 한 번에 비웁니다.
            self.last_success = self.source_age_at_success = None
            self._city_ref = None
            cleared = dict(city_ref=None, temperature=None, humidity=None, precipitation=None, precipitation_interval_seconds=None, weather_code=None, sunrise=None, sunset=None,
                           timezone='', utc_offset_seconds=None, checked_at=None, observed_at=None, stale=True)
        self._publish(country_code=self._location['country_code'] if re.fullmatch('[A-Z]{2}', self._location['country_code']) else '',
                      region=self._region, region_original=self._region_original, region_source=self._region_source,
                      location_mode='automatic', **cleared)
        self._request_weather()

    def _request_weather(self):
        latitude, longitude = self._location['latitude'], self._location['longitude']
        query = urlencode({'latitude': latitude, 'longitude': longitude, 'current': 'temperature_2m,relative_humidity_2m,weather_code,precipitation',
                           'daily': 'sunrise,sunset', 'forecast_days': 1, 'timezone': 'auto',
                           'temperature_unit': 'celsius', 'precipitation_unit': 'mm', 'timeformat': 'unixtime'})
        self._stage = 'weather'
        self._publish(busy=True, status='기온 조회 중')
        self._get('https://api.open-meteo.com/v1/forecast?' + query, self._guard(self._weather_done))

    def _cache_key(self):
        return tuple(self._location.get(key, '') for key in ('city', 'region', 'country_code')) + (
            round(self._location['latitude'], 2), round(self._location['longitude'], 2), self.language)

    def _lookup_region(self):
        if self.closed or self._location is None or self.location_override is not None:
            return
        key = self._cache_key()
        if key in self._region_cache:
            self._region_cache.move_to_end(key)
            self._region, self._region_source, self._city_ref = self._region_cache[key]
            self._publish(region=self._region, region_source=self._region_source, city_ref=self._city_ref)
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
        selected = _selected_geocoded_region(self._location, data)
        self._stage = ''
        if selected:
            ref = select_geocoded_city_ref(self._location, data)
            if ref is not None:
                self._accept_geocoded_region(selected[1], ref)
                return
            identifier = selected[2].get('id')
            if (self.language != 'en' and self._location.get('city', '').isascii()
                    and type(identifier) is int and identifier > 0):
                # 번역 후보를 먼저 표시하지 않고 같은 도시·시도 ID의 영문 응답을 기다립니다.
                query=urlencode({'name':self._location['city'],'count':10,'language':'en','countryCode':self._location['country_code']})
                self._stage='geocode_identity'
                self._get('https://geocoding-api.open-meteo.com/v1/search?'+query,
                          self._guard(lambda rows:self._identity_done(rows,identifier,selected)))
                return
        self._publish(region=self._region, region_source='ipwho.is · 지명 검색 미일치 · 원문 보존', busy=False)

    def _accept_geocoded_region(self, label, ref):
        self._region = label
        self._region_source = 'Open-Meteo Geocoding · GeoNames'
        self._city_ref = ref
        key = self._cache_key()
        self._region_cache[key] = (label, self._region_source, ref)
        self._region_cache.move_to_end(key)
        while len(self._region_cache) > 16:
            self._region_cache.popitem(last=False)
        self._publish(region=label, region_source=self._region_source, city_ref=ref, busy=False)

    def _identity_done(self,data,expected_id,localized=None):
        ref=select_geocoded_city_ref(self._location,data)
        selected = _selected_geocoded_region(self._location, data)
        self._stage=''
        admin_id = localized[2].get('admin1_id') if localized else None
        same_admin = (admin_id is None or (type(admin_id) is int and admin_id > 0
                       and selected is not None and selected[2].get('admin1_id') == admin_id))
        if ref is None or ref['geonames_id']!=expected_id or not same_admin:
            self._publish(city_ref=None,busy=False)
            return
        self._accept_geocoded_region(localized[1] if localized else self._region, ref)

    def _request_failed(self, message):
        if self._stage == 'geocode_identity':
            self._stage=''
            self._publish(city_ref=None,busy=False)
        elif self._stage == 'geocode':
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
        humidity = current.get('relative_humidity_2m')
        humidity = float(humidity) if self._valid_number(humidity, 0, 100) else None
        # 강수량은 제공 응답의 실제 집계 간격과 mm 단위가 함께 확인될 때만 표시합니다.
        precipitation = current.get('precipitation')
        interval = current.get('interval')
        units = data.get('current_units')
        valid_rain = (isinstance(units, dict) and units.get('precipitation') == 'mm'
                      and type(interval) is int and interval > 0
                      and type(precipitation) in (int, float) and math.isfinite(precipitation)
                      and precipitation >= 0)
        precipitation = float(precipitation) if valid_rain else None
        interval = interval if valid_rain else None
        weather_code = current.get('weather_code')
        weather_code = weather_code if type(weather_code) is int and weather_code in _WEATHER_LABELS else None
        zone = data.get('timezone', '')
        zone = zone if isinstance(zone, str) and re.fullmatch(r'[A-Za-z0-9_+/-]{1,80}', zone) else ''
        offset = data.get('utc_offset_seconds')
        offset = offset if zone and type(offset) is int and -86400 < offset < 86400 else None
        daily = data.get('daily')
        def sun_value(key):
            rows = daily.get(key) if isinstance(daily, dict) else None
            stamp = rows[0] if isinstance(rows, list) and len(rows) == 1 else None
            return stamp if offset is not None and self._valid_number(stamp, max(1, now - 172800), now + 172800) else None
        sunrise, sunset = sun_value('sunrise'), sun_value('sunset')
        if sunrise is not None and sunset is not None and sunrise >= sunset:
            sunrise = sunset = None
        stale = now - observed > 900
        self.last_success = time.monotonic() if not stale else None
        self.source_age_at_success = max(0, now - observed) if not stale else None
        self._publish(temperature=float(temperature), humidity=humidity, precipitation=precipitation,
                      precipitation_interval_seconds=interval, weather_code=weather_code,
                      sunrise=sunrise, sunset=sunset, timezone=zone, utc_offset_seconds=offset, region=self._region, region_original=self._region_original,
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
