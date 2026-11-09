"""화면 검사 모드가 기존 자료나 일반 실행 옵션에 접근하지 않는지 확인합니다."""
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from ui_smoke32 import prepare_directory

class UiSmokeBoundary32Tests(unittest.TestCase):
    def test_explicit_new_directory_creates_only_synthetic_marker(self):
        with tempfile.TemporaryDirectory() as parent:
            path = Path(parent) / '새검사'
            self.assertEqual(prepare_directory(SimpleNamespace(data_dir=path), ['--ui-smoke-test','--data-dir',str(path)]), path)
            self.assertEqual(sorted(p.name for p in path.iterdir()), ['합성검사전용.json'])
    def test_default_directory_is_rejected_without_creating_files(self):
        with tempfile.TemporaryDirectory() as parent:
            path = Path(parent) / '없는폴더'
            with self.assertRaises(ValueError):
                prepare_directory(SimpleNamespace(data_dir=path), ['--ui-smoke-test'])
            self.assertFalse(path.exists())
    def test_existing_directory_and_original_bytes_are_preserved(self):
        with tempfile.TemporaryDirectory() as parent:
            path = Path(parent); original = path / '사용자원본.txt'; original.write_bytes(b'original')
            with self.assertRaises(ValueError):
                prepare_directory(SimpleNamespace(data_dir=path), ['--data-dir',str(path)])
            self.assertEqual(original.read_bytes(), b'original')
            self.assertEqual(len(list(path.iterdir())), 1)
    def test_sessions_account_and_external_report_options_are_rejected(self):
        with tempfile.TemporaryDirectory() as parent:
            for name in ('sessions','usage_smoke_test','smoke_test','smoke_report','show_details','show_event'):
                with self.subTest(option=name):
                    path = Path(parent) / name
                    args = SimpleNamespace(data_dir=path, **{name: True})
                    with self.assertRaises(ValueError):
                        prepare_directory(args, ['--data-dir',str(path)])
                    self.assertFalse(path.exists())
