"""위젯 글자 배율이 정보 영역과 실제 그리기·캐시까지 전달되는지 확인합니다."""
import os,sys,tempfile,unittest
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage,QPainter
from PySide6.QtCore import Qt
from visuals import desktop_widget_layout,DesktopOverlayCache
from calendar_art import design_for_date,current_date
from unittest.mock import patch
APP=QApplication.instance() or QApplication([])
class DesktopScale29Tests(unittest.TestCase):
 def test_large_text_keeps_information_areas_separate(self):
  normal=desktop_widget_layout(340,500,'긴 지역과 오늘의 조형',True,True)
  large=desktop_widget_layout(340,500,'긴 지역과 오늘의 조형',True,True,text_scale=1.5)
  self.assertGreater(large['name_font'].pixelSize(),normal['name_font'].pixelSize())
  self.assertLess(large['art'].bottom(),large['dock'].top())
  self.assertLess(large['dock'].bottom(),large['location'].top())
  self.assertLess(large['location'].bottom(),large['weather'].top())
  self.assertLess(large['weather'].bottom(),large['usage'].top())
  self.assertLessEqual(large['usage'].bottom(),500)
 def test_cache_invalidates_when_only_text_scale_changes(self):
  image=QImage(340,500,QImage.Format.Format_ARGB32_Premultiplied);image.fill(Qt.GlobalColor.transparent)
  source=QImage(100,100,QImage.Format.Format_ARGB32_Premultiplied);source.fill(Qt.GlobalColor.transparent)
  cache=DesktopOverlayCache();p=QPainter(image)
  try:
   cache.draw(p,340,500,source,design_for_date(current_date()),.72,'fresh','12:00:00','18°C','서울',text_scale=1.)
   old=cache.key;pixels=cache.layout['date_font'].pixelSize()
   cache.draw(p,340,500,source,design_for_date(current_date()),.72,'fresh','12:00:00','18°C','서울',text_scale=1.5)
   self.assertNotEqual(cache.key,old);self.assertGreater(cache.layout['date_font'].pixelSize(),pixels)
  finally:p.end()
 def test_user_control_reaches_widget_painter_without_resizing_window(self):
  from app import Settings,Controller
  from qt_test_support import cleanup_qt_widgets
  self.addCleanup(cleanup_qt_widgets,self)
  folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
  c=Controller(Settings(folder.name),start_worker=False,start_usage=False);self.addCleanup(c.close)
  original=c.orbit.size();c.orbit29.option('text_scale',150)
  with patch('app.draw_desktop_orbit') as draw:c.orbit.grab()
  self.assertEqual(c.orbit.size(),original);self.assertEqual(draw.call_args.kwargs['text_scale'],1.5)

 def test_retained_orbit_painter_ends_before_grab_returns_and_widget_gc(self):
  import gc
  from app import Settings,Controller
  from qt_test_support import cleanup_qt_widgets
  self.addCleanup(cleanup_qt_widgets,self)
  folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
  c=Controller(Settings(folder.name),start_worker=False,start_usage=False);self.addCleanup(c.close)
  with patch('app.draw_desktop_orbit') as draw:c.orbit.grab()
  painter=draw.call_args.args[0]
  self.assertFalse(painter.isActive(),'그리기 함수가 끝나면 보관된 painter도 비활성이어야 합니다.')
  c.close();cleanup_qt_widgets(self)
  draw.reset_mock();del painter,draw
  gc.collect()

 def test_retained_scene_painter_ends_before_grab_returns_and_widget_gc(self):
  import gc
  from app import Settings,Controller
  from observatory_panel import SceneCanvas
  from qt_test_support import cleanup_qt_widgets
  self.addCleanup(cleanup_qt_widgets,self)
  folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
  c=Controller(Settings(folder.name),start_worker=False,start_usage=False);self.addCleanup(c.close)
  canvas=c.window.findChild(SceneCanvas)
  self.assertIsNotNone(canvas)
  held=[]
  def capture(device):
   painter=QPainter(device);held.append(painter);return painter
  with patch('observatory_panel.QPainter',side_effect=capture):canvas.grab()
  self.assertTrue(held)
  self.assertTrue(all(not painter.isActive() for painter in held),'관측소 그리기 도구도 paintEvent 안에서 끝나야 합니다.')
  c.close();cleanup_qt_widgets(self)
  held.clear();gc.collect()
