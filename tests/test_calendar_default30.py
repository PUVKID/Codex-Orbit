"""설정이 없는 경우에도 기존 날짜별 조형이 모델 이벤트와 무관하게 유지되는지 확인합니다."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtWidgets import QApplication
from app import Controller, Settings
from calendar_art import current_date, design_for_date
from qt_test_support import cleanup_qt_widgets

APP = QApplication.instance() or QApplication([])


class CalendarDefault30Tests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.addCleanup(cleanup_qt_widgets, self)
        scene_patch = patch('calendar_motion.set_calendar_observatory_scene')
        self.scene = scene_patch.start()
        self.addCleanup(scene_patch.stop)

    def controller(self, settings=None):
        controller = Controller(settings or Settings(self.folder.name), start_worker=False, start_usage=False)
        self.addCleanup(controller.close)
        return controller

    def event(self):
        return {'id': 'calendar-default-demo', 'target': 'synthetic-chat', 'chat_name': '합성 모델 변경',
                'before': {'model': 'gpt-6.1-sol', 'effort': 'medium'},
                'after': {'model': 'gpt-6-astra', 'effort': 'high'}, 'reason': '합성 회귀 검사입니다.'}

    def test_new_settings_without_scene_mode_use_calendar(self):
        controller = self.controller()
        self.assertNotIn('scene_mode', controller.settings.values)
        self.assertEqual(controller.orbit29.view.currentData(), 'calendar')
        self.scene.assert_called_with(None)

    def test_existing_settings_without_scene_mode_keep_calendar_and_other_values(self):
        settings = Settings(self.folder.name)
        settings.values['motion_speed'] = .5
        settings.save()
        controller = self.controller(Settings(self.folder.name))
        self.assertNotIn('scene_mode', controller.settings.values)
        self.assertEqual(controller.settings.values['motion_speed'], .5)
        self.assertEqual(controller.orbit29.view.currentData(), 'calendar')
        self.scene.assert_called_with(None)

    def test_model_event_keeps_original_date_title_and_design(self):
        controller = self.controller()
        expected = design_for_date(current_date())
        with patch('app.draw_desktop_orbit') as draw:
            controller.orbit.grab()
            before = draw.call_args.args[4]
            controller.receive(self.event())
            controller.orbit.grab()
            after = draw.call_args.args[4]
        self.assertEqual(before, expected)
        self.assertEqual(after, expected)
        self.assertEqual(after.title, expected.title)
        self.scene.assert_called_with(None)
        self.assertTrue(controller.notice.isVisible())

    def test_explicit_observatory_choice_still_uses_model_scene(self):
        settings = Settings(self.folder.name)
        settings.values['scene_mode'] = 'observatory'
        settings.save()
        controller = self.controller(Settings(self.folder.name))
        self.assertEqual(controller.orbit29.view.currentData(), 'observatory')
        controller.receive(self.event())
        self.assertEqual(self.scene.call_args.args[0]['model'], 'gpt-6-astra')
        with patch('app.draw_desktop_orbit') as draw:
            controller.orbit.grab()
        self.assertEqual(draw.call_args.args[4].title, 'Astra')
