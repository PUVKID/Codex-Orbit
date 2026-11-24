"""격리된 합성 데이터로 새 알림 센터와 두 테마의 연결만 확인합니다."""
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication


def check_workspace(controller, folder):
    from app import stamp
    from theme import apply_theme
    from update_widgets import UpdateDialog
    c = controller
    folder = Path(folder)
    c.settings.values['popup'] = False
    c.settings.values['notification_sound'] = False
    original_count = len(c.features.snapshot()['events'])
    c.receive({'id': 'test37-model', 'target': 'synthetic37', 'kind': 'settings', 'time': stamp(),
               'chat_name': '검사용 채팅 · 실제 채팅 아님',
               'before': {'model': 'gpt-6.1-sol', 'effort': 'medium'},
               'after': {'model': 'gpt-6.1-terra', 'effort': 'high'},
               'reason': '화면 연결을 확인하는 합성 기록입니다.'})
    c.window.resize(1120, 820)
    c.window.show()
    QTest.mouseClick(c.workspace_button37, Qt.MouseButton.LeftButton)
    panel = c.workspace_panel
    assert c.orbit29.stack.currentWidget() is panel
    assert len(panel._rows) == original_count + 1
    QTest.mouseClick(panel.search, Qt.MouseButton.LeftButton)
    panel.search.setText('없는 검색어')
    assert not panel._rows and panel.count.text()
    panel.search.clear()
    assert len(panel._rows) == original_count + 1
    panel._copy()
    assert '검사용 채팅' in QApplication.clipboard().text()
    c.orbit29.option('broadcast_mode', True)
    panel._copy()
    assert '검사용 채팅' not in QApplication.clipboard().text()
    c.orbit29.option('broadcast_mode', False)
    before_preview = len(c.features.snapshot()['events'])
    c.preview_notice37('effort')
    assert len(c.features.snapshot()['events']) == before_preview
    assert '미리보기' in c.preview_card37.title.text()
    c.preview_card37.grab().save(str(folder / '미리보기37.png'))
    c.preview_card37.hide()
    for mode in ('light', 'dark'):
        c.orbit29.option('ui_theme', mode)
        QApplication.processEvents()
        assert c.settings.values['ui_theme'] == mode
        assert c.window.grab().save(str(folder / ('알림센터37_' + mode + '.png')))
        panel.tabs.setCurrentIndex(1)
        QApplication.processEvents()
        assert c.window.grab().save(str(folder / ('알림설정37_' + mode + '.png')))
        panel.tabs.setCurrentIndex(0)
    dialog = UpdateDialog(c)
    assert '3.7.0' in dialog.label.text()
    dialog.error_text = '<b>합성 오류 원문</b>'
    dialog.retranslate()
    dialog.details_button.setChecked(True)
    assert dialog.error_details.toPlainText() == '<b>합성 오류 원문</b>'
    assert dialog.label.textFormat() == Qt.TextFormat.PlainText
    dialog.show()
    QApplication.processEvents()
    assert dialog.grab().save(str(folder / '업데이트37.png'))
    dialog.close()
    panel.tabs.setCurrentIndex(0)
    return {'new_workspace_connected': True, 'themes': ['light', 'dark'],
            'privacy_copy_masked': True, 'preview_not_recorded': True,
            'update_dialog_connected': True, 'synthetic_only': True}
