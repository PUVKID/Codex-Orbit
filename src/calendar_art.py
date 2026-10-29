"""2026~2099년의 날짜별 조형 규칙입니다. 외부 데이터와 계정 정보를 사용하지 않습니다."""
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import hashlib
import colorsys
import calendar
from functools import lru_cache
from calendar_catalog import OBJECTS, collection_for_month, all_collections

FIRST_DATE = date(2026,1,1)
LAST_DATE = date(2099,12,31)
KST = timezone(timedelta(hours=9))
THEMES = tuple(row.title for row in all_collections())


@dataclass(frozen=True)
class Design:
    date: date
    title: str
    theme: str
    key: str
    accent: str
    seed: int
    variant: int
    year_variant: float
    object_id: str
    shape_recipe: str
    anchor_id: str
    companion_id: str
    composition: str


def current_date():
    """호스트의 현지 시간대와 무관하게 한국 날짜를 사용합니다."""
    return datetime.now(KST).date()


def _seed_for_date(value):
    return int.from_bytes(hashlib.sha256(('calendar-art-v1:'+value.isoformat()).encode('ascii')).digest()[:8],'big')


def _raw_accent(value, subject, seed):
    rgb=tuple(int(subject.color[i:i+2],16)/255 for i in (1,3,5))
    h,s,v=colorsys.rgb_to_hsv(*rgb)
    color=colorsys.hsv_to_rgb((h+(seed%29-14)/1000)%1,min(.72,s+.025*(value.day%3)),min(.96,v+.004*(value.day%7)))
    return tuple(round(channel*255) for channel in color)


@lru_cache(maxsize=888)
def _month_palette(year, month):
    """반올림 충돌만 가장 가까운 미사용 RGB로 옮기고 월별 결과를 불변 보관합니다."""
    collection=collection_for_month(year,month)
    used=set();colors=[]
    for day in range(1,calendar.monthrange(year,month)[1]+1):
        value=date(year,month,day)
        rgb=_raw_accent(value,OBJECTS[collection.subjects[day-1]],_seed_for_date(value))
        if rgb in used:
            # 월 최대31색보다 후보가 많으며 8비트 경계의 모서리에서도 64개가 남습니다.
            offsets=sorted(((r,g,b) for r in range(-3,4) for g in range(-3,4) for b in range(-3,4)),
                           key=lambda x:(sum(v*v for v in x),abs(x[0])+abs(x[1]),x))
            for delta in offsets:
                candidate=tuple(a+b for a,b in zip(rgb,delta))
                if all(0<=channel<=255 for channel in candidate) and candidate not in used:
                    rgb=candidate
                    break
            else:raise RuntimeError('날짜별 미사용 색 후보를 찾지 못했습니다.')
        used.add(rgb);colors.append('#'+''.join(f'{channel:02X}' for channel in rgb))
    return tuple(colors)


# 초기화 한 번에 유한한 888개 월 색상을 준비합니다. 화면 조회는 직접 인덱스만 사용합니다.
for _year in range(2026,2100):
    for _month in range(1,13):
        _month_palette(_year,_month)


@lru_cache(maxsize=4)
def design_for_date(value):
    """유효한 날짜만 허용하며 지원 범위 밖을 다른 날짜로 몰래 대체하지 않습니다."""
    if type(value) is not date:
        raise TypeError('조형 날짜는 datetime.date여야 합니다.')
    if not FIRST_DATE <= value <= LAST_DATE:
        raise ValueError('날짜별 조형 지원 범위는 2026-01-01부터 2099-12-31까지입니다.')
    key=value.isoformat()
    seed=_seed_for_date(value)
    collection=collection_for_month(value.year,value.month)
    subject=OBJECTS[collection.subjects[value.day-1]]
    # 기본색에 가까운 범위에서 날짜별 색을 정하며 형상 차이의 대용으로 쓰지 않습니다.
    accent=_month_palette(value.year,value.month)[value.day-1]
    return Design(value,subject.name,collection.title,key,accent,seed,
                  value.day-1,((value.year-2026)+(seed%1000003)/1000003)/74,
                  subject.key,subject.recipe,collection.anchor_id,collection.companion_id,collection.composition)


def all_designs():
    """현재 모델만 렌더하며 이 반복자는 작은 카탈로그를 작성할 때만 사용합니다."""
    value=FIRST_DATE
    while value<=LAST_DATE:
        yield design_for_date(value)
        value+=timedelta(days=1)
