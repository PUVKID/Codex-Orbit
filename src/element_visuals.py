"""원본3D 자산을 변경하지 않는 제한 메모리 Qt 색 합성입니다."""
from PySide6.QtGui import QColor, QImage, QPainter


def colorize_atom(image, element):
    """SourceAtop은 원본 알파를 유지하며 명암에 부드러운 영감색을 더합니다."""
    result = image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
    if result.isNull():
        return result
    painter = QPainter(result)
    try:
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
        tint = QColor(element.color)
        tint.setAlpha(48)
        painter.fillRect(result.rect(),tint)
    finally:
        painter.end()
    # 색 프레임은 보관하지 않습니다. 원본24장 캐시는 기존 재생기만 소유합니다.
    return result
