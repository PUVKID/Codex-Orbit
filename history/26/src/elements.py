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
    ('H','수소','#53c9ef','#c3ecf9'), ('He','헬륨','#b3a0f5','#e4defc'),
    ('Li','리튬','#ef718c','#f9cdd7'), ('Be','베릴륨','#69c8b5','#caece5'),
    ('B','붕소','#a77bcb','#e0d1ed'), ('C','탄소','#99ddf4','#dbf3fb'),
    ('N','질소','#668ce9','#c9d7f7'), ('O','산소','#e96d7e','#f7ccd2'),
    ('F','플루오린','#a1cf62','#deeec8'), ('Ne','네온','#f68d58','#fcd7c5'),
    ('Na','나트륨','#f1c455','#faeac4'), ('Mg','마그네슘','#c4dbe9','#eaf2f7'),
    ('Al','알루미늄','#9ebbd5','#dde7f0'), ('Si','규소','#7889d9','#d0d6f2'),
    ('P','인','#dc8167','#f3d3ca'), ('S','황','#e9d34a','#f7f0c0'),
    ('Cl','염소','#84c754','#d4ebc3'), ('Ar','아르곤','#a197e5','#dedbf6'),
    ('K','칼륨','#c284dd','#ead4f3'), ('Ca','칼슘','#ddd0a6','#f3efe0'),
    ('Sc','스칸듐','#77bdc8','#cfe8ec'), ('Ti','타이타늄','#96adce','#dae2ee'),
    ('V','바나듐','#7b83cb','#d1d4ed'), ('Cr','크로뮴','#69b6ae','#cae5e3'),
    ('Mn','망가니즈','#b67db5','#e5d2e5'), ('Fe','철','#b87561','#e6cfc8'),
    ('Co','코발트','#477bd9','#bfd1f2'), ('Ni','니켈','#91b59b','#d8e5dc'),
    ('Cu','구리','#d38951','#f0d6c2'), ('Zn','아연','#81acc2','#d3e2ea'),
    ('Ga','갈륨','#a7c3e4','#e0eaf6'),
)
ELEMENTS = tuple(Element(index,symbol,name,color,accent)
                 for index,(symbol,name,color,accent) in enumerate(_ROWS,1))


def daily_element(when=None):
    """매 호출 실제 날짜를 다시 읽어 자정·절전 복귀·시계 되돌림을 반영합니다."""
    value = datetime.now(KST) if when is None else when
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('원소 날짜에는 시간대가 있는 datetime이 필요합니다.')
    return ELEMENTS[value.astimezone(KST).day-1]
