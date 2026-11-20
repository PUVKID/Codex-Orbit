import math
import sys
import unittest
from pathlib import Path
from datetime import date
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from calendar_renderer import CalendarRenderer, matrices

class Pixel34Tests(unittest.TestCase):
    def test_rotation_is_full_and_fixed(self):
        for t in (0, 3, 6, 9, 12):
            matrix = matrices(t)[0]
            np.testing.assert_allclose(matrix[:3, 3], 0, atol=1e-12)
            np.testing.assert_allclose(matrix[:3, :3].T @ matrix[:3, :3], np.eye(3), atol=1e-12)
        np.testing.assert_allclose(matrices(0)[0], matrices(12)[0], atol=1e-12)
        self.assertLess(matrices(6)[0][0, 0], -.99)
        for value in (float('nan'), float('inf'), -float('inf')):
            with self.assertRaises(ValueError): matrices(value)

    def test_actual_gpu_pixels_and_loop(self):
        renderer = CalendarRenderer(384)
        try:
            images = [renderer.render(date(2026, 6, 13), t) for t in (0, 3, 6, 12)]
            arrays = [np.frombuffer(i.constBits(), dtype=np.uint8).reshape(384, 384, 4).copy() for i in images]
            self.assertTrue(np.array_equal(arrays[0], arrays[3]))
            self.assertFalse(np.array_equal(arrays[0], arrays[1]))
            self.assertFalse(np.array_equal(arrays[0], arrays[2]))
            self.assertEqual(arrays[0][0, 0, 3], 0)
            self.assertGreater(np.count_nonzero(arrays[0][:, :, 3]), 100)
            self.assertTrue(np.array_equal(arrays[0][::4, ::4], arrays[0][1::4, 1::4]))
        finally:
            renderer.close()

if __name__ == '__main__': unittest.main()
