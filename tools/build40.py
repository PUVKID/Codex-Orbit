"""이미 수행한 관련 검사를 반복하지 않고 40차 납품 파일을 빌드합니다."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

from build_distribution import ROOT, copy_runtime_assets, run

p = argparse.ArgumentParser()
p.add_argument('--runtime-assets', type=Path)
p.add_argument('--compiler', type=Path, required=True)
a = p.parse_args()
(ROOT / 'work').mkdir(exist_ok=True)
release = ROOT / '배포'; release.mkdir(exist_ok=True)
os.environ['PYINSTALLER_CONFIG_DIR'] = str(ROOT / 'work/pyinstaller-cache')
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
runtime = a.runtime_assets
if runtime is None:
    runtime = Path(tempfile.mkdtemp(prefix='runtime-assets-', dir=ROOT / 'work'))
    copy_runtime_assets(ROOT / 'assets', runtime)
assert runtime.is_dir() and not runtime.is_symlink()
os.environ['ORBIT_RUNTIME_ASSETS'] = str(runtime)
run([sys.executable, '-m', 'PyInstaller', '--noconfirm',
     '--distpath', str(release), '--workpath', str(ROOT / 'work/pyinstaller'),
     str(ROOT / 'tools/orbit40.spec')], 'build-exe40-final', 1800)
for source, name in [('assets/사용법.md', '사용법.md'), ('assets/기본_지침.md', '기본_지침.md'),
                     ('README.md', '배포안내.md'), ('README.en.md', 'Usage.en.md'),
                     ('assets/calendar-art/themes.md', '연도별_월_테마.md'),
                     ('assets/calendar-art/themes.csv', '연도별_월_테마.csv'),
                     ('docs/연도별_월별_테마_전체.md', '연도별_월별_테마_전체.md'),
                     ('docs/연도별_월별_테마_전체.csv', '연도별_월별_테마_전체.csv')]:
    shutil.copy2(ROOT / source, release / name)
# 이전부터 사용하는 라이선스 묶음은 내용 변경 없이 재사용합니다.
for name in ('라이선스.zip',):
    source = ROOT / 'assets' / name
    shutil.copy2(source, release / name)
    target = release / '라이선스'; target.mkdir(exist_ok=True)
    with zipfile.ZipFile(source) as archive:
        for entry in archive.infolist():
            destination = (target / entry.filename).resolve()
            assert destination.is_relative_to(target.resolve())
        archive.extractall(target)
run([str(a.compiler), str(ROOT / 'tools/installer.iss')], 'build-installer40', 300)
rows = []
for name in ('CodexOrbit.exe', 'CodexOrbit-Setup.exe'):
    path = release / name
    rows.append({'name': name, 'path': str(path), 'bytes': path.stat().st_size,
                 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
(ROOT / 'evidence/배포40_메타.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(rows, ensure_ascii=False), flush=True)
