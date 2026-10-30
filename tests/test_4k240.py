"""25차 한글 지역·실제 4K 렌더와 240fps 전달 계약을 검증합니다."""
import os
from pathlib import Path
import sys
import time
import unittest
from datetime import date
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import numpy as np
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication
import calendar_motion as motion
from calendar_renderer import CalendarRenderer
from weather import WeatherClient
from test_calendar_motion import FakeRenderer


class KoreanRegionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_korean_mapping_native_duplicate_and_foreign_are_separated(self):
        from weather import localized_region
        for data, expected in ((dict(country_code='KR', city='Seoul', region='Seoul'), '서울특별시'),
                               (dict(country_code='KR', city='Suwon-si', region='Gyeonggi-do'), '경기도 · 수원시'),
                               (dict(country_code='KR', city='부산광역시', region='Busan'), '부산광역시'),
                               (dict(country_code='US', city='Seoul', region='Virginia'), 'Seoul · Virginia · 미국'),
                               ({}, '위치 정보 없음')):
            self.assertEqual(localized_region(data)[0], expected)
        label, original = localized_region(dict(country_code='KR', city='Unknown', region='Gyeonggi-do'))
        self.assertEqual(label, '경기도 · Unknown')
        self.assertIn('Unknown', original)
        self.assertNotIn('서울', label)
        self.assertEqual(localized_region(dict(city=123, region=[]))[0], '위치 정보 없음')

    def test_snapshot_keeps_original_region_without_ip_or_coordinates(self):
        client = WeatherClient()
        try:
            with patch.object(client, '_get'):
                client._location_done(dict(success=True, latitude=37.5, longitude=127,
                                           country_code='KR', city='Suwon-si', region='Gyeonggi-do'))
                client._weather_done(dict(current=dict(temperature_2m=12.5, time=time.time())))
            self.assertEqual(client.snapshot['region'], '경기도 · 수원시')
            self.assertIn('Suwon-si', client.snapshot['region_original'])
            self.assertFalse({'ip', 'latitude', 'longitude'} & client.snapshot.keys())
        finally:
            client.close()

    def test_ambiguous_gwangju_requires_confirmed_province(self):
        from weather import localized_region
        for region, expected in (('Gyeonggi-do', '경기도 · 광주시'),
                                 ('Gwangju', '광주광역시'),
                                 ('', 'Gwangju'),
                                 ('Unknown', 'Unknown · Gwangju')):
            with self.subTest(region=region):
                label, original = localized_region(dict(country_code='KR',city='Gwangju',region=region))
                self.assertEqual(label, expected)
                self.assertIn('Gwangju', original)
                if region:
                    self.assertIn(region, original)


class FourKRendererTests(unittest.TestCase):
    def test_actual_4k_target_square_gpu_delivery_and_original_export(self):
        renderer = CalendarRenderer((3840, 2160))
        try:
            renderer.set_output_size(192)
            image = renderer.render(date(2026, 10, 30), .5)
            self.assertEqual(renderer.target.size, (3840, 2160))
            self.assertEqual(renderer.resolved.size, (3840, 2160))
            self.assertEqual(image.size().toTuple(), (192, 192))
            self.assertEqual(image.pixelColor(0, 0).alpha(), 0)
            raw = renderer.render_original(date(2026, 10, 30), .5)
            self.assertEqual(raw.size().toTuple(), (3840, 2160))
            pixels = np.frombuffer(raw.constBits(), dtype=np.uint8).reshape(2160, 3840, 4)
            ys, xs = np.nonzero(pixels[:, :, 3])
            self.assertGreater(len(xs), 1000)
            self.assertLess(abs((int(xs.max()) + int(xs.min())) / 2 - 1920), 100)
            self.assertLess(abs((int(ys.max()) + int(ys.min())) / 2 - 1080), 100)
            self.assertTrue(np.all(pixels[:, :400, 3] == 0))
            self.assertTrue(np.all(pixels[:, -400:, 3] == 0))
            renderer.set_output_size(512)
            self.assertEqual(renderer.render(date(2026, 10, 30), .6).size().toTuple(), (512, 512))
        finally:
            renderer.close()

    def test_invalid_resolution_and_output_size_are_rejected(self):
        for size in ((3840, 3840), (True, 2160), (3840,), '4K'):
            with self.assertRaises(ValueError):
                CalendarRenderer(size)
        renderer = CalendarRenderer(64)
        try:
            for size in (True, 0, 2161, float('inf')):
                with self.assertRaises(ValueError):
                    renderer.set_output_size(size)
        finally:
            renderer.close()


class Motion240Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def tearDown(self):
        motion.close_calendar_motion()

    def test_absolute_deadlines_skip_missed_slots_without_drift(self):
        self.assertEqual(motion.FPS, 240)
        from calendar_motion import next_frame_deadline
        self.assertAlmostEqual(next_frame_deadline(1, 1.001), 1 + 1 / 240)
        self.assertAlmostEqual(next_frame_deadline(1, 1.02), 1 + 5 / 240)

    def test_native_waiter_handle_lifecycle_and_errors(self):
        import ctypes
        import threading
        from frame_pacing import FrameWaiter
        with patch('frame_pacing.ctypes.WinDLL') as library:
            kernel=library.return_value
            kernel.CreateWaitableTimerExW.return_value=123
            kernel.SetWaitableTimer.return_value=1
            kernel.WaitForSingleObject.return_value=0
            kernel.CloseHandle.return_value=1
            waiter=FrameWaiter()
            try:
                self.assertEqual(waiter.backend,'Windows 고해상도 대기 타이머')
                waiter.wait(.001,threading.Condition())
                kernel.WaitForSingleObject.return_value=258
                with self.assertRaisesRegex(OSError,'258'):waiter.wait(.001,threading.Condition())
                kernel.SetWaitableTimer.return_value=0
                with patch('ctypes.get_last_error',return_value=5):
                    with self.assertRaises(OSError):waiter.wait(.001,threading.Condition())
            finally:
                waiter.close()
            waiter.close()
            kernel.CloseHandle.assert_called_once_with(123)
            kernel.CreateWaitableTimerExW.return_value=0
            with patch('ctypes.get_last_error',return_value=87):unsupported=FrameWaiter()
            self.assertIn('미지원',unsupported.warning)
            unsupported.close()
            kernel.CreateWaitableTimerExW.return_value=456
            kernel.CloseHandle.return_value=0
            bad_close=FrameWaiter()
            with patch('ctypes.get_last_error',return_value=6):
                with self.assertRaises(OSError):bad_close.close()

    def test_arrival_dispatch_metrics_resize_and_pause(self):
        class Owner:
            def __init__(self):
                self.arrivals = 0
            def calendar_frame_ready(self):
                self.arrivals += 1
        owner = Owner()
        with patch('calendar_renderer.CalendarRenderer', FakeRenderer):
            motion.set_calendar_motion_visible(owner, True)
            motion.set_calendar_motion_size(owner, 512)
            loop = QEventLoop(); QTimer.singleShot(80, loop.quit); loop.exec()
            status = motion.calendar_motion_status()
            self.assertEqual(status['target_fps'], 240)
            self.assertEqual(status['pacing_clock'], 'perf_counter')
            self.assertEqual(status['source_dimensions'], [3840, 2160])
            self.assertEqual(status['requested_delivery_size'], 512)
            self.assertGreater(status['render_count'], 6)
            self.assertGreater(owner.arrivals, 2)
            self.assertGreater(status['dispatch_count'], 2)
            motion.set_calendar_motion_visible(owner, False)
            time.sleep(.02)
            before = motion.calendar_motion_status()['render_count']
            time.sleep(.03)
            self.assertEqual(before, motion.calendar_motion_status()['render_count'])


if __name__ == '__main__':
    unittest.main()
