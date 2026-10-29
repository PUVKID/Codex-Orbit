"""전체 지원 날짜와 윤년·한국 날짜·재현 가능한 기하 선택을 검증합니다."""
from datetime import date, datetime, timedelta
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import hashlib
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from calendar_art import FIRST_DATE,LAST_DATE,THEMES,all_designs,design_for_date,current_date


class CalendarArtTests(unittest.TestCase):
    def test_all_27028_days_are_contiguous_unique_and_complete(self):
        rows=list(all_designs())
        self.assertEqual(len(rows),27028); self.assertEqual(rows[0].date,FIRST_DATE); self.assertEqual(rows[-1].date,LAST_DATE)
        self.assertEqual(len({r.key for r in rows}),27028); self.assertEqual(len({r.seed for r in rows}),27028)
        self.assertEqual(len({(r.date.month,r.date.day,r.year_variant) for r in rows}),27028)
        for index,row in enumerate(rows):
            self.assertEqual(row.date,FIRST_DATE+timedelta(days=index))
            self.assertEqual(row.theme,THEMES[(row.date.year-2026)*12+row.date.month-1]); self.assertEqual(row.variant,row.date.day-1)
        self.assertEqual(sum(r.date.month==2 and r.date.day==29 for r in rows),18)

    def test_invalid_dates_are_not_clamped(self):
        for value in (date(2025,12,31),date(2100,1,1)):
            with self.assertRaises(ValueError):design_for_date(value)
        for value in (None,'2026-01-01',datetime(2026,1,1),True):
            with self.assertRaises(TypeError):design_for_date(value)

    def test_leap_year_seed_and_immutable_design(self):
        leap=design_for_date(date(2028,2,29)); self.assertEqual(leap.theme,THEMES[25])
        first=design_for_date(date(2026,1,1)); self.assertEqual(first,design_for_date(date(2026,1,1)))
        self.assertNotEqual(first.seed,design_for_date(date(2027,1,1)).seed)
        self.assertNotEqual(first.year_variant,design_for_date(date(2027,1,1)).year_variant)
        with self.assertRaises(FrozenInstanceError):first.title='변경'
        self.assertEqual(len({design_for_date(date(2026,1,d)).title.split(' · ')[0] for d in range(1,8)}),7)
        self.assertIs(type(current_date()),date)

    def test_year_variant_changes_actual_vertices_in_previously_missing_branches(self):
        from calendar_renderer import build_geometry
        pairs=[(date(2026,m,d),date(2027,m,d)) for m,d in ((1,5),(1,12),(1,19),(1,26),(10,1),(10,31),(8,3),(8,30))]
        pairs.extend(((date(2027,8,29),date(2036,8,29)),(date(2055,3,24),date(2068,3,24))))
        for first,second in pairs:
            hashes=[]; rings=[]
            for value in (first,second):
                parts=build_geometry(design_for_date(value)); digest=hashlib.sha256()
                for (vertices,_),_,_,_ in parts[:-3]:digest.update(vertices[:,:3].tobytes())
                hashes.append(digest.hexdigest())
                rings.append(hashlib.sha256(b''.join(mesh[0].tobytes() for mesh,*_ in parts[-3:])).hexdigest())
            with self.subTest(first=first,second=second):
                self.assertNotEqual(hashes[0],hashes[1]); self.assertEqual(rings[0],rings[1])


if __name__=='__main__':unittest.main()
