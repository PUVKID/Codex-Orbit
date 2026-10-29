"""2026~2099년의 날짜별 조형 규칙입니다. 외부 데이터와 계정 정보를 사용하지 않습니다."""
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import hashlib

FIRST_DATE = date(2026,1,1)
LAST_DATE = date(2099,12,31)
KST = timezone(timedelta(hours=9))
THEMES = ('꽃','보석','나비','물과 비','숲','바다','우주','과일','음악','가을','빛과 건축','겨울')
ACCENTS = ('#f3a8c5','#b6a1f2','#b6a4f7','#83c9ed','#83c7a4','#83d6d1',
           '#a3adf0','#edb58e','#ccb0ef','#dfad7d','#d4d6ee','#b7dcea')
FLOWER_FORMS = ('햇살꽃','봉오리','겹연꽃','종꽃','나팔꽃','동백빛','백합빛')


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


def current_date():
    """호스트의 현지 시간대와 무관하게 한국 날짜를 사용합니다."""
    return datetime.now(KST).date()


def design_for_date(value):
    """유효한 날짜만 허용하며 지원 범위 밖을 다른 날짜로 몰래 대체하지 않습니다."""
    if type(value) is not date:
        raise TypeError('조형 날짜는 datetime.date여야 합니다.')
    if not FIRST_DATE <= value <= LAST_DATE:
        raise ValueError('날짜별 조형 지원 범위는 2026-01-01부터 2099-12-31까지입니다.')
    key=value.isoformat()
    seed=int.from_bytes(hashlib.sha256(('calendar-art-v1:'+key).encode('ascii')).digest()[:8],'big')
    theme=THEMES[value.month-1]
    form=FLOWER_FORMS[(value.day-1)%7] if value.month==1 else theme
    return Design(value,f'{form} · {value.day:02d}',theme,key,ACCENTS[value.month-1],seed,
                  value.day-1,((value.year-2026)+(seed%1000003)/1000003)/74)


def all_designs():
    """현재 모델만 렌더하며 이 반복자는 작은 카탈로그를 작성할 때만 사용합니다."""
    value=FIRST_DATE
    while value<=LAST_DATE:
        yield design_for_date(value)
        value+=timedelta(days=1)
