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
    ('H','수소','#79c9e8','#c8efff'), ('He','헬륨','#d4adf5','#eedcff'),
    ('Li','리튬','#ee91a9','#ffd4df'), ('Be','베릴륨','#90cdb7','#d4f4e8'),
    ('B','붕소','#c9a78e','#f3dfcf'), ('C','탄소','#9baec8','#d9e6fa'),
    ('N','질소','#92a8ed','#d8e1ff'), ('O','산소','#e99eac','#ffdae2'),
    ('F','플루오린','#b1d998','#e4f7d6'), ('Ne','네온','#eea77d','#ffe0c7'),
    ('Na','나트륨','#e1c378','#fff0bf'), ('Mg','마그네슘','#a6c7dc','#dfedf7'),
    ('Al','알루미늄','#a5b9cf','#e1ebf6'), ('Si','규소','#aba5dc','#e4dfff'),
    ('P','인','#e5ad8c','#ffe0ce'), ('S','황','#dbcf7d','#fff7c8'),
    ('Cl','염소','#b5d290','#e5f6ce'), ('Ar','아르곤','#b59ce7','#e7d9ff'),
    ('K','칼륨','#c49de4','#eed8ff'), ('Ca','칼슘','#e4b08a','#ffe3ca'),
    ('Sc','스칸듐','#9ac9c9','#d6f3f2'), ('Ti','타이타늄','#a5b8d8','#dde9ff'),
    ('V','바나듐','#aeabd6','#e4e1fc'), ('Cr','크로뮴','#90c8ad','#d2f3e2'),
    ('Mn','망가니즈','#c49abb','#f2d5e9'), ('Fe','철','#cd9979','#ffe0bd'),
    ('Co','코발트','#809fde','#d6e3ff'), ('Ni','니켈','#9fc5ad','#dbf2e3'),
    ('Cu','구리','#dc9c79','#ffdcc4'), ('Zn','아연','#9abacb','#d9edf5'),
    ('Ga','갈륨','#a7b5e0','#e0e7ff'),
)
ELEMENTS = tuple(Element(index,symbol,name,color,accent)
                 for index,(symbol,name,color,accent) in enumerate(_ROWS,1))


def daily_element(when=None):
    """매 호출 실제 날짜를 다시 읽어 자정·절전 복귀·시계 되돌림을 반영합니다."""
    value = datetime.now(KST) if when is None else when
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('원소 날짜에는 시간대가 있는 datetime이 필요합니다.')
    return ELEMENTS[value.astimezone(KST).day-1]
