"""29차 관측소의 화면 조작과 실제 관측값 연결입니다."""
from copy import deepcopy
from pathlib import Path
import time
from PySide6.QtCore import Qt,QTimer,QSize
from PySide6.QtGui import QPainter,QColor
from PySide6.QtWidgets import (QWidget,QFrame,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,
    QListWidget,QListWidgetItem,QSlider,QComboBox,QFileDialog,QMessageBox,QApplication,QStackedWidget)
from i18n import translate as t,get_language
from typography import app_font


def tr(ko,en):
    return en if get_language()=='en' else ko


def present_event(event,private=False):
    """저장 원문은 유지하고 표시 사본만 정리합니다."""
    from orbit_features import clean_chat_title
    if private:
        keys=('id','target','time','before','after','kind','role','activity_type','activity_action')
        value={key:deepcopy(event[key]) for key in keys if key in event}
        value.update(chat_name=tr('비공개 채팅','Private chat'),task_summary='',reason=tr('방송 모드에서 설명을 가렸습니다.','Details hidden in broadcast mode.'))
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
    notice.setStyleSheet('#notice{background:#fbfffe;border:1px solid #bdd8d0;border-radius:18px;} QLabel{background:transparent;color:#193a37;font-weight:700;}')
    notice.title_marker.hide()
    for label in notice.findChildren(QLabel):
        css=label.styleSheet()
        import re
        css=re.sub(r'color:#[0-9a-fA-F]{3,8}', 'color:#23433f',css)
        css=css.replace('background:#385064','background:#d4f3e7')
        label.setStyleSheet(css.replace('font-weight:600','font-weight:700').replace('font-weight:500','font-weight:700'))


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


class ObservatoryPanel(QFrame):
    def __init__(self,controller):
        super().__init__();self.controller=controller;self.setObjectName('observatoryHero')
        outer=QHBoxLayout(self);outer.setContentsMargins(20,12,20,12);outer.setSpacing(20)
        self.canvas=SceneCanvas(controller);outer.addWidget(self.canvas,2)
        body=QVBoxLayout();body.setSpacing(14);outer.addLayout(body,3);outer.setAlignment(body,Qt.AlignmentFlag.AlignVCenter)
        self.heading=QLabel();self.heading.setObjectName('currentTask');self.heading.setWordWrap(True);body.addWidget(self.heading)
        self.state=QLabel();self.state.setWordWrap(True);body.addWidget(self.state)
        self.observations=QLabel();self.observations.setWordWrap(True);body.addWidget(self.observations)
        self.away=QLabel();self.away.setWordWrap(True);body.addWidget(self.away)
        self.agents=QListWidget();self.agents.setMaximumHeight(120);body.addWidget(self.agents)
        self.agents.itemClicked.connect(self.select_agent)
        row=QHBoxLayout();body.addLayout(row)
        self.pin=QPushButton();self.pin.clicked.connect(self.pin_agent);row.addWidget(self.pin)
        self.bookmark=QPushButton();self.bookmark.clicked.connect(self.bookmark_event);row.addWidget(self.bookmark)
        self.copy=QPushButton();self.copy.clicked.connect(self.copy_id);row.addWidget(self.copy)
        self.timeline=QSlider(Qt.Orientation.Horizontal);self.timeline.setAccessibleName(tr('저장 기록 재생','Replay saved history'));self.timeline.valueChanged.connect(self.seek);body.addWidget(self.timeline)
        replay_row=QHBoxLayout();body.addLayout(replay_row)
        self.replay_label=QLabel();self.replay_label.setWordWrap(True);replay_row.addWidget(self.replay_label,1)
        self.live=QPushButton(tr('실시간 복귀','Return to live'));self.live.clicked.connect(lambda:self.seek(len(self.controller.features.snapshot().get('events',[]))));replay_row.addWidget(self.live)
        self.selected_target=None;self.replaying=False;self.refresh()
    def refresh(self):
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
            item.setData(Qt.ItemDataRole.UserRole,agent.get('target'));self.agents.addItem(item)
        events=snapshot.get('events',[]);last=events[-1] if events else {}
        shown=present_event(last,private)
        self.heading.setText(shown.get('chat_name') or shown.get('title') or tr('새 변경을 기다립니다','Waiting for changes'))
        from orbit_features import task_hint
        self.state.setText(task_hint(shown,get_language()) if last else tr('실제 로컬 기록을 관측하면 표시됩니다.','Appears when local activity is observed.'))
        target=last.get('target')
        selected=snapshot.get('selected',{}).get(target,{})
        executed=snapshot.get('executed',{}).get(target,{})
        def setting(value):return str(value.get('model') or tr('미확인','Unknown'))+' / '+str(value.get('effort') or tr('미확인','Unknown'))
        self.observations.setText(tr('선택 설정: ','Selected: ')+setting(selected)+'\n'+tr('실행 관측: ','Executed: ')+setting(executed))
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
        else:self.replay_label.setText(tr('실시간 · 슬라이더를 움직이면 저장 기록만 재생합니다.','Live · move the slider to replay saved history.'))
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
        nav=QVBoxLayout();row.addLayout(nav);self.stack=QStackedWidget();self.stack.addWidget(self.panel);self.stack.addWidget(tabs);self.stack.setCurrentIndex(1);row.addWidget(self.stack,1);tabs.tabBar().hide()
        self.observatory_button=QPushButton(tr('입체 관측소','3D observatory'));self.observatory_button.setCheckable(True);self.observatory_button.clicked.connect(lambda:(self.stack.setCurrentIndex(0),self.update_navigation()));nav.addWidget(self.observatory_button)
        self.nav_buttons=[]
        for index,ko,en in ((0,'변경 기록','Activity'),(1,'사용 한도','Usage')):
            button=QPushButton(tr(ko,en));button.setMinimumWidth(130);button.setCheckable(True);button.clicked.connect(lambda checked=False,i=index:self.open_page(i));nav.addWidget(button);self.nav_buttons.append(button)
        self.bookmarks=QPushButton(tr('★ 보관한 기록','★ Bookmarks'));self.bookmarks.clicked.connect(self.show_bookmarks);nav.addWidget(self.bookmarks)
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
        c=self.controller;row=QHBoxLayout();c.window.layout().insertLayout(2,row)
        self.view=QComboBox();self.view.addItem(tr('입체 관측소','3D observatory'),'observatory');self.view.addItem(tr('날짜별 조형','Daily sculpture'),'calendar')
        self.view.setCurrentIndex(1 if c.settings.values.get('scene_mode','calendar')=='calendar' else 0)
        self.view.currentIndexChanged.connect(lambda _:self.option('scene_mode',self.view.currentData()));row.addWidget(self.view)
        self.play=QPushButton();self.play.setCheckable(True);self.play.setChecked(c.settings.values.get('motion_paused',False));self.play.toggled.connect(lambda v:self.option('motion_paused',v));row.addWidget(self.play)
        self.privacy=QPushButton();self.privacy.setCheckable(True);self.privacy.setChecked(c.settings.values.get('broadcast_mode',False));self.privacy.toggled.connect(lambda v:self.option('broadcast_mode',v));row.addWidget(self.privacy)
        self.text_size=QComboBox()
        for value in (90,100,115,130,150):self.text_size.addItem(str(value)+'%',value)
        self.text_size.setCurrentIndex(max(0,self.text_size.findData(c.settings.values.get('text_scale',100))))
        self.text_size.setAccessibleName(tr('글자 크기','Text size'));self.text_size.currentIndexChanged.connect(lambda _:self.option('text_scale',self.text_size.currentData()));row.addWidget(self.text_size)
        self.more=QPushButton(tr('표시 조작 ⋯','Display ⋯'));self.menu=QMenu(self.more)
        for key,ko,en in (('reduced_motion','모션 축소','Reduce motion'),('edge_docking','가장자리 도킹','Edge docking'),('notification_sound','알림음','Notification sound')):
            action=self.menu.addAction(tr(ko,en));action.setCheckable(True);action.setChecked(c.settings.values.get(key,False));action.toggled.connect(lambda value,k=key:self.option(k,value))
        quality=self.menu.addMenu(tr('자원 사용','Resource use'))
        for value,ko,en in (('eco','절전','Eco'),('balanced','균형','Balanced'),('high','고화질','High quality')):quality.addAction(tr(ko,en),lambda v=value:self.option('render_quality',v))
        self.menu.addAction(tr('진단 ZIP 저장','Save diagnostics ZIP'),self.diagnostics)
        self.menu.addAction(tr('업데이트 확인','Check for updates'),self.check_update)
        self.menu.setTitle(tr('표시 조작','Display controls'));self.more.setMenu(self.menu);row.addWidget(self.more);row.addStretch();self.update_labels()
    def update_labels(self):
        c=self.controller
        self.play.setText(tr('▶ 재생','▶ Play') if c.settings.values.get('motion_paused') else tr('Ⅱ 일시정지','Ⅱ Pause'))
        self.privacy.setText(tr('방송 모드 켜짐','Broadcast on') if c.settings.values.get('broadcast_mode') else tr('방송 모드','Broadcast mode'))
    def retranslate(self):
        pairs=[('변경 기록','Activity'),('사용 한도','Usage'),('★ 보관한 기록','★ Bookmarks'),('전체 기록','All activity'),('입체 관측소','3D observatory'),('날짜별 조형','Daily sculpture'),('표시 조작 ⋯','Display ⋯'),('표시 조작','Display controls'),('모션 축소','Reduce motion'),('가장자리 도킹','Edge docking'),('알림음','Notification sound'),('자원 사용','Resource use'),('절전','Eco'),('균형','Balanced'),('고화질','High quality'),('진단 ZIP 저장','Save diagnostics ZIP'),('업데이트 확인','Check for updates')]
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
        self.update_labels();self.panel.refresh()

    def option(self,key,value):
        c=self.controller;previous=c.settings.values.get(key)
        c.settings.values[key]=value
        try:c.settings.save()
        except Exception as error:
            c.settings.values[key]=previous;QMessageBox.warning(c.window,tr('저장 실패','Save failed'),str(error));return
        if key=='broadcast_mode':
            for notice in c.notices.values():notice.broadcast_mode=bool(value);notice.update_event(notice.notice_event)
            mask_details(c.window);self.panel.refresh()
        if key=='text_scale':self.apply_text_size();c.orbit._request_motion_size()
        if key=='edge_docking' and not value:self.expand()
        self.update_labels();self.feed_scene()
    def apply_text_size(self):
        c=self.controller;scale=c.settings.values.get('text_scale',100)/100
        font=app_font(round(13*scale));c.window.setFont(font)
        for label in c.window.findChildren(QLabel):
            base=label.property('baseFont29')
            if base is None:base=max(12,label.font().pixelSize() if label.font().pixelSize()>0 else 13);label.setProperty('baseFont29',base)
            label.setFont(app_font(round(base*scale)))
        # 스타일의 px 우선순위에도 사용자 선택이 적용되도록 각 크기를 함께 조정합니다.
        import re
        from theme import STYLE
        c.window.setStyleSheet(re.sub(r'font-size:(\d+)px',lambda m:'font-size:'+str(round(int(m[1])*scale))+'px',STYLE))
        for child in c.window.findChildren(QWidget):
            original=child.property('baseStyle29')
            if original is None:original=child.styleSheet();child.setProperty('baseStyle29',original)
            child.setStyleSheet(re.sub(r'font-size:(\d+)px',lambda m:'font-size:'+str(round(int(m[1])*scale))+'px',original))
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
