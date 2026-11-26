"""37차 알림센터: 관측 기록 사본을 탐색하고 허용 필드만 내보냅니다."""
from collections import OrderedDict
from copy import deepcopy
import csv
from datetime import datetime, timedelta
import io
import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFileDialog,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QScrollArea, QSpinBox, QTabWidget, QVBoxLayout, QWidget, QFrame, QGridLayout, QSizePolicy, QLayout)
from i18n import get_language
from orbit_features import changed_fields
from ui_layout import OrbitComboBox as QComboBox, ResponsiveRow


def tr(ko, en):
    return en if get_language() == 'en' else ko


def event_time(event):
    for key in ('source_time', 'time'):
        try:
            value = datetime.fromisoformat(str(event.get(key, '')).replace('Z', '+00:00'))
            if value.tzinfo is not None:
                return value.astimezone()
        except (ValueError, TypeError, OverflowError):
            pass
    return None


def title(event):
    return str(event.get('chat_name') or event.get('chat_title') or event.get('title') or tr('제목 미확인', 'Title unavailable'))


def filter_events(events, query='', kind='all', period='all', bookmarked=False,
                  pinned=False, bookmarks=(), pins=(), oldest=False, now=None):
    """원문 전후값을 비교하며 시간 미확인 기록은 날짜 필터에서 제외합니다."""
    now = now or datetime.now().astimezone()
    query = query.casefold().strip()
    result = []
    for event in events:
        fields = changed_fields(event)
        if kind in ('model', 'effort') and kind not in fields:
            continue
        if kind == 'resumed' and event.get('activity_type') != 'resumed':
            continue
        if bookmarked and event.get('id') not in bookmarks:
            continue
        if pinned and event.get('target') not in pins:
            continue
        stamp = event_time(event)
        if period == 'today' and (stamp is None or stamp.date() != now.date()):
            continue
        if period == 'week' and (stamp is None or not now - timedelta(days=7) <= stamp <= now):
            continue
        searchable = [title(event), event.get('reason', ''), event.get('task_summary', ''), event.get('task_name', '')]
        for state in ('before', 'after'):
            value = event.get(state)
            if isinstance(value, dict):
                searchable.extend((value.get('model', ''), value.get('effort', '')))
        if query and query not in ' '.join(map(str, searchable)).casefold():
            continue
        result.append(deepcopy(event))
    result.sort(key=lambda event: event_time(event).timestamp() if event_time(event) else float('-inf'), reverse=not oldest)
    return result


def group_events(events):
    """그룹에는 개수와 원본 기록만 보관하고 전후값을 합성하지 않습니다."""
    groups = OrderedDict()
    for event in events:
        groups.setdefault(event.get('target', ''), []).append(deepcopy(event))
    return groups


EXPORT_FIELDS = ('time', 'kind', 'title', 'previous_model', 'model', 'previous_effort', 'effort', 'reason', 'task')


def export_rows(events, private=False):
    """대화 본문·위치·경로·식별자는 출력 필드에 포함하지 않습니다."""
    rows = []
    for event in events:
        before = event.get('before') if isinstance(event.get('before'), dict) else {}
        after = event.get('after') if isinstance(event.get('after'), dict) else {}
        row = dict(zip(EXPORT_FIELDS, (event.get('source_time') or event.get('time', ''),
            event.get('kind', ''), title(event), before.get('model', ''), after.get('model', ''),
            before.get('effort', ''), after.get('effort', ''), event.get('reason', ''),
            event.get('task_summary') or event.get('task_name', ''))))
        if private:
            for key in ('title', 'reason', 'task'):
                row[key] = tr('비공개', 'Private')
        rows.append({key: str(value) if value is not None else '' for key, value in row.items()})
    return rows


def csv_text(events, private=False):
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=EXPORT_FIELDS)
    writer.writeheader()
    for row in export_rows(events, private):
        # 공백 뒤 수식과 탭·개행 시작도 스프레드시트 실행에서 차단합니다.
        writer.writerow({key: "'" + value if value.startswith(('\t', '\r', '\n')) or value.lstrip().startswith(('=', '+', '-', '@')) else value
                         for key, value in row.items()})
    return output.getvalue()


def summary_text(event, private=False):
    row = export_rows([event], private)[0]
    labels = (('시각', 'Time'), ('종류', 'Kind'), ('채팅 제목', 'Chat title'),
              ('이전 모델', 'Previous model'), ('현재 모델', 'Current model'),
              ('이전 추론 강도', 'Previous effort'), ('현재 추론 강도', 'Current effort'),
              ('이유 원문', 'Original reason'), ('작업', 'Task'))
    missing = tr('확인 불가', 'Unavailable')
    return '\n'.join(f'{tr(*label)}: {row[key] or missing}' for key, label in zip(EXPORT_FIELDS, labels))


class WorkspaceComparison(QFrame):
    """좁은 미리보기에서는 이전·현재를 위아래로 배치해 정확한 값을 보존합니다."""
    def __init__(self,callback):
        super().__init__();self.callback=callback
    def resizeEvent(self,event):
        super().resizeEvent(event);self.callback()


class WorkspacePanel(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._rows = []
        self._texts = []
        outer = QVBoxLayout(self)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)
        body = QWidget()
        body.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
        scroll.setWidget(body)
        layout = QVBoxLayout(body)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
        layout.addWidget(self.tabs)
        history = QWidget()
        settings = QWidget()
        self.tabs.addTab(history, '')
        self.tabs.addTab(settings, '')
        history_layout = QVBoxLayout(history)
        self.search = QLineEdit()
        history_layout.addWidget(self.search)
        self.search.textChanged.connect(self.refresh)
        self._button(history_layout, '검색 초기화', 'Reset search', self._reset)
        self.kind = QComboBox()
        self.period = QComboBox()
        self.order = QComboBox()
        for combo in (self.kind, self.period, self.order):
            combo.currentIndexChanged.connect(self.refresh)
        history_layout.addWidget(ResponsiveRow([self.kind, self.period, self.order]))
        self.bookmarked = self._check(history_layout, '보관 기록만', 'Bookmarked records', self.refresh)
        self.pinned = self._check(history_layout, '관심 채팅만', 'Pinned chats', self.refresh)
        self.grouped = self._check(history_layout, '채팅별 묶음', 'Group by chat', self.refresh)
        history_layout.addWidget(ResponsiveRow([self.bookmarked, self.pinned, self.grouped]))
        self.count = QLabel()
        history_layout.addWidget(self.count)
        from observatory_panel import WrappedAgents
        self.records = WrappedAgents()
        self.records.setWordWrap(True)
        self.records.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.records.setMinimumHeight(160)
        history_layout.addWidget(self.records)
        self.records.currentItemChanged.connect(self._select)
        from app import NoticeValue, notice_symbol
        from theme import set_ui_style
        self.comparison=WorkspaceComparison(self._fit_comparison);self.comparison.setObjectName('noticeComparison')
        set_ui_style(self.comparison,'QFrame#noticeComparison {background:#edf8f2;border:1px solid #c4dfd0;border-radius:10px;}')
        grid=QGridLayout(self.comparison);self.comparison_grid=grid;grid.setContentsMargins(10,10,10,10);grid.setSpacing(8)
        self.comparison_previous=QLabel();self.comparison_current=QLabel()
        self.comparison_model=QLabel();self.comparison_effort=QLabel()
        arrow=QLabel();self.comparison_arrow=arrow;arrow.setPixmap(notice_symbol('arrow',16))
        grid.addWidget(self.comparison_previous,0,1);grid.addWidget(arrow,0,2);grid.addWidget(self.comparison_current,0,3)
        self.model_previous=NoticeValue();self.model_current=NoticeValue()
        self.effort_previous=NoticeValue();self.effort_current=NoticeValue()
        for row,caption,previous,current in [(1,self.comparison_model,self.model_previous,self.model_current),(2,self.comparison_effort,self.effort_previous,self.effort_current)]:
            caption.setWordWrap(True);caption.setMaximumWidth(68);grid.addWidget(caption,row,0)
            for column,label in [(1,previous),(3,current)]:
                label.setWordWrap(True);label.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Minimum)
                label.setTextFormat(Qt.TextFormat.PlainText);grid.addWidget(label,row,column)
        grid.setColumnStretch(1,1);grid.setColumnStretch(3,1)
        self.comparison_model_current=QLabel();self.comparison_effort_current=QLabel()
        for label in (self.comparison_model_current,self.comparison_effort_current):label.setWordWrap(True);label.setMaximumWidth(68)
        self.comparison_columns=None
        history_layout.addWidget(self.comparison)
        self.detail = QLabel()
        self.detail.setTextFormat(Qt.TextFormat.PlainText)
        self.detail.setWordWrap(True)
        self.detail.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        history_layout.addWidget(self.detail)
        self.selection_buttons = []
        for ko, en, call in (
            ('선택 요약 복사', 'Copy summary', self._copy),
            ('알림 다시 보기', 'Replay notification', lambda: self._event_action('replay_event')),
            ('전체 설명·근거 보기', 'Full details', lambda: self._event_action('show')),
            ('선택 채팅 30분 무음', 'Mute chat: 30 min', self._mute)):
            self.selection_buttons.append(self._button(history_layout, ko, en, call))
        history_layout.addWidget(ResponsiveRow(self.selection_buttons))
        self._button(history_layout, '현재 결과 CSV 저장', 'Save filtered CSV', lambda: self._export('csv'))
        self._button(history_layout, '현재 결과 JSON 저장', 'Save filtered JSON', lambda: self._export('json'))
        policy_layout = QVBoxLayout(settings)
        form = QFormLayout()
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        policy_layout.addLayout(form)
        self.option_controls = {}
        for key, low, high, ko, en in (
            ('notice_duration_seconds', 5, 120, '알림 표시 시간(초)', 'Notification duration (seconds)'),
            ('visible_limit', 1, 8, '동시 표시 개수', 'Visible notification limit')):
            spin = QSpinBox()
            spin.setRange(low, high)
            label = QLabel()
            label.setWordWrap(True)
            self._texts.append((label, ko, en))
            form.addRow(label, spin)
            spin.valueChanged.connect(lambda value, name=key: self._set_option(name, value))
            self.option_controls[key] = spin
        for key, ko, en in (('activity_popup', '작업 알림 표시', 'Activity alerts'),
                            ('compact_activity', '작업 알림 간결하게', 'Compact activity alerts'),
                            ('sound', '알림음', 'Notification sound')):
            self.option_controls[key] = self._check(policy_layout, ko, en, lambda value, name=key: self._set_option(name, value))
        for minutes in (15, 30, 60):
            self._button(policy_layout, f'{minutes}분 집중', f'Focus for {minutes} minutes', lambda checked=False, value=minutes: self._policy('focus', value))
        self._button(policy_layout, '알림 다시 받기', 'Resume notifications', lambda: self._policy('resume'))
        self._button(policy_layout, '모든 무음 해제', 'Clear all chat mutes', lambda: self._policy('clear_mutes'))
        for kind, ko, en in (('model', '모델 알림 미리보기', 'Preview model notification'),
                             ('effort', '추론 알림 미리보기', 'Preview effort notification'),
                             ('activity', '작업 알림 미리보기', 'Preview activity notification')):
            self._button(policy_layout, ko, en, lambda checked=False, value=kind: controller.preview_notice37(value))
        self._button(policy_layout, '고정하지 않은 알림 모두 닫기', 'Close unpinned alerts', controller.dismiss_unpinned37)
        self.policy_summary = QLabel()
        self.policy_summary.setTextFormat(Qt.TextFormat.PlainText)
        self.policy_summary.setWordWrap(True)
        policy_layout.addWidget(self.policy_summary)
        policy_layout.addStretch()
        self.retranslate()

    def _button(self, layout, ko, en, callback):
        button = QPushButton()
        self._texts.append((button, ko, en))
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button

    def _check(self, layout, ko, en, callback):
        check = QCheckBox()
        self._texts.append((check, ko, en))
        check.toggled.connect(callback)
        layout.addWidget(check)
        return check

    def _private(self):
        return bool(self.controller.settings.values.get('broadcast_mode', False))

    def _reset(self):
        self.search.clear()
        for combo in (self.kind, self.period, self.order):
            combo.setCurrentIndex(0)
        for check in (self.bookmarked, self.pinned):
            check.setChecked(False)
        self.refresh()

    def refresh(self, *unused):
        current = self.records.currentItem()
        identity = current.data(Qt.ItemDataRole.UserRole) if current else None
        features = self.controller.features
        events = features.snapshot()['events']
        signature = (self.search.text(), self.kind.currentData(), self.period.currentData(),
                     self.bookmarked.isChecked(), self.pinned.isChecked(), self.grouped.isChecked(),
                     self.order.currentData(), self._private(), get_language(), tuple(sorted(features.pins)),
                     tuple(sorted(features.bookmarks)), json.dumps(events, sort_keys=True, ensure_ascii=False, default=str))
        if getattr(self, '_history_signature37', None) == signature:
            self._sync_policy()
            return
        self._history_signature37 = signature
        self._rows = filter_events(events, self.search.text(), self.kind.currentData() or 'all',
            self.period.currentData() or 'all', self.bookmarked.isChecked(), self.pinned.isChecked(),
            features.bookmarks, features.pins, self.order.currentData() == 'oldest')[:500]
        self.records.blockSignals(True)
        self.records.clear()
        groups = group_events(self._rows) if self.grouped.isChecked() else {'': self._rows}
        chosen = None
        for target, rows in groups.items():
            if self.grouped.isChecked():
                header = QListWidgetItem(f'{tr("비공개", "Private") if self._private() else title(rows[0])} · {len(rows)} {tr("건", "records")}')
                header.setFlags(Qt.ItemFlag.NoItemFlags)
                # 그룹 헤더는 별도 항목을 늘리지 않고 첫 기록의 표시 접두사로 사용합니다.
                prefix = header.text() + '\n'
            else:
                prefix = ''
            for index, event in enumerate(rows):
                row = export_rows([event], self._private())[0]
                item = QListWidgetItem((prefix if index == 0 else '') + f'{row["time"]} · {row["title"]}\n{row["previous_model"] or "?"} → {row["model"] or "?"} · {row["previous_effort"] or "?"} → {row["effort"] or "?"}')
                item.setData(Qt.ItemDataRole.UserRole, event.get('id'))
                self.records.addItem(item)
                if event.get('id') == identity:
                    chosen = item
        self.records.setCurrentItem(chosen or self.records.item(0))
        self.records.blockSignals(False)
        self.records.fit_rows()
        self.count.setText(f'{len(self._rows)} {tr("건", "records")}' + ('' if self._rows else ' · ' + tr('검색 결과가 없습니다. 필터를 바꿔 주세요.', 'No results. Change the filters.')))
        self._select()
        self._sync_policy()

    def _selected(self):
        item = self.records.currentItem()
        identity = item.data(Qt.ItemDataRole.UserRole) if item else None
        return next((event for event in self._rows if event.get('id') == identity), None)

    def _select(self, *unused):
        event = self._selected()
        from observatory_panel import present_event
        from app import display_notice_comparison
        from notice_format import notice_reason
        shown=present_event(event,self._private()) if event else None
        self.comparison_previous.setText(tr('이전','Previous'));self.comparison_current.setText(tr('현재','Current'))
        for label in (self.comparison_model,self.comparison_model_current):label.setText(tr('모델','Model'))
        for label in (self.comparison_effort,self.comparison_effort_current):
            label.setText(tr('추론 강도','Effort'));label.setAccessibleName(tr('추론 강도','Reasoning effort'))
        self.comparison.setVisible(shown is not None)
        if shown:display_notice_comparison(self,shown)
        self._fit_comparison()
        self.detail.setText(title(shown)+'\n'+tr('이유: ','Reason: ')+notice_reason(shown,140,max_sentences=1) if shown else tr('기록을 선택하면 이전·현재 값과 이유가 표시됩니다.','Select a record to compare values and read its reason.'))
        for button in self.selection_buttons:
            button.setEnabled(event is not None)

    def _fit_comparison(self):
        if not hasattr(self,'comparison_columns'):return
        values=(self.model_previous,self.model_current,self.effort_previous,self.effort_current)
        value_width=max(label.fontMetrics().horizontalAdvance(label.text())+label.contentsMargins().left()+16 for label in values)
        columns=2 if self.comparison.width()>=2*value_width+116 else 1
        if columns==self.comparison_columns:return
        self.comparison_columns=columns;grid=self.comparison_grid
        while grid.count():grid.takeAt(0)
        self.comparison_arrow.setVisible(columns==2)
        for label in (self.comparison_model_current,self.comparison_effort_current):label.setVisible(columns==1)
        if columns==2:
            for widget,row,column in [(self.comparison_previous,0,1),(self.comparison_arrow,0,2),(self.comparison_current,0,3),
                (self.comparison_model,1,0),(self.model_previous,1,1),(self.model_current,1,3),
                (self.comparison_effort,2,0),(self.effort_previous,2,1),(self.effort_current,2,3)]:grid.addWidget(widget,row,column)
        else:
            for offset,heading,model_caption,effort_caption,model,effort in [
                (0,self.comparison_previous,self.comparison_model,self.comparison_effort,self.model_previous,self.effort_previous),
                (3,self.comparison_current,self.comparison_model_current,self.comparison_effort_current,self.model_current,self.effort_current)]:
                grid.addWidget(heading,offset,1,1,3)
                grid.addWidget(model_caption,offset+1,0);grid.addWidget(model,offset+1,1,1,3)
                grid.addWidget(effort_caption,offset+2,0);grid.addWidget(effort,offset+2,1,1,3)

    def _copy(self):
        event = self._selected()
        if event:
            QApplication.clipboard().setText(summary_text(event, self._private()))

    def _event_action(self, method):
        event = self._selected()
        if event:
            getattr(self.controller, method)(event['id'])

    def _sync_policy(self):
        policy = self.controller.workspace_policy
        for key, control in self.option_controls.items():
            control.blockSignals(True)
            value = policy.options.get(key, 5 if key == 'notice_duration_seconds' else 1 if key == 'visible_limit' else False)
            control.setChecked(bool(value)) if isinstance(control, QCheckBox) else control.setValue(value)
            control.blockSignals(False)
        self.policy_summary.setText(str(policy.summary()))

    def _error(self, error):
        box = QMessageBox(QMessageBox.Icon.Warning, tr('저장 실패', 'Save failed'), tr('변경을 저장하지 못했습니다. 현재 설정을 복원합니다.', 'Could not save the change. Restoring current settings.'), parent=self)
        box.setTextFormat(Qt.TextFormat.PlainText)
        box.exec()

    def _set_option(self, key, value):
        self._policy('set_options', **{key: value})

    def _policy(self, method, *args, **kwargs):
        try:
            getattr(self.controller.workspace_policy, method)(*args, **kwargs)
        except (OSError, ValueError, TypeError, RuntimeError) as error:
            self._error(error)
        self._sync_policy()

    def _mute(self):
        event = self._selected()
        if event:
            self._policy('mute_target', event['target'], minutes=30)

    def _export(self, kind):
        path, _ = QFileDialog.getSaveFileName(self, tr('현재 필터 결과 저장', 'Save filtered records'),
            f'orbit-records.{kind}', f'{kind.upper()} (*.{kind})', options=QFileDialog.Option.DontUseNativeDialog)
        if not path:
            return
        try:
            text = csv_text(self._rows, self._private()) if kind == 'csv' else json.dumps(export_rows(self._rows, self._private()), ensure_ascii=False, indent=2)
            with open(path, 'w', encoding='utf-8', newline='') as stream:
                stream.write(text)
        except (OSError, ValueError, TypeError) as error:
            self._error(error)

    def retranslate(self):
        self._display_language=get_language()
        for widget, ko, en in self._texts:
            widget.setText(tr(ko, en))
        self.tabs.setTabText(0, tr('기록 탐색', 'History explorer'))
        self.tabs.setTabText(1, tr('알림 설정', 'Notification settings'))
        self.search.setPlaceholderText(tr('제목·모델·이유·작업 통합 검색', 'Search title, model, reason and task'))
        for combo, values in ((self.kind, [('all', '모든 종류', 'All kinds'), ('model', '모델 변경', 'Model changes'), ('effort', '추론 강도 변경', 'Effort changes'), ('resumed', '작업 재개', 'Resumed tasks')]),
                              (self.period, [('all', '전체 기간', 'All dates'), ('today', '오늘', 'Today'), ('week', '최근 7일', 'Last 7 days')]),
                              (self.order, [('newest', '최신순', 'Newest first'), ('oldest', '오래된순', 'Oldest first')])):
            selected = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            for value, ko, en in values:
                combo.addItem(tr(ko, en), value)
            combo.setCurrentIndex(max(0, combo.findData(selected)))
            combo.blockSignals(False)
        self.refresh()

    def showEvent(self,event):
        super().showEvent(event)
        # 숨겨 둔 알림센터도 언어 선택 후 처음 열 때 같은 언어로 갱신합니다.
        if getattr(self,'_display_language',None)!=get_language():self.retranslate()
