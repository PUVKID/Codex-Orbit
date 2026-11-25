"""1분 갱신·연결별 도시 보정·다른 지역 응답 거부를 확인합니다."""
import os, sys, time, unittest
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication
from weather import WeatherClient, CitySearchClient, network_key
from weather_native import validate_weather_grid
CITY=dict(name='Suwon',admin1='Gyeonggi-do',country='대한민국',country_code='KR',latitude=37.27818,longitude=127.03164,id=1835553)
class Weather43Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def client(self):
  c=WeatherClient(auto_correction=dict(source='user_confirmed',network_key=network_key('192.0.2.4'),city=CITY))
  self.addCleanup(c.close);c._get=lambda *a:None;return c
 def provider(self,ip='192.0.2.4'):
  return dict(success=True,ip=ip,city='Seoul',region='Seoul',country='대한민국',country_code='KR',latitude=37.5665,longitude=126.978)
 def test_city_search_constructor_preserved(self):
  c=CitySearchClient();self.addCleanup(c.close);self.assertEqual(c.language,'ko')
 def test_minute_weather_separate_location_cache(self):
  c=self.client();self.assertEqual(c.poll_timer.interval(),60000)
  c._location_done(self.provider())
  with patch.object(c,'_get') as get:c.refresh();self.assertIn('api.open-meteo.com',get.call_args.args[0])
  c._location_checked_at-=301
  with patch.object(c,'_get') as get:c.refresh();self.assertEqual(get.call_args.args[0],'https://ipwho.is/')
 def test_confirmed_city_not_overwritten_by_geocoding_or_language(self):
  c=self.client();c._location_done(self.provider());self.assertIn('수원',c.snapshot['region']);self.assertIn('경기도',c.snapshot['region'])
  self.assertEqual(c.snapshot['location_mode'],'automatic');self.assertEqual(c.snapshot['city_ref']['geonames_id'],1835553)
  self.assertEqual(c._location['latitude'],CITY['latitude'])
  with patch.object(c,'_get') as get:c._lookup_region();get.assert_not_called()
  c.set_language('en');self.assertIn('Suwon',c.snapshot['region']);self.assertNotIn('Seoul',c.snapshot['region'])
 def test_network_change_removes_correction_and_previous_weather(self):
  c=self.client();c._location_done(self.provider());c.snapshot['temperature']=12
  c._location_done(self.provider('192.0.2.5'));self.assertFalse(c._correction_active);self.assertIn('서울',c.snapshot['region']);self.assertIsNone(c.snapshot['temperature'])
 def test_no_public_default_or_invalid_identity_correction(self):
  c=self.client();d=self.provider();d.pop('ip');c._location_done(d);self.assertFalse(c._correction_active)
 def test_manual_remains_selected(self):
  c=self.client();c.set_location_override(CITY);self.assertEqual(c.snapshot['location_mode'],'manual');self.assertIn('수원',c.snapshot['region'])
 def test_rust_rejects_wrong_city_and_invalid_coordinates(self):
  self.assertLess(validate_weather_grid(CITY,dict(latitude=37.28,longitude=127.03)),1)
  with self.assertRaises(ValueError):validate_weather_grid(CITY,dict(latitude=37.5665,longitude=126.978))
  with self.assertRaises(ValueError):validate_weather_grid(CITY,dict(latitude=float('nan'),longitude=127))
 def test_rust_missing_is_explicit_error(self):
  with patch('weather_native._distance_function',side_effect=ValueError('날씨 위치 검증기를 불러올 수 없습니다')):
   with self.assertRaises(ValueError):validate_weather_grid(CITY,{})
 def test_closed_or_old_callbacks_do_not_update(self):
  c=self.client();cb=c._guard(c._location_done);c.close();cb(self.provider());self.assertEqual(c.snapshot['region'],'')
if __name__=='__main__':unittest.main()
