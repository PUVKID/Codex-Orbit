"""같은 논리 크기의 최신 모션 이미지를 부모 재배치 없이 표시합니다."""
from PySide6.QtGui import QIcon, QPainter
from PySide6.QtWidgets import QLabel, QStyle


class MotionImageLabel(QLabel):
    """최신 이미지 한 개를 보관하고 크기·DPR 변경 때만 기본 크기 힌트를 갱신합니다."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._motion_icon = None
        self._motion_size = None
        self._motion_geometry = None

    def setPixmap(self, pixmap):
        logical = pixmap.deviceIndependentSize()
        geometry = (logical.width(), logical.height(), pixmap.devicePixelRatioF())
        self._motion_icon = QIcon(pixmap)
        self._motion_size = logical.toSize()
        if self._motion_geometry != geometry:
            self._motion_geometry = geometry
            super().setPixmap(pixmap)
        else:
            self.update()

    def pixmap(self):
        if self._motion_icon is None:
            return super().pixmap()
        # 현재 Qt QLabel과 같이 논리 크기의 QIcon 표본을 반환합니다.
        return self._motion_icon.pixmap(self._motion_size)

    def setText(self, text):
        # 현재 Qt의 같은 문자열 no-op 계약도 그대로 보존합니다.
        if text != super().text():
            self._motion_icon = None
            self._motion_size = None
            self._motion_geometry = None
        super().setText(text)

    def clear(self):
        self._motion_icon = None
        self._motion_size = None
        self._motion_geometry = None
        super().clear()

    def paintEvent(self, event):
        if self._motion_icon is None or self._motion_icon.isNull():
            return super().paintEvent(event)
        painter = QPainter(self)
        try:
            self.drawFrame(painter)
            rect = self.contentsRect()
            margin = self.margin()
            rect.adjust(margin, margin, -margin, -margin)
            alignment = QStyle.visualAlignment(self.layoutDirection(), self.alignment())
            mode = QIcon.Mode.Normal if self.isEnabled() else QIcon.Mode.Disabled
            image = self._motion_icon.pixmap(self._motion_size, self.devicePixelRatioF(), mode)
            self.style().drawItemPixmap(painter, rect, alignment.value, image)
        finally:
            painter.end()
