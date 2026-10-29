"""작은 크기에서도 읽히는 Codex Orbit의 단일 정적 브랜드 마크입니다."""
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen


def brand_image(size):
    """검은 경계·굵은 흰 궤도·비대칭 위성을 원래 해상도에서 그립니다."""
    size = int(size)
    image = QImage(size, size, QImage.Format.Format_RGBA8888)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(size, size)
    # 검은 외곽과 흰 안쪽 선이 밝고 어두운 바탕에서 각각 경계를 유지합니다.
    painter.setBrush(QColor('#111111'))
    painter.setPen(QPen(QColor('#111111'), .10))
    painter.drawEllipse(QRectF(.12, .20, .68, .68))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(QColor('#ffffff'), .115))
    painter.drawEllipse(QRectF(.205, .285, .51, .51))
    # 오른쪽 위의 하나의 위성은 궤도와 겹치지 않는 식별 표식입니다.
    painter.setBrush(QColor('#ffffff'))
    painter.setPen(QPen(QColor('#111111'), .075))
    painter.drawEllipse(QPointF(.79, .22), .115, .115)
    painter.end()
    return image
