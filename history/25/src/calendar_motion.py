"""한 GPU 작업 스레드와 최대 네 이미지로 날짜별 모션을 공유합니다."""
from __future__ import annotations
import atexit
import logging
import math
import threading
import time
import weakref
from PySide6.QtCore import QCoreApplication, QObject, QThread, Qt, QRectF, Signal, Slot
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen
from shiboken6 import isValid
from calendar_art import current_date, design_for_date
from frame_pacing import FrameWaiter

FPS = 240
SIZE = 384
RENDER_SIZE = (3840, 2160)
_logger = logging.getLogger(__name__)


def next_frame_deadline(previous, now):
    """절대 시간 슬롯을 유지하며 놓친 슬롯은 한 번에 건너뜁니다."""
    interval=1/FPS
    following=previous+interval
    if following<=now:
        following+=(math.floor((now-following)/interval)+1)*interval
    return following


def fallback_image(value):
    """GPU 준비·실패 때만 쓰는 월 주제의 정적 평면 표식입니다. 3D 성공으로 가장하지 않습니다."""
    design=design_for_date(value); month=value.month
    image=QImage(SIZE,SIZE,QImage.Format.Format_ARGB32_Premultiplied); image.fill(Qt.GlobalColor.transparent)
    painter=QPainter(image); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.translate(SIZE/2,SIZE/2); painter.scale(3,3)
    painter.setPen(QPen(QColor(design.accent),1.5)); painter.setBrush(QColor(design.accent))
    path=QPainterPath()
    if month in (1,3,6,12):
        count={1:6,3:4,6:5,12:6}[month]
        for index in range(count):
            painter.save(); painter.rotate(360*index/count)
            if month==12:
                painter.drawLine(0,0,0,-34); painter.drawLine(0,-22,-8,-29); painter.drawLine(0,-22,8,-29)
            else:painter.drawEllipse(QRectF(-7,-33,14,27))
            painter.restore()
        painter.drawEllipse(QRectF(-7,-7,14,14))
    elif month==2:
        path.moveTo(0,-35); path.lineTo(26,-8); path.lineTo(17,22); path.lineTo(0,35); path.lineTo(-24,4); path.closeSubpath(); painter.drawPath(path)
    elif month in (4,8):
        path.moveTo(0,-36); path.cubicTo(9,-15,29,-4,23,18); path.cubicTo(17,40,-26,33,-23,10); path.cubicTo(-22,-4,-5,-20,0,-36)
        painter.drawPath(path)
    elif month in (5,10):
        for index in range(3):painter.drawEllipse(QRectF(-22+index*7,-33+index*11,34,24))
        painter.drawLine(0,0,0,35)
    elif month==7:
        painter.drawEllipse(QRectF(-23,-23,46,46)); painter.setBrush(Qt.BrushStyle.NoBrush); painter.rotate(-22); painter.drawEllipse(QRectF(-38,-10,76,20))
    elif month==9:
        painter.drawEllipse(QRectF(-28,12,19,12)); painter.drawEllipse(QRectF(10,3,19,12)); painter.drawLine(-10,17,-10,-28); painter.drawLine(28,8,28,-34); painter.drawLine(-10,-28,28,-34)
    else:
        for index,height in enumerate((33,62,45)):painter.drawRoundedRect(QRectF(-29+index*21,30-height,16,height),3,3)
    painter.end(); return image


class _Worker(QThread):
    """Qt 객체나 UI를 조작하지 않고 복사된 최신 이미지 하나만 전달합니다."""
    frame_ready=Signal()

    def __init__(self):
        super().__init__(); self.condition=threading.Condition(); self.stopping=False; self.visible=False
        self.requested_date=None; self.requested_elapsed=0.; self.requested_at=time.perf_counter()
        self.started_at=time.perf_counter()
        self.latest=None; self.latest_date=None; self.error=''; self.render_count=0; self.renderer_name=''
        self.output_size=SIZE; self.notification_pending=False; self.notification_count=0
        self.first_render_at=None; self.last_render_at=None; self.render_seconds=0.
        self.pacing_backend='준비 중'; self.pacing_warning=''

    def configure(self,visible=None,value=None,elapsed=None,output_size=None):
        with self.condition:
            if visible is not None:self.visible=visible
            if output_size is not None:self.output_size=output_size
            if elapsed is not None:
                self.requested_date=value; self.requested_elapsed=elapsed; self.requested_at=time.perf_counter()
            self.condition.notify_all()

    def stop(self):
        with self.condition:self.stopping=True; self.condition.notify_all()

    def run(self):
        renderer=None
        waiter=None
        next_frame_at=0.
        try:
            waiter=FrameWaiter(); self.pacing_backend=waiter.backend; self.pacing_warning=waiter.warning
            if waiter.warning:_logger.warning(waiter.warning)
            while True:
                with self.condition:
                    # 요청 수와 무관하게 절대240Hz 슬롯에 맞춰 유휴 대기합니다.
                    while not self.stopping and not self.visible:self.condition.wait()
                    if self.stopping:break
                    remaining=next_frame_at-time.perf_counter()
                if remaining>0:
                    waiter.wait(remaining,self.condition)
                    continue
                with self.condition:
                    if self.stopping:break
                    if not self.visible:continue
                    value=self.requested_date or current_date()
                    # 각 호출자의 서로 다른 타이머 원점 대신 서비스의 한 시계를 공유합니다.
                    elapsed=time.perf_counter()-self.started_at
                    output_size=self.output_size
                start=time.perf_counter()
                if renderer is None:
                    from calendar_renderer import CalendarRenderer
                    renderer=CalendarRenderer(RENDER_SIZE); self.renderer_name=renderer.ctx.info.get('GL_RENDERER','확인 불가')
                if hasattr(renderer,'set_output_size'):renderer.set_output_size(output_size)
                image=renderer.render(value,elapsed)
                finished=time.perf_counter()
                with self.condition:
                    self.render_count+=1; image.setText('calendar_frame_id',str(self.render_count))
                    self.latest=image; self.latest_date=value
                    if self.first_render_at is None:self.first_render_at=finished
                    self.last_render_at=finished; self.render_seconds+=finished-start
                    next_frame_at=next_frame_deadline(next_frame_at if next_frame_at else start,finished)
                    notify=not self.notification_pending and self.visible
                    if notify:self.notification_pending=True; self.notification_count+=1
                    self.condition.notify_all()
                if notify:self.frame_ready.emit()
        except Exception as error:
            with self.condition:
                self.error=f'날짜별 3D 표시 실패: {type(error).__name__}: {error}'
                self.condition.notify_all()
            _logger.exception('날짜별 3D 렌더가 중단되어 정적 월 표식을 표시합니다.')
        finally:
            if renderer is not None:
                try:renderer.close()
                except Exception:
                    _logger.exception('날짜별 GPU 자원 정리 실패')
            if waiter is not None:
                try:waiter.close()
                except Exception as error:
                    with self.condition:self.error=self.error or f'프레임 대기 핸들 정리 실패: {type(error).__name__}: {error}'
                    _logger.exception('프레임 대기 핸들 정리 실패')


class CalendarMotion(QObject):
    def __init__(self):
        super().__init__(QCoreApplication.instance())
        self.worker=_Worker(); self.owners={}; self.sizes={}; self.presented={}
        self.presentation_count=0; self.dispatch_count=0
        self.fallback=None; self.fallback_date=None; self.closed=False
        self.worker.frame_ready.connect(self._dispatch_frame,Qt.ConnectionType.QueuedConnection)
        self.worker.start()

    @Slot()
    def _dispatch_frame(self):
        if self.closed:return
        with self.worker.condition:self.worker.notification_pending=False
        self.dispatch_count+=1
        for reference in list(self.owners.values()):
            owner=reference()
            if owner is None or (isinstance(owner,QObject) and not isValid(owner)):continue
            callback=getattr(owner,'calendar_frame_ready',None)
            if callable(callback):callback()

    def _configure_size(self):
        self.worker.configure(output_size=max((self.sizes.get(key,SIZE) for key in self.owners),default=SIZE))

    def visible(self,owner,visible):
        if self.closed:raise RuntimeError('날짜별 모션 서비스가 닫혔습니다.')
        key=id(owner)
        if visible:
            def gone(_):
                self.owners.pop(key,None); self.sizes.pop(key,None); self.presented.pop(key,None)
                self.worker.configure(visible=bool(self.owners)); self._configure_size()
            self.owners[key]=weakref.ref(owner,gone)
        else:
            self.owners.pop(key,None); self.sizes.pop(key,None); self.presented.pop(key,None)
        self.worker.configure(visible=bool(self.owners))
        self._configure_size()

    def frame(self,elapsed=0.0,value=None):
        if self.closed:raise RuntimeError('날짜별 모션 서비스가 닫혔습니다.')
        if type(elapsed) not in (int,float):raise ValueError('재생 시각은 유한한 숫자여야 합니다.')
        try:valid=math.isfinite(elapsed)
        except OverflowError:valid=False
        if not valid:raise ValueError('재생 시각은 유한한 숫자여야 합니다.')
        actual=current_date() if value is None else value; design_for_date(actual)
        self.worker.configure(value=value,elapsed=elapsed)
        with self.worker.condition:
            image=self.worker.latest if self.worker.latest_date==actual else None
        if image is not None:return QImage(image)
        if self.fallback_date!=actual:
            self.fallback=fallback_image(actual); self.fallback_date=actual
        return QImage(self.fallback)

    def close(self):
        self.closed=True; self.owners.clear(); self.sizes.clear(); self.presented.clear(); self.worker.stop()
        finished=self.worker.wait(2000)
        if finished:
            with self.worker.condition:self.worker.latest=None
            self.fallback=None
            self.deleteLater()
        return finished


_service=None
_retiring=None
_quit_connected=False


def _main_thread():
    app=QCoreApplication.instance()
    if app is None or QThread.currentThread()!=app.thread():raise RuntimeError('날짜별 모션 API는 Qt 메인 스레드에서 호출해야 합니다.')


def _get_service():
    global _service,_retiring,_quit_connected
    _main_thread()
    if not _quit_connected:
        QCoreApplication.instance().aboutToQuit.connect(close_calendar_motion)
        _quit_connected=True
    if _retiring is not None:
        if _retiring.worker.isRunning():raise RuntimeError('이전 GPU 작업 스레드가 종료 중입니다.')
        _retiring=None
    if _service is None:
        _service=CalendarMotion()
    return _service


def get_calendar_frame(elapsed=0.0,date=None):
    return _get_service().frame(elapsed,date)


def prepare_calendar_motion(timeout_seconds=5.0):
    """창 표시 전에 같은 작업자의 첫 실제 프레임을 최대 5초 준비합니다."""
    if type(timeout_seconds) not in (int,float) or not 0 < timeout_seconds <= 5:
        raise ValueError('3D 준비 제한은 0초 초과 5초 이하여야 합니다.')
    service=_get_service();worker=service.worker;value=current_date()
    deadline=time.monotonic()+timeout_seconds
    with worker.condition:
        previous_date=worker.requested_date
        worker.requested_date=value;worker.visible=True;worker.condition.notify_all()
        try:
            while worker.latest_date!=value and not worker.error and not worker.stopping:
                remaining=deadline-time.monotonic()
                if remaining<=0:break
                worker.condition.wait(remaining)
            ready=worker.latest_date==value and worker.latest is not None and not worker.error
            error=worker.error or ('' if ready else '날짜별 3D 첫 프레임이 준비 제한 안에 도착하지 않았습니다.')
            result={'ready':ready,'error':error,'renderer':worker.renderer_name,
                    'render_count':worker.render_count,'date':str(worker.latest_date)}
        finally:
            worker.requested_date=previous_date
            worker.visible=bool(service.owners);worker.condition.notify_all()
    if not ready and not worker.error:_logger.error(error)
    return result


def set_calendar_motion_visible(owner,visible):
    if type(visible) is not bool:raise TypeError('표시 상태는 bool이어야 합니다.')
    _get_service().visible(owner,visible)


def set_calendar_motion_size(owner,size):
    """현재 보이는 각 소유자의 실제 픽셀 요구 중 최대 크기만 전달합니다."""
    if type(size) is not int or not 32<=size<=2160:raise ValueError('전달 크기는32~2160 정수여야 합니다.')
    service=_get_service()
    if id(owner) in service.owners:
        service.sizes[id(owner)]=size; service._configure_size()


def record_calendar_presentation(owner,image):
    """Qt 그리기 경로가 실제로 소비한 서로 다른 프레임만 셉니다."""
    _main_thread()
    if _service is None or id(owner) not in _service.owners:return
    serial=image.text('calendar_frame_id')
    if serial and _service.presented.get(id(owner))!=serial:
        _service.presented[id(owner)]=serial; _service.presentation_count+=1


def get_calendar_error():
    """제품은 이 문자열을 상태나 툴팁에 표시해 대체 표식과 실제 3D를 구분할 수 있습니다."""
    if _retiring is not None:return 'GPU 작업 스레드 종료를 기다리는 중입니다.'
    if _service is None:return ''
    with _service.worker.condition:return _service.worker.error


def calendar_motion_status():
    if _service is None:return {'running':False,'owners':0,'images':0,'error':get_calendar_error()}
    with _service.worker.condition:
        return {'running':_service.worker.isRunning(),'owners':len(_service.owners),
                'images':int(_service.worker.latest is not None)+int(_service.fallback is not None),
                'render_count':_service.worker.render_count,'date':str(_service.worker.latest_date),
                'target_fps':FPS,'source_dimensions':list(RENDER_SIZE),
                'delivery_dimensions':list(_service.worker.latest.size().toTuple()) if _service.worker.latest is not None else None,
                'requested_delivery_size':_service.worker.output_size,
                'notification_count':_service.worker.notification_count,'dispatch_count':_service.dispatch_count,
                'presentation_count':_service.presentation_count,
                'render_seconds':_service.worker.render_seconds,
                'pacing_clock':'perf_counter','pacing_backend':_service.worker.pacing_backend,
                'pacing_warning':_service.worker.pacing_warning,
                'first_render_at':_service.worker.first_render_at,'last_render_at':_service.worker.last_render_at,
                'renderer':_service.worker.renderer_name,'error':_service.worker.error}


def close_calendar_motion():
    global _service,_retiring
    if _service is not None:
        value,_service=_service,None
        if not value.close():
            _retiring=value
            _logger.error('GPU 스레드가 2초 이내 종료되지 않아 참조를 보존합니다. 새 컨텍스트는 시작하지 않습니다.')


atexit.register(close_calendar_motion)
