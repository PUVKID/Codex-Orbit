"""공식 릴리스 확인·검증·설치 준비와 최소 결과 요약 화면입니다."""
import os
import sys
import threading
from PySide6.QtCore import QObject, Signal, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QPlainTextEdit
from shiboken6 import isValid
from observatory_panel import tr
from safe_update import SafeUpdater, REPOSITORY, read_update_result

VERSION = '3.12.0'
RELEASES_URL = REPOSITORY + '/releases'


class UpdateBridge(QObject):
    result = Signal(object, object)
    phase = Signal(str)


class UpdateDialog(QDialog):
    def __init__(self, controller):
        super().__init__(controller.window)
        self.controller = controller
        self.release = self.staged = None
        self.busy = self.latest = False
        self.error_text = None
        self.stage_kind = None
        self.phase = 'check'
        self.updater = SafeUpdater(controller.settings.directory)
        self.recent_result = read_update_result(controller.settings.directory)
        self.resize(580, 340)
        layout = QVBoxLayout(self)
        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.label)
        self.recent_label = QLabel()
        self.recent_label.setWordWrap(True)
        self.recent_label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.recent_label)
        self.release_button = QPushButton()
        self.release_button.clicked.connect(self.open_release)
        layout.addWidget(self.release_button)
        self.copy_button = QPushButton()
        self.copy_button.clicked.connect(self.copy_sha)
        layout.addWidget(self.copy_button)
        self.action = QPushButton()
        self.action.clicked.connect(self.next_step)
        layout.addWidget(self.action)
        self.details_button = QPushButton()
        self.details_button.setCheckable(True)
        layout.addWidget(self.details_button)
        self.error_details = QPlainTextEdit()
        self.error_details.setReadOnly(True)
        self.error_details.setMaximumHeight(130)
        self.details_button.toggled.connect(self.error_details.setVisible)
        layout.addWidget(self.error_details)
        self.close_button = QPushButton()
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)
        self.bridge = UpdateBridge(self)
        self.bridge.result.connect(self.handle_result)
        self.bridge.phase.connect(self.set_phase)
        self.retranslate()

    def open_release(self):
        # 메타데이터나 오류 원문의 URL을 실행하지 않습니다.
        QDesktopServices.openUrl(QUrl(RELEASES_URL))

    def copy_sha(self):
        if self.staged and not self.busy:
            QGuiApplication.clipboard().setText(self.staged['sha256'])

    def closeEvent(self, event):
        if self.busy:
            event.ignore()
        else:
            super().closeEvent(event)

    def reject(self):
        if not self.busy:
            super().reject()

    def set_phase(self, phase):
        if self.busy and phase in ('download', 'verify'):
            self.phase = phase
            self.retranslate()

    def next_step(self):
        if self.busy:
            return
        if self.staged:
            try:
                self.updater.apply(self.staged, parent_pid=os.getpid())
            except Exception as error:
                self.error_text = str(error)
                self.retranslate()
                return
            self.accept()
            self.controller.request_quit()
            return
        self.busy = True
        self.error_text = None
        self.stage_kind = 'stage' if self.release else 'check'
        self.phase = 'download' if self.release else 'check'
        self.retranslate()
        # 작업 스레드는 대화상자를 소유하거나 UI에 직접 접근하지 않습니다.
        updater, release, bridge = self.updater, self.release, self.bridge
        def emit_phase(phase):
            if isValid(bridge):
                try:
                    bridge.phase.emit(phase)
                except RuntimeError:
                    pass
        def work():
            try:
                value = updater.stage(release, progress=emit_phase) if release else updater.check(VERSION)
                error = None
            except Exception as problem:
                value, error = None, str(problem)
            if isValid(bridge):
                try:
                    bridge.result.emit(value, error)
                except RuntimeError:
                    pass
        threading.Thread(target=work, name='orbit-update-check', daemon=True).start()

    def handle_result(self, value, error):
        self.busy = False
        if error:
            self.error_text = str(error)
        elif self.stage_kind == 'check':
            self.latest = not value.get('available')
            if not self.latest:
                self.release = value
        else:
            self.staged = value
        self.retranslate()

    def retranslate(self):
        self.setWindowTitle(tr('공식 업데이트', 'Official update'))
        self.close_button.setText(tr('닫기', 'Close'))
        self.close_button.setEnabled(not self.busy)
        self.release_button.setText(tr('공식 릴리스 페이지 열기', 'Open official releases'))
        self.copy_button.setText(tr('검증된 SHA-256 복사', 'Copy verified SHA-256'))
        self.copy_button.setVisible(self.staged is not None)
        self.copy_button.setEnabled(self.staged is not None and not self.busy)
        self.details_button.setText(tr('오류 원문 펼치기', 'Show original error'))
        self.details_button.setVisible(bool(self.error_text))
        self.error_details.setPlainText(self.error_text or '')
        self.error_details.setVisible(bool(self.error_text) and self.details_button.isChecked())
        self.action.setEnabled(not self.busy)
        recent = self.recent_result
        if recent:
            labels = {'updated': tr('업데이트 성공', 'Update successful'),
                      'rolled_back': tr('이전 버전 복구·시작 완료', 'Previous version restored and started'),
                      'failed': tr('업데이트 실패', 'Update failed')}
            self.recent_label.setText(tr('최근 결과: ', 'Last result: ') + labels[recent['status']] +
                                      ' · ' + recent['version'] + ' · ' + recent['time'] +
                                      (' · ' + recent['error'] if 'error' in recent else ''))
        self.recent_label.setVisible(bool(recent))
        if self.busy:
            labels = {'check': tr('확인 단계 · 공식 릴리스 정보를 확인합니다.', 'Checking · Reading official release information.'),
                      'download': tr('다운로드 단계 · 여유 공간 확인 후 내려받습니다.', 'Download · Checking free space and downloading.'),
                      'verify': tr('검증 단계 · 크기·SHA-256·EXE 형식을 검사합니다.', 'Verification · Checking size, SHA-256 and EXE format.')}
            text = labels[self.phase]
            self.action.setText(tr('작업 중', 'Working'))
        elif self.error_text:
            text = tr('업데이트를 진행하지 못했습니다. 연결과 디스크 공간을 확인하고 다시 시도해 주세요. 오류 원문에서 상세 원인을 확인할 수 있습니다.',
                      'The update could not proceed. Check your connection and disk space, then retry. Expand the original error for details.')
            self.action.setText(tr('다시 시도', 'Retry'))
        elif self.staged:
            text = tr('설치 준비 완료 · 다운로드 검증을 마쳤습니다.', 'Ready to install · Download verification completed.')
            text += '\nSHA-256: ' + self.staged['sha256']
            text += '\n' + tr('설치 직전에 기존 실행 파일 1개를 백업합니다. 개인 설정과 MD는 유지합니다. 새 실행 파일의 시작 검사나 재시작이 실패하면 이전 실행 파일을 복구하고 시작을 시도합니다.',
                               'One existing executable will be backed up immediately before installation. Settings and MD files are retained. If the new executable fails its startup check or restart, the previous executable is restored and a restart is attempted.')
            self.action.setText(tr('설치하고 재시작', 'Install and restart'))
        elif self.release:
            size = self.release['size'] / (1024 * 1024)
            required = (self.release['size'] * 3 + 64 * 1024 * 1024) / (1024 * 1024)
            text = tr('새 버전: ', 'New version: ') + self.release['version']
            text += '\n' + tr('다운로드 크기: ', 'Download size: ') + f'{size:.2f} MB (1 MB = 1,048,576 bytes)'
            text += '\n' + tr('준비 경로 필요 여유 공간: ', 'Required free space on the staging volume: ') + f'{required:.2f} MB'
            text += '\n' + tr('공식 릴리스에서 내려받은 뒤 크기와 SHA-256을 검증합니다.', 'Size and SHA-256 are verified after downloading the official release.')
            self.action.setText(tr('다운로드하고 검증', 'Download and verify'))
        elif self.latest:
            text = tr('현재 버전이 최신 공개 버전입니다.', 'The current version is up to date.')
            self.action.setText(tr('다시 확인', 'Check again'))
        else:
            text = tr('현재 버전 3.12.0 · 공식 저장소의 릴리스만 확인합니다.', 'Version 3.12.0 · Only releases from the official repository are checked.')
            self.action.setText(tr('새 버전 확인', 'Check for update'))
        if self.staged and not getattr(sys, 'frozen', False):
            self.action.setEnabled(False)
            text += '\n' + tr('소스 실행 중입니다. 배포 EXE에서 설치할 수 있습니다.', 'Running from source. Install from the distributed EXE.')
        self.label.setText(text)


def show_update(controller):
    dialog = getattr(controller, 'update_dialog29', None)
    if dialog is None or not isValid(dialog):
        dialog = UpdateDialog(controller)
        controller.update_dialog29 = dialog
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
