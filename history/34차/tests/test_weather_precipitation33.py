"""강수량과 집계 간격의 유효성 및 지역 경계를 합성 응답으로 검사합니다."""
import os, sys, time, unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtWidgets import QApplication
from weather import WeatherClient
from app import weather_widget_text
from i18n import set_language

APP = QApplication.instance() or QApplication([])
CITY = dict(name='Synthetic City', admin1='Synthetic State', country='United States', country_code='US', latitude=40., longitude=-75.)

class Precipitation33Tests(unittest.TestCase):
    def create(self):
        client = WeatherClient(location_override=CITY)
        self.addCleanup(client.close)
        requests = []
        patcher = patch.object(client, '_get', side_effect=lambda url, callback: requests.append((url, callback)))
        patcher.start(); self.addCleanup(patcher.stop)
        return client, requests

    def payload(self, amount=0., interval=900, unit='mm'):
        return dict(current=dict(time=time.time(), temperature_2m=12, precipitation=amount, interval=interval), current_units=dict(precipitation=unit))

    def test_request_asks_for_precipitation_in_mm(self):
        client, requests = self.create(); client.refresh()
        query = parse_qs(urlparse(requests[-1][0]).query)
        self.assertIn('precipitation', query['current'][0].split(','))
        self.assertEqual(query['precipitation_unit'], ['mm'])

    def test_valid_zero_positive_and_provider_intervals_are_preserved(self):
        client, _ = self.create()
        for amount, interval in [(0., 900), (2.75, 3600)]:
            with self.subTest(amount=amount, interval=interval):
                client._weather_done(self.payload(amount, interval))
                self.assertEqual(client.snapshot['precipitation'], amount)
                self.assertEqual(client.snapshot['precipitation_interval_seconds'], interval)

    def test_missing_invalid_amount_unit_or_interval_is_unknown(self):
        client, _ = self.create()
        for amount, interval, unit in [(None,900,'mm'), (True,900,'mm'), (-1,900,'mm'), (float('inf'),900,'mm'), (1,None,'mm'), (1,True,'mm'), (1,0,'mm'), (1,900,'inch'), (1,900,None)]:
            with self.subTest(amount=amount, interval=interval, unit=unit):
                client._weather_done(self.payload(amount, interval, unit))
                self.assertIsNone(client.snapshot['precipitation'])
                self.assertEqual(client.snapshot['temperature'],12)

    def test_new_location_clears_precipitation_and_old_callback_is_ignored(self):
        client, requests = self.create(); client.refresh(); late = requests[-1][1]
        client._weather_done(self.payload(2.)); client.set_location_override(None)
        for key in ('precipitation','precipitation_interval_seconds'):
            self.assertIsNone(client.snapshot[key])
        late(self.payload(8.)); self.assertIsNone(client.snapshot['precipitation'])
        self.assertEqual(requests[-1][0], 'https://ipwho.is/')

    def test_automatic_region_change_clears_previous_rain(self):
        client, _ = self.create(); client.set_location_override(None)
        region=dict(success=True,city='Synthetic A',country_code='US',latitude=40.,longitude=-75.)
        client._location_done(region); client._weather_done(self.payload(2.))
        client._location_done(dict(region,city='Synthetic B',latitude=41.))
        self.assertIsNone(client.snapshot['precipitation'])
        self.assertIsNone(client.snapshot['precipitation_interval_seconds'])

    def test_display_localizes_interval_distinguishes_zero_unknown_and_stale(self):
        self.addCleanup(set_language,'ko')
        for language, label in [('ko','강수'),('en','Rain')]:
            set_language(language)
            _, extras=weather_widget_text(dict(temperature=12, humidity=43, precipitation=0.,precipitation_interval_seconds=900))
            self.assertIn(label,extras[0]); self.assertIn('0 mm',extras[0]); self.assertIn('15',extras[0])
            self.assertNotIn('현지 시각',extras[0]); self.assertNotIn('Local time',extras[0])
            _, missing=weather_widget_text(dict(temperature=None,humidity=None))
            self.assertIn('—',missing[0]); self.assertNotIn('0 mm',missing[0])
            primary, stale=weather_widget_text(dict(temperature=12,stale=True,precipitation=2.,precipitation_interval_seconds=3600))
            self.assertIn('이전' if language=='ko' else 'Earlier',stale[0])

    def test_display_truncates_without_changing_original_observations(self):
        from app import weather_number_text,percentage_text
        self.assertEqual(weather_number_text(98.7899),'98.78')
        self.assertEqual(weather_number_text(0.00999),'0')
        self.assertEqual(weather_number_text(-1.239),'-1.23')
        raw=dict(temperature=12.3499,humidity=98.7899,precipitation=0.00999,precipitation_interval_seconds=900)
        before=dict(raw);primary,extras=weather_widget_text(raw)
        self.assertEqual(raw,before);self.assertIn('12.34',primary);self.assertIn('98.8%',extras[0])
        for value,expected in [(1.25,'1.3%'),(100,'100.0%'),(99.99,'약 100.0%'),(0,'0.0%'),(None,'—')]:
            with self.subTest(percent=value):self.assertEqual(percentage_text(value),expected)
