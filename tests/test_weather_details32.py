"""기온과 같은 도시·시각에 연결된 날씨·습도·해 시각을 검사합니다."""
import os,sys,time,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs,urlparse
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication
from weather import WeatherClient,weather_description,weather_sun_time
CITY=dict(name='수원시',admin1='경기도',country='대한민국',country_code='KR',latitude=37.29111,longitude=127.00889)
class WeatherDetailsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
 def create(self):
  c=WeatherClient(location_override=CITY);self.addCleanup(c.close);requests=[]
  p=patch.object(c,'_get',side_effect=lambda u,cb:requests.append((u,cb)));p.start();self.addCleanup(p.stop);return c,requests
 def payload(self):
  now=time.time();return dict(current=dict(time=now,temperature_2m=8,relative_humidity_2m=67,weather_code=3),daily=dict(sunrise=[now-10000],sunset=[now+10000]),timezone='Asia/Seoul',utc_offset_seconds=32400)
 def test_one_request_same_coordinates_has_current_and_daily_fields(self):
  c,requests=self.create();c.refresh();q=parse_qs(urlparse(requests[-1][0]).query)
  self.assertEqual(set(q['current'][0].split(',')),{'temperature_2m','relative_humidity_2m','weather_code'});self.assertEqual(q['daily'],['sunrise,sunset']);self.assertEqual(q['timezone'],['auto']);self.assertEqual(q['forecast_days'],['1'])
 def test_valid_details_share_region_and_provider_time_zone(self):
  c,_=self.create();data=self.payload();c._weather_done(data)
  self.assertEqual(c.snapshot['humidity'],67);self.assertEqual(c.snapshot['weather_code'],3);self.assertEqual(c.snapshot['sunrise'],data['daily']['sunrise'][0]);self.assertEqual(c.snapshot['utc_offset_seconds'],32400);self.assertIn('수원',c.snapshot['region'])
 def test_missing_or_polar_sun_is_unknown_while_valid_temperature_remains(self):
  c,_=self.create();data=self.payload();data['current']['relative_humidity_2m']=True;data['current']['weather_code']=True;data['daily']=dict(sunrise=[0],sunset=[None]);c._weather_done(data)
  self.assertEqual(c.snapshot['temperature'],8);self.assertIsNone(c.snapshot['humidity']);self.assertIsNone(c.snapshot['weather_code']);self.assertIsNone(c.snapshot['sunrise']);self.assertIsNone(c.snapshot['sunset'])
 def test_location_switch_clears_all_previous_details(self):
  c,_=self.create();c._weather_done(self.payload());c.set_location_override(None)
  for field in ('temperature','humidity','weather_code','sunrise','sunset','utc_offset_seconds'):self.assertIsNone(c.snapshot[field],field)
 def test_description_localization_and_unknown_codes(self):
  self.assertEqual(weather_description(0),'맑음');self.assertEqual(weather_description(95),'뇌우');self.assertEqual(weather_description(97),'강한 뇌우');self.assertEqual(weather_description(3,'en'),'Overcast');self.assertEqual(weather_description(True),'날씨 미확인');self.assertEqual(weather_description(123),'날씨 미확인')
 def test_sun_time_uses_selected_city_offset_not_computer_local_time(self):
  self.assertEqual(weather_sun_time(1704067200,32400),'09:00');self.assertEqual(weather_sun_time(1704067200,-18000),'19:00');self.assertEqual(weather_sun_time(None,32400),'—');self.assertEqual(weather_sun_time(0,None),'—')
if __name__=='__main__':unittest.main()
