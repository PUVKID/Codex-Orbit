"""실제 GPU와 구분한 제어 IPC로 초기화 예산·진행·취소를 검사합니다."""
import os
from pathlib import Path
import sys
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import calendar_gpu_process as ipc


def controlled_child(generation, parent_pid):
    from calendar_gpu_child import serve
    channel = ipc.SharedChannel(generation)
    class Renderer:
        def __init__(self, size, check_cancelled=None):
            # 실제 여섯 초를 기다리며 제품의 초기화 취소 확인 경로를 그대로 호출합니다.
            end = time.monotonic() + 6.0
            while time.monotonic() < end:
                check_cancelled()
                time.sleep(.1)
            check_cancelled()
            self.ctx = type('Context', (), {'info': {'GL_RENDERER': '합성 초기화 IPC'}})()
        def close(self):
            pass
    try:
        return serve(channel, int(parent_pid), Renderer)
    finally:
        channel.close()


class Startup37Tests(unittest.TestCase):
    def proxy(self):
        def command(generation, parent_pid):
            return [ipc.source_child_executable(), '-B', '-X', 'utf8', str(Path(__file__).resolve()),
                    '--startup-child', generation, str(parent_pid)]
        return ipc.ProcessCalendarRenderer(32, command_factory=command)

    def test_six_second_initialize_reports_real_checkpoints_and_reclaims_job(self):
        proxy = self.proxy()
        observed = []
        stop = threading.Event()
        def observe():
            while not stop.wait(.02):
                observed.append(proxy.progress_status())
        thread = threading.Thread(target=observe)
        thread.start()
        started = time.monotonic()
        try:
            proxy._start()
            self.assertGreaterEqual(time.monotonic() - started, 6.0)
            self.assertEqual(proxy.stage, '준비')
            self.assertFalse(proxy.progress_status()['initializing'])
            self.assertTrue(any(row['initializing'] and row['stage'].startswith('초기화 체크 ') for row in observed))
            self.assertEqual(proxy.ctx.info['GL_RENDERER'], '합성 초기화 IPC')
        finally:
            stop.set()
            thread.join(1)
            self.assertTrue(proxy.close())
        self.assertEqual(proxy.owner.active_processes(), 0)
        self.assertTrue(proxy.channel.closed)

    def test_initialization_cancellation_does_not_wait_for_startup_budget(self):
        proxy = self.proxy()
        observed = threading.Event()
        stopping = threading.Event()
        def cancel_when_started():
            while not stopping.wait(.01):
                if proxy.progress_status()['stage'].startswith('초기화 체크 '):
                    proxy.request_stop()
                    observed.set()
                    return
        thread = threading.Thread(target=cancel_when_started)
        thread.start()
        try:
            with self.assertRaises(ipc.GpuCancelled):
                proxy._start()
            self.assertTrue(observed.wait(1))
            started = time.monotonic()
            self.assertTrue(proxy.close())
            self.assertLess(time.monotonic() - started, 2.0)
        finally:
            stopping.set()
            thread.join(1)
            if not proxy.closed:
                proxy.close()
        self.assertEqual(proxy.owner.active_processes(), 0)
        self.assertTrue(proxy.channel.closed)

    def test_absolute_initialize_and_frame_deadlines_do_not_extend_on_busy(self):
        for kind, budget, busy in (('initialize', 120.0, False), ('initialize', 120.0, True),
                                   ('calendar', 5.0, True)):
            with self.subTest(kind=kind, busy=busy):
                clock = [0.0]
                proxy = ipc.ProcessCalendarRenderer(32)
                class Channel:
                    def send_request(self, request_id, payload, deadline, cancel):
                        self.deadline = deadline
                    def event(self, name, milliseconds=0):
                        if milliseconds:
                            clock[0] += .5
                        return busy
                    def read_response(self, *args):
                        clock[0] += .5
                        return {'status': 'busy', 'stage': '합성 진행'}, b'', 0, 0
                proxy.channel = Channel()
                proxy.owner = type('Owner', (), {'poll': lambda self: None})()
                with patch.object(ipc.time, 'monotonic', side_effect=lambda: clock[0]):
                    with self.assertRaisesRegex(RuntimeError, '응답 제한'):
                        proxy._exchange({'kind': kind})
                self.assertEqual(proxy.channel.deadline, budget)
                self.assertEqual(clock[0], budget)

    def test_warmup_is_preparing_without_false_error(self):
        from types import SimpleNamespace
        import calendar_motion as motion
        class Condition:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def notify_all(self):
                pass
            def wait(self, remaining):
                self.waited = remaining
                clock[0] = remaining
        clock = [0.0]
        condition = Condition()
        worker = SimpleNamespace(condition=condition, requested_date=None, visible=False,
            latest_date=None, latest=None, error='', stopping=False, renderer_name='', render_count=0)
        service = SimpleNamespace(worker=worker, owners={})
        with patch.object(motion, '_get_service', return_value=service), patch.object(motion.time, 'monotonic', side_effect=lambda: clock[0]), patch.object(motion._logger, 'error') as log:
            result = motion.prepare_calendar_motion()
        self.assertEqual(condition.waited, 5.0)
        self.assertEqual(result['state'], 'preparing')
        self.assertEqual(result['error'], '')
        self.assertFalse(result['ready'])
        log.assert_not_called()

    def test_live_initialization_status_uses_only_memory_snapshot(self):
        from PySide6.QtWidgets import QApplication
        import calendar_motion as motion
        app = QApplication.instance() or QApplication([])
        service = motion.CalendarMotion(renderer_factory=lambda *args, **kwargs: None)
        proxy = ipc.ProcessCalendarRenderer(32)
        proxy.initializing = True
        proxy.started_at = time.monotonic()
        proxy.stage = '초기화 체크 4'
        service.worker.renderer = proxy
        try:
            with patch.object(motion, '_service', service), patch.object(proxy, 'status', side_effect=AssertionError('UI에서 OS 상태 조회')):
                status = motion.calendar_motion_status()
            self.assertEqual(status['state'], 'preparing')
            self.assertTrue(status['gpu_process']['initializing'])
            self.assertEqual(status['gpu_process']['stage'], '초기화 체크 4')
            self.assertEqual(status['error'], '')
        finally:
            self.assertTrue(service.close())

    def test_fallback_markers_distinguish_preparing_error_and_language(self):
        from datetime import date
        from PySide6.QtWidgets import QApplication
        from i18n import get_language, set_language
        import calendar_motion as motion
        app = QApplication.instance() or QApplication([])
        class Renderer:
            pass
        service = motion.CalendarMotion(renderer_factory=Renderer)
        previous = get_language()
        try:
            for language, error, expected in (('ko', '', '3D 준비 중'), ('en', '', 'Preparing 3D'),
                                               ('ko', '합성 오류', '3D 표시 오류'), ('en', 'synthetic error', '3D unavailable')):
                set_language(language)
                service.worker.error = error
                image = service.frame(value=date(2026, 11, 20))
                self.assertEqual(image.text('calendar_fallback_label'), expected)
                self.assertEqual(image.text('calendar_fallback_state'), 'error' if error else 'preparing')
                self.assertFalse(image.isNull())
        finally:
            set_language(previous)
            self.assertTrue(service.close())


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--startup-child':
        raise SystemExit(controlled_child(*sys.argv[2:]))
    unittest.main()
