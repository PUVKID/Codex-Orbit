"""도시 식별자는 선택·동일 국가·동일 이름 근거가 있을 때만 전달합니다."""
import os,sys,unittest
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication
from weather import WeatherClient,select_geocoded_city_ref
APP=QApplication.instance() or QApplication([])
CITY=dict(name='Example City',admin1='Example State',country='Example',country_code='US',latitude=40.,longitude=-75.,id=123)
class WeatherCityRef33Tests(unittest.TestCase):
    def client(self,value):
        client=WeatherClient(location_override=value);self.addCleanup(client.close)
        patcher=patch.object(client,'_get');patcher.start();self.addCleanup(patcher.stop);return client
    def test_selected_geonames_identifier_has_selected_provenance(self):
        client=self.client(CITY);ref=client.snapshot['city_ref']
        self.assertEqual(ref['geonames_id'],123);self.assertEqual(ref['confidence'],'selected');self.assertEqual(ref['country_code'],'US')
    def test_photon_place_is_not_forced_to_a_geonames_city(self):
        client=self.client(dict(CITY,display_name='Example Place',address={'city':'Example City'}))
        self.assertIsNone(client.snapshot['city_ref'])
    def test_estimated_city_requires_name_country_and_identifier_not_only_nearby_coordinates(self):
        location=dict(city='Example City',country_code='US',latitude=40.,longitude=-75.)
        row=dict(CITY)
        ref=select_geocoded_city_ref(location,dict(results=[row]))
        self.assertEqual(ref['confidence'],'estimated');self.assertEqual(ref['geonames_id'],123)
        for changed in [dict(row,name='Different City'),dict(row,country_code='CA'),dict(row,id=True),dict(row,id=None)]:
            with self.subTest(row=changed):self.assertIsNone(select_geocoded_city_ref(location,dict(results=[changed])))
    def test_automatic_return_clears_selected_city_reference(self):
        client=self.client(CITY);client.set_location_override(None)
        self.assertIsNone(client.snapshot['city_ref']);self.assertIsNone(client.location_override)

    def test_localized_and_english_rows_must_have_the_same_identifier(self):
        client=self.client(None)
        client._location=dict(city='Example City',country_code='US',latitude=40.,longitude=-75.)
        localized=dict(CITY,name='합성시')
        client._geocode_done(dict(results=[localized]))
        url,callback=client._get.call_args.args
        self.assertIn('language=en',url);self.assertIn('countryCode=US',url)
        label=client.snapshot['region'];callback(dict(results=[CITY]))
        self.assertEqual(client.snapshot['city_ref']['geonames_id'],123)
        self.assertEqual(client.snapshot['region'],label)
        client._city_ref=None;client._geocode_done(dict(results=[localized]))
        _,callback=client._get.call_args.args;callback(dict(results=[dict(CITY,id=456)]))
        self.assertIsNone(client.snapshot['city_ref'])
    def test_identity_lookup_failure_does_not_invalidate_fresh_weather(self):
        client=self.client(None);client.snapshot.update(temperature=12,stale=False)
        client._stage='geocode_identity';client._request_failed('synthetic identity lookup failure')
        self.assertFalse(client.snapshot['stale']);self.assertEqual(client.snapshot['temperature'],12)
        self.assertIsNone(client.snapshot['city_ref'])
