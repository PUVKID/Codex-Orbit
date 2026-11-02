"""명시 생명주기만 별도 채널에 전달하고 기존 모델 알림 수를 보존합니다."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from notifier import NativeToast, Watcher

TARGET = '11111111-1111-4111-8111-111111111111'
OTHER = '22222222-2222-4222-8222-222222222222'


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.sessions = self.root / 'sessions'
        self.sessions.mkdir()
        self.sent = []
        self.watcher = Watcher(self.sessions, self.root / 'work', self.sent.append)
        self.assertTrue(callable(getattr(self.watcher, 'drain_lifecycle', None)), '별도 생명주기 채널이 아직 없습니다.')
        self.write({'type': 'session_meta', 'payload': {'id': TARGET}})
        self.watcher.poll()

    def write(self, *records):
        with (self.sessions / ('rollout-' + TARGET + '.jsonl')).open('ab') as handle:
            for record in records:
                handle.write((json.dumps(record, ensure_ascii=False) + '\n').encode('utf-8'))

    def record(self, kind, **extra):
        return {'type': 'event_msg', 'timestamp': '2026-11-02T00:00:00Z',
                'payload': {'type': kind, 'turn_id': 'own-turn', **extra}}

    def test_started_completed_are_side_channel_only_and_drain_is_consuming(self):
        self.write(self.record('task_started'), self.record('task_complete', last_agent_message='저장 금지 본문'))
        self.watcher.poll()
        events = self.watcher.drain_lifecycle()
        self.assertEqual([event['status'] for event in events], ['running', 'completed'])
        self.assertTrue(all(event['target'] == TARGET for event in events))
        self.assertEqual(self.sent, [])
        self.assertEqual(self.watcher.drain_lifecycle(), [])
        self.watcher.poll()
        self.assertEqual(self.watcher.drain_lifecycle(), [])
        self.assertNotIn('저장 금지 본문', json.dumps(self.watcher.state, ensure_ascii=False))

    def test_baseline_does_not_flood_and_foreign_owner_is_ignored(self):
        self.write(self.record('task_started', thread_id=OTHER), self.record('task_complete', thread_id=OTHER))
        self.watcher.poll()
        self.assertEqual(self.watcher.drain_lifecycle(), [])
        baseline_sessions = self.root / 'baseline'
        baseline_sessions.mkdir()
        (baseline_sessions / (TARGET + '.jsonl')).write_text('\n'.join(json.dumps(value) for value in (
            {'type': 'session_meta', 'payload': {'id': TARGET}}, self.record('task_started'),
            self.record('task_complete'))) + '\n', encoding='utf-8')
        fresh = Watcher(baseline_sessions, self.root / 'fresh', self.sent.append)
        fresh.poll()
        self.assertEqual(fresh.drain_lifecycle(), [])

    def test_wait_abort_error_are_explicit_and_raw_arguments_are_not_kept(self):
        self.write(self.record('turn_aborted'), self.record('error', message='원문비밀'),
                   {'type': 'response_item', 'timestamp': '2026-11-02T00:00:01Z', 'payload': {
                       'type': 'function_call', 'name': 'request_user_input', 'call_id': 'ask1',
                       'arguments': '{"question":"원문비밀"}'}})
        self.watcher.poll()
        events = self.watcher.drain_lifecycle()
        self.assertEqual([event['status'] for event in events], ['aborted', 'error', 'waiting'])
        self.assertNotIn('원문비밀', json.dumps(events, ensure_ascii=False))
        self.assertNotIn('원문비밀', json.dumps(self.watcher.state, ensure_ascii=False))
        self.assertEqual(self.sent, [])

    def test_model_observation_keeps_original_sender_semantics(self):
        self.write(self.record('task_started'), {'type': 'turn_context', 'timestamp': '2026-11-02T00:00:01Z',
                   'payload': {'turn_id': 'own-turn', 'model': 'gpt-6.1-sol', 'effort': 'high'}})
        self.watcher.poll()
        self.assertEqual(len(self.sent), 1)
        self.assertEqual(self.sent[0]['kind'], 'observed')
        self.assertEqual(self.sent[0]['after']['model'], 'gpt-6.1-sol')
        self.assertEqual([event['status'] for event in self.watcher.drain_lifecycle()], ['running'])

    def test_native_toast_cleans_display_title_without_mutating_original(self):
        event = {'id': 'e1', 'chat_name': '🔄 원래 제목 👨‍👩‍👧‍👦', 'target': TARGET,
                 'before': None, 'after': {'model': 'gpt-6.1-sol', 'effort': 'high'}, 'reason': '공개 이유'}
        with patch('notifier.powershell', return_value=None):
            NativeToast(self.root)(event)
        texts = [node.text for node in ET.parse(self.root / 'toast.xml').iter('text')]
        self.assertEqual(texts[0], '원래 제목')
        self.assertEqual(event['chat_name'], '🔄 원래 제목 👨‍👩‍👧‍👦')


if __name__ == '__main__':
    unittest.main()
