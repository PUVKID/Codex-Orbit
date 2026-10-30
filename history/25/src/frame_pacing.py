"""프로세스 전용 고해상도 대기로 전역 타이머 설정 없이 프레임을 조율합니다."""
import ctypes
import os


class FrameWaiter:
    def __init__(self):
        self.handle = None
        self.kernel = None
        self.warning = ''
        self.backend = '조건 변수 대기'
        if os.name != 'nt':
            return
        from ctypes import wintypes
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateWaitableTimerExW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
        self.kernel.CreateWaitableTimerExW.restype = wintypes.HANDLE
        self.kernel.SetWaitableTimer.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_longlong), wintypes.LONG,
                                               ctypes.c_void_p, ctypes.c_void_p, wintypes.BOOL]
        self.kernel.SetWaitableTimer.restype = wintypes.BOOL
        self.kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.kernel.WaitForSingleObject.restype = wintypes.DWORD
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel.CloseHandle.restype = wintypes.BOOL
        # 익명·상속 불가 핸들 하나만 소유하며 전역 timeBeginPeriod는 호출하지 않습니다.
        self.handle = self.kernel.CreateWaitableTimerExW(None, None, 2, 0x1F0003)
        if self.handle:
            self.backend = 'Windows 고해상도 대기 타이머'
        else:
            self.warning = 'Windows 정밀 타이머 미지원: ' + str(ctypes.WinError(ctypes.get_last_error()))
            self.backend = '조건 변수 대기 · 정밀 타이머 미지원'

    def wait(self, seconds, condition):
        if seconds <= 0:
            return
        if self.handle is None:
            with condition:
                condition.wait(seconds)
            return
        due = ctypes.c_longlong(-max(1, round(seconds * 10_000_000)))
        if not self.kernel.SetWaitableTimer(self.handle, ctypes.byref(due), 0, None, None, False):
            raise ctypes.WinError(ctypes.get_last_error())
        status = self.kernel.WaitForSingleObject(self.handle, 1000)
        if status != 0:
            if status == 0xFFFFFFFF:
                raise ctypes.WinError(ctypes.get_last_error())
            raise OSError(f'Windows 정밀 타이머 대기 실패: 반환값 {status}')

    def close(self):
        if self.handle is None:
            return
        handle, self.handle = self.handle, None
        if not self.kernel.CloseHandle(handle):
            raise ctypes.WinError(ctypes.get_last_error())
