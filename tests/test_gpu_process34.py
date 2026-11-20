"""실제품 IPC와 소유 GPU 자식의 중단·회수 경계를 검사합니다."""
from pathlib import Path
import sys
import threading
import unittest
from datetime import date
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtGui import QImage
import calendar_motion as motion


class LauncherSelectionTests(unittest.TestCase):
    def test_source_child_selects_existing_pythonw_in_same_environment(self):
        import tempfile
        from unittest.mock import patch
        import calendar_gpu_process as ipc
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'가상 환경';folder.mkdir()
            executable=folder/'python.exe';executable.write_bytes(b'fixture')
            companion=folder/'pythonw.exe';companion.write_bytes(b'fixture')
            with patch.object(ipc.sys,'executable',str(executable)),patch.object(ipc.sys,'frozen',False,create=True):
                argv=ipc.child_argv('a'*32,123)
                self.assertEqual(argv,[str(companion.resolve()),'-B','-X','utf8',str(Path(ipc.__file__).with_name('orbit_entry.py').resolve()),'--orbit-gpu-child','1','a'*32,'123'])
                controlled=IpcProcessTests.command('normal')('a'*32,123)
                self.assertEqual(controlled[0],str(companion.resolve()))

    def test_missing_pythonw_is_explicit_error_without_console_fallback(self):
        import tempfile
        from unittest.mock import patch
        import calendar_gpu_process as ipc
        with tempfile.TemporaryDirectory() as directory:
            executable=Path(directory)/'python.exe';executable.write_bytes(b'fixture')
            with patch.object(ipc.sys,'executable',str(executable)),patch.object(ipc.sys,'frozen',False,create=True):
                with self.assertRaisesRegex(FileNotFoundError,'pythonw.exe'):ipc.child_argv('b'*32,456)

    def test_frozen_child_keeps_same_windowed_executable_and_arguments(self):
        import tempfile
        from unittest.mock import patch
        import calendar_gpu_process as ipc
        with tempfile.TemporaryDirectory() as directory:
            executable=Path(directory)/'CodexOrbit.exe';executable.write_bytes(b'fixture')
            with patch.object(ipc.sys,'executable',str(executable)),patch.object(ipc.sys,'frozen',True,create=True):
                self.assertEqual(ipc.child_argv('c'*32,789),[str(executable.resolve()),'--orbit-gpu-child','1','c'*32,'789'])


class ProcessBoundaryTests(unittest.TestCase):
    def test_explicit_renderer_factory_keeps_worker_thread_and_elapsed(self):
        # factory가 무시되면 생성 소유권·경과시간·정확 한 프레임 계약이 깨집니다.
        calls = []
        worker = None
        class Renderer:
            def __init__(self, size, check_cancelled=None):
                calls.append(('create', threading.get_ident(), size))
                self.ctx = type('Context', (), {'info': {}})()
            def render(self, value, elapsed, country='KR'):
                calls.append(('render', threading.get_ident(), value, country))
                worker.stop()
                image = QImage(32, 32, QImage.Format.Format_RGBA8888)
                image.fill(0)
                return image
            def close(self): calls.append(('close', threading.get_ident()))
        worker = motion._Worker(renderer_factory=Renderer)
        worker.configure(visible=True, value=date(2028, 2, 29), elapsed=0)
        worker.start()
        self.assertTrue(worker.wait(2000))
        self.assertEqual(worker.error, '')
        self.assertEqual(worker.render_count, 1)
        self.assertEqual([r[0] for r in calls], ['create', 'render', 'close'])
        self.assertEqual(len({r[1] for r in calls}), 1)
        self.assertNotEqual(calls[0][1], threading.get_ident())
        self.assertEqual(calls[1][2:], (date(2028, 2, 29), 'KR'))



class IpcProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    @staticmethod
    def command(mode):
        def argv(generation, parent_pid):
            from calendar_gpu_process import source_child_executable
            return [source_child_executable(), '-B', '-X', 'utf8', str(Path(__file__).resolve()),
                    '--controlled-child', mode, generation, str(parent_pid)]
        return argv

    def renderer(self, mode='normal'):
        from calendar_gpu_process import ProcessCalendarRenderer
        return ProcessCalendarRenderer((3840,2160), command_factory=self.command(mode))

    def test_real_ipc_frame_alpha_stride_and_independent_copy(self):
        renderer=self.renderer()
        try:
            renderer.set_output_size(32)
            image=renderer.render(date(2028,2,29),0,country='KR')
            self.assertEqual(image.size().toTuple(),(32,32))
            self.assertEqual(image.bytesPerLine(),128)
            self.assertEqual(image.pixelColor(5,5).getRgb(),(30,60,90,127))
            renderer.render(date(2028,2,29),1,country='KR')
            self.assertEqual(image.pixelColor(5,5).getRgb(),(30,60,90,127))
            from city_festivals import get_city_catalog_revision
            self.assertEqual(renderer.catalog_context,get_city_catalog_revision())
            self.assertEqual(renderer.ctx.info['GL_RENDERER'],'제어 IPC')
        finally:
            self.assertTrue(renderer.close())
        self.assertEqual(renderer.owner.active_processes(),0)
        self.assertTrue(renderer.channel.closed)
        self.assertFalse(renderer.owner.forced)

    def test_actual_child_catalog_path_and_revision_update_without_restart(self):
        import tempfile
        import city_festivals as catalog
        from test_city_festivals33 import write_bundle,CITY,SERIES,EVENT
        previous=catalog._cache_directory
        renderer=self.renderer('catalog')
        try:
            with tempfile.TemporaryDirectory() as directory:
                root=Path(directory);catalog.configure_city_cache(root)
                renderer.set_output_size(32)
                revisions=[];pid=None
                for generation,kind,color in (('a'*64,'film',2),('b'*64,'music',1)):
                    bundle=root/'city-festivals'/'generations'/generation
                    bundle.mkdir(parents=True)
                    write_bundle(bundle,series=[dict(SERIES,kind=kind)],events=[dict(EVENT,kind=kind)])
                    revision=catalog.activate_country_cache('FR',bundle);revisions.append(revision)
                    image=renderer.render(date(2027,5,11),country='FR',city_ref=CITY)
                    self.assertEqual(image.pixelColor(0,0).red(),color)
                    self.assertEqual(renderer.catalog_context,revision)
                    if pid is None:pid=renderer.owner.pid
                    self.assertEqual(renderer.owner.pid,pid)
                self.assertNotEqual(revisions[0],revisions[1])
                self.assertTrue(renderer.close())
        finally:
            renderer.close()
            catalog.configure_city_cache(previous.parent if previous is not None else None)

    def test_suspended_spawn_assignment_failure_reclaims_exact_root_and_handles(self):
        from unittest.mock import patch
        import calendar_gpu_process as ipc
        from calendar_gpu_windows import OwnedGpuProcess
        owner=OwnedGpuProcess();renderer=self.renderer()
        try:
            with patch.object(ipc,'OwnedGpuProcess',return_value=owner),\
                 patch.object(owner.k,'AssignProcessToJobObject',return_value=0):
                with self.assertRaises(OSError):renderer.render(date(2026,11,13))
            self.assertIsNotNone(owner.pid)
            self.assertFalse(owner.assigned)
            self.assertTrue(renderer.close())
            self.assertEqual(owner.active_processes(),0)
            self.assertTrue(owner.closed);self.assertTrue(renderer.channel.closed)
        finally:renderer.close()

    def test_native_hang_create_render_close_is_reaped_within_original_two_seconds(self):
        import functools,time
        for stage in ('create','render','close'):
            with self.subTest(stage=stage):
                service=motion.CalendarMotion(renderer_factory=functools.partial(
                    __import__('calendar_gpu_process').ProcessCalendarRenderer,
                    command_factory=self.command(stage)))
                worker=service.worker
                worker.configure(visible=True,value=date(2028,2,29),elapsed=0)
                deadline=time.monotonic()+5
                expected={'create':'가져오기·생성','render':'렌더','close':'프레임'}[stage]
                try:
                    while time.monotonic()<deadline:
                        proxy=worker.renderer
                        if proxy is not None and proxy.stage==expected:break
                        time.sleep(.005)
                    self.assertIsNotNone(worker.renderer)
                    self.assertEqual(worker.renderer.stage,expected)
                    started=time.monotonic()
                    self.assertTrue(service.close(2000))
                    elapsed=time.monotonic()-started
                    self.assertLessEqual(elapsed,2.0)
                    self.assertFalse(worker.isRunning())
                    self.assertEqual(worker.renderer.owner.active_processes(),0)
                    self.assertTrue(worker.renderer.owner.forced)
                    self.assertTrue(worker.renderer.closed)
                    print('NATIVE_HANG',stage,'종료초',elapsed,'실제잔존',0,flush=True)
                finally:
                    service.close(2000)

    def test_actual_ipc_committed_error_precedes_later_stop(self):
        import time
        from calendar_gpu_process import decode_control,RESPONSE_OFFSET
        renderer=self.renderer('error')
        try:
            renderer.set_output_size(32);renderer._start()
            channel=renderer.channel;original_send=channel.send_request
            def send_then_stop(request_id,payload,deadline,cancel):
                original_send(request_id,payload,deadline,cancel)
                limit=time.monotonic()+1
                while time.monotonic()<limit:
                    if channel.event('response'):
                        with channel.locked(limit):
                            req,resp,_,length,*_=channel._header()
                            meta=decode_control(channel._read(RESPONSE_OFFSET,length)) if length else {}
                        if req==request_id and resp==request_id and meta.get('status')=='error':
                            renderer.request_stop(time.monotonic()+2)
                            return
                    time.sleep(.001)
                raise AssertionError('실제 자식 오류 슬롯이 먼저 확정되지 않았습니다.')
            channel.send_request=send_then_stop
            with self.assertRaisesRegex(RuntimeError,'제어된 자식 렌더 오류'):
                renderer.render(date(2026,11,13))
            self.assertIn('제어된 자식 렌더 오류',renderer.last_error)
            self.assertEqual(renderer.request_id,2)
        finally:self.assertTrue(renderer.close())

    def test_child_crash_reports_real_code_and_stage_without_restart(self):
        renderer=self.renderer('crash')
        try:
            renderer.set_output_size(32)
            with self.assertRaisesRegex(RuntimeError,'code=77.*렌더'):
                renderer.render(date(2026,11,13))
            pid=renderer.owner.pid
            with self.assertRaisesRegex(RuntimeError,'code=77'):
                renderer.render(date(2026,11,13))
            self.assertEqual(renderer.owner.pid,pid)
        finally:self.assertTrue(renderer.close())

    def test_child_exception_and_null_image_are_explicit(self):
        for mode,message in (('error','제어된 자식 렌더 오류'),('null','빈 영상')):
            with self.subTest(mode=mode):
                renderer=self.renderer(mode)
                try:
                    renderer.set_output_size(32)
                    with self.assertRaisesRegex(RuntimeError,message):renderer.render(date(2026,11,13))
                finally:self.assertTrue(renderer.close())


class ProtocolTests(unittest.TestCase):
    def test_pure_slot_committed_error_precedes_stop_without_new_request(self):
        from calendar_gpu_process import ProcessCalendarRenderer
        proxy=ProcessCalendarRenderer(32)
        error_text='종료 전에 이미 확정된 실제 오류'
        class ErrorSlot:
            closed=False;committed=False
            def send_request(self,request_id,payload,deadline,cancel):
                self.request_id=request_id;self.committed=True
                proxy.request_stop()
            def signal(self,name):pass
            def event(self,name,milliseconds=0):return name=='response' and self.committed
            def read_response(self,*args):return {'status':'error','stage':'렌더','error':error_text},b'',0,0
            def read_terminal_error(self,request_id,deadline):
                return {'status':'error','stage':'렌더','error':error_text} if self.committed and request_id==self.request_id else None
        proxy.channel=ErrorSlot()
        with self.assertRaisesRegex(RuntimeError,error_text):proxy._exchange({'kind':'initialize'})
        self.assertEqual(proxy.last_error,error_text)
        self.assertEqual(proxy.request_id,1)

    def test_shared_slot_committed_error_precedes_stop_and_discards_ready_frame(self):
        import time
        from calendar_gpu_process import ProcessCalendarRenderer,SharedChannel,GpuCancelled
        for status in ('error','frame'):
            with self.subTest(status=status):
                proxy=ProcessCalendarRenderer(32);channel=SharedChannel(proxy.generation,create=True);proxy.channel=channel
                try:
                    proxy.request_id=1
                    channel.send_request(1,{'kind':'calendar'},time.monotonic()+1,lambda:False)
                    if status=='error':channel.respond(1,{'status':'error','stage':'렌더','error':'공유 슬롯 원문 오류'})
                    else:channel.respond(1,{'status':'frame','format':'RGBA8888'},bytes(32*32*4),32,32)
                    proxy.request_stop(time.monotonic()+2)
                    expected=RuntimeError if status=='error' else GpuCancelled
                    with self.assertRaises(expected):proxy._exchange({'kind':'calendar'})
                    self.assertEqual(proxy.request_id,1,'종료 뒤 새 요청은 보내지 않습니다.')
                    if status=='error':self.assertEqual(proxy.last_error,'공유 슬롯 원문 오류')
                    else:self.assertEqual(proxy.last_error,'')
                finally:self.assertTrue(proxy.close())

    def test_malformed_internal_entry_never_imports_gui_or_falls_back_to_app(self):
        import subprocess
        code="import sys;from orbit_entry import main;assert main(['--orbit-gpu-child','1','bad','1'])==64;assert 'app' not in sys.modules;assert 'PySide6.QtWidgets' not in sys.modules"
        result=subprocess.run([sys.executable,'-B','-X','utf8','-c',code],
            cwd=Path(__file__).resolve().parents[1]/'src',capture_output=True,timeout=3)
        self.assertEqual(result.returncode,0,result.stderr.decode('utf-8'))

    def test_stop_and_final_channel_reclaim_are_serialized(self):
        import traceback
        from calendar_gpu_process import ProcessCalendarRenderer,SharedChannel
        proxy=ProcessCalendarRenderer(32);channel=SharedChannel(proxy.generation,create=True);proxy.channel=channel
        entered=threading.Event();release=threading.Event();closing=threading.Event();closed=threading.Event()
        original=channel.signal;errors=[];calls=[];counter_lock=threading.Lock()
        def delayed(name):
            with counter_lock:
                calls.append(name);first=len(calls)==1
            if first:
                entered.set()
                if not release.wait(1):raise RuntimeError('제어 신호 스케줄 실패')
            original(name)
        channel.signal=delayed
        def stop():
            try:proxy.request_stop()
            except Exception:errors.append(traceback.format_exc())
        def close():
            closing.set()
            try:
                if not proxy.close():raise RuntimeError('최종 채널 회수 실패')
            except Exception:errors.append(traceback.format_exc())
            finally:closed.set()
        a=threading.Thread(target=stop);a.start()
        self.assertTrue(entered.wait(1))
        b=threading.Thread(target=close);b.start()
        try:
            self.assertTrue(closing.wait(1));closed.wait(.05)
        finally:
            release.set();a.join(1);b.join(1)
        self.assertFalse(a.is_alive());self.assertFalse(b.is_alive())
        self.assertEqual(errors,[]);self.assertTrue(channel.closed)

    def test_continuous_busy_responses_obey_original_five_second_deadline(self):
        from unittest.mock import patch
        import calendar_gpu_process as ipc
        proxy=ipc.ProcessCalendarRenderer(32)
        class BusyChannel:
            calls=0
            def send_request(self,*args):pass
            def event(self,*args):return True
            def read_response(self,*args):
                self.calls+=1
                if self.calls>20:raise AssertionError('시간 제한을 건너뛰며 busy를 계속 소비했습니다.')
                return {'status':'busy','stage':'제어 busy'},b'',0,0
        proxy.channel=BusyChannel()
        # 시계를 제어해 5초 기준 자체는 유지하고 busy 분기의 시간 검사만 분리합니다.
        with patch.object(ipc.time,'monotonic',side_effect=range(100)):
            with self.assertRaisesRegex(RuntimeError,'응답 제한'):
                proxy._exchange({'kind':'initialize'})

    def test_initialize_requires_ready_and_render_requires_frame(self):
        import calendar_gpu_process as ipc
        for kind,status in (('initialize','frame'),('calendar','ready'),('observatory','ready')):
            with self.subTest(kind=kind,status=status):
                proxy=ipc.ProcessCalendarRenderer(32)
                class Channel:
                    def send_request(self,*args):pass
                    def event(self,*args):return True
                    def read_response(self,*args):
                        return {'status':status,'identity':None,'catalog_revision':None,'parent_pid':__import__('os').getpid(),'child_pid':1},b'',0,0
                proxy.channel=Channel()
                with self.assertRaisesRegex(ipc.GpuProtocolError,'요청 종류'):
                    proxy._exchange({'kind':kind})

    def test_bounded_payload_and_wrong_generation_id_size_rejected(self):
        import time,uuid
        from calendar_gpu_process import SharedChannel, GpuProtocolError, encode_control, REQUEST_LIMIT
        with self.assertRaises(GpuProtocolError):encode_control({'x':'가'*REQUEST_LIMIT},REQUEST_LIMIT)
        channel=SharedChannel(uuid.uuid4().hex,create=True)
        try:
            channel.send_request(1,{'kind':'x'},time.monotonic()+1,lambda:False)
            channel.respond(1,{'status':'frame','format':'RGBA8888'},b'x',32,32)
            with self.assertRaisesRegex(GpuProtocolError,'크기'):channel.read_response(1,time.monotonic()+1,lambda:False)
            channel.respond(1,{'status':'ready'})
            with self.assertRaisesRegex(GpuProtocolError,'일련번호'):channel.read_response(2,time.monotonic()+1,lambda:False)
            channel._write(0,b'WRONGHDR')
            with self.assertRaisesRegex(GpuProtocolError,'세대'):channel.read_response(1,time.monotonic()+1,lambda:False)
        finally:channel.close()

    def test_stop_signal_does_not_wait_for_mutex_and_abandoned_is_not_frame(self):
        import time,uuid
        from calendar_gpu_process import SharedChannel,GpuProtocolError
        channel=SharedChannel(uuid.uuid4().hex,create=True)
        entered=threading.Event();release=threading.Event()
        def owner():
            channel.k.WaitForSingleObject(channel.handles['mutex'],0)
            entered.set();release.wait(1)
            # 실제 OS 스레드를 종료해 abandoned mutex 경계를 만듭니다.
        thread=threading.Thread(target=owner);thread.start()
        try:
            self.assertTrue(entered.wait(1))
            started=time.monotonic();channel.signal('stop')
            self.assertTrue(channel.event('stop'));self.assertLess(time.monotonic()-started,.1)
            release.set();thread.join(1);self.assertFalse(thread.is_alive())
            with self.assertRaisesRegex(GpuProtocolError,'비정상 종료'):
                with channel.locked(time.monotonic()+1):pass
        finally:release.set();thread.join(1);channel.close()


def controlled_child(mode,generation,parent_pid):
    from calendar_gpu_process import SharedChannel
    from calendar_gpu_child import serve
    from PySide6.QtGui import QColor
    import os
    channel=SharedChannel(generation)
    def native_hang():
        event=channel.k.CreateEventW(None,True,False,None)
        channel.k.WaitForSingleObject(event,0xFFFFFFFF)
        raise AssertionError('제어 native 영구 대기가 반환됐습니다.')
    class Renderer:
        def __init__(self,size,check_cancelled=None):
            if mode=='create':native_hang()
            self.ctx=type('Context',(),{'info':{'GL_RENDERER':'제어 IPC'}})()
            self.size=384
        def set_output_size(self,size):self.size=size
        def render(self,value,elapsed,country='KR',city_ref=None):
            if mode=='render':native_hang()
            if mode=='crash':os._exit(77)
            if mode=='error':raise RuntimeError('제어된 자식 렌더 오류')
            if mode=='null':return QImage()
            image=QImage(self.size,self.size,QImage.Format.Format_RGBA8888)
            if mode=='catalog':
                from city_festivals import city_events_for_date
                events=city_events_for_date(value,city_ref,country)
                image.fill(QColor({'film':2,'music':1}[events[0]['kind']],0,0,255))
            else:image.fill(QColor(30+int(elapsed),60,90,127))
            return image
        def close(self):
            if mode=='close':native_hang()
    try:return serve(channel,int(parent_pid),Renderer)
    finally:channel.close()


if __name__ == '__main__':
    if len(sys.argv)==5 and sys.argv[1]=='--controlled-child':
        raise SystemExit(controlled_child(*sys.argv[2:]))
    unittest.main()
