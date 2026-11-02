"""29차 기능의 실제 기록 분리·표시 정리·개인정보 제외 계약입니다."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
features = __import__('orbit_features') if importlib.util.find_spec('orbit_features') else None


class FeatureTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(features, '29차 기능 저장소 API가 아직 없습니다.')
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.store = features.FeatureStore(self.root)

    def event(self, identity='e1', **extra):
        return {'id': identity, 'target': 'agent', 'chat_name': '🔄 실제 채팅 29',
                'time': '2026-11-02T00:00:00Z', 'kind': 'settings',
                'before': {'model': 'sol', 'effort': 'medium'},
                'after': {'model': 'astra', 'effort': 'medium'}, **extra}

    def test_emoji_clusters_leave_real_words_numbers_and_original_event(self):
        for raw, expected in [('🔄 프로젝트 29 👨‍👩‍👧‍👦', '프로젝트 29'),
                              ('🇰🇷 1️⃣ 작업 #42 ©️', '작업 #42'),
                              ('자료 2026-11-02 ✅', '자료 2026-11-02'),
                              ('보통 텍스트 A+B', '보통 텍스트 A+B')]:
            with self.subTest(raw=raw):
                self.assertEqual(features.clean_chat_title(raw), expected)
        event = self.event()
        original = copy.deepcopy(event)
        self.store.ingest(event)
        self.assertEqual(event, original)
        self.assertEqual(self.store.snapshot()['agents'][0]['title'], '실제 채팅 29')

    def test_plain_title_preserves_original_whitespace(self):
        for title in ('제목  제목  ', '첫 줄\n둘째 줄\t ', '  앞뒤 공백  '):
            with self.subTest(title=title):
                self.assertEqual(features.clean_chat_title(title), title)

    def test_only_actual_changed_fields_and_explicit_task_are_returned(self):
        self.assertEqual(features.changed_fields(self.event()), {'model'})
        self.assertEqual(features.changed_fields(self.event(before=None)), {'model', 'effort'})
        self.assertEqual(features.changed_fields(self.event(after={'model': 'sol', 'effort': 'medium'})), set())
        self.assertEqual(features.task_hint(self.event(task_summary='실제  문서\n검토')), '실제 문서 검토')
        self.assertNotIn('문서 검토', features.task_hint(self.event(reason='문서 검토를 추측하면 안 됩니다.')))
        self.assertNotIn('gAAAA', features.task_hint(self.event(task_summary='gAAAA' + 'A' * 180)))

    def test_selection_execution_and_explicit_status_are_separate(self):
        self.store.ingest(self.event())
        snap = self.store.snapshot()
        self.assertEqual(snap['selected']['agent'], {'model': 'astra', 'effort': 'medium'})
        self.assertEqual(snap['executed'], {})
        self.assertEqual(snap['agents'][0]['status'], 'unknown')
        self.store.ingest(self.event('e2', kind='observed', time='2026-11-02T00:01:00Z',
                                     after={'model': 'sol', 'effort': 'high'}))
        self.store.ingest(self.event('e3', kind='lifecycle', status='completed', time='2026-11-02T00:02:00Z'))
        snap = self.store.snapshot()
        self.assertEqual(snap['selected']['agent']['model'], 'astra')
        self.assertEqual(snap['executed']['agent']['model'], 'sol')
        self.assertEqual(snap['agents'][0]['status'], 'completed')

    def test_replay_uses_observed_time_without_changing_live_state(self):
        self.store.load_history([self.event(), self.event('e2', kind='lifecycle', status='waiting',
                                                        time='2026-11-02T00:02:00Z')])
        self.assertEqual(self.store.snapshot(at='2026-11-02T00:01:00Z')['agents'][0]['status'], 'unknown')
        self.assertEqual(self.store.snapshot()['agents'][0]['status'], 'waiting')
        self.assertEqual(len(self.store.snapshot()['events']), 2)

    def test_replay_boundary_uses_selected_record_despite_delivery_delay_or_equal_time(self):
        for second_source in ('2026-11-02T00:01:00Z', '2026-11-02T00:00:00Z'):
            with self.subTest(second_source=second_source):
                self.store.ingest(self.event('first', source_time='2026-11-02T00:00:00Z',
                                            time='2026-11-02T03:00:00Z', after={'model':'sol','effort':'medium'}))
                self.store.ingest(self.event('second', source_time=second_source,
                                            time='2026-11-02T03:01:00Z', after={'model':'sol','effort':'high'}))
                snapshot=self.store.snapshot(through='first')
                self.assertEqual([event['id'] for event in snapshot['events']],['first'])
                self.assertEqual(snapshot['selected']['agent']['effort'],'medium')
                self.assertEqual(self.store.snapshot()['selected']['agent']['effort'],'high')
        with self.assertRaises(ValueError):self.store.snapshot(through='missing')

    def test_repeated_enrichment_keeps_id_and_copies_input(self):
        event = self.event()
        self.store.load_history([event])
        event['chat_name'] = '🛰️ 보강된 제목'
        self.store.load_history([event])
        self.store.load_history([event])
        event['after']['model'] = '외부 변조'
        snapshot = self.store.snapshot()
        self.assertEqual(len(snapshot['events']), 1)
        self.assertEqual(snapshot['events'][0]['id'], 'e1')
        self.assertEqual(snapshot['agents'][0]['title'], '보강된 제목')
        self.assertEqual(snapshot['selected']['agent']['model'], 'astra')

    def test_pins_bookmarks_survive_restart_without_storing_event_body(self):
        self.store.ingest(self.event(reason='비공개 이유 원문', content='대화 본문 비밀'))
        self.store.set_pin('agent', True)
        self.store.set_bookmark('e1', True)
        restored = features.FeatureStore(self.root)
        self.assertIn('agent', restored.pins)
        self.assertIn('e1', restored.bookmarks)
        self.assertNotIn('대화 본문 비밀', ''.join(p.read_text(encoding='utf-8') for p in self.root.glob('*.json')))
        self.assertNotIn('비공개 이유 원문', ''.join(p.read_text(encoding='utf-8') for p in self.root.glob('*.json')))
        self.assertEqual(restored.snapshot()['events'], [])

    def test_away_summary_seen_marker_and_explicit_since(self):
        self.store.ingest(self.event())
        self.assertEqual(self.store.away_summary()['count'], 1)
        self.store.mark_seen()
        self.assertEqual(self.store.away_summary()['total'], 0)
        self.store.ingest(self.event('e2', kind='lifecycle', status='error', time='2026-11-02T00:02:00Z'))
        self.assertEqual(self.store.away_summary()['total'], 1)
        self.assertEqual(self.store.away_summary(since='2026-11-01T00:00:00Z')['total'], 2)

    def test_diagnostic_zip_contains_only_whitelisted_metrics(self):
        secret = '원문비밀 C:\\Users\\PRIVATE token=SECRET'
        self.store.ingest(self.event(chat_name=secret, reason=secret))
        target = self.root / '진단.zip'
        self.store.write_diagnostics(target, {'running': True, 'token': secret, 'path': secret, 'error': secret},
                                     {'render_count': 123, 'fps': 55.0, 'raw_event': secret, 'renderer': secret})
        with zipfile.ZipFile(target) as archive:
            self.assertEqual(archive.namelist(), ['diagnostics.json'])
            data = archive.read('diagnostics.json').decode('utf-8')
        self.assertNotIn(secret, data)
        self.assertNotIn('PRIVATE', data)
        self.assertEqual(json.loads(data)['render']['render_count'], 123)
        self.assertTrue(json.loads(data)['health']['running'])

    def test_failed_preference_write_keeps_previous_memory_and_disk(self):
        self.store.set_pin('old', True)
        before = {p.name: p.read_bytes() for p in self.root.glob('*.json')}
        with patch('orbit_features.os.replace', side_effect=OSError('제어된 저장 실패')):
            with self.assertRaises(OSError):
                self.store.set_pin('new', True)
        self.assertEqual(set(self.store.pins), {'old'})
        self.assertEqual({p.name: p.read_bytes() for p in self.root.glob('*.json')}, before)

    def test_lifecycle_restart_replay_merges_history_and_keeps_preferences(self):
        original = self.event('done', kind='lifecycle', status='completed',
                              time='2026-11-02T00:02:00Z', source_time='2026-11-02T00:02:00Z',
                              role='deep', parent='root', parent_id='parent-1',
                              task_summary='비공개 작업 내용', evidence='비공개 증거 내용',
                              content='비공개 대화 내용', reason='비공개 이유 내용')
        unchanged = copy.deepcopy(original)
        self.store.ingest(original)
        self.store.ingest(self.event('wait', kind='lifecycle', status='waiting',
                                     time='2026-11-02T00:03:00Z'))
        self.store.set_pin('agent', True)
        self.store.set_bookmark('done', True)
        self.store.mark_seen()
        restored = features.FeatureStore(self.root)
        self.assertEqual(original, unchanged)
        self.assertEqual(restored.snapshot()['agents'][0]['status'], 'waiting')
        self.assertEqual(restored.snapshot(at='2026-11-02T00:02:30Z')['agents'][0]['status'], 'completed')
        history = [self.event('selected'), self.event('executed', kind='observed',
                    time='2026-11-02T00:01:00Z', after={'model': 'sol', 'effort': 'high'})]
        restored.load_history(history)
        restored.load_history(history)
        snap = restored.snapshot()
        self.assertEqual(len(snap['events']), 4)
        self.assertEqual(snap['agents'][0]['status'], 'waiting')
        self.assertEqual(snap['agents'][0]['model'], 'sol')
        self.assertEqual(snap['selected']['agent']['model'], 'astra')
        self.assertEqual(snap['executed']['agent']['effort'], 'high')
        self.assertIn('agent', restored.pins)
        self.assertIn('done', restored.bookmarks)
        self.assertEqual(restored.away_summary()['count'], 2)
        restored.mark_seen()
        self.assertEqual(features.FeatureStore(self.root).away_summary()['count'], 0)
        data = json.loads((self.root / 'lifecycle-v1.json').read_text(encoding='utf-8'))
        allowed = {'id', 'target', 'status', 'time', 'source_time', 'role', 'parent', 'parent_id'}
        self.assertEqual(len(data['events']), 2)
        for row in data['events']:
            self.assertLessEqual(set(row), allowed)
        on_disk = ''.join(path.read_text(encoding='utf-8') for path in self.root.glob('*.json'))
        for secret in ('실제 채팅', '비공개 작업', '비공개 증거', '비공개 대화', '비공개 이유', 'astra'):
            self.assertNotIn(secret, on_disk)

    def test_invalid_lifecycle_state_preserves_original_file(self):
        valid = {'id': 'e1', 'target': 'agent', 'status': 'waiting', 'time': '2026-11-02T00:00:00Z'}
        invalid = [b'{broken', json.dumps({'schema_version': True, 'events': []}).encode(),
                   json.dumps({'schema_version': 1, 'events': [dict(valid, content='본문')]}).encode(),
                   json.dumps({'schema_version': 1, 'events': [dict(valid, id='x' * 129)]}).encode(),
                   json.dumps({'schema_version': 1, 'events': [dict(valid, status='guessed')]}).encode(),
                   json.dumps({'schema_version': 1, 'events': [dict(valid, time='2026-11-02T00:00:00')]}).encode(),
                   json.dumps({'schema_version': 1, 'events': [dict(valid, role='deep\n본문')]}).encode(),
                   json.dumps({'schema_version': 1, 'events': [valid, valid]}).encode(),
                   json.dumps({'schema_version': 1, 'events': [dict(valid, id=f'e{i}') for i in range(513)]}).encode(),
                   b' ' * (1048576 + 1)]
        path = self.root / 'lifecycle-v1.json'
        for raw in invalid:
            with self.subTest(size=len(raw), prefix=raw[:80]):
                path.write_bytes(raw)
                with self.assertRaises(ValueError):
                    features.FeatureStore(self.root)
                self.assertEqual(path.read_bytes(), raw)

    def test_failed_lifecycle_save_keeps_memory_and_previous_file(self):
        self.store.ingest(self.event('old', kind='lifecycle', status='running'))
        before_snapshot = self.store.snapshot()
        before_files = {p.name: p.read_bytes() for p in self.root.glob('*.json')}
        with patch('orbit_features.os.replace', side_effect=OSError('제어된 저장 실패')):
            with self.assertRaises(OSError):
                self.store.ingest(self.event('new', kind='lifecycle', status='completed'))
        self.assertEqual(self.store.snapshot(), before_snapshot)
        self.assertEqual({p.name: p.read_bytes() for p in self.root.glob('*.json')}, before_files)

    def test_bounded_lifecycle_file_keeps_status_with_full_model_history(self):
        rows = [{'id': f'{i:04d}' + 'i' * 124, 'target': 'a' * 128, 'status': 'waiting',
                 'time': '2026-11-02T00:02:00.000000+00:00',
                 'source_time': '2026-11-02T00:02:00.000000+00:00', 'role': '역' * 64,
                 'parent': 'p' * 128, 'parent_id': 'q' * 128} for i in range(512)]
        path = self.root / 'lifecycle-v1.json'
        path.write_text(json.dumps({'schema_version': 1, 'events': rows}, ensure_ascii=False, indent=2), encoding='utf-8')
        restored = features.FeatureStore(self.root)
        restored.ingest(self.event('new', target='a' * 128, kind='lifecycle', status='completed',
                                   time='2026-11-02T00:03:00Z'))
        restored.load_history([self.event(f'model-{i}', target='a' * 128, kind='observed',
                              time='2026-11-02T00:01:00Z') for i in range(512)])
        snap = restored.snapshot()
        self.assertEqual(snap['agents'][0]['status'], 'completed')
        self.assertEqual(snap['executed']['a' * 128]['model'], 'astra')
        self.assertEqual(len(snap['events']), 512)
        self.assertEqual(len(json.loads(path.read_text(encoding='utf-8'))['events']), 512)
        self.assertLessEqual(path.stat().st_size, 1048576)
        self.assertEqual(features.FeatureStore(self.root).snapshot()['agents'][0]['status'], 'completed')


if __name__ == '__main__':
    unittest.main()
