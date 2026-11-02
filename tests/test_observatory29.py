"""관측소의 실제 메시·공유 작업자·정적 모드와 클릭 투영을 검사합니다."""
import copy
import importlib.util
import math
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))


class ObservatoryAvailabilityTests(unittest.TestCase):
    def test_scene_module_exists(self):
        self.assertIsNotNone(importlib.util.find_spec('observatory_scene'))


if importlib.util.find_spec('observatory_scene'):
    import observatory_scene as scene_api
    import calendar_motion as motion
    from calendar_renderer import CalendarRenderer, build_observatory_geometry
    from PySide6.QtWidgets import QApplication
    from test_calendar_motion import FakeRenderer, Owner
    from qt_test_support import wait_qt

    class ObservatorySceneTests(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.qt = QApplication.instance() or QApplication([])

        def tearDown(self):
            motion.close_calendar_motion()

        def scene(self, **extra):
            return {'model': 'gpt-6.1-sol', 'effort': 'medium',
                    'agents': [{'target': 'synthetic-worker', 'status': 'running', 'pinned': True}],
                    'usage_fraction': .375, 'quality': 'balanced', **extra}

        def test_snapshot_is_copied_and_invalid_inputs_are_rejected(self):
            raw = self.scene(); original = copy.deepcopy(raw)
            value = scene_api.normalize_scene(raw)
            raw['agents'][0]['status'] = 'error'
            self.assertEqual(value['agents'][0]['status'], 'running')
            self.assertEqual(original['usage_fraction'], value['usage_fraction'])
            for extra in ({'usage_fraction': False}, {'usage_fraction': math.nan}, {'usage_fraction': 1.1},
                          {'quality': 'unlimited'}, {'pointer': [math.inf, 0]}, {'transition': -1},
                          {'agents': [{'target': 'same'}, {'target': 'same'}]},
                          {'agents': [{'target': str(i)} for i in range(25)]}):
                with self.subTest(extra=extra), self.assertRaises((TypeError, ValueError)):
                    scene_api.normalize_scene(self.scene(**extra))

        def test_unknown_model_and_missing_usage_are_not_sol_or_zero(self):
            value = scene_api.normalize_scene({'model': None, 'usage_fraction': None})
            self.assertEqual(scene_api.model_family(value['model']), 'unknown')
            self.assertIsNone(value['usage_fraction'])
            empty = build_observatory_geometry(scene_api.normalize_scene(self.scene(usage_fraction=0)))
            unknown = build_observatory_geometry(scene_api.normalize_scene(self.scene(usage_fraction=None)))
            self.assertNotEqual([p[4] for p in empty], [p[4] for p in unknown])

        def test_distinct_model_meshes_and_effort_density(self):
            signatures = []
            for name in ('sol', 'astra', 'terra', 'luna'):
                parts = build_observatory_geometry(scene_api.normalize_scene(self.scene(model='gpt-6.1-' + name)))
                core = [p for p in parts if p[4] == 'core']
                self.assertTrue(core)
                signatures.append(tuple((len(p[0][0]), len(p[0][1])) for p in core))
                self.assertEqual(sum(p[4] == 'ring' for p in parts), 3)
                for (vertices, indices), *_ in parts:
                    self.assertTrue(len(indices) and len(indices) % 3 == 0)
                    self.assertTrue((indices < len(vertices)).all())
            self.assertEqual(len(set(signatures)), 4)
            counts = [scene_api.particle_count(name) for name in ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'ultra')]
            self.assertEqual(counts[0], 0)
            self.assertTrue(all(a < b for a, b in zip(counts, counts[1:])))

        def test_positions_use_shared_world_projection_and_keep_target(self):
            scene = scene_api.normalize_scene(self.scene(pointer=[.6, -.3], press=.5))
            positions = scene_api.observatory_positions(scene, .75)
            self.assertEqual(positions[0]['target'], 'synthetic-worker')
            self.assertTrue(0 <= positions[0]['x'] <= 1 and 0 <= positions[0]['y'] <= 1)
            point = scene_api.agent_world_positions(scene, .75)[0]
            x, y, depth = scene_api.project_point(scene_api.transform_point(scene, point['position']))
            self.assertAlmostEqual(positions[0]['x'], x)
            self.assertAlmostEqual(positions[0]['y'], y)
            self.assertAlmostEqual(positions[0]['depth'], depth)

        def test_satellite_orbits_keep_the_usage_vessel_uncovered(self):
            scene = self.scene(agents=[{'target': str(i), 'status': 'running'} for i in range(24)])
            for elapsed in (0, .5, 2, 7, 14):
                for agent in scene_api.agent_world_positions(scene, elapsed):
                    x, y, _ = agent['position']
                    if abs(x) <= 16:
                        self.assertGreaterEqual(y, -22)

        def test_quality_budgets_and_reduced_motion_are_bounded(self):
            self.assertEqual([scene_api.scene_fps(self.scene(quality=q)) for q in ('eco', 'balanced', 'high')], [20, 30, 60])
            scene = self.scene(reduced_motion=True)
            self.assertEqual(scene_api.observatory_positions(scene, 0), scene_api.observatory_positions(scene, 100))

        def test_global_calendar_options_pause_date_refresh_and_restore_legacy(self):
            from datetime import date
            with patch('calendar_renderer.CalendarRenderer', FakeRenderer):
                motion.set_calendar_motion_options(paused=True, quality='eco')
                owner = Owner(); motion.set_calendar_motion_visible(owner, True)
                for _ in range(100):
                    wait_qt(10)
                    if motion.calendar_motion_status().get('render_count', 0): break
                first = motion.calendar_motion_status()
                self.assertEqual(first['target_fps'], 20)
                self.assertEqual(first['mode'], 'calendar')
                wait_qt(80)
                self.assertEqual(first['render_count'], motion.calendar_motion_status()['render_count'])
                motion.get_calendar_frame(0, date(2027, 1, 1))
                for _ in range(100):
                    wait_qt(10)
                    if motion.calendar_motion_status()['render_count'] > first['render_count']: break
                second = motion.calendar_motion_status()
                self.assertEqual(second['date'], '2027-01-01')
                self.assertEqual(second['render_count'], first['render_count'] + 1)
                wait_qt(80)
                self.assertEqual(second['render_count'], motion.calendar_motion_status()['render_count'])
                motion.set_calendar_motion_options(reduced_motion=True, quality='high')
                for _ in range(100):
                    wait_qt(10)
                    if motion.calendar_motion_status()['render_count'] > second['render_count']: break
                static = motion.calendar_motion_status()
                self.assertEqual(static['scene_elapsed'], 0)
                wait_qt(80)
                self.assertEqual(static['render_count'], motion.calendar_motion_status()['render_count'])
                motion.set_calendar_motion_options(None)
                self.assertEqual(motion.calendar_motion_status()['target_fps'], 240)

        def test_paused_worker_renders_once_per_data_change_and_none_restores_calendar(self):
            class SceneRenderer(FakeRenderer):
                def render_observatory(self, scene, elapsed):
                    from datetime import date
                    return self.render(date(2026, 11, 2), elapsed)
            with patch('calendar_renderer.CalendarRenderer', SceneRenderer):
                motion.set_calendar_observatory_scene(self.scene(paused=True))
                owner = Owner(); motion.set_calendar_motion_visible(owner, True)
                for _ in range(100):
                    wait_qt(10)
                    if motion.calendar_motion_status().get('render_count', 0): break
                first = motion.calendar_motion_status()
                self.assertEqual(first['mode'], 'observatory')
                self.assertEqual(first['target_fps'], 30)
                wait_qt(80)
                self.assertEqual(first['render_count'], motion.calendar_motion_status()['render_count'])
                motion.set_calendar_observatory_scene(self.scene(paused=True, usage_fraction=.5))
                for _ in range(100):
                    wait_qt(10)
                    if motion.calendar_motion_status()['render_count'] > first['render_count']: break
                second = motion.calendar_motion_status()
                self.assertEqual(second['render_count'], first['render_count'] + 1)
                wait_qt(80)
                self.assertEqual(second['render_count'], motion.calendar_motion_status()['render_count'])
                motion.set_calendar_observatory_scene(None)
                self.assertEqual(motion.calendar_motion_status()['target_fps'], 240)
                self.assertEqual(motion.calendar_motion_status()['mode'], 'calendar')

        def test_actual_gpu_models_are_distinct_transparent_and_four_k_source_is_kept(self):
            renderer = CalendarRenderer((3840, 2160))
            try:
                renderer.set_output_size(160)
                images = []
                for name in ('sol', 'astra', 'terra', 'luna'):
                    image = renderer.render_observatory(self.scene(model='gpt-6.1-' + name), .25)
                    self.assertEqual(image.size().toTuple(), (160, 160))
                    self.assertEqual(image.pixelColor(0, 0).alpha(), 0)
                    self.assertGreater(sum(image.pixelColor(x, y).alpha() > 0 for x in range(0, 160, 8) for y in range(0, 160, 8)), 15)
                    images.append(bytes(image.constBits()))
                self.assertEqual(len(set(images)), 4)
                self.assertEqual(renderer.dimensions, (3840, 2160))
            finally:
                renderer.close()
