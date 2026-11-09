"""수동 도시 좌표와 자동 위치 복귀의 공개 데이터 경계를 검사합니다."""
import os,sys,time,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlparse,parse_qs
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication
from weather import WeatherClient, CitySearchClient, normalize_city, parse_city_results
CITY=dict(id=1835553,name='수원시',admin1='경기도',country='대한민국',country_code='KR',latitude=37.29111,longitude=127.00889)
class ManualLocationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def create(self,value=CITY):
  c=WeatherClient(location_override=value);self.addCleanup(c.close);requests=[]
  p=patch.object(c,'_get',side_effect=lambda url,cb:requests.append((url,cb)));p.start();self.addCleanup(p.stop)
  return c,requests
 def test_manual_uses_selected_coordinates_without_IP_and_has_matching_region(self):
  c,requests=self.create();c.refresh();url,cb=requests.pop();q=parse_qs(urlparse(url).query)
  self.assertIn('api.open-meteo.com',url);self.assertEqual(float(q['latitude'][0]),CITY['latitude']);self.assertEqual(float(q['longitude'][0]),CITY['longitude'])
  cb(dict(current=dict(temperature_2m=12.3,time=time.time())))
  self.assertIn('수원',c.snapshot['region']);self.assertEqual(c.snapshot['temperature'],12.3);self.assertEqual(c.snapshot['location_mode'],'manual');self.assertEqual(requests,[])
  self.assertNotIn('latitude',c.snapshot);self.assertNotIn('longitude',c.snapshot)
 def test_changing_city_clears_old_temperature_and_rejects_late_IP(self):
  c,requests=self.create(None);c.refresh();_,old= requests.pop();c.set_location_override(CITY)
  old(dict(success=True,city='Seoul',country_code='KR',latitude=37.56,longitude=126.97))
  self.assertIn('수원',c.snapshot['region']);self.assertIsNone(c.snapshot['temperature']);self.assertEqual(len(requests),1)
 def test_automatic_return_does_not_keep_manual_coordinates_or_temperature(self):
  c,requests=self.create();c.refresh();c.set_location_override(None)
  self.assertEqual(c.snapshot['location_mode'],'automatic');self.assertIsNone(c.snapshot['temperature']);self.assertEqual(c.snapshot['region'],'');self.assertEqual(requests[-1][0],'https://ipwho.is/')
 def test_validation_rejects_invalid_coordinates_and_keeps_selected_city(self):
  c,requests=self.create()
  for value in (dict(CITY,latitude=True),dict(CITY,longitude=float('nan')),dict(CITY,country_code='BAD'),dict(CITY,name='')):
   with self.assertRaises(ValueError):c.set_location_override(value)
  self.assertEqual(c.location_override['id'],CITY['id']);self.assertEqual(requests,[])
 def test_search_rows_are_bounded_clean_and_do_not_silently_pick_first(self):
  rows=parse_city_results(dict(results=[CITY,dict(CITY,name='Suwon',country_code='US',id=123)]))
  self.assertEqual(len(rows),2);self.assertEqual(rows[1]['country_code'],'US');self.assertEqual(parse_city_results({}),[])
  self.assertEqual(normalize_city(dict(CITY,ip='private',extra='private')),CITY)
  with self.assertRaises(ValueError):parse_city_results(dict(results=[CITY]*11))
 def test_manual_language_and_close_do_not_start_location_lookup(self):
  c,requests=self.create();c.refresh();c.set_language('en');self.assertTrue(all('ipwho.is' not in url for url,_ in requests));late=requests[-1][1];c.close();late(dict(current=dict(temperature_2m=20,time=time.time())));self.assertIsNone(c.snapshot['temperature'])
 def test_automatic_new_region_never_relabels_previous_weather(self):
  c,requests=self.create(None)
  a=dict(success=True,city='Example A',region='State A',country='Example',country_code='US',latitude=40,longitude=-74)
  c._location_done(a);c._weather_done(dict(current=dict(temperature_2m=12,relative_humidity_2m=20,weather_code=0,time=time.time()),timezone='Etc/UTC',utc_offset_seconds=0))
  self.assertEqual(c.snapshot['temperature'],12)
  c._location_done(dict(a,city='Example B',country_code='GB',latitude=51,longitude=0))
  for field in ('temperature','humidity','weather_code','sunrise','sunset','utc_offset_seconds','checked_at','observed_at'):
   self.assertIsNone(c.snapshot[field],field)
  self.assertIsNone(c.last_success);self.assertTrue(c.snapshot['stale']);self.assertEqual(c.snapshot['timezone'],'');self.assertIn('Example B',c.snapshot['region'])
  c._request_failed('기온 조회 실패');self.assertIsNone(c.snapshot['temperature'])
 def test_automatic_same_region_keeps_last_known_weather_while_refreshing(self):
  c,requests=self.create(None);a=dict(success=True,city='Example',country_code='US',latitude=40,longitude=-74)
  c._location_done(a);c._weather_done(dict(current=dict(temperature_2m=12,time=time.time())))
  c._location_done(a);self.assertEqual(c.snapshot['temperature'],12)
if __name__=='__main__':unittest.main()
