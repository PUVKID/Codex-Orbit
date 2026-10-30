"""전세계 공개 도시 좌표의 제어 응답으로 언어·국가·거리·수명 경계를 검사합니다."""
import json
import os
from pathlib import Path
import sys
import time
import unittest
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtNetwork import QNetworkReply
from PySide6.QtWidgets import QApplication
from weather import WeatherClient


# 번역 문자열은 제어 응답이며 실제 API 번역 지원을 주장하는 자료가 아닙니다.
CASES = (
    ('JP', 'Tokyo', 35.68, 139.69, ('도쿄', '도쿄도', '일본'), ('Tokyo', 'Tokyo', 'Japan')),
    ('FR', 'Paris', 48.86, 2.35, ('파리', '일드프랑스', '프랑스'), ('Paris', 'Ile-de-France', 'France')),
    ('KE', 'Nairobi', -1.29, 36.82, ('나이로비', '나이로비 카운티', '케냐'), ('Nairobi', 'Nairobi County', 'Kenya')),
    ('US', 'New York', 40.71, -74.01, ('뉴욕', '뉴욕주', '미국'), ('New York', 'New York', 'United States')),
)


class Reply:
    def __init__(self, raw=b'{}', error=QNetworkReply.NetworkError.NoError):
        self.raw=raw; self.network_error=error; self.aborted=False
    def read(self,count):return self.raw[:count]
    def error(self):return self.network_error
    def abort(self):self.aborted=True
    def deleteLater(self):pass


class GlobalWeatherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def create(self,language='ko'):
        client=WeatherClient(language=language)
        self.addCleanup(client.close)
        requests=[]
        mocked=patch.object(client,'_get',side_effect=lambda url,callback:requests.append((url,callback)))
        mocked.start();self.addCleanup(mocked.stop)
        return client,requests

    def locate(self,client,requests,code='JP',city='Tokyo',latitude=35.68,longitude=139.69,expect_geo=True):
        client._location_done(dict(success=True,country_code=code,city=city,region='Original region',country='Original country',
                                   latitude=latitude,longitude=longitude))
        self.assertIn('api.open-meteo.com/v1/forecast',requests[0][0])
        requests.pop(0)[1](dict(current=dict(temperature_2m=18.5,time=time.time())))
        self.assertEqual(client.snapshot['temperature'],18.5)
        self.assertFalse(client.snapshot['stale'])
        if expect_geo:self.assertIn('geocoding-api.open-meteo.com',requests[-1][0])

    def test_four_continents_in_both_languages_and_request_parameters(self):
        for code,city,lat,lon,ko,en in CASES:
            for language,names in (('ko',ko),('en',en)):
                with self.subTest(country=code,language=language):
                    client,requests=self.create(language)
                    self.locate(client,requests,code,city,lat,lon)
                    query=parse_qs(urlparse(requests[-1][0]).query)
                    self.assertEqual(query['language'],[language]);self.assertEqual(query['countryCode'],[code])
                    self.assertEqual(query['count'],['10']);self.assertEqual(query['name'],[city])
                    row=dict(name=names[0],admin1=names[1],country=names[2],country_code=code,latitude=lat,longitude=lon)
                    requests.pop()[1](dict(results=[row]))
                    self.assertEqual(client.snapshot['region'],' · '.join(dict.fromkeys(names)))
                    self.assertEqual(client.snapshot['language'],language)
                    self.assertIn('GeoNames',client.snapshot['region_source'])
                    self.assertIn(city,client.snapshot['region_original'])

    def test_country_mismatch_distance_and_malformed_candidates_use_original(self):
        for row in (dict(name='다른 나라',country_code='US',latitude=35.68,longitude=139.69),
                    dict(name='먼 도시',country_code='JP',latitude=45,longitude=140),
                    dict(name='잘못된 좌표',country_code='JP',latitude=True,longitude=139.69),
                    dict(name=123,country_code='JP',latitude=35.68,longitude=139.69)):
            with self.subTest(candidate=row):
                client,requests=self.create();self.locate(client,requests)
                requests.pop()[1](dict(results=[row]))
                self.assertIn('Tokyo',client.snapshot['region'])
                self.assertEqual(client.snapshot['temperature'],18.5)
                self.assertFalse(client.snapshot['busy']);self.assertFalse(client.snapshot['stale'])

    def test_nearest_same_country_candidate_and_missing_translation_preserved(self):
        client,requests=self.create();self.locate(client,requests)
        requests.pop()[1](dict(results=[dict(name='Wrong city',country_code='JP',latitude=35.85,longitude=139.69),
                                       dict(name='Tokyo native fallback',country='Japan',country_code='JP',latitude=35.681,longitude=139.69)]))
        self.assertEqual(client.snapshot['region'],'Tokyo native fallback · Japan')

    def test_geocoding_network_timeout_oversize_and_malformed_do_not_discard_weather(self):
        for failure in ('network','timeout','oversize','malformed','empty'):
            with self.subTest(failure=failure):
                client,requests=self.create();self.locate(client,requests)
                callback=requests.pop()[1]
                if failure=='empty':callback({})
                else:
                    raw=b'x'*(client.LIMIT+1) if failure=='oversize' else (b'{broken' if failure=='malformed' else b'{}')
                    error=QNetworkReply.NetworkError.ConnectionRefusedError if failure=='network' else QNetworkReply.NetworkError.NoError
                    reply=Reply(raw,error);client.reply=reply
                    if failure=='timeout':client._timeout();self.assertTrue(reply.aborted)
                    else:client._finish(reply,callback)
                self.assertEqual(client.snapshot['temperature'],18.5)
                self.assertFalse(client.snapshot['busy']);self.assertFalse(client.snapshot['stale'])
                self.assertIn('Tokyo',client.snapshot['region'])

    def test_language_race_old_response_close_and_invalid_language(self):
        client,requests=self.create();self.locate(client,requests)
        old=requests.pop()[1]
        client.set_language('en')
        self.assertEqual(client.snapshot['language'],'en')
        old(dict(results=[dict(name='오래된 언어',country_code='JP',latitude=35.68,longitude=139.69)]))
        self.assertNotIn('오래된',client.snapshot['region'])
        new=requests.pop()[1]
        new(dict(results=[dict(name='Tokyo',country_code='JP',latitude=35.68,longitude=139.69)]))
        self.assertEqual(client.snapshot['region'],'Tokyo')
        client.set_language('ko');late=requests.pop()[1];client.close();before=dict(client.snapshot)
        late(dict(results=[dict(name='닫힌 뒤',country_code='JP',latitude=35.68,longitude=139.69)]))
        self.assertEqual(client.snapshot,before)
        with self.assertRaises(ValueError):client.set_language('xx')

    def test_language_switch_aborts_inflight_reply_and_preserves_temperature(self):
        client,requests=self.create();self.locate(client,requests)
        reply=Reply();client.reply=reply
        client.set_language('en')
        self.assertTrue(reply.aborted);self.assertIsNone(client.reply)
        self.assertEqual(client.snapshot['temperature'],18.5)
        self.assertIn('language=en',requests[-1][0])

    def test_language_change_during_location_and_weather_ignores_previous_generation(self):
        client,requests=self.create();client.refresh();old_location=requests.pop()[1]
        client.set_language('en');new_location=requests.pop()[1]
        location=dict(success=True,country_code='JP',city='Tokyo',latitude=35.68,longitude=139.69)
        old_location(location);self.assertEqual(requests,[])
        new_location(location);old_weather=requests.pop()[1]
        client.set_language('ko');new_weather=requests.pop()[1]
        old_weather(dict(current=dict(temperature_2m=99,time=time.time())))
        self.assertIsNone(client.snapshot['temperature'])
        new_weather(dict(current=dict(temperature_2m=18.5,time=time.time())))
        self.assertEqual(client.snapshot['temperature'],18.5)
        self.assertIn('language=ko',requests[-1][0])

    def test_missing_country_and_excess_results_keep_original_without_false_matching(self):
        client,requests=self.create();self.locate(client,requests)
        row=dict(name='도쿄',country_code='JP',latitude=35.68,longitude=139.69)
        requests.pop()[1](dict(results=[row]*11))
        self.assertIn('Tokyo',client.snapshot['region'])
        from weather import select_geocoded_region
        self.assertIsNone(select_geocoded_region(dict(latitude=35.68,longitude=139.69),dict(results=[row])))
        row['latitude']=10**400
        self.assertIsNone(select_geocoded_region(dict(country_code='JP',latitude=35.68,longitude=139.69),dict(results=[row])))

    def test_bounded_cache_reuses_same_language_and_location(self):
        client,requests=self.create()
        for index in range(20):
            self.locate(client,requests,city='City '+str(index))
            requests.pop()[1](dict(results=[dict(name='도시 '+str(index),country_code='JP',latitude=35.68,longitude=139.69)]))
        self.assertLessEqual(len(client._region_cache),16)
        self.locate(client,requests,city='City 19',expect_geo=False)
        self.assertEqual(len(requests),0)
        self.assertEqual(client.snapshot['region'],'도시 19')

    def test_no_private_coordinates_in_snapshot_and_limits_unchanged(self):
        client,requests=self.create();self.locate(client,requests)
        self.assertEqual((client.LIMIT,client.TIMEOUT_MS,client.INTERVAL_MS),(65536,8000,300000))
        self.assertFalse({'ip','latitude','longitude','coordinates'}&client.snapshot.keys())
        self.assertNotIn('35.68',json.dumps(client.snapshot));self.assertNotIn('139.69',json.dumps(client.snapshot))


if __name__=='__main__':unittest.main()
