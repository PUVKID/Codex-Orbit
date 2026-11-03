"""스모크에서 직접 만든 프로세스를 실행 전부터 전용 Windows Job에 묶습니다.

공식 근거:
https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
https://learn.microsoft.com/en-us/windows/win32/toolhelp/traversing-the-thread-list
https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-resumethread
https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_accounting_information
https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess
https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_process_id_list
https://learn.microsoft.com/en-us/windows/win32/api/jobapi/nf-jobapi-isprocessinjob
"""
import ctypes
from ctypes import wintypes
import math
import os
import subprocess
import time
import threading


class _BasicLimit(ctypes.Structure):
    _fields_ = [('PerProcessUserTimeLimit', ctypes.c_longlong), ('PerJobUserTimeLimit', ctypes.c_longlong),
                ('LimitFlags', wintypes.DWORD), ('MinimumWorkingSetSize', ctypes.c_size_t),
                ('MaximumWorkingSetSize', ctypes.c_size_t), ('ActiveProcessLimit', wintypes.DWORD),
                ('Affinity', ctypes.c_size_t), ('PriorityClass', wintypes.DWORD), ('SchedulingClass', wintypes.DWORD)]


class _IoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in ('ReadOperationCount', 'WriteOperationCount',
                'OtherOperationCount', 'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]


class _ExtendedLimit(ctypes.Structure):
    _fields_ = [('BasicLimitInformation', _BasicLimit), ('IoInfo', _IoCounters),
                ('ProcessMemoryLimit', ctypes.c_size_t), ('JobMemoryLimit', ctypes.c_size_t),
                ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]


class _Accounting(ctypes.Structure):
    _fields_ = [(name, ctypes.c_longlong) for name in ('TotalUserTime', 'TotalKernelTime',
                'ThisPeriodTotalUserTime', 'ThisPeriodTotalKernelTime')] + [
                (name, wintypes.DWORD) for name in ('TotalPageFaultCount', 'TotalProcesses',
                                                   'ActiveProcesses', 'TotalTerminatedProcesses')]


class _ThreadEntry(ctypes.Structure):
    _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD), ('th32ThreadID', wintypes.DWORD),
                ('th32OwnerProcessID', wintypes.DWORD), ('tpBasePri', wintypes.LONG),
                ('tpDeltaPri', wintypes.LONG), ('dwFlags', wintypes.DWORD)]


def _require(result, description):
    if not result:
        error = ctypes.WinError(ctypes.get_last_error())
        error.add_note(description)
        raise error
    return result


class WindowsJob:
    """이 객체가 만든 root와 자동 상속된 후손만 관리하며 재사용하지 않습니다."""
    def __init__(self):
        if os.name != 'nt':
            raise OSError('소유 프로세스 Job 검사는 Windows에서만 지원합니다.')
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        signatures = {
            'CreateJobObjectW': ((ctypes.c_void_p, wintypes.LPCWSTR), ctypes.c_void_p),
            'SetInformationJobObject': ((ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD), wintypes.BOOL),
            'AssignProcessToJobObject': ((ctypes.c_void_p, ctypes.c_void_p), wintypes.BOOL),
            'TerminateJobObject': ((ctypes.c_void_p, wintypes.UINT), wintypes.BOOL),
            'QueryInformationJobObject': ((ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p,
                                           wintypes.DWORD, ctypes.c_void_p), wintypes.BOOL),
            'OpenProcess': ((wintypes.DWORD, wintypes.BOOL, wintypes.DWORD), ctypes.c_void_p),
            'CreateToolhelp32Snapshot': ((wintypes.DWORD, wintypes.DWORD), ctypes.c_void_p),
            'Thread32First': ((ctypes.c_void_p, ctypes.POINTER(_ThreadEntry)), wintypes.BOOL),
            'Thread32Next': ((ctypes.c_void_p, ctypes.POINTER(_ThreadEntry)), wintypes.BOOL),
            'OpenThread': ((wintypes.DWORD, wintypes.BOOL, wintypes.DWORD), ctypes.c_void_p),
            'GetProcessIdOfThread': ((ctypes.c_void_p,), wintypes.DWORD),
            'ResumeThread': ((ctypes.c_void_p,), wintypes.DWORD),
            'CloseHandle': ((ctypes.c_void_p,), wintypes.BOOL),
            'IsProcessInJob': ((ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(wintypes.BOOL)), wintypes.BOOL),
            'GetProcessTimes': ((ctypes.c_void_p,) + (ctypes.POINTER(wintypes.FILETIME),) * 4, wintypes.BOOL),
            'WaitForSingleObject': ((ctypes.c_void_p, wintypes.DWORD), wintypes.DWORD),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.kernel, name)
            function.argtypes, function.restype = arguments, result
        self.process = None
        self._assigned = False
        self._cleanup_started = False
        self._finished = False
        self._members = {}
        self._tracking_stop = threading.Event()
        self._tracker = None
        self._tracking_error = None
        self._resource_lock = threading.Lock()
        self._tracker_done = False
        self._deferred_close = False
        self.handle = _require(self.kernel.CreateJobObjectW(None, None), '스모크 전용 Job 생성 실패')
        try:
            limits = _ExtendedLimit()
            # breakaway를 허용하지 않고 마지막 Job 핸들이 닫혀도 정확한 소유 후손을 정리합니다.
            limits.BasicLimitInformation.LimitFlags = 0x00002000
            _require(self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)),
                     '스모크 Job 종료 경계 설정 실패')
        except BaseException:
            self.kernel.CloseHandle(self.handle)
            self.handle = None
            raise

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _assign_process(self, process):
        # Popen이 생성해 보유 중인 정확한 PID만 엽니다. 다른 앱을 검색하거나 연결하지 않습니다.
        handle = _require(self.kernel.OpenProcess(0x00100101, False, process.pid), '생성 root 핸들 확인 실패')
        try:
            _require(self.kernel.AssignProcessToJobObject(self.handle, handle), '스모크 root의 Job 연결 실패')
        finally:
            _require(self.kernel.CloseHandle(handle), '생성 root 핸들 회수 실패')

    def _resume_process(self, process):
        snapshot = self.kernel.CreateToolhelp32Snapshot(0x00000004, 0)
        if snapshot == ctypes.c_void_p(-1).value:
            _require(False, '초기 스레드 목록 확인 실패')
        threads = []
        try:
            entry = _ThreadEntry()
            entry.dwSize = ctypes.sizeof(entry)
            _require(self.kernel.Thread32First(snapshot, ctypes.byref(entry)), '초기 스레드 목록이 없습니다.')
            while True:
                if entry.th32OwnerProcessID == process.pid:
                    threads.append(entry.th32ThreadID)
                if not self.kernel.Thread32Next(snapshot, ctypes.byref(entry)):
                    if ctypes.get_last_error() != 18:
                        _require(False, '초기 스레드 목록 순회 실패')
                    break
        finally:
            _require(self.kernel.CloseHandle(snapshot), '스레드 목록 핸들 회수 실패')
        if len(threads) != 1:
            raise OSError('일시 정지한 root의 초기 스레드를 하나로 확인하지 못해 실행하지 않았습니다.')
        thread = _require(self.kernel.OpenThread(0x00000802, False, threads[0]), '생성 초기 스레드 핸들 확인 실패')
        try:
            if self.kernel.GetProcessIdOfThread(thread) != process.pid:
                raise OSError('초기 스레드 소유 PID가 달라 재개하지 않았습니다.')
            previous = self.kernel.ResumeThread(thread)
            if previous == 0xFFFFFFFF:
                _require(False, '생성 초기 스레드 재개 실패')
            if previous != 1:
                raise OSError('생성 초기 스레드의 정지 횟수가 예상과 달라 종료합니다.')
        finally:
            _require(self.kernel.CloseHandle(thread), '생성 초기 스레드 핸들 회수 실패')

    def start(self, argv, **kwargs):
        if self.process is not None or not self.handle or self._cleanup_started:
            raise OSError('소유 Job은 한 번만 실행할 수 있습니다.')
        flags = kwargs.pop('creationflags', 0)
        if flags & 0x01000000:
            raise OSError('상위 Job의 보안 경계를 우회하는 실행은 허용하지 않습니다.')
        # 사용자 코드가 후손을 만들기 전에 반드시 Job 연결을 마칩니다.
        self.process = subprocess.Popen(argv, creationflags=flags | 0x00000004, **kwargs)
        self._assign_process(self.process)
        self._assigned = True
        # root를 실행하기 전에 정확한 핸들을 확보하고 이 Job에만 속한 추적을 시작합니다.
        self._capture_members()
        self._tracker = threading.Thread(target=self._track_members, name='OrbitSmokeJob', daemon=False)
        self._tracker.start()
        self._resume_process(self.process)
        return self.process

    def _accounting(self):
        value = _Accounting()
        _require(self.kernel.QueryInformationJobObject(self.handle, 1, ctypes.byref(value),
                                                      ctypes.sizeof(value), None), '소유 후손 종료 확인 실패')
        return value

    def _active_processes(self):
        return self._accounting().ActiveProcesses

    def _member_pids(self):
        capacity = 16
        while capacity <= 4096:
            # DWORD 두 개 뒤 ULONG_PTR 배열이며 x64에서도 첫 PID 오프셋은 8입니다.
            buffer = ctypes.create_string_buffer(8 + ctypes.sizeof(ctypes.c_size_t) * capacity)
            result = self.kernel.QueryInformationJobObject(self.handle, 3, buffer, len(buffer), None)
            assigned, count = (wintypes.DWORD * 2).from_buffer(buffer)
            if result and assigned == count and count <= capacity:
                return list((ctypes.c_size_t * count).from_buffer(buffer, 8))
            if not result and ctypes.get_last_error() != 234:
                _require(False, '전용 Job 구성원 목록 확인 실패')
            capacity = max(capacity * 2, assigned)
        raise OSError('전용 Job 구성원 추적 상한을 넘어 종료 성공으로 처리하지 않습니다.')

    def _capture_members(self):
        for pid in self._member_pids():
            # 이미 보유한 프로세스 객체의 핸들이 살아 있어 같은 PID의 재사용도 막습니다.
            if any(key[0] == pid for key in self._members):
                continue
            handle = _require(self.kernel.OpenProcess(0x00101000, False, pid),
                              '전용 Job 구성원 핸들을 확보하지 못했습니다.')
            try:
                member = wintypes.BOOL()
                _require(self.kernel.IsProcessInJob(handle, self.handle, ctypes.byref(member)),
                         '전용 Job 구성원 소유 확인 실패')
                if not member.value:
                    raise OSError('구성원 PID의 소유 Job이 달라 변경하지 않고 종료 확인을 중단합니다.')
                created, exited, kernel, user = (wintypes.FILETIME() for _ in range(4))
                _require(self.kernel.GetProcessTimes(handle, ctypes.byref(created), ctypes.byref(exited),
                                                     ctypes.byref(kernel), ctypes.byref(user)),
                         '소유 구성원 생성 시각 확인 실패')
                identity = (pid, (created.dwHighDateTime << 32) | created.dwLowDateTime)
                self._members[identity] = handle
                handle = None
            finally:
                if handle:
                    _require(self.kernel.CloseHandle(handle), '미확정 구성원 핸들 회수 실패')

    def _track_members(self):
        # 전역 daemon이 아니라 단일 스모크 수명 안에서만 동작하는 유한 추적입니다.
        deadline = time.monotonic() + 45
        try:
            while not self._tracking_stop.is_set() and time.monotonic() < deadline:
                self._capture_members()
                self._tracking_stop.wait(.01)
        except BaseException as error:
            self._tracking_error = error
        finally:
            with self._resource_lock:
                self._tracker_done = True
                if self._deferred_close:
                    try:
                        self._release_resources()
                    except BaseException as error:
                        self._tracking_error = error

    @staticmethod
    def _remaining(deadline):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise OSError('소유 프로세스의 실제 종료 확인이 정리 시간 상한을 넘었습니다.')
        return remaining

    def finish(self, timeout=5):
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 0 < timeout <= 5:
            raise ValueError('소유 프로세스 정리 상한은 0초 초과 5초 이하이어야 합니다.')
        if self._finished:
            return
        if self._cleanup_started:
            raise OSError('소유 프로세스 정리가 이미 실패하여 성공으로 처리하지 않습니다.')
        self._cleanup_started = True
        if self.process is None:
            self._finished = True
            return
        deadline = time.monotonic() + timeout
        if self._assigned:
            self._tracking_stop.set()
            if self._tracker is not None:
                self._tracker.join(self._remaining(deadline))
            alive = self._tracker is not None and self._tracker.is_alive()
            if not alive:
                try:
                    self._capture_members()
                except BaseException as error:
                    self._tracking_error = error
            # 수집 실패여도 이 Job에 대해서만 종료를 요청하며 성공을 보고하지 않습니다.
            _require(self.kernel.TerminateJobObject(self.handle, 1), '소유 Job 종료 요청 실패')
            if alive:
                raise OSError('구성원 추적 스레드가 정리 시간 안에 종료되지 않았습니다.')
            for handle in self._members.values():
                while True:
                    milliseconds = max(1, math.floor(self._remaining(deadline) * 1000))
                    result = self.kernel.WaitForSingleObject(handle, milliseconds)
                    if result == 0:
                        break
                    if result == 0xFFFFFFFF:
                        _require(False, '소유 구성원의 실제 종료 대기 실패')
                    if result != 258:
                        raise OSError('소유 구성원 종료 대기 결과를 확인할 수 없습니다.')
        elif self.process.poll() is None:
            # Job 할당에 실패한 root는 아직 정지 상태이므로 이 생성 PID만 종료합니다.
            self.process.kill()
        self.process.communicate(timeout=self._remaining(deadline))
        if self._assigned:
            accounting = self._accounting()
            if self._tracking_error is not None:
                raise OSError('구성원 추적 실패로 전체 종료를 확인할 수 없습니다.') from self._tracking_error
            # 수집 사이 생성·종료나 종료 직전 생성 경쟁도 누적 수가 다르면 성공 금지입니다.
            if accounting.TotalProcesses != len(self._members) or accounting.ActiveProcesses != 0:
                raise OSError('추적한 고유 구성원과 Job 누적 수가 달라 전체 종료를 확인할 수 없습니다.')
        self._remaining(deadline)
        self._finished = True

    def _release_resources(self):
        try:
            for identity, handle in list(self._members.items()):
                _require(self.kernel.CloseHandle(handle), '소유 구성원 핸들 회수 실패')
                del self._members[identity]
        finally:
            try:
                if self.handle:
                    handle, self.handle = self.handle, None
                    _require(self.kernel.CloseHandle(handle), '스모크 Job 핸들 회수 실패')
            finally:
                if self.process is not None:
                    for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
                        if stream is not None and not stream.closed:
                            stream.close()

    def close(self):
        try:
            if not self._cleanup_started:
                self.finish(timeout=5)
        finally:
            self._tracking_stop.set()
            with self._resource_lock:
                if self._tracker is not None and self._tracker.is_alive() and not self._tracker_done:
                    # 기한을 넘긴 시스템 호출과 핸들 닫기의 경쟁을 피하고 추적자가 회수합니다.
                    self._deferred_close = True
                else:
                    self._release_resources()
