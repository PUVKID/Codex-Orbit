"""28차 알림의 여섯 필드·이모지·공개 근거 보존을 실제 화면에서 검사합니다."""
import copy
import os
from pathlib import Path
import sys
import tempfile
import unittest
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtWidgets import QApplication
import app
from i18n import set_language
from qt_test_support import cleanup_qt_widgets

class SimpleNoticeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])
    def setUp(self):
        set_language('ko')
        self.addCleanup(set_language, 'ko')
        self.addCleanup(cleanup_qt_widgets, self)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.c = app.Controller(app.Settings(folder.name), start_worker=False, start_usage=False)
        self.addCleanup(self.c.close)
    def event(self, **extra):
        return {'id':'simple28','target':'fixture','chat_name':'합성 알림 검토',
                'before':{'model':'gpt-6.1-sol','effort':'medium'},
                'after':{'model':'gpt-6.1-terra','effort':'high'},
                'reason':'화면의 글자 겹침을 확인해 UI 수정을 맡깁니다.', **extra}
    def test_effort_mapping_preserves_all_seven_raw_values_in_both_languages(self):
        cases=[('none','⚪','없음','None'),('minimal','💧','최소','Minimal'),('low','🌱','낮음','Low'),
               ('medium','⚖️','보통','Medium'),('high','🔥','높음','High'),('xhigh','🚀','매우 높음','Very high'),('ultra','⚡','최고','Maximum')]
        for language in ('ko','en'):
            set_language(language)
            for raw,emoji,korean,english in cases:
                with self.subTest(language=language,raw=raw):
                    self.assertEqual(app.friendly_effort(raw),f'{korean if language=="ko" else english} ({raw}) {emoji}')

    def test_effort_icons_reach_existing_windows_and_all_notice_kinds(self):
        cases=[('none','⚪'),('minimal','💧'),('low','🌱'),('medium','⚖️'),('high','🔥'),('xhigh','🚀'),('ultra','⚡')]
        kinds=({}, {'kind':'settings'}, {'kind':'activity','activity_type':'assigned'}, {'kind':'activity','activity_type':'resumed'})
        for language in ('ko','en'):
            self.c.set_language(language)
            for index,extra in enumerate(kinds):
                before,before_icon=cases[index];current,current_icon=cases[index+3]
                event=self.event(id=language+str(index),before={'model':'gpt-6.1-sol','effort':before},after={'model':'gpt-6.1-terra','effort':current},**extra)
                original=copy.deepcopy(event);self.c.receive(event)
                for surface in (self.c.notice,self.c.window):
                    self.assertIn(before_icon,surface.effort_previous.text())
                    self.assertIn('('+before+')',surface.effort_previous.text())
                    self.assertIn(current_icon,surface.effort_current.text())
                    self.assertIn('('+current+')',surface.effort_current.text())
                self.assertTrue(self.c.replay_event(event['id']))
                self.assertIn(current_icon,self.c.notice.effort_current.text())
                self.assertEqual(event,original)

    def test_effort_unknown_icon_never_turns_missing_record_into_none_effort(self):
        self.assertEqual(app.previous_field(None,'effort'),'이전 기록 없음 ❔')
        self.assertEqual(app.previous_field({},'effort'),'확인 불가 ❔')
        self.assertEqual(app.friendly_effort(None),'미확인 ❔')
        self.assertEqual(app.friendly_effort('future-effort'),'future-effort ❔')
        self.assertEqual(app.previous_field(None,'model'),'이전 기록 없음')
        for before in (None,{}):
            self.c.receive(self.event(id=str(before),before=before,after={'model':'gpt-6.1-terra'}))
            for surface in (self.c.notice,self.c.window):
                self.assertIn('❔',surface.effort_previous.text())
                self.assertIn('❔',surface.effort_current.text())
                self.assertNotIn('(none)',surface.effort_previous.text()+surface.effort_current.text())

    def test_each_model_family_and_unknown_keeps_exact_id(self):
        self.assertTrue(hasattr(app, 'notice_model_label'))
        for model, emoji in [('gpt-6.1-sol','☀️'),('gpt-6-astra','✨'),('gpt-6.1-terra','🌍'),('gpt-6-luna','🌙'),('unknown-id','🤖')]:
            with self.subTest(model=model):
                self.assertEqual(app.notice_model_label(model), emoji+' '+model)
    def test_six_fields_and_no_redundant_rows_for_every_kind_and_replay(self):
        for index, extra in enumerate(({}, {'kind':'settings'}, {'kind':'activity','activity_type':'assigned'}, {'kind':'activity','activity_type':'resumed'})):
            event=self.event(id=str(index), **extra); original=copy.deepcopy(event)
            self.c.receive(event); card=self.c.notice
            self.assertEqual(card.title.text(), event['chat_name'])
            for label, heading, content in ((card.model_previous,'이전 모델','☀️ gpt-6.1-sol'),(card.effort_previous,'이전 추론 강도','보통 (medium)'),(card.model_current,'현재 모델','🌍 gpt-6.1-terra'),(card.effort_current,'현재 추론 강도','높음 (high)')):
                self.assertTrue(label.isVisible())
                self.assertIn(heading, label.text())
                self.assertIn(content, label.text())
            for label in (card.task_value,card.after_value,card.selection_reason): self.assertTrue(label.isHidden())
            self.assertTrue(card.text.text().startswith('💬 이유: '))
            self.assertIn('🧠', card.effort_previous.text())
            self.assertIn('🧠', card.effort_current.text())
            self.assertEqual(card.title_marker.text(), '💬')
            self.assertTrue(card.notice_after_heading.text().startswith('➡️'))
            self.assertEqual(event, original)
            self.assertTrue(self.c.replay_event(str(index)))
            self.assertIn('🔁',self.c.notice.category.text())
    def test_assignment_task_is_in_reason_without_invented_selection_motive(self):
        event=self.event(kind='activity',activity_type='assigned',reason='',task_summary='한글 안내문을 다듬습니다.')
        self.c.receive(event)
        self.assertIn('한글 안내문을 다듬습니다.',self.c.notice.text.text())
        self.assertIn('이유가 기록되지 않았습니다.',self.c.notice.text.text())
        self.assertNotIn('적합',self.c.notice.text.text())
    def test_long_reason_is_short_but_full_original_remains_in_tooltip_and_detail(self):
        reason='화면의 글자가 겹쳐 배치를 조정합니다. '+('공개 근거 원문을 유지합니다. '*40)
        self.c.receive(self.event(reason=reason))
        self.assertLessEqual(len(self.c.notice.text.text()), 230)
        self.assertIn(reason,self.c.notice.text.toolTip())
        self.assertIn(reason,self.c.window.detail.toPlainText())
    def test_unknown_previous_and_protected_reason_remain_safe(self):
        for previous,expected in [(None,'이전 기록 없음'),({'model':'gpt-6.1-sol'},'확인 불가')]:
            self.c.receive(self.event(id=str(previous),before=previous,reason='<private>숨긴 값</private>'))
            self.assertIn(expected,self.c.notice.effort_previous.text())
            self.assertNotIn('숨긴 값',self.c.notice.text.text()+self.c.notice.text.toolTip())
    def test_reason_sentinels_are_missing_but_normal_sentences_are_preserved(self):
        for reason in (None, '', '   ', '확인 불가', '확인되지 않음', '<private>비공개</private>'):
            with self.subTest(reason=reason):
                self.c.receive(self.event(id=str(reason), reason=reason))
                self.assertEqual(self.c.notice.text.text(), '💬 이유: 이유가 기록되지 않았습니다.')
        normal='확인 불가 항목을 찾아 안내문에 표시합니다.'
        self.c.receive(self.event(id='normal-reason',reason=normal))
        self.assertIn(normal,self.c.notice.text.text())
        self.assertIn(normal,self.c.notice.text.toolTip())

    def test_queue_growth_keeps_wrapped_value_rows_readable(self):
        self.c.receive(self.event(before=None, after={'model':'m'}))
        card=self.c.notice
        from PySide6.QtCore import QRect
        card.available_rect=QRect(0,0,1000,900)
        card.queue_hint.setText('알림 표시 8건 · 새 변경은 즉시 표시')
        card.fit_content();before=card.height()
        card.queue_hint.setText('알림 표시 8건 · 새 변경은 즉시 표시 · 표시 상한으로 숨긴 1건은 변경 이력에서 확인하세요.')
        card.fit_content()
        self.assertGreater(card.height(),before)
        for label in (card.model_previous,card.model_current,card.effort_previous,card.effort_current,card.text,card.queue_hint):
            with self.subTest(label=label.text()):
                self.assertGreaterEqual(label.height(),label.heightForWidth(label.width()))
                self.assertLessEqual(label.mapTo(card,label.rect().bottomRight()).y(),card.height())
        self.assertEqual(card.title.text(),'합성 알림 검토')

    def test_open_windows_switch_all_headers_fields_and_buttons_both_ways(self):
        from PySide6.QtWidgets import QLabel,QPushButton
        event=self.event();original=copy.deepcopy(event);self.c.receive(event)
        card=self.c.notice;window=self.c.window
        card_identity=id(card);window_identity=id(window)
        for language,previous_header,previous_effort,current_model,current_effort,detail_button,close_button in (
                ('en','⬅️ Previous','Previous reasoning effort 🧠','Current model','Current reasoning effort','🔎 View details','✕ Close'),
                ('ko','⬅️ 이전','이전 추론 강도 🧠','현재 모델','현재 추론 강도','🔎 자세히 보기','✕ 닫기')):
            self.c.set_language(language);self.qt.processEvents()
            self.assertEqual(id(self.c.notice),card_identity)
            self.assertEqual(id(self.c.window),window_identity)
            self.assertIn(previous_header,[label.text() for label in card.findChildren(QLabel)])
            self.assertIn(previous_effort,[label.text() for label in window.card.findChildren(QLabel)])
            self.assertIn(current_model,card.model_current.text())
            self.assertIn(current_effort,card.effort_current.text())
            self.assertTrue(card.model_previous.text().startswith('Previous model' if language=='en' else '이전 모델'))
            self.assertIn(previous_effort,card.effort_previous.text())
            self.assertTrue(card.text.text().startswith('💬 Reason: ' if language=='en' else '💬 이유: '))
            self.assertEqual(card.title_marker.accessibleName(),'Chat title' if language=='en' else '채팅 제목')
            self.assertEqual([label.text() for label,_ in window.after_headings],
                             ['Current Model','Current Reasoning effort 🧠'] if language=='en' else ['현재 모델','현재 추론 강도 🧠'])
            self.assertEqual(card.detail_hint.text(),detail_button)
            self.assertIn(close_button,[button.text() for button in card.findChildren(QPushButton)])
            self.assertEqual(card.title.text(),event['chat_name'])
            self.assertEqual(window.chat_title.text(),event['chat_name'])
            self.assertIn(event['reason'],card.text.toolTip())
            for surface in (card,window):
                self.assertIn('☀️ gpt-6.1-sol',surface.model_previous.text())
                self.assertIn('🌍 gpt-6.1-terra',surface.model_current.text())
                self.assertIn('medium',surface.effort_previous.text())
                self.assertIn('high',surface.effort_current.text())
                self.assertIn('🧠',card.effort_previous.text())
                self.assertIn('🧠',card.effort_current.text())
            self.assertEqual(event,original)

    def test_english_labels_keep_original_title_reason_and_model(self):
        event=self.event();self.c.receive(event);self.c.set_language('en')
        card=self.c.notice
        self.assertIn('Current model',card.model_current.text())
        self.assertIn('Current reasoning effort',card.effort_current.text())
        self.assertIn('High (high)',card.effort_current.text())
        self.assertIn('🌍 gpt-6.1-terra',card.model_current.text())
        self.assertEqual(card.title.text(),event['chat_name'])
        self.assertIn(event['reason'],card.text.toolTip())


class NativeNoticeFormattingTests(unittest.TestCase):
    def setUp(self):
        set_language('ko')
        self.addCleanup(set_language, 'ko')
    def xml(self, event):
        from unittest.mock import patch
        from notifier import NativeToast
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as folder, patch('notifier.powershell', return_value='합성 전달') as send:
            NativeToast(folder)(event)
            root=ET.parse(Path(folder)/'toast.xml').getroot()
            send.assert_called_once()
            return [node.text or '' for node in root.findall('.//text')]
    def event(self, **extra):
        return {'id':'synthetic-toast','chat_name':'정확한 합성 제목','target':'노출하지않는ID',
                'before':{'model':'gpt-6.1-sol','effort':'medium'},
                'after':{'model':'gpt-6-astra','effort':'high'},'reason':'화면을 읽기 쉽게 정리합니다.',**extra}
    def test_all_effort_icons_use_shared_native_toast_mapping(self):
        for language in ('ko','en'):
            set_language(language)
            for raw,emoji in [('none','⚪'),('minimal','💧'),('low','🌱'),('medium','⚖️'),('high','🔥'),('xhigh','🚀'),('ultra','⚡')]:
                with self.subTest(language=language,raw=raw):
                    texts=self.xml(self.event(before={'model':'gpt-6.1-sol','effort':raw},after={'model':'gpt-6-astra','effort':raw}))
                    self.assertEqual(texts[1].count(emoji),2)
                    self.assertEqual(texts[1].count('('+raw+')'),2)

    def test_title_four_fields_and_reason_replace_target_and_evidence(self):
        texts=self.xml(self.event(evidence='원시근거숨김'))
        self.assertEqual(texts[0],'정확한 합성 제목')
        for value in ('이전 모델: ☀️ gpt-6.1-sol','이전 추론 강도: 🧠 보통 (medium)','현재 모델: ✨ gpt-6-astra','현재 추론 강도: 🧠 높음 (high)'):
            self.assertIn(value,texts[1])
        self.assertIn('화면을 읽기 쉽게 정리합니다.',texts[2])
        self.assertNotIn('원시근거숨김',''.join(texts));self.assertNotIn('노출하지않는ID',''.join(texts))
    def test_utf16_budget_preserves_surrogate_pairs_and_xml_escapes(self):
        texts=self.xml(self.event(chat_name='🌍'*100,reason='"문장" & <이유> $(cmd)\x01'+'🌙'*300))
        self.assertLessEqual(len(texts[0].encode('utf-16-le'))//2,64)
        self.assertLessEqual(len('\n'.join(texts[1:]).encode('utf-16-le'))//2,255)
        self.assertNotIn('\x01',''.join(texts))
        self.assertIn('"문장" & <이유> $(cmd)',texts[2])
    def test_missing_protected_and_english_values(self):
        texts=self.xml(self.event(before=None,reason='<private>비공개</private>'))
        self.assertIn('이전 기록 없음',texts[1]);self.assertNotIn('비공개',''.join(texts))
        set_language('en');texts=self.xml(self.event(after={'model':'unknown-model','effort':'low'}))
        self.assertIn('Current model: 🤖 unknown-model',texts[1]);self.assertIn('Low (low)',texts[1])
