"""날씨의 고정 안내만 번역하고 실제 지명과 출처의 고유 이름은 보존합니다."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from i18n import translate,set_language,get_language

class WeatherI18n32Tests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(set_language,get_language())
    def test_timeout_and_selected_location_sources_switch_both_languages(self):
        rows=[
            ('위치 또는 기온 조회 시간 초과','Location or temperature lookup timed out'),
            ('사용자 선택 지점 · Photon / OpenStreetMap','Selected place · Photon / OpenStreetMap'),
            ('사용자 지정 도시 · Open-Meteo / GeoNames','Selected city · Open-Meteo / GeoNames'),
        ]
        for language in ('ko','en','ko'):
            set_language(language)
            for korean,english in rows:
                with self.subTest(language=language,source=korean):
                    self.assertEqual(translate(korean),english if language=='en' else korean)
    def test_existing_network_statuses_and_source_notices_keep_exact_translations(self):
        rows=[
            ('위치 또는 기온 네트워크 조회 실패','Location / temperature network request failed'),
            ('네트워크 위치를 확인할 수 없습니다','Network location unavailable'),
            ('기온 조회 준비','Preparing weather lookup'),
            ('기온 조회 중','Loading temperature'),
            ('기온 조회 완료','Temperature updated'),
            ('기온 제공 자료 지연 · 이전 값','Weather data delayed · previous value'),
            ('기온 조회 지연 · 이전 값','Weather lookup delayed · previous value'),
            ('ipwho.is · 원문','ipwho.is · original name'),
            ('ipwho.is · 지명 검색 미일치 · 원문 보존','ipwho.is · no matching place name · original retained'),
            ('ipwho.is · 지역 번역 실패 · 원문 보존','ipwho.is · translation unavailable · original retained'),
        ]
        for language in ('ko','en'):
            set_language(language)
            for korean,english in rows:
                with self.subTest(language=language,source=korean):
                    self.assertEqual(translate(korean),english if language=='en' else korean)
    def test_place_names_and_provider_names_are_not_invented_translations(self):
        for language in ('ko','en'):
            set_language(language)
            for original in ('합성 장소 · 예시 구역','Synthetic Place / Example District','Photon / OpenStreetMap','Open-Meteo / GeoNames'):
                with self.subTest(language=language,original=original):
                    self.assertEqual(translate(original),original)
