"""알림 표시 정책의 만료·저장 실패와 관측 상태를 최소 확인합니다."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import unittest
from types import SimpleNamespace
from operations37 import NotificationPolicy, health_snapshot


class PolicyTests(unittest.TestCase):
    def make(self):
        settings = SimpleNamespace(values={}, save=lambda: None)
        now = [1000]
        return settings, now, NotificationPolicy(settings, lambda: now[0])

    def test_focus_expires_without_replaying_or_mutating_event(self):
        settings, now, policy = self.make()
        event = {'target': 'chat', 'kind': 'settings', 'after': {'model': 'sol'}}
        policy.focus(15)
        self.assertFalse(policy.allows(event))
        now[0] += 901
        self.assertTrue(policy.allows(event))
        self.assertEqual(event['after'], {'model': 'sol'})
        self.assertEqual(policy.suppressed, 1)

    def test_mute_is_per_chat_and_activity_filter_keeps_model_notice(self):
        _, now, policy = self.make()
        policy.mute_target('a')
        self.assertFalse(policy.allows({'target': 'a'}))
        self.assertTrue(policy.allows({'target': 'b'}))
        policy.clear_mutes()
        policy.set_options(activity_popup=False)
        self.assertFalse(policy.allows({'target': 'a', 'kind': 'activity'}))
        self.assertTrue(policy.allows({'target': 'a', 'kind': 'settings'}))

    def test_save_failure_preserves_settings_and_options(self):
        settings, _, policy = self.make()
        settings.values['existing'] = 'keep'
        def fail():
            raise OSError('synthetic save failure')
        settings.save = fail
        with self.assertRaises(OSError):
            policy.set_options(visible_limit=3)
        self.assertEqual(settings.values, {'existing': 'keep'})
        self.assertEqual(policy.options['visible_limit'], 8)
        with self.assertRaises(ValueError):
            policy.set_options(visible_limit=9)

    def test_running_without_progress_is_not_reported_healthy(self):
        c = SimpleNamespace(last_monitor_status={'state': '감시 중', 'files': 3, 'chats': 2},
            monitor_enabled=True, monitor_restart_pending=False,
            monitor=SimpleNamespace(isRunning=lambda: True), last_monitor_progress=10, monitor_retries=1)
        self.assertEqual(health_snapshot(c, 15)['kind'], 'ok')
        self.assertEqual(health_snapshot(c, 40)['kind'], 'delayed')
        c.monitor = None
        self.assertEqual(health_snapshot(c, 40)['kind'], 'error')


if __name__ == '__main__':
    unittest.main()
