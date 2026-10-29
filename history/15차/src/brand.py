"""같은 금속 원자 제작 프레임을 사용하는 정적 앱 마크입니다."""
from functools import lru_cache
from PySide6.QtCore import Qt, QRect
from atom_frames import get_atom_frames


@lru_cache(maxsize=7)
def brand_image(size):
    size = int(size)
    if not 1 <= size <= 512:
        raise ValueError('브랜드 이미지 크기는1~512px여야 합니다.')
    source = get_atom_frames().frame(0)
    # 작은 세 해상도만 투명 여백을 줄이며 금속 픽셀이나 핵을 새로 그리지 않습니다.
    if size <= 32:
        source = source.copy(QRect(16, 16, 264, 264))
    return source.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
