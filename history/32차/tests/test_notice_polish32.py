"""32차 알림 요약·원문 접근과 콤보 팝업의 실제 조작 회귀입니다."""
import copy,os,sys,tempfile,unittest
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication,QStyle,QStyleOptionComboBox,QLabel,QWidget,QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from app import Controller,Settings
from notice_format import notice_reason,notice_reason_original
from i18n import set_language
from qt_test_support import cleanup_qt_widgets
import theme
APP=QApplication.instance() or QApplication([])

class NoticePolish32Tests(unittest.TestCase):
 def setUp(self):
  set_language('ko');self.addCleanup(set_language,'ko');self.addCleanup(cleanup_qt_widgets,self)
  self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
  self.c=Controller(Settings(self.folder.name),start_worker=False,start_usage=False);self.addCleanup(self.c.close)
 def event(self,**extra):
  return {'id':'synthetic32','target':'synthetic-target','chat_name':'합성 알림 검토',
   'before':{'model':'gpt-6.1-sol','effort':'medium'},'after':{'model':'gpt-6.1-terra','effort':'high'},
   'reason':'role=build / task=synthetic32 / session=synthetic-only. 선택 이유: 화면의 글자가 겹쳐 배치를 고칩니다. 같은 화면을 다시 확인합니다. 추가 검증 기록입니다.',**extra}
 def test_reason_extracts_public_purpose_without_metadata_and_preserves_original(self):
  event=self.event();original=copy.deepcopy(event);text=notice_reason(event)
  self.assertNotIn('role=',text);self.assertNotIn('session=',text);self.assertNotIn('추가 검증',text)
  self.assertIn('글자가 겹쳐',text);self.assertNotIn('…',text)
  self.assertEqual(notice_reason_original(event),event['reason']);self.assertEqual(event,original)
 def test_visible_example_prioritizes_observed_failure_over_verification_plan(self):
  # 공개 시험은 검사 계획과 화면 조작 실패를 나타내는 합성 문장만 사용합니다.
  raw='20개 검사와 기존 기능 재확인을 마친 뒤 결과를 정리할 예정입니다.\n합성 선택 버튼을 누르는 데 실패했습니다.'
  event=self.event(reason=raw);text=notice_reason(event)
  self.assertEqual(text,'합성 선택 버튼을 누르는 데 실패했습니다.')
  self.assertEqual(notice_reason_original(event),raw)

 def test_unexplained_assignment_never_invents_model_selection_reason(self):
  event=self.event(reason='role=build / task=synthetic32 / session=synthetic-only',kind='activity',activity_type='assigned',task_summary='한글 안내를 다듬습니다.')
  self.assertIn('선택 이유를 확인할 수 없습니다',notice_reason(event));self.assertIn('한글 안내',notice_reason(event))
  self.assertNotIn('적합',notice_reason(event));self.assertEqual(notice_reason_original(event).split('\n')[0],event['reason'])
 def test_compact_notice_has_plain_title_full_values_and_explicit_original_disclosure(self):
  event=self.event();self.c.receive(event);card=self.c.notice
  self.assertEqual(card.title.text(),event['chat_name']);self.assertEqual(card.title_marker.text(),'')
  for label,value in [(card.model_previous,'gpt-6.1-sol'),(card.model_current,'gpt-6.1-terra'),(card.effort_previous,'medium'),(card.effort_current,'high')]:
   self.assertIn(value,label.text());self.assertTrue(label.isVisible())
  self.assertLessEqual(card.height(),440);self.assertTrue(hasattr(card,'reason_disclosure'))
  self.assertFalse(card.reason_original.isVisible());QTest.mouseClick(card.reason_disclosure,Qt.MouseButton.LeftButton);APP.processEvents()
  self.assertTrue(card.reason_original.isVisible());self.assertIn(event['reason'],card.reason_original.toPlainText())
  QTest.mouseClick(card.reason_disclosure,Qt.MouseButton.LeftButton);APP.processEvents();self.assertFalse(card.reason_original.isVisible())
 def test_same_model_resume_is_distinct_and_privacy_hides_expanded_original(self):
  event=self.event(kind='activity',activity_type='resumed',after={'model':'gpt-6.1-sol','effort':'medium'})
  self.c.receive(event);card=self.c.notice;self.assertIn('재개',card.category.text());self.assertIn('설정 유지',card.category.text())
  self.assertTrue(hasattr(card,'reason_disclosure'));card.reason_disclosure.click();self.c.orbit29.option('broadcast_mode',True);APP.processEvents()
  self.assertNotIn('synthetic32',card.reason_original.toPlainText()+card.reason_original.toolTip());self.assertNotIn('글자가 겹쳐',card.reason_original.toPlainText())
 def test_single_item_popup_has_no_menu_scrollers_and_item_fits(self):
  from ui_layout import OrbitComboBox
  owner=QWidget();self.addCleanup(owner.close);layout=QVBoxLayout(owner);combo=OrbitComboBox(owner);combo.addItem('100%',100);layout.addWidget(combo);owner.show();APP.processEvents()
  option=QStyleOptionComboBox();combo.initStyleOption(option)
  self.assertEqual(combo.style().styleHint(QStyle.StyleHint.SH_ComboBox_Popup,option,combo),0)
  QTest.mouseClick(combo,Qt.MouseButton.LeftButton);APP.processEvents();view=combo.view()
  from time import monotonic
  popup_deadline=monotonic()+.75
  while not view.isVisible() and monotonic()<popup_deadline:QTest.qWait(10)
  self.assertTrue(view.isVisible());rect=view.visualRect(view.model().index(0,0));self.assertTrue(view.viewport().rect().contains(rect));self.assertFalse(view.verticalScrollBar().isVisible())
  QTest.keyClick(view,Qt.Key.Key_Return);APP.processEvents();self.assertFalse(view.isVisible())
 def test_notice_follows_saved_scale_and_returns_without_cumulative_growth(self):
  from PySide6.QtGui import QFontInfo
  self.c.receive(self.event());card=self.c.notice
  for value,expected in ((100,16),(150,24),(100,16)):
   self.c.orbit29.option('text_scale',value);APP.processEvents();card.model_current.ensurePolished()
   self.assertEqual(QFontInfo(card.model_current.font()).pixelSize(),expected)
   self.assertGreaterEqual(card.model_current.height(),card.model_current.heightForWidth(card.model_current.width()))
   self.assertIn('gpt-6.1-terra',card.model_current.text())

 def test_close_button_keeps_actual_height_after_polish_theme_language_and_scale(self):
  from PySide6.QtWidgets import QStyleOptionButton
  self.c.receive(self.event());card=self.c.notice;button=card.close_button
  for mode in ('light','dark'):
   for language in ('ko','en'):
    for scale in (100,150,100):
     with self.subTest(mode=mode,language=language,scale=scale):
      self.c.orbit29.option('ui_theme',mode);self.c.set_language(language);self.c.orbit29.option('text_scale',scale)
      button.ensurePolished();card.layout().activate();APP.processEvents()
      self.assertEqual(button.height(),round(30*scale/100))
      card.activateWindow();button.setFocus();APP.processEvents();self.assertTrue(button.hasFocus())
      self.assertEqual(button.height(),round(30*scale/100))
      option=QStyleOptionButton();button.initStyleOption(option)
      rect=button.style().subElementRect(QStyle.SubElement.SE_PushButtonContents,option,button)
      self.assertGreaterEqual(rect.height(),button.fontMetrics().height())
      self.assertGreaterEqual(rect.width(),button.fontMetrics().horizontalAdvance(button.text()))

 def test_light_and_dark_use_slate_colors_not_green(self):
  for mode in ('light','dark'):
   theme.apply_theme(mode);c=theme.colors();self.assertGreaterEqual(int(c['accent'][5:7],16),int(c['accent'][3:5],16))
  self.assertEqual(theme.PALETTES['light']['bg'],'#f6f8fb')

 def test_combo_actual_hover_focus_press_select_and_disabled_in_both_themes_and_scales(self):
  from ui_layout import OrbitComboBox
  from PySide6.QtGui import QFontInfo
  for mode in ('light','dark'):
   for language in ('ko','en'):
    for scale in (100,150):
     with self.subTest(mode=mode,language=language,scale=scale):
      self.c.orbit29.option('ui_theme',mode);self.c.set_language(language);self.c.orbit29.option('text_scale',scale)
      self.c.window.resize(800,600);self.c.window.show();APP.processEvents();combo=self.c.orbit29.text_size
      from time import monotonic
      deadline=monotonic()+.5;stable=0;last=None
      while monotonic()<deadline and stable<3:
       APP.processEvents();current=combo.geometry();stable=stable+1 if current==last else 0;last=current;QTest.qWait(1)
      self.assertEqual(stable,3,'배율·언어 변경 뒤 실제 배치가 준비되어야 합니다.')
      before=combo.geometry();QTest.mouseMove(combo,combo.rect().center());APP.processEvents();self.assertEqual(combo.geometry(),before)
      combo.setFocus();APP.processEvents();self.assertTrue(combo.hasFocus());self.assertEqual(combo.geometry(),before)
      QTest.mousePress(combo,Qt.MouseButton.LeftButton);QTest.mouseRelease(combo,Qt.MouseButton.LeftButton);APP.processEvents()
      popup_deadline=monotonic()+.75
      while not combo.view().isVisible() and monotonic()<popup_deadline:QTest.qWait(10)
      self.assertTrue(combo.view().isVisible());QTest.keyClick(combo.view(),Qt.Key.Key_End);QTest.keyClick(combo.view(),Qt.Key.Key_Return);APP.processEvents()
      self.assertEqual(combo.currentData(),150);self.assertEqual(self.c.settings.values['text_scale'],150)
      combo.setEnabled(False);value=combo.currentData();QTest.keyClick(combo,Qt.Key.Key_Home);self.assertEqual(combo.currentData(),value)
      self.assertEqual(QFontInfo(combo.font()).weight(),700);combo.setEnabled(True)
      for label in (self.c.orbit29.location_label,):self.assertLessEqual(label.geometry().right(),self.c.orbit29.controls.width())

class LocationUi32Tests(unittest.TestCase):
 def setUp(self):
  set_language('ko');self.addCleanup(set_language,'ko');self.addCleanup(cleanup_qt_widgets,self)
  self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
  self.c=Controller(Settings(self.folder.name),start_worker=False,start_usage=False);self.addCleanup(self.c.close)
 def test_city_choice_persists_validated_coordinates_and_automatic_reset(self):
  from unittest.mock import patch
  city={'name':'Synthetic City','admin1':'Synthetic State','country':'Synthetic Country','country_code':'KR','latitude':37.2,'longitude':127.0,'id':123}
  self.assertTrue(hasattr(self.c,'set_weather_location'))
  with patch.object(self.c.weather,'refresh') as refresh:
   self.c.set_weather_location(city);self.assertEqual(self.c.weather.location_override['latitude'],37.2)
   self.assertEqual(Settings(self.folder.name).values['weather_location'],city);self.assertIn('지정한 지역',self.c.orbit.location_text)
   self.c.set_weather_location(None);self.assertIsNone(Settings(self.folder.name).values['weather_location']);self.assertIn('네트워크 추정',self.c.orbit.location_text)
   self.assertEqual(refresh.call_count,2)
 def test_city_search_dialog_only_sends_explicit_search_and_applies_selected_row(self):
  from unittest.mock import patch
  from PySide6.QtCore import QObject,Signal
  class Search(QObject):
   results=Signal(list);failed=Signal(str)
   def __init__(self,parent=None,language='ko'):super().__init__(parent);self.queries=[];self.closed=False
   def search(self,text):self.queries.append(text);return True
   def close(self):self.closed=True
  self.assertTrue(hasattr(self.c,'show_weather_location'))
  with patch('app.CitySearchClient',Search),patch.object(self.c.weather,'refresh'):
   self.c.show_weather_location();dialog=self.c.location_dialog;self.assertEqual(dialog.client.queries,[])
   dialog.query.setText('Synthetic City');QTest.mouseClick(dialog.search_button,Qt.MouseButton.LeftButton);self.assertEqual(dialog.client.queries,['Synthetic City'])
   city={'name':'Synthetic City','admin1':'Synthetic State','country':'Synthetic Country','country_code':'KR','latitude':37.2,'longitude':127.0,'id':123}
   dialog.client.results.emit([city]);dialog.cities.setCurrentRow(0);QTest.mouseClick(dialog.apply_button,Qt.MouseButton.LeftButton)
   self.assertEqual(self.c.settings.values['weather_location'],city);self.assertTrue(dialog.client.closed)
