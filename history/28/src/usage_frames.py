"""검증된 대시보드 조형 프레임을 추출 없이 읽는 제한 메모리 재생기입니다."""
from collections import OrderedDict
import atexit
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys
import zipfile

from PySide6.QtGui import QImage


FRAME_COUNT = 360
FRAME_SIZE = 384
FPS = 30
PERIOD_SECONDS = 12
CACHE_LIMIT = 16
MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_FRAME_BYTES = 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_MANIFEST_BYTES = 64 * 1024


class UsageAssetError(RuntimeError):
    """조형 표시 오류를 호출자에게 전달하며 계정 조회 흐름과 분리합니다."""


def asset_directory():
    root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
    return root / 'assets' / 'usage3d'


def _identity(path):
    value = path.stat()
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns


def _json_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise UsageAssetError('대시보드 조형 자산 매니페스트에 중복 필드가 있습니다.')
        value[key] = item
    return value


class UsageFrames:
    """시작 시 전체 무결성을 검사하고 해제된 QImage는 최대16장만 보존합니다."""
    def __init__(self, directory):
        # 제품 호출은 asset_directory만 사용하며 별도 경로는 고립 fixture용입니다.
        self.directory = Path(directory)
        self.cache = OrderedDict()
        self.archive = None
        self._stream = None
        try:
            self._prepare()
        except Exception as error:
            self.close()
            if isinstance(error, UsageAssetError):
                raise
            raise UsageAssetError('필수 대시보드 조형 자산을 읽을 수 없습니다: ' + str(error)) from error

    def _prepare(self):
        manifest_path = self.directory / 'manifest.json'
        archive_path = self.directory / 'frames.zip'
        if not 0 < manifest_path.stat().st_size <= MAX_MANIFEST_BYTES:
            raise UsageAssetError('대시보드 조형 자산 매니페스트 크기가 허용 범위를 벗어났습니다.')
        self.manifest = json.loads(manifest_path.read_text(encoding='utf-8'), object_pairs_hook=_json_object)
        expected = {'schema_version': 1, 'width': FRAME_SIZE, 'height': FRAME_SIZE,
                    'fps': FPS, 'period_seconds': PERIOD_SECONDS, 'frame_count': FRAME_COUNT,
                    'frame_pattern': 'frame_{:04d}.png', 'archive': 'frames.zip'}
        if not isinstance(self.manifest, dict):
            raise UsageAssetError('대시보드 조형 자산 매니페스트는 객체여야 합니다.')
        for key, value in expected.items():
            actual = self.manifest.get(key)
            if type(actual) is not type(value) or actual != value:
                raise UsageAssetError('대시보드 조형 자산 계약 불일치: ' + key)
        for key in ('geometry', 'lighting', 'source'):
            if not isinstance(self.manifest.get(key), (dict, str)) or not self.manifest[key]:
                raise UsageAssetError('대시보드 조형 자산 제작 근거 누락: ' + key)
        digest = self.manifest.get('archive_sha256')
        if not isinstance(digest, str) or re.fullmatch('[0-9a-f]{64}', digest) is None:
            raise UsageAssetError('대시보드 조형 프레임 ZIP의 SHA256 형식이 잘못됐습니다.')
        if not 0 < archive_path.stat().st_size <= MAX_ARCHIVE_BYTES:
            raise UsageAssetError('대시보드 조형 프레임 ZIP 크기가 허용 범위를 벗어났습니다.')
        self.identities = (_identity(manifest_path), _identity(archive_path))
        self._stream = archive_path.open('rb')
        hasher = hashlib.sha256()
        while chunk := self._stream.read(1024 * 1024):
            hasher.update(chunk)
        if hasher.hexdigest() != digest:
            raise UsageAssetError('대시보드 조형 프레임 ZIP의 SHA256이 일치하지 않습니다.')
        self._stream.seek(0)
        self.archive = zipfile.ZipFile(self._stream)
        members = self.archive.infolist()
        names = {f'frame_{index:04d}.png' for index in range(FRAME_COUNT)}
        if len(members) != FRAME_COUNT or {item.filename for item in members} != names:
            raise UsageAssetError('대시보드 조형 프레임 ZIP의 정확한360개 이름·목록이 일치하지 않습니다.')
        if sum(item.file_size for item in members) > MAX_TOTAL_BYTES:
            raise UsageAssetError('대시보드 조형 프레임 전체 읽기 상한을 초과했습니다.')
        for item in members:
            if (item.is_dir() or item.flag_bits & 1 or item.compress_type not in
                    (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED) or
                    not 0 < item.file_size <= MAX_FRAME_BYTES):
                raise UsageAssetError('대시보드 조형 프레임 멤버의 형식·크기가 허용 범위를 벗어났습니다.')
            # read는 각 멤버의 CRC도 검사합니다. 이미지는 한 장씩 검사하고 버립니다.
            image = self._decode(item.filename)
            if item.filename == 'frame_0000.png':
                self.cache[0] = image
        self._check_unchanged()

    def _decode(self, name):
        with self.archive.open(name) as stream:
            data = stream.read(MAX_FRAME_BYTES + 1)
        if len(data) > MAX_FRAME_BYTES or len(data) < 33 or data[:8] != b'\x89PNG\r\n\x1a\n':
            raise UsageAssetError('대시보드 조형 프레임 PNG 서명·크기가 잘못됐습니다: ' + name)
        if (data[12:16] != b'IHDR' or struct.unpack('>II', data[16:24]) != (FRAME_SIZE, FRAME_SIZE)
                or data[24:26] != bytes((8, 6))):
            raise UsageAssetError('대시보드 조형 프레임은384x384의8비트RGBA PNG여야 합니다: ' + name)
        image = QImage.fromData(data, 'PNG')
        if (image.isNull() or image.width() != FRAME_SIZE or image.height() != FRAME_SIZE
                or not image.hasAlphaChannel()):
            raise UsageAssetError('대시보드 조형 프레임의 디코딩·알파 계약이 잘못됐습니다: ' + name)
        if any(image.pixelColor(x, y).alpha() for x, y in ((0, 0), (383, 0), (0, 383), (383, 383))):
            raise UsageAssetError('대시보드 조형 프레임의 모서리는 투명해야 합니다: ' + name)
        return image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)

    def _check_unchanged(self):
        actual = (_identity(self.directory / 'manifest.json'), _identity(self.directory / 'frames.zip'))
        if actual != self.identities:
            raise UsageAssetError('검증 뒤 대시보드 조형 자산이 변경됐습니다. 앱을 다시 실행해 주세요.')

    @staticmethod
    def frame_index(elapsed):
        if type(elapsed) not in (int, float):
            raise UsageAssetError("조형 재생 시각은 유한한 숫자여야 합니다.")
        try:
            finite = math.isfinite(elapsed)
        except OverflowError:
            finite = False
        if not finite:
            raise UsageAssetError('대시보드 조형 프레임의 재생 시각이 유한한 숫자가 아닙니다.')
        return int((elapsed % PERIOD_SECONDS) * FPS) % FRAME_COUNT

    def frame(self, elapsed):
        if self.archive is None:
            raise UsageAssetError("조형 재생기가 닫혔습니다.")
        try:
            self._check_unchanged()
        except OSError as error:
            raise UsageAssetError("조형 자산 경로가 변경됐습니다.") from error
        index = self.frame_index(elapsed)
        if index not in self.cache:
            try:
                self.cache[index] = self._decode(f'frame_{index:04d}.png')
            except Exception as error:
                raise UsageAssetError('대시보드 조형 프레임 재생 실패: ' + str(error)) from error
            while len(self.cache) > CACHE_LIMIT:
                self.cache.popitem(last=False)
        self.cache.move_to_end(index)
        return self.cache[index]

    @property
    def cache_bytes(self):
        return sum(image.sizeInBytes() for image in self.cache.values())

    def close(self):
        if self.archive is not None:
            self.archive.close()
            self.archive = None
        if self._stream is not None:
            self._stream.close()
            self._stream = None
        self.cache.clear()


_runtime_frames = None


def close_usage_frames():
    """프로세스 공유 ZIP을 한 번 닫으며 중복 종료 호출도 안전하게 처리합니다."""
    global _runtime_frames
    value, _runtime_frames = _runtime_frames, None
    if value is not None:
        value.close()


atexit.register(close_usage_frames)


def preflight_usage_frames():
    """제품의 고정 경로는 프로세스에서 한 번 검증하고 모든 창이 공유합니다."""
    global _runtime_frames
    if _runtime_frames is None:
        _runtime_frames = UsageFrames(asset_directory())
    else:
        try:
            _runtime_frames._check_unchanged()
        except OSError as error:
            raise UsageAssetError("조형 자산 경로가 변경됐습니다.") from error
    return _runtime_frames


def get_usage_frame(elapsed):
    """공유 팩의 한 프레임을 반환하며 계정 조회 상태에는 관여하지 않습니다."""
    UsageFrames.frame_index(elapsed)
    return preflight_usage_frames().frame(elapsed)
