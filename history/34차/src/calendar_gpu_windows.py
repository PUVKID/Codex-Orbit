"""GPU 자식 전용 Windows 소유 핸들입니다. 스모크 Job 정책과 분리합니다."""
from __future__ import annotations
import ctypes
from ctypes import wintypes as w
import os
import subprocess
import time


class _Security(ctypes.Structure):
    _fields_ = [('nLength', w.DWORD), ('lpSecurityDescriptor', ctypes.c_void_p), ('bInheritHandle', w.BOOL)]


class _Startup(ctypes.Structure):
    _fields_ = [('cb', w.DWORD), ('lpReserved', w.LPWSTR), ('lpDesktop', w.LPWSTR),
                ('lpTitle', w.LPWSTR)] + [(n, w.DWORD) for n in
                ('dwX', 'dwY', 'dwXSize', 'dwYSize', 'dwXCountChars', 'dwYCountChars', 'dwFillAttribute', 'dwFlags')] + [
                ('wShowWindow', w.WORD), ('cbReserved2', w.WORD), ('lpReserved2', ctypes.c_void_p),
                ('hStdInput', w.HANDLE), ('hStdOutput', w.HANDLE), ('hStdError', w.HANDLE)]


class _ProcessInfo(ctypes.Structure):
    _fields_ = [('hProcess', w.HANDLE), ('hThread', w.HANDLE), ('dwProcessId', w.DWORD), ('dwThreadId', w.DWORD)]


class _BasicLimit(ctypes.Structure):
    _fields_ = [('PerProcessUserTimeLimit', ctypes.c_longlong), ('PerJobUserTimeLimit', ctypes.c_longlong),
                ('LimitFlags', w.DWORD), ('MinimumWorkingSetSize', ctypes.c_size_t),
                ('MaximumWorkingSetSize', ctypes.c_size_t), ('ActiveProcessLimit', w.DWORD),
                ('Affinity', ctypes.c_size_t), ('PriorityClass', w.DWORD), ('SchedulingClass', w.DWORD)]


class _Io(ctypes.Structure):
    _fields_ = [(n, ctypes.c_ulonglong) for n in ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
                'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]


class _Limits(ctypes.Structure):
    _fields_ = [('BasicLimitInformation', _BasicLimit), ('IoInfo', _Io), ('ProcessMemoryLimit', ctypes.c_size_t),
                ('JobMemoryLimit', ctypes.c_size_t), ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]


class _Accounting(ctypes.Structure):
    _fields_ = [(n, ctypes.c_longlong) for n in ('TotalUserTime', 'TotalKernelTime', 'ThisPeriodTotalUserTime',
                'ThisPeriodTotalKernelTime')] + [(n, w.DWORD) for n in ('TotalPageFaultCount', 'TotalProcesses',
                'ActiveProcesses', 'TotalTerminatedProcesses')]


def require(value, message):
    if not value:
        error = ctypes.WinError(ctypes.get_last_error())
        error.add_note(message)
        raise error
    return value


def kernel():
    if os.name != 'nt': raise OSError('GPU 프로세스 격리는 Windows에서만 지원합니다.')
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    signatures = {
        'CloseHandle': ([w.HANDLE], w.BOOL),
        'CreateJobObjectW': ([ctypes.c_void_p, w.LPCWSTR], w.HANDLE),
        'SetInformationJobObject': ([w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD], w.BOOL),
        'QueryInformationJobObject': ([w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.c_void_p], w.BOOL),
        'AssignProcessToJobObject': ([w.HANDLE, w.HANDLE], w.BOOL),
        'TerminateJobObject': ([w.HANDLE, w.UINT], w.BOOL),
        'TerminateProcess': ([w.HANDLE, w.UINT], w.BOOL),
        'ResumeThread': ([w.HANDLE], w.DWORD),
        'CreateProcessW': ([w.LPCWSTR, w.LPWSTR, ctypes.c_void_p, ctypes.c_void_p, w.BOOL, w.DWORD,
                            ctypes.c_void_p, w.LPCWSTR, ctypes.POINTER(_Startup), ctypes.POINTER(_ProcessInfo)], w.BOOL),
        'OpenProcess': ([w.DWORD, w.BOOL, w.DWORD], w.HANDLE),
        'IsProcessInJob': ([w.HANDLE, w.HANDLE, ctypes.POINTER(w.BOOL)], w.BOOL),
        'GetCurrentProcess': ([], w.HANDLE),
        'GetExitCodeProcess': ([w.HANDLE, ctypes.POINTER(w.DWORD)], w.BOOL),
        'WaitForSingleObject': ([w.HANDLE, w.DWORD], w.DWORD),
        'CreateEventW': ([ctypes.c_void_p, w.BOOL, w.BOOL, w.LPCWSTR], w.HANDLE),
        'OpenEventW': ([w.DWORD, w.BOOL, w.LPCWSTR], w.HANDLE),
        'SetEvent': ([w.HANDLE], w.BOOL), 'ResetEvent': ([w.HANDLE], w.BOOL),
        'CreateMutexW': ([ctypes.c_void_p, w.BOOL, w.LPCWSTR], w.HANDLE),
        'OpenMutexW': ([w.DWORD, w.BOOL, w.LPCWSTR], w.HANDLE),
        'ReleaseMutex': ([w.HANDLE], w.BOOL),
        'CreateFileMappingW': ([w.HANDLE, ctypes.c_void_p, w.DWORD, w.DWORD, w.DWORD, w.LPCWSTR], w.HANDLE),
        'OpenFileMappingW': ([w.DWORD, w.BOOL, w.LPCWSTR], w.HANDLE),
        'MapViewOfFile': ([w.HANDLE, w.DWORD, w.DWORD, w.DWORD, ctypes.c_size_t], ctypes.c_void_p),
        'UnmapViewOfFile': ([ctypes.c_void_p], w.BOOL),
        'LocalFree': ([ctypes.c_void_p], ctypes.c_void_p),
    }
    for name, (args, result) in signatures.items():
        f = getattr(k, name); f.argtypes = args; f.restype = result
    return k


class UserSecurity:
    """명명 IPC의 DACL을 현재 프로세스 사용자 SID 한 명으로 제한합니다."""
    def __init__(self, k):
        self.k = k; self.descriptor = ctypes.c_void_p()
        a = ctypes.WinDLL('advapi32', use_last_error=True)
        a.OpenProcessToken.argtypes = [w.HANDLE, w.DWORD, ctypes.POINTER(w.HANDLE)]; a.OpenProcessToken.restype = w.BOOL
        a.GetTokenInformation.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.POINTER(w.DWORD)]
        a.GetTokenInformation.restype = w.BOOL
        a.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        a.ConvertSidToStringSidW.restype = w.BOOL
        a.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [w.LPCWSTR, w.DWORD, ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
        a.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = w.BOOL
        token = w.HANDLE(); sid_text = ctypes.c_void_p()
        require(a.OpenProcessToken(k.GetCurrentProcess(), 8, ctypes.byref(token)), '현재 사용자 토큰 조회 실패')
        try:
            size = w.DWORD()
            a.GetTokenInformation(token, 1, None, 0, ctypes.byref(size))
            if size.value == 0: require(False, '사용자 SID 길이 조회 실패')
            buf = ctypes.create_string_buffer(size.value)
            require(a.GetTokenInformation(token, 1, buf, size, ctypes.byref(size)), '사용자 SID 조회 실패')
            sid = ctypes.c_void_p.from_buffer(buf).value
            require(a.ConvertSidToStringSidW(sid, ctypes.byref(sid_text)), '사용자 SID 표현 실패')
            sddl = 'D:P(A;;GA;;;' + ctypes.wstring_at(sid_text) + ')'
            require(a.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, ctypes.byref(self.descriptor), None), 'IPC 접근 경계 생성 실패')
            self.attributes = _Security(ctypes.sizeof(_Security), self.descriptor, False)
        finally:
            if sid_text: k.LocalFree(sid_text)
            require(k.CloseHandle(token), '사용자 토큰 핸들 회수 실패')

    def close(self):
        if self.descriptor:
            self.k.LocalFree(self.descriptor); self.descriptor = ctypes.c_void_p()


class OwnedGpuProcess:
    """생성 root의 핸들과 Job만 소유하며 전역 프로세스 검색·추적 스레드를 쓰지 않습니다."""
    def __init__(self):
        self.k = kernel(); self.job = None; self.process = None; self.thread = None
        self.pid = None; self.assigned = False; self.forced = False; self.closed = False
        self.last_active = 0; self.exit_code = None; self.argv = None
        self.members = {}; self.total_processes = 0; self.tracking_error = None
        self.job = require(self.k.CreateJobObjectW(None, None), 'GPU 소유 Job 생성 실패')
        try:
            limits = _Limits(); limits.BasicLimitInformation.LimitFlags = 0x2000
            require(self.k.SetInformationJobObject(self.job, 9, ctypes.byref(limits), ctypes.sizeof(limits)), 'GPU Job kill-on-close 설정 실패')
        except BaseException:
            self.k.CloseHandle(self.job); self.job = None; raise

    def start(self, argv, cwd):
        if self.process or self.closed: raise RuntimeError('GPU 소유 프로세스를 다시 생성할 수 없습니다.')
        if not argv or not os.path.isabs(argv[0]): raise ValueError('GPU 실행 파일은 절대 경로여야 합니다.')
        self.argv = list(argv)
        info = _ProcessInfo(); startup = _Startup(); startup.cb = ctypes.sizeof(startup)
        startup.dwFlags = 1; startup.wShowWindow = 0
        # 명명 IPC를 사용하므로 Job·프로세스·임의 파일 핸들 상속은 모두 금지합니다.
        require(self.k.CreateProcessW(argv[0], ctypes.create_unicode_buffer(subprocess.list2cmdline(argv)),
                None, None, False, 0x08000004, None, str(cwd), ctypes.byref(startup), ctypes.byref(info)), 'GPU 자식 생성 실패')
        self.process, self.thread, self.pid = info.hProcess, info.hThread, info.dwProcessId
        require(self.k.AssignProcessToJobObject(self.job, self.process), '정지 GPU 자식 Job 연결 실패')
        self.assigned = True
        self.members[self.pid] = self.process
        self.total_processes = 1
        previous = self.k.ResumeThread(self.thread)
        if previous == 0xFFFFFFFF: require(False, 'GPU 자식 재개 실패')
        if previous != 1: raise OSError('GPU 초기 스레드 정지 횟수가 달라 실행 성공으로 처리하지 않습니다.')
        require(self.k.CloseHandle(self.thread), 'GPU 초기 스레드 핸들 회수 실패'); self.thread = None

    def poll(self):
        if self.closed: return self.exit_code
        if self.process is None: return None
        self._capture_members()
        result = self.k.WaitForSingleObject(self.process, 0)
        if result == 258: return None
        if result != 0: require(False, 'GPU root 종료 조회 실패')
        code = w.DWORD(); require(self.k.GetExitCodeProcess(self.process, ctypes.byref(code)), 'GPU 종료 코드 조회 실패')
        self.exit_code = code.value
        return self.exit_code

    def _capture_members(self):
        if not self.assigned or self.closed:return
        capacity=16
        while capacity<=256:
            buffer=ctypes.create_string_buffer(8+ctypes.sizeof(ctypes.c_size_t)*capacity)
            result=self.k.QueryInformationJobObject(self.job,3,buffer,len(buffer),None)
            assigned,count=(w.DWORD*2).from_buffer(buffer)
            if result and assigned==count and count<=capacity:
                pids=list((ctypes.c_size_t*count).from_buffer(buffer,8));break
            if not result and ctypes.get_last_error()!=234:require(False,'GPU Job 구성원 조회 실패')
            capacity=max(capacity*2,assigned)
        else:raise OSError('GPU 소유 후손 수집 상한 초과')
        for pid in pids:
            if pid in self.members:continue
            handle=self.k.OpenProcess(0x00101000,False,pid)
            if not handle:
                self.tracking_error='GPU 후손 핸들 확보 실패: '+str(ctypes.WinError(ctypes.get_last_error()))
                continue
            try:
                member=w.BOOL()
                require(self.k.IsProcessInJob(handle,self.job,ctypes.byref(member)),'GPU 후손 소유 확인 실패')
                if not member.value:raise OSError('GPU 후손의 소유 Job 불일치')
                self.members[pid]=handle;handle=None
            finally:
                if handle:require(self.k.CloseHandle(handle),'GPU 미확정 후손 핸들 회수 실패')

    def active_processes(self):
        if self.closed: return 0
        if not self.assigned: return int(self.process is not None and self.poll() is None)
        self._capture_members()
        info = _Accounting()
        require(self.k.QueryInformationJobObject(self.job, 1, ctypes.byref(info), ctypes.sizeof(info), None), 'GPU Job 실제 잔존 조회 실패')
        self.last_active = info.ActiveProcesses; self.total_processes = info.TotalProcesses
        return self.last_active

    def terminate(self):
        if self.closed: return
        if self.assigned:
            require(self.k.TerminateJobObject(self.job, 1), '소유 GPU Job 종료 요청 실패')
        elif self.process is not None and self.poll() is None:
            # Job 할당 실패 root는 아직 정지 상태이며 정확한 생성 핸들로만 회수합니다.
            require(self.k.TerminateProcess(self.process, 1), '미할당 GPU root 회수 실패')
        self.forced = True

    def wait_empty(self, deadline):
        if self.closed:return True
        while True:
            active = self.active_processes()
            root_done = self.process is None or self.poll() is not None
            # ActiveProcesses=0과 각 확보 핸들의 실제 signaled를 함께 확인합니다.
            members_done=True
            for handle in self.members.values():
                result=self.k.WaitForSingleObject(handle,0)
                if result not in (0,258):require(False,'GPU 후손 실제 종료 조회 실패')
                if result!=0:members_done=False
            complete_members=(not self.assigned or self.total_processes==len(self.members))
            if active == 0 and root_done and members_done and complete_members and self.tracking_error is None:return True
            remaining = deadline - time.monotonic()
            if remaining <= 0: return False
            time.sleep(min(.005, remaining))

    def release(self):
        if self.closed: return True
        if self.active_processes() or (self.process and self.poll() is None): return False
        if not self.wait_empty(time.monotonic()):return False
        for pid,handle in list(self.members.items()):
            if handle!=self.process:require(self.k.CloseHandle(handle),'GPU 후손 핸들 회수 실패')
            del self.members[pid]
        for name in ('thread', 'process', 'job'):
            handle = getattr(self, name)
            if handle:
                require(self.k.CloseHandle(handle), 'GPU 소유 핸들 회수 실패: ' + name)
                setattr(self, name, None)
        self.closed = True
        return True
