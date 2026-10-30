"""배율 변경이 누적 모션 위상을 보존하고 실제 시계와 분리되는지 검사합니다."""
from pathlib import Path
from datetime import date
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import frame_pacing


class MotionClockTests(unittest.TestCase):
    def clock(self, now=100.0):
        clock_type = getattr(frame_pacing, 'MotionClock', None)
        self.assertIsNotNone(clock_type, '위상 연속 모션 시계가 없습니다.')
        return clock_type(now)

    def test_default_speed_uses_elapsed_seconds(self):
        clock = self.clock()
        self.assertEqual(clock.speed, 1.0)
        self.assertEqual(clock.sample(100.0), 0.0)
        self.assertEqual(clock.sample(102.0), 2.0)

    def test_changing_speed_preserves_phase_and_changes_only_slope(self):
        clock = self.clock()
        self.assertEqual(clock.sample(102.0), 2.0)
        clock.set_speed(2.0, 102.0)
        self.assertEqual(clock.sample(102.0), 2.0)
        self.assertEqual(clock.sample(103.0), 4.0)
        clock.set_speed(.5, 103.0)
        self.assertEqual(clock.sample(103.0), 4.0)
        self.assertEqual(clock.sample(105.0), 5.0)

    def test_change_integrates_unsampled_time_at_previous_speed(self):
        clock = self.clock()
        clock.set_speed(3.0, 102.0)
        self.assertEqual(clock.sample(102.0), 2.0)
        clock.set_speed(.25, 104.0)
        self.assertEqual(clock.sample(104.0), 8.0)
        self.assertEqual(clock.sample(108.0), 9.0)

    def test_repeated_same_instant_changes_do_not_advance_phase(self):
        clock = self.clock()
        clock.set_speed(.25, 101.0)
        clock.set_speed(3.0, 101.0)
        clock.set_speed(1, 101.0)
        self.assertEqual(clock.sample(101.0), 1.0)
        self.assertEqual(clock.sample(102.0), 2.0)

    def test_invalid_speed_does_not_change_phase_or_speed(self):
        invalid = (True, False, None, '2', float('nan'), float('inf'),
                   -float('inf'), .2499, 3.0001, 0, -1, 10 ** 400)
        for value in invalid:
            with self.subTest(value=repr(value)):
                clock = self.clock()
                with self.assertRaises(ValueError):
                    clock.set_speed(value, 102.0)
                self.assertEqual(clock.speed, 1.0)
                self.assertEqual(clock.sample(103.0), 3.0)

    def test_worker_passes_integrated_phase_without_changing_date(self):
        import calendar_motion as motion
        from PySide6.QtGui import QImage

        with patch.object(motion.time, 'perf_counter', return_value=100.0):
            worker = motion._Worker()
        worker.visible = True
        worker.requested_date = date(2028, 2, 29)
        with patch.object(motion.time, 'perf_counter', return_value=102.0):
            worker.configure(motion_speed=3.0)
        rendered = []

        class OneFrameRenderer:
            def __init__(self, size):
                self.ctx = type('Context', (), {'info': {}})()

            def render(self, value, elapsed):
                rendered.append((value, elapsed))
                worker.stop()
                return QImage(32, 32, QImage.Format.Format_ARGB32_Premultiplied)

            def close(self):
                pass

        with patch('calendar_renderer.CalendarRenderer', OneFrameRenderer):
            with patch.object(motion.time, 'perf_counter', return_value=104.0):
                worker.run()
        self.assertEqual(rendered, [(date(2028, 2, 29), 8.0)])


if __name__ == '__main__':
    unittest.main()
