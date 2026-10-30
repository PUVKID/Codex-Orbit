"""기온 연결은 네트워크 없이 표시·시작·종료·저장 크기를 검사합니다."""
from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtCore import QObject,Signal
from PySide6.QtWidgets import QApplication
from app import Controller,Settings
from qt_test_support import cleanup_qt_widgets

class FakeWeather(QObject):
    changed=Signal(dict)
    def __init__(self,parent=None,language='ko'):
        super().__init__(parent);self.started=0;self.closed=False
        self.language=language if language in ('ko','en') else 'ko'
        self.snapshot={'temperature':None,'region':'','checked_at':None,'observed_at':None,'status':'기온 조회 준비','stale':True,'busy':False,
                       'language':self.language,'region_original':'','region_source':'ipwho.is · 원문'}
    def set_language(self,language):
        if self.closed:return
        language=language if language in ('ko','en') else 'ko'
        if language==self.language:return
        self.language=language
        self.snapshot={**self.snapshot,'language':language}
        self.changed.emit(dict(self.snapshot))
    def start(self):
        if not self.closed:self.started+=1
    def close(self):self.closed=True

class WeatherIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.addCleanup(cleanup_qt_widgets,self)
        self.settings=Settings(Path(self.temp.name))
    def create(self,**kwargs):
        with patch('app.WeatherClient',FakeWeather):
            self.controller=Controller(self.settings,start_worker=False,start_usage=False,**kwargs)
        return self.controller
    def test_fresh_stale_failed_and_tooltip_survive_usage_refresh(self):
        c=self.create();self.assertEqual(c.weather.started,0)
        value=dict(temperature=5.2,region='추정 지역',checked_at=1793199840,observed_at=1793199600,status='기온 최신',stale=False,busy=False)
        c.weather.changed.emit(value);self.assertEqual(c.orbit.weather_text,'5.2℃')
        self.assertIn('제공 시각: '+datetime.fromtimestamp(1793199600).astimezone().strftime('%Y-%m-%d %H:%M:%S'),c.orbit.toolTip())
        self.assertIn('조회 시각: '+datetime.fromtimestamp(1793199840).astimezone().strftime('%Y-%m-%d %H:%M:%S'),c.orbit.toolTip())
        c.update_usage(c.usage.snapshot)
        self.assertIn('네트워크 추정',c.orbit.toolTip());self.assertIn('Open-Meteo',c.orbit.toolTip())
        c.weather.changed.emit(dict(value,stale=True));self.assertIn('이전',c.orbit.weather_text)
        c.weather.changed.emit(dict(value,temperature=None,stale=True,status='네트워크 조회 실패'))
        self.assertIn('미확인',c.orbit.weather_text);self.assertIn('실패',c.orbit.toolTip())
        c.weather.changed.emit(dict(value,observed_at=None,checked_at=None))
        self.assertIn('제공 시각: 미확인',c.orbit.toolTip());self.assertIn('조회 시각: 미확인',c.orbit.toolTip())
    def test_explicit_start_close_and_late_signal(self):
        c=self.create(start_weather=True);self.assertEqual(c.weather.started,1)
        c.close();self.assertTrue(c.weather.closed)
        before=c.orbit.weather_text;c.update_weather({'temperature':99})
        self.assertEqual(c.orbit.weather_text,before)
        c.close()
    def test_clock_seconds_default_size_and_saved_size(self):
        c=self.create();self.assertEqual((c.orbit.width(),c.orbit.height()),(220,332))
        with patch('app.datetime') as clock:
            clock.now.return_value=datetime(2026,10,29,1,2,3)
            self.assertEqual(c.orbit.clock_text(),'01:02:03')
            clock.now.return_value=datetime(2026,10,29,1,2,4)
            self.assertEqual(c.orbit.clock_text(),'01:02:04')
        c.close();self.settings.values['size']=[230,270]
        c=self.create();self.assertEqual((c.orbit.width(),c.orbit.height()),(230,270))

if __name__=='__main__':unittest.main()
