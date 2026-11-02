"""공식 릴리스 확인과 검증된 업데이트 준비 화면입니다."""
import os,sys,threading
from pathlib import Path
from PySide6.QtCore import QObject,Signal,Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QLabel,QPushButton
from shiboken6 import isValid
from observatory_panel import tr

VERSION='3.0.1'

class UpdateBridge(QObject):
    result=Signal(object,object)

class UpdateDialog(QDialog):
    def __init__(self,controller):
        super().__init__(controller.window);self.controller=controller;self.release=None;self.staged=None;self.busy=False;self.latest=False;self.error_text=None
        from safe_update import SafeUpdater
        self.updater=SafeUpdater(controller.settings.directory)
        self.setWindowTitle(tr('공식 업데이트','Official update'));self.resize(540,260)
        layout=QVBoxLayout(self);self.label=QLabel(tr('현재 버전 3.0.1 · 공식 저장소의 릴리스만 확인합니다.','Version 3.0.1 · Only releases from the official repository are checked.'));self.label.setWordWrap(True);self.label.setTextFormat(Qt.TextFormat.PlainText);layout.addWidget(self.label)
        self.action=QPushButton(tr('새 버전 확인','Check for update'));self.action.clicked.connect(self.next_step);layout.addWidget(self.action)
        self.close_button=QPushButton(tr('닫기','Close'));self.close_button.clicked.connect(self.close);layout.addWidget(self.close_button)
        self.bridge=UpdateBridge(self);self.bridge.result.connect(self.done)
        self.stage_kind=None
        self.retranslate()
    def next_step(self):
        if self.busy:return
        if self.staged:
            try:
                self.updater.apply(self.staged,parent_pid=os.getpid())
            except Exception as error:self.label.setText(tr('업데이트를 시작하지 못했습니다: ','Could not start the update: ')+str(error));return
            self.accept();self.controller.request_quit();return
        self.busy=True;self.error_text=None;self.retranslate();self.action.setEnabled(False)
        function=(lambda:self.updater.stage(self.release)) if self.release else (lambda:self.updater.check(VERSION))
        self.stage_kind='stage' if self.release else 'check';bridge=self.bridge
        def work():
            try:value=function();error=None
            except Exception as problem:value=None;error=str(problem)
            if isValid(bridge):
                try:bridge.result.emit(value,error)
                except RuntimeError:pass
        threading.Thread(target=work,name='orbit-update-check',daemon=True).start()
    def done(self,value,error):
        self.busy=False;self.action.setEnabled(True)
        if error:self.error_text=str(error);self.retranslate();return
        if self.stage_kind=='check':
            if not value.get('available'):
                self.latest=True;self.retranslate();return
            self.release=value
            self.label.setText(tr('새 버전: ','New version: ')+str(value['version'])+'\n'+tr('공식 릴리스에서 내려받고 SHA-256을 검증합니다. 개인 설정과 MD는 보존합니다.','Download from the official release and verify SHA-256. Your settings and MD files are preserved.'))
            self.action.setText(tr('검증하여 준비','Download and verify'))
        else:
            self.staged=value
            self.label.setText(tr('다운로드 검증 완료. 재시작 검사에 실패하면 이전 실행 파일을 복구합니다.','Download verified. The previous executable is restored if the restart check fails.')+'\nSHA-256: '+str(value['sha256']))
            self.action.setText(tr('설치하고 재시작','Install and restart'))
            if not getattr(sys,'frozen',False):
                self.action.setEnabled(False);self.label.setText(self.label.text()+'\n'+tr('소스 실행 중입니다. 배포 EXE에서 설치할 수 있습니다.','Running from source. Install from the distributed EXE.'))


    def retranslate(self):
        self.setWindowTitle(tr('공식 업데이트','Official update'))
        self.close_button.setText(tr('닫기','Close'))
        self.action.setEnabled(not self.busy)
        if self.error_text:
            self.label.setText(tr('확인 실패: ','Check failed: ')+self.error_text)
            self.action.setText(tr('다시 시도','Retry'))
        elif self.busy:
            self.label.setText(tr('공식 릴리스를 확인하고 있습니다. 잠시만 기다려 주세요.','Checking the official release. Please wait.'))
            self.action.setText(tr('확인 중','Checking'))
        elif self.staged:
            self.label.setText(tr('검증 완료. 재시작 검사에 실패하면 이전 실행 파일을 복구합니다.','Verified. The previous executable is restored if the restart check fails.')+'\nSHA-256: '+str(self.staged['sha256']))
            self.action.setText(tr('설치하고 재시작','Install and restart'))
            if not getattr(sys,'frozen',False):
                self.action.setEnabled(False);self.label.setText(self.label.text()+'\n'+tr('소스 실행 중입니다. 배포 EXE에서 설치할 수 있습니다.','Running from source. Install from the distributed EXE.'))
        elif self.release:
            self.label.setText(tr('새 버전: ','New version: ')+str(self.release['version'])+'\n'+tr('공식 릴리스에서 내려받아 SHA-256을 검증합니다. 개인 설정과 MD는 보존합니다.','Download from the official release and verify SHA-256. Your settings and MD are preserved.'))
            self.action.setText(tr('검증하여 준비','Download and verify'))
        elif self.latest:
            self.label.setText(tr('현재 버전이 최신 공개 버전입니다.','The current version is up to date.'));self.action.setText(tr('다시 확인','Check again'))
        else:
            self.label.setText(tr('현재 버전 3.0.1 · 공식 저장소의 릴리스만 확인합니다.','Version 3.0.1 · Only releases from the official repository are checked.'));self.action.setText(tr('새 버전 확인','Check for update'))


def show_update(controller):
    dialog=getattr(controller,'update_dialog29',None)
    if dialog is None or not isValid(dialog):dialog=UpdateDialog(controller);controller.update_dialog29=dialog
    dialog.show();dialog.raise_();dialog.activateWindow()
