"""지역 자동·수동 선택에서 저장 전후의 경계를 검사합니다."""
import os,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication,QWidget
from app import Settings,Controller,WeatherLocationDialog
from i18n import set_language
APP=QApplication.instance() or QApplication([])
CITY=dict(name='Synthetic City',admin1='Synthetic State',country='United States',country_code='US',latitude=40.,longitude=-75.)

class LocationMode33Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.settings=Settings(self.temp.name);self.window=QWidget();self.addCleanup(self.window.close)
        self.c=SimpleNamespace(window=self.window,settings=self.settings,set_weather_location=Mock(),set_theme_country=Mock())
    def dialog(self):
        dialog=WeatherLocationDialog(self.c);self.addCleanup(dialog.close_search);self.addCleanup(dialog.close);return dialog
    def test_new_settings_are_automatic_and_mode_labels_are_plain(self):
        self.assertIsNone(self.settings.values['weather_location']);self.assertEqual(self.settings.values['theme_country_mode'],'auto')
        dialog=self.dialog();self.assertEqual(dialog.mode_selector.currentData(),'automatic')
        self.assertIn('자동',dialog.mode_status.text());self.assertFalse(dialog.search_button.isEnabled())
        self.assertEqual(dialog.mode_selector.itemText(0),'자동');self.assertEqual(dialog.mode_selector.itemText(1),'수동')
    def test_manual_draft_search_and_cancel_do_not_save_or_apply(self):
        dialog=self.dialog();before=dict(self.settings.values)
        dialog.mode_selector.setCurrentIndex(dialog.mode_selector.findData('manual'))
        self.assertTrue(dialog.search_button.isEnabled());dialog.reject()
        self.assertEqual(self.settings.values,before);self.c.set_weather_location.assert_not_called();self.c.set_theme_country.assert_not_called()
    def test_selecting_automatic_from_manual_applies_none_immediately(self):
        self.settings.values['weather_location']=CITY;dialog=self.dialog()
        self.assertEqual(dialog.mode_selector.currentData(),'manual')
        dialog.mode_selector.setCurrentIndex(dialog.mode_selector.findData('automatic'))
        self.c.set_weather_location.assert_called_once_with(None)
    def test_automatic_reapply_requests_new_lookup_when_backend_already_automatic(self):
        self.settings.values.update(language='en',text_scale=150,custom_preserved='unchanged')
        self.settings.save();weather=Mock();weather.set_location_override.return_value=False
        c=SimpleNamespace(closing=False,settings=self.settings,weather=weather,_apply_theme_country=Mock(),refresh_region_summary=Mock())
        Controller.set_weather_location(c,None)
        weather.refresh.assert_called_once_with();saved=Settings(self.temp.name).values
        self.assertEqual(saved['language'],'en');self.assertEqual(saved['text_scale'],150);self.assertEqual(saved['custom_preserved'],'unchanged');self.assertIsNone(saved['weather_location']);self.assertEqual(saved['theme_country_mode'],'auto')
    def test_mode_labels_are_owned_translations_in_both_languages(self):
        self.addCleanup(set_language,'ko')
        for language,expected in [('ko','자동'),('en','Automatic')]:
            set_language(language);dialog=self.dialog()
            self.assertIn(expected,dialog.mode_selector.itemText(0));self.assertIn(expected,dialog.mode_status.text())
