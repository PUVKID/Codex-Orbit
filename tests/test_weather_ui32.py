"""날씨 부가정보의 현지시각·누락과 호환 레이아웃을 합성 값으로 검사합니다."""
import os,sys,unittest
from pathlib import Path
from datetime import date
from types import SimpleNamespace
os.environ.setdefault('QT_QPA_PLATFORM','offscreen');sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage,QPainter
from PySide6.QtCore import Qt
import app,visuals
from i18n import set_language
APP=QApplication.instance() or QApplication([])
class WeatherUi32Tests(unittest.TestCase):
 def tearDown(self):set_language('ko')
 def test_weather_extras_use_provider_offset_and_missing_values_are_not_zero(self):
  set_language('ko');self.assertTrue(hasattr(app,'weather_widget_text'))
  value={'temperature':12.5,'humidity':43,'weather_code':0,'sunrise':86400,'sunset':90000,'utc_offset_seconds':9*3600,'stale':False}
  primary,extras=app.weather_widget_text(value)
  self.assertIn('맑음',primary);self.assertIn('43%',extras[0]);self.assertIn('09:00',extras[1]);self.assertIn('10:00',extras[1]);self.assertIn('현지',extras[0])
  primary,extras=app.weather_widget_text({'temperature':None,'humidity':None,'weather_code':None,'sunrise':None,'sunset':None,'utc_offset_seconds':None})
  self.assertIn('—',extras[0]);self.assertNotIn('0%',extras[0]);self.assertEqual(extras[1].count('—'),2)
 def test_extra_layout_keeps_actual_text_lines_inside_view_and_reports_reading_height(self):
  for scale in (1.,1.5):
   layout=visuals.desktop_widget_layout(180,250,'코코넛',True,True,text_scale=scale,weather_extras=('습도 43% · 현지 시각','일출 06:51 · 일몰 17:25'))
   self.assertIn('minimum_height',layout);self.assertGreaterEqual(layout['minimum_height'],250)
   fitted=visuals.desktop_widget_layout(180,layout['minimum_height'],'코코넛',True,True,text_scale=scale,weather_extras=('습도 43% · 현지 시각','일출 06:51 · 일몰 17:25'))
   self.assertGreaterEqual(fitted['dock'].top(),24)
   self.assertLessEqual(fitted['dock'].bottom(),fitted['location'].top());self.assertLessEqual(fitted['location'].bottom(),fitted['weather'].top());self.assertLessEqual(fitted['weather'].bottom(),fitted['usage'].top())
   for line,rect in zip(fitted['weather_lines'],fitted['weather_extra_rects']):
    from PySide6.QtGui import QFontMetricsF
    self.assertLessEqual(QFontMetricsF(fitted['weather_font']).horizontalAdvance(line),rect.width()+1)
 def test_overlay_cache_includes_extra_weather_and_old_api_stays_identical(self):
  design=SimpleNamespace(title='코코넛',date=date(2026,11,10),accent='#8EDCCB');source=QImage(32,32,QImage.Format.Format_ARGB32_Premultiplied);source.fill(Qt.GlobalColor.transparent);canvas=QImage(220,432,QImage.Format.Format_ARGB32_Premultiplied);canvas.fill(Qt.GlobalColor.transparent);cache=visuals.DesktopOverlayCache()
  painter=QPainter(canvas)
  try:
   old=visuals.draw_desktop_orbit(painter,220,432,source,design,.4,'fresh','12:00:00','12℃','합성 지역',cache=cache);key=cache.key
   first=visuals.draw_desktop_orbit(painter,220,432,source,design,.4,'fresh','12:00:00','12℃','합성 지역',cache=cache,weather_extras=('습도 43%','일출 — · 일몰 —'));first_key=cache.key
   self.assertNotEqual(key,first_key);self.assertGreater(first['weather'].height(),old['weather'].height())
   visuals.draw_desktop_orbit(painter,220,432,source,design,.4,'fresh','12:00:00','12℃','합성 지역',cache=cache,weather_extras=('습도 44%','일출 — · 일몰 —'));self.assertNotEqual(first_key,cache.key)
  finally:painter.end()
