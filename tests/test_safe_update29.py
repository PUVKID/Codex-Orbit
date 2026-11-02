"""네트워크·실제 EXE 실행 없이 공식 릴리스 검증과 교체·복구를 검사합니다."""
import hashlib
import importlib.util
import ctypes
import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
update = __import__('safe_update') if importlib.util.find_spec('safe_update') else None


class SafeUpdateTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(update, '안전한 릴리스 업데이트 API가 아직 없습니다.')
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.local = Path(folder.name) / 'Local'
        self.data = self.local / 'CodexOrbit'
        self.exe = self.local / 'Programs/CodexOrbit/CodexOrbit.exe'
        self.exe.parent.mkdir(parents=True)
        self.data.mkdir(parents=True)
        self.old = b'MZ' + b'old-executable' * 8
        self.body = b'MZ' + b'new-executable' * 8
        self.exe.write_bytes(self.old)
        (self.data / 'settings.json').write_text('{"language":"ko"}', encoding='utf-8')
        (self.data / 'AGENTS.md').write_text('사용자 지침 원문', encoding='utf-8')
        self.environment = patch.dict(os.environ, {'LOCALAPPDATA': str(self.local)})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.updater = update.SafeUpdater(self.data, executable=self.exe)

    def metadata(self):
        return {'tag_name': 'v3.1.0', 'draft': False, 'prerelease': False,
                'html_url': 'https://github.com/PUVKID/Codex-Orbit/releases/tag/v3.1.0',
                'assets': [{'name': 'CodexOrbit.exe', 'state': 'uploaded',
                            'browser_download_url': 'https://github.com/PUVKID/Codex-Orbit/releases/download/v3.1.0/CodexOrbit.exe',
                            'size': len(self.body), 'digest': 'sha256:' + hashlib.sha256(self.body).hexdigest()}]}

    def checked(self, current='3.0.0'):
        with patch('safe_update.fetch_bytes', return_value=json.dumps(self.metadata()).encode('utf-8')):
            return self.updater.check(current)

    def staged(self):
        release = self.checked()
        with patch('safe_update.fetch_bytes', return_value=self.body):
            return self.updater.stage(release)

    def plan(self):
        staged = self.staged()
        with patch('safe_update.subprocess.Popen', return_value=SimpleNamespace(pid=12345)):
            launch = self.updater.apply(staged, parent_pid=99999)
        self.assertTrue(launch['pending'])
        return Path(launch['plan'])

    def assert_personal_data_preserved(self):
        self.assertEqual((self.data / 'settings.json').read_text(encoding='utf-8'), '{"language":"ko"}')
        self.assertEqual((self.data / 'AGENTS.md').read_text(encoding='utf-8'), '사용자 지침 원문')

    def test_official_release_semver_and_sha_are_derived_from_metadata(self):
        release = self.checked()
        self.assertTrue(release['available'])
        self.assertEqual(release['version'], '3.1.0')
        self.assertEqual(release['sha256'], hashlib.sha256(self.body).hexdigest())
        self.assertFalse(self.checked('3.10.0')['available'])
        for version in ('3', '03.0.0', '3.0.0/../../x', True):
            with self.subTest(version=version), self.assertRaises((ValueError, update.UpdateError)):
                self.checked(version)

    def test_missing_hash_unofficial_host_and_draft_are_rejected(self):
        cases = []
        value = self.metadata()
        del value['assets'][0]['digest']
        cases.append(value)
        for url in ('http://github.com/PUVKID/Codex-Orbit/releases/download/v3.1.0/CodexOrbit.exe',
                    'https://github.com.evil.invalid/PUVKID/Codex-Orbit/releases/download/v3.1.0/CodexOrbit.exe',
                    'https://github.com/OTHER/Other/releases/download/v3.1.0/CodexOrbit.exe'):
            value = self.metadata()
            value['assets'][0]['browser_download_url'] = url
            cases.append(value)
        value = self.metadata()
        value['draft'] = True
        cases.append(value)
        for metadata in cases:
            with self.subTest(metadata=metadata), patch('safe_update.fetch_bytes', return_value=json.dumps(metadata).encode('utf-8')):
                with self.assertRaises(update.UpdateError):
                    self.updater.check('3.0.0')

    def test_stage_verifies_bytes_inside_same_appdata_before_touching_executable(self):
        staged = self.staged()
        path = Path(staged['path'])
        self.assertTrue(path.resolve().is_relative_to((self.data / 'updates').resolve()))
        self.assertEqual(path.read_bytes(), self.body)
        self.assertEqual(self.exe.read_bytes(), self.old)
        self.assert_personal_data_preserved()

    def test_bad_sha_size_and_path_escape_never_replace_existing_executable(self):
        release = self.checked()
        with patch('safe_update.fetch_bytes', return_value=b'MZtampered'):
            with self.assertRaises(update.UpdateError):
                self.updater.stage(release)
        for key, value in [('version', '../escape'), ('size', True), ('sha256', '0' * 63)]:
            with self.subTest(key=key), self.assertRaises(update.UpdateError):
                self.updater.stage({**release, key: value})
        self.assertEqual(self.exe.read_bytes(), self.old)
        self.assert_personal_data_preserved()

    def test_transaction_replaces_after_parent_exit_and_preserves_settings_md(self):
        plan = self.plan()
        observed = []
        result = update.apply_update_plan(plan, wait_for_parent=lambda pid: observed.append(('wait', pid)),
                  smoke=lambda executable, directory: executable.read_bytes() == self.body,
                  restart=lambda executable, directory: observed.append(('restart', executable.read_bytes())) or True)
        self.assertTrue(result['updated'])
        self.assertFalse(result['rolled_back'])
        self.assertEqual(observed[0], ('wait', 99999))
        self.assertEqual(self.exe.read_bytes(), self.body)
        self.assert_personal_data_preserved()

    def test_failed_smoke_rolls_back_and_restarts_previous_executable(self):
        plan = self.plan()
        restarted = []
        result = update.apply_update_plan(plan, wait_for_parent=lambda pid: None, smoke=lambda *args: False,
                  restart=lambda executable, directory: restarted.append(executable.read_bytes()) or True)
        self.assertFalse(result['updated'])
        self.assertTrue(result['rolled_back'])
        self.assertEqual(self.exe.read_bytes(), self.old)
        self.assertEqual(restarted, [self.old])
        self.assert_personal_data_preserved()

    def test_failed_restart_rolls_back_then_restarts_previous_executable(self):
        plan = self.plan()
        restarted = []
        def restart(executable, directory):
            restarted.append(executable.read_bytes())
            return len(restarted) > 1
        result = update.apply_update_plan(plan, wait_for_parent=lambda pid: None, smoke=lambda *args: True, restart=restart)
        self.assertTrue(result['rolled_back'])
        self.assertEqual(restarted, [self.body, self.old])
        self.assertEqual(self.exe.read_bytes(), self.old)
        self.assert_personal_data_preserved()

    def test_tampered_plan_or_staged_file_is_rejected_before_any_replacement(self):
        plan = self.plan()
        metadata = json.loads(plan.read_text(encoding='utf-8'))
        Path(metadata['staged']['path']).write_bytes(b'MZchanged')
        with self.assertRaises(update.UpdateError):
            update.apply_update_plan(plan, wait_for_parent=lambda pid: None)
        self.assertEqual(self.exe.read_bytes(), self.old)
        metadata['staged']['path'] = str(self.local.parent / 'escape.exe')
        plan.write_text(json.dumps(metadata), encoding='utf-8')
        with self.assertRaises(update.UpdateError):
            update.apply_update_plan(plan, wait_for_parent=lambda pid: None)
        self.assert_personal_data_preserved()

    def test_source_execution_can_check_but_cannot_launch_replacement(self):
        updater = update.SafeUpdater(self.data, executable=Path(sys.executable))
        with self.assertRaises(update.UpdateError):
            updater.apply(self.staged(), parent_pid=99999)
        self.assertEqual(self.exe.read_bytes(), self.old)

    def test_normal_cli_is_untouched_and_redirects_are_checked(self):
        self.assertIsNone(update.handle_update_cli(['--show-details']))
        for url in ('http://release-assets.githubusercontent.com/x', 'https://evil.invalid/file',
                    'file:///C:/secret', 'https://release-assets.githubusercontent.com@evil.invalid/file'):
            with self.subTest(url=url), self.assertRaises(update.UpdateError):
                update.validate_download_redirect(url)
        self.assertEqual(update.validate_download_redirect('https://release-assets.githubusercontent.com/github-production-release-asset/file'),
                         'https://release-assets.githubusercontent.com/github-production-release-asset/file')

    def test_empty_semver_build_identifiers_are_rejected(self):
        for version in ('3.0.0+a..b', '3.0.0+.', '3.0.0+a.'):
            with self.subTest(version=version), self.assertRaises(update.UpdateError):
                self.checked(version)

    def test_transient_installed_file_sharing_conflict_is_retried_without_data_changes(self):
        plan = self.plan()
        original = os.replace
        attempted = []
        def replace(source, destination):
            if Path(source) == self.exe and Path(destination).name == 'previous.exe':
                attempted.append(True)
                if len(attempted) == 1:
                    error = OSError('제어된 일시 파일 공유 경합')
                    error.winerror = 32
                    raise error
            return original(source, destination)
        try:
            with patch('safe_update.os.replace', side_effect=replace):
                result = update.apply_update_plan(plan, wait_for_parent=lambda pid: None,
                                                  smoke=lambda *args: True, restart=lambda *args: True)
        except OSError as error:
            self.fail('일시 공유 경합을 해결하지 못했습니다: ' + str(error))
        self.assertTrue(result['updated'])
        self.assertEqual(self.exe.read_bytes(), self.body)
        self.assert_personal_data_preserved()

    def test_persistent_sharing_conflict_is_bounded_and_keeps_old_executable(self):
        plan = self.plan()
        original = os.replace
        attempted = []
        def replace(source, destination):
            if Path(source) == self.exe and Path(destination).name == 'previous.exe':
                attempted.append(True)
                error = OSError('제어된 지속 파일 공유 경합')
                error.winerror = 32
                raise error
            return original(source, destination)
        with patch('safe_update.os.replace', side_effect=replace), self.assertRaises(OSError):
            update.apply_update_plan(plan, wait_for_parent=lambda pid: None,
                                     smoke=lambda *args: True, restart=lambda *args: True)
        self.assertLessEqual(len(attempted), 5)
        self.assertEqual(self.exe.read_bytes(), self.old)
        self.assert_personal_data_preserved()

    @staticmethod
    def process_alive(pid):
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = (ctypes.c_uint, ctypes.c_int, ctypes.c_uint)
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.WaitForSingleObject.argtypes = (ctypes.c_void_p, ctypes.c_uint)
        kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
        handle = kernel.OpenProcess(0x00100000, False, pid)
        if not handle:
            return False
        try:
            return kernel.WaitForSingleObject(handle, 0) == 258
        finally:
            kernel.CloseHandle(handle)

    def test_smoke_timeout_terminates_the_exact_created_process_tree(self):
        ready = self.local / 'owned-processes.json'
        child_code = 'import time;time.sleep(20)'
        source = ('import json,os,pathlib,subprocess,sys,time;'
                  'child=subprocess.Popen([sys.executable,"-c",' + repr(child_code) + '],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);'
                  'pathlib.Path(' + repr(str(ready)) + ').write_text(json.dumps([os.getpid(),child.pid]));time.sleep(20)')
        original = subprocess.Popen
        owned = []
        def launch(argv, **kwargs):
            if Path(argv[0]) != self.exe:
                return original(argv, **kwargs)
            process = original([sys._base_executable, '-B', '-X', 'utf8', '-c', source], **kwargs)
            owned.append(process.pid)
            communicate = process.communicate
            def bounded(*args, **options):
                if options.get('timeout') == 45:
                    deadline = time.monotonic() + 3
                    while not ready.exists() and time.monotonic() < deadline:
                        time.sleep(.005)
                    options['timeout'] = .05
                return communicate(*args, **options)
            process.communicate = bounded
            return process
        try:
            with patch('safe_update.subprocess.Popen', side_effect=launch):
                try:
                    result = update._smoke(self.exe, self.data)
                except subprocess.TimeoutExpired:
                    result = False
            self.assertTrue(ready.is_file(), '직접 만든 자식의 소유 PID 기록이 필요합니다.')
            owned.extend(json.loads(ready.read_text(encoding='utf-8')))
            self.assertFalse(result)
            self.assertTrue(all(not self.process_alive(pid) for pid in owned), '시간 초과 뒤 직접 만든 후손이 남았습니다.')
        finally:
            if ready.exists():
                owned.extend(json.loads(ready.read_text(encoding='utf-8')))
            for pid in dict.fromkeys(owned):
                if self.process_alive(pid):
                    subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True, timeout=5)
            deadline = time.monotonic() + 2
            while any(self.process_alive(pid) for pid in owned) and time.monotonic() < deadline:
                time.sleep(.005)
            self.assertTrue(all(not self.process_alive(pid) for pid in owned), '제어 fixture의 정확한 생성 PID 정리가 끝나지 않았습니다.')

    def test_parent_exit_with_inherited_pipes_still_reaps_owned_descendant(self):
        ready = self.local / 'exited-parent-processes.json'
        source = ('import json,os,pathlib,subprocess,sys;'
                  'child=subprocess.Popen([sys.executable,"-c","import time;time.sleep(20)"]);'
                  'pathlib.Path(' + repr(str(ready)) + ').write_text(json.dumps([os.getpid(),child.pid]));os._exit(7)')
        original = subprocess.Popen
        owned = []
        def launch(argv, **kwargs):
            if Path(argv[0]) != self.exe:
                return original(argv, **kwargs)
            process = original([sys._base_executable, '-B', '-X', 'utf8', '-c', source], **kwargs)
            owned.append(process.pid)
            communicate = process.communicate
            def bounded(*args, **options):
                if options.get('timeout') == 45:
                    process.wait(timeout=3)
                    options['timeout'] = .05
                return communicate(*args, **options)
            process.communicate = bounded
            return process
        try:
            with patch('safe_update.subprocess.Popen', side_effect=launch):
                try:
                    result = update._smoke(self.exe, self.data)
                except subprocess.TimeoutExpired as error:
                    self.fail('부모 선종료 후 상속된 출력 파이프와 후손을 회수하지 못했습니다: ' + str(error))
            self.assertTrue(ready.is_file())
            owned.extend(json.loads(ready.read_text(encoding='utf-8')))
            self.assertFalse(result)
            self.assertTrue(all(not self.process_alive(pid) for pid in owned), '부모 선종료 뒤 직접 만든 후손이 남았습니다.')
        finally:
            if ready.is_file():
                owned.extend(json.loads(ready.read_text(encoding='utf-8')))
            for pid in dict.fromkeys(owned):
                if self.process_alive(pid):
                    subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True, timeout=5)
            deadline = time.monotonic() + 2
            while any(self.process_alive(pid) for pid in owned) and time.monotonic() < deadline:
                time.sleep(.005)
            self.assertTrue(all(not self.process_alive(pid) for pid in owned))

    def test_job_is_assigned_before_user_code_and_preserves_other_process(self):
        self.assertIsNotNone(importlib.util.find_spec('windows_job'), '실행 전 소유 Job 연결 API가 필요합니다.')
        from windows_job import WindowsJob
        marker = self.local / 'user-code-ran.txt'
        source = 'from pathlib import Path;Path(' + repr(str(marker)) + ').write_text("ready");print("latest")'
        outside = subprocess.Popen([sys._base_executable, '-c', 'import time;time.sleep(20)'],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: (outside.terminate(), outside.wait(timeout=2)) if outside.poll() is None else None)
        native_resume = WindowsJob._resume_process
        observed = []
        def checked_resume(job, process):
            self.assertFalse(marker.exists(), 'Job 연결 전에 사용자 코드가 실행됐습니다.')
            self.assertEqual(job._active_processes(), 1)
            observed.append(process.pid)
            return native_resume(job, process)
        with patch.object(WindowsJob, '_resume_process', checked_resume):
            with WindowsJob() as job:
                process = job.start([sys._base_executable, '-B', '-X', 'utf8', '-c', source],
                                    cwd=self.local, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate(timeout=3)
                job.finish(timeout=5)
        self.assertEqual(observed, [process.pid])
        self.assertEqual(stdout.strip(), b'latest')
        self.assertEqual(stderr, b'')
        self.assertEqual(marker.read_text(), 'ready')
        self.assertFalse(self.process_alive(process.pid))
        self.assertIsNone(outside.poll(), '스모크 Job 밖의 별도 프로세스를 종료하면 안 됩니다.')

    def test_job_assignment_failure_never_resumes_and_reaps_suspended_root(self):
        self.assertIsNotNone(importlib.util.find_spec('windows_job'), '실행 전 소유 Job 연결 API가 필요합니다.')
        from windows_job import WindowsJob
        marker = self.local / 'must-not-run.txt'
        source = 'from pathlib import Path;Path(' + repr(str(marker)) + ').write_text("unsafe")'
        job = WindowsJob()
        with patch.object(WindowsJob, '_assign_process', side_effect=OSError('제어된 상위 Job 충돌')), \
             patch.object(WindowsJob, '_resume_process') as resume:
            with self.assertRaisesRegex(OSError, '상위 Job 충돌'):
                with job:
                    job.start([sys._base_executable, '-c', source], cwd=self.local,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        resume.assert_not_called()
        self.assertFalse(marker.exists())
        self.assertFalse(self.process_alive(job.process.pid))
        self.assertTrue(job.process.stdout.closed)
        self.assertTrue(job.process.stderr.closed)

    def test_job_handle_closes_after_normal_finish_and_resume_failure(self):
        self.assertIsNotNone(importlib.util.find_spec('windows_job'), '소유 Job 핸들 회수가 필요합니다.')
        from windows_job import WindowsJob
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetHandleInformation.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint))
        for fail_resume in (False, True):
            with self.subTest(fail_resume=fail_resume):
                job = WindowsJob()
                handle = job.handle
                try:
                    with patch.object(WindowsJob, '_resume_process', side_effect=OSError('제어된 재개 실패')) if fail_resume else patch.dict(os.environ, {}):
                        with job:
                            process = job.start([sys._base_executable, '-c', 'pass'], cwd=self.local,
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            process.communicate(timeout=3)
                except OSError as error:
                    if not fail_resume:
                        raise
                    self.assertIn('재개 실패', str(error))
                else:
                    self.assertFalse(fail_resume, '재개 실패를 숨기면 안 됩니다.')
                flags = ctypes.c_uint()
                self.assertFalse(kernel.GetHandleInformation(handle, ctypes.byref(flags)))
                self.assertEqual(ctypes.get_last_error(), 6)
                self.assertFalse(self.process_alive(job.process.pid))


    def test_zero_job_active_count_does_not_hide_unsignaled_process_handle(self):
        from windows_job import WindowsJob
        job = WindowsJob()
        with job:
            process = job.start([sys._base_executable, '-c', 'pass'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate(timeout=3)
            # 실제로 관측한 활성수 0 / 미신호 경계를 결정적으로 재현합니다.
            with patch.object(job.kernel, 'WaitForSingleObject', return_value=258):
                started = time.monotonic()
                with self.assertRaises(OSError):
                    job.finish(timeout=.05)
                self.assertLess(time.monotonic() - started, .5)
                self.assertFalse(job._finished)
        self.assertFalse(self.process_alive(process.pid))

    def test_unobserved_job_lifetime_member_is_not_reported_as_finished(self):
        from windows_job import WindowsJob, _Accounting
        job = WindowsJob()
        with job:
            process = job.start([sys._base_executable, '-c', 'pass'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate(timeout=3)
            original_query = job.kernel.QueryInformationJobObject
            def missing_member(handle, kind, buffer, size, returned):
                result = original_query(handle, kind, buffer, size, returned)
                if result and kind == 1:
                    value = ctypes.cast(buffer, ctypes.POINTER(_Accounting)).contents
                    value.TotalProcesses += 1
                return result
            # 추적 사이 생성·종료된 구성원을 누적 수로 발견하는 경계입니다.
            with patch.object(job.kernel, 'QueryInformationJobObject', side_effect=missing_member):
                with self.assertRaisesRegex(OSError, '추적|누락|구성원'):
                    job.finish(timeout=5)
                self.assertFalse(job._finished)
        self.assertFalse(self.process_alive(process.pid))

    def test_exited_normal_child_is_tracked_before_root_finishes(self):
        from windows_job import WindowsJob
        ready = self.local / 'normal-child.json'
        source = ('import json,pathlib,subprocess,sys;'
                  'child=subprocess.Popen([sys.executable,"-c","import time;time.sleep(.3)"]);'
                  'pathlib.Path(' + repr(str(ready)) + ').write_text(json.dumps(child.pid));'
                  'child.wait();print("completed")')
        job = WindowsJob()
        with job:
            process = job.start([sys._base_executable, '-c', source],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(timeout=3)
            child_pid = json.loads(ready.read_text())
            self.assertFalse(self.process_alive(child_pid))
            job.finish(timeout=5)
        self.assertEqual(stdout.strip(), b'completed')
        self.assertEqual(stderr, b'')
        self.assertFalse(self.process_alive(process.pid))

    def test_cleanup_failure_rolls_back_instead_of_reporting_update_success(self):
        plan = self.plan()
        def unconfirmed(*args):
            raise OSError('추적되지 않은 구성원으로 종료 확인 불가')
        result = update.apply_update_plan(plan, wait_for_parent=lambda pid: None,
                                          smoke=unconfirmed, restart=lambda *args: True)
        self.assertFalse(result['updated'])
        self.assertTrue(result['rolled_back'])
        self.assertTrue(result['rollback_restarted'])
        self.assertEqual(self.exe.read_bytes(), self.old)
        self.assert_personal_data_preserved()



    def test_job_rejects_outside_pid_without_terminating_outside_process(self):
        from windows_job import WindowsJob
        outside = subprocess.Popen([sys._base_executable, '-c', 'import time;time.sleep(20)'],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: (outside.terminate(), outside.wait(timeout=2)) if outside.poll() is None else None)
        job = WindowsJob()
        with patch.object(job, '_member_pids', return_value=[outside.pid]):
            with self.assertRaises(OSError):
                with job:
                    job.start([sys._base_executable, '-c', 'pass'],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertIsNone(outside.poll())
        self.assertFalse(self.process_alive(job.process.pid))
        self.assertIsNone(job.handle)

    def test_tracker_failure_is_reported_and_thread_is_reaped(self):
        from windows_job import WindowsJob
        import threading
        entered = threading.Event()
        job = WindowsJob()
        native_capture = job._capture_members
        calls = []
        def broken_capture():
            calls.append(True)
            if len(calls) == 1:
                return native_capture()
            entered.set()
            raise OSError('제어된 구성원 조회 실패')
        with patch.object(job, '_capture_members', side_effect=broken_capture):
            with self.assertRaisesRegex(OSError, '추적 실패'):
                with job:
                    process = job.start([sys._base_executable, '-c', 'import time;time.sleep(20)'],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.assertTrue(entered.wait(2))
                    job.finish(timeout=5)
        self.assertFalse(job._tracker.is_alive())
        self.assertFalse(self.process_alive(process.pid))
        self.assertIsNone(job.handle)

    def test_tracker_join_timeout_defers_handle_close_without_racing_reader(self):
        from windows_job import WindowsJob
        import threading
        entered, release = threading.Event(), threading.Event()
        job = WindowsJob()
        native_capture = job._capture_members
        calls = []
        def delayed_capture():
            calls.append(True)
            if len(calls) > 1:
                entered.set()
                if not release.wait(3):
                    raise OSError('제어 reader 해제 누락')
            return native_capture()
        try:
            with patch.object(job, '_capture_members', side_effect=delayed_capture):
                with self.assertRaisesRegex(OSError, '추적 스레드'):
                    with job:
                        process = job.start([sys._base_executable, '-c', 'import time;time.sleep(20)'],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        self.assertTrue(entered.wait(2))
                        job.finish(timeout=.05)
                self.assertFalse(job._finished, '기한을 넘긴 정리를 성공으로 처리하면 안 됩니다.')
                self.assertIsNotNone(job.handle, '진행 중인 reader의 Job 핸들을 닫으면 안 됩니다.')
                release.set()
                job._tracker.join(2)
                self.assertFalse(job._tracker.is_alive())
            self.assertIsNone(job.handle)
            # 실패 뒤 fixture가 보유한 정확한 프로세스의 종료를 별도로 회수합니다.
            process.wait(timeout=2)
            self.assertFalse(self.process_alive(process.pid))
            self.assertTrue(process.stdout.closed)
        finally:
            release.set()
            if job._tracker is not None:
                job._tracker.join(3)
            job.close()


if __name__ == '__main__':
    unittest.main()
