"""한국 날짜의1~31일에 대응하는 원소와 디자인 영감 팔레트입니다."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
SOURCES = ('https://pml.nist.gov/PhysRefData/Elements/per.html',
           'https://periodic-table.rsc.org/element/26/Iron')
PALETTE_NOTE = '원소에서 영감받은 디자인 색이며 실제 원소·불꽃색이나 전자배치 재현이 아닙니다.'


@dataclass(frozen=True)
class Element:
    number: int
    symbol: str
    name: str
    color: str
    accent: str


# 번호·기호는 NIST 표를 따르며 색은 시각 디자인을 위한 별도 선택입니다.
_ROWS = (
    ('H','수소','#a0cce4','#dcecff'), ('He','헬륨','#b4bee3','#dcecff'),
    ('Li','리튬','#a9bedc','#dcecff'), ('Be','베릴륨','#9fcbd6','#dcecff'),
    ('B','붕소','#a6bfd5','#dcecff'), ('C','탄소','#a1b7d2','#dcecff'),
    ('N','질소','#9db9df','#dcecff'), ('O','산소','#b1c4df','#dcecff'),
    ('F','플루오린','#a7cbd5','#dcecff'), ('Ne','네온','#a4bfdc','#dcecff'),
    ('Na','나트륨','#aec8dd','#dcecff'), ('Mg','마그네슘','#a6c7dc','#dcecff'),
    ('Al','알루미늄','#a5b9cf','#dcecff'), ('Si','규소','#afaee0','#dcecff'),
    ('P','인','#a9c2db','#dcecff'), ('S','황','#b0ccdf','#dcecff'),
    ('Cl','염소','#accdda','#dcecff'), ('Ar','아르곤','#b6b8df','#dcecff'),
    ('K','칼륨','#b6b5dc','#dcecff'), ('Ca','칼슘','#acc5d9','#dcecff'),
    ('Sc','스칸듐','#9fc8dc','#dcecff'), ('Ti','타이타늄','#a5b8d8','#dcecff'),
    ('V','바나듐','#aeabd6','#dcecff'), ('Cr','크로뮴','#9ec4d7','#dcecff'),
    ('Mn','망가니즈','#b2badb','#dcecff'), ('Fe','철','#a3bdd7','#dcecff'),
    ('Co','코발트','#809fde','#dcecff'), ('Ni','니켈','#a4c3d6','#dcecff'),
    ('Cu','구리','#a6bfd7','#dcecff'), ('Zn','아연','#9abacb','#dcecff'),
    ('Ga','갈륨','#a7b5e0','#dcecff'),
)
ELEMENTS = tuple(Element(index,symbol,name,color,accent)
                 for index,(symbol,name,color,accent) in enumerate(_ROWS,1))


def daily_element(when=None):
    """매 호출 실제 날짜를 다시 읽어 자정·절전 복귀·시계 되돌림을 반영합니다."""
    value = datetime.now(KST) if when is None else when
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('원소 날짜에는 시간대가 있는 datetime이 필요합니다.')
    return ELEMENTS[value.astimezone(KST).day-1]
