"""실제 대상 이름과 조형 특징을 연결하는 편집 사전입니다.

정밀 도감 모델이 아니라 주요 구조를 드러내는 장식용 해석입니다.
37개 주제 모티프와 24개 동반 모티프의 역할 있는 조합을 사용합니다.
"""
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class ObjectSpec:
    key: str
    name: str
    category: str
    recipe: str
    color: str
    count: int
    layers: int
    width: float
    length: float
    feature: str


# 개수와 비율은 장식용 메시의 형태 지시값이며 종의 불변 생물학 수치가 아닙니다.
_FLOWERS = (
 ('rose','장미','rosette','#D95D83',7,4,9,13,'겹쳐 감기는 꽃잎'),
 ('tulip','튤립','cup','#ED718B',6,1,10,22,'위로 모인 컵형 꽃잎'),
 ('daffodil','수선화','trumpet','#F1CC54',6,1,6,16,'바깥 꽃잎과 돌출된 중앙 나팔'),
 ('lily','백합','bloom','#E8DBEC',6,1,5,23,'길게 뻗은 여섯 꽃잎과 수술'),
 ('lotus','연꽃','rosette','#E898B8',8,3,8,18,'넓게 펼친 여러 겹 꽃잎'),
 ('cherry','벚꽃','bloom','#F0B8CD',5,1,9,12,'둥근 다섯 꽃잎'),
 ('plum','매화','bloom','#EE92B4',5,1,7,10,'작은 다섯 꽃잎과 긴 수술'),
 ('camellia','동백꽃','rosette','#CA4863',7,2,12,13,'두꺼운 둥근 꽃잎과 노란 중심'),
 ('magnolia','목련','cup','#EAE3D6',9,1,7,23,'위로 선 긴 꽃잎'),
 ('hibiscus','무궁화','bloom','#DFA4D5',5,1,12,17,'넓은 꽃잎과 길게 나온 중심 기둥'),
 ('sunflower','해바라기','disc','#EEC145',18,1,4,17,'큰 원반과 좁은 방사 꽃잎'),
 ('daisy','데이지','disc','#E8E3D3',16,1,3,13,'노란 원반 둘레 흰 꽃잎'),
 ('cosmos','코스모스','bloom','#D783B7',8,1,8,17,'얇고 넓게 펼친 여덟 꽃잎'),
 ('chrysanthemum','국화','rosette','#DDAE60',16,4,3,16,'촘촘한 여러 겹의 좁은 꽃잎'),
 ('gerbera','거베라','disc','#ED8E66',20,2,3,19,'큰 원반 둘레 여러 겹 꽃잎'),
 ('dahlia','달리아','rosette','#C685C9',10,5,5,16,'기하적으로 겹친 뾰족한 꽃잎'),
 ('zinnia','백일홍','rosette','#DB6D89',12,3,5,13,'낮게 층진 둥근 꽃머리'),
 ('marigold','금잔화','disc','#E8A047',15,2,4,15,'주황색 방사 꽃잎'),
 ('carnation','카네이션','rosette','#E19EBC',11,4,7,11,'촘촘하고 부풀어 오른 겹꽃'),
 ('peony','모란','rosette','#CD6FAD',9,4,11,15,'크고 넓은 겹꽃잎'),
 ('poppy','양귀비','bloom','#E76C5C',4,1,15,17,'넓은 네 꽃잎과 어두운 중심'),
 ('anemone','아네모네','bloom','#AA89D8',7,1,9,17,'꽃잎에 대비되는 짙은 중심'),
 ('ranunculus','라넌큘러스','rosette','#EBC99A',12,5,7,12,'동심원처럼 겹쳐진 얇은 꽃잎'),
 ('bellflower','도라지꽃','star_bloom','#968BD9',5,1,8,19,'끝이 뾰족한 별 모양 꽃잎'),
 ('morning_glory','나팔꽃','funnel','#A582D6',5,1,17,25,'하나로 연결된 긴 나팔형 꽃'),
 ('petunia','페튜니아','funnel','#D784C7',5,1,22,16,'넓은 입구와 짧은 깔때기'),
 ('foxglove','디기탈리스','spike','#CB8DC3',7,1,5,10,'긴 줄기에 매달린 종형 꽃 무리'),
 ('lavender','라벤더','spike','#A499D7',12,1,3,5,'가느다란 줄기 끝의 작은 꽃 이삭'),
 ('hydrangea','수국','umbel','#9EBCDF',13,1,5,6,'작은 꽃들이 모인 둥근 꽃차례'),
 ('lilac','라일락','spike','#B7A0D9',10,1,4,6,'원뿔형으로 모인 작은 꽃 무리'),
 ('gujeolcho','구절초','disc','#EFE8DE',12,1,3,17,'노란 중심 둘레 길고 흰 꽃잎'),
)

_FRUITS = (
 ('apple','사과','round_fruit','#D86B65',5,1,23,22,'둥근 몸체와 움푹한 꼭지'),
 ('pear','배','pear','#D8BE75',1,1,22,27,'위쪽이 가늘고 아래가 넓은 몸체'),
 ('quince','모과','pear','#D6BD51',5,1,20,29,'울퉁불퉁하고 길쭉한 몸체'),
 ('peach','복숭아','lobed_fruit','#E5A6A2',2,1,23,22,'가운데 골이 있는 두 갈래 둥근 몸체'),
 ('apricot','살구','lobed_fruit','#E5AB62',2,1,18,18,'작고 둥근 두 갈래 열매'),
 ('plum_fruit','자두','round_fruit','#A26A9F',1,1,18,23,'세로로 긴 둥근 열매'),
 ('cherry_fruit','체리','paired_fruit','#C75B78',2,1,11,12,'긴 꼭지에 매달린 두 열매'),
 ('grape','포도','cluster','#9782BD',4,4,8,9,'아래로 좁아지는 송이'),
 ('muscat','청포도','cluster','#B6C977',5,3,8,11,'연녹색의 길쭉한 포도알'),
 ('orange','오렌지','citrus','#E7A14D',10,1,23,23,'둥근 감귤과 방사 단면'),
 ('mandarin','귤','citrus','#EAAF4B',9,1,24,18,'위아래가 납작한 감귤'),
 ('lemon','레몬','citrus','#E3D36C',8,1,16,26,'양끝이 좁은 긴 감귤'),
 ('lime','라임','citrus','#B8CB79',7,1,17,20,'작고 녹색인 감귤'),
 ('grapefruit','자몽','citrus','#EBA18F',12,1,27,25,'큰 감귤과 분홍빛 단면'),
 ('strawberry','딸기','seeded_fruit','#D87583',14,1,19,26,'아래로 뾰족한 몸체와 표면 씨'),
 ('raspberry','라즈베리','berry','#CB829B',8,3,5,6,'작은 알갱이가 모인 속빈 열매'),
 ('blackberry','블랙베리','berry','#817CA8',7,4,5,6,'세로로 긴 작은 알갱이 무리'),
 ('blueberry','블루베리','cluster','#849BCB',3,2,10,10,'푸른 열매와 별 모양 꽃받침'),
 ('banana','바나나','banana','#E2CE75',3,1,6,28,'휘어진 긴 열매가 모인 송이'),
 ('pineapple','파인애플','pineapple','#CDB66B',8,5,21,27,'마름모 결 몸체와 뾰족한 잎관'),
 ('mango','망고','pear','#E4B16D',1,1,22,30,'한쪽으로 기운 긴 열매'),
 ('papaya','파파야','seeded_fruit','#E9A976',20,1,19,31,'길쭉한 열매와 중앙 씨'),
 ('kiwi','키위','citrus','#ADC781',16,1,19,24,'긴 타원과 방사상 씨'),
 ('watermelon','수박','striped_fruit','#86B594',10,1,28,25,'큰 둥근 몸체의 세로 줄무늬'),
 ('melon','멜론','striped_fruit','#B4C88C',12,1,25,24,'둥근 몸체의 격자형 결'),
 ('persimmon','감','lobed_fruit','#D99D62',4,1,23,20,'네 갈래 꽃받침과 납작한 열매'),
 ('pomegranate','석류','crowned_fruit','#D58C87',6,1,23,24,'왕관처럼 뻗은 꽃받침'),
 ('fig','무화과','pear','#B793B6',1,1,23,26,'가느다란 목과 넓은 밑부분'),
 ('starfruit','스타프루트','starfruit','#DBCD7C',5,1,22,29,'다섯 개의 길게 솟은 능선'),
 ('dragonfruit','용과','dragonfruit','#DA8DB5',7,3,21,27,'타원 몸체를 감싸는 뾰족한 비늘'),
 ('coconut','코코넛','round_fruit','#B39C7F',3,1,25,28,'거친 타원형 껍질과 세 발아구'),
)

_LEAVES = (
 ('maple','단풍나무 잎','palmate','#DDA27E',7,1,9,25,'손바닥처럼 갈라진 뾰족한 잎'),
 ('ginkgo','은행나무 잎','fan','#D6C478',9,1,22,25,'가운데가 갈라진 부채꼴'),
 ('oak','참나무 잎','lobed_leaf','#A8BE91',7,1,12,29,'깊게 굴곡진 긴 잎'),
 ('birch','자작나무 잎','leaf','#B8CC99',9,1,19,25,'끝이 뾰족한 삼각형 잎'),
 ('beech','너도밤나무 잎','leaf','#A1BF96',8,1,16,27,'물결 가장자리의 타원 잎'),
 ('elm','느릅나무 잎','leaf','#9ABD8A',11,1,17,25,'비대칭 밑부분과 톱니 가장자리'),
 ('willow','버드나무 잎','leaf','#A6C7AE',10,1,6,34,'아주 가늘고 긴 잎'),
 ('olive','올리브 잎','leaf','#A0B7A2',6,1,8,27,'좁고 은빛인 타원 잎'),
 ('eucalyptus','유칼립투스 잎','round_leaf','#9BC1B6',6,1,21,22,'둥근 은청색 잎'),
 ('poplar','포플러 잎','leaf','#A6C59D',7,1,21,25,'넓은 삼각형 잎'),
 ('linden','보리수 잎','heart_leaf','#A8C694',9,1,23,27,'넓은 심장 모양 잎'),
 ('ivy','담쟁이 잎','palmate','#92B5A0',3,1,12,26,'세 갈래로 나뉜 잎'),
 ('grape_leaf','포도나무 잎','palmate','#A2BE85',5,1,14,24,'넓은 다섯 갈래 잎'),
 ('fig_leaf','무화과 잎','palmate','#9CB893',5,1,10,29,'손가락처럼 길게 갈라진 잎'),
 ('monstera','몬스테라 잎','split_leaf','#8BB7A3',7,1,23,31,'깊게 갈라지고 구멍이 난 잎'),
 ('philodendron','필로덴드론 잎','heart_leaf','#80B29C',8,1,20,31,'길쭉한 심장 모양 잎'),
 ('lotus_leaf','연잎','round_leaf','#A0C4AE',12,1,27,27,'방사상 잎맥의 큰 둥근 잎'),
 ('nasturtium','한련화 잎','round_leaf','#ACCA9A',9,1,23,22,'중앙에서 퍼지는 잎맥'),
 ('clover','클로버','compound','#9FC18B',3,1,12,15,'세 작은 잎이 모인 구조'),
 ('oxalis','괭이밥','compound','#BBA1BC',3,1,14,17,'세 개의 심장형 작은 잎'),
 ('horse_chestnut','칠엽수 잎','compound','#A5C58F',7,1,8,23,'한 점에서 퍼지는 일곱 작은 잎'),
 ('ash','물푸레나무 잎','pinnate','#A0BD8E',7,1,9,15,'중앙 잎축 양옆의 작은 잎'),
 ('rowan','마가목 잎','pinnate','#B4BE84',11,1,7,13,'촘촘한 깃꼴 작은 잎'),
 ('fern','고사리 잎','fern','#A0C3A4',13,1,6,15,'반복 분지하는 깃꼴 잎'),
 ('palm','야자수 잎','palm','#B0C695',13,1,3,30,'한 점에서 부채처럼 퍼지는 긴 갈래'),
 ('bamboo','대나무 잎','pinnate','#AEC79B',5,1,4,23,'좁은 작은 잎이 붙은 가는 가지'),
 ('pine','소나무 바늘잎','needle','#8EB4A1',2,5,1,29,'쌍으로 묶여 뻗는 바늘잎'),
 ('fir','전나무 가지','needle','#8AAE9B',12,2,1,17,'가지 양옆의 짧은 바늘잎'),
 ('rosemary','로즈메리 가지','needle','#A5C5B8',9,2,2,13,'가는 가지에 달린 좁은 잎'),
 ('mint','민트 잎','leaf','#9CC7AD',12,1,18,23,'톱니 가장자리와 도드라진 잎맥'),
 ('sage','세이지 잎','leaf','#B1C1BA',8,1,13,29,'부드러운 은회색의 긴 잎'),
)

_MUSIC = (
 ('violin','바이올린','bowed','#C4A281',4,1,14,24,'잘록한 몸통과 긴 목'),
 ('viola','비올라','bowed','#B99B80',4,1,16,26,'바이올린보다 넓은 몸통'),
 ('cello','첼로','bowed','#B79379',4,1,19,29,'큰 몸통과 하단 지지봉'),
 ('bass','콘트라베이스','bowed','#A9907D',4,1,21,32,'큰 어깨와 길게 솟은 목'),
 ('guitar','기타','guitar','#D2B78C',6,1,18,25,'잘록한 울림통과 원형 소리구멍'),
 ('ukulele','우쿨렐레','guitar','#D8BF98',4,1,15,20,'작은 울림통과 짧은 목'),
 ('mandolin','만돌린','lute','#C4AD91',8,1,17,23,'물방울형 울림통'),
 ('lute','류트','lute','#D3B995',6,1,20,24,'둥근 배 모양 울림통과 꺾인 목'),
 ('harp','하프','harp','#DBC59C',12,1,26,32,'세 모서리 틀과 길이가 다른 현'),
 ('lyre','리라','lyre','#D4B38F',7,1,23,24,'두 팔과 가로대 사이의 현'),
 ('piano','그랜드 피아노','piano','#A3A5B8',12,1,28,22,'곡선 몸체와 가로 건반'),
 ('accordion','아코디언','accordion','#BA8F9F',10,1,27,19,'양쪽 상자와 가운데 주름통'),
 ('xylophone','실로폰','bars','#B1C0C5',8,1,28,20,'길이가 다른 나란한 음판'),
 ('marimba','마림바','bars','#C5AD92',12,2,30,22,'음판 아래 긴 공명관'),
 ('kalimba','칼림바','bars','#D5C4A4',9,1,19,23,'작은 상자 위 길이가 다른 금속 혀'),
 ('flute','플루트','flute','#C8D8DC',7,1,3,34,'가는 관과 나란한 키'),
 ('recorder','리코더','flute','#D8C7A7',7,1,4,31,'곧은 관의 구멍과 부리형 입구'),
 ('clarinet','클라리넷','reed','#A4ACBB',8,1,4,34,'키가 달린 관과 작은 종형 끝'),
 ('oboe','오보에','reed','#A6B3BB',9,1,3,33,'가느다란 관과 좁은 리드'),
 ('bassoon','바순','reed','#BB9B85',7,2,5,34,'긴 이중 관과 굽은 입관'),
 ('saxophone','색소폰','sax','#D6BD88',7,1,9,29,'굽은 관과 넓은 종형 끝'),
 ('trumpet','트럼펫','brass','#D6C391',3,1,12,26,'접힌 관과 세 밸브'),
 ('trombone','트롬본','brass','#D0BB91',2,1,10,34,'길게 왕복하는 슬라이드관'),
 ('horn','호른','horn','#CDBD96',3,1,24,23,'둥글게 감긴 관과 벌어진 종'),
 ('tuba','튜바','brass','#CEB88C',4,2,20,31,'굵은 접힌 관과 위로 열린 종'),
 ('snare','스네어 드럼','drum','#A4B8CB',10,1,25,13,'낮고 넓은 원통 북'),
 ('bongo','봉고','drum','#C9AA8E',2,2,16,22,'높이가 다른 두 원통 북'),
 ('timpani','팀파니','bowl_drum','#C8B59D',8,1,27,24,'반구형 몸체와 넓은 북면'),
 ('tambourine','탬버린','tambourine','#D4B691',8,1,25,6,'얇은 원형 틀 둘레의 작은 징'),
 ('triangle','트라이앵글','triangle','#C2D1D5',3,1,27,28,'한 모서리가 열린 삼각 금속봉'),
 ('handbell','핸드벨','bell','#D9C591',1,1,19,26,'종형 몸체와 위쪽 손잡이'),
)


def _objects(rows, category):
    return tuple(ObjectSpec(row[0],row[1],category,*row[2:]) for row in rows)


POOLS = {'꽃': _objects(_FLOWERS,'꽃'), '열매': _objects(_FRUITS,'열매'),
         '잎': _objects(_LEAVES,'잎'), '악기': _objects(_MUSIC,'악기')}
OBJECTS = {obj.key:obj for pool in POOLS.values() for obj in pool}

# 주제와 동반 대상은 역할을 분리하고 서로 겹치지 않아 역순 쌍의 중복이 없습니다.
ANCHORS = tuple(OBJECTS[key] for key in (
 'rose','tulip','daffodil','lily','lotus','cherry','plum','camellia','magnolia','hibiscus',
 'apple','pear','quince','peach','apricot','plum_fruit','cherry_fruit','grape','muscat',
 'maple','ginkgo','oak','birch','beech','elm','willow','olive','eucalyptus',
 'violin','viola','cello','bass','guitar','ukulele','mandolin','lute','harp'))
COMPANIONS = tuple(OBJECTS[key] for key in (
 'sunflower','daisy','cosmos','chrysanthemum','gerbera','gujeolcho',
 'orange','mandarin','lemon','lime','grapefruit','strawberry',
 'poplar','linden','ivy','grape_leaf','fig_leaf','monstera',
 'lyre','piano','accordion','xylophone','marimba','kalimba'))

# 네 범주의 실제 조형 관계에 맞춰 제목과 세 물체의 배치를 함께 선택합니다.
COMPOSITIONS = {
 ('꽃','꽃'):('꽃의 화원','bouquet'), ('꽃','열매'):('꽃과 열매의 정물','diagonal'),
 ('꽃','잎'):('잎이 감싼 화원','shelter'), ('꽃','악기'):('꽃의 실내악','stage'),
 ('열매','꽃'):('꽃이 핀 과수원','bouquet'), ('열매','열매'):('열매의 정물','triangle'),
 ('열매','잎'):('잎과 수확의 정물','shelter'), ('열매','악기'):('수확의 음악실','stage'),
 ('잎','꽃'):('잎과 꽃의 정원','diagonal'), ('잎','열매'):('숲의 수확','triangle'),
 ('잎','잎'):('잎의 표본 정원','fan'), ('잎','악기'):('숲의 음악실','stage'),
 ('악기','꽃'):('꽃으로 꾸민 연주실','stage'), ('악기','열매'):('음악과 열매의 정물','diagonal'),
 ('악기','잎'):('잎으로 꾸민 연주실','shelter'), ('악기','악기'):('실내악 편성','stage'),
}
COMPOSITION_NAMES = {'bouquet':'꽃다발형','diagonal':'대각선형','shelter':'감싸는 형태',
                     'stage':'연주대형','triangle':'삼각형 정물','fan':'부채형'}


@dataclass(frozen=True)
class Collection:
    key: str
    title: str
    anchor_id: str
    companion_id: str
    composition: str
    description: str
    subjects: tuple


def joining_particle(name):
    """마지막 한글 음절의 받침에 맞춰 대상 이름을 연결합니다."""
    last=ord(name[-1])
    return '과' if 0xAC00 <= last <= 0xD7A3 and (last-0xAC00)%28 else '와'


@lru_cache(maxsize=888)
def collection_for_month(year, month):
    index=(year-2026)*12+month-1
    if not 0 <= index < 888 or not 1 <= month <= 12:
        raise ValueError('연월 컬렉션은 2026년 1월부터 2099년 12월까지입니다.')
    # 서로소 순회로 이웃한 달도 주제와 동반 대상이 함께 바뀝니다.
    pair=(index*113)%888
    anchor=ANCHORS[pair//24]; companion=COMPANIONS[pair%24]
    context,composition=COMPOSITIONS[anchor.category,companion.category]
    primary=POOLS[anchor.category]
    # 날짜별 주연은 그 달 주제의 분류에 속하는 서로 다른 실제 대상 31종입니다.
    start=(pair//24+pair%24*7)%31
    subjects=tuple(primary[(start+i*11)%31].key for i in range(31))
    title=f'{anchor.name}{joining_particle(anchor.name)} {companion.name} · {context}'
    description=f'날짜별 {anchor.category} 주연, 왼쪽의 {anchor.name}, 오른쪽의 {companion.name}을 {COMPOSITION_NAMES[composition]} 구성으로 함께 전시합니다.'
    return Collection(f'{year:04d}-{month:02d}',title,anchor.key,companion.key,composition,description,subjects)


def all_collections():
    return tuple(collection_for_month(year,month) for year in range(2026,2100) for month in range(1,13))
