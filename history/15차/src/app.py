"""Codex Orbit: 독립 회전 위젯과 로컬 변경 기록·사용 한도."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timezone, timedelta
import re
from collections import deque

from PySide6.QtCore import QEvent, QObject, QLockFile, Qt, QThread, QTimer, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (QApplication, QDialog,
                             QFrame, QGridLayout, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QMenu, QMessageBox,
                             QPlainTextEdit, QPushButton, QSplitter, QTabWidget,
                             QProgressBar, QScrollArea, QSizePolicy, QLayout, QVBoxLayout, QWidget)

from core import clamp_position, read_jsonl_tail, read_text_strict, title_catalog, resolve_title
from notifier import Watcher, append_log, atomic_json, stamp, POLL_INTERVAL_SECONDS
from usage import UsageClient, reset_label
from visuals import draw_orbit
from atom_frames import get_atom_frames
from brand import brand_image
from theme import STYLE, apply_theme


def asset(name):
    root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
    return root / 'assets' / name


def operation_record(directory, stage, sessions=None, error=None, **details):
    """대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다."""
    value = {'time': stamp(), 'kst': datetime.now(timezone(timedelta(hours=9))).isoformat(),
             'pid': os.getpid(), 'executable': sys.executable, 'cwd': str(Path.cwd()),
             'data_dir': str(Path(directory).absolute()),
             'sessions': str(Path(sessions).absolute()) if sessions is not None else None,
             'stage': stage, **details}
    if error is not None:
        value['error'] = str(error)[:2000]
    try:
        append_log(Path(directory) / 'startup.jsonl', value)
    except Exception as log_error:
        return str(log_error)
    return None


def model_label(value):
    if value is None:
        return '미배정'
    return f"{value.get('model', '확인 불가')} / {value.get('effort', '확인 불가')}"


def model_card_label(value):
    if value is None:
        return '미배정'
    return f"{value.get('model', '확인 불가')} · 추론 {value.get('effort', '확인 불가')}"


def friendly_model(value):
    return {'gpt-6.1-sol': 'Sol', 'gpt-6-sol': 'Sol', 'gpt-6-astra': 'Astra',
            'gpt-6-luna': 'Luna'}.get(value, str(value or '미배정'))


def friendly_effort(value):
    labels = {'none': '없음', 'minimal': '최소', 'low': '낮음', 'medium': '보통',
              'high': '높음', 'xhigh': '매우 높음', 'ultra': '최고'}
    return labels.get(value, str(value or '미확인')) + (f' ({value})' if value in labels else '')


ROLE_LABELS = {'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',
               'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}


def kst_label(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            return str(value) + ' (시간대 미기록)'
        return parsed.astimezone(timezone(timedelta(hours=9))).strftime('%Y.%m.%d %H:%M:%S KST')
    except ValueError:
        return str(value or '확인 불가')


def short_reason(event, limit=180):
    """명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다."""
    text = str(event.get('short_reason') or event.get('reason') or '확인 불가').strip()
    marked = re.search(r'(?:핵심 이유|선택 이유|이유)\s*[:：]\s*([^\n]+)', text)
    if marked:
        text = marked.group(1)
    else:
        sentences = [sentence for sentence in re.split(r'(?<=[.!?。])\s+|\n', text) if sentence.strip()]
        purpose = None if event.get('short_reason') else next((sentence for sentence in sentences if re.search(
            r'위한\s+(?:배정|선택|변경|교체)|(?:배정|선택|변경|교체)(?:의|한)?\s*(?:이유|목적)'
            r'|(?:때문|확인돼|확인되어).*(?:배정|선택|변경|교체)', sentence)), None)
        if not purpose and not event.get('short_reason'):
            for index, sentence in enumerate(sentences[:-1]):
                if re.search(r'(?:배정합니다|배정하겠습니다|맡기겠습니다)[.!]?$', sentence.replace('**', '').strip()):
                    candidate = sentences[index + 1].strip()
                    if re.search(r'(?:대조|검사|확인|검토|검증|구현|수정)', candidate):
                        purpose = candidate
                        break
        text = purpose or (sentences[0] if sentences else '확인 불가')
        if not purpose and len(sentences) > 1 and len(text) < 70 and re.search(r'(?:맡기겠습니다|배정하겠습니다)[.!]?$', text):
            text = sentences[1]
    text = text.replace('**', '')
    return text if len(text) <= limit else text[:limit - 1] + '…'


def event_kind(event):
    if event.get('kind') == 'settings':
        if event.get('before') is None:
            return '자식 작업자 첫 선택 설정 관측' if event.get('parent') else '채팅 선택 설정 첫 관측'
        return '채팅 선택 설정 변경'
    if event.get('assignment_type') == 'replacement':
        return '새 작업자 배정 · 이전 작업자 교체'
    if event.get('before') is None:
        return '자식 작업자 첫 배정' if event.get('parent') else '첫 관측'
    return '모델 · 추론 강도 변경'


def event_description(event):
    return '\n'.join([
        '채팅: ' + str(event.get('chat_name') or event.get('target', '확인 불가')),
        '채팅 ID: ' + str(event.get('target', '확인 불가')),
        '구분: ' + ('자식 작업' if event.get('parent') else 'main 또는 부모 정보 미기록'),
        '역할: ' + str(event.get('role', '확인 불가')),
        '작업 이름: ' + str(event.get('task_name') or '기록 없음'),
        '부모 ID: ' + str(event.get('parent') or '기록 없음'),
        '작업 경로: ' + str(event.get('agent_path') or '기록 없음'),
        '제목 출처: ' + str(event.get('title_source') or '확인 불가'),
        '제목 확인 시각: ' + kst_label(event.get('title_checked_at')),
        '이유 호출 ID: ' + str(event.get('reason_call_id') or '기록 없음'),
        '변경 전: ' + model_label(event.get('before')),
        '변경 후: ' + model_label(event.get('after')),
        '감지 시각: ' + kst_label(event.get('time')),
        '원본 기록 시각: ' + kst_label(event.get('source_time')),
        '기록 종류: ' + str(event.get('kind', '확인 불가')),
        '', '공개 이유', str(event.get('reason') or '확인 불가'),
        '', '근거 수준', str(event.get('evidence') or '확인 불가'),
        '', '선택 설정 관측 근거', str(event.get('configuration_evidence') or '해당 없음'),
        '', '표시 기록', str(event.get('delivery') or '앱 표시 요청; 사용자 수신 미확인'),
        '', '로컬 기록과 공개 이유의 연결 근거입니다. 서버 모델 신원이나 비공개 추론을 증명하지 않습니다.'
    ])


class Settings:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / 'settings.json'
        home = Path(os.environ.get('CODEX_HOME') or (Path.home() / '.codex'))
        self.values = {'sessions': str(home / 'sessions'), 'theme': '자동', 'popup': True, 'notice_timeout_ms': 30000}
        if self.path.exists():
            value = json.loads(read_text_strict(self.path))
            if not isinstance(value, dict):
                raise ValueError('앱 설정은 JSON 객체여야 합니다.')
            self.values.update(value)

    def save(self):
        atomic_json(self.path, self.values)


class Monitor(QThread):
    event = Signal(dict)
    status = Signal(dict)
    enriched = Signal(list)

    def __init__(self, sessions, directory):
        super().__init__()
        self.sessions = Path(sessions)
        key = hashlib.sha256(str(self.sessions.absolute()).encode('utf-8')).hexdigest()[:16]
        self.work = Path(directory) / 'watches' / key
        self.directory = Path(directory)
        self.cache_path = Path(directory) / 'title-cache.json'
        self.titles = {}
        self.recent_errors = deque(maxlen=5)

    def send(self, event):
        value = resolve_title(event, self.titles)
        value['delivery'] = '앱 표시 요청; 사용자 수신 미확인'
        self.event.emit(value)
        return value['delivery']

    def run(self):
        watcher = None
        try:
            watcher = Watcher(self.sessions, self.work, self.send)
            while not self.isInterruptionRequested():
                try:
                    watcher.diagnostic_failures.clear()
                    if not self.sessions.is_dir():
                        raise FileNotFoundError('세션 폴더가 없거나 접근할 수 없습니다: ' + str(self.sessions))
                    self.titles = title_catalog(self.sessions.parent / 'session_index.jsonl', self.cache_path)
                    watcher.poll()
                    history, _ = read_jsonl_tail(self.work / 'history.jsonl')
                    values = []
                    for event in history:
                        if event.get('reason') == '확인 불가':
                            watcher.lookup_parent_reason(event)
                        values.append(resolve_title(watcher.enrich_event(event), self.titles))
                    self.enriched.emit(values)
                    atomic_json(watcher.state_path, watcher.state)
                    diagnostics, problems = read_jsonl_tail(self.work / 'diagnostics.jsonl', max_records=5)
                    remaining = sum(max(0, info.get('baseline_end', 0) - info['offset'])
                                    for info in watcher.state['files'].values())
                    status = {'time': stamp(), 'state': '기준선 준비 중' if remaining else '감시 중', 'sessions': str(self.sessions),
                              'files': len(watcher.state['files']), 'pending': len(watcher.state['pending']),
                              'baseline_remaining_bytes': remaining,
                              'diagnostics': diagnostics, 'read_problems': problems,
                              'recent_errors': list(self.recent_errors)}
                    if watcher.diagnostic_failures:
                        status['state'] = '오류 · 진단 기록 실패 · 다음 주기 재시도'
                        status['diagnostic_write_failures'] = list(watcher.diagnostic_failures)
                        self.recent_errors.extend(watcher.diagnostic_failures)
                        status['recent_errors'] = list(self.recent_errors)
                        for failure in watcher.diagnostic_failures:
                            log_error = operation_record(self.directory, 'monitor-diagnostic-failed', self.sessions,
                                                         failure['error'], diagnostic_error=failure['diagnostic_error'])
                            if log_error:
                                status['operation_log_error'] = log_error
                    self.status.emit(status)
                    atomic_json(self.work / 'heartbeat.json', status)
                except Exception as error:
                    self.report_failure(error, watcher)
                for _ in range(max(1, round(POLL_INTERVAL_SECONDS / 0.1))):
                    if self.isInterruptionRequested():
                        break
                    self.msleep(100)
        except Exception as error:
            self.report_failure(error, watcher, stopped=True)

    def report_failure(self, error, watcher, stopped=False):
        value = {'time': stamp(), 'state': '감시 중단 · 상태 점검 필요' if stopped else '오류 · 다음 주기 재시도',
                 'error': str(error), 'sessions': str(self.sessions)}
        if watcher is not None:
            try:
                diagnostic_failure = watcher.diagnostic(error)
                if diagnostic_failure:
                    value['diagnostic_error'] = diagnostic_failure['diagnostic_error']
                    value['state'] += ' · 진단 기록 실패'
            except Exception as diagnostic_error:
                value['diagnostic_error'] = str(diagnostic_error)
                value['state'] += ' · 진단 기록 실패'
        log_error = operation_record(self.directory, 'monitor-stopped' if stopped else 'monitor-retry',
                                     self.sessions, error, diagnostic_error=value.get('diagnostic_error'))
        if log_error:
            value['operation_log_error'] = log_error
        self.recent_errors.append(dict(value))
        self.status.emit(value)


class OrbitWidget(QWidget):
    def __init__(self, settings, details, quit_app):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle('Codex Orbit')
        self.setFixedSize(148, 148)
        self.settings, self.details = settings, details
        self.quit_app = quit_app
        self.origin_time = time.monotonic()
        self.render_time = None
        self.healthy = False
        self.unread = False
        self.usage_badge = '—'
        self.usage_fraction = None
        self.usage_state = 'unknown'
        self.press_global = None
        self.dragged = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setToolTip('Codex Orbit · 클릭: 상세 · 드래그: 이동 · 우클릭: 기록/종료')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(20)
        self.restore_position()
        for screen in QApplication.screens():
            screen.availableGeometryChanged.connect(self.restore_position)
        QApplication.instance().screenRemoved.connect(lambda _: self.restore_position())

    def restore_position(self, *_):
        screens = [(r.x(), r.y(), r.width(), r.height()) for r in
                   [screen.availableGeometry() for screen in QApplication.screens()]]
        value = self.settings.values.get('position', [900000, 900000])
        if not isinstance(value, (list, tuple)) or len(value) != 2 or not all(isinstance(v, int) for v in value):
            value = [900000, 900000]
        self.move(*clamp_position(value, screens, self.width()))

    def paintEvent(self, _):
        elapsed = self.render_time if self.render_time is not None else time.monotonic() - self.origin_time
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        draw_orbit(painter, elapsed, self.usage_badge, self.usage_fraction, self.usage_state,
                   self.healthy, self.unread, self.settings.values.get('theme') == '밝은 배경')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_global = event.globalPosition().toPoint()
            self.press_position = self.pos()
            self.dragged = False
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self.press_global is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.press_global
            if delta.manhattanLength() > QApplication.startDragDistance():
                self.dragged = True
            if self.dragged:
                self.move(self.press_position + delta)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.press_global is not None:
            self.press_global = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            if self.dragged:
                self.settings.values['position'] = [self.x(), self.y()]
                try:
                    self.settings.save()
                except Exception as error:
                    QMessageBox.warning(self, '위치 저장 실패', str(error))
            else:
                self.unread = False
                self.details()

    def contextMenuEvent(self, event):
        menu = self.create_menu()
        menu.exec(event.globalPos())

    def create_menu(self):
        menu = QMenu(self)
        menu.addAction('상세 이력 열기', self.details)
        menu.addSeparator()
        menu.addAction('종료', self.quit_app)
        return menu


class Notice(QFrame):
    completed = Signal(str)

    def __init__(self, open_details):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.open_details = open_details
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setObjectName('notice')
        self.setStyleSheet('#notice {background:#141414;border:1px solid #666666;border-radius:10px;} QLabel {color:#F1F1F1;background:transparent;border:none;font-weight:700;}')
        self.setFixedWidth(410)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(7)
        self.title = QLabel('모델 · 추론 강도 변경')
        self.text = QLabel()
        self.title.setTextFormat(Qt.TextFormat.PlainText)
        self.title.setWordWrap(True)
        self.title.setStyleSheet('font-size:16px;color:#FFFFFF;')
        self.text.setTextFormat(Qt.TextFormat.PlainText)
        self.text.setWordWrap(True)
        heading = QHBoxLayout()
        self.brand_mark = QLabel()
        self.brand_mark.setPixmap(QPixmap.fromImage(brand_image(24)))
        self.brand_mark.setFixedSize(24, 24)
        self.brand_mark.setAccessibleName('Codex Orbit 로고')
        self.brand_mark.setToolTip('Codex Orbit')
        heading.addWidget(self.brand_mark, 0, Qt.AlignmentFlag.AlignTop)
        heading.addWidget(self.title, 1)
        close = QPushButton('닫기')
        close.setToolTip('알림 닫기 · 이력은 유지됩니다')
        close.setStyleSheet('padding:0;min-height:28px;max-height:28px;font-size:12px;')
        close.setFixedSize(48, 30)
        close.clicked.connect(self.dismiss)
        heading.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(heading)
        self.category = QLabel()
        self.category.setStyleSheet('font-size:18px;color:#f8f8f8;padding:4px 0;')
        self.category.setWordWrap(True)
        self.category.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.category)
        values = QHBoxLayout()
        values.setSpacing(16)
        self.model_previous = QLabel()
        self.model_current = QLabel()
        self.effort_previous = QLabel()
        self.effort_current = QLabel()
        for previous, current, size in ((self.model_previous, self.model_current, 26),
                                        (self.effort_previous, self.effort_current, 24)):
            column = QVBoxLayout()
            column.setSpacing(4)
            for label, pixels, color in ((previous, 11, '#aaaaaa'), (current, size, '#ffffff')):
                label.setWordWrap(True)
                label.setTextFormat(Qt.TextFormat.PlainText)
                label.setStyleSheet(f'font-size:{pixels}px;color:{color};padding:0;')
                column.addWidget(label)
            column.addStretch()
            values.addLayout(column, 1)
        layout.addLayout(values)
        # 기존 필드는 실제 보이는 이전 행과 연결하며 숨김 호환 라벨은 만들지 않습니다.
        self.before_value = self.model_previous
        self.transition = self.model_previous
        self.after_value = QLabel()
        self.after_value.setWordWrap(True)
        self.after_value.setTextFormat(Qt.TextFormat.PlainText)
        self.after_value.setStyleSheet('font-size:11px;color:#999999;padding:0;')
        layout.addWidget(self.after_value)
        self.text.setStyleSheet('font-size:12px;color:#C9C9C9;')
        layout.addWidget(self.text)
        hint = QLabel('이 변경 자세히 보기  ›')
        hint.setStyleSheet('font-size:12px;color:#FFFFFF;')
        layout.addWidget(hint)
        self.queue_hint = QLabel('')
        self.queue_hint.setWordWrap(True)
        self.queue_hint.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.queue_hint)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.dismiss)

    def dismiss(self):
        if not self.isVisible():
            return
        self.timer.stop()
        self.hide()
        self.completed.emit(str(getattr(self, 'event_id', '')))

    def closeEvent(self, event):
        self.dismiss()
        super().closeEvent(event)

    def fit_content(self, rect=None):
        # 제목은 닫기 버튼을 뺀 실제 폭으로 측정하며 원본 이벤트는 바꾸지 않습니다.
        if rect is not None:
            self.available_rect = rect
        self.layout().activate()
        margins = self.layout().contentsMargins()
        width = self.contentsRect().width() - margins.left() - margins.right()
        self.text.setMinimumHeight(self.text.heightForWidth(width))
        full_title = str(getattr(self, 'event', {}).get('chat_name') or '채팅 제목 확인 불가')
        self.title.setToolTip(full_title)
        self.title.setText(full_title)
        self.title.setMinimumHeight(0)
        self.title.setMaximumHeight(16777215)
        title_width = max(1, self.title.width())
        needed = max(self.title.fontMetrics().height(), self.title.heightForWidth(title_width))
        self.title.setFixedHeight(needed)
        self.layout().activate()
        self.adjustSize()
        rect = getattr(self, 'available_rect', None)
        if rect is not None and self.height() > rect.height():
            budget = max(self.title.fontMetrics().height(), needed - (self.height() - rect.height()))
            # 화면을 넘는 제목만 명시적으로 줄이고 전체 원문은 툴팁과 상세에 남깁니다.
            self.title.setMinimumHeight(0)
            self.title.setMaximumHeight(16777215)
            low, high = 0, len(full_title)
            while low < high:
                middle = (low + high + 1) // 2
                self.title.setText(full_title[:middle].rstrip() + '…')
                if self.title.heightForWidth(title_width) <= budget:
                    low = middle
                else:
                    high = middle - 1
            self.title.setText(full_title[:low].rstrip() + '…')
            self.title.setFixedHeight(max(self.title.fontMetrics().height(), self.title.heightForWidth(title_width)))
            self.layout().activate()
            self.adjustSize()

    def display(self, event, orbit, timeout_ms=30000, replay=False):
        screen = QApplication.screenAt(orbit.pos()) or QApplication.primaryScreen()
        self.available_rect = screen.availableGeometry()
        self.update_event(event, replay)
        rect = self.available_rect
        self.move(max(rect.left(), min(orbit.x() - self.width(), rect.right() - self.width() + 1)),
                  max(rect.top(), min(orbit.y(), rect.bottom() - self.height() + 1)))
        self.show()
        self.appearance = QPropertyAnimation(self, b'windowOpacity', self)
        self.appearance.setDuration(180)
        self.appearance.setStartValue(.92)
        self.appearance.setEndValue(1.)
        self.appearance.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.appearance.start()
        self.timer.stop()
        if timeout_ms != 0:
            self.timer.start(max(30000, min(300000, int(timeout_ms))))

    def update_event(self, event, replay=None):
        # 제목 보강과 동일 ID 갱신은 다른 카드나 남은 표시 시간을 바꾸지 않습니다.
        if replay is not None:
            self.replay = replay
        self.event = dict(event)
        self.event_id = event.get('id')
        name = str(event.get('chat_name') or '채팅 제목 확인 불가')
        self.title.setText(name)
        before, after = event.get('before'), event.get('after')
        if before is None:
            category = event_kind(event)
        else:
            model_changed = before.get('model') != (after or {}).get('model')
            effort_changed = before.get('effort') != (after or {}).get('effort')
            category = ('모델·추론 변경' if model_changed and effort_changed else '모델 변경' if model_changed
                        else '추론 강도 변경' if effort_changed else '설정 관측')
        if event.get('kind') == 'settings':
            category += ' · 선택 설정'
        self.category.setText(category)
        before_map, after_map = before or {}, after or {}
        self.model_previous.setText('이전 모델  ' + friendly_model(before_map.get('model')))
        self.model_current.setText(friendly_model(after_map.get('model')))
        self.effort_previous.setText('이전 추론  ' + friendly_effort(before_map.get('effort')))
        self.effort_current.setText(friendly_effort(after_map.get('effort')))
        self.before_value.setText('이전  ' + self.setting_label(before))
        self.after_value.setText('→ 변경 후\n' + self.setting_label(after))
        reason = short_reason(event)
        reason = '확인되지 않음' if reason == '확인 불가' else reason
        self.text.setText(('기록 다시 보기 · ' if self.replay else '') + '변경 이유: ' + reason)
        self.fit_content()

    @staticmethod
    def setting_label(value):
        if value is None:
            return '미배정 · 이전 값 없음'
        effort = value.get('effort')
        labels = {'none': '없음', 'minimal': '최소', 'low': '낮음', 'medium': '보통',
                  'high': '높음', 'xhigh': '매우 높음', 'ultra': '최고'}
        strength = f'{labels[effort]} ({effort})' if effort in labels else str(effort or '확인 불가')
        return str(value.get('model') or '모델 확인 불가') + '\n추론 ' + strength

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_details(self.event_id)
            self.dismiss()


class DiagnosticLabel(QLabel):
    """오류가 있을 때 변경 기록 안에 원문을 보여 주는 읽기 전용 라벨입니다."""
    def __init__(self):
        super().__init__()
        self.setWordWrap(True)
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setStyleSheet('font-size:12px;color:#dddddd;border-left:2px solid #aaaaaa;padding:10px;')
        self.original_text = ''
        self.hide()
    def setPlainText(self, text):
        self.original_text = str(text)
        try:
            value = json.loads(text)
            failed = any(value.get(key) for key in ('error','diagnostic_error','notice_presentation_error',
                'operation_log_error','diagnostic_write_failures','recent_errors','read_problems'))
            failed = failed or any(word in value.get('state','') for word in ('오류','실패','중단','지연'))
        except (ValueError, TypeError, AttributeError):
            failed = bool(text)
        self.setText('감시 진단\n' + self.original_text if failed else '')
        self.setVisible(bool(failed))
    def toPlainText(self):
        return self.original_text


class Details(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Codex Orbit · 로컬 모델 변경 기록')
        self.resize(1120, 780)
        self.setMinimumSize(740, 540)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 20)
        layout.setSpacing(10)
        header = QHBoxLayout()
        self.brand_mark = QLabel()
        self.brand_mark.setPixmap(QPixmap.fromImage(brand_image(32)))
        self.brand_mark.setFixedSize(32, 32)
        self.brand_mark.setAccessibleName('Codex Orbit 로고')
        self.brand_mark.setToolTip('Codex Orbit')
        header.addWidget(self.brand_mark)
        self.setWindowIcon(QIcon(QPixmap.fromImage(brand_image(32))))
        heading = QLabel('Codex Orbit')
        heading.setStyleSheet('font-size:19px;color:#f5f5f5;')
        header.addWidget(heading, 1)
        self.usage_compact = QLabel('사용 한도 미확인')
        self.usage_compact.setStyleSheet('font-size:12px;color:#b0b0b0;')
        header.addWidget(self.usage_compact)
        layout.addLayout(header)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)
        self.build_history()
        usage_page = QWidget()
        usage_layout = QVBoxLayout(usage_page)
        usage_layout.setContentsMargins(32, 28, 32, 28)
        self.build_usage(usage_layout)
        usage_layout.addStretch()
        self.tabs.insertTab(1, usage_page, '사용 한도')
        self.setStyleSheet(STYLE)

    def build_usage(self, layout):
        panel = QFrame()
        panel.setObjectName('eventCard')
        box = QVBoxLayout(panel)
        heading = QHBoxLayout()
        title = QLabel('계정 사용 한도 · 남은 비율')
        title.setStyleSheet('color:#eeeeee;font-size:25px;padding-bottom:18px;')
        heading.addWidget(title, 1)
        self.usage_refresh = QPushButton('새로고침')
        self.usage_refresh.clicked.connect(lambda: self.controller.usage.manual_refresh())
        heading.addWidget(self.usage_refresh)
        box.addLayout(heading)
        self.usage_status = QLabel('잔량 조회 준비 · 30초마다 자동 갱신')
        self.usage_status.setWordWrap(True)
        self.usage_status.setTextFormat(Qt.TextFormat.PlainText)
        box.addWidget(self.usage_status)
        self.usage_values = QLabel('계정 한도 미확인')
        self.usage_values.setWordWrap(True)
        self.usage_values.setTextFormat(Qt.TextFormat.PlainText)
        self.usage_scroll = QScrollArea()
        self.usage_scroll.setWidgetResizable(True)
        self.usage_scroll.setMinimumHeight(200)
        self.usage_rows = QWidget()
        self.usage_rows_layout = QVBoxLayout(self.usage_rows)
        self.usage_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.usage_rows_layout.addWidget(self.usage_values)
        self.usage_scroll.setWidget(self.usage_rows)
        box.addWidget(self.usage_scroll)
        layout.addWidget(panel)

    def display_usage(self, value):
        stale, busy = value.get('stale', True), value.get('busy', False)
        checked = value.get('checked_at')
        updated = reset_label(checked) if checked else '아직 조회하지 않음'
        self.usage_status.setText(('지연 · ' if stale and checked else '') + value.get('status', '미확인') +
                                  '  ·  최종 조회: ' + updated + '  ·  30초 자동 갱신')
        self.usage_refresh.setEnabled(not busy)
        rows = value.get('rows', [])
        texts = []
        while self.usage_rows_layout.count() > 1:
            child = self.usage_rows_layout.takeAt(1).widget()
            child.deleteLater()
        for row in rows:
            remaining = row['remaining']
            label = f"{remaining:g}% 남음" if remaining is not None else '잔량 미확인'
            text = f"{row['bucket']} · {row['period']}  {label}  ·  초기화: {reset_label(row['resets_at'])}"
            if stale:
                text += '  ·  이전 조회 값'
            texts.append(text)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(round(remaining) if remaining is not None else 0)
            bar.setFormat(row['period'] + (' · 이전 조회' if stale else '') + ' · ' + label)
            bar.setEnabled(not stale and remaining is not None)
            bar.setFixedHeight(19)
            bar.setStyleSheet('QProgressBar {border:1px solid #3C3C3C;border-radius:4px;text-align:center;background:#131313;color:#EEEEEE;} QProgressBar::chunk {background:#555555;}')
            self.usage_rows_layout.addWidget(bar)
        self.usage_compact.setText(('이전 조회 · ' if stale and checked else '') + (f"{rows[0]['remaining']:g}% 남음" if rows and rows[0].get('remaining') is not None else '사용 한도 미확인'))
        self.usage_values.setText('\n'.join(texts) if texts else '계정 한도 미확인 · 남은 토큰 개수가 아닌 사용 한도 비율입니다.')

    def build_history(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(8)
        self.summary = QLabel('감시 준비 중')
        self.summary.setStyleSheet('color:#888888;font-size:11px;')
        self.summary.setTextFormat(Qt.TextFormat.PlainText)
        self.summary.setWordWrap(True)
        self.summary.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        layout.addWidget(self.summary)
        self.notice_summary = QLabel('알림 대기 0건')
        self.notice_summary.setStyleSheet('color:#888888;font-size:11px;')
        layout.addWidget(self.notice_summary)
        self.notice_summary.setWordWrap(True)
        split = QSplitter()
        self.history = QListWidget()
        self.history.setWordWrap(True)
        self.history.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history.currentItemChanged.connect(self.select_event)
        panel = QWidget()
        cards = QVBoxLayout(panel)
        cards.setContentsMargins(24, 6, 0, 0)
        cards.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.card = QFrame()
        self.card.setObjectName('eventCard')
        self.card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 12, 20, 20)
        card_layout.setSpacing(12)
        self.chat_title = QLabel('변경을 기다리고 있습니다')
        self.chat_title.setStyleSheet('font-size:25px;color:#F8F8F8;padding:8px 0;')
        self.change_heading = QLabel('변경을 기다리고 있습니다')
        self.change_heading.setStyleSheet('font-size:12px;color:#999999;padding:0 0 12px 0;')
        self.model_transition = QLabel('')
        self.model_transition.setStyleSheet('font-size:21px;color:#a0a0a0;')
        self.model_previous = self.model_transition
        self.model_current = QLabel('—')
        self.model_current.setStyleSheet('font-size:26px;color:#eeeeee;')
        self.effort_transition = QLabel('')
        self.effort_transition.setStyleSheet('font-size:21px;color:#a0a0a0;')
        self.effort_previous = self.effort_transition
        self.effort_current = QLabel('—')
        self.effort_current.setStyleSheet('font-size:26px;color:#eeeeee;')
        self.before_value = QLabel('변경 전  ·  —')
        self.after_value = QLabel('변경 후  ·  —')
        self.after_value.setStyleSheet('font-size:12px;color:#a0a0a0;padding:0;')
        self.before_value.setStyleSheet('font-size:12px;color:#888888;')
        self.reason_title = QLabel('변경 이유 · 공개 기록')
        self.reason_title.setStyleSheet('color:#A4A4A4;font-size:11px;padding-top:10px;')
        self.reason_value = QLabel('첫 실행은 과거 기록을 기준선으로 읽으며 과거 알림을 만들지 않습니다.')
        self.reason_value.setStyleSheet('font-size:16px;padding:4px 0 12px 0;')
        self.event_time = QLabel('')
        self.event_time.setStyleSheet('color:#969696;font-size:11px;padding-top:12px;')
        all_labels = (self.chat_title, self.event_time, self.change_heading, self.model_previous, self.model_current,
                      self.effort_previous, self.effort_current, self.before_value, self.after_value,
                      self.reason_title, self.reason_value)
        for label in all_labels:
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        for label in (self.event_time, self.chat_title, self.change_heading):card_layout.addWidget(label)
        table = QGridLayout()
        table.setHorizontalSpacing(18)
        table.setVerticalSpacing(12)
        for row, (kind, previous, current) in enumerate((('모델',self.model_previous,self.model_current),
                                                       ('추론 강도',self.effort_previous,self.effort_current))):
            for col, text in ((0,'이전 '+kind),(2,'새 '+kind)):
                label=QLabel(text);label.setStyleSheet('font-size:12px;color:#999999;');table.addWidget(label,row*3,col)
            arrow=QLabel('→');arrow.setStyleSheet('font-size:16px;color:#888888;')
            table.addWidget(previous,row*3+1,0)
            table.addWidget(arrow,row*3+1,1)
            table.addWidget(current,row*3+1,2)
            line=QFrame();line.setFrameShape(QFrame.Shape.HLine);line.setStyleSheet('color:#303030;')
            table.addWidget(line,row*3+2,0,1,3)
        table.setColumnStretch(0,1);table.setColumnStretch(2,1)
        card_layout.addLayout(table)
        for label in (self.before_value,self.after_value,self.reason_title,self.reason_value):card_layout.addWidget(label)
        self.diagnostics = DiagnosticLabel()
        cards.addWidget(self.diagnostics)
        cards.addWidget(self.card)
        self.evidence_toggle = QPushButton('▸ 원문 · ID · 근거 펼치기')
        self.evidence_toggle.setObjectName('disclosure')
        self.evidence_toggle.setCheckable(True)
        cards.addWidget(self.evidence_toggle)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        self.detail.setMinimumHeight(180)
        self.detail.setPlainText('변경을 감지하면 이곳에서 전후 값과 공개 이유를 확인할 수 있습니다.\n첫 실행은 과거 기록을 기준선으로 읽으며 과거 알림을 만들지 않습니다.')
        self.detail.hide()
        self.evidence_toggle.toggled.connect(self.toggle_evidence)
        cards.addWidget(self.detail, 1)
        cards.addStretch()
        # 카드와 펼친 원문이 서로 높이를 빼앗지 않도록 우측 전체를 스크롤합니다.
        self.history_detail_scroll = QScrollArea()
        self.history_detail_scroll.setWidgetResizable(True)
        self.history_detail_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.history_detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history_detail_scroll.setWidget(panel)
        split.addWidget(self.history)
        split.addWidget(self.history_detail_scroll)
        split.setChildrenCollapsible(False)
        self.history.setMinimumWidth(200)
        split.setSizes([310, 700])
        layout.addWidget(split, 1)
        self.tabs.addTab(page, '변경 기록')

    def select_event(self, current, _previous):
        if current:
            value = current.data(Qt.ItemDataRole.UserRole)
            self.detail.setPlainText(event_description(value))
            self.chat_title.setText(str(value.get('chat_name') or '채팅 제목 확인 불가'))
            before, after = value.get('before') or {}, value.get('after') or {}
            model_changed = before.get('model') != after.get('model')
            self.change_heading.setText('모델이 바뀌었습니다' if model_changed else '추론 강도가 바뀌었습니다')
            self.model_previous.setText(str(before.get('model') or '미배정'))
            self.model_current.setText(str(after.get('model') or '확인 불가'))
            self.effort_previous.setText(friendly_effort(before.get('effort')))
            self.effort_current.setText(friendly_effort(after.get('effort')))
            self.before_value.setText('이전  ' + model_card_label(value.get('before')))
            self.after_value.setText('→  ' + model_card_label(value.get('after')))
            self.reason_value.setText(short_reason(value, 180))
            self.event_time.setText(kst_label(value.get('time')))

    def toggle_evidence(self, checked):
        self.detail.setVisible(checked)
        self.evidence_toggle.setText('▾ 원문 · ID · 근거 접기' if checked else '▸ 원문 · ID · 근거 펼치기')

    def update_event(self, event):
        for index in range(self.history.count()):
            item = self.history.item(index)
            old = item.data(Qt.ItemDataRole.UserRole)
            if event.get('id') and old.get('id') == event['id']:
                item.setData(Qt.ItemDataRole.UserRole, event)
                item.setText(str(event.get('chat_name') or '채팅 제목 확인 불가') + '\n' + model_label(event.get('after')))
                if item == self.history.currentItem():
                    self.select_event(item, None)
                return True
        return False

    def add_event(self, event):
        if self.update_event(event):
            return
        item = QListWidgetItem(str(event.get('chat_name') or event.get('target'))[:100] + '\n' + model_label(event.get('after'))[:100])
        item.setData(Qt.ItemDataRole.UserRole, event)
        self.history.insertItem(0, item)
        while self.history.count() > 500:
            self.history.takeItem(self.history.count() - 1)
        self.history.setCurrentItem(item)



class QuitGuard(QObject):
    """직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다."""
    def __init__(self, controller):
        super().__init__(QApplication.instance())
        self.controller = controller

    def eventFilter(self, watched, event):
        if watched is QApplication.instance() and event.type() == QEvent.Type.Quit and not self.controller.quit_ready:
            event.ignore()
            QTimer.singleShot(0, self.controller.request_quit)
            return True
        return False


class Controller:
    def __init__(self, settings, start_worker=True, start_usage=None):
        # 필수 이미지가 손상됐으면 타이머나 창을 만들기 전에 시작 실패로 전달합니다.
        get_atom_frames()
        apply_theme()
        self.settings = settings
        self.monitor = None
        self.closing = False
        self.cleaned = False
        self.quit_requested = False
        self.quit_ready = False
        self.monitor_enabled = start_worker
        self.last_monitor_progress = time.monotonic()
        self.monitor_retries = 0
        self.monitor_restart_pending = False
        self.notices = {}
        self.max_visible_notices = 8
        self.notice_overflow = 0
        self.presentation_error = None
        self.operation_log_error = None
        self.monitor_retry_timer = QTimer()
        self.monitor_retry_timer.setSingleShot(True)
        self.monitor_retry_timer.timeout.connect(self.restart_dead_monitor)
        self.monitor_health_timer = QTimer()
        self.monitor_health_timer.setInterval(1000)
        self.monitor_health_timer.timeout.connect(self.check_monitor_health)
        self.window = Details(self)
        self.orbit = OrbitWidget(settings, self.show, self.request_quit)
        self.notice = None
        for screen in QApplication.screens():
            screen.availableGeometryChanged.connect(self.layout_notices)
        QApplication.instance().screenRemoved.connect(self.layout_notices)
        self.usage = UsageClient(settings.values.get('codex_exe', ''))
        self.usage.changed.connect(self.update_usage)
        self.update_usage(self.usage.snapshot)
        self.quit_guard = QuitGuard(self)
        QApplication.instance().installEventFilter(self.quit_guard)
        if start_worker:
            try:
                self.start_monitor()
                self.monitor_health_timer.start()
            except Exception:
                # 필수 준비 실패 시 오류창의 이벤트 루프에 회전 위젯을 남기지 않습니다.
                self.close()
                raise
        self.orbit.show()
        if (start_worker if start_usage is None else start_usage):
            self.usage.start()

    def restart_usage(self):
        self.usage.close()
        self.usage.deleteLater()
        self.usage = UsageClient(self.settings.values.get('codex_exe', ''))
        self.usage.changed.connect(self.update_usage)
        self.update_usage(self.usage.snapshot)
        self.usage.start()

    def update_usage(self, value):
        self.window.display_usage(value)
        valid = [row for row in value.get('rows', []) if row.get('remaining') is not None]
        self.orbit.usage_fraction = min(row['remaining'] for row in valid) / 100 if valid else None
        self.orbit.usage_state = 'stale' if value.get('stale') and value.get('checked_at') else 'fresh' if valid and not value.get('stale') else 'unknown'
        if value.get('stale'):
            self.orbit.usage_badge = '?' if value.get('checked_at') else '—'
        elif valid:
            self.orbit.usage_badge = f"{min(row['remaining'] for row in valid):g}%"
        else:
            self.orbit.usage_badge = '—'
        self.orbit.setToolTip('Codex Orbit · 계정 한도 ' + self.orbit.usage_badge +
                             ' · ' + value.get('status', '미확인') + '\n클릭: 기간별 잔량과 변경 이력 · 드래그: 이동')
        self.orbit.update()

    def stop_monitor(self):
        if self.monitor:
            self.monitor.requestInterruption()
            if self.monitor.isRunning():
                # 실행 중인 감시기의 정리는 finished 신호에 맡기며 GUI에서 기다리지 않습니다.
                return False
            self.monitor = None
        return True

    def start_monitor(self):
        if self.closing:
            return False
        if self.monitor is not None and self.monitor.isRunning():
            self.monitor_enabled = True
            self.monitor_retry_timer.stop()
            if not self.monitor_restart_pending:
                self.monitor_restart_pending = True
                self.monitor.requestInterruption()
            self.orbit.healthy = False
            self.window.summary.setText('감시 재시작 대기 · 이전 작업자 종료 후 최종 설정으로 자동 시작합니다.')
            return False
        self.monitor_restart_pending = False
        self.monitor_retry_timer.stop()
        if not self.stop_monitor():
            self.orbit.healthy = False
            self.window.summary.setText('감시 지연 · 이전 작업자가 종료 중입니다. 종료 후 다시 시작하세요.')
            return False
        self.monitor_enabled = True
        self.orbit.healthy = False
        self.window.summary.setText('감시 준비 중 · 첫 진행 확인 대기')
        self.last_monitor_progress = time.monotonic()
        self.operation_log_error = operation_record(self.settings.directory, 'monitor-preparation', self.settings.values['sessions'])
        try:
            self.monitor = Monitor(self.settings.values['sessions'], self.settings.directory)
            self.monitor.event.connect(self.receive)
            self.monitor.status.connect(self.status)
            self.monitor.enriched.connect(self.refresh_history)
            self.monitor.finished.connect(self.check_monitor_health)
            history, problems = read_jsonl_tail(self.monitor.work / 'history.jsonl')
            self.window.history.clear()
            titles = title_catalog(Path(self.settings.values['sessions']).parent / 'session_index.jsonl', self.settings.directory / 'title-cache.json')
            for event in history:
                self.window.add_event(resolve_title(event, titles))
            if problems:
                self.window.diagnostics.setPlainText('\n'.join(problems))
            self.monitor.start()
        except Exception as error:
            self.monitor_enabled = False
            self.operation_log_error = operation_record(self.settings.directory, 'monitor-preparation-failed',
                                                        self.settings.values['sessions'], error) or self.operation_log_error
            raise
        self.monitor_health_timer.start()
        return True

    def check_monitor_health(self):
        if self.closing or not self.monitor_enabled or self.monitor is None:
            return
        if not self.monitor.isRunning():
            if self.monitor_restart_pending:
                self.monitor_restart_pending = False
                try:
                    self.start_monitor()
                except Exception as error:
                    self.window.summary.setText('감시 시작 실패 · 변경 기록의 진단을 확인하세요.')
                    self.window.diagnostics.setPlainText(str(error))
                return
            self.orbit.healthy = False
            self.window.summary.setText('감시 중단 · ' + ('자동 재시도 대기' if self.monitor_retries < 3 else '앱 다시 실행 필요'))
            if self.monitor_retries < 3 and not self.monitor_retry_timer.isActive():
                self.monitor_retry_timer.start(3000 * (self.monitor_retries + 1))
        elif time.monotonic() - self.last_monitor_progress > 20:
            self.orbit.healthy = False
            self.window.summary.setText('감시 지연 · 20초 이상 진행 확인 없음. 작업자는 실행 중이며 강제 재시작하지 않습니다.')
        self.orbit.update()

    def restart_dead_monitor(self):
        if self.closing or not self.monitor_enabled or self.monitor_retries >= 3:
            return
        if self.monitor is not None and self.monitor.isRunning():
            return
        self.monitor_retries += 1
        self.start_monitor()

    def receive(self, event):
        if self.closing:
            return
        self.window.add_event(event)
        self.orbit.unread = True
        if self.settings.values.get('popup', True):
            self.enqueue_notice(event)

    def update_notice_count(self):
        text = f'알림 표시 {len(self.notices)}건 · 새 변경은 즉시 표시'
        if self.notice_overflow:
            text += f' · 표시 상한으로 숨긴 {self.notice_overflow}건은 변경 이력에서 확인하세요.'
        self.window.notice_summary.setText(text)
        for notice in self.notices.values():
            notice.queue_hint.setText(text)
            notice.fit_content()
        self.layout_notices()

    def layout_notices(self, *_):
        if self.closing or not self.notices:
            return
        screen = QApplication.screenAt(self.orbit.pos()) or QApplication.primaryScreen()
        rect = screen.availableGeometry()
        cards = list(self.notices.values())
        for card in cards:
            card.fit_content(rect)
        total = sum(card.height() for card in cards) + 10 * (len(cards) - 1)
        top = max(rect.top(), min(self.orbit.y(), rect.bottom() + 1 - total))
        y = top
        # 모두 들어가지 않아도 새 카드를 기다리게 하지 않고 화면 안에서 어긋나게 겹칩니다.
        overlap = total > rect.height()
        for index, card in enumerate(cards):
            x = self.orbit.x() - card.width()
            if overlap:
                x += index * 18
                span = max(0, rect.height() - max(c.height() for c in cards))
                y = rect.top() + (span * index // max(1, len(cards) - 1))
            card.move(max(rect.left(), min(x, rect.right() + 1 - card.width())),
                      max(rect.top(), min(y, rect.bottom() + 1 - card.height())))
            card.raise_()
            if not overlap:
                y += card.height() + 10

    def enqueue_notice(self, event, replay=False):
        if self.closing:
            return
        notice = self.notices.get(event.get('id'))
        if notice is not None:
            if replay:
                notice.display(event, self.orbit, self.settings.values.get('notice_timeout_ms', 30000), replay=True)
            else:
                notice.update_event(event)
            self.update_notice_count()
            return
        if len(self.notices) >= self.max_visible_notices:
            oldest = next(iter(self.notices.values()))
            oldest.dismiss()
            self.notice_overflow += 1
        self.display_notice(event, replay=replay)
        self.update_notice_count()

    def display_notice(self, event, replay=False):
        self.notice = Notice(self.show)
        self.notices[event.get('id')] = self.notice
        self.notice.completed.connect(self.remove_notice)
        self.notice.display(event, self.orbit, self.settings.values.get('notice_timeout_ms', 30000), replay=replay)
        after = event.get('after') or {}
        value = {'event': 'display_requested', 'time': stamp(), 'id': event.get('id'),
                 'target': event.get('target'), 'model': after.get('model'), 'effort': after.get('effort'),
                 'source_time': event.get('source_time'), 'event_time': event.get('time'),
                 'queue_depth': 0, 'visible_count': len(self.notices),
                 'replay': replay, 'user_confirmed': False}
        try:
            append_log(self.settings.directory / 'notice-presentations.jsonl', value)
        except Exception as error:
            self.presentation_error = str(error)
            self.window.diagnostics.setPlainText(json.dumps({'state': '알림 표시 기록 실패', 'error': str(error)},
                                                            ensure_ascii=False, indent=2))

    def remove_notice(self, event_id):
        notice = self.notices.pop(event_id, None)
        if notice is not None:
            notice.deleteLater()
        self.update_notice_count()

    def replay_event(self, event_id):
        for index in range(self.window.history.count()):
            item = self.window.history.item(index)
            event = item.data(Qt.ItemDataRole.UserRole)
            if event_id in (event.get('id'), event.get('target')):
                self.window.history.setCurrentItem(item)
                self.enqueue_notice(event, replay=True)
                return True
        return False

    def refresh_history(self, events):
        if self.closing:
            return
        for event in events:
            self.window.update_event(event)
            notice = self.notices.get(event.get('id'))
            if notice is not None:
                notice.update_event(event)
        self.layout_notices()

    def status(self, value):
        if self.closing:
            return
        if self.monitor_restart_pending:
            return
        self.last_monitor_progress = time.monotonic()
        if self.presentation_error or self.operation_log_error:
            value = {**value, 'notice_presentation_error': self.presentation_error,
                     'operation_log_error': self.operation_log_error}
        self.orbit.healthy = value.get('state') == '감시 중'
        self.window.summary.setText('● ' + value.get('state', '') + '  ·  ' + kst_label(value.get('time')))
        self.window.diagnostics.setPlainText(json.dumps(value, ensure_ascii=False, indent=2))

    def show(self, event_id=None):
        if event_id:
            found = False
            for index in range(self.window.history.count()):
                item = self.window.history.item(index)
                if item.data(Qt.ItemDataRole.UserRole).get('id') == event_id:
                    self.window.history.setCurrentItem(item)
                    found = True
                    break
            if not found and event_id in self.notices:
                # 화면 이력 상한 밖으로 밀려나도 클릭한 원래 알림을 정확히 엽니다.
                self.window.add_event(self.notices[event_id].event)
        self.window.tabs.setCurrentIndex(0)
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        self.orbit.unread = False

    def request_quit(self):
        if self.quit_requested or self.cleaned:
            return
        self.quit_requested = True
        self.closing = True
        self.monitor_restart_pending = False
        self.monitor_enabled = False
        self.monitor_health_timer.stop()
        self.monitor_retry_timer.stop()
        self.usage.close()
        for notice in list(self.notices.values()):
            notice.dismiss()
        self.orbit.healthy = False
        self.window.summary.setText('종료 중 · 감시 작업자의 안전한 종료를 기다리고 있습니다.')
        if self.monitor is not None and self.monitor.isRunning():
            self.monitor.finished.connect(self.finish_quit)
            self.monitor.requestInterruption()
            # 신호 연결 직전에 종료된 경우도 대기 상태로 남지 않도록 다시 확인합니다.
            if self.monitor.isRunning():
                return
        self.finish_quit()

    def finish_quit(self):
        if not self.quit_requested or (self.monitor is not None and self.monitor.isRunning()):
            return
        self.quit_ready = True
        self.close()
        QApplication.instance().quit()

    def close(self):
        if self.cleaned:
            return
        self.cleaned = True
        self.closing = True
        self.monitor_restart_pending = False
        self.monitor_enabled = False
        self.monitor_health_timer.stop()
        self.monitor_retry_timer.stop()
        self.usage.close()
        self.stop_monitor()
        for notice in list(self.notices.values()):
            notice.close()
        self.notices.clear()
        self.orbit.close()
        self.window.close()
        QApplication.instance().removeEventFilter(self.quit_guard)
        self.quit_guard.deleteLater()


def main():
    parser = argparse.ArgumentParser(description='Codex Orbit · 로컬 모델 변경 투명 궤도')
    parser.add_argument('--data-dir', type=Path, default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit')
    parser.add_argument('--sessions', type=Path)
    parser.add_argument('--smoke-test', action='store_true')
    parser.add_argument('--usage-smoke-test', action='store_true', help='실제 계정 잔량과 표시를 조회한 뒤 종료')
    parser.add_argument('--smoke-report', type=Path)
    parser.add_argument('--show-details', action='store_true')
    parser.add_argument('--show-event', help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시')
    args = parser.parse_args()
    args.data_dir = args.data_dir.absolute()
    app = QApplication(sys.argv[:1])
    app.setApplicationName('Codex Orbit')
    apply_theme()
    app.setWindowIcon(QIcon(str(asset('Orbit.ico'))))
    app.setQuitOnLastWindowClosed(False)
    font_id = QFontDatabase.addApplicationFont(str(asset('NanumGothic-Bold.ttf')))
    families = QFontDatabase.applicationFontFamilies(font_id)
    font = QFont(families[0] if families else 'NanumGothic', 10, QFont.Weight.Bold)
    # Windows ClearType의 유채색 서브픽셀 테두리가 무채색 UI에 섞이지 않게 합니다.
    font.setStyleStrategy(font.styleStrategy() | QFont.StyleStrategy.NoSubpixelAntialias)
    app.setFont(font)
    effective_sessions = args.sessions or (Path(os.environ.get('CODEX_HOME') or (Path.home() / '.codex')) / 'sessions')
    stage = 'settings-load'
    log_error = operation_record(args.data_dir, stage, effective_sessions)
    try:
        settings = Settings(args.data_dir)
        if args.sessions:
            settings.values['sessions'] = str(args.sessions.absolute())
        effective_sessions = settings.values['sessions']
        stage = 'lock-acquire'
        log_error = operation_record(args.data_dir, stage, effective_sessions) or log_error
        lock = QLockFile(str(args.data_dir / 'app.lock'))
        if not lock.tryLock(100):
            raise RuntimeError('같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.')
        if not (args.smoke_test or args.usage_smoke_test):
            # 필수 캐시 오류를 UI 구성보다 먼저 알리고 준비 중 변경은 start_monitor에서 다시 검사합니다.
            stage = 'monitor-preflight'
            log_error = operation_record(args.data_dir, stage, effective_sessions, lock_acquired=True) or log_error
            title_catalog(Path(effective_sessions).parent / 'session_index.jsonl', args.data_dir / 'title-cache.json')
        stage = 'visual-assets-preflight'
        log_error = operation_record(args.data_dir, stage, effective_sessions, lock_acquired=True) or log_error
        get_atom_frames()
        stage = 'controller-prepare'
        log_error = operation_record(args.data_dir, stage, effective_sessions, lock_acquired=True) or log_error
        controller = Controller(settings, start_worker=not (args.smoke_test or args.usage_smoke_test))
    except Exception as error:
        log_error = operation_record(args.data_dir, stage + '-failed', effective_sessions, error) or log_error
        message = str(error) + ('\n시작 운영 기록 실패: ' + log_error if log_error else '')
        if args.smoke_report:
            args.smoke_report.write_text(json.dumps({'ok': False, 'error': str(error), 'operation_log_error': log_error}, ensure_ascii=False), encoding='utf-8')
        else:
            QMessageBox.critical(None, 'Codex Orbit 시작 실패', message)
        return 1
    controller.operation_log_error = operation_record(args.data_dir, 'controller-ready', effective_sessions) or log_error or controller.operation_log_error
    app.aboutToQuit.connect(controller.close)
    if args.show_details:
        controller.show()
    if args.usage_smoke_test and not args.smoke_test:
        controller.show()
        usage_finished = False
        def finish_usage(value=None, timed_out=False):
            nonlocal usage_finished
            if usage_finished:
                return
            value = value or controller.usage.snapshot
            ok = not value.get('stale', True) and value.get('checked_at') is not None
            if not ok and not timed_out:
                return
            usage_finished = True
            report = {**value, 'ok': ok, 'frozen': bool(getattr(sys, 'frozen', False)),
                      'widget_badge': controller.orbit.usage_badge,
                      'display_text': controller.window.usage_values.text(),
                      'display_status': controller.window.usage_status.text(),
                      'time': stamp()}
            if args.smoke_report:
                controller.orbit.grab().save(str(args.smoke_report.with_suffix('.orbit.png')))
                controller.window.grab().save(str(args.smoke_report.with_suffix('.details.png')))
                args.smoke_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
            app.exit(0 if ok else 1)
        controller.usage.changed.connect(lambda value: QTimer.singleShot(100, lambda: finish_usage(value)))
        QTimer.singleShot(18000, lambda: finish_usage(timed_out=True))
        controller.usage.start()
    if args.show_event and not controller.replay_event(args.show_event):
        controller.window.summary.setText('지정한 이력을 찾지 못했습니다. 감시가 기록을 읽은 뒤 이력에서 확인하세요.')
    if args.smoke_test:
        first = controller.orbit.grab().toImage()
        if args.smoke_report:
            first.save(str(args.smoke_report.with_suffix('.frame1.png')))
        def finish():
            second = controller.orbit.grab().toImage()
            if args.smoke_report:
                second.save(str(args.smoke_report.with_suffix('.frame2.png')))
            report = {'ok': bool(first != second and first.pixelColor(0, 0).alpha() == 0 and families),
                      'frame_changed': first != second, 'corner_alpha': first.pixelColor(0, 0).alpha(),
                      'translucent': controller.orbit.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground),
                      'always_on_top': bool(controller.orbit.windowFlags() & Qt.WindowType.WindowStaysOnTopHint),
                      'font_families': families, 'time': stamp(), 'frozen': bool(getattr(sys, 'frozen', False))}
            if args.smoke_report:
                args.smoke_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
            if sys.stdout:
                print(json.dumps(report, ensure_ascii=False))
            app.exit(0 if report['ok'] else 1)
        QTimer.singleShot(850, finish)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
