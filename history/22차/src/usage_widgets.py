from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy
import time


class CalendarHero(QLabel):
    """사용 한도 화면에서만 날짜별 입체 이미지를 갱신합니다."""
    def __init__(self, parent=None):
        super().__init__('입체 이미지 준비 중', parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(120, 150)
        self.setMaximumWidth(300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet('color:#B5C8D4;background:transparent;')
        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.refresh_frame)
        self.started = time.monotonic()

    def set_active(self, active):
        from calendar_motion import set_calendar_motion_visible
        set_calendar_motion_visible(self, active)
        if active:
            self.timer.start()
            self.refresh_frame()
        else:
            self.timer.stop()

    def refresh_frame(self):
        from calendar_motion import get_calendar_frame, get_calendar_error
        image = get_calendar_frame(time.monotonic() - self.started)
        error = get_calendar_error()
        if error:
            self.setText('입체 이미지 표시 오류: ' + str(error))
        elif not image.isNull():
            pixmap = QPixmap.fromImage(image)
            self.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation))
