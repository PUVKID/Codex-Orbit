"""가져오기·생성 중 종료와 미완료 작업자 회수를 제어된 경계에서 검사합니다."""
import builtins
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import calendar_motion as motion


class ShutdownTests(unittest.TestCase):
    def test_stop_during_import_skips_context_creation(self):
        self._stop_at('import')

    def test_stop_during_creation_closes_without_first_render(self):
        self._stop_at('creation')

    def _stop_at(self,stage):
        entered=threading.Event();release=threading.Event();calls=[]
        class Renderer:
            def __init__(self,size):
                calls.append('create')
                if stage=='creation':entered.set();release.wait(1)
                self.ctx=type('Context',(),{'info':{}})()
            def render(self,*args,**kwargs):
                calls.append('render');raise RuntimeError('종료 뒤 렌더 호출')
            def close(self):calls.append('close')
        original=builtins.__import__
        def importing(name,*args,**kwargs):
            if name=='calendar_renderer':
                if stage=='import':entered.set();release.wait(1)
                return type('Module',(),{'CalendarRenderer':Renderer})
            return original(name,*args,**kwargs)
        worker=motion._Worker();worker.configure(visible=True)
        thread=threading.Thread(target=worker.run)
        with patch('builtins.__import__',side_effect=importing):
            thread.start()
            try:
                self.assertTrue(entered.wait(1))
                worker.stop();release.set();thread.join(1)
                self.assertFalse(thread.is_alive())
            finally:
                worker.stop();release.set();thread.join(1)
        self.assertEqual(calls,[] if stage=='import' else ['create','close'])

    def test_second_close_reaps_retiring_without_new_service(self):
        class Service:
            def __init__(self):self.calls=[]
            def close(self,*args,**kwargs):
                self.calls.append((args,kwargs));return len(self.calls)>1
        service=Service()
        with patch.object(motion,'_service',service),patch.object(motion,'_retiring',None):
            with self.assertLogs('calendar_motion',level='ERROR'):motion.close_calendar_motion()
            self.assertIsNone(motion._service);self.assertIs(motion._retiring,service)
            motion.close_calendar_motion()
            self.assertIsNone(motion._retiring);self.assertEqual(len(service.calls),2)

    def test_restart_cleans_finished_retiring_before_creating_service(self):
        calls=[]
        class Retiring:
            worker=type('Worker',(),{'isRunning':lambda self:False})()
            def close(self,*args,**kwargs):calls.append('clean');return True
        def create():calls.append('create');return object()
        with patch.object(motion,'_main_thread'),patch.object(motion,'_quit_connected',True),\
             patch.object(motion,'_service',None),patch.object(motion,'_retiring',Retiring()),\
             patch.object(motion,'CalendarMotion',side_effect=create):
            motion._get_service()
            self.assertEqual(calls,['clean','create'])
            self.assertIsNone(motion._retiring)


if __name__=='__main__':unittest.main()
