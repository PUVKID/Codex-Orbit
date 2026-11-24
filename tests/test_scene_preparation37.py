"""느린 장면 준비가 회전 프레임 기한과 섞이지 않는지 확인합니다."""
from datetime import date
from pathlib import Path
import sys, unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from calendar_gpu_process import ProcessCalendarRenderer
from observatory_scene import normalize_scene


class ScenePreparationTests(unittest.TestCase):
    def renderer(self):
        r = ProcessCalendarRenderer(64)
        r._start = lambda: None
        r._catalog = lambda: {'data_dir': None, 'revision': 'a' * 64}
        r.calls = []
        def exchange(payload):
            r.calls.append(payload['kind'])
            if payload['kind'].startswith('prepare_'):
                self.assertTrue(r.initializing)
                return {'status': 'prepared'}, b'', 0, 0
            side=r.output_size
            return {'status': 'frame', 'catalog_revision': 'a' * 64}, bytes([25, 50, 75, 255]) * side * side, side, side
        r._exchange = exchange
        return r

    def test_rotation_reuses_prepared_scene(self):
        r = self.renderer()
        for t in (0, .65):
            self.assertFalse(r.render(date(2026, 11, 25), t).isNull())
        self.assertEqual(r.calls, ['prepare_calendar', 'calendar', 'calendar'])

    def test_date_region_and_catalog_each_prepare_again(self):
        r = self.renderer()
        r.render(date(2026, 11, 25))
        r.render(date(2026, 11, 26))
        r.render(date(2026, 11, 26), country='US')
        r._catalog = lambda: {'data_dir': None, 'revision': 'b' * 64}
        r.render(date(2026, 11, 26), country='US')
        self.assertEqual(r.calls.count('prepare_calendar'), 4)

    def test_observatory_pointer_does_not_rebuild_but_geometry_does(self):
        r = self.renderer()
        scene = normalize_scene({'model': 'gpt-6.1-sol', 'effort': 'medium'})
        r.render_observatory(scene)
        scene['pointer'] = [.2, .3]
        r.render_observatory(scene, .65)
        scene['model'] = 'gpt-6-astra'
        r.render_observatory(scene, 1)
        self.assertEqual(r.calls, ['prepare_observatory', 'observatory', 'observatory', 'prepare_observatory', 'observatory'])

    def test_failed_preparation_is_not_cached_or_reported_as_a_frame(self):
        r = self.renderer()
        exchange = r._exchange
        with patch.object(r, '_exchange', side_effect=RuntimeError('제어 장면 준비 실패')):
            with self.assertRaisesRegex(RuntimeError, '준비 실패'):
                r.render(date(2026, 11, 25))
        self.assertFalse(r.initializing)
        self.assertIsNone(r.first_frame_at)
        r._exchange = exchange
        r.render(date(2026, 11, 25))
        self.assertEqual(r.calls, ['prepare_calendar', 'calendar'])

    def test_output_resize_prepares_once_and_preserves_requested_size(self):
        r=self.renderer()
        r.render(date(2026,11,25))
        r.set_output_size(96)
        self.assertEqual(r.render(date(2026,11,25)).width(),96)
        self.assertEqual(r.render(date(2026,11,25),.65).width(),96)
        self.assertEqual(r.calls,['prepare_calendar','calendar','prepare_calendar','calendar','calendar'])


if __name__ == '__main__':
    unittest.main()
