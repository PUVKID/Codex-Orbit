"""같은 실제3D 자산을 공유하는 정적 마크와 가시성 기반 내부 모션입니다."""
from functools import lru_cache
import time
import weakref
import json
import hashlib
import struct
import re
from PySide6.QtCore import Qt, QRect, QObject, QTimer
from PySide6.QtGui import QImage, QPixmap, QIcon, QPainter
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout
from shiboken6 import isValid
from atom_frames import get_atom_frames, asset_directory, AtomAssetError
from elements import daily_element
from element_frames import get_element_frame


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


def motion_brand_source(source, size):
    """원소 프레임의 실제 크기에 비례해 여백만 줄이며 영역 밖을 복사하지 않습니다."""
    if size > 32:
        return source
    margin=round(source.width()*16/296)
    return source.copy(source.rect().adjusted(margin,margin,-margin,-margin))


class BrandClock(QObject):
    """보이는 로고만 단일 시계에서 같은 프레임으로 갱신합니다."""
    def __init__(self):
        super().__init__(QApplication.instance())
        self.members = weakref.WeakSet()
        self.origin = time.monotonic()
        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.tick)

    @property
    def active_count(self):
        return sum(isValid(mark) and mark.isVisible() for mark in self.members)

    def watch(self, mark):
        self.members.add(mark)
        from calendar_motion import set_calendar_motion_visible
        set_calendar_motion_visible(mark, True)
        if not self.timer.isActive():
            self.timer.start()
        self.tick()

    def unwatch(self, mark):
        self.members.discard(mark)
        from calendar_motion import set_calendar_motion_visible
        set_calendar_motion_visible(mark, False)
        self.prune()

    def prune(self, *_):
        if not self.active_count:
            self.timer.stop()

    def tick(self):
        marks = [mark for mark in self.members if isValid(mark) and mark.isVisible()]
        if not marks:
            self.timer.stop()
            return
        elapsed = time.monotonic() - self.origin
        from calendar_motion import get_calendar_frame
        source = get_calendar_frame(elapsed)
        pixmaps = {}
        for mark in marks:
            size = mark.width()
            if size not in pixmaps:
                image = motion_brand_source(source,size)
                pixmaps[size] = QPixmap.fromImage(image.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                                                              Qt.TransformationMode.SmoothTransformation))
            mark.setPixmap(pixmaps[size])


_brand_clock = None


def brand_clock():
    global _brand_clock
    if _brand_clock is None or not isValid(_brand_clock):
        _brand_clock = BrandClock()
    return _brand_clock


class AnimatedBrand(QLabel):
    """닫힘·숨김 이벤트에 맞춰 재생 구독을 끝내는 실제3D 로고입니다."""
    def __init__(self, size, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setPixmap(QPixmap.fromImage(brand_image(size)))
        self.setAccessibleName('Codex Orbit 로고')
        self.setToolTip('Codex Orbit · 실제3D 모션')
        self.playback_clock = brand_clock()
        self.destroyed.connect(self.playback_clock.prune)

    def showEvent(self, event):
        super().showEvent(event)
        self.playback_clock.watch(self)

    def hideEvent(self, event):
        self.playback_clock.unwatch(self)
        super().hideEvent(event)

    def closeEvent(self, event):
        self.playback_clock.unwatch(self)
        super().closeEvent(event)


SYMBOL_NAMES = ('model', 'reasoning', 'time', 'reason', 'usage', 'refresh', 'history')


@lru_cache(maxsize=1)
def validate_symbols():
    """실제 메시에서 제작한 고정 기호 일곱 개를 창 생성 전에 검증합니다."""
    directory = asset_directory().parent / 'icons3d'
    try:
        path = directory / 'manifest.json'
        if not 0 < path.stat().st_size <= 65536:
            raise AtomAssetError('3D 기능 기호 매니페스트 크기 오류입니다.')
        metadata = json.loads(path.read_text(encoding='utf-8'))
        if type(metadata.get('schema_version')) is not int or metadata['schema_version'] != 1:
            raise AtomAssetError('3D 기능 기호 매니페스트 버전 오류입니다.')
        files = metadata.get('files')
        if not isinstance(files, dict) or set(files) != set(SYMBOL_NAMES):
            raise AtomAssetError('3D 기능 기호 일곱 개 목록이 일치하지 않습니다.')
        images = {}
        for name in SYMBOL_NAMES:
            record = files[name]
            if not isinstance(record, dict) or record.get('filename') != name+'.png':
                raise AtomAssetError('3D 기능 기호의 고정 파일 이름이 일치하지 않습니다.')
            digest = record.get('sha256')
            if not isinstance(digest, str) or re.fullmatch('[0-9a-f]{64}', digest) is None:
                raise AtomAssetError('3D 기능 기호의 SHA256 형식 오류입니다.')
            path = directory / (name+'.png')
            if not 0 < path.stat().st_size <= 262144:
                raise AtomAssetError('3D 기능 기호 읽기 크기 상한 오류입니다.')
            data = path.read_bytes()
            if len(data) > 262144 or hashlib.sha256(data).hexdigest() != digest:
                raise AtomAssetError('3D 기능 기호 SHA256이 일치하지 않습니다: '+name)
            if (len(data) < 33 or data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR'
                    or struct.unpack('>II', data[16:24]) != (96,96) or data[24:26] != bytes((8,6))):
                raise AtomAssetError('3D 기능 기호는96x96 RGBA PNG여야 합니다: '+name)
            image = QImage.fromData(data,'PNG')
            if image.isNull() or not image.hasAlphaChannel() or not image.allGray():
                raise AtomAssetError('3D 기능 기호의 무채색·투명 디코딩 오류입니다: '+name)
            if any(image.pixelColor(x,y).alpha() for x,y in ((0,0),(95,0),(0,95),(95,95))):
                raise AtomAssetError('3D 기능 기호의 모서리는 투명해야 합니다: '+name)
            images[name] = image
        return images
    except AtomAssetError:
        raise
    except Exception as error:
        raise AtomAssetError('필수3D 기능 기호를 읽을 수 없습니다: '+str(error)) from error


@lru_cache(maxsize=32)
def symbol_image(kind, size=20):
    """실제 메시 렌더만 축소하고 새로운 도형이나 글자를 덧그리지 않습니다."""
    name = {'effort':'reasoning', 'quota':'usage'}.get(kind,kind)
    if name not in SYMBOL_NAMES or not 1 <= size <= 96:
        raise ValueError('3D 기능 기호의 종류나 크기가 올바르지 않습니다.')
    source = validate_symbols()[name]
    points = [(x,y) for y in range(96) for x in range(96) if source.pixelColor(x,y).alpha() > 0]
    if not points:
        raise AtomAssetError('3D 기능 기호에 보이는 형상이 없습니다: '+name)
    left, right = min(x for x,_ in points), max(x for x,_ in points)
    top, bottom = min(y for _,y in points), max(y for _,y in points)
    bounds = QRect(max(0,left-2),max(0,top-2),min(95,right+2)-max(0,left-2)+1,
                   min(95,bottom+2)-max(0,top-2)+1)
    cropped = source.copy(bounds).scaled(size,size,Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
    # 원본 래스터의 종횡비를 보존하고 투명 정사각형 안에 중앙 배치합니다.
    image = QImage(size,size,QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.drawImage((size-cropped.width())//2,(size-cropped.height())//2,cropped)
    painter.end()
    return image


def symbol_icon(kind, size=20):
    return QIcon(QPixmap.fromImage(symbol_image(kind, size)))


def with_symbol(label, kind):
    """원문 QLabel을 유지하며 기능 의미를 읽기 쉬운 기호로 보조합니다."""
    row = QWidget()
    row.setStyleSheet('background:transparent;')
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(7)
    mark = QLabel()
    mark.setPixmap(QPixmap.fromImage(symbol_image(kind, 20)))
    mark.setFixedSize(20,20)
    mark.setAccessibleName({'model':'모델','effort':'추론 강도','time':'시각','reason':'공개 근거',
                            'quota':'사용 한도','history':'변경 기록'}.get(kind,kind))
    layout.addWidget(mark,0,Qt.AlignmentFlag.AlignVCenter)
    layout.addWidget(label,1)
    return row
