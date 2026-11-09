"""국가·도시 선택의 저장 경계를 창이나 네트워크 없이 검사합니다."""
import sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from app import Controller,Settings
class RegionPreferences32Tests(unittest.TestCase):
 def setUp(self):
  self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup);self.settings=Settings(self.folder.name)
  self.c=SimpleNamespace(closing=False,settings=self.settings,weather=Mock(),_apply_theme_country=Mock(),refresh_region_summary=Mock())
 def city(self):return dict(name='Synthetic City',admin1='Synthetic State',country='Synthetic Country',country_code='US',latitude=40.,longitude=-75.,id=123)
 def test_country_only_changes_event_country_without_replacing_weather_coordinates(self):
  self.assertTrue(hasattr(Controller,'set_theme_country'));before=self.settings.values.get('weather_location')
  Controller.set_theme_country(self.c,'US');saved=Settings(self.folder.name).values
  self.assertEqual(saved['theme_country_mode'],'selected');self.assertEqual(saved['theme_country'],'US');self.assertEqual(saved['weather_location'],before);self.c.weather.set_location_override.assert_not_called();self.c._apply_theme_country.assert_called_once_with('US',estimated=False)
 def test_city_selection_stores_weather_and_event_country_together_and_auto_resets_both_modes(self):
  Controller.set_weather_location(self.c,self.city());saved=Settings(self.folder.name).values
  self.assertEqual(saved['theme_country'],'US');self.assertEqual(saved['theme_country_mode'],'selected');self.assertEqual(saved['weather_location'],self.city())
  Controller.set_weather_location(self.c,None);saved=Settings(self.folder.name).values;self.assertEqual(saved['theme_country_mode'],'auto');self.assertIsNone(saved['weather_location'])
 def test_failed_save_preserves_previous_city_country_and_does_not_apply_new_values(self):
  before=dict(self.settings.values)
  with patch.object(self.settings,'save',side_effect=OSError('synthetic save failure')):
   with self.assertRaises(OSError):Controller.set_weather_location(self.c,self.city())
  self.assertEqual(self.settings.values,before);self.c.weather.set_location_override.assert_not_called();self.c._apply_theme_country.assert_not_called()

 def test_invalid_country_does_not_save_or_change_weather(self):
  before=dict(self.settings.values)
  with self.assertRaises(ValueError):Controller.set_theme_country(self.c,'ZZ')
  self.assertEqual(self.settings.values,before);self.c._apply_theme_country.assert_not_called();self.c.weather.set_location_override.assert_not_called()
 def test_local_date_offset_requires_matching_country_and_valid_integer(self):
  for country,offset,expected in [('US',-18000,-18000),('CA',-18000,None),('US',True,None),('US',60000,None),('US',None,None)]:
   with self.subTest(country=country,offset=offset):
    c=SimpleNamespace(orbit=SimpleNamespace(theme_country='US'),weather=SimpleNamespace(snapshot={'country_code':country,'utc_offset_seconds':offset}))
    with patch('calendar_motion.set_calendar_utc_offset') as setter:
     Controller._sync_calendar_timezone(c);setter.assert_called_once_with(expected)
