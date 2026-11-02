"""29차 알림·개인정보·상호작용의 사용자 동작 검사입니다."""
import os,sys,tempfile,unittest
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEvent,Qt
from observatory_panel import present_event, pause_notice, resume_notice, mask_details
from app import Notice
APP=QApplication.instance() or QApplication([])

class Interface29Tests(unittest.TestCase):
 def event(self):
  return {'id':'e1','target':'chat1','chat_name':'🔄 실제 제목','before':{'model':'gpt-6.1-sol','effort':'medium'},'after':{'model':'gpt-6.1-sol','effort':'high'},'reason':'검사를 자세히 확인합니다.'}
 def test_title_presentation_preserves_original(self):
  e=self.event(); shown=present_event(e,False)
  self.assertEqual(shown['chat_name'],'실제 제목');self.assertEqual(e['chat_name'],'🔄 실제 제목')
 def test_privacy_hides_all_public_sensitive_fields(self):
  e=self.event();e.update(task_summary='비공개 작업',evidence='비공개근거')
  p=present_event(e,True)
  self.assertNotIn('실제 제목',str(p));self.assertNotIn('비공개 작업',str(p));self.assertNotIn('비공개근거',str(p))
  self.assertEqual(p['after'],e['after'])
 def test_hover_freezes_auto_close_and_resumes_remaining(self):
  n=Notice(lambda *_:None);n.timer.start(35000)
  pause_notice(n);remaining=n._hover_remaining
  self.assertFalse(n.timer.isActive());self.assertGreater(remaining,30000)
  resume_notice(n);self.assertTrue(n.timer.isActive());self.assertLessEqual(n.timer.remainingTime(),remaining)
  n.timer.stop();n.close()
 def test_pinned_notice_stays_open_after_leave(self):
  n=Notice(lambda *_:None);n.pinned=True;n.timer.start(35000)
  pause_notice(n);resume_notice(n);self.assertFalse(n.timer.isActive());n.close()

class IntegratedExperience29Tests(unittest.TestCase):
 def setUp(self):
  from app import Controller,Settings
  from i18n import set_language
  from qt_test_support import cleanup_qt_widgets
  set_language('ko');self.addCleanup(set_language,'ko');self.addCleanup(cleanup_qt_widgets,self)
  folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
  # 관측소 기능 검사는 명시 선택 상태를 유지하고 달력 기본값은30차에서 따로 검사합니다.
  settings=Settings(folder.name);settings.values['scene_mode']='observatory'
  self.c=Controller(settings,start_worker=False,start_usage=False);self.addCleanup(self.c.close)
 def record(self,**extra):
  return {'id':'private-event','target':'chat-only-fixture','time':'2026-11-02T01:00:00+00:00','chat_name':'🔄 비공개 시험 제목','before':{'model':'gpt-6.1-sol','effort':'medium'},'after':{'model':'gpt-6-astra','effort':'high'},'reason':'비공개 작업 이유','task_summary':'비공개 작업 본문',**extra}
 def test_broadcast_masks_existing_card_history_and_tooltips_then_restores(self):
  from PySide6.QtWidgets import QLabel
  self.c.receive(self.record());self.c.show();self.c.orbit29.option('broadcast_mode',True)
  notice=self.c.notice
  shown=' '.join(x.text()+x.toolTip() for x in notice.findChildren(QLabel))
  shown+=self.c.window.detail.toPlainText()+self.c.window.history.item(0).text()
  self.assertNotIn('비공개 시험 제목',shown);self.assertNotIn('비공개 작업 본문',shown);self.assertNotIn('비공개 작업 이유',shown)
  self.assertEqual(notice.notice_event['chat_name'],'🔄 비공개 시험 제목')
  self.c.orbit29.option('broadcast_mode',False)
  self.assertEqual(notice.title.text(),'비공개 시험 제목')
 def test_pause_keeps_notifications_and_actual_fraction(self):
  self.c.orbit29.option('motion_paused',True);self.c.receive(self.record())
  self.assertTrue(self.c.notice.isVisible());self.assertTrue(self.c.orbit29.scene['paused'])
  self.assertIsNone(self.c.orbit29.scene['usage_fraction'])
 def test_history_replay_does_not_change_settings_or_live_events(self):
  self.c.receive(self.record());self.c.receive(self.record(id='later',time='2026-11-02T02:00:00+00:00',after={'model':'gpt-6-luna','effort':'low'}))
  before=dict(self.c.settings.values);events=self.c.features.snapshot()['events']
  self.c.orbit29.panel.seek(0)
  self.assertEqual(before,self.c.settings.values);self.assertEqual(events,self.c.features.snapshot()['events'])
  self.assertIn('기록 재생',self.c.orbit29.panel.replay_label.text())
 def test_targetless_notice_does_not_create_fictional_satellite(self):
  self.c.receive({'id':'targetless','after':{'model':'unknown'}})
  self.assertTrue(self.c.notice.isVisible());self.assertFalse(self.c.features.snapshot()['agents'])
 def test_pinned_notification_survives_overflow(self):
  self.c.receive(self.record());first=self.c.notice;first.set_pinned(True)
  for i in range(10):self.c.receive(self.record(id='overflow'+str(i)))
  self.assertIs(self.c.notices['private-event'],first);self.assertTrue(first.isVisible())
 def test_user_text_scale_changes_labels_without_resizing_widget(self):
  size=self.c.orbit.size();font=self.c.window.chat_title.font().pixelSize()
  self.c.orbit29.option('text_scale',150)
  self.assertEqual(size,self.c.orbit.size());self.assertGreater(self.c.window.chat_title.font().pixelSize(),font)

 def test_small_window_minimum_layout_fits_768_height(self):
  self.c.window.resize(1100,700);APP.processEvents()
  self.assertLessEqual(self.c.window.minimumSizeHint().height(),768)
 def test_existing_update_dialog_retranslates_without_network(self):
  from update_widgets import UpdateDialog
  dialog=UpdateDialog(self.c);self.c.update_dialog29=dialog
  self.c.set_language('en')
  self.assertEqual(dialog.windowTitle(),'Official update');self.assertEqual(dialog.action.text(),'Check for update')
  dialog.close()
 def test_explicit_lifecycle_keeps_last_observed_model(self):
  self.c.receive(self.record(kind='observed'))
  self.c.receive_lifecycle({'id':'done','target':'chat-only-fixture','kind':'lifecycle','status':'completed','time':'2026-11-02T02:00:00+00:00'})
  self.assertEqual(self.c.orbit29.scene['model'],'gpt-6-astra')
 def replay_first_record(self):
  self.c.receive(self.record())
  self.c.receive(self.record(id='later',time='2026-11-02T02:00:00+00:00',chat_name='나중 합성 제목'))
  panel=self.c.orbit29.panel;panel.timeline.setValue(0)
  self.assertTrue(panel.replaying)
  return panel
 def test_broadcast_masks_replayed_title_task_and_agent_without_moving_history(self):
  panel=self.replay_first_record();saved=panel.replay_snapshot;position=panel.timeline.value()
  self.c.orbit29.option('broadcast_mode',True)
  shown=' '.join([panel.heading.text(),panel.state.text(),*[panel.agents.item(i).text() for i in range(panel.agents.count())]])
  self.assertNotIn('비공개 시험 제목',shown);self.assertNotIn('비공개 작업 본문',shown)
  self.assertTrue(panel.replaying);self.assertEqual(panel.timeline.value(),position);self.assertEqual(panel.replay_snapshot,saved)
  self.c.orbit29.option('broadcast_mode',False)
  self.assertEqual(panel.heading.text(),'비공개 시험 제목')
  self.assertNotIn('나중 합성 제목',panel.heading.text())
 def test_language_switch_retranslates_replay_controls_without_changing_snapshot(self):
  panel=self.replay_first_record();saved=panel.replay_snapshot;position=panel.timeline.value()
  self.c.set_language('en')
  self.assertEqual(panel.pin.text(),'★ Pin chat');self.assertEqual(panel.copy.text(),'Copy chat ID')
  self.assertIn('History replay',panel.replay_label.text());self.assertEqual(panel.live.text(),'Return to live')
  self.assertTrue(panel.replaying);self.assertEqual(panel.timeline.value(),position);self.assertEqual(panel.replay_snapshot,saved)
 def test_replay_selects_exact_record_when_delivery_was_delayed(self):
  self.c.receive(self.record(source_time='2026-11-02T00:00:00Z',time='2026-11-02T03:00:00Z',after={'model':'gpt-6.1-sol','effort':'medium'}))
  self.c.receive(self.record(id='later',source_time='2026-11-02T00:01:00Z',time='2026-11-02T03:01:00Z',after={'model':'gpt-6.1-sol','effort':'high'}))
  panel=self.c.orbit29.panel;panel.timeline.setValue(0)
  self.assertEqual([event['id'] for event in panel.replay_snapshot['events']],['private-event'])
  self.assertEqual(self.c.orbit29.scene['effort'],'medium')
 def test_navigation_marks_only_the_visible_page_after_real_button_clicks(self):
  from PySide6.QtTest import QTest
  experience=self.c.orbit29
  for button,page,tab in ((experience.nav_buttons[0],1,0),(experience.observatory_button,0,None),(experience.nav_buttons[0],1,0),(experience.nav_buttons[1],1,1)):
   QTest.mouseClick(button,Qt.MouseButton.LeftButton)
   self.assertEqual(experience.stack.currentIndex(),page)
   self.assertEqual(experience.observatory_button.isChecked(),page==0)
   self.assertEqual([item.isChecked() for item in experience.nav_buttons],[page==1 and index==tab for index in range(2)])
