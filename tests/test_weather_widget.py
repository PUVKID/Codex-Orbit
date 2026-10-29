"""네트워크 기온의 유효성·수명주기와 위젯 정보 영역을 검증합니다."""
import math
import os
import sys
import time
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetricsF, QImage, QPainter
from PySide6.QtWidgets import QApplication
from weather import WeatherClient
from visuals import draw_desktop_orbit

class WeatherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.client = WeatherClient()
        self.addCleanup(self.client.close)

    def test_location_no_coordinates_in_snapshot_and_invalid(self):
        with patch.object(self.client, '_get') as get:
            self.client._location_done({'success': True, 'latitude': 37.5, 'longitude': 127.0, 'city': '서울', 'region': '서울'})
            self.assertIn('api.open-meteo.com', get.call_args.args[0])
            self.assertNotIn('37.5', str(self.client.snapshot))
            self.assertNotIn('127.0', str(self.client.snapshot))
        for latitude in (True, float('nan'), float('inf'), 91):
            with self.assertRaises(ValueError):
                self.client._location_done({'success': True, 'latitude': latitude, 'longitude': 127})
        self.client._location_done({'success': False})
        self.assertTrue(self.client.snapshot['stale'])
        self.assertIn('위치', self.client.snapshot['status'])

    def test_weather_fresh_old_invalid_and_close(self):
        now = time.time()
        self.client._weather_done({'current': {'temperature_2m': 19.5, 'time': now}})
        self.assertEqual(self.client.snapshot['temperature'], 19.5)
        self.assertFalse(self.client.snapshot['stale'])
        self.client._weather_done({'current': {'temperature_2m': 18, 'time': now-1800}})
        self.assertTrue(self.client.snapshot['stale'])
        for temp in (True, float('nan'), float('inf'), 71):
            with self.assertRaises(ValueError):
                self.client._weather_done({'current': {'temperature_2m': temp, 'time': now}})
        with self.assertRaises(ValueError):
            self.client._weather_done({'current': {'temperature_2m': 10, 'time': now+1000}})
        self.client.close()
        old = dict(self.client.snapshot)
        self.client._publish(status='종료 이후')
        self.assertEqual(old, self.client.snapshot)
        self.assertFalse(self.client.refresh())

    def test_source_age_crosses_limit_after_receipt(self):
        with patch('weather.time.time', return_value=10000), patch('weather.time.monotonic', return_value=1000):
            self.client._weather_done({'current': {'temperature_2m': 12, 'time': 9101}})
        self.assertFalse(self.client.snapshot['stale'])
        with patch('weather.time.time', return_value=10002), patch('weather.time.monotonic', return_value=1002):
            self.client._check_age()
        self.assertTrue(self.client.snapshot['stale'])
        self.assertIn('지연', self.client.snapshot['status'])

    def test_receipt_age_limit_still_applies(self):
        with patch('weather.time.time', return_value=10000), patch('weather.time.monotonic', return_value=1000):
            self.client._weather_done({'current': {'temperature_2m': 12, 'time': 10000}})
        with patch('weather.time.time', return_value=10601), patch('weather.time.monotonic', return_value=1601):
            self.client._check_age()
        self.assertTrue(self.client.snapshot['stale'])

    def test_timeout_marks_previous_value_stale(self):
        self.client._weather_done({'current': {'temperature_2m': 12, 'time': time.time()}})
        self.client._timeout()
        self.assertTrue(self.client.snapshot['stale'])
        self.assertIn('시간 초과', self.client.snapshot['status'])

    def test_response_limit_malformed_and_abort(self):
        from PySide6.QtNetwork import QNetworkReply
        class Reply:
            def __init__(self, raw): self.raw, self.aborted = raw, False
            def read(self, count): return self.raw[:count]
            def error(self): return QNetworkReply.NetworkError.NoError
            def deleteLater(self): pass
            def abort(self): self.aborted = True
        for raw in (b'x' * (self.client.LIMIT + 1), b'{broken'):
            reply = Reply(raw)
            self.client.reply = reply
            self.client._finish(reply, lambda value: self.fail('잘못된 응답 수락'))
            self.assertTrue(self.client.snapshot['stale'])
            self.assertFalse(self.client.snapshot['busy'])
        reply = Reply(b'')
        self.client.reply = reply
        self.client._timeout()
        self.assertTrue(reply.aborted)
        self.assertIsNone(self.client.reply)
        self.assertNotIn('127.0', str(self.client.snapshot))

    def test_queued_signal_receiver_context_and_no_publish_after_close(self):
        from PySide6.QtCore import QObject, QEventLoop, QThread, QTimer, Slot
        class Receiver(QObject):
            def __init__(self):
                super().__init__()
                self.received = []
            @Slot(dict)
            def accept(self, value):
                self.received.append((QThread.currentThread(), value['status']))
        receiver = Receiver()
        self.client.changed.connect(receiver.accept, Qt.ConnectionType.QueuedConnection)
        loop = QEventLoop()
        QTimer.singleShot(0, lambda: self.client._publish(status='신호 확인'))
        QTimer.singleShot(20, loop.quit)
        loop.exec()
        self.assertEqual(len(receiver.received), 1)
        self.assertIs(receiver.received[0][0], receiver.thread())
        self.client.close()
        loop = QEventLoop()
        QTimer.singleShot(0, lambda: self.client._publish(status='종료 뒤'))
        QTimer.singleShot(20, loop.quit)
        loop.exec()
        self.assertEqual(len(receiver.received), 1)

    def test_clock_temperature_layout_no_overlap(self):
        design=SimpleNamespace(title='열여섯글자까지길어지는실제꽃이름입니다', date=date(2026,10,29), accent='#8EDCCB')
        source=QImage(96,96,QImage.Format.Format_ARGB32_Premultiplied)
        source.fill(Qt.GlobalColor.transparent)
        for w,h in ((180,210),(220,260),(640,210),(180,500)):
            image=QImage(w,h,QImage.Format.Format_ARGB32_Premultiplied)
            image.fill(Qt.GlobalColor.transparent)
            painter=QPainter(image)
            result=draw_desktop_orbit(painter,w,h,source,design,.4325,'fresh','23:59:59','기온 12.5°C')
            painter.end()
            self.assertEqual(''.join(result['lines']),design.title)
            self.assertEqual(result['name_font'].pixelSize(),16)
            self.assertEqual(result['date_font'].pixelSize(),14)
            self.assertTrue(all(QFontMetricsF(result['name_font']).horizontalAdvance(line)<=w-32 for line in result['lines']))
            self.assertLessEqual(result['art'].bottom(),result['dock'].top())
            self.assertLessEqual(result['dock'].bottom(),result['weather'].top())
            self.assertLessEqual(result['weather'].bottom(),result['usage'].top())
            self.assertGreater(result['art'].width(),0)
            self.assertAlmostEqual(result['fill'].width(),result['track'].width()*.4325)

if __name__ == '__main__':
    unittest.main()
