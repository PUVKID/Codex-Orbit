"""31차 테마·설정 저장·프라이버시와 화면 마감 회귀입니다."""
import os,sys,tempfile,unittest
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette,QFontInfo
from PySide6.QtCore import Qt
from app import Controller,Settings
import theme
from qt_test_support import cleanup_qt_widgets
APP=QApplication.instance() or QApplication([])
class UiPolish31Tests(unittest.TestCase):
 def setUp(self):
  self.addCleanup(cleanup_qt_widgets,self);self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
  self.c=Controller(Settings(self.folder.name),start_worker=False,start_usage=False);self.addCleanup(self.c.close)
 def test_light_dark_light_updates_palette_and_open_widgets(self):
  theme.apply_theme('light');light=APP.palette().color(QPalette.ColorRole.Window)
  self.c.orbit29.option('ui_theme','dark');dark=APP.palette().color(QPalette.ColorRole.Window)
  self.assertLess(dark.lightness(),light.lightness());self.assertNotIn('#f3faf7',self.c.window.styleSheet())
  self.c.orbit29.option('ui_theme','light');self.assertEqual(APP.palette().color(QPalette.ColorRole.Window),light)
 def test_theme_saved_and_restarted_with_legacy_automatic_normalized(self):
  self.c.orbit29.option('ui_theme','dark');self.assertEqual(Settings(self.folder.name).values['ui_theme'],'dark')
  settings=Settings(self.folder.name);settings.values['ui_theme']='자동';settings.save()
  other=Controller(settings,start_worker=False,start_usage=False);self.addCleanup(other.close)
  self.assertEqual(other.orbit29.theme_combo.currentData(),'system');self.assertEqual(Settings(self.folder.name).values['ui_theme'],'system')
 def test_system_theme_signal_only_affects_system_mode(self):
  theme.apply_theme('system');APP.styleHints().colorSchemeChanged.emit(Qt.ColorScheme.Dark)
  self.assertEqual(theme.effective_theme(),'dark')
  theme.apply_theme('light');APP.styleHints().colorSchemeChanged.emit(Qt.ColorScheme.Dark)
  self.assertEqual(theme.effective_theme(),'light')
 def test_privacy_label_masks_existing_notice_and_replayed_tooltips(self):
  event={'id':'synthetic-ui31','target':'synthetic-target','chat_name':'합성 비공개 제목','task_summary':'합성 비공개 본문','reason':'합성 이유','after':{'model':'gpt-6.1-sol','effort':'high'}}
  self.c.receive(event);self.c.orbit29.panel.seek(0);self.c.orbit29.option('broadcast_mode',True)
  self.assertIn('프라이버시',self.c.orbit29.privacy.text());self.assertNotIn('합성 비공개',self.c.notice.title.text())
  for item in [self.c.orbit29.panel.agents.item(i) for i in range(self.c.orbit29.panel.agents.count())]:self.assertNotIn('합성 비공개',item.text()+item.toolTip())
  self.c.set_language('en');self.assertIn('Privacy',self.c.orbit29.privacy.text())
 def test_controls_font_and_no_horizontal_scroll_at_large_scale(self):
  self.c.orbit29.option('text_scale',150);self.c.window.resize(800,600);self.c.window.show();APP.processEvents()
  self.assertLessEqual(self.c.window.height(),600)
  self.assertLessEqual(self.c.window.width(),800)
  self.assertEqual(self.c.orbit29.panel.agents.horizontalScrollBarPolicy(),Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
  self.assertEqual(self.c.orbit29.theme_combo.minimumHeight(),self.c.orbit29.text_size.minimumHeight())
  for widget in (self.c.orbit29.panel.heading,self.c.orbit29.text_size,self.c.orbit29.more):
   info=QFontInfo(widget.font());self.assertIn('NanumGothic',info.family());self.assertEqual(info.weight(),700)
  self.assertEqual(sum(a.isChecked() for a in self.c.orbit29.quality_group.actions()),1)

 def test_keyboard_theme_choice_is_visible_and_persisted(self):
  from PySide6.QtTest import QTest
  self.c.window.show();combo=self.c.orbit29.theme_combo;combo.setCurrentIndex(combo.findData('light'));combo.setFocus()
  QTest.keyClick(combo,Qt.Key.Key_Down);APP.processEvents()
  self.assertEqual(combo.currentData(),'dark');self.assertEqual(Settings(self.folder.name).values['ui_theme'],'dark')
  self.assertEqual(theme.effective_theme(),'dark')
 def test_long_content_actions_reachable_at_800_by_600_in_english_150_percent(self):
  from PySide6.QtTest import QTest
  self.c.set_language('en');self.c.orbit29.option('text_scale',150)
  self.c.receive({'id':'long-ui31','target':'synthetic-long','kind':'observed','chat_name':'Synthetic long title with readable activity and navigation '*4,'task_summary':'Synthetic recorded task '*5,'after':{'model':'gpt-6.1-sol','effort':'medium'}})
  self.c.orbit29.stack.setCurrentIndex(0);self.c.window.show();self.c.window.resize(800,600);QTest.qWait(60)
  self.assertLessEqual(self.c.window.height(),600);self.assertLessEqual(self.c.window.width(),800)
  panel=self.c.orbit29.panel;scroll=panel.content_scroll
  self.assertLessEqual(scroll.widget().width(),scroll.viewport().width())
  scroll.ensureWidgetVisible(panel.copy);QTest.qWait(30)
  point=panel.copy.mapTo(scroll.viewport(),panel.copy.rect().center())
  self.assertTrue(scroll.viewport().rect().contains(point),'작은 창에서도 마지막 동작 버튼에 스크롤로 접근해야 합니다.')
  panel.copy.setFocus();self.assertTrue(panel.copy.hasFocus())

 def test_identical_style_is_idempotent_but_source_and_changed_theme_are_kept(self):
  from PySide6.QtWidgets import QLabel
  class CountedLabel(QLabel):
   calls=0
   def setStyleSheet(self,css):self.calls+=1;super().setStyleSheet(css)
  label=CountedLabel();self.addCleanup(label.close)
  source='font-size:13px;color:#193c36;'
  theme.set_ui_style(label,source);calls=label.calls
  theme.set_ui_style(label,source)
  self.assertEqual(label.calls,calls,'동일한 스타일 요청은 불필요한 Qt 재적용을 하지 않아야 합니다.')
  changed='font-size:19px;color:#193c36;';theme.set_ui_style(label,changed)
  self.assertEqual(label.property('orbit_style_source'),changed);self.assertIn('font-size:19px',label.styleSheet())
  theme.apply_theme('dark');self.assertIn(theme.colors()['text'],label.styleSheet())
  theme.apply_theme('light');self.assertIn(theme.colors()['text'],label.styleSheet())

 def test_dynamic_change_rows_survive_real_theme_and_scale_options(self):
  window=self.c.window
  before={'model':'gpt-6.1-sol','effort':'medium'}
  cases=[('model',{'model':'gpt-6-astra','effort':'medium'},True,False),
         ('effort',{'model':'gpt-6.1-sol','effort':'high'},False,True),
         ('activity',{'model':'gpt-6-astra','effort':'high'},False,False)]
  for identity,after,model_changed,effort_changed in cases:
   window.add_event({'id':'synthetic-r6-'+identity,'target':'synthetic-r6','chat_name':'합성 변경 표시',
                     'kind':'activity' if identity=='activity' else 'settings','before':before,'after':after})
   for mode in ('dark','light'):
    self.c.orbit29.option('ui_theme',mode)
    for scale in (100,150,100):
     with self.subTest(case=identity,theme=mode,scale=scale):
      self.c.orbit29.option('text_scale',scale);APP.processEvents()
      for labels,changed in (((window.model_previous,window.model_current),model_changed),
                             ((window.effort_previous,window.effort_current),effort_changed)):
       for label in labels:
        self.assertEqual('background:'+theme.colors()['selected'] in label.styleSheet(),changed)
        self.assertIn('font-size:'+str(round(26*scale/100))+'px',label.styleSheet())
        self.assertEqual(QFontInfo(label.font()).pixelSize(),round(26*scale/100))
      self.assertIn(before['model'],window.model_previous.text());self.assertIn(after['model'],window.model_current.text())
      self.assertIn('medium',window.effort_previous.text());self.assertIn(after['effort'],window.effort_current.text())

 def test_new_and_dynamically_restyled_rows_use_current_scale_without_accumulation(self):
  from PySide6.QtWidgets import QLabel
  self.c.orbit29.option('text_scale',150)
  label=QLabel(self.c.window);source='font-size:26px;color:#23453f;background:#d4f3e7;'
  theme.set_ui_style(label,source)
  self.assertIn('font-size:39px',label.styleSheet());self.assertEqual(label.property('orbit_style_source'),source)
  theme.set_ui_style(label,source)
  self.assertIn('font-size:39px',label.styleSheet())
  changed='font-size:26px;color:#23453f;';theme.set_ui_style(label,changed)
  self.c.orbit29.option('ui_theme','dark')
  self.assertNotIn('background:',label.styleSheet());self.assertIn('font-size:39px',label.styleSheet())
  self.c.orbit29.option('ui_theme','system')
  APP.styleHints().colorSchemeChanged.emit(Qt.ColorScheme.Dark)
  self.assertIn('font-size:39px',label.styleSheet())
  theme.set_ui_style(label,source)
  APP.styleHints().colorSchemeChanged.emit(Qt.ColorScheme.Light)
  self.assertIn('font-size:39px',label.styleSheet());self.assertIn('background:'+theme.colors()['selected'],label.styleSheet())
  theme.set_ui_style(label,changed)
  self.c.orbit29.option('text_scale',100)
  self.assertIn('font-size:26px',label.styleSheet());self.assertEqual(label.property('orbit_style_source'),changed)

 def test_persisted_150_fresh_and_restarted_top_controls_keep_unscaled_font_base(self):
  from PySide6.QtWidgets import QLabel
  for language in ('ko','en'):
   folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
   settings=Settings(folder.name);settings.values.update(language=language,text_scale=150,ui_theme='dark');settings.save()
   for restart in (False,True):
    with self.subTest(language=language,restart=restart):
     other=Controller(Settings(folder.name),start_worker=False,start_usage=False);self.addCleanup(other.close)
     other.window.show();other.window.resize(800,600);APP.processEvents()
     controls=[other.window.language_combo,other.orbit29.theme_combo,other.orbit29.text_size]
     controls += other.orbit29.preferences.findChildren(QLabel)
     for widget in controls:
      self.assertEqual(QFontInfo(widget.font()).pixelSize(),20)
      self.assertLessEqual(widget.fontMetrics().height(),widget.height())
     self.assertEqual(Settings(folder.name).values['text_scale'],150)
     other.close();APP.processEvents()

 def test_new_row_inherits_unscaled_font_at_150_without_multiplication(self):
  from PySide6.QtWidgets import QLabel
  self.c.orbit29.option('text_scale',150)
  label=QLabel('합성 새 행',self.c.orbit29.preferences)
  theme.set_ui_style(label,'color:#193c36;');label.ensurePolished();APP.processEvents()
  self.assertEqual(QFontInfo(label.font()).pixelSize(),20)
  self.c.orbit29.apply_text_size();APP.processEvents()
  self.assertEqual(label.property('baseFont31'),13);self.assertEqual(QFontInfo(label.font()).pixelSize(),20)
  self.c.orbit29.option('text_scale',100);self.assertEqual(QFontInfo(label.font()).pixelSize(),13)
  self.c.orbit29.option('text_scale',150);self.assertEqual(QFontInfo(label.font()).pixelSize(),20)

  self.c.update_usage({'rows':[{'bucket':'Synthetic Codex','period':'주간','remaining':43.25,'resets_at':None}],
                       'stale':False,'busy':False,'checked_at':1,'status':'합성 한도 예시'})
  self.c.orbit29.open_page(1);self.c.window.show();APP.processEvents()
  number=self.c.window.usage_rows_layout.itemAt(3).widget()
  self.assertEqual(QFontInfo(number.font()).pixelSize(),63)
  self.c.orbit29.option('text_scale',100);APP.processEvents();self.assertEqual(QFontInfo(number.font()).pixelSize(),42)
  self.c.orbit29.option('text_scale',150);APP.processEvents();self.assertEqual(QFontInfo(number.font()).pixelSize(),63)

 def test_history_detail_fits_viewport_and_keeps_full_evidence_when_resized(self):
  from PySide6.QtTest import QTest
  from PySide6.QtGui import QTextCursor
  import json
  w=self.c.window
  event={'id':'synthetic-responsive-history','target':'synthetic-responsive-history','kind':'settings',
         'chat_name':'합성 긴 제목과 모델 변경 기록을 끝까지 확인합니다. '*4,
         'task_summary':'Synthetic recorded task with a readable explanation. '*5,
         'before':{'model':'gpt-6.1-sol','effort':'medium'},'after':{'model':'gpt-6-astra','effort':'high'},
         'reason':'공개 설명의 줄바꿈과 마지막 줄을 확인합니다. '*30+'마지막 합성 이유 문장'}
  w.add_event(event);self.c.show();w.evidence_toggle.setChecked(True)
  for language in ('ko','en'):
   self.c.set_language(language)
   for scale in (100,150):
    self.c.orbit29.option('text_scale',scale)
    for width,height in ((800,600),(1400,900)):
     with self.subTest(language=language,scale=scale,width=width):
      w.resize(width,height);QTest.qWait(35)
      scroll=w.history_detail_scroll;panel=scroll.widget();split=w.history.parentWidget()
      measured={'split':split.width(),'viewport':scroll.viewport().width(),'panel':panel.width(),'panel_min':panel.minimumSizeHint().width(),'card':w.card.width(),'card_min':w.card.minimumSizeHint().width()}
      self.assertLessEqual(panel.width(),scroll.viewport().width(),json.dumps(measured))
      self.assertEqual(scroll.horizontalScrollBar().maximum(),0)
      self.assertEqual(split.orientation(),Qt.Orientation.Vertical if width==800 else Qt.Orientation.Horizontal)
      self.assertEqual(w.history.currentItem().data(Qt.ItemDataRole.UserRole)['id'],event['id'])
      if width==800:
       self.c.set_language('en' if language=='ko' else 'ko');QTest.qWait(15)
       self.assertEqual(split.orientation(),Qt.Orientation.Vertical)
       self.c.set_language(language);QTest.qWait(15)
       self.assertEqual(split.orientation(),Qt.Orientation.Vertical)
      for label in (w.chat_title,w.change_heading,w.task_value,w.reason_value,w.model_previous,w.model_current,w.effort_previous,w.effort_current):
       self.assertGreaterEqual(label.height(),label.heightForWidth(label.width()),label.text())
       left=label.mapTo(scroll.viewport(),label.rect().topLeft()).x()
       self.assertGreaterEqual(left,0);self.assertLessEqual(left+label.width(),scroll.viewport().width(),label.text())
      scroll.ensureWidgetVisible(w.detail);scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
      cursor=w.detail.textCursor();cursor.movePosition(QTextCursor.MoveOperation.End);w.detail.setTextCursor(cursor);w.detail.ensureCursorVisible();QTest.qWait(10)
      self.assertIn(event['reason'],w.detail.toPlainText())
      self.assertTrue(w.detail.viewport().rect().intersects(w.detail.cursorRect()))
