"""알림 정책과 현재 관측 상태를 연결하며 실제 변경 원문은 수정하지 않습니다."""
from copy import deepcopy
import math
import time

from i18n import get_language


def tr(ko, en):
    return en if get_language() == 'en' else ko


class NotificationPolicy:
    """집중·음소거는 표시만 조절하고 모든 원래 기록은 계속 수집합니다."""
    def __init__(self, settings, clock=time.time):
        self.settings, self.clock = settings, clock
        value = settings.values.get('workspace37', {})
        self.options = {'notice_duration_seconds': 30, 'visible_limit': 8,
                        'activity_popup': True, 'compact_activity': True, 'sound': False}
        if isinstance(value, dict):
            try:
                self.options.update(self._validated({k: v for k, v in value.items() if k in self.options}))
            except ValueError:
                # 원본 설정은 유지하고 잘못된 새 옵션만 기본 표시로 사용합니다.
                pass
        self.options['sound'] = bool(settings.values.get('notification_sound', self.options['sound']))
        self.focus_until = 0
        self.mutes = {}
        self.suppressed = 0

    @staticmethod
    def _validated(changes):
        for key, value in changes.items():
            if key in ('notice_duration_seconds', 'visible_limit'):
                lower, upper = (5, 120) if key == 'notice_duration_seconds' else (1, 8)
                if type(value) is not int or not lower <= value <= upper:
                    raise ValueError('알림 시간은 5~120초, 표시 수는 1~8개여야 합니다.')
            elif key in ('activity_popup', 'compact_activity', 'sound'):
                if type(value) is not bool:
                    raise ValueError('알림 선택값은 켜짐 또는 꺼짐이어야 합니다.')
            else:
                raise ValueError('지원하지 않는 알림 설정입니다.')
        return changes

    def set_options(self, **changes):
        candidate = {**self.options, **self._validated(changes)}
        before = deepcopy(self.settings.values)
        self.settings.values.update(workspace37=candidate,
                                    notice_timeout_ms=candidate['notice_duration_seconds'] * 1000,
                                    notification_sound=candidate['sound'])
        try:
            self.settings.save()
        except Exception:
            self.settings.values.clear()
            self.settings.values.update(before)
            raise
        self.options = candidate

    def focus(self, minutes):
        if minutes not in (15, 30, 60):
            raise ValueError('집중 시간은 15분, 30분, 60분 중에서 고르세요.')
        self.focus_until = self.clock() + minutes * 60

    def resume(self):
        self.focus_until = 0

    def mute_target(self, target, minutes=30):
        if not isinstance(target, str) or not target or len(target) > 256 or minutes != 30:
            raise ValueError('선택한 채팅을 30분 동안 조용히 표시할 수 있습니다.')
        self.mutes = {k: v for k, v in self.mutes.items() if v > self.clock()}
        if len(self.mutes) >= 64 and target not in self.mutes:
            raise ValueError('음소거한 채팅이 너무 많습니다. 먼저 음소거를 해제하세요.')
        self.mutes[target] = self.clock() + minutes * 60

    def clear_mutes(self):
        self.mutes.clear()

    def allows(self, event, count=True):
        now = self.clock()
        allowed = not (self.focus_until > now or self.mutes.get(event.get('target'), 0) > now)
        if event.get('kind') == 'activity' and not self.options['activity_popup']:
            allowed = False
        if not allowed and count:
            self.suppressed += 1
        return allowed

    def summary(self):
        now = self.clock()
        minutes = max(0, math.ceil((self.focus_until - now) / 60))
        muted = sum(value > now for value in self.mutes.values())
        return (tr(f'집중 모드 {minutes}분 남음', f'Focus: {minutes} min left') if minutes else
                tr('알림 받는 중', 'Notifications on')) + tr(
                    f' · 음소거 {muted}개 · 조용히 기록 {self.suppressed}건',
                    f' · {muted} muted · {self.suppressed} recorded quietly')


def health_snapshot(controller, now=None):
    """실제 진행·작업자 수명으로만 상태를 정하며 채팅 수를 추정하지 않습니다."""
    now = time.monotonic() if now is None else now
    status = controller.last_monitor_status or {}
    age = max(0, int(now - controller.last_monitor_progress))
    if not controller.monitor_enabled:
        kind, label = 'off', tr('감시 꺼짐', 'Monitor off')
    elif controller.monitor_restart_pending:
        kind, label = 'waiting', tr('재연결 중', 'Reconnecting')
    elif controller.monitor is None or not controller.monitor.isRunning():
        kind, label = 'error', tr('감시 중단', 'Monitor stopped')
    elif age > 20:
        kind, label = 'delayed', tr('감시 지연', 'Monitor delayed')
    elif status.get('state') == '감시 중':
        kind, label = 'ok', tr('감시 정상', 'Monitor active')
    elif status.get('state') == '기준선 준비 중':
        kind, label = 'waiting', tr('기존 기록 준비 중', 'Preparing existing records')
    elif status:
        kind, label = 'error', tr('감시 확인 필요', 'Monitor needs attention')
    else:
        kind, label = 'waiting', tr('첫 확인 대기', 'Waiting for first check')
    files = status.get('files')
    count = str(files) if type(files) is int and files >= 0 else '—'
    latest = status.get('time')
    return {'kind': kind, 'label': label, 'age': age, 'files': count,
            'chats': str(status['chats']) if type(status.get('chats')) is int else '—',
            'checked': latest, 'retries': controller.monitor_retries}


def freshness(value):
    checked = value.get('checked_at')
    if type(checked) not in (int, float) or not math.isfinite(checked):
        return tr('아직 확인하지 못함', 'Not checked yet')
    clock = time.strftime('%H:%M:%S', time.localtime(checked))
    return clock + (tr(' · 이전 정보', ' · Earlier data') if value.get('stale') else '')


def install_workspace(controller):
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
    from workspace37 import WorkspacePanel
    c = controller
    strip = QFrame(); strip.setObjectName('controlsBar')
    row = QHBoxLayout(strip); row.setContentsMargins(12, 8, 12, 8)
    c.health_label37 = QLabel(); c.health_label37.setWordWrap(True)
    c.health_label37.setTextFormat(Qt.TextFormat.PlainText)
    row.addWidget(c.health_label37, 1)
    c.retry_button37 = QPushButton(); row.addWidget(c.retry_button37)
    c.retry_button37.clicked.connect(c.retry_monitor37)
    c.window.layout().insertWidget(2, strip)
    c.workspace_panel = WorkspacePanel(c)
    c.workspace_page37 = c.orbit29.stack.addWidget(c.workspace_panel)
    c.workspace_button37 = QPushButton(); c.workspace_button37.setCheckable(True)
    nav = c.orbit29.observatory_button.parentWidget().layout()
    nav.insertWidget(3, c.workspace_button37)
    def open_workspace():
        c.orbit29.stack.setCurrentIndex(c.workspace_page37)
        c.workspace_panel.refresh()
    c.workspace_button37.clicked.connect(open_workspace)
    c.workspace_timer37 = QTimer(c.gui_owner); c.workspace_timer37.setInterval(2000)
    c.workspace_timer37.timeout.connect(lambda: refresh_workspace(c))
    c.workspace_timer37.start()
    c.orbit29.stack.currentChanged.connect(lambda _: refresh_workspace(c))
    refresh_workspace(c, translate=True)


def refresh_workspace(c, translate=False):
    if c.closing or not hasattr(c, 'health_label37'):
        return
    health = health_snapshot(c)
    c.orbit.health37 = health
    c.max_visible_notices = c.workspace_policy.options['visible_limit']
    c.workspace_policy.options['sound'] = bool(c.settings.values.get('notification_sound', False))
    c.workspace_button37.setText(tr('알림 센터', 'Notification center'))
    c.workspace_button37.setChecked(c.orbit29.stack.currentIndex() == c.workspace_page37)
    if c.workspace_button37.isChecked():
        for button in c.orbit29.nav_buttons:
            button.setChecked(False)
    c.retry_button37.setText(tr('감시 다시 연결', 'Reconnect monitor'))
    c.retry_button37.setEnabled(not c.monitor_restart_pending)
    privacy = c.settings.values.get('broadcast_mode', False)
    source = tr('프라이버시 모드에서 경로 숨김', 'Path hidden in privacy mode') if privacy else c.settings.values['sessions']
    info = health['label'] + tr(f" · 최근 진행 {health['age']}초 전 · 복구 {health['retries']}회 · 관측 파일 {health['files']}개",
                              f" · Last progress {health['age']}s ago · {health['retries']} retries · {health['files']} observed files")
    c.health_label37.setText(info)
    c.health_label37.setToolTip(str(source) + '\n' + c.workspace_policy.summary() + '\n' +
        tr('관측된 채팅 ', 'Observed chats ') + health['chats'] + '\n' +
        tr('잔량 조회 ', 'Usage checked ') + freshness(c.usage.snapshot) + '\n' +
        tr('날씨 조회 ', 'Weather checked ') + freshness(c.weather.snapshot))
    if c.workspace_panel.isVisible():
        if translate:
            c.workspace_panel.retranslate()
        c.workspace_panel.refresh()
    c.orbit.update()
