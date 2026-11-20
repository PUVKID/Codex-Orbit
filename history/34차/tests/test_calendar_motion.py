"""실제 GPU와 분리한 제어 렌더러로 공유·상한·자정·실패·종료를 검사합니다."""
from datetime import date
import gc
import math
from pathlib import Path
import sys
import threading
import subprocess
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtGui import QImage,QColor
from PySide6.QtWidgets import QApplication
import calendar_motion as motion
from renderer_test_support34 import motion_renderer_factory


class Owner:pass


class FakeRenderer:
    instances=[]
    def __init__(self,size,check_cancelled=None):
        self.thread=threading.get_ident(); self.closed=False; self.times=[]
        self.ctx=type('Context',(),{'info':{'GL_RENDERER':'제어검사용'}})(); self.instances.append(self)
    def render(self,value,elapsed,country='KR'):
        if threading.get_ident()!=self.thread:raise RuntimeError('스레드 소유권 위반')
        self.times.append(elapsed)
        image=QImage(384,384,QImage.Format.Format_ARGB32_Premultiplied); image.fill(QColor(value.month*15,value.day*7,120,255)); return image
    def close(self):
        if threading.get_ident()!=self.thread:raise RuntimeError('종료 스레드 위반')
        self.closed=True


class CalendarMotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        motion.close_calendar_motion(); FakeRenderer.instances=[]
        self.patch=motion_renderer_factory(FakeRenderer); self.patch.start()

    def tearDown(self):motion.close_calendar_motion(); self.patch.stop()

    def wait_for(self,predicate):
        deadline=time.monotonic()+1
        while time.monotonic()<deadline:
            if predicate():return
            time.sleep(.005)
        self.fail('1초 안에 제어 조건이 충족되지 않았습니다.')

    def test_shared_context_throttle_pause_and_close(self):
        first,second=Owner(),Owner(); motion.set_calendar_motion_visible(first,True); motion.set_calendar_motion_visible(second,True)
        self.wait_for(lambda:motion.calendar_motion_status().get('render_count',0)>0)
        initial=motion.calendar_motion_status()['render_count']; start=time.monotonic()
        while time.monotonic()-start<.15:
            motion.get_calendar_frame(0 if int(time.monotonic()*1000)%2 else 10000); time.sleep(.001)
        # 초당30회였던 상한6은 사용자 요청의240Hz 실제 측정 구간으로 정합합니다.
        duration=time.monotonic()-start
        status=motion.calendar_motion_status(); self.assertLessEqual(status['render_count']-initial,math.ceil(duration*motion.FPS)+2)
        self.assertEqual(len(FakeRenderer.instances),1); self.assertLessEqual(status['images'],4)
        renderer=FakeRenderer.instances[0]; self.assertNotEqual(renderer.thread,threading.get_ident())
        self.assertEqual(renderer.times,sorted(renderer.times)); self.assertLess(renderer.times[-1]-renderer.times[0],1)
        motion.set_calendar_motion_visible(first,False); motion.set_calendar_motion_visible(second,False)
        time.sleep(.04); paused=motion.calendar_motion_status()['render_count']; time.sleep(.05)
        self.assertEqual(paused,motion.calendar_motion_status()['render_count'])
        motion.close_calendar_motion(); self.assertTrue(renderer.closed); self.assertFalse(motion.calendar_motion_status()['running'])

    def test_midnight_explicit_date_and_owner_collection(self):
        now=[date(2028,2,28)]; owner=Owner()
        with patch.object(motion,'current_date',side_effect=lambda:now[0]):
            motion.set_calendar_motion_visible(owner,True); motion.get_calendar_frame()
            self.wait_for(lambda:motion.calendar_motion_status().get('date')=='2028-02-28')
            now[0]=date(2028,2,29)
            self.wait_for(lambda:motion.calendar_motion_status().get('date')=='2028-02-29')
            image=motion.get_calendar_frame(); self.assertEqual(image.pixelColor(100,100).green(),203)
            motion.get_calendar_frame(date=date(2099,12,31))
            self.wait_for(lambda:motion.calendar_motion_status().get('date')=='2099-12-31')
            del owner; gc.collect(); self.assertEqual(motion.calendar_motion_status()['owners'],0)

    def test_failure_is_visible_and_static_fallback_is_not_null(self):
        self.patch.stop()
        def fail_renderer(*args,**kwargs):raise RuntimeError('제어된 GPU 불가')
        self.patch=motion_renderer_factory(fail_renderer); self.patch.start()
        owner=Owner()
        with self.assertLogs('calendar_motion',level='ERROR') as messages:
            motion.set_calendar_motion_visible(owner,True)
            self.wait_for(lambda:bool(motion.get_calendar_error()) and not motion.calendar_motion_status()['running'])
            image=motion.get_calendar_frame(date=date(2026,4,1))
            self.assertFalse(image.isNull()); self.assertIn('제어된 GPU 불가',motion.get_calendar_error())
            self.assertEqual(image.pixelColor(0,0).alpha(),0)
            self.assertEqual(len(messages.output),1)

    def test_bad_time_and_date_are_explicit(self):
        for elapsed in (True,None,float('nan'),float('inf'),10**400):
            with self.assertRaises(ValueError):motion.get_calendar_frame(elapsed)
        with self.assertRaises(ValueError):motion.get_calendar_frame(date=date(2100,1,1))

    def test_country_change_while_paused_refreshes_same_date(self):
        owner=Owner()
        motion.set_calendar_motion_options(paused=True)
        motion.set_calendar_motion_visible(owner,True)
        motion.get_calendar_frame(date=date(2026,10,9))
        self.wait_for(lambda:motion.calendar_motion_status().get('rendered_country')=='KR')
        before=motion.calendar_motion_status()['render_count']
        motion.set_calendar_country('US')
        self.wait_for(lambda:motion.calendar_motion_status().get('rendered_country')=='US')
        self.assertGreater(motion.calendar_motion_status()['render_count'],before)
        self.assertEqual(motion.calendar_motion_status()['date'],'2026-10-09')
        time.sleep(.04)
        stable=motion.calendar_motion_status()['render_count'];time.sleep(.04)
        self.assertEqual(motion.calendar_motion_status()['render_count'],stable)
        motion.close_calendar_motion()
        self.assertTrue(FakeRenderer.instances[-1].closed)
        self.assertIsNone(motion._retiring)

    def test_city_midnight_and_offset_change_refresh_paused_worker(self):
        owner=Owner();now=[date(2026,12,24)]
        with patch.object(motion,'current_date',side_effect=lambda offset=None:now[0] if offset==-28800 else date(2026,12,25)):
            motion.set_calendar_motion_options(paused=True)
            motion.set_calendar_utc_offset(-28800)
            motion.set_calendar_motion_visible(owner,True)
            motion.get_calendar_frame()
            self.wait_for(lambda:motion.calendar_motion_status().get('date')=='2026-12-24')
            self.assertEqual(motion.get_calendar_date(),date(2026,12,24))
            now[0]=date(2026,12,25)
            # 제어 시계의 날짜 변경을 알리고 기존 정지 루프가 한 프레임을 갱신하는지 확인합니다.
            with motion._service.worker.condition:motion._service.worker.condition.notify_all()
            self.wait_for(lambda:motion.calendar_motion_status().get('date')=='2026-12-25')
            before=motion.calendar_motion_status()['render_count']
            motion.set_calendar_utc_offset(None)
            self.wait_for(lambda:motion.calendar_motion_status().get('rendered_utc_offset_seconds') is None)
            self.assertGreater(motion.calendar_motion_status()['render_count'],before)
        motion.close_calendar_motion();self.assertIsNone(motion._retiring)

    def test_main_thread_and_missing_application_guards(self):
        errors=[]
        def request():
            try:motion.get_calendar_frame()
            except RuntimeError as error:errors.append(str(error))
        thread=threading.Thread(target=request); thread.start(); thread.join(1)
        self.assertFalse(thread.is_alive()); self.assertEqual(len(errors),1); self.assertIn('메인 스레드',errors[0])
        source="import sys;sys.path.insert(0,'src');import calendar_motion as m\ntry:m.get_calendar_frame()\nexcept RuntimeError as e:print(str(e))\nelse:raise AssertionError('QApplication 없이 허용됨')"
        result=subprocess.run([sys.executable,'-B','-X','utf8','-c',source],cwd=Path(__file__).resolve().parents[1],capture_output=True,timeout=3)
        self.assertEqual(result.returncode,0,result.stderr.decode('utf-8')); self.assertIn('메인 스레드',result.stdout.decode('utf-8'))


if __name__=='__main__':unittest.main()
