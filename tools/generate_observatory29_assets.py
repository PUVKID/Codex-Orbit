"""새 관측소의 실제 4K GPU 렌더에서 ICO와 민트 설치 이미지를 재현합니다."""
import hashlib
import json
import os
from pathlib import Path
import struct
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from PySide6.QtCore import QBuffer, QIODevice, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QImage, QPainter
from PySide6.QtWidgets import QApplication
from calendar_renderer import CalendarRenderer


def png_bytes(image):
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, 'PNG'):
        raise RuntimeError('실제 렌더 PNG를 저장하지 못했습니다.')
    return bytes(buffer.data())


def main():
    app = QApplication.instance() or QApplication([])
    font_id = QFontDatabase.addApplicationFont(str(ROOT / 'assets/NanumGothic-Bold.ttf'))
    families = QFontDatabase.applicationFontFamilies(font_id)
    if not families:
        raise RuntimeError('설치 배너용 나눔고딕 Bold 글꼴을 읽지 못했습니다.')
    renderer = CalendarRenderer((3840, 2160))
    try:
        renderer.set_output_size(1024)
        image = renderer.render_observatory({'model': None, 'effort': 'none', 'agents': [],
                                             'usage_fraction': 0, 'transition': 1}, .65)
        gpu = renderer.ctx.info.get('GL_RENDERER', '확인 불가')
    finally:
        renderer.close()
    assets = ROOT / 'assets'
    icon_sizes = (16, 24, 32, 48, 64, 128, 256)
    icons = [(size, png_bytes(image.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation))) for size in icon_sizes]
    directory = bytearray(struct.pack('<HHH', 0, 1, len(icons)))
    offset = 6 + 16 * len(icons)
    for size, data in icons:
        directory += struct.pack('<BBBBHHII', size % 256, size % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    (assets / 'Orbit.ico').write_bytes(directory + b''.join(data for _, data in icons))
    for name, width, height in (('SetupBanner.bmp', 328, 628), ('SetupSmall.bmp', 110, 110)):
        banner = QImage(width, height, QImage.Format.Format_RGB32)
        banner.fill(QColor('#f0faf6'))
        painter = QPainter(banner)
        size = width - 24 if height > width else width - 8
        y = 64 if height > width else 4
        painter.drawImage((width - size) // 2, y, image.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                                                            Qt.TransformationMode.SmoothTransformation))
        if height > width:
            painter.setPen(QColor('#193d36'))
            painter.setFont(QFont(families[0], 22, QFont.Weight.Bold))
            painter.drawText(QRectF(12, 405, width - 24, 50), Qt.AlignmentFlag.AlignCenter, 'Codex Orbit')
            painter.setFont(QFont(families[0], 12, QFont.Weight.Bold))
            painter.drawText(QRectF(12, 470, width - 24, 90), Qt.AlignmentFlag.AlignCenter, '3D 관측소\n모델 · 작업 · 계정 한도')
        painter.end()
        if not banner.save(str(assets / name)):
            raise RuntimeError('설치 배너 저장에 실패했습니다.')
    output = ROOT / 'evidence'
    output.mkdir(exist_ok=True)
    image.save(str(output / '29_observatory_brand_source.png'))
    files = {}
    for name in ('Orbit.ico', 'SetupBanner.bmp', 'SetupSmall.bmp'):
        raw = (assets / name).read_bytes()
        files[name] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    record = {'source': '관측소 실제 삼각형 메시와 깊이·금속 셰이더의 GPU 직접 렌더',
              'source_dimensions': [3840, 2160], 'delivery_size': 1024, 'elapsed': .65,
              'neutral_model': True, 'icon_sizes': list(icon_sizes), 'gpu': gpu, 'files': files}
    (output / '29_observatory_assets.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'files': files, 'icon_sizes': list(icon_sizes)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
