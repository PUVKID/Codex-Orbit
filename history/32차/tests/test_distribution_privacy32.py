"""실행 자산에서 내부 생성 기록만 제외하는 계약을 확인합니다."""
import hashlib
from pathlib import Path
import tempfile
import unittest
import importlib.util


# 독립 검사 스크립트의 실행 위치와 관계없이 검증 대상 도구를 직접 읽습니다.
_spec = importlib.util.spec_from_file_location(
    'distribution_privacy32_build', Path(__file__).resolve().parents[1] / 'tools' / 'build_distribution.py')
build_distribution = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_distribution)


class DistributionPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'assets'
        self.destination = Path(self.temp.name) / 'runtime'
        self.destination.mkdir()
        self.data = {
            'atom3d/creation_report.json': b'private creation',
            'icons3d/direct_validation.json': b'private validation',
            'other/creation_report.json': b'public same name',
            'atom3d/nested/creation_report.json': b'public nested name',
            'other/direct_validation.json': b'public other validation',
            'atom3d/LICENSE.txt': b'original license A',
            'icons3d/LICENSE.txt': b'original license B',
            'materials/notice.md': b'material attribution',
            'Orbit.ico': bytes(range(256)),
            'atom3d/frames.bin': b'required frames',
            'elements3d/legacy.bin': b'legacy source only',
        }
        for name, data in self.data.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    def copy(self):
        build_distribution.copy_runtime_assets(self.source, self.destination)

    def test_only_exact_internal_record_paths_are_excluded(self):
        self.copy()
        for name in ('atom3d/creation_report.json', 'icons3d/direct_validation.json'):
            self.assertFalse((self.destination / name).exists(), name)
        for name in ('other/creation_report.json', 'atom3d/nested/creation_report.json', 'other/direct_validation.json'):
            self.assertEqual((self.destination / name).read_bytes(), self.data[name])

    def test_required_assets_and_licenses_keep_exact_bytes(self):
        self.copy()
        for name in ('atom3d/LICENSE.txt', 'icons3d/LICENSE.txt', 'materials/notice.md', 'Orbit.ico', 'atom3d/frames.bin'):
            self.assertEqual((self.destination / name).read_bytes(), self.data[name], name)

    def test_source_inventory_and_hashes_are_unchanged(self):
        def inventory():
            return {str(p.relative_to(self.source)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.source.rglob('*') if p.is_file()}
        before = inventory()
        self.copy()
        self.assertEqual(inventory(), before)
        self.assertEqual(len(before), len(self.data))

    def test_existing_elements3d_exclusion_is_preserved(self):
        self.copy()
        self.assertFalse((self.destination / 'elements3d').exists())
        expected = set(self.data) - {'atom3d/creation_report.json', 'icons3d/direct_validation.json', 'elements3d/legacy.bin'}
        actual = {p.relative_to(self.destination).as_posix() for p in self.destination.rglob('*') if p.is_file()}
        self.assertEqual(actual, expected)
