"""양력 날짜가 명확한 특집만 별도로 정의합니다. 음력 날짜를 추정하지 않습니다."""
from types import MappingProxyType
from dataclasses import replace
from calendar_catalog import ObjectSpec, OBJECTS
from holiday_calendar import event_for_date, normalize_country


SPECIAL_DATES = MappingProxyType({
    (1, 1): ('special_new_year', '새해 특집 · 새로운 시작', 'new_year', '#E6BB63'),
    (2, 14): ('special_valentine', '밸런타인데이 특집 · 마음을 담은 선물', 'heart', '#D66483'),
    (5, 5): ('special_children', '어린이날 특집 · 바람개비', 'pinwheel', '#72B5DA'),
    (10, 9): ('special_hangul', '한글날 특집 · 한글', 'hangul', '#DFD4B3'),
    (10, 31): ('special_halloween', '할로윈 특집 · 호박 등', 'pumpkin', '#EBA04B'),
    (12, 24): ('special_christmas_eve', '크리스마스이브 특집 · 선물', 'gift', '#CA5261'),
    (12, 25): ('special_christmas', '크리스마스 특집 · 크리스마스트리', 'tree', '#468366'),
    (12, 31): ('special_year_end', '연말 특집 · 자정을 기다리는 시계', 'clock', '#D8B65B'),
})
SPECIAL_OBJECTS = MappingProxyType({
    key: ObjectSpec(key, title, '특집', recipe, color, 1, 1, 24, 30, title)
    for key, title, recipe, color in SPECIAL_DATES.values()
})

PUBLIC_HOLIDAY = ObjectSpec('special_public_holiday', '공휴일 특집', '특집', 'celebration', '#CFA95B', 1, 1, 24, 30, '입체 축하 장식')
KIND_KEYS = MappingProxyType({
    'new_year': 'special_new_year', 'valentine': 'special_valentine',
    'children': 'special_children', 'hangul': 'special_hangul',
    'halloween': 'special_halloween', 'christmas_eve': 'special_christmas_eve',
    'christmas': 'special_christmas', 'year_end': 'special_year_end',
    'public_holiday': PUBLIC_HOLIDAY.key,
})


CITY_FESTIVAL_OBJECTS = MappingProxyType({
    'city_festival_'+kind: ObjectSpec('city_festival_'+kind,title,'특집','city_'+kind,color,1,1,24,30,title)
    for kind,title,color in (
        ('music','도시 음악 행사','#718FC5'),('film','도시 영화 행사','#B9AB88'),
        ('snow','도시 눈 행사','#A4C9DD'),('lights','도시 빛 행사','#E1A64E'),
        ('carnival','도시 카니발','#B57A9C'),('flowers','도시 꽃 행사','#D795A6'),
        ('culture','도시 문화 행사','#B79265'),('balloon','도시 열기구 행사','#CF8D62'))
})


def special_for_date(value, country='KR', city_ref=None):
    """고정 특집·발표 도시 일정·국가 공휴일 순서로만 특집을 고릅니다."""
    country=normalize_country(country)
    event=event_for_date(value,country)
    if event is not None and event['kind'] != 'public_holiday':
        key=KIND_KEYS.get(event['kind'],PUBLIC_HOLIDAY.key)
        return replace(subject_for_id(key),name=event['title'],feature=event['kind'])
    row=SPECIAL_DATES.get((value.month,value.day))
    if country!='KR' and (value.month,value.day) in ((5,5),(10,9)):row=None
    if row:return SPECIAL_OBJECTS[row[0]]
    if city_ref is not None:
        from city_festivals import city_events_for_date
        rows=city_events_for_date(value,city_ref,country)
        rows=[row for row in rows if row.get('status')=='announced' and row.get('date_precision')=='day'
              and row.get('date_evidence') in ('official_api_consistent','official_page_crosschecked')
              and (not row.get('time_conflict') or row.get('date_evidence')=='official_page_crosschecked')]
        if rows:
            selected=sorted(rows,key=lambda row:row['id'])[0]
            key='city_festival_'+selected.get('kind','culture')
            template=CITY_FESTIVAL_OBJECTS.get(key,CITY_FESTIVAL_OBJECTS['city_festival_culture'])
            return replace(template,name=selected['title'],feature=selected.get('kind','culture'))
    if event is not None:return replace(PUBLIC_HOLIDAY,name=event['title'],feature=event['kind'])
    return None


def subject_for_id(key):
    if key==PUBLIC_HOLIDAY.key:return PUBLIC_HOLIDAY
    if key in CITY_FESTIVAL_OBJECTS:return CITY_FESTIVAL_OBJECTS[key]
    return SPECIAL_OBJECTS[key] if key in SPECIAL_OBJECTS else OBJECTS[key]
