"""행사 목록·발표 일정·출처를 구분하며 없는 자료를 만들지 않습니다."""
import os,sys,unittest
from pathlib import Path
from datetime import date
from unittest.mock import patch
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication
from city_ui33 import CityEventsDialog,city_summary
from i18n import set_language
APP=QApplication.instance() or QApplication([])
CITY=dict(provider='geonames',geonames_id=123,country_code='US',confidence='estimated',provenance='synthetic')
COVERAGE=dict(catalog_items_count=5,series_count=3,edition_count=1,unclassified_count=1,catalog_series_count=3,announced_occurrences_count=1,announced_dates_count=2,coverage_status='partial')
EVENT=dict(id='synthetic-event',title='합성 축제',title_en='Synthetic festival',status='announced',kind='music',dates=['2027-06-10','2027-06-11'],license='CC0-1.0',source_url='https://example.org/synthetic')
class CityUi33Tests(unittest.TestCase):
    def tearDown(self):set_language('ko')
    def test_unidentified_city_does_not_invent_zero_catalog_coverage(self):
        text=city_summary(None,'US',2027);self.assertIn('식별자 미확인',text);self.assertNotIn('0개',text)
    def test_estimated_user_location_is_distinct_from_announced_schedule(self):
        with patch('city_festivals.city_coverage',return_value=COVERAGE):
            text=city_summary(CITY,'US',2027)
        self.assertIn('도시 행사',text);self.assertNotIn('추정',text);self.assertIn('축제 목록 5개 항목',text);self.assertIn('발표 일정 1개',text)
    def test_annual_announced_dates_sources_and_license_remain_accessible(self):
        with patch('city_festivals.city_coverage',return_value=COVERAGE),patch('city_festivals.series_for_city',return_value=[dict(EVENT,display_title='합성 행사 시리즈',dates=[])]),patch('city_festivals.announced_events_for_year',return_value=[dict(EVENT,time_conflict=True,date_evidence='official_page_crosschecked')]):
            dialog=CityEventsDialog(None,CITY,'US',date(2027,6,10));self.addCleanup(dialog.close)
            self.assertEqual(dialog.rows.count(),2);self.assertIn('발표된 일정',dialog.rows.item(0).text())
            self.assertIn('2027-06-11',dialog.details.toPlainText());self.assertIn('CC0-1.0',dialog.details.toPlainText());self.assertIn('https://example.org/synthetic',dialog.details.toPlainText())
            self.assertIn('공식 페이지에서 날짜 확인',dialog.details.toPlainText());self.assertIn('시간은 미확인',dialog.details.toPlainText())
            dialog.rows.setCurrentRow(1);self.assertIn('행사 목록입니다',dialog.details.toPlainText())
    def test_english_summary_and_limits_are_app_owned_translations(self):
        set_language('en')
        with patch('city_festivals.city_coverage',return_value=COVERAGE):self.assertIn('City events',city_summary(CITY,'US',2027))
        dialog=CityEventsDialog(None,None,'US',date(2027,1,1));self.addCleanup(dialog.close)
        self.assertIn('not guaranteed',dialog.limits.text());self.assertIn('unavailable',dialog.summary.text())
