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


def special_for_date(value, country='KR'):
    country=normalize_country(country)
    event=event_for_date(value,country)
    if event is not None:
        key=KIND_KEYS.get(event['kind'],PUBLIC_HOLIDAY.key)
        template=subject_for_id(key)
        return replace(template,name=event['title'],feature=event['kind'])
    row = SPECIAL_DATES.get((value.month, value.day))
    if country!='KR' and (value.month,value.day) in ((5,5),(10,9)):
        return None
    # 제공처에 공휴일이 없는 날의 고정 모티프는 계절 특집이며 법정 공휴일 표식이 아닙니다.
    return SPECIAL_OBJECTS[row[0]] if row else None


def subject_for_id(key):
    if key==PUBLIC_HOLIDAY.key:return PUBLIC_HOLIDAY
    return SPECIAL_OBJECTS[key] if key in SPECIAL_OBJECTS else OBJECTS[key]
