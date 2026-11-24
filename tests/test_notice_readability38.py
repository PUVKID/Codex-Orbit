"""알림의 비교 구조와 이유 원문 보존을 확인합니다."""
import os,sys,unittest,copy
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QRect
from app import Notice
from notice_format import notice_reason
from i18n import set_language
from theme import apply_theme
APP=QApplication.instance() or QApplication([])

class NoticeReadability38Tests(unittest.TestCase):
    def event(self,**extra):
        return {'id':'read38','target':'synthetic','chat_name':'합성 화면 확인','kind':'settings',
                'before':{'model':'gpt-6.1-sol','effort':'medium'},'after':{'model':'gpt-6-astra','effort':'high'},
                'reason':'이유: UI에서 글자가 겹쳐 배치를 수정합니다. 회귀 검사를 진행합니다.',**extra}
    def test_comparison_has_explicit_row_labels_and_only_current_change_highlight(self):
        set_language('ko');apply_theme('dark');card=Notice(lambda key:None);self.addCleanup(card.close)
        event=self.event();original=copy.deepcopy(event);card.update_event(event,replay=False)
        self.assertEqual([label.text() for label in card.comparison_labels],['모델','추론 강도'])
        self.assertNotIn('background:#d4f3e7',card.model_previous.property('orbit_style_source'))
        self.assertIn('background:#d4f3e7',card.model_current.property('orbit_style_source'))
        self.assertEqual(event,original)
    def test_unchanged_setting_is_not_styled_as_a_change(self):
        card=Notice(lambda key:None);self.addCleanup(card.close)
        card.update_event(self.event(after={'model':'gpt-6.1-sol','effort':'high'}),replay=False)
        self.assertNotIn('background:#d4f3e7',card.model_current.property('orbit_style_source'))
        self.assertIn('background:#d4f3e7',card.effort_current.property('orbit_style_source'))
    def test_easy_terms_keep_the_original_reason_untouched(self):
        event=self.event(reason='이유: UI 오류를 수정하고 회귀 검사를 진행합니다.')
        original=copy.deepcopy(event);summary=notice_reason(event)
        self.assertIn('기존 기능 확인을',summary);self.assertNotIn('재확인를',summary);self.assertEqual(event,original)
    def test_full_reason_is_accessible_after_short_summary(self):
        set_language('ko');card=Notice(lambda key:None);self.addCleanup(card.close)
        raw='화면의 글자가 겹쳐 배치를 수정합니다. '+('추가 공개 설명입니다. '*25)
        card.update_event(self.event(reason=raw),replay=False);card.show();APP.processEvents()
        self.assertLessEqual(len(card.text.text()),150)
        card.reason_disclosure.click();APP.processEvents();self.assertTrue(card.reason_original.isVisible());self.assertIn(raw,card.reason_original.toPlainText())
    def test_row_labels_translate_and_values_remain_exact(self):
        set_language('en');self.addCleanup(set_language,'ko');card=Notice(lambda key:None);self.addCleanup(card.close)
        card.update_event(self.event(),replay=False)
        self.assertEqual([label.text() for label in card.comparison_labels],['Model','Reasoning effort'])
        self.assertIn('gpt-6.1-sol',card.model_previous.text());self.assertIn('gpt-6-astra',card.model_current.text())
        self.assertIn('(medium)',card.effort_previous.text());self.assertIn('(high)',card.effort_current.text())

    def test_queue_hint_appears_when_the_first_live_count_arrives(self):
        card=Notice(lambda key:None);self.addCleanup(card.close);card.available_rect=QRect(0,0,1200,900)
        card.update_event(self.event(),replay=False);card.show();APP.processEvents()
        self.assertTrue(card.queue_hint.isHidden())
        card.queue_hint.setText('알림 표시 2건');card.fit_content();APP.processEvents()
        self.assertFalse(card.queue_hint.isHidden())
        card.queue_hint.setText('');card.fit_content();APP.processEvents();self.assertTrue(card.queue_hint.isHidden())

    def test_full_explanation_keeps_small_screen_card_and_timer_safe(self):
        set_language('en');self.addCleanup(set_language,'ko')
        card=Notice(lambda key:None);self.addCleanup(card.close)
        card.available_rect=QRect(0,0,700,400)
        card.update_event(self.event(reason='이유: '+('긴 공개 설명입니다. '*100)),replay=False)
        card.apply_text_scale(1.5);card.show();APP.processEvents()
        before=card.size();card.timer.start(30000)
        card.reason_disclosure.click();APP.processEvents()
        self.assertEqual(card.size(),before);self.assertLessEqual(card.height(),400)
        self.assertTrue(card.reason_original.isVisible());self.assertFalse(card.timer.isActive())
        self.assertTrue(card.available_rect.contains(card.reason_dialog.geometry()))
        card.reason_dialog.reject();APP.processEvents()
        self.assertFalse(card.reason_disclosure.isChecked());self.assertFalse(card.reason_dialog.isVisible())
        card.pinned=True;card.reason_disclosure.click();card.reason_dialog.reject();APP.processEvents()
        self.assertFalse(card.timer.isActive())

    def test_full_date_and_clock_split_without_losing_the_year(self):
        from visuals import desktop_widget_layout
        layout=desktop_widget_layout(180,432,'확인',text_scale=1.5,clock_text='12:34:56',calendar_date='2026/11/25')
        self.assertEqual(layout['clock_lines'],['2026/11/25','12:34:56'])

if __name__=='__main__':unittest.main()
