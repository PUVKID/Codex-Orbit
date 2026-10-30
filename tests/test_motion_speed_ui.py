"""회전 속도 입력 경계와 실제 UI·저장·런타임 연결을 검사합니다."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from app import Controller, Settings
from i18n import set_language


class MotionSpeedSettingsTests(unittest.TestCase):
    def test_missing_and_invalid_speed_restore_default_without_losing_settings(self):
        for value in (None, False, True, 0, '', '1.5', [], {}, -.5, .24, 3.01,
                      float('nan'), float('inf'), -float('inf')):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'settings.json'
                path.write_text(json.dumps({'motion_speed': value, 'language': 'en',
                                            'sessions': 'preserved'}), encoding='utf-8')
                settings = Settings(folder)
                self.assertEqual(settings.values['motion_speed'], 1.0)
                self.assertIs(type(settings.values['motion_speed']), float)
                self.assertEqual(settings.values['language'], 'en')
                self.assertEqual(settings.values['sessions'], 'preserved')
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(Settings(folder).values.get('motion_speed'), 1.0)

    def test_valid_speed_round_trips(self):
        for value in (.25, .5, 1, 1.37, 1.5, 2, 3):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as folder:
                settings = Settings(folder)
                settings.values['motion_speed'] = value
                settings.save()
                self.assertEqual(Settings(folder).values['motion_speed'], value)


class MotionSpeedUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        from qt_test_support import cleanup_qt_widgets
        set_language('ko')
        self.addCleanup(set_language, 'ko')
        self.addCleanup(cleanup_qt_widgets, self)
        self.folder = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / 'work')
        self.addCleanup(self.folder.cleanup)
        self.c = Controller(Settings(self.folder.name), start_worker=False, start_usage=False)
        self.addCleanup(self.c.close)

    def assert_runtime_speed(self, value):
        from calendar_motion import calendar_motion_status
        self.assertEqual(calendar_motion_status()['motion_speed'], value)

    def speed_menu(self):
        menu = self.c.orbit.create_menu()
        return next(action.menu() for action in menu.actions()
                    if action.menu() and action.menu().objectName() == 'motionSpeedMenu')

    def test_slider_persists_updates_runtime_and_restores_on_restart(self):
        slider = self.c.window.motion_speed_slider
        self.assertEqual((slider.minimum(), slider.maximum(), slider.value()), (25, 300, 100))
        slider.setValue(137)
        self.assertEqual(self.c.window.motion_speed_value.text(), '1.37배')
        self.assertEqual(Settings(self.folder.name).values['motion_speed'], 1.37)
        self.assert_runtime_speed(1.37)
        self.c.close()
        self.c = Controller(Settings(self.folder.name), start_worker=False, start_usage=False)
        self.addCleanup(self.c.close)
        self.assertEqual(self.c.window.motion_speed_slider.value(), 137)
        self.assert_runtime_speed(1.37)
        self.c.window.motion_speed_reset.click()
        self.assertEqual(self.c.window.motion_speed_slider.value(), 100)
        self.assertEqual(Settings(self.folder.name).values['motion_speed'], 1.0)
        self.assert_runtime_speed(1.0)

    def test_presets_apply_real_values_and_language_switch_keeps_speed(self):
        for index, value in enumerate((.25, .5, 1, 1.5, 2, 3)):
            submenu = self.speed_menu()
            submenu.actions()[index].trigger()
            self.assertEqual(self.c.window.motion_speed_slider.value(), round(value * 100))
            self.assert_runtime_speed(value)
            self.assertEqual([a.data() for a in self.speed_menu().actions() if a.isChecked()], [value])
        self.c.set_language('en')
        self.assertEqual(self.c.window.motion_speed_label.text(), 'Rotation speed')
        self.assertEqual(self.c.window.motion_speed_value.text(), '3×')
        self.assertEqual(self.c.window.motion_speed_reset.text(), 'Reset to 1×')
        self.assertEqual(self.speed_menu().title(), 'Rotation speed')
        self.assertEqual(Settings(self.folder.name).values['motion_speed'], 3.0)
        self.assert_runtime_speed(3.0)
        self.c.window.resize(740, 540)
        self.c.window.show()
        self.qt.processEvents()
        controls = (self.c.window.motion_speed_label, self.c.window.motion_speed_slider,
                    self.c.window.motion_speed_value, self.c.window.motion_speed_reset)
        self.assertGreaterEqual(self.c.window.motion_speed_slider.width(), 100)
        for control in controls:
            self.assertTrue(self.c.window.rect().contains(control.geometry()))
        for left, right in zip(controls, controls[1:]):
            self.assertFalse(left.geometry().intersects(right.geometry()))
        self.c.set_language('ko')
        self.assertEqual(self.c.window.motion_speed_value.text(), '3배')

    def test_invalid_runtime_selection_is_rejected_without_changing_saved_speed(self):
        self.c.set_motion_speed(1.5)
        for value in (None, False, True, '', '2', 0, .24, 3.01, float('nan'), float('inf')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.c.set_motion_speed(value)
        self.assertEqual(Settings(self.folder.name).values['motion_speed'], 1.5)
        self.assertEqual(self.c.window.motion_speed_slider.value(), 150)
        self.assert_runtime_speed(1.5)

    def test_save_failure_is_visible_and_preserves_previous_runtime(self):
        from unittest.mock import patch
        self.c.set_motion_speed(1.5)
        with patch.object(self.c.settings, 'save', side_effect=OSError('속도 저장 실패')):
            with self.assertRaisesRegex(OSError, '속도 저장 실패'):
                self.c.set_motion_speed(2.0)
        self.assertEqual(self.c.settings.values['motion_speed'], 1.5)
        self.assertEqual(self.c.window.motion_speed_slider.value(), 150)
        self.assert_runtime_speed(1.5)

    def assert_user_save_failure_is_reported(self, operation):
        from unittest.mock import patch
        self.c.set_motion_speed(1.5)
        escaped = []
        with patch.object(self.c.settings, 'save', side_effect=OSError('속도 저장 실패')), \
                patch.object(sys, 'excepthook', lambda *args: escaped.append(args)):
            operation()
        self.assertFalse(escaped, '사용자 조작 실패가 Qt 예외 출력으로만 사라지면 안 됩니다.')
        self.assertEqual(Settings(self.folder.name).values['motion_speed'], 1.5)
        self.assertEqual(self.c.window.motion_speed_slider.value(), 150)
        self.assert_runtime_speed(1.5)
        self.assertTrue(self.c.window.isVisible())
        self.assertTrue(self.c.window.motion_speed_error.isVisible())
        self.assertIn('회전 속도 변경 실패:', self.c.window.motion_speed_error.text())
        self.assertIn('속도 저장 실패', self.c.window.motion_speed_error.text())
        self.c.set_language('en')
        self.assertIn('Unable to change rotation speed:', self.c.window.motion_speed_error.text())
        self.assertIn('속도 저장 실패', self.c.window.motion_speed_error.text())
        self.c.window.motion_speed_slider.setValue(175)
        self.assertEqual(Settings(self.folder.name).values['motion_speed'], 1.75)
        self.assert_runtime_speed(1.75)
        self.assertTrue(self.c.window.motion_speed_error.isHidden())

    def test_slider_save_failure_is_reported_to_user_and_success_clears_error(self):
        self.assert_user_save_failure_is_reported(lambda: self.c.window.motion_speed_slider.setValue(200))

    def test_reset_save_failure_is_reported_to_user_and_success_clears_error(self):
        self.assert_user_save_failure_is_reported(self.c.window.motion_speed_reset.click)

    def test_menu_save_failure_is_reported_to_user_and_success_clears_error(self):
        self.assert_user_save_failure_is_reported(lambda: self.speed_menu().actions()[4].trigger())


if __name__ == '__main__':
    unittest.main()
