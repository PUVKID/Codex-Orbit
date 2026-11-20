"""렌더러 생성 경계의 정상 취소·실패 보존·소유 스레드 자원 해제를 검사합니다."""
from contextlib import ExitStack
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import calendar_motion as motion
import calendar_renderer as renderer
from PySide6.QtGui import QImage


class ControlledCancellation(Exception):
    pass


class AllocationProbe:
    """실제 생성자에 유한한 자원 대역을 연결하며 중단 위치를 기록합니다."""
    def __init__(self, stop_at=None, failure=None, entered=None, release=None, invalid_image=False):
        self.stop_at = stop_at
        self.failure = failure
        self.entered = entered
        self.release = release
        self.invalid_image = invalid_image
        self.calls = []
        self.resources = []
        self.cancelled = False
        self.context = None

    def visit(self, stage):
        self.calls.append(stage)
        if stage == self.stop_at:
            self.cancelled = True
            if self.entered is not None:
                self.entered.set()
                if not self.release.wait(1):
                    raise RuntimeError('검사 생성 단계 해제 신호가 도착하지 않았습니다.')
            if self.failure is not None:
                raise self.failure

    def check_cancelled(self):
        if self.cancelled:
            raise ControlledCancellation('제어된 생성 중단')

    def patches(self):
        probe = self

        class Resource:
            def __init__(self, name):
                self.name = name
                self.created_thread = threading.get_ident()
                self.release_threads = []
                probe.resources.append(self)

            def release(self):
                self.release_threads.append(threading.get_ident())

            def build_mipmaps(self):
                probe.visit('mipmap')

            def __getitem__(self, name):
                return self

            def write(self, value):
                probe.visit('uniform')

        class Context(Resource):
            info = {}

            def program(self, **kwargs):
                probe.visit('shader')
                return Resource('program')

            def texture(self, *args, **kwargs):
                probe.visit('texture')
                return Resource('texture')

            def renderbuffer(self, *args, **kwargs):
                probe.visit('renderbuffer')
                return Resource('color')

            def depth_renderbuffer(self, *args, **kwargs):
                probe.visit('depth')
                return Resource('depth')

            def framebuffer(self, *args, **kwargs):
                probe.visit('framebuffer')
                return Resource('framebuffer')

            def vertex_array(self, *args, **kwargs):
                probe.visit('vao')
                return Resource('vao')

            def enable(self, value):
                probe.visit('enable')

        class Image:
            Format = QImage.Format

            def __init__(self, *args):
                probe.visit('image_read')
                self.stage = 'image_read'

            def convertToFormat(self, value):
                probe.visit('image_convert')
                self.stage = 'image_convert'
                return self

            def width(self):
                return 2

            def height(self):
                return 2

            def constBits(self):
                return bytes(16)

            def isNull(self):
                return probe.invalid_image and self.stage == probe.stop_at

        def create_context(**kwargs):
            probe.context = Context('context')
            probe.visit('context')
            return probe.context

        def load_catalog(*args):
            probe.visit('catalog')
            return {}

        stack = ExitStack()
        stack.enter_context(patch.object(renderer.moderngl, 'create_standalone_context', create_context))
        stack.enter_context(patch.object(renderer, 'organic_shaders', lambda *args: args))
        stack.enter_context(patch.object(renderer, 'QImage', Image))
        stack.enter_context(patch('material_catalog32.load_catalog', load_catalog))
        return stack


class RendererLifetimeTests(unittest.TestCase):
    def assert_released_once_by_owner(self, probe):
        self.assertTrue(probe.resources)
        for resource in probe.resources:
            self.assertEqual(resource.release_threads, [resource.created_thread], resource.name)

    def test_cancel_between_finite_initialization_stages_releases_partial_resources(self):
        stages = ('context', 'shader', 'catalog', 'image_read', 'image_convert',
                  'texture', 'mipmap', 'renderbuffer', 'depth', 'framebuffer', 'vao', 'enable', 'uniform')
        for stage in stages:
            with self.subTest(stage=stage):
                probe = AllocationProbe(stop_at=stage)
                with probe.patches():
                    with self.assertRaises(ControlledCancellation):
                        renderer.CalendarRenderer(64, check_cancelled=probe.check_cancelled)
                self.assertEqual(probe.calls[-1], stage, '취소된 뒤 다음 생성 단계가 실행되면 안 됩니다.')
                self.assert_released_once_by_owner(probe)

    def test_default_synchronous_constructor_retains_existing_allocation_and_close(self):
        probe = AllocationProbe()
        with probe.patches():
            value = renderer.CalendarRenderer(64)
            self.assertEqual(value.output_size, 64)
            value.close()
        self.assertIn('uniform', probe.calls)
        self.assert_released_once_by_owner(probe)

    def test_worker_actual_stop_cancels_creation_without_error_or_first_frame(self):
        entered, release = threading.Event(), threading.Event()
        probe = AllocationProbe(stop_at='shader', entered=entered, release=release)
        worker = motion._Worker(renderer_factory=renderer.CalendarRenderer)
        worker.configure(visible=True)
        with probe.patches():
            worker.start()
            try:
                self.assertTrue(entered.wait(1))
                worker.stop()
                release.set()
                self.assertTrue(worker.wait(2000), '기존 종료 2초 상한을 유지합니다.')
            finally:
                worker.stop()
                release.set()
                worker.wait(2000)
        self.assertEqual(worker.error, '')
        self.assertEqual(worker.render_count, 0)
        self.assertIsNone(worker.latest)
        self.assertEqual(probe.calls, ['context', 'shader'])
        self.assert_released_once_by_owner(probe)

    def test_real_creation_error_is_not_swallowed_when_stop_was_requested(self):
        entered, release = threading.Event(), threading.Event()
        probe = AllocationProbe(stop_at='shader', failure=RuntimeError('제어된 셰이더 실패'),
                                entered=entered, release=release)
        worker = motion._Worker(renderer_factory=renderer.CalendarRenderer)
        worker.configure(visible=True)
        with probe.patches(), self.assertLogs('calendar_motion', level='ERROR'):
            worker.start()
            try:
                self.assertTrue(entered.wait(1))
                worker.stop()
                release.set()
                self.assertTrue(worker.wait(2000))
            finally:
                worker.stop()
                release.set()
                worker.wait(2000)
        self.assertIn('RuntimeError: 제어된 셰이더 실패', worker.error)
        self.assertEqual(worker.render_count, 0)
        self.assert_released_once_by_owner(probe)

    def test_null_image_failure_is_preserved_when_stop_arrives_during_decode_or_conversion(self):
        for stage in ('image_read', 'image_convert'):
            with self.subTest(stage=stage):
                entered, release = threading.Event(), threading.Event()
                probe = AllocationProbe(stop_at=stage, entered=entered, release=release, invalid_image=True)
                worker = motion._Worker(renderer_factory=renderer.CalendarRenderer)
                worker.configure(visible=True)
                with probe.patches():
                    worker.start()
                    try:
                        self.assertTrue(entered.wait(1))
                        worker.stop()
                        release.set()
                        self.assertTrue(worker.wait(2000))
                    finally:
                        worker.stop()
                        release.set()
                        worker.wait(2000)
                self.assertIn('코코넛 표면 재질을 읽을 수 없습니다.', worker.error)
                self.assertEqual(worker.render_count, 0)
                self.assert_released_once_by_owner(probe)


if __name__ == '__main__':
    unittest.main()
