"""앱과 같은 렌더러로 무채색 ICO·설치 그림·입체 모션 미리보기를 만듭니다."""
import binascii
from pathlib import Path
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QImage, QPainter
from PySide6.QtWidgets import QApplication
from visuals import draw_orbit


def orbit_image(size, moment=0, badge='81%', fraction=.81):
    image = QImage(size, size, QImage.Format.Format_RGBA8888)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.translate(size / 2, size / 2)
    painter.scale(size / 148, size / 148)
    draw_orbit(painter, moment, badge, fraction, 'fresh', True)
    painter.end()
    return image


def png_bytes(image):
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, 'PNG')
    return bytes(data)


def chunk(kind, value):
    return struct.pack('>I', len(value)) + kind + value + struct.pack('>I', binascii.crc32(kind + value) & 0xffffffff)


def write_motion(path):
    size, frames = 360, 48
    output = bytearray(b'\x89PNG\r\n\x1a\n')
    output += chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
    output += chunk(b'acTL', struct.pack('>II', frames, 0))
    sequence = 0
    for index in range(frames):
        image = orbit_image(size, index / 12)
        if index in (0, 12, 24, 36):
            image.save(str(path.parent / f'orbit-frame-{index:02}.png'))
        raw = bytes(image.constBits())
        packed = zlib.compress(b''.join(b'\0' + raw[y * size * 4:(y + 1) * size * 4] for y in range(size)), 6)
        output += chunk(b'fcTL', struct.pack('>IIIIIHHBB', sequence, size, size, 0, 0, 1, 12, 0, 0))
        sequence += 1
        if index == 0:
            output += chunk(b'IDAT', packed)
        else:
            output += chunk(b'fdAT', struct.pack('>I', sequence) + packed)
            sequence += 1
    output += chunk(b'IEND', b'')
    path.write_bytes(output)


def main():
    app = QApplication.instance() or QApplication([])
    identity = QFontDatabase.addApplicationFont(str(ROOT / 'assets/NanumGothic-Bold.ttf'))
    app.setFont(QFont(QFontDatabase.applicationFontFamilies(identity)[0], 10, QFont.Weight.Bold))
    assets = ROOT / 'assets'
    icons = [(size, png_bytes(orbit_image(size, .7, '')))
             for size in (16, 24, 32, 48, 64, 128, 256)]
    directory = bytearray(struct.pack('<HHH', 0, 1, len(icons)))
    offset = 6 + len(icons) * 16
    for size, data in icons:
        directory += struct.pack('<BBBBHHII', size % 256, size % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    (assets / 'Orbit.ico').write_bytes(directory + b''.join(data for _, data in icons))
    for name, width, height in (('SetupBanner.bmp', 328, 628), ('SetupSmall.bmp', 110, 110)):
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(QColor('#141414'))
        painter = QPainter(image)
        size = width - 28 if height > width else 100
        painter.drawImage((width - size) // 2, 100 if height > width else 5, orbit_image(size, .7, ''))
        if height > width:
            painter.setPen(QColor('#eeeeee'))
            painter.setFont(QFont(app.font().family(), 19, QFont.Weight.Bold))
            painter.drawText(QRectF(10, 415, width - 20, 50), Qt.AlignmentFlag.AlignCenter, 'Codex Orbit')
            painter.setFont(QFont(app.font().family(), 11, QFont.Weight.Bold))
            painter.drawText(QRectF(12, 473, width - 24, 80), Qt.AlignmentFlag.AlignCenter, '로컬 관측\n모델 변경 · 계정 한도')
        painter.end()
        image.save(str(assets / name))
    preview = ROOT / 'work/visual-review/repair4'
    preview.mkdir(parents=True, exist_ok=True)
    write_motion(preview / 'orbit-motion.apng')
    print('무채색 ICO 7해상도·설치 BMP 2개·360px APNG 48프레임 생성')


if __name__ == '__main__':
    main()
