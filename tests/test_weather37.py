"""합성 응답으로 자동 지역의 도시·행정구역 정합성만 검사합니다."""
import os
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtCore import QCoreApplication
from weather import WeatherClient, select_geocoded_region

APP = QCoreApplication.instance() or QCoreApplication([])


class WeatherRegion37Tests(unittest.TestCase):
    def setUp(self):
        # 공개 도시 중심점과 식별자를 사용하며 사용자 IP·위치는 읽지 않습니다.
        self.location = dict(city='Suwon', region='Gyeonggi-do', country_code='KR',
                             latitude=37.27818, longitude=127.03164)
        self.english = dict(id=1835553, name='Suwon', admin1='Gyeonggi-do', admin1_id=1841610,
                            country='South Korea', country_code='KR', latitude=37.27818, longitude=127.03164)
        self.localized = dict(self.english, name='수원시', admin1='경기도', country='대한민국')

    def client(self):
        client = WeatherClient(language='ko')
        self.addCleanup(client.close)
        client._location = dict(self.location)
        client._region = 'IP original'
        client.snapshot['region'] = 'IP original'
        patcher = patch.object(client, '_get')
        patcher.start()
        self.addCleanup(patcher.stop)
        return client

    def test_nearby_candidate_with_other_administration_is_rejected(self):
        wrong = dict(self.localized, id=12010348, admin1='충청남도', admin1_id=1845105)
        self.assertIsNone(select_geocoded_region(self.location, dict(results=[wrong])))
        self.assertEqual(select_geocoded_region(self.location, dict(results=[wrong, self.localized])),
                         '수원시 · 경기도 · 대한민국')

    def test_distant_homonym_is_not_substituted_for_suwon_city(self):
        village = dict(self.localized, id=11906993, name='수원', admin1='전라북도',
                       admin1_id=1845789, latitude=35.35881, longitude=126.53487)
        self.assertIsNone(select_geocoded_region(self.location, dict(results=[village])))
        self.assertEqual(select_geocoded_region(self.location, dict(results=[village, self.localized])),
                         '수원시 · 경기도 · 대한민국')

    def test_translation_is_published_only_after_same_city_and_admin_ids(self):
        client = self.client()
        client._geocode_done(dict(results=[self.localized]))
        self.assertEqual(client.snapshot['region'], 'IP original')
        _, callback = client._get.call_args.args
        callback(dict(results=[self.english]))
        self.assertEqual(client.snapshot['region'], '수원시 · 경기도 · 대한민국')
        self.assertEqual(client.snapshot['city_ref']['geonames_id'], 1835553)

    def test_mismatched_identity_or_admin_keeps_original_ip_label(self):
        for row in (dict(self.english, id=12010348),
                    dict(self.english, admin1_id=1845105),
                    dict(self.english, name='Different City')):
            with self.subTest(row=row):
                client = self.client()
                client._geocode_done(dict(results=[self.localized]))
                _, callback = client._get.call_args.args
                callback(dict(results=[row]))
                self.assertEqual(client.snapshot['region'], 'IP original')
                self.assertIsNone(client.snapshot['city_ref'])


if __name__ == '__main__':
    unittest.main()
