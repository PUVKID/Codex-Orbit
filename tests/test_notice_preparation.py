"""동일 알림의 재측정 생략과 창 표시 전 공유 GPU 준비 경계를 검사합니다."""
import cProfile
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtCore import QRect, QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication
from app import Notice
from theme import apply_theme
from typography import app_font
import calendar_motion as motion
from test_calendar_motion import FakeRenderer, Owner


class NoticePreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        apply_theme();cls.app.setFont(app_font())

    def tearDown(self):
        motion.close_calendar_motion()
        QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)

    def measured_adjusts(self,notice,rect):
        profile=cProfile.Profile();profile.enable()
        notice.fit_content(rect)
        profile.disable()
        return sum(entry.callcount for entry in profile.getstats() if isinstance(entry.code,str) and 'adjustSize' in entry.code)

    def test_same_content_and_same_queue_height_do_not_measure_again(self):
        notice=Notice(lambda:None)
        try:
            notice.available_rect=QRect(0,0,1000,900)
            notice.update_event({'id':'one','chat_name':'같은 제목','after':{'model':'m','effort':'high'}},False)
            notice.queue_hint.setText('알림 표시 1건 · 새 변경은 즉시 표시')
            notice.fit_content(notice.available_rect)
            self.assertEqual(self.measured_adjusts(notice,notice.available_rect),0)
            notice.queue_hint.setText('알림 표시 2건 · 새 변경은 즉시 표시')
            self.assertEqual(self.measured_adjusts(notice,notice.available_rect),0)
            notice.text.setText('다른 이유가 뒤늦게 도착했습니다. '*20)
            self.assertGreater(self.measured_adjusts(notice,notice.available_rect),0)
        finally:notice.deleteLater()

    def test_queue_height_only_updates_size_without_resetting_title(self):
        notice=Notice(lambda:None)
        try:
            notice.available_rect=QRect(0,0,1000,900)
            notice.update_event({'id':'one','chat_name':'같은 제목','after':{'model':'m'}},False)
            notice.queue_hint.setText('알림 표시 8건 · 새 변경은 즉시 표시')
            notice.fit_content();before=notice.height()
            notice.queue_hint.setText('알림 표시 8건 · 새 변경은 즉시 표시 · 표시 상한으로 숨긴 1건은 변경 이력에서 확인하세요.')
            profile=cProfile.Profile();profile.enable();notice.fit_content();profile.disable()
            resets=sum(e.callcount for e in profile.getstats() if isinstance(e.code,str) and ('setText' in e.code or 'setContentsMargins' in e.code))
            self.assertEqual(resets,0)
            self.assertGreater(notice.height(),before)
            self.assertEqual(notice.title.text(),'같은 제목')
            self.assertEqual(self.measured_adjusts(notice,notice.available_rect),0)
            # 안내만 늘어도 화면 높이를 넘으면 기존 전체 계산으로 되돌아갑니다.
            notice.queue_hint.setText('안내\n'*100)
            profile=cProfile.Profile();profile.enable();notice.fit_content();profile.disable()
            self.assertGreater(sum(e.callcount for e in profile.getstats() if isinstance(e.code,str) and 'setContentsMargins' in e.code),0)
        finally:notice.deleteLater()

    def test_small_screen_and_font_changes_invalidate_measurement(self):
        notice=Notice(lambda:None)
        try:
            notice.available_rect=QRect(0,0,1000,900)
            notice.update_event({'id':'one','chat_name':'긴 제목 '*40,'after':{'model':'m','effort':'high'}},False)
            small=QRect(0,0,700,320)
            self.assertGreater(self.measured_adjusts(notice,small),0)
            self.assertLessEqual(notice.height(),320)
            self.assertEqual(self.measured_adjusts(notice,small),0)
            notice.text.setStyleSheet('font-size:13px;')
            self.assertGreater(self.measured_adjusts(notice,small),0)
            self.assertEqual(notice.title.toolTip(),'긴 제목 '*40)
        finally:notice.deleteLater()

    def test_repeated_long_title_keeps_small_screen_elision(self):
        notice=Notice(lambda:None)
        try:
            notice.available_rect=QRect(0,0,700,320)
            event={'id':'one','chat_name':'아주 긴 제목 '*60,'after':{'model':'m','effort':'high'}}
            notice.update_event(event,False)
            shortened=notice.title.text()
            self.assertNotEqual(shortened,event['chat_name'])
            notice.update_event(event,False)
            self.assertEqual(notice.title.text(),shortened)
            self.assertEqual(notice.title.toolTip(),event['chat_name'])
            self.assertEqual(self.measured_adjusts(notice,notice.available_rect),0)
        finally:notice.deleteLater()

    def test_preparation_reuses_worker_context_and_pauses_without_owners(self):
        self.assertTrue(hasattr(motion,'prepare_calendar_motion'))
        motion.close_calendar_motion()
        FakeRenderer.instances=[]
        with patch('calendar_renderer.CalendarRenderer',FakeRenderer):
            result=motion.prepare_calendar_motion()
            self.assertTrue(result['ready']);self.assertFalse(result['error'])
            time.sleep(.05);before=motion.calendar_motion_status()['render_count'];time.sleep(.05)
            self.assertEqual(before,motion.calendar_motion_status()['render_count'])
            owner=Owner();motion.set_calendar_motion_visible(owner,True)
            time.sleep(.05)
            self.assertEqual(len(FakeRenderer.instances),1)
            self.assertGreater(motion.calendar_motion_status()['render_count'],before)
            motion.set_calendar_motion_visible(owner,False)


if __name__=='__main__':unittest.main()
