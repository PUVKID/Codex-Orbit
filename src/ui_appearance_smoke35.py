"""격리된 합성 화면 검사에서만 실제 색상 조절창을 조작합니다."""
from copy import deepcopy
import json


def check_appearance(controller, directory, number):
    from unittest.mock import patch
    from PySide6.QtCore import QTimer, Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    from appearance35 import AppearanceDialog, normalize_config, PRESETS
    from theme import configure_appearance, colors

    c = controller
    QTest.qWait(30)
    original_values = deepcopy(c.settings.values)
    original_config = normalize_config(original_values.get('appearance35'))
    saved = c.settings.path.read_bytes()
    button = c.orbit29.appearance_button
    assert button.isVisible() and button.isEnabled()
    center = c.window.mapFromGlobal(button.mapToGlobal(button.rect().center()))
    assert c.window.rect().contains(center), '색상 조절 버튼이 창 밖에 있습니다.'
    scale = c.settings.values.get('text_scale', 100)
    opened = []
    failures = []

    def inspect_opened():
        dialog = QApplication.activeModalWidget()
        try:
            assert isinstance(dialog, AppearanceDialog), '색상 조절창이 열리지 않았습니다.'
            dialog.resize(min(760, dialog.width()), min(580, dialog.height()))
            QTest.qWait(20)
            assert all(field.font().pixelSize() == round(13 * scale / 100) for field in dialog.fields.values())
            assert dialog.rect().contains(dialog.footer.geometry())
            assert dialog.scroll.horizontalScrollBar().maximum() == 0
            assert dialog.grab().save(str(directory / f'{number}-appearance.png'))
            dialog.fields['accent'].setText('#XYZ')
            assert not dialog.apply_button.isEnabled()
            assert dialog.field_errors['accent'].text()
            assert c.settings.path.read_bytes() == saved
            opened.append(True)
        except Exception as error:
            failures.append(error)
        finally:
            if isinstance(dialog, AppearanceDialog):
                QTest.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)

    QTimer.singleShot(0, inspect_opened)
    QTest.mouseClick(button, Qt.MouseButton.LeftButton)
    if failures:
        raise failures[0]
    assert opened == [True]
    assert c.settings.values == original_values and c.settings.path.read_bytes() == saved

    dialog = AppearanceDialog(original_config, c.orbit29.apply_appearance, c.window,
                              language=c.settings.values.get('language', 'ko'))
    c.orbit29.apply_text_size()
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
    QTest.qWait(20)
    before_palette = dict(colors())
    index = (number + 1) % len(PRESETS)
    dialog.preset_combo.setFocus()
    QTest.keyClick(dialog.preset_combo, Qt.Key.Key_Home)
    for _ in range(index):
        QTest.keyClick(dialog.preset_combo, Qt.Key.Key_Down)
    assert dialog.candidate() == normalize_config(PRESETS[index]['values'])
    QTest.mouseMove(dialog.fields['accent'], dialog.fields['accent'].rect().center())
    dialog.fields['accent'].setFocus()
    QTest.keyClick(dialog.fields['accent'], Qt.Key.Key_End)
    assert dialog.fields['accent'].hasFocus()
    dialog.preview_mode.setCurrentIndex(1)
    dialog.glow_slider.setValue(0)
    assert dialog.preview_card.graphicsEffect() is None
    chosen = dialog.candidate()
    assert dict(colors()) == before_palette and c.settings.path.read_bytes() == saved
    with patch.object(c.settings, 'save', side_effect=OSError('합성 저장 실패')):
        QTest.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
    assert dialog.isVisible() and dialog.error_label.text()
    assert c.settings.values == original_values and c.settings.path.read_bytes() == saved
    assert dict(colors()) == before_palette
    QTest.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)
    dialog.deleteLater()

    c.orbit29.apply_appearance(chosen)
    assert json.loads(c.settings.path.read_text(encoding='utf-8'))['appearance35'] == chosen
    reloaded = type(c.settings)(c.settings.directory)
    assert normalize_config(reloaded.values['appearance35']) == chosen
    assert colors()['glow'] == 0
    assert {key: value for key, value in c.settings.values.items() if key != 'appearance35'} == {
        key: value for key, value in original_values.items() if key != 'appearance35'}
    c.orbit.grab()
    changed_key = c.orbit._desktop_overlay_cache.key
    c.settings.values.clear()
    c.settings.values.update(deepcopy(original_values))
    c.settings.save()
    configure_appearance(original_config)
    c.orbit29.apply_text_size()
    c.orbit.grab()
    assert c.orbit._desktop_overlay_cache.key != changed_key, '색상 변경 뒤 정보창 캐시가 갱신되지 않았습니다.'
    assert c.settings.values == original_values
    return {'opened_by_button': True, 'scale': scale, 'cancel_unchanged': True,
            'hex_validation': True, 'preset_selection': True, 'preview_isolated': True,
            'apply_reload': True, 'save_failure_restored': True, 'glow_zero': True,
            'hover_focus_keyboard': True, 'overlay_cache_refreshed': True}
