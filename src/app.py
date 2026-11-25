"""Codex Orbit: 독립 회전 위젯과 로컬 변경 기록·사용 한도."""
import argparse
import hashlib
import math
import json
import os
from pathlib import Path
import sys
import time
import threading
from datetime import datetime, timezone, timedelta
import re
from collections import deque
from shiboken6 import isValid

from i18n import translate as t, get_language, set_language, remember_translations, retranslate_widgets
from notice_format import (friendly_effort, previous_field, short_reason, public_text,
                           public_reason_original, notice_model_label, notice_previous_model,
                           notice_reason, notice_reason_original, notice_reason_caption)
from PySide6.QtCore import QEvent, QObject, QLockFile, Qt, QSize, QThread, QTimer, Signal, Slot, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QPainter, QPixmap, QColor, QImage, QPen, QPainterPath
from PySide6.QtWidgets import (QApplication, QDialog,
                             QFrame, QGridLayout, QHBoxLayout, QLabel, QComboBox,
                             QListWidget, QListWidgetItem, QMenu, QMessageBox,
                             QPlainTextEdit, QPushButton, QSplitter, QTabWidget,
                             QProgressBar, QScrollArea, QSizePolicy, QSlider, QLayout, QVBoxLayout, QWidget, QLineEdit)

from core import clamp_position, read_jsonl_tail, read_text_strict, title_catalog, resolve_title
from notifier import Watcher, append_log, atomic_json, stamp, POLL_INTERVAL_SECONDS, MAX_PENDING
from usage import UsageClient, reset_label
from weather import WeatherClient, CitySearchClient, PlaceSearchClient, normalize_city
from holiday_calendar import available_countries, find_countries, country_status, normalize_country
from visuals import draw_orbit, draw_desktop_orbit, desktop_widget_layout, status_label, usage_bar
from atom_frames import get_atom_frames
from calendar_art import design_for_date, current_date
from brand import brand_image, AnimatedBrand, brand_clock, symbol_icon, with_symbol, validate_symbols
from theme import apply_theme, set_ui_style, themed_stylesheet
from ui_layout import OrbitComboBox as QComboBox
from typography import app_font
from elements import daily_element
from usage_widgets import CalendarHero


EMPTY_HISTORY_GUIDANCE = '변경을 감지하면 이곳에서 전후 값과 공개 이유를 확인할 수 있습니다.\n첫 실행은 과거 기록을 기준선으로 읽으며 과거 알림을 만들지 않습니다.'


def validated_motion_speed(value):
    """설정과 UI의 속도는 유한한 실제 숫자 범위로 제한합니다."""
    if type(value) not in (int, float) or not .25 <= value <= 3.0 or not math.isfinite(value):
        raise ValueError(t('회전 속도는 0.25~3배의 유한한 숫자여야 합니다.'))
    return float(value)


def _application_gui_root():
    """Python 순환 수집과 무관하게 살아 있는 GUI 소유자를 앱에 보관합니다."""
    application = QApplication.instance()
    if application is None or QThread.currentThread() != application.thread():
        raise RuntimeError('GUI 소유자는 QApplication의 메인 스레드에서 생성해야 합니다.')
    root = getattr(application, '_codex_orbit_gui_root', None)
    if root is None or not isValid(root):
        root = QWidget()
        root.setObjectName('codexOrbitGuiRoot')
        application._codex_orbit_gui_root = root
    return root


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
        return t('모델·추론 확인 불가')
    return str(value.get('model') or t('확인 불가')) + " / " + str(value.get('effort') or t('확인 불가'))


def model_card_label(value):
    if value is None:
        return t('모델·추론 확인 불가')
    return str(value.get('model') or t('확인 불가')) + " · " + t('추론') + " " + (friendly_effort(value['effort']) if value.get('effort') else t('확인 불가'))


def friendly_model(value):
    return {'gpt-6.1-sol': 'Sol', 'gpt-6-sol': 'Sol', 'gpt-6-astra': 'Astra',
            'gpt-6-luna': 'Luna'}.get(value, str(value or t('확인 불가')))














ROLE_LABELS = {'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',
               'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}


def kst_label(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            return str(value) + t(' (시간대 미기록)')
        return parsed.astimezone(timezone(timedelta(hours=9))).strftime('%Y.%m.%d %H:%M:%S KST')
    except ValueError:
        return str(value or t('확인 불가'))




def event_kind(event):
    if event.get('kind') == 'activity':
        return {'assigned':t('새 작업 배정'), 'resumed':t('작업 재개')}.get(event.get('activity_type'), t('작업 활동 관측'))
    if event.get('kind') == 'settings':
        if event.get('before') is None:
            return t('자식 작업자 첫 선택 설정 관측') if event.get('parent') else t('채팅 선택 설정 첫 관측')
        return configuration_change_label(event) + ' · ' + t('선택 설정')
    if event.get('assignment_type') == 'replacement':
        return t('새 작업자 배정 · 이전 작업자 교체')
    if event.get('before') is None:
        return t('자식 작업자 첫 관측') if event.get('parent') else t('첫 관측')
    return configuration_change_label(event)


def configuration_change_label(event):
    before, after = event.get('before'), event.get('after')
    if before is None or after is None:
        return t('설정 관측 · 현재 값 확인 불가')
    model_changed = before.get('model') != after.get('model')
    effort_changed = before.get('effort') != after.get('effort')
    if model_changed and effort_changed:
        return t('모델 · 추론 강도 변경')
    if model_changed:
        return t('모델 변경')
    return t('추론 강도 변경') if effort_changed else t('설정 유지')




def task_explanation(event, limit=360):
    fallback = '공개된 작업 설명이 기록되지 않았습니다.'
    if event.get('task_summary'):
        return public_text(event['task_summary'], fallback, limit)
    if event.get('reason'):
        return public_text(short_reason(event, limit), fallback, limit)
    return t(fallback)


def selection_explanation(event):
    """공개된 작업 목적을 모델 선택 이유로 바꾸어 말하지 않습니다."""
    text = public_text(event.get('reason'), '', 1200)
    match = re.search(r'(?:모델(?:·추론 강도)? 선택 이유|선택 이유)\s*[:：]\s*([^\n]+)', text)
    return (t('선택 이유: ')+match.group(1).strip()) if match else t('모델·추론 강도 선택 이유는 공개되지 않았습니다.')


def event_accent(event):
    if event.get('kind') == 'activity':
        return '#11764f' if event.get('activity_type') == 'assigned' else '#915024'
    before, after = event.get('before') or {}, event.get('after') or {}
    if event.get('before') is None:
        return '#496578'
    if before.get('model') != after.get('model'):
        return '#70499d'
    return '#1a6b83' if before.get('effort') != after.get('effort') else '#496578'


def activity_message(event):
    if event.get('kind') != 'activity':
        return ''
    role = t(ROLE_LABELS.get(event.get('role'), '담당'))
    return (t('기존 {role} 작업자에게 다시 맡겼어요.', role=role) if event.get('activity_type') == 'resumed'
            else t('{role} 작업자에게 새 작업을 맡겼어요.', role=role))


def history_label(event):
    from orbit_features import clean_chat_title
    title = clean_chat_title(str(event.get('chat_name') or t('채팅 제목 확인 불가')))
    if event.get('kind') == 'activity':
        return title+'\n'+event_kind(event)+'\n'+task_explanation(event, 70)
    return title+'\n'+model_label(event.get('after'))


def event_icon(event):
    image = QImage(16,16,QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(event_accent(event)))
    painter.drawEllipse(3,3,10,10)
    painter.end()
    return QIcon(QPixmap.fromImage(image))




def event_description(event):
    return '\n'.join([
        t('채팅') + ': ' + str(event.get('chat_name') or event.get('target', t('확인 불가'))),
        t('채팅 ID') + ': ' + str(event.get('parent') or event.get('target') or t('확인 불가')),
        t('작업자 ID') + ': ' + str(event.get('target') if event.get('parent') else t('해당 없음')),
        t('구분') + ': ' + (t('자식 작업') if event.get('parent') else t('main 또는 부모 정보 미기록')),
        t('역할') + ': ' + str(event.get('role', t('확인 불가'))),
        t('작업 이름') + ': ' + str(event.get('task_name') or t('기록 없음')),
        t('부모 ID') + ': ' + str(event.get('parent') or t('기록 없음')),
        t('작업 경로') + ': ' + str(event.get('agent_path') or t('기록 없음')),
        t('제목 출처') + ': ' + str(event.get('title_source') or t('확인 불가')),
        t('제목 확인 시각') + ': ' + kst_label(event.get('title_checked_at')),
        t('호출 ID') + ': ' + str(event.get('call_id') or t('기록 없음')),
        t('활동 종류') + ': ' + str(event.get('activity_type') or t('해당 없음')),
        t('맡긴 일') + ': ' + task_explanation(event, 2000),
        t('작업 설명 출처') + ': ' + str(event.get('task_source') or t('기록 없음')),
        t('활동 근거') + ': ' + str(event.get('assignment_evidence') or t('해당 없음')),
        t('요청 설정') + ': ' + str(event.get('requested') or t('기록 없음')),
        t('이유 호출 ID') + ': ' + str(event.get('reason_call_id') or t('기록 없음')),
        t('변경 전') + ': ' + (t('이전 기록 없음') if event.get('before') is None else model_label(event['before'])),
        t('변경 후') + ': ' + model_label(event.get('after')),
        t('감지 시각') + ': ' + kst_label(event.get('time')),
        t('원본 기록 시각') + ': ' + kst_label(event.get('source_time')),
        t('기록 종류') + ': ' + str(event.get('kind', t('확인 불가'))),
        '', t('공개 이유 원문'), public_reason_original(event),
        '', t('모델·추론 강도 선택 이유'), selection_explanation(event),
        '', t('근거 수준'), str(event.get('evidence') or t('확인 불가')),
        '', t('선택 설정 관측 근거'), str(event.get('configuration_evidence') or t('해당 없음')),
        '', t('표시 기록'), str(event.get('delivery') or t('앱 표시 요청; 사용자 수신 미확인')),
        '', t('로컬 기록과 공개 이유의 연결 근거입니다. 서버 모델 신원이나 비공개 추론을 증명하지 않습니다.')
    ])


def weather_number_text(value):
    """표시만 소수 둘째 자리 아래를 버리고 저장된 관측값은 바꾸지 않습니다."""
    from decimal import Decimal, ROUND_DOWN, localcontext
    if type(value) not in (int, float) or not math.isfinite(value):
        return '—'
    with localcontext() as context:
        context.prec = 330
        text = format(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_DOWN), 'f')
    return text.rstrip('0').rstrip('.') if '.' in text else text


def percentage_text(value):
    from percentage_display import percentage_text as display
    return display(value)


def percentage_tooltip(value):
    from percentage_display import percentage_tooltip as display
    return display(value)


def remaining_text(value):
    return t('{percent} 남음',percent=percentage_text(value)) if value is not None else t('잔량 미확인')


def weather_widget_text(value):
    """기온과 부가정보를 분리하고 일출·일몰은 제공된 지역 시간대로만 표시합니다."""
    temperature = value.get('temperature')
    code = value.get('weather_code')
    if code is None:
        description = t('날씨 미확인')
    else:
        from weather import weather_description
        description = weather_description(code, get_language())
    primary = (weather_number_text(temperature)+'℃' if type(temperature) in (int,float) and math.isfinite(temperature) else t('기온 미확인')) + ' · ' + description
    stale = bool(value.get('stale')) and temperature is not None
    if stale:primary = t('이전 정보: ') + primary
    humidity = value.get('humidity')
    humidity_text = percentage_text(humidity)
    offset = value.get('utc_offset_seconds')
    from weather import weather_sun_time
    def local_time(key):return weather_sun_time(value.get(key), offset)
    rain = value.get('precipitation')
    interval = value.get('precipitation_interval_seconds')
    valid_rain = (type(rain) in (int, float) and math.isfinite(rain) and rain >= 0
                  and type(interval) is int and interval > 0)
    rain_text = weather_number_text(rain)+' mm' if valid_rain else '—'
    interval_text = (t('직전 {minutes:g}분').format(minutes=interval // 60) if interval % 60 == 0
                     else t('직전 {seconds}초').format(seconds=interval)) if valid_rain else ''
    rain_label = t('이전 강수 ') if stale else t('강수 ')
    extras = ((t('이전 습도 ') if stale else t('습도 '))+humidity_text+' · '+rain_label+rain_text+
              (' ('+interval_text+')' if interval_text else ''),
              t('일출 ')+local_time('sunrise')+' · '+t('일몰 ')+local_time('sunset'))
    return primary, extras


def regional_calendar_date():
    """제목과 그림에 같은 공통 지역 날짜를 사용합니다."""
    from calendar_motion import get_calendar_date
    return get_calendar_date()


def validated_theme_country(value):
    """검색 목록에 실제로 존재하는 국가·지역 코드만 사용합니다."""
    code = normalize_country(value)
    if not any(row['code'] == code for row in available_countries()):
        raise ValueError(t('국가 목록에서 선택해 주세요.'))
    return code


class Settings:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / 'settings.json'
        home = Path(os.environ.get('CODEX_HOME') or (Path.home() / '.codex'))
        self.values = {'sessions': str(home / 'sessions'), 'theme': '자동', 'popup': True, 'notice_timeout_ms': 30000, 'language': 'ko', 'motion_speed': 1.0, 'weather_location': None, 'theme_country_mode': 'auto', 'theme_country': 'KR'}
        if self.path.exists():
            value = json.loads(read_text_strict(self.path))
            if not isinstance(value, dict):
                raise ValueError('앱 설정은 JSON 객체여야 합니다.')
            self.values.update(value)
        if self.values.get('language') not in ('ko', 'en'):
            self.values['language'] = 'ko'
        try:
            self.values['motion_speed'] = validated_motion_speed(self.values['motion_speed'])
        except ValueError:
            self.values['motion_speed'] = 1.0

    def save(self):
        atomic_json(self.path, self.values)


class NoticeDelivery:
    """Qt 예약 호출을 포함한 미처리 전달 수를 스레드 사이에서 제한합니다."""
    def __init__(self):
        self.lock = threading.Lock()
        self.tickets = set()
        self.closed = False

    def acquire(self):
        with self.lock:
            if self.closed or len(self.tickets) >= MAX_PENDING:
                raise RuntimeError('알림 전달 대기 한도 또는 종료 상태: 다음 감시 주기에 재시도합니다.')
            ticket = NoticeTicket(self)
            self.tickets.add(ticket)
            return ticket

    def available(self):
        with self.lock:
            return MAX_PENDING - len(self.tickets)

    def close(self):
        with self.lock:
            self.closed = True
            self.tickets.clear()


class NoticeTicket:
    """중복 반환과 종료 뒤 도착한 신호도 같은 한도를 다시 늘리지 않습니다."""
    def __init__(self, gate):
        self.gate = gate

    def release(self):
        with self.gate.lock:
            self.gate.tickets.discard(self)


class Monitor(QThread):
    event = Signal((dict,), (object, dict))
    status = Signal(dict)
    enriched = Signal(list)
    lifecycle_event = Signal(dict)

    def __init__(self, sessions, directory):
        super().__init__()
        self.sessions = Path(sessions)
        key = hashlib.sha256(str(self.sessions.absolute()).encode('utf-8')).hexdigest()[:16]
        self.work = Path(directory) / 'watches' / key
        self.directory = Path(directory)
        self.cache_path = Path(directory) / 'title-cache.json'
        self.titles = {}
        self.recent_errors = deque(maxlen=5)
        self.delivery_gate = None

    def send(self, event):
        value = resolve_title(event, self.titles)
        value['delivery'] = '앱 표시 요청; 사용자 수신 미확인'
        if self.delivery_gate is None:
            self.event.emit(value)
        else:
            ticket = self.delivery_gate.acquire()
            try:
                self.event[object, dict].emit(ticket, value)
            except Exception:
                ticket.release()
                raise
        return value['delivery']

    def run(self):
        watcher = None
        try:
            watcher = Watcher(self.sessions, self.work, self.send)
            last_enriched = None
            while not self.isInterruptionRequested():
                try:
                    watcher.diagnostic_failures.clear()
                    if not self.sessions.is_dir():
                        raise FileNotFoundError('세션 폴더가 없거나 접근할 수 없습니다: ' + str(self.sessions))
                    self.titles = title_catalog(self.sessions.parent / 'session_index.jsonl', self.cache_path)
                    watcher.poll()
                    for lifecycle in watcher.drain_lifecycle():
                        self.lifecycle_event.emit(resolve_title(lifecycle, self.titles))
                    history, _ = read_jsonl_tail(self.work / 'history.jsonl')
                    values = []
                    for event in history:
                        if event.get('reason') == '확인 불가':
                            watcher.lookup_parent_reason(event)
                        values.append(resolve_title(watcher.enrich_event(event), self.titles))
                    # 감지·오류·상태 주기는 유지하고 같은 이력의 GUI 예약 호출만 반복하지 않습니다.
                    if values != last_enriched:
                        self.enriched.emit(values)
                        last_enriched = values
                    atomic_json(watcher.state_path, watcher.state)
                    diagnostics, problems = read_jsonl_tail(self.work / 'diagnostics.jsonl', max_records=5)
                    remaining = sum(max(0, info.get('baseline_end', 0) - info['offset'])
                                    for info in watcher.state['files'].values())
                    remaining += max(0, watcher.state.get('activity_replay_remaining_bytes', 0))
                    status = {'time': stamp(), 'state': '기준선 준비 중' if remaining else '감시 중', 'sessions': str(self.sessions),
                              'files': len(watcher.state['files']), 'pending': len(watcher.state['pending']),
                              'chats': len(watcher.state['models']),
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
    def showEvent(self, event):
        super().showEvent(event)
        from calendar_motion import set_calendar_motion_visible
        set_calendar_motion_visible(self, True)
        self._request_motion_size()
        if hasattr(self,'timer'):self.timer.start()

    def hideEvent(self, event):
        from calendar_motion import set_calendar_motion_visible
        set_calendar_motion_visible(self, False)
        if hasattr(self,'timer'):self.timer.stop()
        super().hideEvent(event)

    def closeEvent(self, event):
        from calendar_motion import set_calendar_motion_visible
        set_calendar_motion_visible(self, False)
        if hasattr(self,'timer'):self.timer.stop()
        super().closeEvent(event)

    def __init__(self, settings, details, quit_app, parent=None):
        super().__init__(parent if parent is not None else _application_gui_root(),
                         Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle('Codex Orbit')
        self.setMinimumSize(180, 250)
        self.settings, self.details = settings, details
        self.theme_country = validated_theme_country(settings.values.get('theme_country', 'KR'))
        self.city_ref = None
        self.language_changed = lambda language: None
        self.motion_speed_changed = lambda value: None
        size = settings.values.get('size', [220, 432])
        if not isinstance(size, (list, tuple)) or len(size) != 2 or any(type(v) is not int for v in size):
            size = [220, 432]
        self.resize(max(180, min(size[0], 4096)), max(250, min(size[1], 4096)))
        self.quit_app = quit_app
        self.origin_time = brand_clock().origin
        self.render_time = None
        self.healthy = False
        self.unread = False
        self.usage_badge = '—'
        self.usage_fraction = None
        self.usage_state = 'unknown'
        self.weather_text = t('기온 미확인')
        self.weather_extras = ()
        self.location_text = t('위치 정보 없음')
        self.weather_tooltip = ''
        self.usage_tooltip = ''
        self.press_global = None
        self.dragged = False
        self.resize_edges = (False, False)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setMouseTracking(True)
        self.setToolTip(t('Codex Orbit · 클릭: 상세 · 드래그: 이동 · 오른쪽/아래 가장자리: 크기 조절 · 우클릭: 기록/종료'))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_static_clock)
        self.timer.start(1000)
        self.restore_position()
        for screen in QApplication.screens():
            screen.availableGeometryChanged.connect(self.restore_position)
        QApplication.instance().screenRemoved.connect(self.restore_position)

    def restore_position(self, *_):
        screens = [screen.availableGeometry() for screen in QApplication.screens()]
        value = self.settings.values.get('position', [900000, 900000])
        if not isinstance(value, (list, tuple)) or len(value) != 2 or any(type(v) is not int for v in value):
            value = [900000, 900000]
        if not screens:
            self.move(24, 24)
            return
        screen = next((r for r in screens if r.contains(value[0], value[1])), None)
        if screen is None:
            screen = screens[0]
            value = [screen.left() + 24, screen.top() + 24]
        self.resize(min(self.width(), max(self.minimumWidth(), screen.width())),
                    min(self.height(), max(self.minimumHeight(), screen.height())))
        x = max(screen.left(), min(value[0], screen.right() + 1 - self.width()))
        y = max(screen.top(), min(value[1], screen.bottom() + 1 - self.height()))
        self.move(x, y)

    def clock_text(self):
        from calendar_motion import get_calendar_utc_offset
        offset=get_calendar_utc_offset()
        return datetime.now(timezone(timedelta(seconds=9*3600 if offset is None else offset))).strftime('%H:%M:%S')

    def _refresh_static_clock(self):
        from calendar_motion import calendar_motion_status
        status=calendar_motion_status()
        self.update()  # 모션이 정지되어도 시각·기온·잔량 표시는 갱신합니다.

    @Slot()
    def calendar_frame_ready(self):
        if self.isVisible():self.update()

    def _request_motion_size(self):
        if not hasattr(self,'timer') or not self.isVisible():return
        from calendar_motion import set_calendar_motion_size
        design=design_for_date(regional_calendar_date(),country=self.theme_country,city_ref=self.city_ref)
        layout=desktop_widget_layout(self.width(),self.height(),t(design.title),True,True,text_scale=self.settings.values.get('text_scale',100)/100,weather_extras=self.weather_extras,clock_text=self.clock_text(),weather_text=self.weather_text,fraction=self.usage_fraction,state=self.usage_state,calendar_date=design.date.strftime('%Y/%m/%d'))
        if self.weather_extras and self.minimumHeight()!=layout['minimum_height']:
            self.setMinimumHeight(layout['minimum_height'])
        size=max(32,min(2160,round(layout['art'].width()*self.devicePixelRatioF())))
        set_calendar_motion_size(self,size)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self._request_motion_size()

    def refresh_tooltip(self):
        self.setToolTip(self.usage_tooltip + '\n' + self.weather_tooltip +
                        t('\n감시 상태: ') + status_label(self.healthy, self.unread))
        if hasattr(self, 'health37'):
            self.setToolTip(self.toolTip() + '\n' + self.health37['label'])

    def paintEvent(self, _):
        self.refresh_tooltip()
        elapsed = self.render_time if self.render_time is not None else time.monotonic() - self.origin_time
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            from calendar_motion import get_calendar_frame,record_calendar_presentation
            design = design_for_date(regional_calendar_date(),country=self.theme_country,city_ref=self.city_ref)
            if hasattr(self,'experience') and self.settings.values.get('scene_mode','calendar')=='observatory':
                from dataclasses import replace
                model=self.experience.scene.get('model')
                name={'gpt-6.1-sol':'Sol','gpt-6-sol':'Sol','gpt-6-astra':'Astra','gpt-6.1-terra':'Terra','gpt-6-luna':'Luna'}.get(model,t('모델 확인 불가'))
                design=replace(design,title=name,accent='#77c9aa')
            source=get_calendar_frame(elapsed)
            from visuals import DesktopOverlayCache
            if not hasattr(self, '_desktop_overlay_cache'):
                self._desktop_overlay_cache = DesktopOverlayCache()
            draw_desktop_orbit(painter, self.width(), self.height(), source, design,
                               self.usage_fraction, self.usage_state, self.clock_text(), self.weather_text, self.location_text,
                               cache=self._desktop_overlay_cache,text_scale=self.settings.values.get('text_scale',100)/100,weather_extras=self.weather_extras)
            record_calendar_presentation(self,source)
            health = getattr(self, 'health37', None)
            if health:
                painter.save()
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor({'ok': '#32b781', 'error': '#e26868', 'delayed': '#d7a34b',
                                        'waiting': '#7699b8', 'off': '#7c8790'}.get(health['kind'], '#7c8790')))
                painter.drawEllipse(8, 8, 9, 9)
                painter.restore()
            from theme import colors
            painter.setPen(QColor(colors()['muted']))
            painter.drawLine(self.width()-4, self.height()//2-12, self.width()-4, self.height()//2+12)
            painter.drawLine(self.width()//2-12, self.height()-4, self.width()//2+12, self.height()-4)
            for offset in (5, 9, 13):
                painter.drawLine(self.width()-offset, self.height()-3, self.width()-3, self.height()-offset)
        finally:
            # 그리기 구간을 벗어나기 전에 모의 호출이 보관한 참조도 비활성화합니다.
            painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_global = event.globalPosition().toPoint()
            self.press_position = self.pos()
            self.press_size = self.size()
            point = event.position()
            self.resize_edges = (point.x() >= self.width()-14, point.y() >= self.height()-14)
            self.dragged = False
            self.setCursor(Qt.CursorShape.SizeFDiagCursor if all(self.resize_edges) else
                           Qt.CursorShape.SizeHorCursor if self.resize_edges[0] else
                           Qt.CursorShape.SizeVerCursor if self.resize_edges[1] else Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self.press_global is None:
            point = event.position()
            if hasattr(self,'experience'):
                self.experience.pointer=[point.x()/max(1,self.width())*2-1,point.y()/max(1,self.height())*2-1]
                self.experience.feed_scene()
            right = point.x() >= self.width()-14
            bottom = point.y() >= self.height()-14
            self.setCursor(Qt.CursorShape.SizeFDiagCursor if right and bottom else
                           Qt.CursorShape.SizeHorCursor if right else
                           Qt.CursorShape.SizeVerCursor if bottom else Qt.CursorShape.OpenHandCursor)
        if self.press_global is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.press_global
            if delta.manhattanLength() > QApplication.startDragDistance():
                self.dragged = True
            if self.dragged:
                if any(self.resize_edges):
                    screen = QApplication.screenAt(self.pos()) or QApplication.primaryScreen()
                    rect = screen.availableGeometry() if screen else None
                    width = self.press_size.width() + (delta.x() if self.resize_edges[0] else 0)
                    height = self.press_size.height() + (delta.y() if self.resize_edges[1] else 0)
                    if rect:
                        width = min(width, rect.right()+1-self.x())
                        height = min(height, rect.bottom()+1-self.y())
                    self.resize(max(self.minimumWidth(), width), max(self.minimumHeight(), height))
                else:
                    self.move(self.press_position + delta)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.press_global is not None:
            self.press_global = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            if self.dragged:
                self.settings.values['position'] = [self.x(), self.y()]
                if any(self.resize_edges):
                    self.settings.values['size'] = [self.width(), self.height()]
                self.restore_position()
                self.settings.values['position'] = [self.x(), self.y()]
                try:
                    self.settings.save()
                except Exception as error:
                    QMessageBox.warning(self, '위젯 설정 저장 실패', str(error))
            elif not any(self.resize_edges):
                self.unread = False
                if hasattr(self,'experience') and self.settings.values.get('scene_mode','calendar')=='observatory':
                    layout=desktop_widget_layout(self.width(),self.height(),'',True,True,text_scale=self.settings.values.get('text_scale',100)/100,weather_extras=self.weather_extras,clock_text=self.clock_text(),weather_text=self.weather_text,fraction=self.usage_fraction,state=self.usage_state)
                    art=layout['art'];point=event.position()
                    self.experience.hit((point.x()-art.x())/max(1,art.width()),(point.y()-art.y())/max(1,art.height()))
                else:self.details()
            self.resize_edges = (False, False)

    def enterEvent(self, event):
        if hasattr(self,'experience'):self.experience.expand()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if hasattr(self,'experience'):QTimer.singleShot(900, self._dock_if_outside)
        super().leaveEvent(event)

    def _dock_if_outside(self):
        if not self.underMouse() and hasattr(self,'experience'):self.experience.dock()

    def contextMenuEvent(self, event):
        menu = self.create_menu()
        menu.exec(event.globalPos())

    def create_menu(self):
        menu = QMenu(self)
        menu.addAction(t('상세 이력 열기'), self.details)
        languages = menu.addMenu(t('언어'))
        for language, label in (('ko', '한국어'), ('en', 'English')):
            action = languages.addAction(label)
            action.setCheckable(True)
            action.setChecked(get_language() == language)
            action.triggered.connect(lambda checked=False, value=language: self.language_changed(value))
        speeds = menu.addMenu(t('회전 속도'))
        speeds.setObjectName('motionSpeedMenu')
        for value in (.25, .5, 1.0, 1.5, 2.0, 3.0):
            action = speeds.addAction(t('{speed:g}배', speed=value))
            action.setData(value)
            action.setCheckable(True)
            action.setChecked(self.settings.values['motion_speed'] == value)
            action.triggered.connect(lambda checked=False, speed=value: self.motion_speed_changed(speed))
        menu.addSeparator()
        if hasattr(self,'experience'):
            menu.addMenu(self.experience.menu)
        menu.addAction(t('종료'), self.quit_app)
        return menu


def notice_plain(value):
    """알림 장식 문자만 그림으로 분리하며 저장 원문은 그대로 둡니다."""
    return re.sub(r'[\U0001f000-\U0001faff\u2600-\u27ff\ufe0f\u200d]', '', str(value)).strip()


def notice_symbol(kind, size=20):
    """글꼴 설치 여부와 관계없이 동일하게 보이는 고해상도 알림 아이콘입니다."""
    image=QPixmap(size*3,size*3);image.fill(Qt.GlobalColor.transparent)
    painter=QPainter(image);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(size*3/24,size*3/24)
    color=QColor({'sol':'#d6a73e','astra':'#a18be5','terra':'#57b8af','luna':'#90a9d7'}.get(kind,'#759e91'))
    painter.setPen(QPen(color,1.9,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin))
    if kind.startswith('effort:'):
        count={'none':0,'minimal':1,'low':2,'medium':3,'high':4,'xhigh':5,'ultra':6}.get(kind[7:],-1)
        for i in range(6):
            painter.setPen(Qt.PenStyle.NoPen);painter.setBrush(QColor('#56af93') if i<count else QColor('#7d8c88'))
            painter.setOpacity(1 if i<count else .24);painter.drawRoundedRect(2+i*3.5,18-i*2,2.4,4+i*2,1,1)
        if count<0:
            painter.setOpacity(1);painter.setPen(QPen(color,1.9));painter.drawLine(3,3,21,21)
    elif kind=='sol':
        painter.drawEllipse(7,7,10,10)
        for i in range(8):
            a=i*math.pi/4;painter.drawLine(round(12+8*math.cos(a)),round(12+8*math.sin(a)),round(12+10*math.cos(a)),round(12+10*math.sin(a)))
    elif kind=='astra':
        path=QPainterPath();path.moveTo(12,2)
        for x,y in [(15,9),(22,12),(15,15),(12,22),(9,15),(2,12),(9,9),(12,2)]:path.lineTo(x,y)
        painter.drawPath(path)
    elif kind=='terra':
        painter.drawEllipse(3,3,18,18);painter.drawEllipse(8,3,8,18);painter.drawLine(3,12,21,12)
    elif kind=='luna':
        path=QPainterPath();path.moveTo(16,3);path.cubicTo(-2,1,-2,23,16,21);path.cubicTo(5,17,5,7,16,3);painter.drawPath(path)
    elif kind=='close':painter.drawLine(6,6,18,18);painter.drawLine(18,6,6,18)
    elif kind=='pin':
        painter.drawLine(8,4,16,4);painter.drawLine(9,4,9,10);painter.drawLine(15,4,15,10)
        painter.drawLine(9,10,6,14);painter.drawLine(6,14,18,14);painter.drawLine(18,14,15,10);painter.drawLine(12,14,12,21)
    elif kind=='bookmark':
        path=QPainterPath();path.moveTo(6,3);path.lineTo(18,3);path.lineTo(18,21);path.lineTo(12,17);path.lineTo(6,21);path.closeSubpath();painter.drawPath(path)
    elif kind=='arrow':painter.drawLine(3,12,21,12);painter.drawLine(16,7,21,12);painter.drawLine(16,17,21,12)
    else:
        painter.drawRoundedRect(4,4,16,16,4,4);painter.drawLine(8,9,16,9);painter.drawLine(8,14,14,14)
    painter.end();image.setDevicePixelRatio(3)
    return image


class NoticeValue(QLabel):
    """값과 독립된 그림을 함께 그려 글자 누락과 아이콘 겹침을 방지합니다."""
    def __init__(self, text=''):
        super().__init__(text);self.symbol_kind='';self.setContentsMargins(26,0,0,0);self.setMinimumHeight(24)

    def set_symbol(self, kind):
        self.symbol_kind=kind;self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.symbol_kind:
            side=round(20*float(self.property('orbit_text_scale31') or 1))
            painter=QPainter(self);painter.drawPixmap(2,max(0,(self.height()-side)//2),notice_symbol(self.symbol_kind,side));painter.end()


class Notice(QFrame):
    completed = Signal(str)

    def __init__(self, open_details, parent=None):
        super().__init__(parent if parent is not None else _application_gui_root(),
                         Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.open_details = open_details
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setObjectName('notice')
        set_ui_style(self,'#notice {background:#f9fffc;border:1px solid #bad8ce;border-radius:16px;} QLabel {color:#193c36;background:transparent;border:none;font-weight:700;}')
        self.setFixedWidth(500)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)
        self.title = QLabel(t('모델 · 추론 강도 변경'))
        self.text = QLabel()
        self.title.setTextFormat(Qt.TextFormat.PlainText)
        self.title.setWordWrap(True)
        set_ui_style(self.title,'font-size:19px;color:#193c36;padding-bottom:4px;')
        self.text.setTextFormat(Qt.TextFormat.PlainText)
        self.text.setWordWrap(True)
        heading = QHBoxLayout()
        self.brand_mark = AnimatedBrand(32)
        self.brand_mark.hide()
        self.title_marker = QLabel('')
        self.title_marker.setAccessibleName(t('채팅 제목'))
        set_ui_style(self.title_marker,'font-size:16px;')
        heading.addWidget(self.title_marker, 0, Qt.AlignmentFlag.AlignTop)
        heading.addWidget(self.title, 1)
        close = QPushButton(t('닫기'))
        self.close_button = close
        close.setIcon(QIcon(notice_symbol('close',16)))
        close.setToolTip(t('알림 닫기 · 이력은 유지됩니다'))
        set_ui_style(close,'padding:0;font-size:12px;min-height:28px;max-height:28px;border-width:1px;')
        close.setFixedSize(64, 30)
        close.clicked.connect(self.dismiss)
        heading.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(heading)
        self.category = QLabel()
        self.category.setContentsMargins(0,0,0,0)
        set_ui_style(self.category,'font-size:13px;color:#193c36;padding:2px 0;')
        self.category.setWordWrap(True)
        self.category.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.category)
        self.task_value = QLabel()
        set_ui_style(self.task_value,'font-size:13px;color:#193c36;padding:0;')
        self.task_value.setWordWrap(True)
        self.task_value.setTextFormat(Qt.TextFormat.PlainText)
        self.task_value.hide()
        self.comparison = QFrame()
        self.comparison.setObjectName('noticeComparison')
        set_ui_style(self.comparison,'QFrame#noticeComparison {background:#edf8f2;border:1px solid #c4dfd0;border-radius:10px;}')
        values = QGridLayout(self.comparison)
        self.values_layout = values
        values.setContentsMargins(10,10,10,10)
        values.setHorizontalSpacing(8)
        values.setVerticalSpacing(8)
        self.model_previous = NoticeValue()
        self.model_current = NoticeValue()
        self.effort_previous = NoticeValue()
        self.effort_current = NoticeValue()
        self.notice_after_heading = QLabel(t('변경 후'))
        for column, text in ((1, t('이전')), (2, ''), (3, t('현재'))):
            label = self.notice_after_heading if column == 3 else QLabel(text)
            if column==2:label.setPixmap(notice_symbol('arrow',16))
            set_ui_style(label,'font-size:12px;color:#193c36;')
            values.addWidget(label, 0, column)
        self.comparison_labels=[]
        for row, caption in ((1,'모델'),(2,'추론 강도')):
            label=QLabel(t(caption));label.setWordWrap(True)
            label.setMinimumWidth(60)
            label.setMaximumWidth(66)
            set_ui_style(label,'font-size:12px;color:#193c36;padding-right:4px;')
            values.addWidget(label,row,0);self.comparison_labels.append(label)
        for row, (previous, current) in enumerate(((self.model_previous, self.model_current),
                                                    (self.effort_previous, self.effort_current)), 1):
            for column, label in ((1, previous), (3, current)):
                label.setWordWrap(True)
                label.setTextFormat(Qt.TextFormat.PlainText)
                set_ui_style(label,'font-size:16px;font-weight:700;color:#193c36;padding:3px;')
                values.addWidget(label, row, column)
        values.setColumnStretch(1, 1)
        values.setColumnStretch(3, 1)
        layout.addWidget(self.comparison)
        # 기존 필드는 실제 보이는 이전 행과 연결하며 숨김 호환 라벨은 만들지 않습니다.
        self.before_value = self.model_previous
        self.transition = self.model_previous
        self.after_value = QLabel()
        self.after_value.setWordWrap(True)
        self.after_value.setTextFormat(Qt.TextFormat.PlainText)
        set_ui_style(self.after_value,'font-size:10px;color:#193c36;padding:0;')
        self.after_value.hide()
        set_ui_style(self.text,'font-size:14px;color:#193c36;padding:10px 0;')
        layout.addWidget(self.text)
        self.selection_reason = QLabel()
        set_ui_style(self.selection_reason,'font-size:10px;color:#193c36;padding:0;')
        self.selection_reason.setWordWrap(True)
        self.selection_reason.setTextFormat(Qt.TextFormat.PlainText)
        self.selection_reason.hide()
        hint = QPushButton(t('자세히 보기'))
        hint.clicked.connect(lambda: (self.open_details(self.event_id),self.dismiss()))
        self.detail_hint = hint
        set_ui_style(hint,'QPushButton {font-size:12px;padding:4px 0;min-height:20px;text-align:right;background:transparent;border:0;color:#193c36;} QPushButton:focus {border:1px solid #9bdbc9;}')
        self.reason_disclosure = QPushButton(t('설명 더 보기'))
        self.reason_disclosure.setCheckable(True)
        self.reason_disclosure.toggled.connect(self.show_reason_original)
        set_ui_style(self.reason_disclosure,'QPushButton {font-size:12px;padding:4px 0;min-height:20px;text-align:left;background:transparent;border:0;} QPushButton:focus {border:1px solid #9bdbc9;}')
        explanation_actions=QHBoxLayout()
        explanation_actions.addWidget(self.reason_disclosure)
        explanation_actions.addStretch()
        explanation_actions.addWidget(hint)
        layout.addLayout(explanation_actions)
        self.reason_original = QPlainTextEdit()
        self.reason_original.setReadOnly(True)
        self.reason_dialog = QDialog(self)
        self.reason_dialog.setWindowTitle(t('공개 이유 원문'))
        reason_layout = QVBoxLayout(self.reason_dialog)
        reason_layout.addWidget(self.reason_original)
        self.reason_dialog.finished.connect(lambda _: self.reason_disclosure.setChecked(False))
        self.queue_hint = QLabel('')
        self.queue_hint.setWordWrap(True)
        self.queue_hint.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.queue_hint)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.dismiss)
        self.pinned = False
        self.hold = QPushButton(t('고정'))
        self.hold.setIcon(QIcon(notice_symbol('pin',18)))
        self.hold.setCheckable(True)
        self.hold.toggled.connect(self.set_pinned)
        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(self.hold)
        self.bookmark_callback = lambda key: None
        self.bookmark_button = QPushButton(t('기록 보관'))
        self.bookmark_button.setIcon(QIcon(notice_symbol('bookmark',18)))
        self.bookmark_button.clicked.connect(lambda: self.bookmark_callback(self.event_id))
        actions.addWidget(self.bookmark_button)
        layout.addLayout(actions)
        remember_translations(self)

    def apply_text_scale(self, scale):
        """독립 알림 창도 같은 기준 글꼴에서만 배율을 계산합니다."""
        from theme import unscaled_font_size
        widgets = [self, *self.findChildren(QWidget)]
        bases = [unscaled_font_size(widget) for widget in widgets]
        self.setFixedWidth(round(500*min(scale,1.25)))
        for label in self.comparison_labels:
            label.setMinimumWidth(round(60*scale));label.setMaximumWidth(round(66*scale))
        for widget,base in zip(widgets,bases):
            widget.setFont(app_font(round(base*scale)))
            widget.setProperty('orbit_text_scale31',scale)
            if isinstance(widget,NoticeValue):
                widget.setContentsMargins(round(26*scale),0,0,0);widget.setMinimumHeight(round(24*scale)+(6 if scale>1 else 0))
            source = widget.property('orbit_style_source')
            set_ui_style(widget,widget.styleSheet() if source is None else source)
        height=round(30*scale)
        # 폴리시가 전역 최소 높이로 낮추지 않도록 실제 테두리 안쪽 높이도 명시합니다.
        set_ui_style(self.close_button,f'padding:0;font-size:12px;min-height:{height-2}px;max-height:{height-2}px;border-width:1px;')
        self.close_button.setFixedSize(round(64*scale),height)
        self._last_fit_signature = None
        if hasattr(self,'notice_event'):self.fit_content()

    def show_reason_original(self, expanded):
        # 긴 설명은 독립된 스크롤 창에서 읽어 알림의 배치와 높이를 유지합니다.
        from observatory_panel import pause_notice, resume_notice
        if expanded:
            pause_notice(self)
            screen = self.screen() or QApplication.primaryScreen()
            available = getattr(self, 'available_rect', screen.availableGeometry())
            self.reason_dialog.resize(min(self.width(), available.width()), min(360, available.height()))
            self.reason_dialog.move(max(available.left(), min(self.x(), available.right()-self.reason_dialog.width()+1)),
                                    max(available.top(), min(self.y(), available.bottom()-self.reason_dialog.height()+1)))
            self.reason_dialog.show()
            # 창 테두리와 제목 표시줄까지 포함해 실제 가용 화면 안에 배치합니다.
            frame = self.reason_dialog.frameGeometry()
            extra_width = max(0, frame.width() - available.width())
            extra_height = max(0, frame.height() - available.height())
            if extra_width or extra_height:
                self.reason_dialog.resize(max(1,self.reason_dialog.width()-extra_width),
                                          max(1,self.reason_dialog.height()-extra_height))
                frame = self.reason_dialog.frameGeometry()
            target_x = max(available.left(),min(frame.x(),available.right()-frame.width()+1))
            target_y = max(available.top(),min(frame.y(),available.bottom()-frame.height()+1))
            position = self.reason_dialog.pos()
            self.reason_dialog.move(position.x()+target_x-frame.x(),position.y()+target_y-frame.y())
            self.reason_dialog.raise_()
        else:
            self.reason_dialog.hide()
            if self.isVisible() and not self.underMouse():resume_notice(self)
        self.reason_disclosure.setText(t('설명 접기') if expanded else t('설명 더 보기'))

    def enterEvent(self, event):
        from observatory_panel import pause_notice
        pause_notice(self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        from observatory_panel import resume_notice
        if not self.reason_dialog.isVisible():resume_notice(self)
        super().leaveEvent(event)

    def set_pinned(self, value):
        from observatory_panel import pause_notice, resume_notice
        self.pinned = bool(value)
        if value:pause_notice(self)
        elif not self.underMouse() and not self.reason_dialog.isVisible():resume_notice(self)

    def dismiss(self):
        if not self.isVisible():
            return
        self.timer.stop()
        self.hide()
        self.reason_dialog.hide()
        self.completed.emit(str(getattr(self, 'event_id', '')))

    def closeEvent(self, event):
        self.dismiss()
        super().closeEvent(event)

    def _content_fit_signature(self):
        """말줄임 전 제목과 실제 높이에 영향을 주는 표시 조건만 비교합니다."""
        available = getattr(self, 'available_rect', None)
        compact = available is not None and available.height() <= 400
        margins = self.layout().contentsMargins()
        width = max(1, self.contentsRect().width() - margins.left() - margins.right())
        labels = []
        queue_height = 0
        for label in self.findChildren(QLabel):
            if label is self.title:
                content = (str(getattr(self, 'notice_event', {}).get('chat_name') or t('채팅 제목 확인 불가')), label.text())
            elif label is self.queue_hint:
                queue_height = 0 if compact else label.heightForWidth(width)
                content = bool(label.text().strip())
            else:
                content = label.text()
            labels.append((content, label.font().toString(), label.styleSheet(), label.isHidden(),
                           label.minimumHeight(), label.maximumHeight(), label.wordWrap()))
        buttons = tuple((button.text(), button.font().toString(), button.styleSheet(),
                         button.minimumSize().toTuple(), button.maximumSize().toTuple())
                        for button in self.findChildren(QPushButton))
        return (self.width(), self.title.width(), self.brand_mark.size().toTuple(),
                available.getRect() if available is not None else None,
                self.logicalDpiX(), self.logicalDpiY(), self.devicePixelRatioF(), self.font().toString(),
                self.styleSheet(), QApplication.instance().styleSheet(), self.style().objectName(), tuple(labels), buttons, queue_height)

    def _adjust_content_size(self):
        """고정된 실제 폭의 줄바꿈 높이를 반영해 값 행이 압축되지 않게 합니다."""
        self.adjustSize()
        required = self.layout().totalHeightForWidth(self.width())
        if required >= 0:
            self.resize(self.width(), max(self.minimumSizeHint().height(), required))
        self.layout().activate()

    def fit_content(self, rect=None):
        # 제목은 닫기 버튼을 뺀 실제 폭으로 측정하며 원본 이벤트는 바꾸지 않습니다.
        if rect is not None:
            self.available_rect = rect
        signature = self._content_fit_signature()
        previous = getattr(self, '_last_fit_signature', None)
        if previous == signature:
            return
        available = getattr(self, 'available_rect', None)
        from observatory_panel import present_event
        full_title = str(present_event(getattr(self, 'notice_event', {}), getattr(self, 'broadcast_mode', False)).get('chat_name') or t('채팅 제목 확인 불가'))
        if previous is not None and previous[:-1] == signature[:-1] and self.title.text() == full_title:
            # 안내의 줄 높이만 바뀌었으면 제목·여백을 초기화하지 않고 실제 카드 크기만 갱신합니다.
            self.layout().activate()
            self._adjust_content_size()
            if available is None or self.height() <= available.height():
                self._last_fit_signature = self._content_fit_signature()
                return
        compact = available is not None and available.height() <= 400
        self.layout().setContentsMargins(*( (10, 6, 10, 6) if compact else (18, 14, 18, 14) ))
        self.layout().setSpacing(2 if compact else 5)
        self.values_layout.setVerticalSpacing(2 if compact else 8)
        for label in (self.after_value, self.selection_reason, self.task_value):
            label.hide()
        self.detail_hint.setVisible(True)
        self.queue_hint.setVisible(not compact and bool(self.queue_hint.text().strip()))
        self.layout().activate()
        margins = self.layout().contentsMargins()
        width = self.contentsRect().width() - margins.left() - margins.right()
        self.text.setMinimumHeight(self.text.heightForWidth(width))
        from observatory_panel import present_event
        full_title = str(present_event(getattr(self, 'notice_event', {}), getattr(self, 'broadcast_mode', False)).get('chat_name') or t('채팅 제목 확인 불가'))
        self.title.setToolTip(full_title)
        self.title.setText(full_title)
        self.title.setMinimumHeight(0)
        self.title.setMaximumHeight(16777215)
        title_width = max(1, self.title.width())
        needed = max(self.title.fontMetrics().height(), self.title.heightForWidth(title_width))
        self.title.setFixedHeight(needed)
        self.layout().activate()
        self._adjust_content_size()
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
            self._adjust_content_size()
        self._last_fit_signature = self._content_fit_signature()

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
            self.timer.start(max(5000, min(120000, int(timeout_ms))))

    def update_event(self, event, replay=None):
        # 제목 보강과 동일 ID 갱신은 다른 카드나 남은 표시 시간을 바꾸지 않습니다.
        if replay is not None:
            self.replay = replay
        self.notice_event = dict(event)
        self.event_id = event.get('id')
        from observatory_panel import present_event, style_notice
        event = present_event(event, getattr(self, 'broadcast_mode', False))
        name = str(event.get('chat_name') or t('채팅 제목 확인 불가'))
        self.title.setText(name)
        before, after = event.get('before'), event.get('after')
        if event.get('kind') == 'activity' or before is None:
            category = event_kind(event)
        else:
            model_changed = bool(before.get('model') and (after or {}).get('model') and before['model'] != after['model'])
            effort_changed = bool(before.get('effort') and (after or {}).get('effort') and before['effort'] != after['effort'])
            category = (t('모델·추론 변경') if model_changed and effort_changed else t('모델 변경') if model_changed
                        else t('추론 강도 변경') if effort_changed else t('설정 관측'))
        if event.get('kind') == 'settings':
            category += ' · ' + t('선택 설정')
        if event.get('kind') == 'activity' and before is not None and before == after:
            category += ' · ' + t('설정 유지')
        icon = '📋' if event.get('kind') == 'activity' and event.get('activity_type') == 'assigned' else '▶️' if event.get('kind') == 'activity' else '✅' if event.get('kind') == 'settings' else '🔄'
        self.category.setText(('🔁 ' + t('기록 다시 보기 · ') if self.replay else '') + icon + ' ' + t(category))
        set_ui_style(self.category,'font-size:13px;padding:2px 0;color:#193c36;')
        self.task_value.setText(task_explanation(event, 100))
        self.task_value.setToolTip(task_explanation(event, 2000))
        self.selection_reason.setText(selection_explanation(event))
        after_map = after or {}
        self.notice_after_heading.setText(t('현재'))
        for label, caption in ((self.model_previous, '이전 모델'), (self.model_current, '현재 모델'), (self.effort_previous, '이전 추론 강도'), (self.effort_current, '현재 추론 강도')):
            label.setAccessibleName(t(caption))
        self.model_previous.setText(str(before.get('model')) if before and before.get('model') else notice_previous_model(before))
        self.model_current.setText(str(after_map.get('model')) if after_map.get('model') else notice_model_label(None))
        self.effort_previous.setText(friendly_effort(before.get('effort')).rsplit(' ',1)[0] if before and before.get('effort') in ('none','minimal','low','medium','high','xhigh','ultra') else previous_field(before,'effort'))
        self.effort_current.setText(friendly_effort(after_map.get('effort')).rsplit(' ',1)[0] if after_map.get('effort') in ('none','minimal','low','medium','high','xhigh','ultra') else friendly_effort(after_map.get('effort')))
        for value,model_label,effort_label in ((before or {},self.model_previous,self.effort_previous),(after_map,self.model_current,self.effort_current)):
            family=re.fullmatch(r'gpt-\d+(?:\.\d+)?-(sol|astra|terra|luna)',str(value.get('model') or ''))
            model_label.set_symbol(family.group(1) if family else 'model')
            effort_label.set_symbol('effort:'+str(value.get('effort') or 'unknown'))
        for key, labels in (('model', (self.model_previous, self.model_current)), ('effort', (self.effort_previous, self.effort_current))):
            changed = event.get('kind') != 'activity' and before is not None and before.get(key) and after_map.get(key) and before.get(key) != after_map.get(key)
            for index,label in enumerate(labels):
                size=16 if key=='model' else 14
                set_ui_style(label,f'font-size:{size}px;font-weight:700;color:#193c36;padding:5px;' + ('background:#d4f3e7;border-radius:6px;' if changed and index==1 else ''))
        self.after_value.setText((t('현재 설정 · ') if event.get('kind') == 'activity' else t('→ 변경 후 · ')) + (self.setting_label(after).replace('\n',' · ') if after is not None else t('확인 불가')))
        self.text.setText(notice_reason_caption(event) + notice_reason(event, 140, max_sentences=1))
        self.reason_original.setPlainText(notice_reason_original(event))
        self.reason_disclosure.setText(t('설명 접기') if self.reason_disclosure.isChecked() else t('설명 더 보기'))
        self.text.setToolTip(notice_reason_original(event))
        style_notice(self)
        self.fit_content()

    @staticmethod
    def setting_label(value):
        if value is None:
            return t('이전 기록 없음')
        effort = value.get('effort')
        labels = {'none': t('없음'), 'minimal': t('최소'), 'low': t('낮음'), 'medium': t('보통'),
                  'high': t('높음'), 'xhigh': t('매우 높음'), 'ultra': t('최고')}
        strength = f'{labels[effort]} ({effort})' if effort in labels else str(effort or t('확인 불가'))
        return str(value.get('model') or t('모델 확인 불가')) + '\n' + t('추론') + ' ' + strength

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_details(self.event_id)
            self.dismiss()


class WeatherLocationDialog(QDialog):
    """도시 검색은 명시한 요청에만 수행하고 검증된 후보만 저장합니다."""
    def __init__(self, controller):
        super().__init__(controller.window)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.controller = controller
        self.setWindowTitle(t('지역 선택'))
        self.resize(500, 410)
        layout = QVBoxLayout(self)
        explanation = QLabel(t('도시·장소를 고르면 행사와 날씨를 함께 바꿉니다.'))
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel(t('위치 모드')))
        self.mode_selector = QComboBox()
        self.mode_selector.addItem(t('자동'), 'automatic')
        self.mode_selector.addItem(t('수동'), 'manual')
        manual = bool(controller.settings.values.get('weather_location'))
        self.mode_selector.setCurrentIndex(1 if manual else 0)
        mode_row.addWidget(self.mode_selector, 1)
        layout.addLayout(mode_row)
        self.mode_status = QLabel(t('현재 모드: 수동') if manual else t('현재 모드: 자동'))
        self.mode_status.setWordWrap(True)
        layout.addWidget(self.mode_status)
        event_row=QHBoxLayout()
        from city_ui33 import city_summary
        snapshot=getattr(getattr(controller,'weather',None),'snapshot',{})
        self.city_ref=snapshot.get('city_ref')
        self.city_country=controller.settings.values.get('theme_country','KR')
        self.city_summary=QLabel(city_summary(self.city_ref,self.city_country,regional_calendar_date().year))
        self.city_summary.setWordWrap(True);event_row.addWidget(self.city_summary,1)
        self.city_button=QPushButton(t('축제 목록·출처'))
        self.city_button.clicked.connect(self.show_city_events);event_row.addWidget(self.city_button)
        layout.addLayout(event_row)
        search_row = QHBoxLayout()
        self.search_kind = QComboBox()
        for caption, kind in (('도시·지역','city'), ('주소·장소','place'), ('국가','country')):
            self.search_kind.addItem(t(caption), kind)
        search_row.addWidget(self.search_kind)
        self.query = QLineEdit()
        self.query.setMaxLength(80)
        self.query.setPlaceholderText(t('도시 이름 · 예: 수원, Paris'))
        self.query.setAccessibleName(t('도시 이름'))
        self.search_button = QPushButton(t('검색'))
        search_row.addWidget(self.query, 1)
        search_row.addWidget(self.search_button)
        layout.addLayout(search_row)
        self.status_label = QLabel(t('검색어는 검색 버튼을 누를 때 Open-Meteo로 전송됩니다.'))
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        self.attribution = QLabel('© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · Photon')
        self.attribution.setWordWrap(True)
        self.attribution.setOpenExternalLinks(True)
        layout.addWidget(self.attribution)
        self.cities = QListWidget()
        self.cities.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.cities.setWordWrap(True)
        layout.addWidget(self.cities, 1)
        buttons = QHBoxLayout()
        self.automatic_button = QPushButton(t('자동 모드 적용'))
        self.apply_button = QPushButton(t('선택한 지역 적용'))
        self.apply_button.setEnabled(False)
        self.cancel_button = QPushButton(t('취소'))
        for button in (self.automatic_button, self.apply_button, self.cancel_button):
            buttons.addWidget(button)
        layout.addLayout(buttons)
        self.client = None
        self.search_kind.currentIndexChanged.connect(self.change_search_kind)
        self.search_button.clicked.connect(self.search)
        self.query.returnPressed.connect(self.search)
        self.cities.currentRowChanged.connect(lambda row: self.apply_button.setEnabled(row >= 0))
        self.cities.itemDoubleClicked.connect(lambda item: self.apply_selection())
        self.apply_button.clicked.connect(self.apply_selection)
        self.automatic_button.clicked.connect(lambda: self.apply_city(None))
        self.cancel_button.clicked.connect(self.reject)
        self.finished.connect(lambda result: self.close_search())
        self.mode_selector.currentIndexChanged.connect(self.change_location_mode)
        self.change_search_kind()
        self.update_search_enabled()
        remember_translations(self)

    def refresh_city_summary(self):
        from city_ui33 import city_summary
        snapshot=getattr(getattr(self.controller,'weather',None),'snapshot',{})
        self.city_ref=snapshot.get('city_ref')
        self.city_country=self.controller.settings.values.get('theme_country','KR')
        self.city_summary.setText(city_summary(self.city_ref,self.city_country,regional_calendar_date().year))

    def show_city_events(self):
        from city_ui33 import CityEventsDialog
        self.city_dialog=CityEventsDialog(self,self.city_ref,self.city_country,regional_calendar_date(),
                                          getattr(self.controller,'city_updater',None))
        self.city_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.city_dialog.show()

    def update_search_enabled(self):
        manual = self.mode_selector.currentData() == 'manual'
        for widget in (self.search_kind, self.query, self.search_button, self.cities):
            widget.setEnabled(manual)
        self.apply_button.setEnabled(manual and self.cities.currentRow() >= 0)

    def change_location_mode(self):
        if self.mode_selector.currentData() == 'automatic':
            self.apply_city(None)
        else:
            # 수동 모드는 검색 준비 상태이며 실제 후보 적용 전에는 저장하지 않습니다.
            self.update_search_enabled()

    def retranslate(self):
        retranslate_widgets(self)
        self.mode_selector.setItemText(0,t('자동'))
        self.mode_selector.setItemText(1,t('수동'))
        if hasattr(self,'city_dialog') and isValid(self.city_dialog):self.city_dialog.retranslate()
        for index,caption in enumerate(('도시·지역','주소·장소','국가')):
            self.search_kind.setItemText(index,t(caption))
        self.change_search_kind()

    def close_search(self):
        if self.client is not None:self.client.close()

    def change_search_kind(self):
        self.close_search()
        self.client = None
        self.cities.clear()
        self.apply_button.setEnabled(False)
        kind = self.search_kind.currentData()
        self.query.setPlaceholderText(t('국가 이름 · 예: 대한민국, Japan') if kind=='country' else t('주소나 장소 이름') if kind=='place' else t('도시 이름 · 예: 수원, Paris'))
        if kind == 'country':
            self.status_label.setText(t('국가만 고르면 행사 기준만 바뀌고 날씨 지역은 유지됩니다.'))
        else:
            self.client = (PlaceSearchClient if kind=='place' else CitySearchClient)(self,language=get_language())
            client = self.client
            client.results.connect(lambda rows: self.show_results(rows) if self.client is client else None)
            client.failed.connect(lambda message: self.show_error(message) if self.client is client else None)
            if kind == 'place':
                if self.controller.settings.values.get('theme_country_mode')=='selected':
                    client.set_country(self.controller.settings.values.get('theme_country'))
                self.status_label.setText(t('검색할 때만 Photon / OpenStreetMap으로 장소 이름을 보냅니다.'))
            else:self.status_label.setText(t('검색할 때만 Open-Meteo로 도시 이름을 보냅니다.'))

    def search(self):
        self.cities.clear()
        self.apply_button.setEnabled(False)
        if self.search_kind.currentData() == 'country':
            for row in find_countries(self.query.text(),get_language()):
                item = QListWidgetItem(row['name']+' · '+row['code'])
                item.setData(Qt.ItemDataRole.UserRole,dict(country_only=True,country_code=row['code']))
                self.cities.addItem(item)
            self.status_label.setText(t('나라를 고르면 그 나라의 행사 기준을 적용합니다. 날씨는 도시·장소를 따로 골라 주세요.'))
        else:
            self.status_label.setText(t('지역을 찾는 중입니다.'))
            self.client.search(self.query.text())

    def show_results(self, rows):
        self.cities.clear()
        for row in rows:
            city = normalize_city(row)
            if city is None:
                continue
            label = city.get('display_name') or ' · '.join(dict.fromkeys(x for x in (city['name'], city['admin1'], city['country']) if x))
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, city)
            item.setToolTip(label)
            self.cities.addItem(item)
        self.status_label.setText(t('동명 지역이 있으니 도시·행정구역·나라를 확인한 뒤 골라 주세요.') if self.cities.count() else t('검색 결과가 없습니다. 영문 도시 이름이나 주소·장소 검색을 이용해 보세요.'))

    def show_error(self, message):
        self.status_label.setText(t(message))
        self.status_label.setToolTip(t(message))

    def apply_selection(self):
        item = self.cities.currentItem()
        if item is not None:
            value = item.data(Qt.ItemDataRole.UserRole)
            if value.get('country_only'):
                try:self.controller.set_theme_country(value['country_code'])
                except (ValueError,OSError):
                    self.status_label.setText(t('지역을 저장하지 못했습니다. 다시 시도해 주세요.'));return
                self.accept()
            else:self.apply_city(value)

    def apply_city(self, city):
        try:
            self.controller.set_weather_location(city)
        except (ValueError, OSError) as error:
            self.status_label.setText(t('지역을 저장하지 못했습니다. 다시 시도해 주세요.'))
            return
        self.accept()


class DiagnosticLabel(QLabel):
    """오류가 있을 때 변경 기록 안에 원문을 보여 주는 읽기 전용 라벨입니다."""
    def __init__(self):
        super().__init__()
        self.setWordWrap(True)
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        set_ui_style(self,'font-size:12px;color:#49615b;border-left:2px solid #aaaaaa;padding:10px;')
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
        self.setText(t('감시 진단\n') + self.original_text if failed else '')
        self.setVisible(bool(failed))
    def toPlainText(self):
        return self.original_text


class Details(QDialog):
    def __init__(self, controller, parent=None):
        owner = parent if parent is not None else getattr(controller, 'gui_owner', None)
        super().__init__(owner if owner is not None else _application_gui_root())
        self.controller = controller
        self.setWindowTitle(t('Codex Orbit · 로컬 모델 변경 기록'))
        self.resize(1120, 780)
        self.setMinimumSize(740, 540)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 20)
        layout.setSpacing(10)
        header = QHBoxLayout()
        self.brand_mark = AnimatedBrand(40)
        header.addWidget(self.brand_mark)
        self.setWindowIcon(QIcon(QPixmap.fromImage(brand_image(32))))
        heading = QLabel('Codex Orbit')
        set_ui_style(heading,'font-size:19px;color:#183c36;')
        header.addWidget(heading, 1)
        self.language_combo = QComboBox()
        self.language_combo.addItem('한국어', 'ko')
        self.language_combo.addItem('English', 'en')
        self.language_combo.setCurrentIndex(0 if get_language() == 'ko' else 1)
        self.language_combo.setAccessibleName(t('언어'))
        self.language_combo.currentIndexChanged.connect(
            lambda index: self.controller.set_language(self.language_combo.itemData(index)))
        header.addWidget(self.language_combo)
        self.usage_compact = QLabel(t('사용 한도 미확인'))
        set_ui_style(self.usage_compact,'font-size:12px;color:#55736b;')
        header.addWidget(with_symbol(self.usage_compact, 'quota'))
        layout.addLayout(header)
        motion_controls = QHBoxLayout()
        self.motion_speed_label = QLabel(t('회전 속도'))
        motion_controls.addWidget(self.motion_speed_label)
        self.motion_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.motion_speed_slider.setRange(25, 300)
        self.motion_speed_slider.setSingleStep(5)
        self.motion_speed_slider.setPageStep(25)
        self.motion_speed_slider.setEnabled(controller is not None)
        self.motion_speed_slider.setAccessibleName(t('회전 속도'))
        self.motion_speed_slider.setToolTip(t('회전 속도만 변경합니다. 날짜와 시각은 그대로입니다.'))
        motion_controls.addWidget(self.motion_speed_slider, 1)
        self.motion_speed_value = QLabel()
        self.motion_speed_value.setMinimumWidth(58)
        motion_controls.addWidget(self.motion_speed_value)
        self.motion_speed_reset = QPushButton(t('기본 1배 복원'))
        self.motion_speed_reset.setEnabled(controller is not None)
        self.motion_speed_reset.clicked.connect(lambda: self.controller.change_motion_speed(1.0))
        motion_controls.addWidget(self.motion_speed_reset)
        self.update_motion_speed()
        self.motion_speed_slider.valueChanged.connect(lambda value: self.controller.change_motion_speed(value / 100))
        layout.addLayout(motion_controls)
        self.motion_speed_error_text = ''
        self.motion_speed_error = QLabel()
        self.motion_speed_error.setTextFormat(Qt.TextFormat.PlainText)
        self.motion_speed_error.setWordWrap(True)
        self.motion_speed_error.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        set_ui_style(self.motion_speed_error,'color:#355c50;font-size:12px;')
        self.motion_speed_error.hide()
        layout.addWidget(self.motion_speed_error)
        self.tabs = QTabWidget()
        self.tabs.setIconSize(QSize(20, 20))
        layout.addWidget(self.tabs, 1)
        self.build_history()
        usage_page = QWidget()
        usage_layout = QVBoxLayout(usage_page)
        usage_layout.setContentsMargins(12, 16, 12, 12)
        self.build_usage(usage_layout)
        usage_outer=QScrollArea();usage_outer.setWidgetResizable(True);usage_outer.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);usage_outer.setWidget(usage_page)
        self.tabs.insertTab(1, usage_outer, symbol_icon('quota'), t('사용 한도'))
        self.tabs.currentChanged.connect(self.update_usage_motion)
        self.setStyleSheet('')
        remember_translations(self)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'history_layout_timer'):self.history_layout_timer.start(0)

    def update_history_layout(self):
        if not hasattr(self,'history_splitter'):return
        split=self.history_splitter;grid=self.history_comparison_grid
        # 현재 글꼴의 실제 헤더·값 권장 폭과 기존 여백으로 두 열에 필요한 폭을 구합니다.
        column=max([label.sizeHint().width()+27 for label in self.history_comparison_headers]+
                   [label.minimumSizeHint().width() for label in (self.model_previous,self.model_current,self.effort_previous,self.effort_current)])
        arrow=max(label.sizeHint().width() for label in self.history_comparison_arrows)
        card_margin=self.card.layout().contentsMargins();panel_margin=self.history_detail_scroll.widget().layout().contentsMargins()
        detail_width=2*column+arrow+2*grid.horizontalSpacing()+card_margin.left()+card_margin.right()+panel_margin.left()+panel_margin.right()
        # 수리 전 영문100% 상세의 실측 최소461px를 공통 읽기 폭 하한으로 유지합니다.
        scale=self.controller.settings.values.get('text_scale',100)/100 if self.controller is not None else 1.0
        detail_width=max(detail_width,round(461*scale))
        required=self.history.minimumWidth()+split.handleWidth()+self.history_detail_scroll.verticalScrollBar().sizeHint().width()+detail_width
        orientation=Qt.Orientation.Vertical if split.width()<required else Qt.Orientation.Horizontal
        if split.orientation()==orientation:return
        if orientation==Qt.Orientation.Vertical:
            self.history_horizontal_sizes=split.sizes();split.setOrientation(orientation);split.setSizes([1,3])
        else:
            split.setOrientation(orientation);split.setSizes(getattr(self,'history_horizontal_sizes',[310,700]))

    def update_motion_speed(self):
        value = self.controller.settings.values['motion_speed'] if self.controller is not None else 1.0
        self.motion_speed_slider.blockSignals(True)
        self.motion_speed_slider.setValue(round(value * 100))
        self.motion_speed_slider.blockSignals(False)
        self.motion_speed_value.setText(t('{speed:g}배', speed=value))

    def show_motion_speed_error(self, message):
        self.motion_speed_error_text = message
        # 오류 원문은 일반 텍스트로 보여 주고 긴 진단은 표시 길이를 제한합니다.
        detail = message[:500] + ('…' if len(message) > 500 else '')
        self.motion_speed_error.setText(t('회전 속도 변경 실패: {error}', error=detail) if message else '')
        self.motion_speed_error.setVisible(bool(message))

    def retranslate(self):
        retranslate_widgets(self)
        self.update_motion_speed()
        self.show_motion_speed_error(self.motion_speed_error_text)
        self.language_combo.blockSignals(True)
        self.language_combo.setCurrentIndex(0 if get_language() == 'ko' else 1)
        self.language_combo.blockSignals(False)
        self.tabs.setTabText(0, t('변경 기록'))
        self.tabs.setTabText(1, t('사용 한도'))
        for index in range(self.history.count()):
            item = self.history.item(index)
            item.setText(history_label(item.data(Qt.ItemDataRole.UserRole)))
        # 비어 있는 앱 기본 안내만 갱신하고 원문이나 별도 내용을 바꾸지 않습니다.
        if self.history.count() == 0 and self.detail.toPlainText() == self.empty_history_text:
            self.empty_history_text = t(EMPTY_HISTORY_GUIDANCE)
            self.detail.setPlainText(self.empty_history_text)
        self.select_event(self.history.currentItem(), None)
        self.toggle_evidence(self.evidence_toggle.isChecked())

    def update_usage_motion(self, *args):
        self.usage_hero.set_active(self.isVisible() and self.tabs.currentIndex() == 1)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_usage_motion()

    def hideEvent(self, event):
        self.usage_hero.set_active(False)
        super().hideEvent(event)

    def build_usage(self, layout):
        panel = QFrame()
        panel.setObjectName('usagePanel')
        self.usage_panel = panel
        self.usage_page_layout = layout
        box = QVBoxLayout(panel)
        box.setContentsMargins(22, 20, 22, 20)
        box.setSpacing(12)
        heading = QHBoxLayout()
        title = QLabel(t('계정 사용 한도'))
        set_ui_style(title,'color:#355c50;font-size:25px;font-weight:700;')
        title.setWordWrap(True);title.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
        usage_title=with_symbol(title,'quota');usage_title.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred);heading.addWidget(usage_title,1)
        self.usage_refresh = QPushButton(t('새로고침'))
        self.usage_refresh.setIcon(symbol_icon('refresh'))
        self.usage_refresh.setIconSize(QSize(20, 20))
        self.usage_refresh.setMinimumHeight(44)
        self.usage_refresh.setAccessibleName(t('계정 사용 한도 새로고침'))
        self.usage_refresh.clicked.connect(lambda: self.controller.usage.manual_refresh())
        heading.addWidget(self.usage_refresh)
        box.addLayout(heading)
        self.usage_status = QLabel(t('잔량 조회 준비 · 30초마다 자동 갱신'))
        self.usage_status.setWordWrap(True)
        self.usage_status.setTextFormat(Qt.TextFormat.PlainText)
        set_ui_style(self.usage_status,'color:#355c50;font-size:13px;')
        box.addWidget(self.usage_status)
        content = QHBoxLayout()
        content.setSpacing(14)
        self.usage_scroll = QScrollArea()
        self.usage_scroll.setWidgetResizable(True)
        self.usage_scroll.setMinimumHeight(120)
        self.usage_rows = QWidget()
        self.usage_rows.setObjectName('usageRows')
        set_ui_style(self.usage_rows,'QWidget#usageRows {background:transparent;}')
        set_ui_style(self.usage_scroll,'QScrollArea {background:transparent;border:0;} QScrollArea > QWidget {background:transparent;}')
        self.usage_rows_layout = QVBoxLayout(self.usage_rows)
        self.usage_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.usage_rows_layout.setSpacing(10)
        self.usage_values = QLabel(t('계정 한도 미확인'))
        self.usage_values.setWordWrap(True)
        self.usage_values.setTextFormat(Qt.TextFormat.PlainText)
        self.usage_rows_layout.addWidget(self.usage_values)
        self.usage_scroll.setWidget(self.usage_rows)
        content.addWidget(self.usage_scroll, 65)
        self.usage_hero = CalendarHero()
        self.usage_hero.setFixedHeight(230)
        content.addWidget(self.usage_hero, 35, Qt.AlignmentFlag.AlignTop)
        box.addLayout(content, 1)
        layout.addWidget(panel, 0)
        layout.addStretch(1)
        panel.setMaximumHeight(430)

    def display_usage(self, value):
        stale, busy = value.get('stale', True), value.get('busy', False)
        checked = value.get('checked_at')
        updated = t(reset_label(checked)) if checked else t('아직 조회하지 않음')
        self.usage_status.setText((t('조회 지연 · 이전 조회 값 · ') if stale and checked else '') + t(value.get('status', '미확인')) +
                                  t('  ·  최종 조회: ') + updated + t('  ·  30초 자동 갱신'))
        self.usage_refresh.setEnabled(not busy)
        rows = value.get('rows', [])
        self.usage_hero.setFixedHeight(230 if rows else 140)
        self.usage_scroll.setMinimumHeight(180 if rows else 100)
        self.usage_panel.setMaximumHeight(430 if len(rows) <= 1 else 16777215)
        self.usage_page_layout.setStretch(1, 1 if len(rows) <= 1 else 0)
        while self.usage_rows_layout.count() > 1:
            item = self.usage_rows_layout.takeAt(1)
            if item.widget():
                # 지연 삭제 전에도 이전 언어의 행이 새 행과 겹쳐 보이지 않게 합니다.
                item.widget().hide()
                item.widget().deleteLater()
        texts = []
        for row in rows:
            remaining = row['remaining']
            label = remaining_text(remaining)
            text = str(row['bucket']) + " · " + t(row['period']) + "  " + label + "  ·  " + t("초기화: ") + t(reset_label(row['resets_at']))
            if stale:
                text += t('  ·  이전 조회 값')
            texts.append(text)
            bar = QProgressBar()
            bar.setRange(0, 1000000)
            bar.setValue(round(remaining * 10000) if remaining is not None and not stale else 0)
            bar.setFormat(t(row['period']) + (t(' · 이전 조회') if stale else '') + ' · ' + label)
            bar.setTextVisible(False)
            bar.setAccessibleName(text)
            bar.setToolTip(percentage_tooltip(remaining))
            bar.setEnabled(not stale and remaining is not None)
            bar.setFixedHeight(12)
            set_ui_style(bar,'QProgressBar {border:0;border-radius:6px;background:#dceee4;} QProgressBar::chunk {background:#159e6c;border-radius:6px;}')
            self.usage_rows_layout.addWidget(bar)
            info = QLabel(str(row['bucket']) + " · " + t(row['period']))
            info.setTextFormat(Qt.TextFormat.PlainText)
            info.setWordWrap(True)
            set_ui_style(info,'color:#355c50;font-size:15px;')
            self.usage_rows_layout.addWidget(info)
            number = QLabel(label)
            number.setToolTip(percentage_tooltip(remaining))
            number.setTextFormat(Qt.TextFormat.PlainText)
            number.setWordWrap(True)
            set_ui_style(number,'color:#355c50;font-size:42px;font-weight:700;')
            self.usage_rows_layout.addWidget(number)
            reset = QLabel(t('초기화: ') + t(reset_label(row['resets_at'])) + (t(' · 이전 조회 값') if stale else ''))
            reset.setTextFormat(Qt.TextFormat.PlainText)
            reset.setWordWrap(True)
            set_ui_style(reset,'color:#355c50;font-size:13px;padding-bottom:18px;')
            self.usage_rows_layout.addWidget(reset)
        self.usage_rows_layout.addStretch()
        self.usage_compact.setText((t('이전 조회 · ') if stale and checked else '') + (remaining_text(rows[0]['remaining']) if rows and rows[0].get('remaining') is not None else t('사용 한도 미확인')))
        self.usage_compact.setToolTip(percentage_tooltip(rows[0]['remaining']) if rows else t('미확인'))
        self.usage_values.setText('\n'.join(texts) if texts else t('계정 한도 미확인 · 남은 토큰 개수가 아닌 사용 한도 비율입니다.'))
        self.usage_values.setVisible(not rows)

    def build_history(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(8)
        self.summary = QLabel(t('감시 준비 중'))
        set_ui_style(self.summary,'color:#55736b;font-size:11px;')
        self.summary.setTextFormat(Qt.TextFormat.PlainText)
        self.summary.setWordWrap(True)
        self.summary.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        layout.addWidget(self.summary)
        self.notice_summary = QLabel(t('알림 대기 0건'))
        set_ui_style(self.notice_summary,'color:#55736b;font-size:11px;')
        layout.addWidget(self.notice_summary)
        self.notice_summary.setWordWrap(True)
        split = QSplitter();self.history_splitter=split
        self.history_layout_timer=QTimer(self);self.history_layout_timer.setSingleShot(True);self.history_layout_timer.timeout.connect(self.update_history_layout)
        self.history = QListWidget()
        self.history.setWordWrap(True)
        self.history.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history.currentItemChanged.connect(self.select_event)
        panel = QWidget();panel.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
        cards = QVBoxLayout(panel)
        cards.setContentsMargins(16, 6, 0, 0)
        cards.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.card = QFrame()
        self.card.setObjectName('eventCard')
        self.card.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)
        self.chat_title = QLabel(t('변경을 기다리고 있습니다'))
        set_ui_style(self.chat_title,'font-size:23px;font-weight:700;color:#183c36;padding:2px 0 6px 0;')
        self.change_heading = QLabel(t('변경을 기다리고 있습니다'))
        set_ui_style(self.change_heading,'font-size:13px;color:#14785d;padding:5px 8px;')
        self.model_transition = QLabel('')
        set_ui_style(self.model_transition,'font-size:26px;font-weight:700;color:#23453f;')
        self.model_previous = self.model_transition
        self.model_current = QLabel('—')
        set_ui_style(self.model_current,'font-size:26px;font-weight:700;color:#23453f;')
        self.effort_transition = QLabel('')
        set_ui_style(self.effort_transition,'font-size:26px;font-weight:700;color:#23453f;')
        self.effort_previous = self.effort_transition
        self.effort_current = QLabel('—')
        set_ui_style(self.effort_current,'font-size:26px;font-weight:700;color:#23453f;')
        self.before_value = QLabel(t('변경 전  ·  —'))
        self.after_value = QLabel(t('변경 후  ·  —'))
        set_ui_style(self.after_value,'font-size:12px;color:#55736b;padding:0;')
        set_ui_style(self.before_value,'font-size:12px;color:#55736b;')
        self.activity_message = QLabel()
        self.activity_message.setWordWrap(True)
        set_ui_style(self.activity_message,'font-size:22px;font-weight:700;color:#183c36;padding:6px 0;')
        self.activity_message.hide()
        self.task_value = QLabel(t('공개된 작업 설명을 기다립니다.'))
        self.selection_reason = QLabel(t('모델·추론 강도 선택 이유는 공개되지 않았습니다.'))
        set_ui_style(self.task_value,'font-size:20px;font-weight:700;color:#23453f;padding:4px 0 10px 0;')
        set_ui_style(self.selection_reason,'font-size:11px;color:#55736b;padding:4px 0;')
        self.reason_title = QLabel(t('왜 맡겼나요? · 공개 설명'))
        set_ui_style(self.reason_title,'color:#355c50;font-size:11px;padding-top:10px;')
        self.reason_value = QLabel(t('첫 실행은 과거 기록을 기준선으로 읽으며 과거 알림을 만들지 않습니다.'))
        set_ui_style(self.reason_value,'font-size:15px;background:#edf8f2;border:1px solid #c4dfd0;border-radius:12px;padding:14px;color:#355c50;')
        self.event_time = QLabel('')
        set_ui_style(self.event_time,'color:#355c50;font-size:11px;padding:0;')
        all_labels = (self.chat_title, self.event_time, self.change_heading, self.model_previous, self.model_current,
                      self.effort_previous, self.effort_current, self.before_value, self.after_value,
                      self.reason_title, self.reason_value, self.task_value, self.selection_reason, self.activity_message)
        for label in all_labels:
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        card_layout.addWidget(with_symbol(self.event_time, 'time'))
        for label in (self.chat_title, self.change_heading, self.activity_message, self.task_value):card_layout.addWidget(label)
        table = QGridLayout();self.history_comparison_grid=table
        self.history_comparison_headers=[];self.history_comparison_arrows=[]
        table.setHorizontalSpacing(18)
        table.setVerticalSpacing(12)
        self.after_headings = []
        for row, (kind, previous, current) in enumerate((('모델',self.model_previous,self.model_current),
                                                       ('추론 강도',self.effort_previous,self.effort_current))):
            for col, text in ((0,t('이전')+' '+t(kind)),(2,t('새')+' '+t(kind))):
                label=QLabel(text + (' 🧠' if row == 1 else ''));set_ui_style(label,'font-size:12px;color:#355c50;')
                label.setWordWrap(True);label.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Minimum);self.history_comparison_headers.append(label)
                if col == 2: self.after_headings.append((label, kind))
                table.addWidget(with_symbol(label, 'model' if row == 0 else 'effort'),row*3,col)
            arrow=QLabel('→');set_ui_style(arrow,'font-size:16px;color:#55736b;')
            table.addWidget(previous,row*3+1,0)
            self.history_comparison_arrows.append(arrow);table.addWidget(arrow,row*3+1,1)
            table.addWidget(current,row*3+1,2)
            line=QFrame();line.setFrameShape(QFrame.Shape.HLine);set_ui_style(line,'color:#3c5662;')
            table.addWidget(line,row*3+2,0,1,3)
        table.setColumnStretch(0,1);table.setColumnStretch(2,1)
        card_layout.addLayout(table)
        for label in (self.before_value,self.after_value):card_layout.addWidget(label);label.hide()
        card_layout.addWidget(with_symbol(self.reason_title, 'reason'))
        card_layout.addWidget(self.reason_value)
        card_layout.addWidget(self.selection_reason)
        self.diagnostics = DiagnosticLabel()
        cards.addWidget(self.diagnostics)
        cards.addWidget(self.card)
        self.evidence_toggle = QPushButton(t('▸ 원문 · ID · 근거 펼치기'))
        self.evidence_toggle.setObjectName('disclosure')
        self.evidence_toggle.setIcon(symbol_icon('reason'))
        self.evidence_toggle.setCheckable(True)
        cards.addWidget(self.evidence_toggle)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        self.detail.setMinimumHeight(180)
        self.empty_history_text = t(EMPTY_HISTORY_GUIDANCE)
        self.detail.setPlainText(self.empty_history_text)
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
        self.tabs.addTab(page, symbol_icon('history'), t('변경 기록'))

    def select_event(self, current, _previous):
        if current:
            value = current.data(Qt.ItemDataRole.UserRole)
            from observatory_panel import present_event
            value = present_event(value, bool(self.controller and self.controller.settings.values.get('broadcast_mode',False)))
            self.detail.setPlainText(event_description(value))
            self.chat_title.setText(str(value.get('chat_name') or t('채팅 제목 확인 불가')))
            before, after = value.get('before') or {}, value.get('after') or {}
            model_changed = bool(before.get('model') and after.get('model') and before['model'] != after['model'])
            effort_changed = bool(before.get('effort') and after.get('effort') and before['effort'] != after['effort'])
            if value.get('kind') == 'activity' or value.get('before') is None:
                heading = event_kind(value)
            else:
                heading = (t('모델·추론 강도가 바뀌었습니다') if model_changed and effort_changed
                           else t('모델이 바뀌었습니다') if model_changed
                           else t('추론 강도가 바뀌었습니다') if effort_changed else t('설정 관측'))
            if value.get('kind') == 'activity' and value.get('before') is not None and value['before'] == value.get('after'):
                heading += ' · ' + t('설정 유지')
            self.change_heading.setText(t(heading))
            set_ui_style(self.change_heading,'font-size:13px;padding:5px 8px;border-radius:8px;color:'+event_accent(value)+';background:#e0f4e9;')
            self.activity_message.setText(activity_message(value))
            self.activity_message.setVisible(bool(activity_message(value)))
            self.task_value.setText(task_explanation(value))
            self.selection_reason.setText(selection_explanation(value))
            for heading, kind in self.after_headings:
                heading.setText(t('현재') + ' ' + t(kind) + (' 🧠' if kind == '추론 강도' else ''))
            self.model_previous.setText(notice_previous_model(value.get('before')))
            self.model_current.setText(notice_model_label(after.get('model')))
            self.effort_previous.setText(previous_field(value.get('before'), 'effort'))
            self.effort_current.setText(friendly_effort(after.get('effort')))
            before = value.get('before')
            for key, labels in (('model', (self.model_previous, self.model_current)), ('effort', (self.effort_previous, self.effort_current))):
                changed = value.get('kind') != 'activity' and before is not None and before.get(key) and after.get(key) and before.get(key) != after.get(key)
                for label in labels:
                    set_ui_style(label,'font-size:26px;font-weight:700;color:#23453f;' + ('background:#d4f3e7;border-radius:8px;padding:4px;' if changed else ''))
            self.before_value.setText(t('이전 기록 없음') if value.get('before') is None
                                      else t('이전') + '  ' + model_card_label(value['before']))
            self.after_value.setText((t('현재') + '  ' if value.get('kind') == 'activity' else '→  ') + model_card_label(value.get('after')))
            self.reason_title.setText(t('💬 이유'))
            self.reason_value.setText(notice_reason(value, 600))
            self.reason_value.setToolTip(notice_reason_original(value))
            self.event_time.setText(kst_label(value.get('time')))
            self.history_layout_timer.start(0)

    def toggle_evidence(self, checked):
        self.detail.setVisible(checked)
        self.evidence_toggle.setText(t('▾ 원문 · ID · 근거 접기') if checked else t('▸ 원문 · ID · 근거 펼치기'))

    def _history_items_by_id(self):
        items = {}
        for index in range(self.history.count()):
            item = self.history.item(index)
            identity = item.data(Qt.ItemDataRole.UserRole).get('id')
            if isinstance(identity, str) and identity:
                # 중복 ID가 있어도 기존 선두 행 우선 동작을 유지합니다.
                items.setdefault(identity, item)
        return items

    def update_event(self, event, item_index=None):
        identity = event.get('id')
        if item_index is not None and isinstance(identity, str) and identity:
            item = item_index.get(identity)
            candidates = () if item is None else (item,)
        else:
            candidates = (self.history.item(index) for index in range(self.history.count()))
        for item in candidates:
            old = item.data(Qt.ItemDataRole.UserRole)
            if identity and old.get('id') == identity:
                if old == event:
                    return True
                item.setData(Qt.ItemDataRole.UserRole, event)
                item.setText(history_label(event))
                item.setIcon(event_icon(event))
                if item == self.history.currentItem():
                    self.select_event(item, None)
                return True
        return False

    def promote_first_observation(self, event):
        """실제 첫 관측 한 행만 안정된 활동 ID로 보강하며 다른 변경은 보존합니다."""
        identity = event.get('first_observation_id')
        for index in range(self.history.count()):
            item = self.history.item(index)
            old = item.data(Qt.ItemDataRole.UserRole)
            if old.get('id') != identity:
                continue
            if old.get('target') != event.get('target') or old.get('before') is not None or old.get('kind') == 'activity':
                return False
            item.setData(Qt.ItemDataRole.UserRole, event)
            item.setText(history_label(event))
            item.setIcon(event_icon(event))
            if item == self.history.currentItem():
                self.select_event(item, None)
            return True
        return None

    def add_event(self, event):
        if self.update_event(event):
            return
        item = QListWidgetItem(history_label(event))
        item.setIcon(event_icon(event))
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


class Controller(QObject):
    def __init__(self, settings, start_worker=True, start_usage=None, start_weather=False):
        # 필수 이미지와 오늘의 조형을 창과 타이머 생성 전에 검사합니다.
        validated_theme_country(settings.values.get('theme_country','KR'))
        get_atom_frames()
        design_for_date(current_date())
        validate_symbols()
        from theme import normalize_theme_mode
        mode=normalize_theme_mode(settings.values.get('ui_theme',settings.values.get('defaultTheme','system')))
        if settings.values.get('ui_theme')!=mode:
            settings.values['ui_theme']=mode;settings.save()
        from theme import configure_appearance
        configure_appearance(settings.values.get('appearance35'), refresh=False)
        apply_theme(mode)
        # Qt 수신자 문맥에 수명을 결합해 종료된 Python 객체로 예약 신호가 전달되지 않게 합니다.
        super().__init__(_application_gui_root())
        self.settings = settings
        from operations37 import NotificationPolicy
        self.workspace_policy = NotificationPolicy(settings)
        self.country_estimated = False
        if settings.values.get('theme_country_mode') == 'auto' and settings.values.get('weather_location'):
            city = normalize_city(settings.values['weather_location'])
            settings.values.update(theme_country_mode='selected',theme_country=validated_theme_country(city['country_code']))
            settings.save()
        from orbit_features import FeatureStore
        self.features = FeatureStore(settings.directory)
        set_language(settings.values.get('language', 'ko'))
        from calendar_motion import set_calendar_motion_speed
        set_calendar_motion_speed(settings.values['motion_speed'])
        self.last_monitor_status = None
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
        self.notice_delivery = NoticeDelivery()
        self.notice_queue = deque()
        self.max_visible_notices = 8
        self.notice_overflow = 0
        self.replacing_notice = False
        self.presentation_error = None
        self.operation_log_error = None
        # 앱이 보관한 부모 아래에 두어 worker GC가 창과 타이머를 파괴하지 못하게 합니다.
        self.gui_owner = QWidget(_application_gui_root())
        self.gui_owner.setObjectName('codexOrbitControllerOwner')
        from city_festival_updates import CityFestivalUpdater
        self.city_updater=CityFestivalUpdater(settings.directory,self.gui_owner)
        self.city_updater.changed.connect(self.city_catalog_changed)
        self.setParent(self.gui_owner)
        self.notice_delivery_timer = QTimer(self.gui_owner)
        self.notice_delivery_timer.setSingleShot(True)
        self.notice_delivery_timer.timeout.connect(self.deliver_next_notice)
        self.monitor_retry_timer = QTimer(self.gui_owner)
        self.monitor_retry_timer.setSingleShot(True)
        self.monitor_retry_timer.timeout.connect(self.restart_dead_monitor)
        self.monitor_health_timer = QTimer(self.gui_owner)
        self.monitor_health_timer.setInterval(1000)
        self.monitor_health_timer.timeout.connect(self.check_monitor_health)
        self.window = Details(self)
        self.orbit = OrbitWidget(settings, self.show, self.request_quit, self.gui_owner)
        self.orbit.language_changed = self.set_language
        self.orbit.motion_speed_changed = self.change_motion_speed
        from observatory_panel import OrbitExperience
        self.orbit29 = OrbitExperience(self)
        self.orbit.experience = self.orbit29
        self.notice = None
        self.screen_connections = []
        for screen in QApplication.screens():
            self.screen_connections.append(screen.availableGeometryChanged.connect(self.layout_notices))
        self.screen_connections.append(QApplication.instance().screenRemoved.connect(self.layout_notices))
        self.usage = UsageClient(settings.values.get('codex_exe', ''), self.gui_owner)
        self.usage.changed.connect(self.update_usage)
        self.update_usage(self.usage.snapshot)
        self.weather = WeatherClient(self.gui_owner, language=get_language(), location_override=settings.values.get('weather_location'),
                                     auto_correction=settings.values.get('weather_auto_correction'))
        self.weather.changed.connect(self.update_weather)
        self._apply_theme_country(settings.values.get('theme_country','KR'), estimated=False)
        self.update_weather(self.weather.snapshot)
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
        if start_weather:
            self.weather.start()
        from operations37 import install_workspace
        install_workspace(self)

    def retry_monitor37(self):
        """사용자 재연결은 기존 작업자의 정상 종료를 기다린 뒤 이어갑니다."""
        try:
            self.monitor_retries = 0
            self.start_monitor()
        except Exception as error:
            QMessageBox.warning(self.window, t('감시 시작 실패'), str(error))

    def dismiss_unpinned37(self):
        for notice in list(self.notices.values()):
            if not notice.pinned:
                notice.dismiss()

    def preview_notice37(self, kind):
        """가상 카드는 감시·기록·실제 알림 표시 로그에 넣지 않습니다."""
        from operations37 import tr
        if kind not in ('model', 'effort', 'activity'):
            raise ValueError('지원하지 않는 미리보기입니다.')
        old = getattr(self, 'preview_card37', None)
        if old is not None and isValid(old):
            old.hide(); old.deleteLater()
        before = {'model': 'gpt-6.1-sol', 'effort': 'medium'}
        after = dict(before)
        if kind == 'model':
            after['model'] = 'gpt-6.1-terra'
        elif kind == 'effort':
            after['effort'] = 'high'
        event = {'id': 'preview37', 'target': 'preview37', 'kind': 'activity' if kind == 'activity' else 'settings',
                 'chat_name': tr('미리보기 · 실제 변경이 아닙니다', 'Preview · Not a real change'),
                 'title': 'Preview', 'before': before, 'after': after, 'time': stamp(),
                 'reason': tr('알림 모양을 확인하는 가상 예시입니다.', 'A sample for checking the notification layout.'),
                 'activity_type': 'resumed', 'task_summary': tr('알림 미리보기', 'Notification preview')}
        card = Notice(lambda *_: None, self.gui_owner)
        card.broadcast_mode = False
        card.apply_text_scale(self.settings.values.get('text_scale', 100) / 100)
        card.display(event, self.orbit, self.workspace_policy.options['notice_duration_seconds'] * 1000)
        card.detail_hint.setText(tr('가상 예시 · 변경 기록에 저장하지 않습니다', 'Sample · Not saved to activity'))
        self.preview_card37 = card

    @Slot(float)
    def change_motion_speed(self, value):
        """사용자 조작의 실패는 실제 속도를 복원한 뒤 상세창에서 안내합니다."""
        try:
            self.set_motion_speed(value)
        except Exception as error:
            self.window.update_motion_speed()
            self.window.show_motion_speed_error(str(error) or type(error).__name__)
            self.window.show()
            self.window.raise_()
            self.window.activateWindow()

    @Slot(float)
    def set_motion_speed(self, value):
        application = QApplication.instance()
        if QThread.currentThread() != application.thread():
            raise RuntimeError(t('회전 속도는 GUI 메인 스레드에서만 변경할 수 있습니다.'))
        value = validated_motion_speed(value)
        previous = self.settings.values['motion_speed']
        from calendar_motion import set_calendar_motion_speed
        try:
            set_calendar_motion_speed(value)
        except Exception:
            self.window.update_motion_speed()
            raise
        self.settings.values['motion_speed'] = value
        try:
            self.settings.save()
        except Exception:
            self.settings.values['motion_speed'] = previous
            # 저장 실패를 숨기지 않고 표시와 실제 모션을 이전 배율로 되돌립니다.
            set_calendar_motion_speed(previous)
            self.window.update_motion_speed()
            raise
        self.window.update_motion_speed()
        self.window.show_motion_speed_error('')

    @Slot(str)
    def set_language(self, language):
        application = QApplication.instance()
        if QThread.currentThread() != application.thread():
            raise RuntimeError('언어는 GUI 메인 스레드에서만 변경할 수 있습니다.')
        language = language if language in ('ko', 'en') else 'ko'
        # 설정 저장 성공 뒤 표시 언어를 변경합니다.
        previous = self.settings.values.get('language', 'ko')
        self.settings.values['language'] = language
        try:
            self.settings.save()
        except Exception:
            self.settings.values['language'] = previous
            raise
        set_language(language)
        self.window.retranslate()
        self.orbit29.panel.refresh()
        self.orbit29.retranslate()
        self.window.history_layout_timer.start(0)
        if hasattr(self,"update_dialog29"):self.update_dialog29.retranslate()
        if self.window.diagnostics.original_text:
            self.window.diagnostics.setPlainText(self.window.diagnostics.original_text)
        self.weather.set_language(language)
        if hasattr(self, 'location_dialog') and isValid(self.location_dialog):
            self.location_dialog.retranslate()
        self.update_weather(self.weather.snapshot)
        self.update_usage(self.usage.snapshot)
        if self.last_monitor_status is not None:
            self.status(self.last_monitor_status)
        for notice in self.notices.values():
            retranslate_widgets(notice)
            notice.update_event(notice.notice_event)
        self.update_notice_count()
        from observatory_panel import mask_details
        mask_details(self.window)
        self.orbit.update()
        from operations37 import refresh_workspace
        refresh_workspace(self, translate=True)

    def show_weather_location(self):
        dialog = getattr(self, 'location_dialog', None)
        if dialog is not None and isValid(dialog) and dialog.isVisible():
            dialog.raise_()
            return
        self.location_dialog = WeatherLocationDialog(self)
        self.orbit29.apply_text_size()
        self.location_dialog.show()

    def set_theme_country(self, country):
        """국가만 고르면 행사 기준만 바꾸며 날씨 좌표는 유지합니다."""
        if self.closing:return
        code = validated_theme_country(country)
        previous = dict(self.settings.values)
        self.settings.values.update(theme_country_mode='selected',theme_country=code)
        try:self.settings.save()
        except Exception:
            self.settings.values.clear();self.settings.values.update(previous)
            raise
        self._apply_theme_country(code, estimated=False)

    def set_weather_location(self, value):
        """선택 지역의 행사 국가와 실제 날씨 좌표를 한 번에 저장합니다."""
        if self.closing:return
        city = normalize_city(value)
        code = validated_theme_country(city['country_code']) if city else None
        previous = dict(self.settings.values)
        self.settings.values['weather_location'] = city
        self.settings.values['theme_country_mode'] = 'selected' if city else 'auto'
        if code:self.settings.values['theme_country'] = code
        try:self.settings.save()
        except Exception:
            self.settings.values.clear();self.settings.values.update(previous)
            raise
        if code:self._apply_theme_country(code,estimated=False)
        else:self.country_estimated=False
        changed = self.weather.set_location_override(city)
        if city is None and changed is False:
            self.weather.refresh()
        self.refresh_region_summary()

    def _apply_theme_country(self, country, estimated=False):
        code = validated_theme_country(country)
        from calendar_motion import set_calendar_country
        set_calendar_country(code)
        self.orbit.theme_country = code
        if (getattr(self.orbit,'city_ref',None) or {}).get('country_code',code)!=code:
            self.orbit.city_ref=None
        self.country_estimated = bool(estimated)
        self._sync_calendar_timezone()
        self.orbit._request_motion_size()
        self.orbit.update()
        self.refresh_region_summary()
        self.window.usage_hero.setAccessibleName(t('선택 지역의 날짜별 조형'))

    def city_catalog_changed(self,revision):
        if self.closing:return
        design_for_date.cache_clear()
        self._sync_calendar_city(self.weather.snapshot,catalog_revision=revision)
        if hasattr(self,'location_dialog') and isValid(self.location_dialog):self.location_dialog.refresh_city_summary()
        self.orbit.update()

    def _sync_calendar_city(self,value,catalog_revision=None):
        from calendar_motion import set_calendar_city_ref
        from calendar_city import normalize_calendar_city
        from city_festivals import city_coverage
        ref=value.get('city_ref')
        if ref is not None and ref.get('country_code')!=self.orbit.theme_country:ref=None
        try:
            ref=normalize_calendar_city(ref)
            if ref is not None:city_coverage(ref,self.orbit.theme_country,regional_calendar_date().year)
        except (ValueError,OSError):ref=None
        self.orbit.city_ref=ref
        if catalog_revision is None:set_calendar_city_ref(ref)
        else:set_calendar_city_ref(ref,catalog_revision=catalog_revision)

    def _sync_calendar_timezone(self, value=None):
        from calendar_motion import set_calendar_utc_offset
        value = self.weather.snapshot if value is None else value
        offset = value.get('utc_offset_seconds')
        matched = value.get('country_code') == self.orbit.theme_country
        valid = type(offset) is int and -43200 <= offset <= 50400
        set_calendar_utc_offset(offset if matched and valid else None)

    def refresh_region_summary(self):
        code = self.orbit.theme_country
        name = next(row['name'] for row in available_countries(get_language()) if row['code']==code)
        mode = t('수동') if self.settings.values.get('theme_country_mode')=='selected' else t('자동')
        self.orbit29.location_label.setText(t('날씨: ')+self.orbit.location_text+'\n'+t('행사: ')+name+' · '+mode)
        status = country_status(code,regional_calendar_date().year)
        warning = t('행사는 국가 단위 자료이며 규칙과 법이 바뀔 수 있습니다.')
        if not status['supported'] or status['warnings']:
            warning += '\n'+t('일부 행사 자료는 지원되지 않거나 확인이 필요합니다.')
        from calendar_motion import get_calendar_utc_offset
        warning += '\n'+(t('날짜·시각: 선택한 지역의 현지 기준') if get_calendar_utc_offset() is not None else t('날짜·시각: 기본 한국 시각 · 도시나 장소를 고르면 현지 기준을 적용합니다.'))
        self.orbit29.location_label.setToolTip(warning)

    @Slot(dict)
    def update_weather(self, value):
        if self.closing:
            return
        temperature = value.get("temperature")
        self.orbit.location_text = value.get("region") or t("위치 정보 없음")
        if self.settings.values.get('theme_country_mode') == 'auto' and value.get('location_mode') == 'automatic' and value.get('country_code'):
            code=value['country_code']
            if any(row['code']==code for row in available_countries()):self._apply_theme_country(code, estimated=True)
            else:self.country_estimated=False
        self._sync_calendar_timezone(value)
        self._sync_calendar_city(value)
        self.refresh_region_summary()
        self.orbit.weather_text, self.orbit.weather_extras = weather_widget_text(value)
        if value.get('busy') and temperature is None:self.orbit.weather_text = t('기온 조회 중')
        checked = value.get("checked_at")
        checked_label = datetime.fromtimestamp(checked).astimezone().strftime("%Y-%m-%d %H:%M:%S") if checked is not None else t("미확인")
        observed = value.get("observed_at")
        observed_label = datetime.fromtimestamp(observed).astimezone().strftime("%Y-%m-%d %H:%M:%S") if observed is not None else t("미확인")
        location_heading = t('지역: ')
        location_source = t('지정한 도시 좌표') if value.get('location_mode') == 'manual' else 'ipwho.is'
        self.orbit.weather_tooltip = (location_heading + (value.get("region") or t("미확인")) +
                                     t("\n지역 원문: ") + (value.get("region_original") or t("미확인")) +
                                     t('\n기온 출처: Open-Meteo · 위치: ') + location_source +
                                     t("\n제공 시각: ") + observed_label +
                                     t("\n조회 시각: ") + checked_label + "\n" + t(value.get("status", "기온 미확인")))
        self.orbit.weather_tooltip += t("\n지명 출처: ") + t(str(value.get("region_source") or "GeoNames / Open-Meteo (CC BY 4.0)"))
        self.orbit.weather_tooltip += '\n'+self.orbit.weather_text+'\n'+'\n'.join(self.orbit.weather_extras)
        self.orbit.weather_tooltip += '\n'+t('기온·강수량은 소수 둘째 자리 아래 버림 · 백분율은 소수 첫째 자리 반올림 · 원값: ')+json.dumps(
            {key:value.get(key) for key in ('temperature','humidity','precipitation','precipitation_interval_seconds')},ensure_ascii=False)
        self.orbit.weather_tooltip += '\n'+percentage_tooltip(value.get('humidity'))
        self.orbit._request_motion_size()
        self.orbit.refresh_tooltip()
        self.orbit.update()

    def restart_usage(self):
        self.usage.close()
        self.usage.deleteLater()
        self.usage = UsageClient(self.settings.values.get('codex_exe', ''), self.gui_owner)
        self.usage.changed.connect(self.update_usage)
        self.update_usage(self.usage.snapshot)
        self.usage.start()

    @Slot(dict)
    def update_usage(self, value):
        if self.closing:
            return
        self.window.display_usage(value)
        if hasattr(self,'orbit29'):self.orbit29.apply_text_size()
        valid = [row for row in value.get('rows', []) if row.get('remaining') is not None]
        self.orbit.usage_fraction = min(row['remaining'] for row in valid) / 100 if valid else None
        self.orbit.usage_state = 'stale' if value.get('stale') and value.get('checked_at') else 'fresh' if valid and not value.get('stale') else 'unknown'
        if value.get('stale'):
            self.orbit.usage_badge = '?' if value.get('checked_at') else '—'
        elif valid:
            self.orbit.usage_badge = percentage_text(min(row['remaining'] for row in valid))
        else:
            self.orbit.usage_badge = '—'
        self.orbit.usage_tooltip = (t('Codex Orbit · 계정 한도 ') + self.orbit.usage_badge +
                                    ' · ' + t(value.get('status', '미확인')) + t('\n클릭: 기간별 잔량과 변경 이력 · 드래그: 이동'))
        if valid:self.orbit.usage_tooltip+='\n'+percentage_tooltip(min(row['remaining'] for row in valid))
        self.orbit.refresh_tooltip()
        self.orbit.update()
        self.orbit29.feed_scene()

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
            self.window.summary.setText(t('감시 재시작 대기 · 이전 작업자 종료 후 최종 설정으로 자동 시작합니다.'))
            return False
        self.monitor_restart_pending = False
        self.monitor_retry_timer.stop()
        if not self.stop_monitor():
            self.orbit.healthy = False
            self.window.summary.setText(t('감시 지연 · 이전 작업자가 종료 중입니다. 종료 후 다시 시작하세요.'))
            return False
        self.monitor_enabled = True
        self.orbit.healthy = False
        self.window.summary.setText(t('감시 준비 중 · 첫 진행 확인 대기'))
        self.last_monitor_progress = time.monotonic()
        self.operation_log_error = operation_record(self.settings.directory, 'monitor-preparation', self.settings.values['sessions'])
        try:
            self.monitor = Monitor(self.settings.values['sessions'], self.settings.directory)
            self.monitor.delivery_gate = self.notice_delivery
            self.monitor.event.connect(self.queue_receive)
            self.monitor.event[object, dict].connect(self.queue_delivery)
            self.monitor.status.connect(self.status)
            self.monitor.enriched.connect(self.refresh_history)
            self.monitor.lifecycle_event.connect(self.receive_lifecycle)
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

    @Slot()
    def check_monitor_health(self):
        if self.closing or not self.monitor_enabled or self.monitor is None:
            return
        if not self.monitor.isRunning():
            if self.monitor_restart_pending:
                self.monitor_restart_pending = False
                try:
                    self.start_monitor()
                except Exception as error:
                    self.window.summary.setText(t('감시 시작 실패 · 변경 기록의 진단을 확인하세요.'))
                    self.window.diagnostics.setPlainText(str(error))
                return
            self.orbit.healthy = False
            self.window.summary.setText(t('감시 중단 · ') + (t('자동 재시도 대기') if self.monitor_retries < 3 else t('앱 다시 실행 필요')))
            if self.monitor_retries < 3 and not self.monitor_retry_timer.isActive():
                self.monitor_retry_timer.start(3000 * (self.monitor_retries + 1))
        elif time.monotonic() - self.last_monitor_progress > 20:
            self.orbit.healthy = False
            self.window.summary.setText(t('감시 지연 · 20초 이상 진행 확인 없음. 작업자는 실행 중이며 강제 재시작하지 않습니다.'))
        self.orbit.update()

    @Slot()
    def restart_dead_monitor(self):
        if self.closing or not self.monitor_enabled or self.monitor_retries >= 3:
            return
        if self.monitor is not None and self.monitor.isRunning():
            return
        self.monitor_retries += 1
        self.start_monitor()

    @Slot(dict)
    def queue_receive(self, event):
        if not self.closing:
            self.queue_delivery(self.notice_delivery.acquire(), event)

    @Slot(object, dict)
    def queue_delivery(self, ticket, event):
        if self.closing:
            ticket.release()
            return
        self.notice_queue.append((ticket, event))
        if not self.notice_delivery_timer.isActive():
            self.notice_delivery_timer.start(0)

    @Slot()
    def deliver_next_notice(self):
        if self.closing or not self.notice_queue:
            return
        ticket, event = self.notice_queue.popleft()
        try:
            self.receive(event)
        finally:
            ticket.release()
            if self.notice_queue and not self.closing:
                self.notice_delivery_timer.start(0)

    def close_notice_delivery(self):
        self.notice_delivery_timer.stop()
        self.notice_queue.clear()
        self.notice_delivery.close()

    @Slot(dict)
    def receive_lifecycle(self, event):
        if not self.closing:
            self.orbit29.ingest(event)

    @Slot(dict)
    def receive(self, event):
        if self.closing:
            return
        self.orbit29.ingest(event)
        if (event.get('kind') == 'activity' and event.get('first_observation_already_delivered') is True
                and isinstance(event.get('first_observation_id'), str)):
            promoted = self.window.promote_first_observation(event)
            if promoted is not False:
                if promoted is None:
                    self.window.add_event(event)
                prior_id = event['first_observation_id']
                notice = self.notices.get(prior_id)
                if (notice is not None and notice.notice_event.get('target') == event.get('target')
                        and notice.notice_event.get('before') is None and notice.notice_event.get('kind') != 'activity'):
                    self.notices.pop(prior_id)
                    self.notices[event.get('id')] = notice
                    # 만료 시간·최초 표시 기록·애니메이션을 재시작하지 않고 정확한 ID만 보강합니다.
                    notice.update_event(event)
                self.update_notice_count()
                return
        self.window.add_event(event)
        if self.settings.values.get('broadcast_mode'):
            from observatory_panel import mask_details
            mask_details(self.window)
        self.orbit.unread = True
        if self.settings.values.get('popup', True) and self.workspace_policy.allows(event):
            self.enqueue_notice(event)

    def update_notice_count(self):
        text = t('알림 표시 {count}건 · 새 변경은 즉시 표시', count=len(self.notices))
        if self.notice_overflow:
            text += t(' · 표시 상한으로 숨긴 {count}건은 변경 이력에서 확인하세요.', count=self.notice_overflow)
        self.window.notice_summary.setText(text)
        for notice in self.notices.values():
            notice.queue_hint.setText(text)
        self.layout_notices()

    @Slot()
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
            x = max(rect.left(), min(self.orbit.x() - card.width(), rect.right() + 1 - card.width()))
            if overlap:
                # 기준 위치를 먼저 화면 안으로 제한한 뒤 반대 방향으로 어긋나게 배치합니다.
                offset = min(index * 18, max(0, rect.width() - card.width()))
                x = x - offset if x - offset >= rect.left() else x + offset
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
        unpinned = [n for n in self.notices.values() if not getattr(n,'pinned',False)]
        if len(unpinned) >= self.max_visible_notices:
            oldest = unpinned[0]
            # 교체 도중의 중간 정렬은 새 카드가 들어간 뒤 최종 정렬 한 번으로 합칩니다.
            self.replacing_notice = True
            try:
                oldest.dismiss()
            finally:
                self.replacing_notice = False
            self.notice_overflow += 1
        self.display_notice(event, replay=replay)
        self.update_notice_count()

    def display_notice(self, event, replay=False):
        self.notice = Notice(self.show, self.gui_owner)
        self.notices[event.get('id')] = self.notice
        self.notice.broadcast_mode = bool(self.settings.values.get('broadcast_mode', False))
        self.notice.apply_text_scale(self.settings.values.get('text_scale',100)/100)
        self.notice.bookmark_callback = lambda key: self.features.set_bookmark(key, key not in self.features.bookmarks)
        self.notice.completed.connect(self.remove_notice)
        self.notice.display(event, self.orbit, self.workspace_policy.options['notice_duration_seconds'] * 1000, replay=replay)
        if event.get('kind') == 'activity' and self.workspace_policy.options['compact_activity']:
            self.notice.layout().setContentsMargins(14, 10, 14, 10)
            self.notice.layout().setSpacing(3)
            self.notice.fit_content()
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

    @Slot(str)
    def remove_notice(self, event_id):
        notice = self.notices.pop(event_id, None)
        if notice is not None:
            notice.deleteLater()
        if not self.replacing_notice:
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

    @Slot(list)
    def refresh_history(self, events):
        if self.closing:
            return
        self.features.load_history(events)
        self.orbit29.panel.refresh()
        self.orbit29.feed_scene()
        items = self.window._history_items_by_id()
        notice_changed = False
        for event in events:
            self.window.update_event(event, items)
            notice = self.notices.get(event.get('id'))
            if notice is not None and notice.notice_event != event:
                notice.update_event(event)
                notice_changed = True
        if self.settings.values.get('broadcast_mode'):
            from observatory_panel import mask_details
            mask_details(self.window)
        if notice_changed:
            self.layout_notices()

    @Slot(dict)
    def status(self, value):
        if self.closing:
            return
        if self.monitor_restart_pending:
            return
        self.last_monitor_progress = time.monotonic()
        if self.presentation_error or self.operation_log_error:
            value = {**value, 'notice_presentation_error': self.presentation_error,
                     'operation_log_error': self.operation_log_error}
        self.last_monitor_status = dict(value)
        self.orbit.healthy = value.get('state') == '감시 중'
        self.orbit29.health(value)
        from operations37 import refresh_workspace
        refresh_workspace(self)
        self.window.summary.setText('● ' + t(value.get('state', '')) + '  ·  ' + kst_label(value.get('time')))
        self.window.diagnostics.setPlainText(json.dumps(value, ensure_ascii=False, indent=2))
        if self.settings.values.get('broadcast_mode'):self.window.diagnostics.hide()

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
                self.window.add_event(self.notices[event_id].notice_event)
        self.orbit29.open_page(0)
        self.orbit29.panel.refresh()
        self.features.mark_seen()
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        self.orbit.unread = False

    def request_quit(self):
        if self.quit_requested or self.cleaned:
            return
        self.quit_requested = True
        self.closing = True
        self.close_notice_delivery()
        self.monitor_restart_pending = False
        self.monitor_enabled = False
        self.monitor_health_timer.stop()
        self.monitor_retry_timer.stop()
        self.usage.close()
        self.weather.close()
        self.city_updater.close()
        if hasattr(self, 'location_dialog') and isValid(self.location_dialog):
            self.location_dialog.reject()
        for notice in list(self.notices.values()):
            notice.dismiss()
        self.orbit.healthy = False
        self.window.summary.setText(t('종료 중 · 감시 작업자의 안전한 종료를 기다리고 있습니다.'))
        if self.monitor is not None and self.monitor.isRunning():
            self.monitor.finished.connect(self.finish_quit)
            self.monitor.requestInterruption()
            # 신호 연결 직전에 종료된 경우도 대기 상태로 남지 않도록 다시 확인합니다.
            if self.monitor.isRunning():
                return
        self.finish_quit()

    @Slot()
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
        if hasattr(self,"orbit29"):self.orbit29.timer.stop()
        self.close_notice_delivery()
        self.monitor_restart_pending = False
        self.monitor_enabled = False
        self.monitor_health_timer.stop()
        self.monitor_retry_timer.stop()
        self.usage.close()
        self.weather.close()
        self.city_updater.close()
        if hasattr(self, 'location_dialog') and isValid(self.location_dialog):
            self.location_dialog.reject()
        worker = self.monitor
        self.stop_monitor()
        for notice in list(self.notices.values()):
            notice.close()
        self.notices.clear()
        self.orbit.close()
        self.window.close()
        QApplication.instance().removeEventFilter(self.quit_guard)
        self.quit_guard.deleteLater()
        for connection in self.screen_connections:
            QObject.disconnect(connection)
        self.screen_connections.clear()
        if worker is not None and worker.isRunning():
            # 실행 중 QThread를 자식으로 묶지 않고 종료 신호 뒤 GUI에서 정리합니다.
            worker.finished.connect(self._finish_closed_gui, Qt.ConnectionType.QueuedConnection)
            if not worker.isRunning():
                self._finish_closed_gui()
        else:
            self._finish_closed_gui()

    @Slot()
    def _finish_closed_gui(self):
        """외부 QThread 참조를 무효화하지 않고 종료된 감시기와 GUI 소유자를 해제합니다."""
        if self.monitor is not None and self.monitor.isRunning():
            return
        self.monitor = None
        self.gui_owner.deleteLater()


def usage_smoke_state(controller):
    """지연된 신호 인자 대신 최신 스냅샷과 현재 레이아웃의 실제 표시를 대조합니다."""
    value = controller.usage.snapshot
    rows = value.get('rows', [])
    valid = [row for row in rows if row.get('remaining') is not None]
    expected = min((row['remaining'] for row in valid), default=None)
    layout = controller.window.usage_rows_layout
    widgets = [layout.itemAt(i).widget() for i in range(layout.count())]
    bars = [widget for widget in widgets if isinstance(widget, QProgressBar)]
    labels = [widget.text() for widget in widgets if isinstance(widget, QLabel) and widget.isVisible()]
    expected_values = [round(row['remaining'] * 10000) if row.get('remaining') is not None else 0 for row in rows]
    expected_labels = [remaining_text(row['remaining']) for row in rows]
    presented = {'badge': controller.orbit.usage_badge, 'fraction': controller.orbit.usage_fraction,
                 'state': controller.orbit.usage_state, 'bar_values': [bar.value() for bar in bars],
                 'remaining_labels': [label for label in labels if label in expected_labels]}
    fresh = not value.get('stale', True) and not value.get('busy', False) and value.get('checked_at') is not None
    matches = (expected is not None and presented['badge'] == percentage_text(expected)
               and presented['fraction'] == expected / 100 and presented['state'] == 'fresh'
               and presented['bar_values'] == expected_values
               and presented['remaining_labels'] == expected_labels
               and all(bar.isVisible() and bar.maximum() == 1000000 for bar in bars))
    return value, presented, bool(fresh and matches)


def motion_smoke_stage(status, baseline_count, expired):
    """실제 GPU 렌더 수를 기준으로 준비·비교 단계를 판정합니다."""
    if status.get('error'):
        return 'error'
    if expired:
        return 'timeout'
    if not status.get('running') or not status.get('renderer'):
        return 'wait'
    count = status.get('render_count', 0)
    if baseline_count is None:
        return 'baseline' if count >= 2 else 'wait'
    return 'compare' if count >= baseline_count + 2 else 'wait'


def main():
    from safe_update import handle_update_cli
    result = None if '--ui-smoke-test' in sys.argv[1:] else handle_update_cli(sys.argv[1:])
    if result is not None:return result
    parser = argparse.ArgumentParser(description='Codex Orbit · 로컬 모델 변경 투명 궤도')
    parser.add_argument('--data-dir', type=Path, default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit')
    parser.add_argument('--sessions', type=Path)
    parser.add_argument('--ui-smoke-test', action='store_true', help='새 격리 폴더에서 합성 화면 조작 검사 후 종료')
    parser.add_argument('--smoke-test', action='store_true')
    parser.add_argument('--workspace-smoke-test', action='store_true', help='새 알림 센터의 격리된 합성 화면 연결 검사')
    parser.add_argument('--usage-smoke-test', action='store_true', help='실제 계정 잔량과 표시를 조회한 뒤 종료')
    parser.add_argument('--smoke-report', type=Path)
    parser.add_argument('--show-details', action='store_true')
    parser.add_argument('--show-event', help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시')
    args = parser.parse_args()
    if args.workspace_smoke_test:
        if '--data-dir' not in sys.argv[1:] or (args.data_dir.exists() and any(args.data_dir.iterdir())):
            parser.error('새 알림 센터 검사는 명시한 빈 격리 데이터 폴더가 필요합니다.')
        args.smoke_test = True
    if args.ui_smoke_test:
        from ui_smoke32 import run_ui_smoke
        return run_ui_smoke(args, sys.argv[1:])
    args.data_dir = args.data_dir.absolute()
    app = QApplication(sys.argv[:1])
    app.setApplicationName('Codex Orbit')
    apply_theme()
    app.setWindowIcon(QIcon(str(asset('Orbit.ico'))))
    app.setQuitOnLastWindowClosed(False)
    effective_sessions = args.sessions or (Path(os.environ.get('CODEX_HOME') or (Path.home() / '.codex')) / 'sessions')
    stage = 'settings-load'
    log_error = operation_record(args.data_dir, stage, effective_sessions)
    try:
        stage = 'font-load'
        app.setFont(app_font())
        families = [app.font().family()]
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
        design_for_date(current_date())
        validate_symbols()
        stage = 'calendar-motion-prepare'
        from calendar_motion import prepare_calendar_motion
        preparation = prepare_calendar_motion()
        log_error = operation_record(args.data_dir, stage, effective_sessions,
                                     ready=preparation['ready'], error=preparation['error'] or None,
                                     renderer=preparation['renderer']) or log_error
        stage = 'controller-prepare'
        log_error = operation_record(args.data_dir, stage, effective_sessions, lock_acquired=True) or log_error
        controller = Controller(settings, start_worker=not (args.smoke_test or args.usage_smoke_test),
                                start_weather=not (args.smoke_test or args.usage_smoke_test))
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
    from calendar_motion import close_calendar_motion
    app.aboutToQuit.connect(close_calendar_motion)
    if args.show_details:
        controller.show()
    if args.usage_smoke_test and not args.smoke_test:
        controller.show()
        controller.window.tabs.setCurrentIndex(1)
        usage_finished = False
        def finish_usage(timed_out=False):
            nonlocal usage_finished
            if usage_finished:
                return
            value, presented, ok = usage_smoke_state(controller)
            if not ok and not timed_out:
                return
            usage_finished = True
            report = {**value, 'ok': ok, 'frozen': bool(getattr(sys, 'frozen', False)),
                      'language': get_language(),
                      'detail_tabs': [controller.window.tabs.tabText(index) for index in range(controller.window.tabs.count())],
                      'widget_badge': controller.orbit.usage_badge,
                      'widget_fraction': controller.orbit.usage_fraction,
                      'widget_state': controller.orbit.usage_state,
                      'bar_fill_width': usage_bar(controller.orbit.usage_badge,controller.orbit.usage_fraction,controller.orbit.usage_state)[0].width(),
                      'display_text': controller.window.usage_values.text(),
                      'display_status': controller.window.usage_status.text(),
                      'latest': {'checked_at': value.get('checked_at'), 'stale': value.get('stale'),
                                 'remaining': [row.get('remaining') for row in value.get('rows', [])]},
                      'presented': presented,
                      'error': '' if ok else '최신 계정 한도와 현재 화면 표시가 일치하지 않습니다.',
                      'time': stamp()}
            if args.smoke_report:
                controller.orbit.grab().save(str(args.smoke_report.with_suffix('.orbit.png')))
                controller.window.grab().save(str(args.smoke_report.with_suffix('.details.png')))
                args.smoke_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
            app.exit(0 if ok else 1)
        controller.usage.changed.connect(lambda _value: QTimer.singleShot(100, finish_usage))
        QTimer.singleShot(18000, lambda: finish_usage(timed_out=True))
        controller.usage.start()
    if args.show_event and not controller.replay_event(args.show_event):
        controller.window.summary.setText('지정한 이력을 찾지 못했습니다. 감시가 기록을 읽은 뒤 이력에서 확인하세요.')
    if args.smoke_test:
        from calendar_motion import calendar_motion_status
        first = None
        baseline_count = None
        # 실제 첫 프레임과 프레임 변화를 요구하되 초기화와 프레임 교환의 서로 다른 총기한을 따릅니다.
        from calendar_gpu_process import INITIALIZE_TIMEOUT_SECONDS, FRAME_TIMEOUT_SECONDS
        deadline = time.monotonic() + 2 * INITIALIZE_TIMEOUT_SECONDS + 2 * FRAME_TIMEOUT_SECONDS
        smoke_timer = QTimer()
        smoke_timer.setInterval(33)
        def finish():
            nonlocal first, baseline_count
            status = calendar_motion_status()
            stage = motion_smoke_stage(status, baseline_count, time.monotonic() >= deadline)
            if stage == 'wait':
                return
            if stage == 'baseline':
                first = controller.orbit.grab().toImage()
                baseline_count = status['render_count']
                if args.smoke_report:
                    first.save(str(args.smoke_report.with_suffix('.frame1.png')))
                return
            smoke_timer.stop()
            second = controller.orbit.grab().toImage()
            changed = first is not None and hashlib.sha256(bytes(first.constBits())).digest() != hashlib.sha256(bytes(second.constBits())).digest()
            alpha = first.pixelColor(0, 0).alpha() if first is not None else None
            error = status.get('error') or ('GPU 프레임 준비가 5초 제한을 넘었습니다.' if stage == 'timeout' else '')
            if args.smoke_report:
                second.save(str(args.smoke_report.with_suffix('.frame2.png')))
            report = {'ok': bool(stage == 'compare' and changed and alpha == 0 and second.pixelColor(0, 0).alpha() == 0 and families),
                      'frame_changed': changed, 'corner_alpha': alpha,
                      'gpu': status, 'baseline_render_count': baseline_count, 'error': error,
                      'translucent': controller.orbit.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground),
                      'always_on_top': bool(controller.orbit.windowFlags() & Qt.WindowType.WindowStaysOnTopHint),
                      'font_families': families, 'time': stamp(), 'frozen': bool(getattr(sys, 'frozen', False)),
                      'language': get_language(),
                      'detail_tabs': [controller.window.tabs.tabText(index) for index in range(controller.window.tabs.count())]}
            if args.workspace_smoke_test:
                try:
                    from ui_workspace_smoke37 import check_workspace
                    report['workspace37'] = check_workspace(controller, args.smoke_report.parent)
                except Exception as error:
                    report['ok'] = False
                    report['workspace_error'] = str(error)
            if args.smoke_report:
                args.smoke_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
            if sys.stdout:
                print(json.dumps(report, ensure_ascii=False))
            app.exit(0 if report['ok'] else 1)
        smoke_timer.timeout.connect(finish)
        smoke_timer.start()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
