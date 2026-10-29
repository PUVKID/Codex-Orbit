"""네트워크로 대략적인 지역과 현재 기온을 비동기 조회합니다."""
import json
import math
import time
from urllib.parse import urlencode

from PySide6.QtCore import QObject, QTimer, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest


class WeatherClient(QObject):
    changed = Signal(dict)
    LIMIT = 65536
    TIMEOUT_MS = 8000
    INTERVAL_MS = 300000

    def __init__(self, parent=None):
        super().__init__(parent)
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
                         'status': '기온 조회 준비', 'stale': True, 'busy': False, 'observed_at': None}
        self.reply = None
        self.closed = False
        self.last_success = None
        self.source_age_at_success = None
        self._region = ''

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
        self._get('https://ipwho.is/', self._location_done)
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
            self._publish(busy=False, stale=True, status='위치 또는 기온 네트워크 조회 실패')
            return
        raw = bytes(reply.read(self.LIMIT + 1))
        reply.deleteLater()
        if len(raw) > self.LIMIT:
            self._publish(busy=False, stale=True, status='기온 조회 응답이 너무 큽니다')
            return
        try:
            data = json.loads(raw.decode('utf-8'))
            if not isinstance(data, dict):
                raise ValueError('응답 형식')
            callback(data)
        except (ValueError, TypeError, UnicodeError, KeyError, OverflowError):
            self._publish(busy=False, stale=True, status='위치 또는 기온 응답을 확인할 수 없습니다')

    @staticmethod
    def _valid_number(value, low, high):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and low <= value <= high

    def _location_done(self, data):
        if data.get('success') is not True:
            self._publish(busy=False, stale=True, status='네트워크 위치를 확인할 수 없습니다')
            return
        latitude, longitude = data.get('latitude'), data.get('longitude')
        if not self._valid_number(latitude, -90, 90) or not self._valid_number(longitude, -180, 180):
            raise ValueError('위치 범위')
        city, region = data.get('city'), data.get('region')
        self._region = ' · '.join(dict.fromkeys(v.strip()[:80] for v in (city, region) if isinstance(v, str) and v.strip()))
        query = urlencode({'latitude': latitude, 'longitude': longitude, 'current': 'temperature_2m',
                           'temperature_unit': 'celsius', 'timeformat': 'unixtime'})
        self._get('https://api.open-meteo.com/v1/forecast?' + query, self._weather_done)

    def _weather_done(self, data):
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
        self._publish(temperature=float(temperature), region=self._region, checked_at=now, observed_at=observed,
                      busy=False, stale=stale, status='기온 제공 자료 지연 · 이전 값' if stale else '기온 조회 완료')

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
        self._publish(busy=False, stale=True, status=message)

    def _timeout(self):
        self._fail('위치 또는 기온 조회 시간 초과')

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.poll_timer.stop()
        self.age_timer.stop()
        self.deadline.stop()
        reply, self.reply = self.reply, None
        if reply is not None:
            reply.abort()
            reply.deleteLater()
