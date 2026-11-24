"""제품 설정과 분리한 색상 준비 모듈의 제어 검사입니다."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

_source = Path(__file__).resolve().parents[1] / 'src'
if _source.is_dir():
    sys.path.insert(0, str(_source))

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QColorDialog, QDialog

from appearance35 import (
    DEFAULTS, PRESETS, AppearanceDialog, contrast_ratio,
    normalize_config, palette_for,
)


class ConfigurationTests(unittest.TestCase):
    def test_defaults_and_results_do_not_share_mutable_values(self):
        expected = {'accent': '#73F936', 'dark_bg': '#0B0D0C',
                    'light_bg': '#F7F8F7', 'glow': 25}
        self.assertEqual(normalize_config(None), expected)
        first = normalize_config(None)
        first['accent'] = '#000000'
        self.assertEqual(normalize_config(None), expected)
        self.assertEqual(DEFAULTS, expected)

    def test_six_presets_are_complete_and_independent(self):
        self.assertIsInstance(PRESETS, tuple)
        self.assertEqual(len(PRESETS), 6)
        for row in PRESETS:
            self.assertTrue(row['name_ko'])
            self.assertTrue(row['name_en'])
            self.assertEqual(set(normalize_config(row['values'])), set(DEFAULTS))
        before = copy.deepcopy(PRESETS)
        normalize_config(PRESETS[0]['values'])['glow'] = 0
        self.assertEqual(PRESETS, before)

    def test_hex_normalization_and_invalid_colors(self):
        self.assertEqual(normalize_config({'accent': ' aAbBcC '})['accent'], '#AABBCC')
        for bad in ('#abc', '#12345678', 'red', 'transparent', '#GG0000', '', None, 123456):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                normalize_config({'accent': bad})

    def test_glow_boundaries_reject_bool_and_non_integer(self):
        self.assertEqual(normalize_config({'glow': 0})['glow'], 0)
        self.assertEqual(normalize_config({'glow': 100})['glow'], 100)
        for bad in (-1, 101, True, False, 25.0, '25', None):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                normalize_config({'glow': bad})

    def test_unknown_keys_and_non_objects_are_rejected(self):
        for bad in ({'sessions': '기존 설정'}, [], True, '설정'):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                normalize_config(bad)
        with self.assertRaises(ValueError):
            palette_for('system', None)


class PaletteTests(unittest.TestCase):
    def test_wcag_known_values(self):
        self.assertAlmostEqual(contrast_ratio('#000000', '#FFFFFF'), 21.0)
        self.assertAlmostEqual(contrast_ratio('#123456', '#123456'), 1.0)

    def test_arbitrary_backgrounds_keep_all_reading_roles_readable(self):
        for background in ('#000000', '#FFFFFF', '#777777', '#73F936',
                           '#FF00FF', '#0044FF', '#FFDD00', '#135527'):
            for mode in ('dark', 'light'):
                with self.subTest(background=background, mode=mode):
                    config = normalize_config({'dark_bg': background, 'light_bg': background})
                    colors = palette_for(mode, config)
                    for role in ('text', 'muted', 'disabled', 'accent', 'error', 'warning'):
                        for surface in ('bg', 'surface', 'raised', 'selected'):
                            self.assertGreaterEqual(contrast_ratio(colors[role], colors[surface]), 4.5)
                    self.assertGreaterEqual(contrast_ratio(colors['accent_text'], colors['accent']), 4.5)
                    self.assertEqual(colors['bg'], background)

    def test_original_accent_and_configuration_are_not_changed(self):
        original = normalize_config({'accent': '#73F936'})
        before = dict(original)
        colors = palette_for('light', original)
        self.assertEqual(original, before)
        self.assertEqual(colors['accent_raw'], '#73F936')
        self.assertNotEqual(colors['accent'], '#73F936')
        self.assertNotEqual(colors['error'], colors['accent'])

    def test_zero_glow_changes_no_color_or_geometry_setting(self):
        on = palette_for('dark', {'glow': 25})
        off = palette_for('dark', {'glow': 0})
        self.assertEqual({k: v for k, v in on.items() if k != 'glow'},
                         {k: v for k, v in off.items() if k != 'glow'})
        self.assertEqual(off['glow'], 0)


class DialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def tearDown(self):
        for widget in list(self.app.topLevelWidgets()):
            widget.close()
            widget.deleteLater()
        self.app.processEvents()

    def test_cancel_and_preview_never_apply_global_settings(self):
        calls = []
        style = self.app.styleSheet()
        palette = self.app.palette()
        dialog = AppearanceDialog(None, calls.append)
        dialog.show()
        dialog.fields['accent'].setText('#FFFFFF')
        dialog.glow_slider.setValue(80)
        QTest.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)
        self.assertEqual(calls, [])
        self.assertEqual(dialog.result(), QDialog.DialogCode.Rejected)
        self.assertEqual(self.app.styleSheet(), style)
        self.assertEqual(self.app.palette(), palette)

    def test_successful_apply_and_reopen_use_copied_normalized_config(self):
        saved = []
        dialog = AppearanceDialog(None, lambda value: saved.append(dict(value)), language='en')
        dialog.show()
        dialog.fields['accent'].setText('abcdef')
        QTest.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
        self.assertEqual(dialog.result(), QDialog.DialogCode.Accepted)
        self.assertEqual(saved[0]['accent'], '#ABCDEF')
        restored = AppearanceDialog(json.loads(json.dumps(saved[0])), lambda value: None)
        self.assertEqual(restored.candidate(), saved[0])

    def test_callback_failure_keeps_dialog_open_and_original_unchanged(self):
        original = normalize_config(None)
        def fail(value):
            raise OSError('합성 저장 실패')
        dialog = AppearanceDialog(original, fail)
        dialog.show()
        dialog.fields['accent'].setText('#ABCDEF')
        QTest.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
        self.assertTrue(dialog.isVisible())
        self.assertIn('합성 저장 실패', dialog.error_label.text())
        self.assertEqual(original, DEFAULTS)

    def test_invalid_field_is_identified_and_not_applied(self):
        calls = []
        dialog = AppearanceDialog(None, calls.append)
        dialog.show()
        dialog.fields['light_bg'].setText('#12')
        self.assertFalse(dialog.apply_button.isEnabled())
        self.assertTrue(dialog.field_errors['light_bg'].text())
        self.assertEqual(calls, [])

    def test_presets_and_reset_modify_only_draft_and_glow_zero_removes_effect(self):
        calls = []
        dialog = AppearanceDialog(None, calls.append)
        dialog.show()
        dialog.preset_combo.setCurrentIndex(2)
        self.assertEqual(dialog.candidate(), normalize_config(PRESETS[2]['values']))
        dialog.glow_slider.setValue(0)
        self.assertIsNone(dialog.preview_card.graphicsEffect())
        QTest.mouseClick(dialog.reset_button, Qt.MouseButton.LeftButton)
        self.assertEqual(dialog.candidate(), DEFAULTS)
        self.assertEqual(calls, [])

    def test_ambient_changes_pixels_without_effect_or_layout_change(self):
        dialog = AppearanceDialog(None, lambda value: None)
        dialog.show()
        self.app.processEvents()
        dialog.glow_slider.setValue(0)
        self.app.processEvents()
        geometry = dialog.preview_card.geometry()
        size = dialog.size()
        unlit = dialog.preview_card.grab().toImage()
        dialog.glow_slider.setValue(100)
        self.app.processEvents()
        lit = dialog.preview_card.grab().toImage()
        self.assertIsNone(dialog.preview_card.graphicsEffect())
        self.assertEqual(dialog.preview_card.geometry(), geometry)
        self.assertEqual(dialog.size(), size)
        self.assertEqual(unlit.size(), lit.size())
        self.assertNotEqual(unlit, lit, '조명 강도가 실제 카드 픽셀에 반영돼야 합니다.')
        center = unlit.rect().center()
        self.assertEqual(unlit.pixel(center), lit.pixel(center), '카드 안쪽 본문은 조명을 덧칠하지 않습니다.')
        dialog.glow_slider.setValue(0)
        self.app.processEvents()
        self.assertEqual(dialog.preview_card.grab().toImage(), unlit)

    def test_color_picker_uses_qt_dialog_and_rejects_cancel(self):
        dialog = AppearanceDialog(None, lambda value: None)
        before = dialog.fields['accent'].text()
        with patch('appearance35.QColorDialog.getColor', return_value=QColor()) as picker:
            dialog.choose_color('accent')
        self.assertEqual(dialog.fields['accent'].text(), before)
        self.assertTrue(picker.call_args.args[3] & QColorDialog.ColorDialogOption.DontUseNativeDialog)

    def test_small_window_both_languages_and_font_scales_keep_footer_accessible(self):
        previous = self.app.font()
        try:
            for language in ('ko', 'en'):
                for pixels in (13, 20):
                    with self.subTest(language=language, pixels=pixels):
                        font = QFont(previous)
                        font.setPixelSize(pixels)
                        self.app.setFont(font)
                        dialog = AppearanceDialog(None, lambda value: None, language=language)
                        dialog.resize(800, 600)
                        dialog.show()
                        self.app.processEvents()
                        self.assertEqual(dialog.font().pixelSize(), pixels)
                        self.assertEqual(dialog.font().weight(), QFont.Weight.Bold)
                        self.assertEqual(dialog.scroll.horizontalScrollBar().maximum(), 0)
                        self.assertGreaterEqual(dialog.footer.geometry().top(), 0)
                        self.assertLessEqual(dialog.footer.geometry().bottom(), dialog.height())
                        self.assertTrue(dialog.apply_button.isVisible())
                        dialog.close()
        finally:
            self.app.setFont(previous)


if __name__ == '__main__':
    unittest.main()
