"""37차 변경 경로만 합성 자료로 검사하며 실제 설치·네트워크는 사용하지 않습니다."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_safe_update29 import SafeUpdateTests
import safe_update as update


class Update37Tests(unittest.TestCase):
    setUp = SafeUpdateTests.setUp
    metadata = SafeUpdateTests.metadata
    checked = SafeUpdateTests.checked
    staged = SafeUpdateTests.staged
    plan = SafeUpdateTests.plan
    assert_personal_data_preserved = SafeUpdateTests.assert_personal_data_preserved

    def test_disk_requirement_uses_staging_volume_before_network(self):
        release = self.checked()
        required = release['size'] * 3 + 64 * 1024 * 1024
        with patch('safe_update.shutil.disk_usage', return_value=SimpleNamespace(free=required - 1)) as disk, \
             patch('safe_update.fetch_bytes') as fetch:
            with self.assertRaises(update.UpdateError):
                self.updater.stage(release)
            fetch.assert_not_called()
            self.assertTrue(Path(disk.call_args.args[0]).is_relative_to(update._stage_root()))
        phases = []
        with patch('safe_update.shutil.disk_usage', return_value=SimpleNamespace(free=required)), \
             patch('safe_update.fetch_bytes', return_value=self.body):
            self.updater.stage(release, progress=phases.append)
        self.assertEqual(phases, ['download', 'verify'])
        self.assert_personal_data_preserved()

    def test_receipt_allowed_fields_and_bounded_reader(self):
        self.assertTrue(update._record_update_result(self.data, '3.7.0', 'updated'))
        self.assertEqual(set(update.read_update_result(self.data)), {'status', 'time', 'version'})
        path = self.data / 'update-result.json'
        good = json.loads(path.read_text(encoding='utf-8'))
        for bad in ({**good, 'path': 'private'}, {**good, 'error': 'secret'},
                    {**good, 'time': 'yesterday'}, {**good, 'version': '../private'}):
            path.write_text(json.dumps(bad), encoding='utf-8')
            self.assertEqual(update.read_update_result(self.data), {})
        path.write_bytes(b' ' * 16385)
        self.assertEqual(update.read_update_result(self.data), {})

    def test_receipt_reparse_point_is_rejected_without_following(self):
        update._record_update_result(self.data, '3.7.0', 'updated')
        plan = self.plan()
        original = Path.lstat
        def attributes(path):
            info = original(path)
            if path == self.data:
                return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400)
            return info
        with patch.object(Path, 'lstat', attributes):
            self.assertEqual(update.read_update_result(self.data), {})
            self.assertFalse(update._record_update_result(self.data, '3.7.0', 'failed', 'apply_failed'))
            with patch('safe_update._write_json') as writer:
                result = update.apply_update_plan(plan, wait_for_parent=lambda pid: None,
                                                 smoke=lambda *args: False, restart=lambda *args: True)
                self.assertTrue(result['rollback_restarted'])
                writer.assert_not_called()
        self.assertEqual(self.updater.data_directory, self.data.absolute())

    def test_rollback_receipt_distinguishes_recovered_start(self):
        result = update.apply_update_plan(self.plan(), wait_for_parent=lambda pid: None,
                                         smoke=lambda *args: False, restart=lambda *args: True)
        self.assertTrue(result['rollback_restarted'])
        receipt = update.read_update_result(self.data)
        self.assertEqual((receipt['status'], receipt['error']), ('rolled_back', 'smoke_failed'))
        self.assertEqual(self.exe.read_bytes(), self.old)
        self.assert_personal_data_preserved()

    def test_rollback_start_failure_is_not_successful_recovery(self):
        result = update.apply_update_plan(self.plan(), wait_for_parent=lambda pid: None,
                                         smoke=lambda *args: False, restart=lambda *args: False)
        self.assertFalse(result['rollback_restarted'])
        receipt = update.read_update_result(self.data)
        self.assertEqual((receipt['status'], receipt['error']), ('failed', 'rollback_restart_failed'))
        self.assertEqual(self.exe.read_bytes(), self.old)

    def test_receipt_write_failure_never_blocks_rollback_or_masks_original(self):
        plan = self.plan()
        with patch('safe_update._write_json', side_effect=OSError('제어된 기록 실패')):
            result = update.apply_update_plan(plan, wait_for_parent=lambda pid: None,
                                             smoke=lambda *args: False, restart=lambda *args: True)
        self.assertTrue(result['rollback_restarted'])
        self.assertEqual(self.exe.read_bytes(), self.old)
        (plan.parent / 'previous.exe').unlink(missing_ok=True)
        error = OSError('원래 부모 대기 실패')
        def fail(pid):
            raise error
        with patch('safe_update._write_json', side_effect=OSError('제어된 기록 실패')):
            with self.assertRaises(OSError) as raised:
                update.apply_update_plan(plan, wait_for_parent=fail)
        self.assertIs(raised.exception, error)

    def test_dialog_version_plaintext_result_and_verified_copy(self):
        from PySide6.QtWidgets import QApplication, QWidget
        from PySide6.QtCore import QEvent
        import update_widgets as widgets
        app = QApplication.instance() or QApplication([])
        window = QWidget()
        controller = SimpleNamespace(window=window, settings=SimpleNamespace(directory=self.data), request_quit=lambda: None)
        update._record_update_result(self.data, '3.7.0', 'failed', 'restart_failed')
        dialog = widgets.UpdateDialog(controller)
        self.assertEqual(widgets.VERSION, '3.7.0')
        self.assertIn('3.7.0', dialog.label.text())
        self.assertFalse(dialog.copy_button.isVisible())
        with patch.object(widgets.QDesktopServices, 'openUrl') as open_url:
            dialog.open_release()
            self.assertEqual(open_url.call_args.args[0].toString(), widgets.RELEASES_URL)
        dialog.release = self.checked()
        dialog.retranslate()
        self.assertIn('MB', dialog.label.text())
        dialog.stage_kind = 'stage'
        dialog.handle_result(self.staged(), None)
        dialog.copy_sha()
        self.assertEqual(app.clipboard().text(), dialog.staged['sha256'])
        dialog.error_text = '<b>원문</b>'
        dialog.retranslate()
        dialog.details_button.setChecked(True)
        self.assertEqual(dialog.error_details.toPlainText(), '<b>원문</b>')
        dialog.busy = True
        event = QEvent(QEvent.Type.Close)
        dialog.closeEvent(event)
        self.assertFalse(event.isAccepted())
        dialog.busy = False
        dialog.close()
        reopened = widgets.UpdateDialog(controller)
        self.assertEqual(reopened.recent_result['status'], 'failed')
        self.assert_personal_data_preserved()
        reopened.close()
        window.close()


# 원래 검사 클래스를 이 모듈의 unittest 수집 대상에서 제외합니다.
del SafeUpdateTests

if __name__ == '__main__':
    unittest.main()
