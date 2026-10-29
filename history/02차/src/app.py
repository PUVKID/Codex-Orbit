"""Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

from PySide6.QtCore import QLockFile, QPoint, QPointF, QRectF, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPainter, QPen
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QFileDialog,
                             QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMenu, QMessageBox,
                             QPlainTextEdit, QPushButton, QSplitter, QTabWidget,
                             QSizePolicy, QVBoxLayout, QWidget)

from core import InstructionStore, clamp_position, read_jsonl_tail, read_text_strict, session_titles
from notifier import Watcher, append_log, atomic_json, stamp


def asset(name):
    root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
    return root / 'assets' / name


def model_label(value):
    if value is None:
        return '미배정'
    return f"{value.get('model', '확인 불가')} / {value.get('effort', '확인 불가')}"


def event_description(event):
    return '\n'.join([
        '채팅: ' + str(event.get('chat_name') or event.get('target', '확인 불가')),
        '채팅 ID: ' + str(event.get('target', '확인 불가')),
        '구분: ' + ('자식 작업' if event.get('parent') else 'main 또는 부모 정보 미기록'),
        '역할: ' + str(event.get('role', '확인 불가')),
        '부모 ID: ' + str(event.get('parent') or '기록 없음'),
        '작업 경로: ' + str(event.get('agent_path') or '기록 없음'),
        '변경 전: ' + model_label(event.get('before')),
        '변경 후: ' + model_label(event.get('after')),
        '감지 시각: ' + str(event.get('time', '확인 불가')),
        '기록 종류: ' + str(event.get('kind', '확인 불가')),
        '', '공개 이유', str(event.get('reason') or '확인 불가'),
        '', '근거 수준', str(event.get('evidence') or '확인 불가'),
        '', '표시 기록', str(event.get('delivery') or '앱 표시 요청; 사용자 수신 미확인'),
        '', '로컬 기록과 공개 이유의 연결 근거입니다. 서버 모델 신원이나 비공개 추론을 증명하지 않습니다.'
    ])


class Settings:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / 'settings.json'
        home = Path(os.environ.get('CODEX_HOME') or (Path.home() / '.codex'))
        self.values = {'sessions': str(home / 'sessions'), 'theme': '자동', 'popup': True}
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

    def __init__(self, sessions, directory):
        super().__init__()
        self.sessions = Path(sessions)
        key = hashlib.sha256(str(self.sessions.absolute()).encode('utf-8')).hexdigest()[:16]
        self.work = Path(directory) / 'watches' / key
        self.titles = {}

    def send(self, event):
        value = {**event, 'chat_name': self.titles.get(event.get('target'), event.get('target')),
                 'delivery': '앱 표시 요청; 사용자 수신 미확인'}
        self.event.emit(value)
        return value['delivery']

    def run(self):
        try:
            watcher = Watcher(self.sessions, self.work, self.send)
            while not self.isInterruptionRequested():
                try:
                    if not self.sessions.is_dir():
                        raise FileNotFoundError('세션 폴더가 없거나 접근할 수 없습니다: ' + str(self.sessions))
                    self.titles = session_titles(self.sessions.parent / 'session_index.jsonl')
                    watcher.poll()
                    diagnostics, problems = read_jsonl_tail(self.work / 'diagnostics.jsonl', max_records=5)
                    status = {'time': stamp(), 'state': '감시 중', 'sessions': str(self.sessions),
                              'files': len(watcher.state['files']), 'pending': len(watcher.state['pending']),
                              'diagnostics': diagnostics, 'read_problems': problems}
                    self.status.emit(status)
                    atomic_json(self.work / 'heartbeat.json', status)
                except Exception as error:
                    watcher.diagnostic(error)
                    self.status.emit({'time': stamp(), 'state': '오류 · 다음 주기 재시도', 'error': str(error), 'sessions': str(self.sessions)})
                for _ in range(20):
                    if self.isInterruptionRequested():
                        break
                    self.msleep(100)
        except Exception as error:
            self.status.emit({'time': stamp(), 'state': '감시 중단 · 상태 점검 필요', 'error': str(error), 'sessions': str(self.sessions)})


class OrbitWidget(QWidget):
    def __init__(self, settings, details, preferences, quit_app):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle('Codex Orbit')
        self.setFixedSize(148, 148)
        self.settings, self.details = settings, details
        self.preferences, self.quit_app = preferences, quit_app
        self.origin_time = time.monotonic()
        self.render_time = None
        self.healthy = True
        self.unread = False
        self.press_global = None
        self.dragged = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setToolTip('Codex Orbit · 클릭: 상세 · 드래그: 이동 · 우클릭: 설정/종료')
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
        colors = ['#49E6E0', '#9B8BFF', '#FFCA72']
        theme = self.settings.values.get('theme', '자동')
        outline = QColor('#FFFFFF' if theme == '밝은 배경' else '#0B1425')
        for index, speed in enumerate([23, -31, 41]):
            painter.save()
            painter.rotate(elapsed * speed + index * 60)
            # 세 궤도의 납작한 정도도 천천히 달라져 실제 프레임이 계속 변합니다.
            height = 22 + math.sin(elapsed * 0.7 + index) * 5
            ellipse = QRectF(-56, -height, 112, height * 2)
            painter.setPen(QPen(outline, 7.5))
            painter.drawEllipse(ellipse)
            painter.setPen(QPen(QColor(colors[index]), 4.4))
            painter.drawEllipse(ellipse)
            angle = elapsed * (0.9 + index * 0.2) + index * 2.1
            painter.setPen(QPen(outline, 2))
            painter.setBrush(QColor(colors[index]))
            painter.drawEllipse(QPointF(56 * math.cos(angle), height * math.sin(angle)), 4.5, 4.5)
            painter.restore()
        painter.setPen(QPen(QColor('#ECF7FF'), 2))
        painter.setBrush(QColor('#111B2E'))
        painter.drawEllipse(QPointF(0, 0), 15, 15)
        painter.setFont(QFont('NanumGothic', 15, QFont.Weight.Bold))
        painter.drawText(QRectF(-16, -17, 32, 32), Qt.AlignmentFlag.AlignCenter, 'C')
        painter.setPen(QPen(QColor('#101827'), 1.5))
        painter.setBrush(QColor('#FFB85C' if not self.healthy else ('#FF7095' if self.unread else '#52E5B7')))
        painter.drawEllipse(QPointF(14, 14), 5, 5)

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
        menu = QMenu(self)
        menu.addAction('상세 이력 열기', self.details)
        menu.addAction('설정 · 지침 관리', self.preferences)
        menu.addSeparator()
        menu.addAction('종료', self.quit_app)
        menu.exec(event.globalPos())


class Notice(QFrame):
    def __init__(self, open_details):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.open_details = open_details
        self.setObjectName('notice')
        self.setStyleSheet('#notice {background:#142137;border:1px solid #58DAD7;border-radius:14px;} QLabel {color:#F2F7FF;background:transparent;border:none;}')
        self.setFixedWidth(380)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        self.title = QLabel('모델 · 추론 강도 변경')
        self.text = QLabel()
        self.title.setTextFormat(Qt.TextFormat.PlainText)
        self.text.setTextFormat(Qt.TextFormat.PlainText)
        self.text.setWordWrap(True)
        layout.addWidget(self.title)
        layout.addWidget(self.text)
        hint = QLabel('클릭하여 전체 이유와 근거 보기')
        layout.addWidget(hint)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def display(self, event, orbit):
        name = str(event.get('chat_name') or event.get('target'))
        self.title.setText('모델 · 추론 강도 변경')
        self.text.setText(name[:70] + '\n' + model_label(event.get('before'))[:90] + '\n→ ' + model_label(event.get('after'))[:90])
        self.adjustSize()
        screen = QApplication.screenAt(orbit.pos()) or QApplication.primaryScreen()
        rect = screen.availableGeometry()
        self.move(max(rect.left(), min(orbit.x() - self.width(), rect.right() - self.width())),
                  max(rect.top(), min(orbit.y(), rect.bottom() - self.height())))
        self.show()
        self.timer.start(10000)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.hide()
            self.open_details()


class Details(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.store = InstructionStore(controller.settings.directory)
        self.plan = None
        self.setWindowTitle('Codex Orbit · 로컬 모델 변경 기록')
        self.resize(950, 700)
        self.setMinimumSize(740, 540)
        layout = QVBoxLayout(self)
        heading = QLabel('Codex Orbit')
        heading.setStyleSheet('font-size:24px;color:#57DBD7;')
        layout.addWidget(heading)
        layout.addWidget(QLabel('로컬 관측 · 공개된 배정 이유 · 내 지침'))
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.build_history()
        self.build_settings()
        self.build_instructions()
        help_text = QPlainTextEdit()
        help_text.setReadOnly(True)
        help_text.setPlainText(read_text_strict(asset('사용법.md')))
        self.tabs.addTab(help_text, '사용 설명')
        self.setStyleSheet('QDialog,QWidget {background:#101A2B;color:#EDF3FF;} QLineEdit,QPlainTextEdit,QListWidget,QComboBox {background:#18263C;border:1px solid #354762;border-radius:5px;padding:7px;} QPushButton {background:#253B56;border:1px solid #3D617D;border-radius:5px;padding:8px 12px;} QPushButton:hover {background:#345978;} QPushButton:disabled {color:#718198;} QTabBar::tab {padding:10px;background:#19283C;} QTabBar::tab:selected {background:#2C4560;} QSplitter::handle {background:#354762;}')

    def build_history(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.summary = QLabel('감시 준비 중')
        self.summary.setTextFormat(Qt.TextFormat.PlainText)
        self.summary.setWordWrap(True)
        self.summary.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        layout.addWidget(self.summary)
        split = QSplitter()
        self.history = QListWidget()
        self.history.currentItemChanged.connect(self.select_event)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        self.detail.setPlainText('변경을 감지하면 이곳에서 전후 값과 공개 이유를 확인할 수 있습니다.\n첫 실행은 과거 기록을 기준선으로 읽으며 과거 알림을 만들지 않습니다.')
        split.addWidget(self.history)
        split.addWidget(self.detail)
        split.setSizes([280, 600])
        layout.addWidget(split, 1)
        self.tabs.addTab(page, '변경 이력')

    def select_event(self, current, _previous):
        if current:
            self.detail.setPlainText(event_description(current.data(Qt.ItemDataRole.UserRole)))

    def add_event(self, event):
        item = QListWidgetItem(str(event.get('chat_name') or event.get('target'))[:100] + '\n' + model_label(event.get('after'))[:100])
        item.setData(Qt.ItemDataRole.UserRole, event)
        self.history.insertItem(0, item)
        while self.history.count() > 500:
            self.history.takeItem(self.history.count() - 1)
        self.history.setCurrentItem(item)

    def build_settings(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        form = QFormLayout()
        self.sessions = QLineEdit(self.controller.settings.values['sessions'])
        row = QHBoxLayout()
        row.addWidget(self.sessions)
        pick = QPushButton('폴더 선택')
        pick.clicked.connect(self.choose_sessions)
        row.addWidget(pick)
        form.addRow('Codex sessions 폴더', row)
        self.theme = QComboBox()
        self.theme.addItems(['자동', '어두운 배경', '밝은 배경'])
        self.theme.setCurrentText(self.controller.settings.values.get('theme', '자동'))
        form.addRow('궤도 대비', self.theme)
        self.popup = QCheckBox('변경 시 클릭 가능한 말풍선 표시')
        self.popup.setChecked(self.controller.settings.values.get('popup', True))
        form.addRow('', self.popup)
        layout.addLayout(form)
        save = QPushButton('설정 저장 · 감시 다시 시작')
        save.clicked.connect(self.save_settings)
        layout.addWidget(save)
        self.diagnostics = QPlainTextEdit()
        self.diagnostics.setReadOnly(True)
        layout.addWidget(QLabel('감시 상태와 최근 진단 · 오류는 숨기지 않습니다'))
        layout.addWidget(self.diagnostics)
        self.tabs.addTab(page, '설정 · 진단')

    def choose_sessions(self):
        path = QFileDialog.getExistingDirectory(self, 'Codex sessions 폴더 선택', self.sessions.text())
        if path:
            self.sessions.setText(path)

    def save_settings(self):
        try:
            path = Path(self.sessions.text()).absolute()
            if not path.is_dir():
                raise ValueError('존재하는 sessions 폴더를 선택하세요.')
            values = self.controller.settings.values
            values.update(sessions=str(path), theme=self.theme.currentText(), popup=self.popup.isChecked())
            self.controller.settings.save()
            self.controller.start_monitor()
            QMessageBox.information(self, '설정 저장', '앱 설정을 저장하고 감시를 시작했습니다.')
        except Exception as error:
            self.error(error)

    def build_instructions(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        intro = QLabel('UTF-8 Markdown을 편집한 뒤 대상을 선택하고 미리보기를 확인하세요. 적용 버튼을 눌러야 파일이 바뀝니다.')
        intro.setWordWrap(True)
        layout.addWidget(intro)
        buttons = QHBoxLayout()
        for name, action in [('기본 지침', self.load_default), ('MD 가져오기', self.import_md), ('MD 내보내기', self.export_md)]:
            button = QPushButton(name)
            button.clicked.connect(action)
            buttons.addWidget(button)
        layout.addLayout(buttons)
        self.editor = QPlainTextEdit()
        custom = self.controller.settings.directory / 'instructions.md'
        self.editor.setPlainText(read_text_strict(custom if custom.exists() else asset('기본_지침.md')))
        self.editor.textChanged.connect(self.invalidate_plan)
        layout.addWidget(self.editor, 3)
        targets = QHBoxLayout()
        self.target = QLineEdit()
        self.target.setPlaceholderText('적용할 AGENTS.md 경로 · 자동 적용하지 않습니다')
        self.target.textChanged.connect(self.invalidate_plan)
        targets.addWidget(self.target)
        project = QPushButton('프로젝트 선택')
        project.clicked.connect(self.project_target)
        user = QPushButton('사용자 지침 선택')
        user.clicked.connect(self.user_target)
        targets.addWidget(project)
        targets.addWidget(user)
        layout.addLayout(targets)
        actions = QHBoxLayout()
        preview = QPushButton('적용 미리보기')
        preview.clicked.connect(self.preview_md)
        self.apply_button = QPushButton('미리본 대상에 명시 적용')
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply_md)
        restore = QPushButton('백업 선택 · 원복')
        restore.clicked.connect(self.restore_md)
        for button in (preview, self.apply_button, restore):
            actions.addWidget(button)
        layout.addLayout(actions)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText('적용 후 전체 문서가 표시됩니다. 기존 구역은 유지하며 앱 관리구역만 추가·교체합니다.')
        layout.addWidget(self.preview, 2)
        self.tabs.addTab(page, 'MD 지침')

    def invalidate_plan(self):
        self.plan = None
        if hasattr(self, 'apply_button'):
            self.apply_button.setEnabled(False)

    def load_default(self):
        try:
            self.editor.setPlainText(read_text_strict(asset('기본_지침.md')))
        except Exception as error:
            self.error(error)

    def import_md(self):
        path, _ = QFileDialog.getOpenFileName(self, '엄격 UTF-8 Markdown 가져오기', '', 'Markdown (*.md);;모든 파일 (*)')
        if path:
            try:
                self.editor.setPlainText(read_text_strict(path))
            except Exception as error:
                self.error(error)

    def export_md(self):
        path, _ = QFileDialog.getSaveFileName(self, 'UTF-8 Markdown 내보내기', '모델_알림_지침.md', 'Markdown (*.md)')
        if path:
            try:
                Path(path).write_bytes(self.editor.toPlainText().encode('utf-8'))
            except Exception as error:
                self.error(error)

    def project_target(self):
        directory = QFileDialog.getExistingDirectory(self, '프로젝트 폴더 선택')
        if directory:
            self.target.setText(str(Path(directory) / 'AGENTS.md'))

    def user_target(self):
        directory = Path(os.environ.get('CODEX_HOME') or (Path.home() / '.codex'))
        self.target.setText(str(directory / 'AGENTS.md'))

    def preview_md(self):
        try:
            self.plan = self.store.preview(self.target.text(), self.editor.toPlainText())
            self.preview.setPlainText(self.plan['applied_bytes'].decode('utf-8-sig'))
            self.apply_button.setEnabled(True)
        except Exception as error:
            self.invalidate_plan()
            self.error(error)

    def apply_md(self):
        try:
            if self.plan is None:
                raise ValueError('새 미리보기가 필요합니다.')
            receipt = self.store.apply(self.plan)
            (self.controller.settings.directory / 'instructions.md').write_text(self.editor.toPlainText(), encoding='utf-8')
            self.invalidate_plan()
            QMessageBox.information(self, '지침 파일 적용 완료', '대상: ' + receipt['target'] + '\n원문 백업: ' + receipt['backup'] + '\n\n파일을 저장했습니다. 열린 대화의 재주입·서버 동기화·자동 모델 전환을 보장하지 않습니다.')
        except Exception as error:
            self.error(error)

    def restore_md(self):
        try:
            receipts = self.store.receipts()
            if not receipts:
                raise ValueError('앱이 만든 적용 백업이 없습니다.')
            dialog = QDialog(self)
            dialog.setWindowTitle('원복할 적용 기록 선택')
            layout = QVBoxLayout(dialog)
            choices = QListWidget()
            for receipt in receipts:
                choices.addItem(receipt['target'] + '\n' + Path(receipt['backup']).name)
            choices.setCurrentRow(0)
            layout.addWidget(choices)
            button = QPushButton('현재 해시 확인 후 원문 바이트 복원')
            button.clicked.connect(dialog.accept)
            layout.addWidget(button)
            dialog.resize(650, 360)
            if dialog.exec() == QDialog.DialogCode.Accepted and choices.currentRow() >= 0:
                self.store.restore(receipts[choices.currentRow()])
                self.invalidate_plan()
                QMessageBox.information(self, '원복 완료', '원문 바이트를 복원했습니다. 적용 뒤 변경된 파일은 원복하지 않습니다.')
        except Exception as error:
            self.error(error)

    def error(self, error):
        QMessageBox.warning(self, '작업을 완료하지 못했습니다', str(error))


class Controller:
    def __init__(self, settings, start_worker=True):
        self.settings = settings
        self.monitor = None
        self.window = Details(self)
        self.orbit = OrbitWidget(settings, self.show, self.preferences, QApplication.instance().quit)
        self.notice = Notice(self.show)
        self.orbit.show()
        if start_worker:
            self.start_monitor()

    def stop_monitor(self):
        if self.monitor:
            self.monitor.requestInterruption()
            self.monitor.wait()
            self.monitor = None

    def start_monitor(self):
        self.stop_monitor()
        self.monitor = Monitor(self.settings.values['sessions'], self.settings.directory)
        self.monitor.event.connect(self.receive)
        self.monitor.status.connect(self.status)
        history, problems = read_jsonl_tail(self.monitor.work / 'history.jsonl')
        self.window.history.clear()
        titles = session_titles(Path(self.settings.values['sessions']).parent / 'session_index.jsonl')
        for event in history:
            event['chat_name'] = titles.get(event.get('target'), event.get('target'))
            self.window.add_event(event)
        if problems:
            self.window.diagnostics.setPlainText('\n'.join(problems))
        self.monitor.start()

    def receive(self, event):
        self.window.add_event(event)
        self.orbit.unread = True
        if self.settings.values.get('popup', True):
            self.notice.display(event, self.orbit)

    def status(self, value):
        self.orbit.healthy = value.get('state') == '감시 중'
        self.window.summary.setText(value.get('state', '') + ' · ' + value.get('time', '') + '\n' + value.get('sessions', ''))
        self.window.diagnostics.setPlainText(json.dumps(value, ensure_ascii=False, indent=2))

    def show(self):
        self.window.tabs.setCurrentIndex(0)
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        self.orbit.unread = False

    def preferences(self):
        self.show()
        self.window.tabs.setCurrentIndex(1)

    def close(self):
        self.stop_monitor()
        self.notice.close()
        self.orbit.close()
        self.window.close()


def main():
    parser = argparse.ArgumentParser(description='Codex Orbit · 로컬 모델 변경 투명 궤도')
    parser.add_argument('--data-dir', type=Path, default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit')
    parser.add_argument('--sessions', type=Path)
    parser.add_argument('--smoke-test', action='store_true')
    parser.add_argument('--smoke-report', type=Path)
    parser.add_argument('--show-details', action='store_true')
    args = parser.parse_args()
    app = QApplication(sys.argv[:1])
    app.setApplicationName('Codex Orbit')
    app.setWindowIcon(QIcon(str(asset('Orbit.ico'))))
    app.setQuitOnLastWindowClosed(False)
    font_id = QFontDatabase.addApplicationFont(str(asset('NanumGothic-Bold.ttf')))
    families = QFontDatabase.applicationFontFamilies(font_id)
    font = QFont(families[0] if families else 'NanumGothic', 10, QFont.Weight.Bold)
    app.setFont(font)
    try:
        settings = Settings(args.data_dir)
        if args.sessions:
            settings.values['sessions'] = str(args.sessions.absolute())
        lock = QLockFile(str(args.data_dir / 'app.lock'))
        if not lock.tryLock(100):
            raise RuntimeError('같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.')
        controller = Controller(settings, start_worker=not args.smoke_test)
    except Exception as error:
        if args.smoke_report:
            args.smoke_report.write_text(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=False), encoding='utf-8')
        else:
            QMessageBox.critical(None, 'Codex Orbit 시작 실패', str(error))
        return 1
    app.aboutToQuit.connect(controller.close)
    if args.show_details:
        controller.show()
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
