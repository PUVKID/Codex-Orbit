"""17차 내부 실제3D 브랜드의 가시성·공유 재생·종료 경계입니다."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from app import Controller, Settings
from qt_test_support import cleanup_qt_widgets, wait_qt


class MotionBrandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.addCleanup(cleanup_qt_widgets, self)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.c = Controller(Settings(folder.name), start_worker=False, start_usage=False)
        self.addCleanup(self.c.close)

    def test_visible_header_plays_actual_frames_and_hidden_header_stops(self):
        mark = self.c.window.brand_mark
        self.assertTrue(hasattr(mark, 'playback_clock'), '정지 로고를 공유 재생기로 바꿉니다.')
        self.assertFalse(mark.playback_clock.timer.isActive())
        from calendar_motion import prepare_calendar_motion
        # 실제 시작 경로처럼 GPU 첫 프레임 준비를 재생 측정 구간과 분리합니다.
        preparation = prepare_calendar_motion(timeout_seconds=2.0)
        self.assertIs(preparation['ready'], True, preparation['error'])
        self.assertEqual(preparation['error'], '')
        self.c.show()
        first = mark.pixmap().toImage()
        wait_qt(180)
        self.assertNotEqual(first, mark.pixmap().toImage())
        self.assertTrue(mark.playback_clock.timer.isActive())
        self.c.window.hide()
        self.assertFalse(mark.playback_clock.timer.isActive())
        held = mark.pixmap().toImage()
        wait_qt(70)
        self.assertEqual(held, mark.pixmap().toImage())

    def test_notice_and_header_share_clock_and_close_unregisters(self):
        self.c.show()
        self.c.receive({'id': 'motion-brand', 'target': 'motion-brand', 'after': {'model': 'm'}})
        header, notice = self.c.window.brand_mark, self.c.notice.brand_mark
        self.assertTrue(hasattr(header, 'playback_clock'))
        self.assertIs(header.playback_clock, notice.playback_clock)
        self.assertEqual(self.c.orbit.origin_time, header.playback_clock.origin)
        self.assertGreaterEqual(notice.width(), 32)
        self.c.close()
        self.assertFalse(header.playback_clock.timer.isActive())
        self.assertEqual(header.playback_clock.active_count, 0)

    def test_existing_function_controls_keep_text_with_monochrome_symbols(self):
        self.assertEqual(self.c.window.usage_refresh.text(), '새로고침')
        self.assertFalse(self.c.window.usage_refresh.icon().isNull())
        self.assertEqual([self.c.window.tabs.tabText(i) for i in range(2)], ['변경 기록', '사용 한도'])
        self.assertTrue(all(not self.c.window.tabs.tabIcon(i).isNull() for i in range(2)))
        from brand import symbol_image
        for kind in ('model', 'effort', 'time', 'reason', 'quota', 'refresh', 'history'):
            image = symbol_image(kind)
            self.assertTrue(image.allGray())
            self.assertEqual(image.pixelColor(0, 0).alpha(), 0)

    def test_many_notices_share_one_clock_and_bounded_original_frame_cache(self):
        for i in range(8):
            self.c.receive({'id': str(i), 'target': str(i), 'after': {'model': 'm'}})
        marks = [card.brand_mark for card in self.c.notices.values()]
        self.assertTrue(all(hasattr(mark, 'playback_clock') for mark in marks))
        self.assertEqual(len({id(mark.playback_clock) for mark in marks}), 1)
        QTest.qWait(120)
        from atom_frames import get_atom_frames
        self.assertLessEqual(len(get_atom_frames().cache), 24)
