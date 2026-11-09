"""동봉한 국가 행사 자료와 날짜·언어·무결성 경계를 검사합니다."""
import hashlib,json,sys,unittest
from datetime import date,datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import holiday_calendar as calendar

class CountryCalendarTests(unittest.TestCase):
    def test_country_names_languages_and_aliases(self):
        self.assertEqual(len(calendar.available_countries()),250)
        for query,code in [('한국','KR'),('USA','US'),('UK','GB'),('대만','TW')]:
            self.assertIn(code,[r['code'] for r in calendar.find_countries(query)])
        self.assertEqual(calendar.normalize_country('uk'),'GB')
        for value in ('../KR','KOR','',None):
            with self.assertRaises(ValueError):calendar.normalize_country(value)

    def test_actual_country_specific_holidays(self):
        kr=calendar.event_for_date(date(2026,2,17),'KR')
        self.assertIn('설날',kr['title']);self.assertEqual(kr['kind'],'lunar_new_year')
        us=calendar.event_for_date(date(2026,7,4),'US')
        self.assertIn('Independence',us['title']);self.assertEqual(us['country_code'],'US')
        self.assertIsNone(calendar.event_for_date(date(2026,12,25),'JP'))
        self.assertIn('Christmas',calendar.event_for_date(date(2026,12,25),'US')['title'])

    def test_bounds_unsupported_and_future_limitations_are_distinct(self):
        self.assertFalse(calendar.country_status('ZZ')['supported'])
        self.assertIsNone(calendar.event_for_date(date(2026,1,1),'ZZ'))
        self.assertTrue(calendar.country_status('KR',2099)['future_rules_may_change'])
        india=calendar.country_status('IN',2099)
        self.assertEqual(india['status'],'limited');self.assertTrue(india['warnings'])
        for year in (True,2025,2100):
            with self.assertRaises(ValueError):calendar.country_status('KR',year)
        for value in (date(2025,12,31),date(2100,1,1),datetime(2026,1,1)):
            with self.assertRaises(ValueError):calendar.event_for_date(value)

    def test_returned_metadata_cannot_mutate_cached_source(self):
        rows=calendar.available_countries();rows[0]['name']='changed'
        self.assertNotEqual(calendar.available_countries()[0]['name'],'changed')
        status=calendar.country_status('IN',2099);status['warnings'].clear()
        self.assertTrue(calendar.country_status('IN',2099)['warnings'])

    def test_every_shipped_file_hash_date_and_year(self):
        index=json.loads((calendar._root()/'index.json').read_text(encoding='utf8'))
        total=0
        for row in index['countries']:
            raw=(calendar._root()/row['file']).read_bytes()
            self.assertEqual(len(raw),row['bytes']);self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            data=json.loads(raw);self.assertEqual(data['country_code'],row['code'])
            self.assertEqual(set(data['years']),{str(y) for y in range(2026,2100)})
            for year,entry in data['years'].items():
                self.assertIn(entry['status'],('computed','limited'))
                for day,event in entry['events'].items():
                    self.assertEqual(date.fromisoformat(day).year,int(year))
                    self.assertTrue(event['names']);self.assertTrue(event['categories'])
                    self.assertTrue(all(isinstance(n,str) and n.strip() for n in event['names']))
                    total+=1
        self.assertEqual(total,246906)

if __name__=='__main__':unittest.main()
