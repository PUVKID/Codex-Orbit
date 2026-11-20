"""지역 설정에서 도시 행사 수록 범위와 발표 일정·출처를 읽습니다."""
import html
import json
from datetime import date
from urllib.parse import urlsplit
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QListWidget,QListWidgetItem,QTextBrowser,QPushButton
from PySide6.QtCore import Qt,Slot
from i18n import translate as t,get_language,remember_translations,retranslate_widgets


def city_summary(city_ref,country,year):
    if city_ref is None:return t('도시 행사: 식별자 미확인')
    from city_festivals import city_coverage
    try:coverage=city_coverage(city_ref,country,year)
    except (ValueError,OSError):return t('도시 행사: 자료 미확인')
    heading=t('도시 행사')
    return heading+' · '+t('축제 목록 {items}개 항목 · 발표 일정 {events}개').format(items=coverage['catalog_items_count'],events=coverage['announced_occurrences_count'])


class CityEventsDialog(QDialog):
    def __init__(self,parent,city_ref,country,local_date,updater=None):
        super().__init__(parent)
        self.setWindowTitle(t('도시 축제·행사'))
        self.resize(650,530)
        self.city_ref=dict(city_ref) if city_ref else None
        self.country=country;self.local_date=local_date;self.updater=updater
        layout=QVBoxLayout(self)
        top=QHBoxLayout();top.addWidget(QLabel(t('일정 기준 연도')))
        self.year=QComboBox()
        for year in range(2026,2100):self.year.addItem(str(year),year)
        self.year.setCurrentIndex(max(0,min(73,local_date.year-2026)))
        top.addWidget(self.year);top.addStretch()
        self.refresh_button=QPushButton(t('일정 새로고침'));self.refresh_button.setEnabled(updater is not None)
        self.refresh_button.clicked.connect(self.request_update);top.addWidget(self.refresh_button);layout.addLayout(top)
        self.summary=QLabel();self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.limits=QLabel(t('수록 목록과 발표된 날짜를 구분합니다. 미발표 일정과 전 세계 모든 도시 행사를 보장하지 않습니다.'))
        self.limits.setWordWrap(True);layout.addWidget(self.limits)
        self.rows=QListWidget();self.rows.setWordWrap(True);self.rows.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);layout.addWidget(self.rows,1)
        self.details=QTextBrowser();self.details.setOpenExternalLinks(True);self.details.setMinimumHeight(100);self.details.setMaximumHeight(170);layout.addWidget(self.details)
        close=QPushButton(t('닫기'));close.clicked.connect(self.accept);layout.addWidget(close)
        self.rows.currentRowChanged.connect(self.show_details);self.year.currentIndexChanged.connect(self.refresh)
        if updater is not None:
            updater.changed.connect(self.catalog_changed)
            updater.failed.connect(self.update_failed)
        self.refresh()
        remember_translations(self)

    def retranslate(self):
        retranslate_widgets(self)
        self.setWindowTitle(t('도시 축제·행사'))
        self.refresh()

    def request_update(self):
        if self.updater is not None:self.updater.refresh(self.country)

    @Slot(str)
    def catalog_changed(self,revision):
        self.refresh()

    @Slot(str)
    def update_failed(self,message):
        self.summary.setText(t('일정 갱신 실패 · 기존 자료 유지'))
        self.summary.setToolTip(message)

    def refresh(self):
        current=self.rows.currentItem()
        selected_id=current.data(Qt.ItemDataRole.UserRole).get('id') if current is not None else None
        self.rows.clear();self.details.clear()
        year=self.year.currentData()
        if self.city_ref is None:
            self.summary.setText(t('도시 식별자가 없습니다. 도시 검색 결과를 적용하면 지원 범위를 확인할 수 있습니다.'))
            return
        from city_festivals import city_coverage,series_for_city,announced_events_for_year
        try:
            coverage=city_coverage(self.city_ref,self.country,year)
            series=series_for_city(self.city_ref,self.country,get_language())
            announced=announced_events_for_year(self.city_ref,self.country,year)
        except (ValueError,OSError) as error:
            self.summary.setText(t('도시 행사: 자료 미확인'));self.summary.setToolTip(str(error));return
        self.summary.setText(city_summary(self.city_ref,self.country,year)+' · '+t('발표된 날짜 {days}일').format(days=coverage['announced_dates_count']))
        self.summary.setToolTip(t('원본 수록 범위: ')+json.dumps(coverage,ensure_ascii=False,sort_keys=True))
        for row in announced:
            title=row.get('title_en') if get_language()=='en' else row['title']
            item=QListWidgetItem(t('발표된 일정: ')+str(title or row['title']))
            item.setData(Qt.ItemDataRole.UserRole,row);self.rows.addItem(item)
        for row in series:
            item=QListWidgetItem(str(row.get('display_title') or row['title'])+' · '+{'series':t('시리즈'),'edition':t('개최 회차'),'unclassified':t('미분류 항목')}.get(row.get('item_role','unclassified'),t('미분류 항목')))
            item.setData(Qt.ItemDataRole.UserRole,row);self.rows.addItem(item)
        if self.rows.count():
            index=next((i for i in range(self.rows.count()) if self.rows.item(i).data(Qt.ItemDataRole.UserRole).get('id')==selected_id),0)
            self.rows.setCurrentRow(index)

    def show_details(self,index):
        item=self.rows.item(index)
        if item is None:self.details.clear();return
        row=item.data(Qt.ItemDataRole.UserRole)
        # 출처는 제공 원문을 유지하고 HTTPS 링크만 명시적으로 열 수 있습니다.
        source=str(row.get('source_url') or '')
        safe=html.escape(source,quote=True)
        link=('<a href="'+safe+'">'+safe+'</a>') if urlsplit(source).scheme=='https' else safe
        fields={key:row.get(key) for key in ('id','status','kind','item_role','local_date','dates','start_date','end_date','date_precision','date_evidence','time_conflict','location_confidence','selection_confidence','license') if key in row}
        dates=row.get('dates') or []
        period=' · '.join(str(value) for value in dates) if dates else t('행사 목록입니다. 개별 발표 일정은 위에서 확인합니다.')
        warning=''
        if row.get('time_conflict'):
            message=('공식 페이지에서 날짜 확인 · 시간은 미확인' if row.get('date_evidence')=='official_page_crosschecked'
                     else '시간 정보 충돌 · 날짜 조형 적용 제외')
            warning='<p>'+html.escape(t(message))+'</p>'
        self.details.setHtml('<p>'+html.escape(period)+'</p>'+warning+'<p>'+html.escape(t('라이선스: ')+str(row.get('license') or t('미확인')))+'</p><p>'+link+'</p>')
        self.details.setToolTip(json.dumps(fields,ensure_ascii=False,indent=2))
