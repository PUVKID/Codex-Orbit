from theme import set_ui_style, themed_stylesheet
"""29차 관측소의 화면 조작과 실제 관측값 연결입니다."""
from copy import deepcopy
from pathlib import Path
import time
from PySide6.QtCore import Qt,QTimer,QSize,QRect
from PySide6.QtGui import QPainter,QColor,QActionGroup
from PySide6.QtWidgets import (QWidget,QFrame,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,
    QListWidget,QListWidgetItem,QSlider,QComboBox,QFileDialog,QMessageBox,QApplication,QStackedWidget,QScrollArea,QSizePolicy,QWidgetAction,QCheckBox,QRadioButton)
from i18n import translate as t,get_language
from typography import app_font
from ui_layout import OrbitComboBox as QComboBox,ResponsiveRow,PageStack as QStackedWidget


def tr(ko,en):
    return en if get_language()=='en' else ko


def present_event(event,private=False):
    """저장 원문은 유지하고 표시 사본만 정리합니다."""
    from orbit_features import clean_chat_title
    if private:
        keys=('id','target','time','before','after','kind','role','activity_type','activity_action')
        value={key:deepcopy(event[key]) for key in keys if key in event}
        value.update(chat_name=tr('비공개 채팅','Private chat'),task_summary='',reason=tr('프라이버시 모드에서 설명을 가렸습니다.','Details hidden in privacy mode.'))
        return value
    value=deepcopy(event)
    for key in ('chat_name','title','chat_title'):
        if key in value:value[key]=clean_chat_title(value[key])
    return value


def pause_notice(notice):
    notice._hover_remaining=notice.timer.remainingTime() if notice.timer.isActive() else getattr(notice,'_hover_remaining',-1)
    notice.timer.stop()


def resume_notice(notice):
    remaining=getattr(notice,'_hover_remaining',-1)
    if remaining>0 and not getattr(notice,'pinned',False):notice.timer.start(remaining)


def mask_details(window):
    """목록·선택 카드·원문·툴팁을 함께 갱신해 기존 열린 정보도 가립니다."""
    from app import history_label
    private=window.controller.settings.values.get('broadcast_mode',False)
    for i in range(window.history.count()):
        item=window.history.item(i);event=item.data(Qt.ItemDataRole.UserRole)
        item.setText(history_label(present_event(event,private)))
        item.setToolTip('')
    window.select_event(window.history.currentItem(),None)
    if private:
        window.diagnostics.hide()
        for child in window.findChildren(QWidget):child.setToolTip('')
    elif window.diagnostics.original_text:window.diagnostics.setPlainText(window.diagnostics.original_text)


def style_notice(notice):
    set_ui_style(notice,'#notice{background:#fbfffe;border:1px solid #bdd8d0;border-radius:18px;} QLabel{background:transparent;color:#193a37;font-weight:700;}')
    notice.title_marker.hide()
    for label in notice.findChildren(QLabel):
        css=label.property('orbit_style_source') or label.styleSheet()
        import re
        css=re.sub(r'color:#[0-9a-fA-F]{3,8}', 'color:#23433f',css)
        css=css.replace('background:#385064','background:#d4f3e7')
        set_ui_style(label,css.replace('font-weight:600','font-weight:700').replace('font-weight:500','font-weight:700'))


class SceneCanvas(QWidget):
    """기존 GPU 작업자의 실제 투명 프레임을 공유합니다."""
    def __init__(self,controller):
        super().__init__();self.controller=controller;self.setMinimumSize(200,180)
        self.setMouseTracking(True);self.setAccessibleName(tr('실시간 입체 관측소','Live 3D observatory'))
    def showEvent(self,event):
        from calendar_motion import set_calendar_motion_visible,set_calendar_motion_size
        set_calendar_motion_visible(self,True);set_calendar_motion_size(self,max(32,min(2160,round(min(self.width(),self.height())*self.devicePixelRatioF()))))
        super().showEvent(event)
    def hideEvent(self,event):
        from calendar_motion import set_calendar_motion_visible
        set_calendar_motion_visible(self,False);super().hideEvent(event)
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if self.isVisible():
            from calendar_motion import set_calendar_motion_size
            set_calendar_motion_size(self,max(32,min(2160,round(min(self.width(),self.height())*self.devicePixelRatioF()))))
    def calendar_frame_ready(self):
        if self.isVisible():self.update()
    def paintEvent(self,event):
        from calendar_motion import get_calendar_frame
        image=get_calendar_frame();p=QPainter(self)
        try:
            if image is not None and not image.isNull():
                side=min(self.width(),self.height());x=(self.width()-side)//2;y=(self.height()-side)//2
                p.drawImage(x,y,image.scaled(side,side,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        finally:
            # 그리기 구간을 벗어나기 전에 모의 호출이 보관한 참조도 비활성화합니다.
            p.end()
    def mouseMoveEvent(self,event):
        self.controller.orbit29.pointer=[event.position().x()/max(1,self.width())*2-1,event.position().y()/max(1,self.height())*2-1]
        self.controller.orbit29.feed_scene()
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            side=min(self.width(),self.height());x=(event.position().x()-(self.width()-side)/2)/side;y=(event.position().y()-(self.height()-side)/2)/side
            self.controller.orbit29.hit(x,y)


class WrappedAgents(QListWidget):
    """긴 이름은 가로 스크롤 없이 전체 행 높이에 맞춰 표시합니다."""
    def resizeEvent(self,event):
        super().resizeEvent(event);self.fit_rows()
    def fit_rows(self):
        width=max(80,self.viewport().width()-28)
        for index in range(self.count()):
            item=self.item(index)
            height=self.fontMetrics().boundingRect(QRect(0,0,width,3000),Qt.TextFlag.TextWordWrap,item.text()).height()
            item.setSizeHint(QSize(0,max(48,height+24)))


class ObservatoryPanel(QFrame):
    def __init__(self,controller):
        super().__init__();self.controller=controller;self.setObjectName('observatoryHero')
        outer=QHBoxLayout(self);outer.setContentsMargins(20,20,20,20);outer.setSpacing(24)
        self.canvas=SceneCanvas(controller);outer.addWidget(self.canvas,2)
        right=QWidget();right.setMinimumWidth(0);right.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Expanding);outer.addWidget(right,3)
        body=QVBoxLayout(right);body.setContentsMargins(0,0,0,0);body.setSpacing(12)
        self.content_scroll=QScrollArea();self.content_scroll.setWidgetResizable(True);self.content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);body.addWidget(self.content_scroll,1)
        content=QWidget();content.setMinimumWidth(0);self.content_scroll.setWidget(content);section=QVBoxLayout(content);section.setContentsMargins(0,0,8,0);section.setSpacing(10)
        self.caption=QLabel(tr('현재 작업','Current activity'));self.caption.setObjectName('sectionCaption');section.addWidget(self.caption)
        self.heading=QLabel();self.heading.setObjectName('currentTask');self.heading.setWordWrap(True);self.heading.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred);set_ui_style(self.heading,'font-size:22px;');section.addWidget(self.heading)
        self.state=QLabel();self.state.setWordWrap(True);self.state.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred);section.addWidget(self.state)
        card=QFrame();card.setObjectName('observationCard');info=QVBoxLayout(card);info.setContentsMargins(14,12,14,12)
        self.observations=QLabel();self.observations.setWordWrap(True);self.observations.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred);info.addWidget(self.observations);section.addWidget(card)
        self.away=QLabel();self.away.setWordWrap(True);self.away.setObjectName('sectionCaption');section.addWidget(self.away)
        self.agents=WrappedAgents();self.agents.setWordWrap(True);self.agents.setTextElideMode(Qt.TextElideMode.ElideRight);self.agents.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);self.agents.setMinimumHeight(100);self.agents.setMaximumHeight(210);section.addWidget(self.agents,1)
        self.agents.itemClicked.connect(self.select_agent)
        row_buttons=[]
        self.pin=QPushButton();self.pin.clicked.connect(self.pin_agent);row_buttons.append(self.pin)
        self.bookmark=QPushButton();self.bookmark.clicked.connect(self.bookmark_event);row_buttons.append(self.bookmark)
        self.copy=QPushButton();self.copy.clicked.connect(self.copy_id);row_buttons.append(self.copy);section.addWidget(ResponsiveRow(row_buttons))
        replay=QFrame();replay.setObjectName('replayBar');controls=QVBoxLayout(replay);controls.setContentsMargins(12,10,12,10);controls.setSpacing(8);body.addWidget(replay)
        self.timeline=QSlider(Qt.Orientation.Horizontal);self.timeline.setAccessibleName(tr('저장 기록 재생','Replay saved history'));self.timeline.valueChanged.connect(self.seek);controls.addWidget(self.timeline)
        replay_row=QHBoxLayout();controls.addLayout(replay_row)
        self.replay_label=QLabel();self.replay_label.setWordWrap(True);self.replay_label.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred);replay_row.addWidget(self.replay_label,1)
        self.live=QPushButton(tr('실시간 복귀','Return to live'));self.live.clicked.connect(lambda:self.seek(len(self.controller.features.snapshot().get('events',[]))));replay_row.addWidget(self.live)
        self.selected_target=None;self.replaying=False;self.refresh()
    def refresh(self):
        self.caption.setText(tr('현재 작업','Current activity'))
        features=self.controller.features; private=self.controller.settings.values.get('broadcast_mode',False)
        live_snapshot=features.snapshot()
        # 재생 자료는 고정하되 개인정보 가림과 번역은 현재 표시 설정을 적용합니다.
        snapshot=self.replay_snapshot if self.replaying else live_snapshot
        if not self.replaying and hasattr(self.controller,'orbit29'):self.controller.orbit29.snapshot_cache=snapshot
        agents=snapshot.get('agents',[])
        self.agents.clear()
        labels={'active':('진행 중','Active'),'running':('진행 중','Active'),'assigned':('배정','Assigned'),'resumed':('재개','Resumed'),'complete':('완료','Complete'),'completed':('완료','Complete'),'waiting':('응답 대기','Waiting'),'error':('오류','Error'),'retrying':('재시도','Retrying'),'unknown':('상태 미확인','State unknown'),'aborted':('■ 중단','■ Aborted')}
        for agent in sorted(agents,key=lambda a:not a.get('pinned')):
            title=tr('비공개 채팅','Private chat') if private else str(agent.get('title') or agent.get('chat_name') or tr('제목 미확인','Title unavailable'))
            status=tr(*labels.get(agent.get('status'),labels['unknown']))
            item=QListWidgetItem(('★ ' if agent.get('pinned') else '')+title+' · '+status)
            item.setToolTip('' if private else title+' · '+status);item.setData(Qt.ItemDataRole.UserRole,agent.get('target'));self.agents.addItem(item)
        events=snapshot.get('events',[]);last=events[-1] if events else {}
        shown=present_event(last,private)
        self.heading.setText(shown.get('chat_name') or shown.get('title') or tr('새 변경을 기다립니다','Waiting for changes'))
        from orbit_features import task_hint
        self.state.setText((tr('기록된 작업 · ','Recorded task · ')+task_hint(shown,get_language())) if last and task_hint(shown,get_language()) else tr('기록된 작업을 기다립니다.','Waiting for recorded activity.'))
        target=last.get('target')
        selected=snapshot.get('selected',{}).get(target,{})
        executed=snapshot.get('executed',{}).get(target,{})
        def setting(value):return str(value.get('model') or tr('미확인','Unknown'))+' / '+str(value.get('effort') or tr('미확인','Unknown'))
        self.observations.setText(tr('선택한 설정','Selected settings')+'\n'+(setting(selected) if selected else tr('선택 기록이 아직 없습니다.','No selection has been recorded yet.'))+'\n\n'+tr('최근 실행에서 확인','Observed in the latest run')+'\n'+(setting(executed) if executed else tr('실행 기록이 아직 없습니다.','No execution has been recorded yet.')))
        self.agents.fit_rows()
        summary=features.away_summary()
        count=summary.get('count',summary.get('total',0)) if isinstance(summary,dict) else len(summary) if isinstance(summary,list) else 0
        self.away.setText(tr('자리비움 이후','Since last visit')+f' · {count} '+tr('건 · 실제 기록 기준','events · recorded activity'))
        self.pin.setText(tr('★ 관심 채팅','★ Pin chat'));self.bookmark.setText(tr('☆ 기록 보관','☆ Bookmark'));self.copy.setText(tr('채팅 ID 복사','Copy chat ID'))
        self.copy.setToolTip(tr('직접 이동은 지원 확인 전 제공하지 않습니다.','Direct navigation is unavailable until verified.'))
        self.live.setText(tr('실시간 복귀','Return to live'))
        self.timeline.setAccessibleName(tr('저장 기록 재생','Replay saved history'))
        self.timeline.blockSignals(True);self.timeline.setRange(0,len(live_snapshot.get('events',[])))
        if not self.replaying:self.timeline.setValue(len(events))
        self.timeline.blockSignals(False)
        if self.replaying:
            self.replay_label.setText(tr('기록 재생 · 실제 설정은 바뀌지 않습니다','History replay · actual settings stay unchanged')+' · '+str(last.get('time','')))
        else:
            self.replay_label.setText(tr('실시간','Live'));self.replay_label.setToolTip(tr('슬라이더를 움직이면 저장한 기록만 다시 봅니다. 실제 설정은 바뀌지 않습니다.','Move the slider to replay saved history. Actual settings stay unchanged.'))
    def select_agent(self,item):
        self.selected_target=item.data(Qt.ItemDataRole.UserRole);self.controller.orbit29.open_target(self.selected_target)
    def pin_agent(self):
        target=self.selected_target or (self.controller.features.snapshot().get('events') or [{}])[-1].get('target')
        if target:
            self.controller.features.set_pin(target,target not in self.controller.features.pins);self.refresh();self.controller.orbit29.feed_scene()
    def bookmark_event(self):
        item=self.controller.window.history.currentItem()
        if item:
            key=item.data(Qt.ItemDataRole.UserRole).get('id')
            if key:self.controller.features.set_bookmark(key,key not in self.controller.features.bookmarks);self.controller.orbit29.show_bookmarks()
    def copy_id(self):
        item=self.controller.window.history.currentItem()
        target=self.selected_target or (item.data(Qt.ItemDataRole.UserRole).get('target') if item else '')
        if target:QApplication.clipboard().setText(str(target))
    def seek(self,index):
        events=self.controller.features.snapshot().get('events',[])
        if index>=len(events):self.replaying=False;self.refresh();self.controller.orbit29.feed_scene();return
        event=events[index];snapshot=self.controller.features.snapshot(through=event['id']);self.replay_snapshot=snapshot;self.replay_id=event['id'];self.replaying=True
        self.replay_label.setText(tr('기록 재생 · 실제 설정은 바뀌지 않습니다','History replay · actual settings stay unchanged')+' · '+str(event.get('time','')))
        self.controller.orbit29.feed_scene(snapshot=snapshot);self.controller.show(event.get('id'))


class OrbitExperience:
    def __init__(self,controller):
        self.controller=controller;self.pointer=[0,0];self.transition=1.;self.transition_started=time.monotonic();self.last_health=None
        self.snapshot_cache=controller.features.snapshot()
        self.click_started=None
        self.scene={};self.docked=False;self.expanded_size=None;self._notifying_health=False
        self.timer=QTimer(controller.gui_owner);self.timer.setInterval(40);self.timer.timeout.connect(self.animate)
        self.panel=ObservatoryPanel(controller)
        self.install_navigation();self.install_controls();self.apply_text_size();self.feed_scene()
    def install_navigation(self):
        window=self.controller.window;layout=window.layout();tabs=window.tabs
        layout.removeWidget(tabs);wrapper=QWidget();row=QHBoxLayout(wrapper);row.setContentsMargins(0,0,0,0)
        navigation=QFrame();navigation.setObjectName('navigationSurface');nav=QVBoxLayout(navigation);nav.setContentsMargins(8,12,8,12);nav.setSpacing(4);row.addWidget(navigation);self.stack=QStackedWidget();self.stack.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Ignored);self.stack.addWidget(self.panel);self.stack.addWidget(tabs);self.stack.setCurrentIndex(1);row.addWidget(self.stack,1);tabs.tabBar().hide()
        self.observatory_button=QPushButton(tr('작업 현황','Overview'));self.observatory_button.setCheckable(True);self.observatory_button.clicked.connect(lambda:(self.stack.setCurrentIndex(0),self.update_navigation()));nav.addWidget(self.observatory_button)
        self.nav_buttons=[]
        for index,ko,en in ((0,'변경 기록','Activity'),(1,'사용 한도','Usage')):
            button=QPushButton(tr(ko,en));button.setMinimumWidth(130);button.setCheckable(True);button.clicked.connect(lambda checked=False,i=index:self.open_page(i));nav.addWidget(button);self.nav_buttons.append(button)
        self.bookmarks=QPushButton(tr('★ 보관한 기록','★ Bookmarks'));self.bookmarks.clicked.connect(self.show_bookmarks);nav.addSpacing(12);nav.addWidget(self.bookmarks)
        self.all_records=QPushButton(tr('전체 기록','All activity'));self.all_records.clicked.connect(self.show_all);nav.addWidget(self.all_records);nav.addStretch()
        tabs.currentChanged.connect(self.update_navigation);self.stack.currentChanged.connect(self.update_navigation)
        self.update_navigation();layout.addWidget(wrapper,1)
    def update_navigation(self,*_):
        observatory=self.stack.currentIndex()==0
        self.observatory_button.setChecked(observatory)
        for index,button in enumerate(self.nav_buttons):button.setChecked(not observatory and self.controller.window.tabs.currentIndex()==index)
    def open_page(self,index):
        self.stack.setCurrentIndex(1);self.controller.window.tabs.setCurrentIndex(index);self.update_navigation()

    def install_controls(self):
        from PySide6.QtWidgets import QMenu
        c=self.controller;self.ui_labels=[]
        self.controls=QFrame();self.controls.setObjectName('controlsBar');rows=QVBoxLayout(self.controls);rows.setContentsMargins(12,10,12,10);rows.setSpacing(8);c.window.layout().insertWidget(1,self.controls)
        preference_groups=[]
        c.window.layout().itemAt(0).layout().removeWidget(c.window.language_combo)
        def group(ko,en,widget):
            container=QWidget();layout=QHBoxLayout(container);layout.setContentsMargins(0,0,0,0);layout.setSpacing(8);label=QLabel(tr(ko,en));label.setObjectName('sectionCaption');self.ui_labels.append((label,ko,en));layout.addWidget(label);layout.addWidget(widget,1);preference_groups.append(container)
        group('언어','Language',c.window.language_combo)
        self.theme_combo=QComboBox()
        for ko,en,value in [('시스템','System','system'),('라이트','Light','light'),('다크','Dark','dark')]:self.theme_combo.addItem(tr(ko,en),value)
        self.theme_combo.setCurrentIndex(max(0,self.theme_combo.findData(c.settings.values.get('ui_theme','system'))));self.theme_combo.setAccessibleName(tr('화면 테마','Appearance'))
        self.theme_combo.currentIndexChanged.connect(lambda _:self.option('ui_theme',self.theme_combo.currentData()));group('화면 테마','Appearance',self.theme_combo)
        self.text_size=QComboBox()
        for value in (90,100,115,130,150):self.text_size.addItem(str(value)+'%',value)
        self.text_size.setCurrentIndex(max(0,self.text_size.findData(c.settings.values.get('text_scale',100))));self.text_size.setAccessibleName(tr('글자 크기','Text size'))
        self.text_size.currentIndexChanged.connect(lambda _:self.option('text_scale',self.text_size.currentData()));group('글자 크기','Text size',self.text_size);self.preferences=ResponsiveRow(preference_groups);rows.addWidget(self.preferences)
        row=QHBoxLayout();row.setSpacing(8);rows.addLayout(row)
        self.view=QComboBox();self.view.addItem(tr('입체 관측소','3D observatory'),'observatory');self.view.addItem(tr('날짜별 조형','Daily sculpture'),'calendar')
        self.view.setCurrentIndex(1 if c.settings.values.get('scene_mode','calendar')=='calendar' else 0);self.view.currentIndexChanged.connect(lambda _:self.option('scene_mode',self.view.currentData()));row.addWidget(self.view)
        self.play=QPushButton();self.play.setCheckable(True);self.play.setChecked(c.settings.values.get('motion_paused',False));self.play.toggled.connect(lambda v:self.option('motion_paused',v));row.addWidget(self.play)
        self.privacy=QPushButton();self.privacy.setCheckable(True);self.privacy.setChecked(c.settings.values.get('broadcast_mode',False));self.privacy.toggled.connect(lambda v:self.option('broadcast_mode',v));row.addWidget(self.privacy)
        self.more=QPushButton(tr('화면 설정','Display settings'));self.menu=QMenu(self.more);self.menu.setTitle(tr('화면 설정','Display settings'));self.more.setMenu(self.menu);row.addWidget(self.more);row.addStretch()
        self.menu_rows=[];self.menu_sections=[]
        def menu_heading(ko,en):
            label=QLabel(tr(ko,en));label.setObjectName('sectionCaption');set_ui_style(label,'font-size:12px;padding:8px 12px;')
            action=QWidgetAction(self.menu);action.setDefaultWidget(label);self.menu.addAction(action);self.menu_sections.append((label,ko,en))
        menu_heading('움직임과 알림','Motion and alerts')
        def menu_row(menu,ko,en,description_ko,description_en,check=None):
            action=QWidgetAction(menu);box=QWidget();layout=QVBoxLayout(box);layout.setContentsMargins(12,8,12,8);layout.setSpacing(4)
            button=QCheckBox() if check is not None else QPushButton();button.setText(tr(ko,en));layout.addWidget(button)
            label=QLabel(tr(description_ko,description_en));label.setObjectName('sectionCaption');label.setWordWrap(True);layout.addWidget(label);box.setMinimumWidth(300)
            if check is not None:
                key=check;button.setChecked(c.settings.values.get(key,False));button.toggled.connect(lambda value:self.option(key,value))
            action.setDefaultWidget(box);menu.addAction(action);self.menu_rows.append((button,label,ko,en,description_ko,description_en));return action,button
        for key,ko,en,dk,de in [('reduced_motion','움직임 줄이기','Reduce motion','입체 조형의 움직임을 최소화합니다.','Minimize animation of the sculpture.'),('edge_docking','화면 가장자리에 붙이기','Dock at screen edge','가장자리에서는 작게 접고 마우스를 올리면 펼칩니다.','Fold near the edge; hover to expand.'),('notification_sound','알림 소리','Notification sound','변경 알림이 올 때 짧은 소리를 냅니다.','Play a short sound for new notifications.')]:menu_row(self.menu,ko,en,dk,de,key)
        self.menu.addSeparator();quality=self.menu.addMenu(tr('성능·화질','Performance and quality'));self.quality_menu=quality;self.quality_group=QActionGroup(self.menu);self.quality_group.setExclusive(True)
        for value,ko,en,dk,de in [('eco','절전','Eco','움직임을 초당 최대20회로 제한합니다.','Limit animation to 20 frames per second.'),('balanced','균형','Balanced','움직임을 초당 최대30회로 제한합니다.','Limit animation to 30 frames per second.'),('high','고화질','High quality','움직임을 초당 최대60회로 제한합니다.','Limit animation to 60 frames per second.')]:
            action=quality.addAction(tr(ko,en));action.setCheckable(True);action.setData(value);action.setChecked(c.settings.values.get('render_quality','balanced')==value);self.quality_group.addAction(action);action.triggered.connect(lambda checked=False,v=value:self.option('render_quality',v));action.setToolTip(tr(dk,de))
        menu_heading('도움말과 업데이트','Help and updates')
        action,button=menu_row(self.menu,'문제 확인용 파일 저장','Save diagnostic file','개인 원문 없이 진단 ZIP을 저장합니다.','Save a diagnostic ZIP without private source records.');button.clicked.connect(lambda:(self.menu.hide(),self.diagnostics()))
        action,button=menu_row(self.menu,'새 버전 확인','Check for update','공식 저장소에서 새 버전을 확인합니다.','Check the official repository for a newer version.');button.clicked.connect(lambda:(self.menu.hide(),self.check_update()))
        for combo in (self.theme_combo,self.text_size,c.window.language_combo,self.view):combo.setMinimumHeight(38)
        motion=c.window.layout().takeAt(2).layout();c.window.motion_speed_slider.setMaximumWidth(340);motion.addStretch();rows.addLayout(motion)
        self.update_labels()
    def update_labels(self):
        c=self.controller
        self.play.setText(tr('▶ 재생','▶ Play') if c.settings.values.get('motion_paused') else tr('Ⅱ 일시정지','Ⅱ Pause'))
        self.privacy.setToolTip(tr('화면에서 채팅 제목과 작업 설명을 가립니다. 저장된 기록은 그대로 유지됩니다.','Hide chat titles and task descriptions on screen. Stored records stay unchanged.'))
        self.privacy.setText(tr('프라이버시 모드 켜짐','Privacy on') if c.settings.values.get('broadcast_mode') else tr('프라이버시 모드','Privacy mode'))
    def retranslate(self):
        pairs=[('작업 현황','Overview'),('변경 기록','Activity'),('사용 한도','Usage'),('★ 보관한 기록','★ Bookmarks'),('전체 기록','All activity'),('입체 관측소','3D observatory'),('날짜별 조형','Daily sculpture'),('화면 설정','Display settings'),('화면 설정','Display settings'),('모션 축소','Reduce motion'),('가장자리 도킹','Edge docking'),('알림음','Notification sound'),('자원 사용','Resource use'),('절전','Eco'),('균형','Balanced'),('고화질','High quality'),('진단 ZIP 저장','Save diagnostics ZIP'),('업데이트 확인','Check for updates')]
        translations={text:tr(ko,en) for ko,en in pairs for text in (ko,en)}
        for button in self.nav_buttons+[self.bookmarks,self.all_records,self.more,self.observatory_button]:button.setText(translations.get(button.text(),button.text()))
        self.view.blockSignals(True)
        self.view.setItemText(0,tr('입체 관측소','3D observatory'));self.view.setItemText(1,tr('날짜별 조형','Daily sculpture'));self.view.blockSignals(False)
        def menu_labels(menu):
            menu.setTitle(translations.get(menu.title(),menu.title()))
            for action in menu.actions():
                action.setText(translations.get(action.text(),action.text()))
                if action.menu():menu_labels(action.menu())
        menu_labels(self.menu)
        self.text_size.setAccessibleName(tr('글자 크기','Text size'));self.panel.live.setText(tr('실시간 복귀','Return to live'))
        for label,ko,en in self.ui_labels:label.setText(tr(ko,en))
        for button,label,ko,en,dk,de in self.menu_rows:button.setText(tr(ko,en));label.setText(tr(dk,de))
        for action,ko,en in self.menu_sections:action.setText(tr(ko,en))
        self.quality_menu.setTitle(tr('성능·화질','Performance and quality'))
        for action,(ko,en) in zip(self.quality_group.actions(),[('절전','Eco'),('균형','Balanced'),('고화질','High quality')]):action.setText(tr(ko,en))
        self.theme_combo.blockSignals(True)
        for i,(ko,en) in enumerate([('시스템','System'),('라이트','Light'),('다크','Dark')]):self.theme_combo.setItemText(i,tr(ko,en))
        self.theme_combo.blockSignals(False)
        self.update_labels();self.panel.refresh()

    def option(self,key,value):
        if key=='ui_theme':
            from theme import normalize_theme_mode
            value=normalize_theme_mode(value)
        c=self.controller;previous=c.settings.values.get(key)
        c.settings.values[key]=value
        try:c.settings.save()
        except Exception as error:
            c.settings.values[key]=previous;QMessageBox.warning(c.window,tr('저장 실패','Save failed'),str(error));return
        if key=='broadcast_mode':
            for notice in c.notices.values():notice.broadcast_mode=bool(value);notice.update_event(notice.notice_event)
            mask_details(c.window);self.panel.refresh()
        for setting,combo in [('ui_theme',self.theme_combo),('text_scale',self.text_size),('scene_mode',self.view)]:
            if key==setting:
                combo.blockSignals(True);combo.setCurrentIndex(max(0,combo.findData(value)));combo.blockSignals(False)
        for setting,button in [('broadcast_mode',self.privacy),('motion_paused',self.play)]:
            if key==setting:button.blockSignals(True);button.setChecked(bool(value));button.blockSignals(False)
        if key=='render_quality':
            for action in self.quality_group.actions():action.setChecked(action.data()==value)
        if key=='ui_theme':
            from theme import apply_theme
            apply_theme(value);self.apply_text_size()
        if key=='text_scale':self.apply_text_size();c.orbit._request_motion_size()
        if key=='edge_docking' and not value:self.expand()
        self.update_labels();self.feed_scene()
    def apply_text_size(self):
        c=self.controller;scale=c.settings.values.get('text_scale',100)/100
        from theme import unscaled_font_size
        c.window.setStyleSheet('');c.window.setProperty('orbit_text_scale31',scale)
        children=c.window.findChildren(QWidget)
        # 부모 글꼴을 바꾸기 전에 모든 자식의 비배율 크기를 먼저 확정합니다.
        bases=[unscaled_font_size(child) for child in children]
        for child,base in zip(children,bases):
            child.setFont(app_font(round(base*scale)))
            child.setProperty('orbit_text_scale31',scale)
            source=child.property('orbit_style_source')
            if source is None:source=child.styleSheet()
            set_ui_style(child,source)
        self.panel.agents.fit_rows();c.window.history_layout_timer.start(0)
    def ingest(self,event):
        c=self.controller
        if not isinstance(event.get('target'),str) or not event['target'].strip():return
        c.features.ingest(event);self.snapshot_cache=c.features.snapshot();self.panel.refresh();self.transition=0.;self.transition_started=time.monotonic();self.timer.start();self.feed_scene()
        if c.settings.values.get('notification_sound',False):
            # 자산이 없는 환경에서도 운영체제의 짧은 신호음을 사용합니다.
            import winsound
            flags={'settings':winsound.MB_OK,'activity':winsound.MB_ICONASTERISK,'lifecycle':winsound.MB_ICONEXCLAMATION}
            winsound.MessageBeep(flags.get(event.get('kind'),winsound.MB_OK))
    def animate(self):
        self.transition=min(1,(time.monotonic()-self.transition_started)/.9);self.feed_scene()
        if self.transition>=1 and (self.click_started is None or time.monotonic()-self.click_started>=.35):self.click_started=None;self.timer.stop()
    def feed_scene(self,snapshot=None):
        c=self.controller
        if not hasattr(c,'orbit'):return
        from calendar_motion import set_calendar_observatory_scene,set_calendar_motion_options
        set_calendar_motion_options(paused=bool(c.settings.values.get("motion_paused",False)),reduced_motion=bool(c.settings.values.get("reduced_motion",False)),quality=c.settings.values.get("render_quality","balanced"))
        if c.settings.values.get('scene_mode','calendar')=='calendar':set_calendar_observatory_scene(None);return
        snapshot=snapshot or (self.panel.replay_snapshot if self.panel.replaying else self.snapshot_cache);agents=sorted(snapshot.get('agents',[]),key=lambda a:not a.get('pinned'))
        events=snapshot.get('events',[]);last=events[-1] if events else {};target=last.get('target');current=last.get('after') or snapshot.get('executed',{}).get(target) or snapshot.get('selected',{}).get(target) or {}
        self.scene={'model':current.get('model'),'effort':current.get('effort'),'agents':[{'target':a['target'],'status':a.get('status','unknown'),'pinned':a.get('pinned',False)} for a in agents[:24]],
          'usage_fraction':c.orbit.usage_fraction if c.orbit.usage_state=='fresh' else None,'paused':bool(c.settings.values.get('motion_paused',False) or self.panel.replaying),'reduced_motion':bool(c.settings.values.get('reduced_motion',False)),
          'quality':c.settings.values.get('render_quality','balanced'),'pointer':self.pointer,'transition':self.transition,'press':max(0.,1.-(time.monotonic()-self.click_started)/.35) if self.click_started else 0.}
        set_calendar_observatory_scene(self.scene);self.panel.canvas.update();c.orbit.update()
    def open_target(self,target):
        events=self.controller.features.snapshot().get('events',[])
        event=next((e for e in reversed(events) if e.get('target')==target and e.get('kind')!='lifecycle'),None)
        self.controller.show(event.get('id') if event else None)
    def hit(self,x,y):
        from observatory_scene import observatory_positions
        from calendar_motion import calendar_motion_status
        positions=observatory_positions(self.scene,calendar_motion_status().get('scene_elapsed',0.))
        nearest=min(positions,key=lambda p:(p['x']-x)**2+(p['y']-y)**2,default=None)
        if nearest and (nearest['x']-x)**2+(nearest['y']-y)**2<.035**2:self.open_target(nearest['target'])
        else:self.click_started=time.monotonic();self.timer.start();self.feed_scene();self.controller.show()
    def show_bookmarks(self):
        self.open_page(0)
        c=self.controller
        for i in range(c.window.history.count()):
            item=c.window.history.item(i);item.setHidden(item.data(Qt.ItemDataRole.UserRole).get('id') not in c.features.bookmarks)
    def show_all(self):
        self.open_page(0)
        for i in range(self.controller.window.history.count()):self.controller.window.history.item(i).setHidden(False)
    def diagnostics(self):
        from calendar_motion import calendar_motion_status
        path,_=QFileDialog.getSaveFileName(self.controller.window,tr('진단 ZIP 저장','Save diagnostics ZIP'),'CodexOrbit-diagnostics.zip','ZIP (*.zip)')
        if path:
            try:self.controller.features.write_diagnostics(path,self.controller.last_monitor_status or {},calendar_motion_status())
            except Exception as error:QMessageBox.warning(self.controller.window,tr('저장 실패','Save failed'),str(error))
    def check_update(self):
        from update_widgets import show_update
        show_update(self.controller)
    def health(self,value):
        state=value.get('state','');healthy=state=='감시 중';problem=any(x in state for x in ('오류','중단','지연','실패'))
        if self.last_health is None:
            if healthy:self.last_health=True
            elif problem:self.last_health=False
            return
        if (healthy or problem) and healthy!=self.last_health:
            self.last_health=healthy
            c=self.controller;event={'id':'health-'+str(time.time_ns()),'kind':'health','chat_name':tr('Codex 감시 상태','Codex monitor status'),'time':value.get('time'),'reason':tr('감시 연결이 복구되어 새 변경을 계속 알려드립니다.','Monitoring recovered; new changes will be reported.') if healthy else tr('변경을 확인하지 못하고 있습니다. 연결을 다시 확인하는 중입니다.','Changes cannot be observed. Retrying the connection.'),'before':None,'after':None}
            c.enqueue_notice(event)
    def dock(self):
        c=self.controller;orbit=c.orbit
        if not c.settings.values.get('edge_docking') or self.docked:return
        screen=QApplication.screenAt(orbit.pos()) or QApplication.primaryScreen()
        if not screen:return
        rect=screen.availableGeometry()
        if abs(orbit.x()-rect.left())>32 and abs(rect.right()+1-orbit.x()-orbit.width())>32:return
        self.expanded_size=orbit.size();self.expanded_position=orbit.pos();self.docked=True
        orbit.setMinimumSize(32,80);orbit.resize(40,120)
        orbit.move(rect.left() if orbit.x()-rect.left()<32 else rect.right()-39,max(rect.top(),min(orbit.y(),rect.bottom()-119)))
    def expand(self):
        if self.docked:
            orbit=self.controller.orbit;self.docked=False;orbit.resize(self.expanded_size);orbit.move(self.expanded_position);orbit.setMinimumSize(180,250);orbit.restore_position()
