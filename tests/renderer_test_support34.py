"""GPU 자체가 목적이 아닌 개별 fixture의 명시 renderer factory입니다."""
from functools import partial
from unittest.mock import patch
from PySide6.QtGui import QColor, QImage
import calendar_motion as motion


def motion_renderer_factory(factory):
    """서비스 생성 때만 factory를 주입하며 제품 기본값과 전역 Qt helper는 바꾸지 않습니다."""
    return patch.object(motion,'CalendarMotion',partial(motion.CalendarMotion,renderer_factory=factory))


def direct_renderer_factory(size,check_cancelled=None):
    """import/생성 중 stop의 직접 렌더 경계를 유지하는 기존 수명 검사용입니다."""
    from calendar_renderer import CalendarRenderer
    if check_cancelled:check_cancelled()
    return CalendarRenderer(size,check_cancelled=check_cancelled)


class LayoutRenderer:
    """배치·원문·GUI 소유권 fixture에만 사용합니다. 실제 GPU 증거로 세지 않습니다."""
    def __init__(self,size,check_cancelled=None):
        self.ctx=type('Context',(),{'info':{'GL_RENDERER':'개별 배치 fixture'}})()
        self.size=384
    def set_output_size(self,size):self.size=size
    def render(self,value,elapsed,country='KR',city_ref=None):
        image=QImage(self.size,self.size,QImage.Format.Format_RGBA8888)
        image.fill(QColor(40+int(abs(elapsed)*20)%100,80,120,160))
        return image
    def render_observatory(self,scene,elapsed=0):
        from datetime import date
        return self.render(date(2026,11,13),elapsed)
    def close(self):pass
