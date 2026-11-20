"""좁은 위젯의 고정 백분율 기대와 실제 글자·조형 영역을 확인합니다."""
import os,sys,unittest
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontMetricsF
from i18n import set_language
import visuals
APP=QApplication.instance() or QApplication([])

class WidgetReadability34Tests(unittest.TestCase):
 def tearDown(self):set_language('ko')
 def test_fixed_rounding_labels_keep_raw_bar_fraction(self):
  for language,labels in (('ko',('잔량 0.0%','잔량 25.0%','잔량 100.0%','잔량 약 100.0%','잔량 약 0.0%')),('en',('Remaining 0.0%','Remaining 25.0%','Remaining 100.0%','Remaining About 100.0%','Remaining About 0.0%'))):
   set_language(language)
   for value,expected in zip((0,.25,1,.9999,.0001),labels):
    with self.subTest(language=language,value=value):
     rect,label=visuals.usage_bar('잘못된 외부 표기',value,'fresh')
     self.assertEqual(label,expected)
     self.assertAlmostEqual(rect.width(),visuals.USAGE_TRACK_RECT.width()*value)
 def test_minimum_height_is_stable_and_every_text_line_fits_without_font_shrink(self):
  for language in ('ko','en'):
   set_language(language)
   for scale in (1.,1.5):
    for width in (180,220,420):
     with self.subTest(language=language,scale=scale,width=width):
      arguments=dict(show_weather=True,show_location=True,text_scale=scale,weather_extras=('Humidity About 100.0% · Rain 2 mm (last 60 min)','Sunrise 07:10 · Sunset 17:30'),clock_text='23:59:59',weather_text='Earlier: 22.5°C · Clear',fraction=.9999,state='fresh')
      initial=visuals.desktop_widget_layout(width,250,'긴 합성 조형 이름',**arguments)
      height=initial['minimum_height']
      fitted=visuals.desktop_widget_layout(width,height,'긴 합성 조형 이름',**arguments)
      self.assertEqual(fitted['minimum_height'],height)
      self.assertGreaterEqual(fitted['art'].width(),96*scale)
      self.assertGreaterEqual(fitted['art'].top(),0)
      self.assertLessEqual(fitted['art'].bottom(),fitted['dock'].top())
      self.assertEqual(fitted['date_font'].pixelSize(),round(14*scale))
      for key,font_key in (('clock_lines','date_font'),('primary_weather_lines','date_font'),('usage_lines','date_font')):
       metrics=QFontMetricsF(fitted[font_key])
       for line in fitted[key]:self.assertLessEqual(metrics.horizontalAdvance(line),width-32+.1)
      self.assertEqual(''.join(fitted['primary_weather_lines']).replace(' ',''),'Earlier:22.5°C·Clear')
      self.assertGreaterEqual(fitted['usage'].top(),fitted['weather'].bottom()+6)
 def test_clock_seconds_change_does_not_change_row_count(self):
  first=visuals.desktop_widget_layout(180,600,'배',clock_text='11:11:11',calendar_date='11/13',text_scale=1.5)
  second=visuals.desktop_widget_layout(180,600,'배',clock_text='23:59:59',calendar_date='11/13',text_scale=1.5)
  self.assertEqual(len(first['clock_lines']),2)
  self.assertEqual(len(first['clock_lines']),len(second['clock_lines']))
  self.assertEqual(first['dock'],second['dock'])
