"""늦은 프레임 뒤 불필요한 슬롯 대기와 무제한 추격을 막는지 검사합니다."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import calendar_motion as motion


class FrameRecoveryTests(unittest.TestCase):
    def test_early_frame_keeps_the_next_absolute_deadline(self):
        self.assertAlmostEqual(motion.next_frame_deadline(1.0, 1.001), 1.0041666666666667)

    def test_slightly_late_frame_does_not_wait_for_an_extra_slot(self):
        self.assertEqual(motion.next_frame_deadline(1.0, 1.0042), 1.0042)

    def test_long_stall_rebases_once_without_accumulating_work(self):
        recovered = motion.next_frame_deadline(1.0, 1.067)
        self.assertEqual(recovered, 1.067)
        self.assertAlmostEqual(motion.next_frame_deadline(recovered, 1.068), 1.0711666666666666)


if __name__ == '__main__':
    unittest.main()
