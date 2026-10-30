"""오늘 원소 하나의 압축 프레임만 여는 제한 메모리 재생기입니다."""
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
from elements import ELEMENTS,daily_element

CACHE_LIMIT=24
FRAME_SIZE=192
FRAME_COUNT=540
FPS=30
PERIOD_SECONDS=18
MAX_ARCHIVE_BYTES=64*1024*1024
MAX_FRAME_BYTES=512*1024


class ElementAssetError(RuntimeError):
    """필수 원소 자산 실패를 숨기지 않고 앱의 시작·표시 오류로 전달합니다."""


def asset_directory():
    return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parents[1]))/'assets/elements3d'


def _number(element):
    number=element if type(element) is int else getattr(element,'number',None)
    if type(number) is not int or not 1<=number<=31:
        raise ElementAssetError('원소 번호는1~31 정수여야 합니다.')
    return number


def _identity(path):
    value=path.stat()
    return value.st_dev,value.st_ino,value.st_size,value.st_mtime_ns


def _object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ElementAssetError('원소 매니페스트 중복 필드: '+key)
        result[key]=value
    return result


class ElementFrames:
    def __init__(self,number,directory=None):
        self.number=_number(number);self.cache=OrderedDict();self.archive=None;self.stream=None
        root=asset_directory() if directory is None else Path(directory)
        self.directory=root/f'{self.number:02d}_{ELEMENTS[self.number-1].symbol}'
        try:self._prepare()
        except Exception as error:
            self.close()
            if isinstance(error,ElementAssetError):raise
            raise ElementAssetError('필수 원소 자산 읽기 실패: '+str(error)) from error

    def _prepare(self):
        manifest=self.directory/'manifest.json';archive=self.directory/'frames.zip'
        if not 0<manifest.stat().st_size<=64*1024:raise ElementAssetError('원소 매니페스트 크기 오류')
        self.manifest=json.loads(manifest.read_text(encoding='utf-8'),object_pairs_hook=_object)
        expected={'schema_version':1,'number':self.number,'symbol':ELEMENTS[self.number-1].symbol,'width':192,'height':192,
                  'fps':30,'period_seconds':18,'frame_count':540,'frame_pattern':'frame_{:04d}.png','archive':'frames.zip'}
        if not isinstance(self.manifest,dict):raise ElementAssetError('원소 매니페스트는 객체여야 합니다.')
        for key,value in expected.items():
            actual=self.manifest.get(key)
            if type(actual) is not type(value) or actual!=value:raise ElementAssetError('원소 계약 불일치: '+key)
        digest=self.manifest.get('archive_sha256')
        if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):raise ElementAssetError('원소 해시 형식 오류')
        if not 0<archive.stat().st_size<=MAX_ARCHIVE_BYTES:raise ElementAssetError('원소 압축파일 크기 초과')
        self.identities=(_identity(manifest),_identity(archive));self.stream=archive.open('rb');hasher=hashlib.sha256()
        while block:=self.stream.read(1024*1024):hasher.update(block)
        if hasher.hexdigest()!=digest:raise ElementAssetError('원소 ZIP 해시 불일치')
        self.stream.seek(0);self.archive=zipfile.ZipFile(self.stream);members=self.archive.infolist()
        if len(members)!=540 or {m.filename for m in members}!={f'frame_{i:04d}.png' for i in range(540)}:
            raise ElementAssetError('원소 ZIP 정확한540프레임 목록 불일치')
        if sum(m.file_size for m in members)>128*1024*1024:raise ElementAssetError('원소 해제 크기 초과')
        for member in members:
            if (member.is_dir() or member.flag_bits&1 or member.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED)
                    or not 0<member.file_size<=MAX_FRAME_BYTES):raise ElementAssetError('원소 ZIP 멤버 형식 오류')
        self.cache[0]=self._decode(0);self._check_unchanged()

    def _check_unchanged(self):
        try:actual=(_identity(self.directory/'manifest.json'),_identity(self.directory/'frames.zip'))
        except OSError as error:raise ElementAssetError('원소 자산 경로가 변경됐습니다.') from error
        if actual!=self.identities:raise ElementAssetError('실행 중 원소 자산이 변경됐습니다.')

    def _decode(self,index):
        try:
            with self.archive.open(f'frame_{index:04d}.png') as stream:data=stream.read(MAX_FRAME_BYTES+1)
            if (len(data)>MAX_FRAME_BYTES or len(data)<33 or data[:8]!=b'\x89PNG\r\n\x1a\n' or data[12:16]!=b'IHDR'
                    or struct.unpack('>II',data[16:24])!=(192,192) or data[24:26]!=bytes((8,6))):raise ElementAssetError('원소 PNG 형식 오류')
            image=QImage.fromData(data,'PNG')
            if image.isNull() or image.size().width()!=192 or image.height()!=192 or not image.hasAlphaChannel():raise ElementAssetError('원소 PNG 디코딩 오류')
            if any(image.pixelColor(x,y).alpha() for x,y in ((0,0),(191,0),(0,191),(191,191))):raise ElementAssetError('원소 PNG 투명 모서리 오류')
            return image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
        except ElementAssetError:raise
        except Exception as error:raise ElementAssetError('원소 프레임 읽기 실패: '+str(error)) from error

    def frame(self,elapsed):
        if isinstance(elapsed,bool) or not isinstance(elapsed,(int,float)) or not math.isfinite(elapsed):raise ElementAssetError('원소 재생 시각은 유한한 숫자여야 합니다.')
        if self.archive is None:raise ElementAssetError('원소 재생기가 닫혔습니다.')
        self._check_unchanged();index=int((elapsed%18)*30)%540
        if index not in self.cache:
            self.cache[index]=self._decode(index)
            while len(self.cache)>CACHE_LIMIT:self.cache.popitem(last=False)
        self.cache.move_to_end(index);return self.cache[index]

    @property
    def cache_bytes(self):return sum(image.sizeInBytes() for image in self.cache.values())

    def close(self):
        if self.archive is not None:self.archive.close();self.archive=None
        if self.stream is not None:self.stream.close();self.stream=None
        self.cache.clear()


_active=None


def close_element_frames():
    global _active
    previous,_active=_active,None
    if previous is not None:previous.close()


def preflight_element_frames(element=None):
    """활성 원소의 해시·목록·첫 프레임을 확인합니다.31개를 적재하지 않습니다."""
    global _active
    number=_number(daily_element() if element is None else element)
    if _active is None or _active.number!=number:
        close_element_frames();_active=ElementFrames(number)
    else:_active._check_unchanged()
    return _active


def get_element_frame(element,elapsed):
    return preflight_element_frames(element).frame(elapsed)


atexit.register(close_element_frames)
