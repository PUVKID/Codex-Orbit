"""발표된 도시 행사만 기존 달력 우선순위와 메시로 연결하는지 검사합니다."""
import hashlib,sys,unittest
from pathlib import Path
from datetime import date
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import calendar_specials,calendar_art
CITY=dict(provider='geonames',geonames_id=123,country_code='US',confidence='selected',provenance='synthetic')
EVENT=dict(id='synthetic-festival',title='합성 음악 행사',title_en='Synthetic music festival',kind='music',status='announced',date_precision='day',date_evidence='official_api_consistent')

class CityCalendar33Tests(unittest.TestCase):
    def test_only_explicit_date_evidence_can_override_and_conflicts_need_page_crosscheck(self):
        for evidence,conflict,expected in [('official_api_consistent',False,True),
                                           ('official_api_consistent',True,False),
                                           ('official_page_crosschecked',True,True),
                                           ('official_page_crosschecked',False,True),
                                           (None,False,False),('unverified',False,False)]:
            with self.subTest(evidence=evidence,conflict=conflict),patch('city_festivals.city_events_for_date',return_value=[dict(EVENT,date_evidence=evidence,time_conflict=conflict)]),patch('calendar_specials.event_for_date',return_value=None):
                selected=calendar_specials.special_for_date(date(2027,6,17),'US',CITY)
                self.assertEqual(selected is not None and selected.recipe=='city_music',expected)

    def test_announced_city_event_precedes_general_public_holiday(self):
        holiday=dict(kind='public_holiday',title='합성 공휴일')
        with patch('city_festivals.city_events_for_date',return_value=[EVENT]),patch('calendar_specials.event_for_date',return_value=holiday):
            special=calendar_specials.special_for_date(date(2026,6,17),'US',CITY)
        self.assertEqual(special.name,EVENT['title']);self.assertEqual(special.recipe,'city_music')
    def test_major_fixed_special_still_precedes_city_event(self):
        with patch('city_festivals.city_events_for_date',return_value=[EVENT]):
            special=calendar_specials.special_for_date(date(2026,12,25),'US',CITY)
        self.assertEqual(special.key,'special_christmas')
    def test_unannounced_or_imprecise_events_do_not_replace_original_date(self):
        for status,precision in [('catalog_only','month'),('announced','month')]:
            with self.subTest(status=status,precision=precision),patch('city_festivals.city_events_for_date',return_value=[dict(EVENT,status=status,date_precision=precision)]):
                design=calendar_art.design_for_date(date(2026,6,17),'US',CITY)
                self.assertFalse(design.object_id.startswith('city_festival_'))
    def test_selected_city_and_none_do_not_share_design_cache(self):
        with patch('city_festivals.city_events_for_date',return_value=[dict(EVENT,date_precision='day')]):
            city=calendar_art.design_for_date(date(2026,6,18),'US',CITY)
            normal=calendar_art.design_for_date(date(2026,6,18),'US')
        self.assertNotEqual(city.object_id,normal.object_id)
    def test_all_eight_categories_have_distinct_nonempty_meshes(self):
        from calendar_renderer import build_geometry
        fingerprints=set()
        for index,kind in enumerate(('music','film','snow','lights','carnival','flowers','culture','balloon')):
            with self.subTest(kind=kind),patch('city_festivals.city_events_for_date',return_value=[dict(EVENT,kind=kind,date_precision='day')]):
                design=calendar_art.design_for_date(date(2026,7,index+10),'US',CITY)
                self.assertEqual(design.shape_recipe,'city_'+kind)
                parts=build_geometry(design)
                self.assertTrue(parts)
                self.assertTrue(all(len(mesh[0])>0 and len(mesh[1])>0 for mesh,*_ in parts))
                fingerprints.add(hashlib.sha256(b''.join(mesh[0].tobytes()+mesh[1].tobytes() for mesh,*_ in parts)).hexdigest())
        self.assertEqual(len(fingerprints),8)
    def test_city_context_setter_defensively_copies_and_clears(self):
        from calendar_motion import _Worker
        worker=_Worker();city=dict(CITY);worker.configure(city_ref=city);city['geonames_id']=999
        self.assertEqual(worker.city_ref['geonames_id'],123)
        version=worker.scene_version;worker.configure(city_ref=None)
        self.assertIsNone(worker.city_ref);self.assertGreater(worker.scene_version,version)

    def test_catalog_revision_invalidates_same_city_and_date(self):
        from calendar_motion import _Worker
        worker=_Worker();worker.configure(catalog_revision='first');version=worker.scene_version
        worker.configure(catalog_revision='second');self.assertGreater(worker.scene_version,version)
        with patch('city_festivals.city_events_for_date',return_value=[EVENT]),patch('city_festivals.get_city_catalog_revision',return_value='synthetic-first'):
            first=calendar_art.design_for_date(date(2026,7,29),'US',CITY)
        with patch('city_festivals.city_events_for_date',return_value=[dict(EVENT,title='새 합성 일정')]),patch('city_festivals.get_city_catalog_revision',return_value='synthetic-second'):
            second=calendar_art.design_for_date(date(2026,7,29),'US',CITY)
        self.assertNotEqual(first.title,second.title)
