"""검증된 소스에서 단일 실행 파일과 현재 사용자용 설치본을 만듭니다."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def run(argv, name, timeout):
    """실제 인자와 종료 결과를 별도 파일에 보존합니다."""
    started = time.time()
    build_env = os.environ.copy()
    base_python = Path(sys.base_prefix)
    windows = Path(os.environ.get('SystemRoot', r'C:\Windows'))
    # 외부 PDF 도구 등의 동명 ICU DLL이 Qt 의존성으로 들어오지 않게 합니다.
    build_env['PATH'] = os.pathsep.join(map(str, [Path(sys.executable).parent, base_python,
                                                windows / 'System32', windows]))
    process = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, shell=False, env=build_env)
    captured = bytearray()
    total_bytes = 0
    def collect():
        nonlocal total_bytes
        while True:
            chunk = process.stdout.read(65536)
            if not chunk:
                break
            total_bytes += len(chunk)
            captured.extend(chunk[:max(0, 524288 - len(captured))])
    reader = threading.Thread(target=collect, daemon=True)
    reader.start()
    timed_out = False
    try:
        exit_code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        exit_code = process.wait(timeout=15)
    reader.join(timeout=5)
    process.stdout.close()
    raw = bytes(captured)
    (ROOT / 'work' / (name + '.raw')).write_bytes(raw)
    try:
        decoded = raw.decode('utf-8')
        valid_utf8 = True
    except UnicodeDecodeError:
        decoded = raw.decode('utf-8', errors='replace')
        valid_utf8 = False
    output = decoded.encode('utf-8')
    (ROOT / 'work' / (name + '.log')).write_bytes(output)
    record = {'argv': argv, 'cwd': str(ROOT), 'exit_code': exit_code, 'timed_out': timed_out,
              'started_at': started, 'elapsed_seconds': time.time() - started,
              'output_bytes': total_bytes, 'captured_bytes': len(raw),
              'valid_utf8': valid_utf8, 'output_truncated': total_bytes > len(raw)}
    (ROOT / 'work' / (name + '.json')).write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False), flush=True)
    if exit_code or timed_out:
        print(output[-7000:].decode('utf-8', errors='replace'))
        raise SystemExit(exit_code or 1)


def main():
    # 새로 받은 공개 소스에도 검사용·빌드용 비공개 작업 폴더를 준비합니다.
    (ROOT / 'work').mkdir(exist_ok=True)
    release = ROOT / '배포'
    release.mkdir(exist_ok=True)
    # 빌드 중 임시 추출물은 프로젝트의 D 드라이브 작업 폴더에 둡니다.
    os.environ['PYINSTALLER_CONFIG_DIR'] = str(ROOT / 'work' / 'pyinstaller-cache')
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    run([sys.executable, '-B', '-X', 'utf8', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], 'build-tests', 90)
    run([sys.executable, '-B', '-X', 'utf8', 'tools/check_sources.py'], 'build-sources', 30)
    # 교체된 원소 영상은 소스 자료에 보존하고 현재 달력 GUI에 필요한 자산만 실행본에 넣습니다.
    runtime_assets = Path(tempfile.mkdtemp(prefix='runtime-assets-', dir=ROOT / 'work'))
    for source in (ROOT / 'assets').iterdir():
        if source.name == 'elements3d':
            continue
        if source.is_dir():
            shutil.copytree(source, runtime_assets / source.name)
        else:
            shutil.copy2(source, runtime_assets / source.name)
    args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onefile',
            '--windowed', '--name', 'CodexOrbit', '--icon', str(ROOT / 'assets' / 'Orbit.ico'), '--distpath', str(release),
            '--workpath', str(ROOT / 'work' / 'pyinstaller'),
            '--specpath', str(ROOT / 'work'), '--add-data', str(runtime_assets) + ';assets',
            '--collect-all', 'moderngl', '--collect-all', 'glcontext',
            '--paths', str(ROOT / 'src'), str(ROOT / 'src' / 'app.py')]
    run(args, 'build-exe', 360)
    for name in ('사용법.md', '기본_지침.md'):
        shutil.copy2(ROOT / 'assets' / name, release / name)
    shutil.copy2(ROOT / 'README.md', release / '배포안내.md')
    shutil.copy2(ROOT / 'README.en.md', release / 'Usage.en.md')
    for suffix in ('md', 'csv'):
        shutil.copy2(ROOT / 'assets' / 'calendar-art' / ('themes.' + suffix),
                     release / ('연도별_월_테마.' + suffix))
        # 월별 주제만 빠르게 읽을 수 있는 전체 표도 함께 전달합니다.
        shutil.copy2(ROOT / 'docs' / ('연도별_월별_테마_전체.' + suffix),
                     release / ('연도별_월별_테마_전체.' + suffix))
    license_dir = release / '라이선스'
    license_dir.mkdir(exist_ok=True)
    for path in (ROOT / 'assets').glob('*LICENSE*'):
        shutil.copy2(path, license_dir / path.name)
    shutil.copy2(ROOT / 'assets' / 'OFL.txt', license_dir / 'NanumGothic-OFL.txt')
    shutil.copy2(ROOT / 'assets' / 'atom3d' / 'LICENSE.txt', license_dir / 'Atom3D-LICENSE.txt')
    shutil.copy2(ROOT / 'assets' / 'icons3d' / 'LICENSE.txt', license_dir / 'Icons3D-LICENSE.txt')
    shutil.copy2(ROOT / 'assets' / 'elements3d' / 'LICENSE.txt', license_dir / 'Elements3D-LICENSE.txt')
    # 런타임 입체 렌더에 포함하는 배포판의 원래 라이선스 문서를 함께 전달합니다.
    for package in ('moderngl', 'glcontext', 'numpy', 'Pillow'):
        distribution = importlib.metadata.distribution(package)
        for entry in distribution.files or ():
            if '.dist-info' in str(entry) and any(word in str(entry).lower() for word in ('license', 'copying', 'notice')):
                source = Path(distribution.locate_file(entry))
                if source.is_file():
                    destination = license_dir / package / Path(*entry.parts[1:])
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
    archive = release / '소스와_재빌드.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for folder in ('src', 'tests', 'assets', 'tools'):
            for path in sorted((ROOT / folder).rglob('*')):
                if path.is_file() and '__pycache__' not in path.parts:
                    bundle.write(path, path.relative_to(ROOT))
        for name in ('requirements.txt', 'README.md', 'README.en.md'):
            bundle.write(ROOT / name, name)
        for suffix in ('md', 'csv'):
            name = 'docs/연도별_월별_테마_전체.' + suffix
            bundle.write(ROOT / name, name)
    compiler = Path(os.environ.get('CODEX_ORBIT_ISCC') or ROOT / 'work' / 'inno' / 'ISCC.exe')
    run([str(compiler), str(ROOT / 'tools' / 'installer.iss')], 'build-installer', 180)
    hashes = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
              for p in release.iterdir() if p.is_file() and p.suffix in ('.exe', '.zip')}
    (release / 'SHA256.json').write_text(json.dumps(hashes, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(hashes, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
