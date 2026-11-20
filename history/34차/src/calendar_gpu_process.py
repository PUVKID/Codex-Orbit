"""한 프레임 공유 슬롯과 취소 가능한 GPU 프로세스 대리 객체입니다."""
from __future__ import annotations
from contextlib import contextmanager
import ctypes
from datetime import date
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import threading
import time
from types import SimpleNamespace
import uuid
from calendar_gpu_windows import kernel, require, UserSecurity, OwnedGpuProcess

PROTOCOL = 1
REQUEST_LIMIT = 65536
RESPONSE_LIMIT = 16384
PIXEL_LIMIT = 2160 * 2160 * 4
HEADER = struct.Struct('<8sI32sQQIIIIII')
HEADER_SIZE = 128
REQUEST_OFFSET = HEADER_SIZE
RESPONSE_OFFSET = REQUEST_OFFSET + REQUEST_LIMIT
PIXEL_OFFSET = RESPONSE_OFFSET + RESPONSE_LIMIT
MAP_SIZE = PIXEL_OFFSET + PIXEL_LIMIT
MAGIC = b'ORBGPU34'


class GpuCancelled(Exception):
    """실제 부모 stop 요청을 관측한 IPC 대기만 구분합니다."""


class GpuProtocolError(RuntimeError):
    pass


def bounded_text(value, limit=4096):
    return str(value).encode('utf-8')[:limit].decode('utf-8', errors='ignore')


def encode_control(value, limit):
    raw = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')
    if len(raw) > limit: raise GpuProtocolError('GPU 제어 payload 크기 상한 초과')
    return raw


def decode_control(raw):
    try:
        value = json.loads(raw.decode('utf-8'), parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
    except (UnicodeError, ValueError, RecursionError) as error:
        raise GpuProtocolError('GPU 제어 JSON 형식 오류') from error
    if not isinstance(value, dict): raise GpuProtocolError('GPU 제어 JSON은 객체여야 합니다.')
    return value


class SharedChannel:
    """한 요청/한 응답 슬롯. native GPU 호출 중에는 mutex를 소유하지 않습니다."""
    def __init__(self, generation, create=False):
        if not isinstance(generation, str) or re.fullmatch('[0-9a-f]{32}', generation) is None:
            raise ValueError('GPU 세대 nonce 형식 오류')
        self.generation = generation; self.k = kernel(); self.handles = {}; self.view = None
        self.closed = False; self.broken = False; self.owner = create; self.last_header = None
        security = UserSecurity(self.k) if create else None
        prefix = 'Local\\CodexOrbitGPU-' + generation
        try:
            sa = ctypes.byref(security.attributes) if security else None
            for name in ('request', 'response', 'stop'):
                handle = (self.k.CreateEventW(sa, True, False, prefix + '-' + name) if create
                          else self.k.OpenEventW(0x00100002, False, prefix + '-' + name))
                require(handle, 'GPU IPC 이벤트 열기 실패: ' + name)
                self.handles[name] = handle
                if create and ctypes.get_last_error() == 183: raise GpuProtocolError('GPU IPC 이름 충돌')
            handle = (self.k.CreateMutexW(sa, False, prefix + '-mutex') if create
                      else self.k.OpenMutexW(0x00100001, False, prefix + '-mutex'))
            require(handle, 'GPU IPC mutex 열기 실패'); self.handles['mutex'] = handle
            if create and ctypes.get_last_error() == 183: raise GpuProtocolError('GPU mutex 이름 충돌')
            handle = (self.k.CreateFileMappingW(ctypes.c_void_p(-1), sa, 4, 0, MAP_SIZE, prefix + '-map') if create
                      else self.k.OpenFileMappingW(6, False, prefix + '-map'))
            require(handle, 'GPU 공유 매핑 열기 실패'); self.handles['map'] = handle
            if create and ctypes.get_last_error() == 183: raise GpuProtocolError('GPU 매핑 이름 충돌')
            self.view = require(self.k.MapViewOfFile(handle, 6, 0, 0, MAP_SIZE), 'GPU 공유 매핑 연결 실패')
            if create: self._write_header(0, 0, 0, 0, 0, 0, 0, 0)
        except BaseException:
            self.close(); raise
        finally:
            if security: security.close()

    def event(self, name, milliseconds=0):
        result = self.k.WaitForSingleObject(self.handles[name], milliseconds)
        if result == 0: return True
        if result == 258: return False
        require(False, 'GPU IPC 이벤트 대기 실패: ' + name)

    def signal(self, name): require(self.k.SetEvent(self.handles[name]), 'GPU IPC 이벤트 설정 실패: ' + name)
    def reset(self, name): require(self.k.ResetEvent(self.handles[name]), 'GPU IPC 이벤트 해제 실패: ' + name)

    @contextmanager
    def locked(self, deadline, cancel=None, *, blocking=True):
        acquired = False
        try:
            if self.broken:raise GpuProtocolError('GPU IPC 세대가 이미 폐기됐습니다.')
            while True:
                if cancel and cancel(): raise GpuCancelled()
                result = self.k.WaitForSingleObject(self.handles['mutex'], 0)
                if result == 0: acquired = True; break
                if result == 128:
                    acquired = True;self.broken=True
                    raise GpuProtocolError('GPU IPC mutex 소유자가 비정상 종료됐습니다.')
                if result != 258: require(False, 'GPU IPC mutex 대기 실패')
                if not blocking:
                    yield False
                    return
                remaining = deadline - time.monotonic()
                if remaining <= 0: raise GpuProtocolError('GPU IPC mutex 대기 제한 초과')
                time.sleep(min(.005, remaining))
            yield True
        finally:
            if acquired: require(self.k.ReleaseMutex(self.handles['mutex']), 'GPU IPC mutex 반환 실패')

    def _write(self, offset, raw): ctypes.memmove(self.view + offset, raw, len(raw))
    def _read(self, offset, size): return ctypes.string_at(self.view + offset, size)

    def _write_header(self, request_id, response_id, request_len, response_len, width, height, stride, pixel_len):
        self._write(0, HEADER.pack(MAGIC, PROTOCOL, self.generation.encode('ascii'), request_id, response_id,
                                  request_len, response_len, width, height, stride, pixel_len))

    def _header(self):
        values = HEADER.unpack(self._read(0, HEADER.size))
        magic, version, generation, req, resp, qlen, rlen, width, height, stride, plen = values
        if magic != MAGIC or version != PROTOCOL or generation != self.generation.encode('ascii'):
            raise GpuProtocolError('GPU 헤더 프로토콜·세대 불일치')
        if qlen > REQUEST_LIMIT or rlen > RESPONSE_LIMIT or plen > PIXEL_LIMIT:
            raise GpuProtocolError('GPU 헤더 payload 길이 상한 초과')
        self.last_header = values
        return req, resp, qlen, rlen, width, height, stride, plen

    def send_request(self, request_id, payload, deadline, cancel):
        raw = encode_control(payload, REQUEST_LIMIT)
        with self.locked(deadline, cancel):
            self._header(); self.reset('response')
            self._write(REQUEST_OFFSET, raw); self._write_header(request_id, 0, len(raw), 0, 0, 0, 0, 0)
        self.signal('request')

    def read_request(self, deadline):
        with self.locked(deadline, lambda: self.event('stop')):
            req, _, qlen, *_ = self._header()
            if req <= 0 or qlen == 0: raise GpuProtocolError('GPU 요청 ID·길이 오류')
            value = decode_control(self._read(REQUEST_OFFSET, qlen)); self.reset('request')
            return req, value

    def respond(self, request_id, meta, pixels=b'', width=0, height=0, deadline=None):
        raw = encode_control(meta, RESPONSE_LIMIT)
        if len(pixels) > PIXEL_LIMIT: raise GpuProtocolError('GPU 응답 픽셀 상한 초과')
        with self.locked(deadline if deadline is not None else time.monotonic() + .25):
            req, _, qlen, *_ = self._header()
            if req != request_id: raise GpuProtocolError('GPU 응답 요청 ID 불일치')
            self._write(RESPONSE_OFFSET, raw)
            if pixels: self._write(PIXEL_OFFSET, pixels)
            self._write_header(req, request_id, qlen, len(raw), width, height, width * 4, len(pixels))
        self.signal('response')

    def read_response(self, request_id, deadline, cancel):
        with self.locked(deadline, cancel):
            req, resp, _, rlen, width, height, stride, plen = self._header()
            if req != request_id or resp != request_id or rlen == 0:
                raise GpuProtocolError('GPU 응답 일련번호 불일치')
            meta = decode_control(self._read(RESPONSE_OFFSET, rlen))
            if meta.get('status') == 'frame':
                if (type(width) is not int or not 32 <= width <= 2160 or width != height
                        or stride != width * 4 or plen != stride * height or meta.get('format') != 'RGBA8888'):
                    raise GpuProtocolError('GPU 영상 크기·stride·픽셀 형식 오류')
            elif plen or width or height or stride:
                raise GpuProtocolError('GPU 상태 응답에 무효 픽셀이 포함됐습니다.')
            pixels = self._read(PIXEL_OFFSET, plen) if plen else b''
            self.reset('response')
            return meta, pixels, width, height

    def read_terminal_error(self, request_id, deadline):
        """중단 직전 확정된 오류 JSON만 한 번 읽고 프레임 바이트는 복사하지 않습니다."""
        if self.closed or time.monotonic()>=deadline:return None
        with self.locked(deadline,blocking=False) as acquired:
            if not acquired:return None
            req,resp,_,length,width,height,stride,pixel_len=self._header()
            if req!=request_id or resp!=request_id or not length:return None
            meta=decode_control(self._read(RESPONSE_OFFSET,length))
            if meta.get('status')!='error':return None
            if width or height or stride or pixel_len:raise GpuProtocolError('GPU 오류 응답에 무효 픽셀이 포함됐습니다.')
            self.reset('response')
            return meta

    def close(self):
        if self.closed: return
        if self.view:
            require(self.k.UnmapViewOfFile(self.view), 'GPU 공유 매핑 회수 실패'); self.view = None
        for name, handle in list(self.handles.items()):
            require(self.k.CloseHandle(handle), 'GPU IPC 핸들 회수 실패: ' + name); del self.handles[name]
        self.closed = True


def source_child_executable():
    """현재 가상환경의 GUI 실행 동료만 사용하고 콘솔 실행으로 조용히 되돌리지 않습니다."""
    companion=Path(sys.executable).resolve().with_name('pythonw.exe')
    if not companion.is_file():
        raise FileNotFoundError('GPU 자식용 같은 실행 환경의 pythonw.exe를 찾을 수 없습니다: '+str(companion))
    return str(companion)


def child_argv(generation, parent_pid):
    args = ['--orbit-gpu-child', str(PROTOCOL), generation, str(parent_pid)]
    if getattr(sys, 'frozen', False): return [str(Path(sys.executable).resolve()), *args]
    return [source_child_executable(), '-B', '-X', 'utf8', str(Path(__file__).with_name('orbit_entry.py').resolve()), *args]


class ProcessCalendarRenderer:
    """동일 자식을 재사용합니다. 생성·렌더·close native 호출은 부모에서 실행하지 않습니다."""
    def __init__(self, size=384, check_cancelled=None, *, command_factory=None):
        if size != (3840, 2160) and not (type(size) is int and 32 <= size <= 768): raise ValueError('GPU 원본 크기 오류')
        self.size = size; self.check_cancelled = check_cancelled; self.command_factory = command_factory or child_argv
        self.ctx = SimpleNamespace(info={}); self.output_size = size if type(size) is int else 384
        self.channel = None; self.owner = None; self.generation = uuid.uuid4().hex
        self.request_id = 0; self.stopping = threading.Event(); self.close_deadline = None
        self.closed = False; self.stage = '생성 전'; self.last_error = ''; self.catalog_context = None
        self.started_at = None; self.first_frame_at = None
        self._thread_id = threading.get_ident()
        self._lifecycle_lock=threading.Lock()

    def _raise_committed_error(self):
        channel=self.channel
        if channel is None or channel.closed or self.request_id<=0:return
        # 같은 종료 기한 안에서 이미 도착한 상태만 확인합니다. 새 요청·프레임 복사·잠금 대기는 없습니다.
        deadline=time.monotonic()+.01
        if self.close_deadline is not None:deadline=min(deadline,self.close_deadline)
        if not channel.event('response'):return
        meta=channel.read_terminal_error(self.request_id,deadline)
        if meta is not None:
            self.stage=meta.get('stage',self.stage)
            self.last_error=bounded_text(meta.get('error','GPU 오류 원문 없음'))
            raise RuntimeError('GPU 자식 '+str(self.stage)+': '+self.last_error)

    def _cancel(self):
        if self.stopping.is_set():
            self._raise_committed_error()
            return True
        if self.check_cancelled:
            try:self.check_cancelled()
            except Exception:
                self._raise_committed_error()
                raise
        return False

    def request_stop(self, deadline=None):
        self.stopping.set()
        # 신호와 마지막 핸들 회수만 직렬화합니다. GPU와 프로세스 대기는 잠금 밖입니다.
        with self._lifecycle_lock:
            if deadline is not None:
                self.close_deadline = min(self.close_deadline, deadline) if self.close_deadline is not None else deadline
            if self.channel is not None and not self.channel.closed:self.channel.signal('stop')

    def _start(self):
        if self.owner is not None: return
        if self._cancel(): raise GpuCancelled()
        self.channel = SharedChannel(self.generation, create=True)
        self.owner = OwnedGpuProcess(); self.started_at = time.monotonic()
        self.owner.start(self.command_factory(self.generation, os.getpid()), Path(__file__).resolve().parent)
        if self.stopping.is_set(): self.channel.signal('stop')
        dimensions = list(self.size) if type(self.size) is tuple else self.size
        self._exchange({'kind': 'initialize', 'size': dimensions, 'parent_pid': os.getpid()})

    def _exchange(self, payload):
        if threading.get_ident() != self._thread_id: raise RuntimeError('GPU 대리 호출은 생성 작업 스레드에서만 허용됩니다.')
        if self._cancel(): raise GpuCancelled()
        deadline = time.monotonic() + 5.0
        self.request_id += 1; request_id = self.request_id
        self.channel.send_request(request_id, payload, deadline, self._cancel)
        while True:
            if self._cancel(): raise GpuCancelled()
            if time.monotonic()>=deadline:raise RuntimeError('GPU 자식 응답 제한 초과: 단계=' + str(self.stage))
            if self.channel.event('response'):
                meta, pixels, width, height = self.channel.read_response(request_id, deadline, self._cancel)
                self.stage = meta.get('stage', self.stage)
                if meta.get('status') == 'busy': continue
                if meta.get('status') == 'error':
                    self.last_error = bounded_text(meta.get('error', 'GPU 오류 원문 없음'))
                    raise RuntimeError('GPU 자식 ' + str(self.stage) + ': ' + self.last_error)
                expected='ready' if payload.get('kind')=='initialize' else 'frame'
                if meta.get('status')!=expected:raise GpuProtocolError('GPU 요청 종류와 응답 상태 불일치')
                if meta.get('identity') != payload.get('identity'): raise GpuProtocolError('GPU 응답 날짜·지역 문맥 불일치')
                if meta.get('catalog_revision') != payload.get('catalog', {}).get('revision'):
                    raise GpuProtocolError('GPU 자식 자료 revision 불일치')
                if meta.get('status') == 'ready':
                    if meta.get('parent_pid') != os.getpid() or type(meta.get('child_pid')) is not int:
                        raise GpuProtocolError('GPU 부모/자식 handshake 불일치')
                self.ctx.info = {'GL_RENDERER': bounded_text(meta.get('renderer', '확인 불가'), 1024)}
                return meta, pixels, width, height
            code = self.owner.poll()
            if code is not None: raise RuntimeError(f'GPU 자식 비정상 종료: code={code}, 단계={self.stage}')
            remaining = deadline - time.monotonic()
            if remaining <= 0: raise RuntimeError('GPU 자식 응답 제한 초과: 단계=' + str(self.stage))
            self.channel.event('response', min(5, max(1, int(remaining * 1000))))

    def set_output_size(self, size):
        if type(size) is not int or not 32 <= size <= 2160: raise ValueError('전달 크기는32~2160 정수여야 합니다.')
        self.output_size = size

    def _catalog(self):
        import city_festivals
        directory = city_festivals._cache_directory
        return {'data_dir': str(directory.parent) if directory is not None else None,
                'revision': city_festivals.get_city_catalog_revision()}

    def _render(self, payload):
        self._start()
        payload['output_size'] = self.output_size; payload['catalog'] = self._catalog()
        meta, raw, width, height = self._exchange(payload)
        if meta['status'] != 'frame' or width != self.output_size: raise GpuProtocolError('GPU 프레임 응답 누락·크기 불일치')
        from PySide6.QtGui import QImage
        # 매핑 수명과 독립된 부모 소유 영상으로 복사합니다. 이전 슬롯을 UI가 참조하지 않습니다.
        image = QImage(raw, width, height, width * 4, QImage.Format.Format_RGBA8888).copy()
        if image.isNull(): raise GpuProtocolError('GPU 프레임 QImage 변환 실패')
        if self.first_frame_at is None: self.first_frame_at = time.monotonic()
        self.catalog_context = meta['catalog_revision']
        return image

    def render(self, value, elapsed=0, country='KR', city_ref=None):
        from calendar_city import normalize_calendar_city
        from calendar_specials import normalize_country
        if type(value) is not date: raise ValueError('GPU 날짜 형식 오류')
        city = normalize_calendar_city(city_ref); country = normalize_country(country)
        identity = {'date': value.isoformat(), 'country': country, 'city': city}
        return self._render({'kind': 'calendar', 'date': value.isoformat(), 'elapsed': elapsed,
                             'country': country, 'city_ref': city, 'identity': identity})

    def render_observatory(self, scene, elapsed=0):
        from observatory_scene import normalize_scene
        return self._render({'kind': 'observatory', 'scene': normalize_scene(scene), 'elapsed': elapsed,
                             'identity': {'mode': 'observatory'}})

    def close(self, deadline=None):
        if self.closed: return True
        deadline = deadline if deadline is not None else self.close_deadline
        if deadline is None: deadline = time.monotonic() + 2.0
        self.request_stop(deadline)
        if self.owner is not None:
            grace = min(deadline, time.monotonic() + .75)
            if not self.owner.wait_empty(grace):
                self.owner.terminate()
                if not self.owner.wait_empty(deadline): return False
            if not self.owner.release(): return False
        with self._lifecycle_lock:
            if self.channel is not None:self.channel.close()
            self.closed=True
        return True

    def status(self):
        return {'generation': self.generation, 'pid': self.owner.pid if self.owner else None,
                'active_processes': self.owner.active_processes() if self.owner else 0,
                'forced': bool(self.owner and self.owner.forced), 'closed': self.closed,
                'stage': self.stage, 'catalog_revision': self.catalog_context,
                'shared_bytes': MAP_SIZE if self.channel is not None and not self.channel.closed else 0,
                'started_at': self.started_at, 'first_frame_at': self.first_frame_at}
