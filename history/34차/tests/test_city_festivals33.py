"""도시 신원·발표 일정·미발표·자료 변조 경계를 실제 JSON으로 검사합니다."""
from datetime import date, datetime
import copy
import hashlib
import importlib
import importlib.util
import json
import gzip
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


CITY = dict(provider='geonames', geonames_id=3028808, country_code='FR', confidence='selected', provenance='Open-Meteo / GeoNames')
SERIES = dict(id='wikidata:Q42369', title='칸 영화제', title_en='Cannes Film Festival', kind='film', country_code='FR',
              city_refs=[dict(wikidata_qid='Q39984', geonames_id=3028808)], month=5,
              source_url='https://www.wikidata.org/wiki/Q42369', license='CC0-1.0', status='catalog_only',item_role='series')
EVENT = dict(id='official:cannes:2027', series_id='wikidata:Q42369', title='칸 영화제', title_en='Cannes Film Festival',
             kind='film', country_code='FR', city_refs=[dict(wikidata_qid='Q39984', geonames_id=3028808)],
             dates=['2027-05-11', '2027-05-12', '2027-05-22'], date_precision='day', status='announced',
             time_conflict=False, source_url='https://www.festival-cannes.com/en/', license='factual-schedule',
             checked_at='2026-11-10T09:50:00+09:00', location_confidence='city_verified')


def write_bundle(target, series=None, events=None):
    files = []
    for folder, kind, rows, license_id in [('catalog', 'series', series if series is not None else [SERIES], 'CC0-1.0'),
                                         ('announced', 'occurrences', events if events is not None else [EVENT], 'factual-schedule')]:
        path = target / folder / 'FR.json'
        path.parent.mkdir(exist_ok=True)
        raw = (json.dumps(dict(schema_version=1, country_code='FR', license=license_id, **{kind: rows}), ensure_ascii=False) + '\n').encode('utf-8')
        path.write_bytes(raw)
        files.append(dict(path=folder+'/FR.json', bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), license=license_id))
    index = dict(schema_version=1, first_year=2026, last_year=2099, generated_at='2026-11-10T09:50:00+09:00',
                 coverage_status='partial', countries=[dict(code='FR', files=files)],
                 collection=dict(complete=False, series_count=1, truncated=False))
    (target/'index.json').write_text(json.dumps(index, ensure_ascii=False), encoding='utf-8')


class CityFestivalTests(unittest.TestCase):
    def setUp(self):
        # 누락 모듈을 성공으로 건너뛰지 않아 제어 RED 원인을 명확히 합니다.
        self.assertIsNotNone(importlib.util.find_spec('city_festivals'), '도시 행사 조회 기능이 아직 없습니다.')
        self.api = importlib.import_module('city_festivals')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name)
        write_bundle(self.target)
        self.root_patch = patch.object(self.api, '_root', return_value=self.target)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.api.clear_cache()
        self.addCleanup(self.api.clear_cache)

    def test_only_announced_discrete_days_match(self):
        self.assertEqual(self.api.city_events_for_date(date(2027,5,11), CITY, 'FR')[0]['kind'], 'film')
        self.assertEqual(self.api.city_events_for_date(date(2027,5,12), CITY, 'FR')[0]['local_date'], '2027-05-12')
        self.assertEqual(self.api.city_events_for_date(date(2027,5,13), CITY, 'FR'), [])
        self.assertEqual(self.api.city_events_for_date(date(2028,5,11), CITY, 'FR'), [])

    def test_series_month_does_not_create_future_occurrence(self):
        self.assertEqual(len(self.api.series_for_city(CITY, 'FR')), 1)
        self.assertEqual(self.api.city_events_for_date(date(2099,5,11), CITY, 'FR'), [])
        coverage = self.api.city_coverage(CITY, 'FR', 2099)
        self.assertTrue(coverage['catalog_only'])
        self.assertEqual(coverage['catalog_series_count'], 1)
        self.assertEqual(coverage['announced_occurrences_count'], 0)

    def test_foreign_country_and_nearby_coordinates_never_match_city(self):
        foreign = dict(CITY, country_code='US')
        with self.assertRaises(ValueError): self.api.city_events_for_date(date(2027,5,11), foreign, 'FR')
        self.assertEqual(self.api.series_for_city(dict(country_code='FR', latitude=43.55, longitude=7.018), 'FR'), [])
        self.assertEqual(self.api.series_for_city(dict(CITY, geonames_id=9999999), 'FR'), [])

    def test_qid_and_geonames_must_both_match_when_both_present(self):
        self.assertEqual(len(self.api.series_for_city(dict(CITY, wikidata_qid='Q39984'), 'FR')), 1)
        self.assertEqual(self.api.series_for_city(dict(CITY, wikidata_qid='Q90'), 'FR'), [])
        self.assertEqual(len(self.api.series_for_city(dict(country_code='FR', wikidata_qid='Q39984'), 'FR')), 1)

    def test_provider_namespace_and_estimated_selection_are_preserved(self):
        self.assertEqual(self.api.series_for_city(dict(country_code='FR', provider='photon', id=3028808), 'FR'), [])
        event = self.api.city_events_for_date(date(2027,5,11), dict(CITY, confidence='estimated'), 'FR')[0]
        self.assertEqual(event['selection_confidence'], 'estimated')
        self.assertEqual(event['location_confidence'], 'city_verified')
        self.assertEqual(event['source_url'], EVENT['source_url'])

    def test_cancelled_and_month_precision_do_not_activate_theme(self):
        cancelled = dict(EVENT, status='cancelled')
        write_bundle(self.target, events=[cancelled])
        self.assertEqual(self.api.city_events_for_date(date(2027,5,11), CITY, 'FR'), [])
        self.api.clear_cache()
        write_bundle(self.target, events=[dict(EVENT, date_precision='month')])
        with self.assertRaises(ValueError): self.api.city_events_for_date(date(2027,5,11), CITY, 'FR')

    def test_invalid_dates_and_types_are_rejected(self):
        for value in [date(2025,12,31), date(2100,1,1), datetime(2027,5,11), '2027-05-11']:
            with self.subTest(value=value), self.assertRaises(ValueError): self.api.city_events_for_date(value, CITY, 'FR')
        for year in [True, 2025, 2100]:
            with self.assertRaises(ValueError): self.api.city_coverage(CITY, 'FR', year)

    def test_hash_tampering_and_path_traversal_fail_closed(self):
        p=self.target/'catalog/FR.json'; p.write_bytes(p.read_bytes()+b' ')
        with self.assertRaises(ValueError): self.api.series_for_city(CITY, 'FR')
        self.api.clear_cache(); write_bundle(self.target)
        index=json.loads((self.target/'index.json').read_text(encoding='utf-8'))
        index['countries'][0]['files'][0]['path']='../FR.json'
        (self.target/'index.json').write_text(json.dumps(index), encoding='utf-8')
        with self.assertRaises(ValueError): self.api.series_for_city(CITY, 'FR')

    def test_mutating_return_values_does_not_change_cached_catalog(self):
        self.api.series_for_city(CITY, 'FR')[0]['city_refs'].clear()
        event=self.api.city_events_for_date(date(2027,5,11), CITY, 'FR')[0]
        event['dates'].clear()
        self.assertEqual(len(self.api.series_for_city(CITY, 'FR')), 1)
        self.assertEqual(len(self.api.city_events_for_date(date(2027,5,11), CITY, 'FR')), 1)

    def test_coverage_counts_events_and_dates_separately(self):
        coverage=self.api.city_coverage(CITY, 'FR', 2027)
        self.assertEqual(coverage['catalog_series_count'],1)
        self.assertEqual(coverage['announced_occurrences_count'],1)
        self.assertEqual(coverage['announced_dates_count'],3)
        self.assertEqual(coverage['coverage_status'],'partial')
        self.assertFalse(coverage['catalog_only'])

    def test_unclassified_and_editions_stay_in_catalog_without_becoming_series(self):
        unknown=dict(SERIES,id='wikidata:Q900001',item_role='unclassified')
        edition=dict(SERIES,id='wikidata:Q900002',item_role='edition')
        write_bundle(self.target,series=[SERIES,unknown,edition])
        self.assertEqual(len(self.api.series_for_city(CITY,'FR')),3)
        info=self.api.city_coverage(CITY,'FR',2027)
        self.assertEqual(info['catalog_items_count'],3)
        self.assertEqual(info['series_count'],1)
        self.assertEqual(info['edition_count'],1)
        self.assertEqual(info['unclassified_count'],1)

    def test_year_query_preserves_original_date_set(self):
        self.assertTrue(hasattr(self.api,'announced_events_for_year'),'연도별 발표 일정 기능이 아직 없습니다.')
        rows=self.api.announced_events_for_year(CITY,'FR',2027)
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['dates'],EVENT['dates'])
        self.assertEqual(rows[0]['all_dates'],EVENT['dates'])
        self.assertEqual(self.api.announced_events_for_year(CITY,'FR',2099),[])

    def test_cache_revision_changes_only_after_verified_activation(self):
        self.assertTrue(hasattr(self.api,'configure_city_cache'),'검증 캐시 기능이 아직 없습니다.')
        with tempfile.TemporaryDirectory() as directory:
            data_dir=Path(directory)
            self.api.configure_city_cache(data_dir)
            self.addCleanup(self.api.configure_city_cache,None)
            before=self.api.get_city_catalog_revision()
            generation=data_dir/'city-festivals/generations'/('a'*64)
            generation.mkdir(parents=True)
            write_bundle(generation,events=[dict(EVENT,title='갱신한 영화제')])
            self.api.activate_country_cache('FR',generation)
            self.assertNotEqual(self.api.get_city_catalog_revision(),before)
            self.assertEqual(self.api.city_events_for_date(date(2027,5,11),CITY,'FR')[0]['title'],'갱신한 영화제')
            self.api.configure_city_cache(data_dir)
            self.assertEqual(self.api.city_events_for_date(date(2027,5,11),CITY,'FR')[0]['title'],'갱신한 영화제')

    def test_cache_coverage_uses_updated_source_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            data_dir=Path(directory);self.api.configure_city_cache(data_dir)
            self.addCleanup(self.api.configure_city_cache,None)
            generation=data_dir/'city-festivals/generations'/('b'*64);generation.mkdir(parents=True)
            write_bundle(generation)
            index=json.loads((generation/'index.json').read_text(encoding='utf-8'))
            index['generated_at']='2026-11-11T10:00:00+09:00'
            (generation/'index.json').write_text(json.dumps(index),encoding='utf-8')
            self.api.activate_country_cache('FR',generation)
            self.assertEqual(self.api.city_coverage(CITY,'FR',2027)['source_checked_at'],'2026-11-11T10:00:00+09:00')
            self.api.configure_city_cache(data_dir)
            self.assertEqual(self.api.city_coverage(CITY,'FR',2027)['source_checked_at'],'2026-11-11T10:00:00+09:00')

    def test_gzip_archive_is_bounded_and_single_stream(self):
        index=json.loads((self.target/'index.json').read_text(encoding='utf-8'))
        entry=index['countries'][0]['files'][0]
        plain=(self.target/entry['path']).read_bytes();payload=gzip.compress(plain,mtime=0)
        path=self.target/(entry['path']+'.gz');path.write_bytes(payload)
        entry.update(path=entry['path']+'.gz',bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest())
        (self.target/'index.json').write_text(json.dumps(index),encoding='utf-8')
        self.assertEqual(len(self.api.series_for_city(CITY,'FR')),1)
        self.api.clear_cache();bad=payload+gzip.compress(b'{}',mtime=0);path.write_bytes(bad)
        entry.update(bytes=len(bad),sha256=hashlib.sha256(bad).hexdigest())
        (self.target/'index.json').write_text(json.dumps(index),encoding='utf-8')
        with self.assertRaises(ValueError):self.api.series_for_city(CITY,'FR')


class CityFestivalUpdateTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('city_festival_updates'),'비동기 자료 갱신 기능이 아직 없습니다.')
        self.updates=importlib.import_module('city_festival_updates')

    def test_downloaded_country_must_match_index_hash_and_license(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory);write_bundle(target)
            index=json.loads((target/'index.json').read_text(encoding='utf-8'))
            meta=index['countries'][0]['files'][0];raw=(target/meta['path']).read_bytes()
            result=self.updates.validate_download(raw,meta,'FR')
            self.assertEqual(result['country_code'],'FR')
            with self.assertRaises(ValueError):self.updates.validate_download(raw+b' ',meta,'FR')
            with self.assertRaises(ValueError):self.updates.validate_download(raw,meta,'US')

    def test_update_url_does_not_accept_another_owner_or_scheme(self):
        for url in ['http://raw.githubusercontent.com/PUVKID/Codex-Orbit/main/assets/city-festivals/index.json',
                    'https://raw.githubusercontent.com/other/repo/main/assets/city-festivals/index.json',
                    'https://raw.githubusercontent.com/PUVKID/Codex-Orbit/main/assets/city-festivals/../x.py']:
            self.assertFalse(self.updates.allowed_url(url))
        self.assertTrue(self.updates.allowed_url(self.updates.BASE_URL+'index.json'))

    def test_constructor_and_close_do_not_start_network(self):
        from PySide6.QtWidgets import QApplication
        app=QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as directory:
            updater=self.updates.CityFestivalUpdater(Path(directory))
            self.addCleanup(importlib.import_module('city_festivals').configure_city_cache,None)
            self.assertFalse(updater.busy);self.assertIsNone(updater.reply)
            updater.close();self.assertTrue(updater.closed)
            self.assertFalse(updater.refresh('FR'))

    def test_attempt_write_failure_is_reported_without_network(self):
        from PySide6.QtWidgets import QApplication
        app=QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as directory:
            data_dir=Path(directory);blocker=data_dir/'city-festivals/attempts/FR.json';blocker.mkdir(parents=True)
            updater=self.updates.CityFestivalUpdater(data_dir)
            self.addCleanup(importlib.import_module('city_festivals').configure_city_cache,None)
            failures=[];updater.failed.connect(failures.append)
            self.assertFalse(updater.refresh('FR'))
            self.assertTrue(failures);self.assertFalse(updater.busy);self.assertIsNone(updater.reply)
            updater.close()


class CityFestivalGeneratorTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('city_generator',ROOT/'tools/generate_city_festivals.py')
        self.generator=importlib.util.module_from_spec(spec); spec.loader.exec_module(self.generator)

    def followup_fixture(self, target):
        checkpoint=target/'evidence/checkpoint';checkpoint.mkdir(parents=True)
        started=datetime.now(self.generator.timezone.utc)-self.generator.timedelta(hours=2)
        first=dict(recorded_at_kst=started.isoformat(),session='session',task='task')
        raw=self.generator.encode(first);(checkpoint/'requests.jsonl').write_bytes(raw)
        now=datetime.now(self.generator.timezone.utc)
        value=dict(schema_version=1,phase_id='city-join-paris-1',session='session',task='task',
                   checkpoint='evidence/checkpoint',original_started_at=started.isoformat(),
                   original_deadline=(started+self.generator.timedelta(seconds=2700)).isoformat(),
                   original_exit_code=1,original_requests_bytes=len(raw),original_requests_sha256=hashlib.sha256(raw).hexdigest(),
                   started_at=now.isoformat(),deadline=(now+self.generator.timedelta(seconds=1800)).isoformat(),
                   duration_seconds=1800,allowed_request_prefixes=['city-direct-v3-','city-parent-v3-','paris-offset-'])
        manifest=target/'evidence/followup.json';manifest.write_bytes(self.generator.encode(value))
        return checkpoint,manifest,value

    def test_followup_window_is_fixed_and_cached_metadata_needs_no_network(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory);checkpoint,manifest,value=self.followup_fixture(target)
            with patch.object(self.generator,'ROOT',target):
                collector=self.generator.Collector(checkpoint,followup_window=manifest)
                self.generator.save(checkpoint/'metadata-known.json',{'cached':True})
                with patch.object(self.generator,'urlopen') as network:
                    self.assertEqual(collector.query('metadata-known','query'),{'cached':True})
                    with self.assertRaises(ValueError):collector.query('metadata-missing','query')
                    with self.assertRaises(ValueError):collector.fetch('paris-offset-0','https://example.com/records')
                    network.assert_not_called()
                value['deadline']=(datetime.fromisoformat(value['deadline'])+self.generator.timedelta(seconds=1)).isoformat()
                manifest.write_bytes(self.generator.encode(value))
                with self.assertRaises(ValueError):self.generator.Collector(checkpoint,followup_window=manifest)

    def test_followup_rejects_log_tampering_and_cannot_reset_start(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory);checkpoint,manifest,value=self.followup_fixture(target)
            with patch.object(self.generator,'ROOT',target):
                self.generator.Collector(checkpoint,followup_window=manifest)
                value['started_at']=(datetime.fromisoformat(value['started_at'])+self.generator.timedelta(seconds=1)).isoformat()
                value['deadline']=(datetime.fromisoformat(value['deadline'])+self.generator.timedelta(seconds=1)).isoformat()
                manifest.write_bytes(self.generator.encode(value))
                with self.assertRaises(ValueError):self.generator.Collector(checkpoint,followup_window=manifest)
                (checkpoint/'requests.jsonl').write_bytes(b'{}\n')
                with self.assertRaises(ValueError):self.generator.Collector(checkpoint,followup_window=manifest)

    def test_offline_fetch_and_expired_followup_do_not_use_network(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory);checkpoint,manifest,value=self.followup_fixture(target)
            with patch.object(self.generator,'ROOT',target),patch.object(self.generator,'urlopen') as network:
                collector=self.generator.Collector(checkpoint,offline=True)
                with self.assertRaises(ValueError):collector.fetch('paris-offset-0','https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records')
                value['started_at']=(datetime.now(self.generator.timezone.utc)-self.generator.timedelta(seconds=1900)).isoformat()
                value['deadline']=(datetime.fromisoformat(value['started_at'])+self.generator.timedelta(seconds=1800)).isoformat()
                manifest.write_bytes(self.generator.encode(value))
                collector=self.generator.Collector(checkpoint,followup_window=manifest)
                with self.assertRaises(TimeoutError):collector.query('city-parent-v3-'+'a'*20,'query')
                network.assert_not_called()

    def test_only_failed_uncached_parent_batch_is_split(self):
        places=['Q'+str(number) for number in range(100,300)]
        digest=lambda batch:hashlib.sha256(' '.join(batch).encode()).hexdigest()[:20]
        failed='city-parent-v3-'+digest(places)
        for cached in (False,True):
            with self.subTest(parent_cached=cached),tempfile.TemporaryDirectory() as directory:
                checkpoint=Path(directory)
                self.generator.save(checkpoint/'requests.jsonl',dict(name=failed,phase='failure',error_type='TimeoutError'))
                if cached:self.generator.save(checkpoint/(failed+'.json'),{'results':{'bindings':[]}})
                names=[]
                class FakeCollector:
                    def query(self,name,query):
                        names.append(name)
                        return {'results':{'bindings':[]}}
                collector=FakeCollector();collector.checkpoint=checkpoint
                self.assertEqual(self.generator.collect_cities(collector,places),{})
                expected=['settlement-types-v2-limit20001','city-direct-v3-'+digest(places)]
                expected+=([failed] if cached else ['city-parent-v3-'+digest(places[:100]),'city-parent-v3-'+digest(places[100:])])
                self.assertEqual(names,expected)

    def test_uncached_parent_batches_are_bounded_without_timeout_probe(self):
        places=['Q'+str(number) for number in range(400,600)]
        digest=lambda batch:hashlib.sha256(' '.join(batch).encode()).hexdigest()[:20]
        original='city-parent-v3-'+digest(places)
        for cached in (False,True):
            with self.subTest(parent_cached=cached),tempfile.TemporaryDirectory() as directory:
                checkpoint=Path(directory)
                self.generator.save(checkpoint/'requests.jsonl',dict(name='unrelated',phase='success'))
                if cached:self.generator.save(checkpoint/(original+'.json'),{'results':{'bindings':[]}})
                calls=[]
                class FakeCollector:
                    def query(self,name,query):
                        calls.append((name,query))
                        return {'results':{'bindings':[]}}
                collector=FakeCollector();collector.checkpoint=checkpoint
                self.generator.collect_cities(collector,places)
                parent=[(name,query) for name,query in calls if name.startswith('city-parent-')]
                self.assertEqual([name for name,query in parent],[original] if cached else
                                 ['city-parent-v3-'+digest(places[:100]),'city-parent-v3-'+digest(places[100:])])
                if not cached:
                    for name,query in parent:
                        group=self.generator.re.search(r'VALUES\s+\?place\s*\{([^}]+)\}',query)
                        self.assertLessEqual(len(self.generator.re.findall(r'wd:Q[0-9]+',group.group(1))),100)
                self.assertIn('city-direct-v3-'+digest(places),[name for name,query in calls])

    def test_metadata_keeps_month_without_inventing_a_date(self):
        self.assertTrue(hasattr(self.generator,'normalize_metadata'),'메타 정규화 기능이 아직 없습니다.')
        rows=[{'item':{'value':'http://www.wikidata.org/entity/Q42369'},'en':{'value':'Cannes Film Festival'},
               'ko':{'value':'칸 영화제'},'cc':{'value':'FR'},'place':{'value':'http://www.wikidata.org/entity/Q39984'},
               'month':{'value':'http://www.wikidata.org/entity/Q119'},'typeLabel':{'value':'film festival'}}]
        row=self.generator.normalize_metadata(rows)['Q42369']
        self.assertEqual(row['kind'],'film'); self.assertNotIn('dates',row)
        self.assertEqual(row['location_qids'],['Q39984'])

    def test_unknown_classification_is_not_default_series(self):
        source={'item':{'value':'http://www.wikidata.org/entity/Q900001'},'en':{'value':'Unknown cultural item'}}
        row=self.generator.normalize_metadata([source])['Q900001']
        self.assertEqual(row['item_role'],'unclassified')

    def test_general_festival_type_alone_does_not_confirm_series(self):
        source={'item':{'value':'http://www.wikidata.org/entity/Q900001'},'type':{'value':'http://www.wikidata.org/entity/Q132241'},
                'typeLabel':{'value':'festival'}}
        row=self.generator.normalize_metadata([source])['Q900001']
        self.assertEqual(row['item_role'],'unclassified')
        self.assertEqual(row['type_qids'],['Q132241'])
        self.assertEqual(row['type_labels'],['festival'])

    def test_explicit_recurring_event_type_confirms_series(self):
        source={'item':{'value':'http://www.wikidata.org/entity/Q900001'},'typeLabel':{'value':'recurring event'}}
        row=self.generator.normalize_metadata([source])['Q900001']
        self.assertEqual(row['item_role'],'series')

    def test_series_references_are_classified_across_metadata_batches(self):
        ids=['Q'+str(number) for number in range(1,202)]
        with tempfile.TemporaryDirectory() as directory:
            checkpoint=Path(directory)
            self.generator.save(checkpoint/'requests.jsonl',dict(name='initial',phase='success'))
            generator=self.generator
            class FakeCollector:
                def query(self,name,query):
                    group=generator.re.search(r'VALUES\s+\?item\s*\{([^}]+)\}',query)
                    values=generator.re.findall(r'wd:(Q[0-9]+)',group.group(1));rows=[]
                    for qid in values:
                        row={'item':{'value':'http://www.wikidata.org/entity/'+qid},'typeLabel':{'value':'festival'}}
                        if qid=='Q1':row['series']={'value':'http://www.wikidata.org/entity/Q201'}
                        rows.append(row)
                    return {'results':{'bindings':rows}}
            collector=FakeCollector();collector.checkpoint=checkpoint
            rows=generator.collect_metadata(collector,ids)
            self.assertEqual(len(rows),201)
            self.assertEqual(rows['Q201']['item_role'],'series')
            self.assertEqual(rows['Q1']['item_role'],'unclassified')
            self.assertEqual(rows['Q1']['parent_series'],['Q201'])

    def test_paris_consistent_discrete_occurrences_are_not_interpolated(self):
        self.assertTrue(hasattr(self.generator,'normalize_paris'),'공식 일정 정규화 기능이 아직 없습니다.')
        raw=dict(id='1',title='Atelier',address_city='Paris',date_start='2026-11-11T20:30:00+02:00',
                 date_end='2026-11-18T21:45:00+02:00',
                 occurrences='2026-11-11T20:30:00+02:00_2026-11-11T21:45:00+02:00;2026-11-18T20:30:00+02:00_2026-11-18T21:45:00+02:00',
                 date_description='Le mercredi 11 novembre 2026 et le mercredi 18 novembre 2026',
                 url='https://www.paris.fr/evenements/atelier-1',lat_lon=dict(lat=48.85,lon=2.35),updated_at='2026-11-01T00:00:00Z')
        row=self.generator.normalize_paris(raw,'2026-11-10T10:00:00+09:00')
        self.assertEqual(row['dates'],['2026-11-11','2026-11-18'])
        self.assertFalse(row['time_conflict']); self.assertEqual(row['license'],'ODbL-1.0')
        self.assertNotIn('2026-11-12',row['dates'])
        self.assertIsNone(self.generator.normalize_paris(dict(raw,address_city='Lyon'),'2026-11-10T10:00:00+09:00'))

    def test_paris_unverified_offset_conflicts_never_activate_dates(self):
        row=dict(id='999999',title='Unknown',address_city='Paris',date_start='2026-11-11T20:30:00+00:00',
                 date_end='2026-11-11T21:45:00+00:00',occurrences='2026-11-11T20:30:00+02:00_2026-11-11T21:45:00+02:00',
                 url='https://www.paris.fr/evenements/unknown-999999')
        self.assertIsNone(self.generator.normalize_paris(row,'2026-11-10T10:00:00+09:00'))

    def test_paris_confirmed_page_id_and_day_allow_only_that_day(self):
        row=dict(id='126680',title='Samarpanam',address_city='Paris',date_start='2026-11-11T20:30:00+00:00',
                 date_end='2026-11-11T21:45:00+00:00',occurrences='2026-11-11T20:30:00+02:00_2026-11-11T21:45:00+02:00',
                 url='https://www.paris.fr/evenements/samarpanam-danse-d-inde-du-sud-126680')
        accepted=self.generator.normalize_paris(row,'2026-11-10T10:00:00+09:00')
        self.assertEqual(accepted['dates'],['2026-11-11']);self.assertTrue(accepted['time_conflict'])
        self.assertEqual(accepted['date_evidence'],'official_page_crosschecked')
        self.assertIsNone(self.generator.normalize_paris(dict(row,occurrences='2026-11-12T20:30:00+02:00_2026-11-12T21:45:00+02:00'),'2026-11-10T10:00:00+09:00'))

    def test_paris_missing_bounds_and_date_contradictions_are_not_filled(self):
        row=dict(id='3',title='Unknown',address_city='Paris',date_start='2026-11-11T20:30:00+02:00',
                 date_end='2026-11-11T21:45:00+02:00',occurrences='2026-11-12T20:30:00+02:00_2026-11-12T21:45:00+02:00',
                 url='https://www.paris.fr/evenements/unknown-3')
        self.assertIsNone(self.generator.normalize_paris(row,'2026-11-10T10:00:00+09:00'))
        self.assertIsNone(self.generator.normalize_paris(dict(row,date_start=None),'2026-11-10T10:00:00+09:00'))

    def test_paris_unverifiable_or_missing_schedule_is_not_filled(self):
        self.assertTrue(hasattr(self.generator,'normalize_paris'),'공식 일정 정규화 기능이 아직 없습니다.')
        row=dict(id='2',title='Unknown',address_city='Paris',date_start='2026-01-01T00:00:00+00:00',
                 date_end='2099-01-01T00:00:00+00:00',occurrences='',url='https://www.paris.fr/evenements/unknown-2')
        self.assertIsNone(self.generator.normalize_paris(row,'2026-11-10T10:00:00+09:00'))


if __name__ == '__main__': unittest.main()
