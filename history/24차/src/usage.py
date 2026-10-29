"""Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다."""
from datetime import datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import shutil
import time

from PySide6.QtCore import QObject, QProcess, QTimer, Signal

MAX_BYTES = 1024 * 1024
KST = timezone(timedelta(hours=9))


def number(value):
    """불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, ValueError):
        return False


def reset_label(value):
    if not number(value) or value <= 0:
        return '초기화 미확인'
    try:
        return datetime.fromtimestamp(value, KST).strftime('%Y.%m.%d %H:%M:%S KST')
    except (ValueError, OverflowError, OSError):
        return '초기화 미확인'


def normalize_limits(value):
    """공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다."""
    if not isinstance(value, dict):
        return []
    if isinstance(value.get('rateLimitsByLimitId'), dict):
        buckets = value['rateLimitsByLimitId']
    else:
        legacy = value.get('rateLimits')
        buckets = {str(legacy.get('limitId') or 'codex'): legacy} if isinstance(legacy, dict) else {}
    rows = []
    for key, bucket in buckets.items():
        if not isinstance(bucket, dict):
            continue
        for slot in ('primary', 'secondary'):
            window = bucket.get(slot)
            if not isinstance(window, dict):
                continue
            used = window.get('usedPercent')
            remaining = 100 - max(0, min(100, used)) if number(used) else None
            minutes = window.get('windowDurationMins')
            if minutes == 300 and number(minutes):
                period = '5시간'
            elif minutes == 10080 and number(minutes):
                period = '주간'
            elif number(minutes) and minutes > 0:
                period = f'{minutes:g}분'
            else:
                period = '기간 미확인'
            reset = window.get('resetsAt')
            rows.append({'bucket': str(key)[:80], 'slot': slot, 'period': period,
                         'remaining': remaining, 'resets_at': reset if number(reset) and reset > 0 else None})
    return rows


def discover_codex(override=''):
    """사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다."""
    if override:
        path = Path(override)
        return str(path) if path.is_file() and path.suffix.lower() == '.exe' else None
    found = shutil.which('codex.exe') or shutil.which('codex')
    if found and Path(found).suffix.lower() == '.exe':
        return found
    local = Path(os.environ.get('LOCALAPPDATA') or Path.home() / 'AppData' / 'Local')
    base = local / 'OpenAI' / 'Codex' / 'bin'
    candidates = [p for p in base.glob('*/codex.exe') if p.is_file()]
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return str(candidates[0]) if candidates else None


class UsageClient(QObject):
    changed = Signal(dict)

    def __init__(self, executable='', parent=None):
        super().__init__(parent)
        self.executable = executable
        self.process = QProcess(self)
        # QProcess의 분리 파이프를 사용해 콘솔 창이나 셸을 열지 않습니다.
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.process.started.connect(self._started)
        self.process.readyReadStandardOutput.connect(self._stdout)
        self.process.readyReadStandardError.connect(self._stderr)
        self.process.errorOccurred.connect(self._process_error)
        self.process.finished.connect(self._finished)
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(30000)
        self.poll_timer.timeout.connect(self.refresh)
        self.deadline = QTimer(self)
        self.deadline.setSingleShot(True)
        self.deadline.setInterval(12000)
        self.deadline.timeout.connect(self._timeout)
        self.retry_timer = QTimer(self)
        self.retry_timer.setSingleShot(True)
        self.retry_timer.timeout.connect(self._retry)
        self.age_timer = QTimer(self)
        self.age_timer.setInterval(1000)
        self.age_timer.timeout.connect(self._check_age)
        self.snapshot = {'rows': [], 'checked_at': None, 'status': '잔량 조회 준비', 'stale': True, 'busy': False}
        self.ready = False
        self.enabled = False
        self.closed = False
        self.pending = None
        self.sequence = 0
        self.buffer = bytearray()
        self.stderr_bytes = 0
        self.retries = 0
        self.last_success = None
        self.failed_connection = False
        self.account_epoch = 0
        self.pending_epoch = 0

    def _publish(self, **changes):
        self.snapshot = {**self.snapshot, **changes}
        self.changed.emit(dict(self.snapshot))

    def start(self):
        if self.closed or self.enabled:
            return
        self.enabled = True
        self.poll_timer.start()
        self.age_timer.start()
        self._launch()

    def _launch(self):
        if self.closed or self.process.state() != QProcess.ProcessState.NotRunning:
            return False
        self.retry_timer.stop()
        try:
            executable = discover_codex(self.executable)
        except OSError:
            executable = None
        if not executable:
            self._publish(status='Codex EXE를 찾지 못했습니다. 설정에서 설치된 codex.exe를 선택하세요.', stale=True, busy=False)
            return False
        self.buffer.clear()
        self.stderr_bytes = 0
        self.ready = False
        self.failed_connection = False
        self._publish(status='잔량 연결 중', busy=True)
        self.deadline.start()
        self.process.setProgram(executable)
        self.process.setArguments(['app-server'])
        self.process.start()
        return True

    def _send(self, method, params=None, request=True):
        message = {'method': method}
        if request:
            self.sequence += 1
            message['id'] = self.sequence
            self.pending = (self.sequence, method)
            self.pending_epoch = self.account_epoch
        if params is not None:
            message['params'] = params
        data = (json.dumps(message, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
        if self.process.write(data) == -1:
            self._failed('잔량 요청을 전달하지 못했습니다.')
            return False
        if request:
            self.deadline.start()
        return True

    def _started(self):
        if self.closed:
            self.process.kill()
            return
        self._send('initialize', {'clientInfo': {'name': 'codex_orbit', 'title': 'Codex Orbit', 'version': '1.2.0'}})

    def refresh(self):
        if self.closed or self.pending or self.snapshot['busy']:
            return False
        if not self.ready:
            if self.enabled and self.retries < 3 and not self.retry_timer.isActive():
                return self._launch()
            return False
        self._publish(status='잔량 조회 중', busy=True)
        return self._send('account/rateLimits/read')

    def _stdout(self):
        self.process.setReadChannel(QProcess.ProcessChannel.StandardOutput)
        read = 0
        while self.process.bytesAvailable() and not self.failed_connection:
            chunk = bytes(self.process.read(65536))
            read += len(chunk)
            if read > MAX_BYTES:
                self._failed('잔량 응답이 허용 크기를 넘었습니다.')
                return
            self.feed_bytes(chunk)

    def _stderr(self):
        # 서버 진단에는 개인정보가 섞일 수 있어 저장·표시하지 않고 제한해 비웁니다.
        self.process.setReadChannel(QProcess.ProcessChannel.StandardError)
        while self.process.bytesAvailable() and not self.failed_connection:
            self.stderr_bytes += len(self.process.read(65536))
            if self.stderr_bytes > MAX_BYTES:
                self._failed('잔량 서버 진단이 허용 크기를 넘었습니다.')
                break
        self.process.setReadChannel(QProcess.ProcessChannel.StandardOutput)

    def feed_bytes(self, data):
        if self.closed or self.failed_connection:
            return
        self.buffer.extend(data)
        if len(self.buffer) > MAX_BYTES:
            self._failed('잔량 응답이 허용 크기를 넘었습니다.')
            return
        # 문자열 내부 U+0085 등을 줄 경계로 취급하지 않습니다.
        while b'\n' in self.buffer:
            line, _, tail = self.buffer.partition(b'\n')
            self.buffer = bytearray(tail)
            try:
                message = json.loads(line.decode('utf-8'))
                if not isinstance(message, dict):
                    raise ValueError('객체가 아닌 응답')
            except (ValueError, UnicodeError):
                self._failed('잔량 응답 형식을 확인할 수 없습니다.')
                return
            self._message(message)
            if self.failed_connection:
                return

    def _accept(self, payload, notification=False):
        rows = normalize_limits(payload)
        partial_multi = False
        if notification and isinstance(payload, dict) and not isinstance(payload.get('rateLimitsByLimitId'), dict):
            legacy = payload.get('rateLimits')
            if isinstance(legacy, dict):
                bucket = str(legacy.get('limitId') or 'codex')[:80]
                old = self.snapshot['rows']
                first = next((i for i, row in enumerate(old) if row['bucket'] == bucket), len(old))
                kept = [row for row in old if row['bucket'] != bucket]
                rows = kept[:first] + rows + kept[first:]
                partial_multi = len({row['bucket'] for row in rows}) > 1
        if partial_multi:
            # 다른 버킷을 재조회하지 않은 부분 알림은 기존 전체 조회의 시각·지연을 유지합니다.
            self._publish(rows=rows)
        else:
            self.last_success = time.monotonic()
            self._publish(rows=rows, checked_at=time.time(), stale=False,
                          status='조회 완료' if rows else '제공된 계정 한도가 없습니다.')

    def _message(self, message):
        method = message.get('method')
        if method == 'account/updated':
            self.account_epoch += 1
            self.last_success = None
            self._publish(rows=[], checked_at=None, stale=True, status='계정 정보 갱신 · 잔량 다시 조회 중')
            # 시작 직후에도 오는 통지입니다. 연결은 유지하고 이전 세대의 조회 결과만 폐기합니다.
            if not self.pending:
                self.refresh()
            return
        if method == 'account/rateLimits/updated':
            # 부분 버킷 갱신은 전체 조회의 신선도를 연장하지 않고 전체 재조회를 요청합니다.
            payload = message.get('params')
            if isinstance(payload, dict) and isinstance(payload.get('rateLimitsByLimitId'), dict):
                self._accept(payload)
            elif isinstance(payload, dict) and isinstance(payload.get('rateLimits'), dict):
                self._accept(payload, notification=True)
                self.refresh()
            return
        if not self.pending or isinstance(message.get('id'), bool) or message.get('id') != self.pending[0]:
            return
        _, request = self.pending
        self.pending = None
        self.deadline.stop()
        if request == 'account/rateLimits/read' and self.pending_epoch != self.account_epoch:
            self._publish(busy=False)
            self.refresh()
            return
        if 'error' in message:
            error = message['error']
            text = str(error.get('message', '')).lower() if isinstance(error, dict) else ''
            auth = any(word in text for word in ('auth', 'login', 'sign in', 'chatgpt', '401', '403'))
            self._failed('설치된 Codex의 ChatGPT 로그인을 확인하세요.' if auth else '계정 한도 조회가 거부됐습니다. Codex 연결을 확인하세요.')
            return
        if not isinstance(message.get('result'), dict):
            self._failed('잔량 응답 결과를 확인할 수 없습니다.')
            return
        if request == 'initialize':
            self._send('initialized', request=False)
            self.ready = True
            self._publish(busy=False)
            self.refresh()
        else:
            self.retries = 0
            self._publish(busy=False)
            self._accept(message['result'])

    def _check_age(self):
        expired = any(number(row['resets_at']) and time.time() >= row['resets_at'] for row in self.snapshot['rows'])
        if self.last_success is not None and (time.monotonic() - self.last_success > 65 or expired) and not self.snapshot['stale']:
            self._publish(stale=True, status='조회 지연 · 이전 조회 값')

    def _timeout(self):
        self._failed('잔량 조회 응답 시간이 초과됐습니다.')

    def manual_refresh(self):
        if self.closed or not self.enabled or self.snapshot['busy'] or self.pending:
            return False
        if not self.ready:
            self.retries = 0
            return self._launch()
        return self.refresh()

    def _process_error(self, _):
        if not self.closed and not self.failed_connection:
            self._failed('Codex 잔량 연결을 실행할 수 없습니다. 설정의 EXE와 설치 상태를 확인하세요.')

    def _finished(self, *_):
        if not self.closed and not self.failed_connection:
            self._failed('Codex 잔량 연결이 종료됐습니다.')

    def _failed(self, status):
        self.deadline.stop()
        self.pending = None
        self.ready = False
        self.buffer.clear()
        self.failed_connection = True
        self._publish(status=status, busy=False, stale=True)
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
        if self.enabled and not self.closed and self.retries < 3 and not self.retry_timer.isActive():
            self.retry_timer.start(3000 * (self.retries + 1))

    def _retry(self):
        if self.closed or self.retries >= 3:
            return
        self.retries += 1
        self._launch()

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.enabled = False
        for timer in (self.poll_timer, self.deadline, self.retry_timer, self.age_timer):
            timer.stop()
        self.pending = None
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.closeWriteChannel()
            self.process.terminate()
            if not self.process.waitForFinished(500):
                self.process.kill()
                self.process.waitForFinished(500)
