"""한영 전환이 실제 화면과 원문 보존에 미치는 동작을 검사합니다."""
import copy
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))


class LanguageAvailabilityTests(unittest.TestCase):
    def test_language_feature_exists(self):
        self.assertIsNotNone(importlib.util.find_spec('i18n'), '한영 선택 기능 모듈이 필요합니다.')


if importlib.util.find_spec('i18n'):
    from i18n import get_language, set_language, translate
    from PySide6.QtWidgets import QApplication, QProgressBar
    from app import Controller, Settings
    from qt_test_support import cleanup_qt_widgets

    class LanguageTests(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.qt = QApplication.instance() or QApplication([])

        def setUp(self):
            set_language('ko')
            self.addCleanup(set_language, 'ko')
            self.addCleanup(cleanup_qt_widgets, self)
            self.folder = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / 'work')
            self.addCleanup(self.folder.cleanup)
            self.c = Controller(Settings(self.folder.name), start_worker=False, start_usage=False)
            self.addCleanup(self.c.close)

        def test_switch_updates_open_event_notice_and_preserves_originals(self):
            event = {'id':'language-fixture', 'target':'fixture', 'chat_name':'모델 변경',
                     'kind':'activity', 'activity_type':'assigned', 'role':'build',
                     'before':{'model':'gpt-6.1-sol','effort':'medium'},
                     'after':{'model':'gpt-6-astra','effort':'high'},
                     'reason':'선택 이유: 원문 이유를 유지합니다.', 'task_summary':'원문 작업 설명'}
            original = copy.deepcopy(event)
            self.c.receive(event)
            self.c.window.history.setCurrentRow(0)
            notice = self.c.notice
            remaining = notice.timer.remainingTime()
            self.c.set_language('en')
            self.assertEqual(self.c.window.tabs.tabText(0), 'Change history')
            self.assertEqual(self.c.window.chat_title.text(), '모델 변경')
            self.assertEqual(self.c.window.task_value.text(), '원문 작업 설명')
            self.assertIn('원문 이유를 유지합니다.', self.c.window.selection_reason.text())
            self.assertIn('Previous model', notice.model_previous.text())
            self.assertIn('Medium (medium)', notice.effort_previous.text())
            self.assertLessEqual(notice.timer.remainingTime(), remaining)
            self.assertEqual(event, original)
            self.assertEqual(self.c.window.history.item(0).data(256), original)
            self.c.set_language('ko')
            self.assertEqual(self.c.window.tabs.tabText(0), '변경 기록')
            self.assertIn('이전 모델', notice.model_previous.text())

        def test_saved_language_and_menu_and_usage_weather(self):
            snapshot = {'rows':[{'bucket':'codex','period':'5시간','remaining':37.5,'resets_at':None}],
                        'status':'조회 완료','stale':False,'busy':False,'checked_at':1234567890}
            self.c.usage.snapshot = copy.deepcopy(snapshot)
            self.c.update_usage(snapshot)
            self.c.set_language('en')
            self.assertEqual(Settings(self.folder.name).values['language'], 'en')
            self.assertIn('37.5% remaining', self.c.window.usage_values.text())
            bars = self.c.window.usage_rows.findChildren(QProgressBar)
            self.assertEqual(bars[-1].value(), 375000)
            self.assertEqual(self.c.usage.snapshot, snapshot)
            self.c.update_weather({'temperature':None,'stale':True,'busy':True,'status':'기온 조회 중'})
            self.assertEqual(self.c.orbit.weather_text, 'Loading temperature')
            menu = self.c.orbit.create_menu()
            submenu = next(action.menu() for action in menu.actions() if action.menu())
            self.assertEqual([action.text() for action in submenu.actions()], ['한국어','English'])
            self.assertEqual(get_language(), 'en')
            self.c.set_language('unsupported')
            self.assertEqual(get_language(), 'ko')

        def test_formatting_and_unknown_text_are_safe(self):
            set_language('en')
            self.assertEqual(translate('잔량 {percent}% ', percent=12), 'Remaining 12% ')
            self.assertEqual(translate('원문 작업 {literal}'), '원문 작업 {literal}')
            self.assertEqual(translate('gpt-6.1-sol'), 'gpt-6.1-sol')

        def test_selector_and_menu_apply_then_reload_the_saved_language(self):
            self.c.window.language_combo.setCurrentIndex(1)
            self.assertEqual(get_language(), 'en')
            self.assertEqual(self.c.window.tabs.tabText(1), 'Usage limits')
            self.c.close()
            self.c = Controller(Settings(self.folder.name), start_worker=False, start_usage=False)
            self.addCleanup(self.c.close)
            self.assertEqual(self.c.window.language_combo.currentData(), 'en')
            self.assertEqual(self.c.window.tabs.tabText(0), 'Change history')
            menu = self.c.orbit.create_menu()
            submenu = next(action.menu() for action in menu.actions() if action.menu())
            submenu.actions()[0].trigger()
            self.assertEqual(get_language(), 'ko')
            self.assertEqual(self.c.window.tabs.tabText(1), '사용 한도')
            self.assertEqual(Settings(self.folder.name).values['language'], 'ko')

        def test_canvas_names_and_actual_fraction_at_both_sizes(self):
            from calendar_catalog import OBJECTS
            from calendar_art import design_for_date
            from datetime import date
            from PySide6.QtGui import QImage, QPainter
            from visuals import draw_desktop_orbit
            set_language('en')
            for subject in OBJECTS.values():
                self.assertFalse(any('가' <= letter <= '힣' for letter in translate(subject.name)))
            self.assertEqual(translate('달리아'), 'Dahlia')
            for width, height in ((180,250),(220,332)):
                image = QImage(width,height,QImage.Format.Format_ARGB32_Premultiplied)
                image.fill(0)
                source = QImage(32,32,QImage.Format.Format_ARGB32_Premultiplied)
                source.fill(0)
                painter = QPainter(image)
                layout = draw_desktop_orbit(painter,width,height,source,design_for_date(date(2026,10,30)),
                                             .375,'fresh','12:34:56','Temperature unknown','Fixture region')
                painter.end()
                self.assertAlmostEqual(layout['fill'].width()/layout['track'].width(), .375)
                self.assertTrue(all(not any('가' <= c <= '힣' for c in line) for line in layout['lines']))
                self.assertLessEqual(layout['dock'].bottom(), layout['location'].top())
                self.assertLessEqual(layout['location'].bottom(), layout['weather'].top())
                self.assertLessEqual(layout['weather'].bottom(), layout['usage'].top())

        def test_status_is_translated_without_mutating_backend_snapshot(self):
            status = {'state':'감시 중','time':'2026-10-30T03:00:00Z'}
            self.c.status(status)
            self.c.set_language('en')
            self.assertIn('Monitoring', self.c.window.summary.text())
            self.assertTrue(self.c.orbit.healthy)
            self.assertEqual(status['state'], '감시 중')
            weather = {'temperature':18.5,'region':'Fixture region','region_original':'Fixture original',
                       'status':'기온 제공 자료 지연 · 이전 값','stale':True,'busy':False,
                       'region_source':'ipwho.is · 지역 번역 실패 · 원문 보존'}
            original = copy.deepcopy(weather)
            self.c.update_weather(weather)
            self.assertEqual(self.c.orbit.weather_text, 'Previous 18.5℃')
            self.assertIn('translation unavailable', self.c.orbit.weather_tooltip)
            self.assertIn('Fixture original', self.c.orbit.weather_tooltip)
            self.assertEqual(weather, original)
            for _ in range(3):
                self.c.orbit.refresh_tooltip()
            self.assertEqual(self.c.orbit.toolTip().count('Monitor status:'), 1)

        def test_language_switch_hides_replaced_usage_rows_immediately(self):
            self.c.usage.snapshot = {'rows':[{'bucket':'codex','period':'5시간','remaining':37.5,'resets_at':None}],
                                     'status':'조회 완료','stale':False,'busy':False,'checked_at':1234567890}
            self.c.update_usage(self.c.usage.snapshot)
            self.c.window.tabs.setCurrentIndex(1)
            self.c.window.show()
            self.qt.processEvents()
            layout = self.c.window.usage_rows_layout
            previous_rows = [layout.itemAt(index).widget() for index in range(1,layout.count())
                             if layout.itemAt(index).widget() is not None]
            self.assertTrue(any(widget.isVisible() for widget in previous_rows))
            self.c.set_language('en')
            self.assertTrue(all(widget.isHidden() for widget in previous_rows),
                            '지연 삭제 이전에도 이전 언어 행이 새 행과 겹쳐 보이면 안 됩니다.')

        def test_usage_smoke_matches_current_language_without_weakening_real_values(self):
            from app import usage_smoke_state
            snapshot = {'rows':[{'bucket':'codex','period':'5시간','remaining':37.5,'resets_at':None},
                                {'bucket':'codex','period':'주간','remaining':None,'resets_at':None}],
                        'status':'조회 완료','stale':False,'busy':False,'checked_at':1234567890}
            self.c.usage.snapshot = copy.deepcopy(snapshot)
            self.c.window.tabs.setCurrentIndex(1)
            self.c.window.show()
            for language, expected_labels in (('ko',['37.5% 남음','잔량 미확인']),
                                               ('en',['37.5% remaining','Usage unknown'])):
                with self.subTest(language=language):
                    self.c.set_language(language)
                    self.qt.processEvents()
                    value, presented, ok = usage_smoke_state(self.c)
                    self.assertEqual(value, snapshot)
                    self.assertEqual(presented['badge'], '37.5%')
                    self.assertEqual(presented['fraction'], .375)
                    self.assertEqual(presented['state'], 'fresh')
                    self.assertEqual(presented['bar_values'], [375000,0])
                    self.assertEqual(presented['remaining_labels'], expected_labels)
                    self.assertTrue(ok, '정상 계정 표시를 선택 언어 때문에 실패시키면 안 됩니다.')
                    self.c.orbit.usage_fraction = .5
                    self.assertFalse(usage_smoke_state(self.c)[2], '실제 비율 불일치는 계속 거부해야 합니다.')
                    self.c.orbit.usage_fraction = .375
                    self.c.usage.snapshot = {**snapshot,'busy':True}
                    self.assertFalse(usage_smoke_state(self.c)[2], '진행 중 조회를 최신 완료로 인정하면 안 됩니다.')
                    self.c.usage.snapshot = {**snapshot,'stale':True}
                    self.assertFalse(usage_smoke_state(self.c)[2], '오래된 값은 최신값으로 인정하면 안 됩니다.')
                    self.c.usage.snapshot = copy.deepcopy(snapshot)

        def test_empty_history_guidance_switches_but_custom_content_is_preserved(self):
            korean = ('변경을 감지하면 이곳에서 전후 값과 공개 이유를 확인할 수 있습니다.\n'
                      '첫 실행은 과거 기록을 기준선으로 읽으며 과거 알림을 만들지 않습니다.')
            english = ('Changes show before / after values and public explanations here.\n'
                       'Existing records form the initial baseline without historical notifications.')
            self.assertEqual(self.c.window.history.count(), 0)
            self.assertEqual(self.c.window.detail.toPlainText(), korean)
            self.c.set_language('en')
            self.assertEqual(self.c.window.detail.toPlainText(), english)
            self.c.set_language('ko')
            self.assertEqual(self.c.window.detail.toPlainText(), korean)
            original = '사용자 원문: 모델 변경 · 실제 작업 내용'
            self.c.window.detail.setPlainText(original)
            self.c.set_language('en')
            self.assertEqual(self.c.window.detail.toPlainText(), original)
