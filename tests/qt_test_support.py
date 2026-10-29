"""제품 수명주기를 바꾸지 않는 Qt 시험 자원 정리와 짧은 시험 주기."""
import os
import sys
import traceback

# 시험 프로세스와 그 격리 자식만 화면 서버에 의존하지 않으며 제품 실행 환경은 바꾸지 않습니다.
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtCore import QCoreApplication, QEvent, QEventLoop, QThread, QTimer, Qt
from PySide6.QtWidgets import QApplication
from app import Details, Monitor, OrbitWidget


_qt_slot_errors = []
_previous_excepthook = sys.excepthook


def _record_qt_slot_exception(kind, value, trace):
    """Qt가 시험 밖으로 전달한 예외도 원문을 출력하고 해당 시험을 실패시킵니다."""
    _qt_slot_errors.append(''.join(traceback.format_exception(kind, value, trace)))
    _previous_excepthook(kind, value, trace)


sys.excepthook = _record_qt_slot_exception


class FastMonitor(Monitor):
    """실제 감시 흐름·입출력을 유지하고 시험의 주기 대기만 줄입니다."""
    @staticmethod
    def msleep(milliseconds):
        QThread.msleep(min(milliseconds, 2))


def wait_qt(milliseconds):
    """실제 정밀 타이머가 끝날 때까지 GUI 이벤트 루프에서 기다립니다."""
    loop = QEventLoop()
    timer = QTimer(loop)
    timer.setSingleShot(True)
    timer.setTimerType(Qt.TimerType.PreciseTimer)
    timer.timeout.connect(loop.quit)
    timer.start(milliseconds)
    try:
        loop.exec()
    finally:
        timer.stop()


def cleanup_qt_widgets(testcase):
    """시험별 close와 작업자 종료 뒤 남은 타이머·위젯을 정리합니다."""
    application = QApplication.instance()
    if application is None:
        return
    widgets = application.topLevelWidgets()
    controllers = {widget.controller for widget in widgets if isinstance(widget, Details)}
    for controller in controllers:
        worker = controller.monitor
        controller.close()
        if isinstance(worker, QThread):
            testcase.assertTrue(worker.wait(2000), '시험 위젯을 없애기 전에 감시 작업자가 종료돼야 합니다.')
    for widget in widgets:
        timer = getattr(widget, 'timer', None)
        if timer is not None:
            timer.stop()
        widget.close()
        widget.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    testcase.assertFalse(any(isinstance(widget, OrbitWidget) for widget in application.topLevelWidgets()),
                         '다음 시험에 궤도 위젯이나 회전 타이머를 남기지 않습니다.')
    errors = list(_qt_slot_errors)
    _qt_slot_errors.clear()
    testcase.assertFalse(errors, '처리되지 않은 Qt 슬롯 예외:\n' + '\n'.join(errors))
