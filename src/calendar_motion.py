"""한 GPU 작업 스레드와 최대 네 이미지로 날짜별 모션을 공유합니다."""
from __future__ import annotations
import atexit
import logging
import math
import threading
import time
import weakref
from PySide6.QtCore import QCoreApplication, QThread, Qt, QRectF
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen
from calendar_art import current_date, design_for_date

FPS = 30
SIZE = 384
_logger = logging.getLogger(__name__)


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
    def __init__(self):
        super().__init__(); self.condition=threading.Condition(); self.stopping=False; self.visible=False
        self.requested_date=None; self.requested_elapsed=0.; self.requested_at=time.monotonic()
        self.started_at=time.monotonic()
        self.latest=None; self.latest_date=None; self.error=''; self.render_count=0; self.renderer_name=''

    def configure(self,visible=None,value=None,elapsed=None):
        with self.condition:
            if visible is not None:self.visible=visible
            if elapsed is not None:
                self.requested_date=value; self.requested_elapsed=elapsed; self.requested_at=time.monotonic()
            self.condition.notify_all()

    def stop(self):
        with self.condition:self.stopping=True; self.condition.notify_all()

    def run(self):
        renderer=None
        next_frame_at=0.
        try:
            while True:
                with self.condition:
                    # 여러 위젯의 요청 알림이 와도 렌더 속도는 초당30회를 넘지 않습니다.
                    while not self.stopping:
                        remaining=next_frame_at-time.monotonic()
                        if self.visible and remaining<=0:break
                        self.condition.wait(remaining if self.visible else None)
                    if self.stopping:break
                    value=self.requested_date or current_date()
                    # 각 호출자의 서로 다른 타이머 원점 대신 서비스의 한 시계를 공유합니다.
                    elapsed=time.monotonic()-self.started_at
                start=time.monotonic()
                if renderer is None:
                    from calendar_renderer import CalendarRenderer
                    renderer=CalendarRenderer(SIZE); self.renderer_name=renderer.ctx.info.get('GL_RENDERER','확인 불가')
                image=renderer.render(value,elapsed)
                with self.condition:
                    self.latest=image; self.latest_date=value; self.render_count+=1
                    next_frame_at=start+1/FPS
                    self.condition.notify_all()
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


class CalendarMotion:
    def __init__(self):
        self.worker=_Worker(); self.owners={}; self.fallback=None; self.fallback_date=None; self.closed=False
        self.worker.start()

    def visible(self,owner,visible):
        if self.closed:raise RuntimeError('날짜별 모션 서비스가 닫혔습니다.')
        key=id(owner)
        if visible:
            def gone(_):
                self.owners.pop(key,None); self.worker.configure(visible=bool(self.owners))
            self.owners[key]=weakref.ref(owner,gone)
        else:self.owners.pop(key,None)
        self.worker.configure(visible=bool(self.owners))

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
        self.closed=True; self.owners.clear(); self.worker.stop()
        finished=self.worker.wait(2000)
        if finished:
            with self.worker.condition:self.worker.latest=None
            self.fallback=None
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
                'renderer':_service.worker.renderer_name,'error':_service.worker.error}


def close_calendar_motion():
    global _service,_retiring
    if _service is not None:
        value,_service=_service,None
        if not value.close():
            _retiring=value
            _logger.error('GPU 스레드가 2초 이내 종료되지 않아 참조를 보존합니다. 새 컨텍스트는 시작하지 않습니다.')


atexit.register(close_calendar_motion)
