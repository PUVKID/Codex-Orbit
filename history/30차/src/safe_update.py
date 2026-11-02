"""공식 릴리스만 준비하고 별도 프로세스에서 설치 EXE를 교체·검사·복구합니다."""
from datetime import datetime, timezone
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

from windows_job import WindowsJob


API = 'https://api.github.com/repos/PUVKID/Codex-Orbit/releases/latest'
REPOSITORY = 'https://github.com/PUVKID/Codex-Orbit'
MAX_DOWNLOAD = 512 * 1024 * 1024
_VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?')


class UpdateError(ValueError):
    """공식 출처·무결성·교체 조건이 충족되지 않은 업데이트입니다."""


def _version(value):
    match = _VERSION.fullmatch(value) if isinstance(value, str) else None
    if (not match or any(not piece or (piece.isdigit() and len(piece) > 1 and piece[0] == '0')
                         for piece in (match.group(4) or '').split('.') if match.group(4) is not None)
            or (match.group(5) is not None and any(not piece for piece in match.group(5).split('.')))):
        raise UpdateError('정상적인 SemVer 버전이 필요합니다.')
    return tuple(map(int, match.group(1, 2, 3))), match.group(4)


def _newer(candidate, current):
    left, left_pre = _version(candidate)
    right, right_pre = _version(current)
    if left != right:
        return left > right
    if left_pre is None:
        return right_pre is not None
    if right_pre is None:
        return False
    for a, b in zip(left_pre.split('.'), right_pre.split('.')):
        if a != b:
            if a.isdigit() and b.isdigit():
                return int(a) > int(b)
            if a.isdigit() != b.isdigit():
                return not a.isdigit()
            return a > b
    return len(left_pre.split('.')) > len(right_pre.split('.'))


def _secure_url(url):
    parts = urllib.parse.urlsplit(url) if isinstance(url, str) else None
    if (parts is None or parts.scheme != 'https' or not parts.hostname or parts.username
            or parts.password or parts.port is not None or parts.fragment):
        raise UpdateError('공식 HTTPS 주소만 허용합니다.')
    return parts


def validate_download_redirect(url):
    parts = _secure_url(url)
    if parts.hostname not in ('release-assets.githubusercontent.com', 'objects.githubusercontent.com'):
        raise UpdateError('GitHub 공식 릴리스 자산 CDN만 허용합니다.')
    return url


def _asset_url(url, tag):
    parts = _secure_url(url)
    expected = '/PUVKID/Codex-Orbit/releases/download/' + urllib.parse.quote(tag, safe='') + '/CodexOrbit.exe'
    if parts.hostname != 'github.com' or parts.path != expected or parts.query:
        raise UpdateError('PUVKID/Codex-Orbit의 해당 릴리스 EXE만 허용합니다.')
    return url


class _OfficialRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        # 검증된 GitHub 다운로드에서 시작한 자산 CDN 이동만 뒤따릅니다.
        if request.full_url == API:
            raise UpdateError('릴리스 API의 예상하지 못한 리디렉션입니다.')
        validate_download_redirect(new_url)
        return super().redirect_request(request, file, code, message, headers, new_url)


def fetch_bytes(url, maximum):
    if url != API:
        parts = _secure_url(url)
        prefix = '/PUVKID/Codex-Orbit/releases/download/'
        if parts.hostname != 'github.com' or not parts.path.startswith(prefix) or parts.query:
            raise UpdateError('공식 릴리스 요청만 허용합니다.')
    request = urllib.request.Request(url, headers={'User-Agent': 'CodexOrbit-Updater',
             'Accept': 'application/vnd.github+json' if url == API else 'application/octet-stream',
             'X-GitHub-Api-Version': '2026-03-10'})
    opener = urllib.request.build_opener(_OfficialRedirect())
    chunks, size = [], 0
    with opener.open(request, timeout=20) as response:
        while True:
            chunk = response.read(min(65536, maximum - size + 1))
            if not chunk:
                break
            size += len(chunk)
            if size > maximum:
                raise UpdateError('릴리스 응답이 허용 크기를 초과했습니다.')
            chunks.append(chunk)
    return b''.join(chunks)


def _local_root():
    value = os.environ.get('LOCALAPPDATA')
    if not value:
        raise UpdateError('현재 사용자의 LOCALAPPDATA를 확인할 수 없습니다.')
    return Path(value).resolve()


def _stage_root():
    local = _local_root()
    path = (local / 'CodexOrbit/updates').resolve()
    if not path.is_relative_to(local):
        raise UpdateError('업데이트 준비 폴더가 현재 AppData 밖으로 연결되어 있습니다.')
    return path


def _digest(path):
    hasher = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def _description(value):
    if not isinstance(value, dict):
        raise UpdateError('릴리스 정보가 객체가 아닙니다.')
    version, digest, size = value.get('version'), value.get('sha256'), value.get('size')
    _version(version)
    if (_version(version)[1] is not None or not isinstance(digest, str)
            or re.fullmatch('[0-9a-fA-F]{64}', digest) is None
            or type(size) is not int or not 2 <= size <= MAX_DOWNLOAD):
        raise UpdateError('정식 버전·SHA256·자산 크기가 필요합니다.')
    return version, digest.lower(), size


def _stage_path(value, verify=True):
    version, digest, size = _description(value)
    expected = (_stage_root() / (version + '-' + digest[:12]) / 'CodexOrbit.update.exe').resolve()
    path = Path(value.get('path', '')).resolve()
    if path != expected or not path.is_relative_to(_stage_root()):
        raise UpdateError('준비 EXE의 경로가 업데이트 전용 폴더와 다릅니다.')
    if verify and (not path.is_file() or path.stat().st_size != size or _digest(path) != digest):
        raise UpdateError('준비 EXE의 크기 또는 SHA256이 일치하지 않습니다.')
    return path


def _installed(executable):
    path = Path(executable).resolve()
    local = _local_root()
    expected = (local / 'Programs/CodexOrbit/CodexOrbit.exe').resolve()
    if path != expected or not path.is_relative_to(local) or not path.is_file():
        raise UpdateError('자동 교체는 현재 사용자 AppData의 설치본에서만 지원합니다. 소스·휴대용 실행은 공식 릴리스를 직접 설치하세요.')
    return path


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix='.update-', suffix='.json', dir=path.parent)
    try:
        with os.fdopen(handle, 'w', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def _replace_file(source, destination):
    """Windows의 짧은 공유 경합만 유한하게 재시도하고 다른 오류는 그대로 전달합니다."""
    delays = (.02, .04, .08, .12)
    for attempt in range(len(delays) + 1):
        try:
            os.replace(source, destination)
            return
        except OSError as error:
            if getattr(error, 'winerror', None) not in (5, 32, 33) or attempt == len(delays):
                raise
            time.sleep(delays[attempt])


class SafeUpdater:
    def __init__(self, data_directory, executable=None):
        self.data_directory = Path(data_directory).resolve()
        self.executable = Path(executable or sys.executable).resolve()

    def check(self, current_version):
        _version(current_version)
        try:
            metadata = json.loads(fetch_bytes(API, 1024 * 1024).decode('utf-8'))
        except (ValueError, UnicodeError) as error:
            raise UpdateError('릴리스 응답을 읽을 수 없습니다.') from error
        if not isinstance(metadata, dict) or metadata.get('draft') is not False or metadata.get('prerelease') is not False:
            raise UpdateError('공개된 정식 릴리스만 사용할 수 있습니다.')
        tag = metadata.get('tag_name')
        version = tag[1:] if isinstance(tag, str) and tag.startswith('v') else tag
        _version(version)
        release_url = REPOSITORY + '/releases/tag/' + urllib.parse.quote(tag, safe='')
        if metadata.get('html_url') != release_url:
            raise UpdateError('공식 릴리스 페이지 주소가 일치하지 않습니다.')
        assets = metadata.get('assets')
        assets = [asset for asset in assets if isinstance(asset, dict) and asset.get('name') == 'CodexOrbit.exe'] if isinstance(assets, list) else []
        if len(assets) != 1 or assets[0].get('state') != 'uploaded':
            raise UpdateError('공식 CodexOrbit.exe 자산 하나가 필요합니다.')
        asset = assets[0]
        digest = asset.get('digest', '')
        value = {'version': version, 'tag': tag, 'asset_url': _asset_url(asset.get('browser_download_url'), tag),
                 'sha256': digest[7:] if isinstance(digest, str) and digest.startswith('sha256:') else '',
                 'size': asset.get('size'), 'release_url': release_url,
                 'available': _newer(version, current_version)}
        _description(value)
        return value

    def stage(self, release):
        version, digest, size = _description(release)
        tag = release.get('tag')
        if release.get('available') is not True or tag not in (version, 'v' + version):
            raise UpdateError('확인된 새 정식 릴리스만 준비할 수 있습니다.')
        url = _asset_url(release.get('asset_url'), tag)
        body = fetch_bytes(url, size)
        if len(body) != size or hashlib.sha256(body).hexdigest() != digest or not body.startswith(b'MZ'):
            raise UpdateError('다운로드 EXE의 크기·SHA256·파일 형식이 일치하지 않습니다.')
        folder = _stage_root() / (version + '-' + digest[:12])
        folder.mkdir(parents=True, exist_ok=True)
        destination = folder / 'CodexOrbit.update.exe'
        handle, temporary = tempfile.mkstemp(prefix='.download-', suffix='.exe', dir=folder)
        try:
            with os.fdopen(handle, 'wb') as stream:
                stream.write(body)
            os.replace(temporary, destination)
        finally:
            Path(temporary).unlink(missing_ok=True)
        return {'version': version, 'path': str(destination), 'sha256': digest, 'size': size}

    def apply(self, staged, parent_pid=None):
        executable = _installed(self.executable)
        path = _stage_path(staged)
        pid = os.getpid() if parent_pid is None else parent_pid
        if type(pid) is not int or pid <= 0:
            raise UpdateError('현재 앱의 유효한 프로세스 ID가 필요합니다.')
        plan = path.parent / 'plan.json'
        lock = _stage_root() / 'apply.lock'
        try:
            with lock.open('x', encoding='utf-8') as stream:
                stream.write(str(plan))
        except FileExistsError as error:
            raise UpdateError('이전 업데이트 준비가 남아 있습니다. 실행 상태를 확인해 주세요.') from error
        try:
            value = {'schema_version': 1, 'staged': dict(staged), 'executable': str(executable),
                     'data_directory': str(self.data_directory), 'parent_pid': pid,
                     'current_sha256': _digest(executable), 'created': datetime.now(timezone.utc).isoformat()}
            _write_json(plan, value)
            process = subprocess.Popen([str(path), '--orbit-apply-update', str(plan)],
                        cwd=executable.parent, close_fds=True,
                        creationflags=getattr(subprocess, 'DETACHED_PROCESS', 0) | getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
            return {'pending': True, 'pid': process.pid, 'plan': str(plan)}
        except Exception:
            lock.unlink(missing_ok=True)
            raise


def _wait_for_parent(pid):
    if os.name != 'nt':
        raise UpdateError('설치 EXE 교체는 Windows에서만 지원합니다.')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (ctypes.c_uint, ctypes.c_int, ctypes.c_uint)
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes = (ctypes.c_void_p, ctypes.c_uint)
    kernel.WaitForSingleObject.restype = ctypes.c_uint
    kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
    handle = kernel.OpenProcess(0x00100000, False, pid)
    if not handle:
        if ctypes.get_last_error() == 87:
            return
        raise UpdateError('현재 앱의 안전한 종료를 확인할 수 없습니다.')
    try:
        if kernel.WaitForSingleObject(handle, 30000) != 0:
            raise UpdateError('현재 앱이 30초 안에 종료되지 않아 교체하지 않았습니다.')
    finally:
        kernel.CloseHandle(handle)


def _smoke(executable, folder):
    data = folder / 'smoke-data'
    sessions = data / 'sessions'
    sessions.mkdir(parents=True, exist_ok=True)
    report = folder / 'smoke-result.json'
    with WindowsJob() as job:
        process = job.start([str(executable), '--smoke-test', '--data-dir', str(data),
                  '--sessions', str(sessions), '--smoke-report', str(report)], cwd=executable.parent,
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        timed_out = False
        try:
            process.communicate(timeout=45)
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:
            # 부모 선종료·상속 pipe도 Job의 후손 전체가 종료된 뒤 기존 5초 안에 회수합니다.
            job.finish(timeout=5)
        return (not timed_out and process.returncode == 0 and report.is_file() and report.stat().st_size <= 65536
                and json.loads(report.read_text(encoding='utf-8')).get('ok') is True)


def _restart(executable, data_directory):
    process = subprocess.Popen([str(executable), '--data-dir', str(data_directory)], cwd=executable.parent,
              close_fds=True, creationflags=getattr(subprocess, 'DETACHED_PROCESS', 0) | getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        return True
    return False


def apply_update_plan(plan_path, *, wait_for_parent=None, smoke=None, restart=None):
    """앱 종료 후에만 EXE를 바꾸며 새 검사·시작이 실패하면 이전 EXE를 복원합니다."""
    plan = Path(plan_path).resolve()
    if not plan.is_relative_to(_stage_root()) or plan.name != 'plan.json' or not plan.is_file() or plan.stat().st_size > 65536:
        raise UpdateError('허용된 AppData 업데이트 계획 파일이 아닙니다.')
    value = json.loads(plan.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or value.get('schema_version') != 1:
        raise UpdateError('업데이트 계획 구조가 올바르지 않습니다.')
    staged = _stage_path(value.get('staged'))
    executable = _installed(value.get('executable', ''))
    if plan.parent != staged.parent or _digest(executable) != value.get('current_sha256'):
        raise UpdateError('준비 이후 설치 EXE 또는 계획 경로가 바뀌었습니다.')
    pid = value.get('parent_pid')
    if type(pid) is not int or pid <= 0 or pid == os.getpid():
        raise UpdateError('교체 대상 앱의 프로세스 ID가 올바르지 않습니다.')
    data_directory = Path(value.get('data_directory', '')).resolve()
    backup, candidate = staged.parent / 'previous.exe', executable.with_name('CodexOrbit.pending.exe')
    if backup.exists() or candidate.exists():
        raise UpdateError('이전 교체 자료가 남아 있어 자동으로 덮어쓰지 않습니다.')
    wait_for_parent, smoke, restart = wait_for_parent or _wait_for_parent, smoke or _smoke, restart or _restart
    moved = False
    try:
        wait_for_parent(pid)
        # 같은 설치 폴더에 먼저 복사하여 마지막 교체를 같은 볼륨의 원자 이동으로 만듭니다.
        shutil.copy2(staged, candidate)
        if _digest(candidate) != value['staged']['sha256'] or _digest(executable) != value['current_sha256']:
            raise UpdateError('교체 직전 파일의 무결성이 달라졌습니다.')
        _replace_file(executable, backup)
        moved = True
        _replace_file(candidate, executable)
        if smoke(executable, staged.parent) is not True:
            raise UpdateError('새 실행 파일의 시작 검사가 실패했습니다.')
        if restart(executable, data_directory) is not True:
            raise UpdateError('새 실행 파일의 재시작이 실패했습니다.')
        result = {'updated': True, 'rolled_back': False, 'version': value['staged']['version']}
    except Exception as error:
        if not moved:
            raise
        _replace_file(backup, executable)
        recovered = restart(executable, data_directory)
        result = {'updated': False, 'rolled_back': True, 'error': str(error), 'rollback_restarted': recovered is True}
    finally:
        candidate.unlink(missing_ok=True)
        (_stage_root() / 'apply.lock').unlink(missing_ok=True)
    _write_json(staged.parent / 'update-result.json', result)
    return result


def handle_update_cli(argv):
    if not argv or argv[0] != '--orbit-apply-update':
        return None
    try:
        if len(argv) != 2:
            raise UpdateError('업데이트 계획 파일 인자가 필요합니다.')
        result = apply_update_plan(argv[1])
        return 0 if result.get('updated') else 1
    except Exception as error:
        print('Codex Orbit 업데이트 실패: ' + str(error), file=sys.stderr)
        return 1
