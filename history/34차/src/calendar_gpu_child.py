"""GPU 내부 진입점입니다. GUI·계정·설정·네트워크를 시작하지 않습니다."""
from __future__ import annotations
import ctypes
from datetime import date
import math
import os
from pathlib import Path
import re
import sys
import time
from calendar_gpu_process import SharedChannel, PROTOCOL, GpuCancelled, GpuProtocolError, bounded_text
from calendar_gpu_windows import require


def _renderer_factory(size, check_cancelled=None):
    # 무거운 native import는 이 전용 프로세스의 렌더 실행 스레드 한 곳에서만 수행합니다.
    from calendar_renderer import CalendarRenderer
    if check_cancelled: check_cancelled()
    return CalendarRenderer(size, check_cancelled=check_cancelled)


def _catalog(payload, previous):
    import city_festivals
    from calendar_art import design_for_date
    if not isinstance(payload, dict) or set(payload) != {'data_dir', 'revision'}:
        raise GpuProtocolError('GPU 자료 문맥 형식 오류')
    directory, revision = payload['data_dir'], payload['revision']
    if not isinstance(revision, str) or re.fullmatch('[0-9a-f]{64}', revision) is None:
        raise GpuProtocolError('GPU 자료 revision 형식 오류')
    if directory is not None and (not isinstance(directory, str) or len(directory) > 4096 or not Path(directory).is_absolute()):
        raise GpuProtocolError('GPU 자료 캐시 경로 형식 오류')
    if previous != payload:
        city_festivals.configure_city_cache(directory)
        design_for_date.cache_clear()
        if city_festivals.get_city_catalog_revision() != revision:
            raise GpuProtocolError('GPU 자식의 실제 자료 revision이 부모와 다릅니다.')
    return dict(payload)


def serve(channel, parent_pid, renderer_factory=_renderer_factory):
    """정규 요청만 실행하며 GPU native 호출 전후에는 공유 mutex를 보유하지 않습니다."""
    k = channel.k
    parent = require(k.OpenProcess(0x00100000, False, parent_pid), 'GPU 부모 수명 핸들 열기 실패')
    renderer = None; last_id = 0; catalog = None; stage = '생성 전'; exit_code = 0
    def stopped():
        return channel.event('stop') or k.WaitForSingleObject(parent, 0) == 0
    def check():
        if stopped(): raise GpuCancelled()
    def progress(value):
        nonlocal stage
        stage = value
        channel.respond(last_id, {'status': 'busy', 'stage': stage})
    try:
        check()
        while not stopped():
            if not channel.event('request', 5): continue
            request_id, payload = channel.read_request(time.monotonic() + .25)
            if request_id != last_id + 1: raise GpuProtocolError('GPU 요청 일련번호가 연속되지 않습니다.')
            last_id = request_id
            kind = payload.get('kind')
            if renderer is None:
                if kind != 'initialize' or set(payload) != {'kind', 'size', 'parent_pid'} or payload['parent_pid'] != parent_pid:
                    raise GpuProtocolError('GPU 최초 handshake 요청 오류')
                size = payload['size']
                if isinstance(size, list): size = tuple(size)
                progress('가져오기·생성')
                renderer = renderer_factory(size, check_cancelled=check)
                check()
                channel.respond(last_id, {'status': 'ready', 'stage': '준비', 'identity': None,
                    'catalog_revision': None, 'parent_pid': parent_pid, 'child_pid': os.getpid(),
                    'renderer': bounded_text(renderer.ctx.info.get('GL_RENDERER', '확인 불가'), 1024)})
                continue
            if kind not in ('calendar', 'observatory'): raise GpuProtocolError('GPU 요청 종류 오류')
            expected = ({'kind', 'date', 'elapsed', 'country', 'city_ref', 'identity', 'output_size', 'catalog'}
                        if kind == 'calendar' else {'kind', 'scene', 'elapsed', 'identity', 'output_size', 'catalog'})
            if set(payload) != expected: raise GpuProtocolError('GPU 요청 필드 오류')
            elapsed = payload['elapsed']
            if type(elapsed) not in (int, float): raise GpuProtocolError('GPU 모션 시각 형식 오류')
            try: finite = math.isfinite(elapsed)
            except OverflowError: finite = False
            if not finite: raise GpuProtocolError('GPU 모션 시각은 유한해야 합니다.')
            size = payload['output_size']
            if type(size) is not int or not 32 <= size <= 2160: raise GpuProtocolError('GPU 전달 크기 오류')
            catalog = _catalog(payload['catalog'], catalog)
            check(); progress('렌더'); renderer.set_output_size(size)
            if kind == 'calendar':
                from calendar_city import normalize_calendar_city
                from calendar_specials import normalize_country
                value = date.fromisoformat(payload['date']); country = normalize_country(payload['country'])
                city = normalize_calendar_city(payload['city_ref'])
                identity = {'date': value.isoformat(), 'country': country, 'city': city}
                if payload['identity'] != identity: raise GpuProtocolError('GPU 요청 날짜·지역 문맥 오류')
                image = renderer.render(value, elapsed, country=country, city_ref=city)
            else:
                from observatory_scene import normalize_scene
                if payload['identity'] != {'mode': 'observatory'}: raise GpuProtocolError('GPU 관측소 문맥 오류')
                image = renderer.render_observatory(normalize_scene(payload['scene']), elapsed)
            if image.isNull(): raise GpuProtocolError('GPU 렌더가 빈 영상을 반환했습니다.')
            check(); progress('출력 복사')
            from PySide6.QtGui import QImage
            image = image.convertToFormat(QImage.Format.Format_RGBA8888)
            if image.isNull() or image.width() != size or image.height() != size or image.bytesPerLine() != size * 4:
                raise GpuProtocolError('GPU 반환 영상 크기·stride 오류')
            raw = bytes(image.constBits())
            check()
            channel.respond(last_id, {'status': 'frame', 'stage': '프레임', 'format': 'RGBA8888',
                'identity': payload['identity'], 'catalog_revision': catalog['revision'],
                'renderer': bounded_text(renderer.ctx.info.get('GL_RENDERER', '확인 불가'), 1024)}, raw, size, size)
    except GpuCancelled:
        pass
    except Exception as error:
        exit_code = 2
        if last_id:
            try: channel.respond(last_id, {'status': 'error', 'stage': stage,
                                          'error': bounded_text(type(error).__name__ + ': ' + str(error))})
            except Exception: pass
    finally:
        if renderer is not None:
            try:
                if last_id and exit_code==0: progress('정리')
                renderer.close()
            except Exception as error:
                exit_code = 3
                if last_id:
                    try: channel.respond(last_id, {'status': 'error', 'stage': '정리',
                        'error': bounded_text(type(error).__name__ + ': ' + str(error))})
                    except Exception: pass
        require(k.CloseHandle(parent), 'GPU 부모 수명 핸들 회수 실패')
    return exit_code


def main(arguments):
    if len(arguments) != 3 or arguments[0] != str(PROTOCOL): raise ValueError('GPU 내부 프로토콜 인자 오류')
    generation = arguments[1]
    if re.fullmatch('[0-9a-f]{32}', generation) is None: raise ValueError('GPU 세대 인자 오류')
    if re.fullmatch('[1-9][0-9]{0,9}', arguments[2]) is None: raise ValueError('GPU 부모 PID 인자 오류')
    parent_pid = int(arguments[2])
    if parent_pid == os.getpid() or parent_pid > 0xFFFFFFFF: raise ValueError('GPU 부모 PID 범위 오류')
    channel = SharedChannel(generation)
    try: return serve(channel, parent_pid)
    finally: channel.close()
