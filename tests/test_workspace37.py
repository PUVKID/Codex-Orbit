"""개인 기록을 읽지 않는 37차 알림센터 핵심 검사입니다."""
import csv
from datetime import datetime, timezone
import io
import unittest

from workspace37 import csv_text, export_rows, filter_events, group_events, summary_text


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 20, 12, tzinfo=timezone.utc)
        self.events = [
            {'id': 'a', 'target': 'chat-a', 'title': 'Alpha', 'time': '2026-11-20T10:00:00Z',
             'before': {'model': 'old', 'effort': 'low'}, 'after': {'model': 'new', 'effort': 'low'},
             'reason': 'clear reason', 'task_summary': 'synthetic work', 'messages': 'NEVER_EXPORT', 'location': 'NEVER_EXPORT'},
            {'id': 'b', 'target': 'chat-a', 'title': 'Alpha', 'time': '2026-11-18T10:00:00Z',
             'before': {'model': 'new', 'effort': 'low'}, 'after': {'model': 'new', 'effort': 'high'}},
            {'id': 'c', 'target': 'chat-b', 'title': 'Beta', 'time': '2026-11-01T10:00:00Z',
             'kind': 'activity', 'activity_type': 'resumed'},
            {'id': 'd', 'target': 'chat-b', 'title': 'Unknown date'}]

    def test_search_across_title_model_reason_task(self):
        for term in ('ALPHA', 'old', 'clear reason', 'synthetic work'):
            self.assertIn('a', [row['id'] for row in filter_events(self.events, query=term)])
        self.assertEqual(filter_events(self.events, query='missing'), [])

    def test_changed_fields_and_resume_are_independent(self):
        for kind, identity in (('model', 'a'), ('effort', 'b'), ('resumed', 'c')):
            self.assertEqual([row['id'] for row in filter_events(self.events, kind=kind)], [identity])

    def test_period_and_preference_filters(self):
        self.assertEqual([row['id'] for row in filter_events(self.events, period='today', now=self.now)], ['a'])
        self.assertEqual([row['id'] for row in filter_events(self.events, period='week', now=self.now)], ['a', 'b'])
        self.assertEqual([row['id'] for row in filter_events(self.events, bookmarked=True, bookmarks={'b'})], ['b'])
        self.assertEqual([row['id'] for row in filter_events(self.events, pinned=True, pins={'chat-a'})], ['a', 'b'])

    def test_order_and_group_preserve_original_states(self):
        rows = filter_events(self.events[:3], oldest=True)
        self.assertEqual([row['id'] for row in rows], ['c', 'b', 'a'])
        grouped = group_events(rows)
        self.assertEqual([row['id'] for row in grouped['chat-a']], ['b', 'a'])
        grouped['chat-a'][0]['after']['effort'] = 'changed copy'
        self.assertEqual(self.events[1]['after']['effort'], 'high')

    def test_export_whitelist_and_private_summary(self):
        regular = str(export_rows(self.events))
        self.assertNotIn('NEVER_EXPORT', regular)
        self.assertNotIn('chat-a', regular)
        private = str(export_rows(self.events, private=True)) + summary_text(self.events[0], private=True)
        for secret in ('Alpha', 'clear reason', 'synthetic work', 'NEVER_EXPORT'):
            self.assertNotIn(secret, private)
        self.assertIn('old', private)

    def test_csv_blocks_formula_prefixes_and_remains_parseable(self):
        for value in ('=1+1', '+1', '-1', '@SUM(1)', '\tvalue', '\rvalue', '\nvalue', '  =1'):
            event = {'title': value, 'reason': '한글, "줄"\n둘'}
            row = next(csv.DictReader(io.StringIO(csv_text([event]), newline='')))
            self.assertEqual(row['title'], "'" + value)
            self.assertEqual(row['reason'], event['reason'])

    def test_privacy_csv_masks_without_mutating_source(self):
        private = csv_text(self.events, True)
        self.assertNotIn('Alpha', private)
        self.assertNotIn('clear reason', private)
        self.assertEqual(self.events[0]['title'], 'Alpha')


if __name__ == '__main__':
    unittest.main()
