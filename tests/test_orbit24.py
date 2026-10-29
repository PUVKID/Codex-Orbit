"""24차의 세 금속 링과 별도 추정 위치 행을 검증합니다."""
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetricsF, QImage, QPainter
from PySide6.QtWidgets import QApplication
from app import Controller, OrbitWidget, Settings
from calendar_art import design_for_date
from calendar_renderer import build_geometry, matrices
from qt_test_support import cleanup_qt_widgets
from visuals import draw_desktop_orbit


class ThreeRingTests(unittest.TestCase):
    def test_fixed_rings_are_shared_read_only_and_date_motifs_stay_distinct(self):
        first = build_geometry(design_for_date(date(2026, 10, 30)))
        second = build_geometry(design_for_date(date(2026, 10, 31)))
        for left, right in zip(first[-3:], second[-3:]):
            for initial, reused in zip(left[0], right[0]):
                self.assertIs(initial, reused)
                self.assertFalse(initial.flags.writeable)
                with self.assertRaises(ValueError):
                    reused.flat[0] = 0
        from calendar_renderer import _ring_geometry
        self.assertEqual(_ring_geometry.cache_info().maxsize, 1)
        self.assertEqual(_ring_geometry.cache_info().currsize, 1)
        self.assertNotEqual(b''.join(part[0][0].tobytes() for part in first[:-3]),
                            b''.join(part[0][0].tobytes() for part in second[:-3]))

    def test_three_metal_tubes_have_requested_radius_and_thickness(self):
        parts = build_geometry(design_for_date(date(2026, 10, 30)))
        rings = [part for part in parts if part[2] == 1.0]
        self.assertEqual(len(rings), 3)
        for part, radius in zip(rings, (49, 56, 62)):
            (vertices, indices), _, metal, roughness = part
            radial = np.linalg.norm(vertices[:, :2], axis=1)
            self.assertAlmostEqual(float(radial.max()), radius + 2.5, places=4)
            self.assertAlmostEqual(float(radial.min()), radius - 2.5, places=4)
            self.assertAlmostEqual(float(np.ptp(vertices[:, 2])), 5, places=4)
            self.assertTrue(np.isfinite(vertices).all())
            self.assertLess(int(indices.max()), len(vertices))
            self.assertEqual((metal, roughness), (1.0, .23))

    def test_independent_full_rotations_and_twelve_second_loop(self):
        start = matrices(0)
        self.assertEqual(len(start), 4)
        for index, period in enumerate((12, 6, 4), 1):
            with self.subTest(ring=index):
                np.testing.assert_allclose(start[index], matrices(period)[index], atol=1e-12)
                half = start[index][:3, :3].T @ matrices(period / 2)[index][:3, :3]
                self.assertAlmostEqual(float(np.trace(half)), -1, places=10)
                self.assertGreater(float(np.linalg.norm(start[index][:3, 2] - matrices(.5)[index][:3, 2])), .1)
        for first, last in zip(start, matrices(12)):
            np.testing.assert_allclose(first, last, atol=1e-12)
        relative = lambda values: values[1][:3, :3].T @ values[2][:3, :3]
        self.assertGreater(float(np.linalg.norm(relative(start) - relative(matrices(.5)))), .1)


class LocationRowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(cleanup_qt_widgets, self)

    def test_region_is_visible_and_tooltip_preserves_full_value(self):
        with patch('app.WeatherClient') as weather:
            weather.return_value.snapshot = {}
            self.controller = Controller(Settings(self.temp.name), start_worker=False, start_usage=False)
        c = self.controller
        region = '서울특별시 아주 긴 추정 지역 이름'
        value = dict(temperature=12.5, region=region, stale=False, busy=False)
        c.update_weather(value)
        self.assertEqual(c.orbit.location_text, region)
        self.assertEqual(c.orbit.weather_text, '12.5℃')
        self.assertIn('네트워크 추정 지역: ' + region, c.orbit.toolTip())
        c.update_usage(c.usage.snapshot)
        self.assertIn(region, c.orbit.toolTip())
        c.update_weather(dict(value, region=''))
        self.assertEqual(c.orbit.location_text, '위치 정보 없음')

    def test_location_elision_and_all_rows_do_not_overlap_at_minimum_size(self):
        title = '열여섯글자까지길어지는실제꽃이름입니다'
        region = '대한민국 서울특별시 아주 긴 네트워크 추정 지역'
        design = SimpleNamespace(title=title, date=date(2026, 10, 30), accent='#8EDCCB')
        source = QImage(96, 96, QImage.Format.Format_ARGB32_Premultiplied)
        source.fill(Qt.GlobalColor.transparent)
        for width, height in ((180, 250), (220, 332), (640, 250), (180, 500)):
            image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
            image.fill(Qt.GlobalColor.transparent)
            painter = QPainter(image)
            try:
                result = draw_desktop_orbit(painter, width, height, source, design, .4325, 'fresh', '23:59:59', '12.5℃', region)
            finally:
                painter.end()
            rects = [result[key] for key in ('art', 'dock', 'location', 'weather', 'usage')]
            self.assertGreater(rects[0].width(), 0)
            self.assertGreaterEqual(rects[0].top(), 0)
            for first, second in zip(rects, rects[1:]):
                self.assertLessEqual(first.bottom(), second.top())
            self.assertLessEqual(rects[-1].bottom(), height)
            metrics = QFontMetricsF(result['date_font'])
            self.assertGreaterEqual(result['date_font'].pixelSize(), 14)
            self.assertLessEqual(metrics.horizontalAdvance(result['location_text']), result['location'].width() - 16)
            if width == 180:
                self.assertIn('…', result['location_text'])
            self.assertEqual(''.join(result['lines']), title)
            self.assertAlmostEqual(result['fill'].width(), result['track'].width() * .4325)

    def test_saved_size_only_clamped_to_new_minimum(self):
        settings = Settings(self.temp.name)
        for saved, expected in (([230, 270], (230, 270)), ([180, 210], (180, 250))):
            settings.values['size'] = saved
            widget = OrbitWidget(settings, lambda: None, lambda: None)
            try:
                self.assertEqual(widget.size().toTuple(), expected)
                self.assertEqual(widget.minimumSize().toTuple(), (180, 250))
            finally:
                widget.close()
                widget.deleteLater()


if __name__ == '__main__':
    unittest.main()
