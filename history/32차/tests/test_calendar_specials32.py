"""고정 특집과 기존 일반 날짜의 경계를 전수 대조합니다."""
from datetime import date, datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
import calendar_art
from calendar_catalog import OBJECTS
from calendar_specials import SPECIAL_DATES, SPECIAL_OBJECTS, special_for_date
from holiday_calendar import event_for_date


class CalendarSpecialTests(unittest.TestCase):
    def test_fixed_specials_cover_74_years_and_neighbor_boundaries(self):
        self.assertEqual(len(SPECIAL_DATES), 8)
        self.assertEqual(len(SPECIAL_OBJECTS), 8)
        self.assertFalse(set(OBJECTS) & set(SPECIAL_OBJECTS))
        count = 0
        for year in range(2026, 2100):
            for month, day in SPECIAL_DATES:
                value = date(year, month, day)
                for offset in (-1, 0, 1):
                    neighbor = value+timedelta(days=offset)
                    if not calendar_art.FIRST_DATE <= neighbor <= calendar_art.LAST_DATE:
                        continue
                    design = calendar_art.design_for_date(neighbor)
                    expected = special_for_date(neighbor)
                    if expected:
                        self.assertEqual(design.object_id, expected.key)
                        self.assertEqual(design.title, expected.name)
                        self.assertIn('특집', design.theme)
                        self.assertEqual((design.anchor_id, design.companion_id), ('', ''))
                    else:
                        self.assertIn(design.object_id, OBJECTS)
                count += 1
        self.assertEqual(count, 592)

    def test_kst_midnight_uses_new_date_even_when_utc_is_previous_day(self):
        for utc, expected in (
            (datetime(2026, 12, 24, 14, 59, 59, tzinfo=timezone.utc), date(2026, 12, 24)),
            (datetime(2026, 12, 24, 15, 0, 0, tzinfo=timezone.utc), date(2026, 12, 25)),
            (datetime(2026, 12, 25, 15, 0, 0, tzinfo=timezone.utc), date(2026, 12, 26)),
        ):
            with patch.object(calendar_art, 'datetime') as clock:
                clock.now.side_effect = lambda zone, utc=utc: utc.astimezone(zone)
                self.assertEqual(calendar_art.current_date(), expected)
                clock.now.assert_called_once_with(calendar_art.KST)

    def test_country_provider_title_and_generic_kind_are_not_renamed(self):
        for value,country in ((date(2026,2,17),'KR'),(date(2026,7,4),'US'),(date(2026,5,3),'JP')):
            event=event_for_date(value,country);self.assertIsNotNone(event)
            design=calendar_art.design_for_date(value,country)
            self.assertEqual(design.title,event['title'])
            self.assertIn('특집',design.theme)
        self.assertNotEqual(calendar_art.design_for_date(date(2026,10,9),'KR').object_id,
                            calendar_art.design_for_date(date(2026,10,9),'US').object_id)
        self.assertIsNone(event_for_date(date(2026,12,25),'JP'))
        self.assertIn('특집',calendar_art.design_for_date(date(2026,12,25),'JP').title)

    def test_city_offset_can_select_previous_date_without_changing_kst_default(self):
        instant=datetime(2026,12,25,1,0,tzinfo=timezone.utc)
        with patch.object(calendar_art,'datetime') as clock:
            clock.now.side_effect=lambda zone:instant.astimezone(zone)
            self.assertEqual(calendar_art.current_date(),date(2026,12,25))
            self.assertEqual(calendar_art.current_date(-8*3600),date(2026,12,24))
            self.assertEqual(calendar_art.current_date(14*3600),date(2026,12,25))
        for value in (True,'32400',-43201,50401):
            with self.assertRaises(ValueError):calendar_art.current_date(value)

    def test_special_geometry_has_depth_unit_normals_and_no_orbit_rings(self):
        import numpy as np
        import calendar_renderer
        fingerprints = set()
        import hashlib
        for month, day in SPECIAL_DATES:
            with patch.object(calendar_renderer, '_ring_geometry', side_effect=AssertionError('특집에 고리 생성')):
                parts = calendar_renderer.build_geometry(calendar_art.design_for_date(date(2026, month, day)))
            points = np.concatenate([mesh[0][:, :3] for mesh, *_ in parts])
            self.assertGreater(np.ptp(points[:, 2]), 2)
            self.assertGreater(np.ptp(points, axis=0).max(), 90)
            fingerprints.add(hashlib.sha256(points.tobytes()).hexdigest())
            for (vertices, indices), _, _, _ in parts:
                self.assertTrue(np.isfinite(vertices).all())
                self.assertTrue(np.allclose(np.linalg.norm(vertices[:, 3:], axis=1), 1, atol=2e-5))
                self.assertLess(indices.max(), len(vertices))
        self.assertEqual(len(fingerprints), 8)


if __name__ == '__main__':
    unittest.main()
