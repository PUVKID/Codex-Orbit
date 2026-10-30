"""앱이 소유한 문구만 번역하며 이벤트 원문은 호출자가 그대로 보존합니다."""
import re

_language = 'ko'

# 이 사전의 키는 앱 표시 문구이며 사용자 기록을 검색·치환하지 않습니다.
_EN = {
'회전 속도':'Rotation speed','{speed:g}배':'{speed:g}×','기본 1배 복원':'Reset to 1×',
'회전 속도 변경 실패: {error}':'Unable to change rotation speed: {error}',
'회전 속도만 변경합니다. 날짜와 시각은 그대로입니다.':'Changes rotation speed only. Date and time stay unchanged.',
'회전 속도는 GUI 메인 스레드에서만 변경할 수 있습니다.':'Rotation speed can only be changed on the GUI main thread.',
'회전 속도는 0.25~3배의 유한한 숫자여야 합니다.':'Rotation speed must be a finite number between 0.25× and 3×.',
'확인 불가':'Unavailable','미확인':'Unknown','없음':'None','최소':'Minimal','낮음':'Low','보통':'Medium','높음':'High','매우 높음':'Very high','최고':'Maximum',
'이전 기록 없음':'No previous record','기록 없음':'Not recorded','해당 없음':'Not applicable','모델·추론 확인 불가':'Model / reasoning unavailable','모델 확인 불가':'Model unavailable',
'모델':'Model','추론':'Reasoning','추론 강도':'Reasoning effort','이전 모델':'Previous model','이전 추론 강도':'Previous reasoning effort','이전':'Previous','새':'New','현재':'Current','변경 전':'Before','변경 후':'After',
'부모 조율':'Parent coordination','작업 분류':'Task triage','간단한 수정':'Quick changes','구현':'Implementation','심층 검토·구현':'In-depth implementation','독립 검증':'Independent verification','판단 재검토·수리':'Reassessment and repair','담당':'Assigned',
'새 작업 배정':'New task assigned','작업 재개':'Task resumed','작업 활동 관측':'Task activity observed','자식 작업자 첫 선택 설정 관측':'Initial child selection observed','채팅 선택 설정 첫 관측':'Initial chat selection observed','선택 설정':'Selected settings','새 작업자 배정 · 이전 작업자 교체':'New worker assigned · previous worker replaced','자식 작업자 첫 관측':'Initial child observation','첫 관측':'Initial observation','설정 관측 · 현재 값 확인 불가':'Settings observed · current value unavailable','모델 · 추론 강도 변경':'Model / reasoning effort changed','모델·추론 변경':'Model / reasoning changed','모델 변경':'Model changed','추론 강도 변경':'Reasoning effort changed','설정 유지':'Settings unchanged','설정 관측':'Settings observed',
'공개된 설명이 기록되지 않았습니다.':'No public explanation recorded.','공개된 작업 설명이 기록되지 않았습니다.':'No public task description recorded.','모델·추론 강도 선택 이유는 공개되지 않았습니다.':'No public model / reasoning selection rationale.','선택 이유: ':'Selection rationale: ',
'채팅 제목 확인 불가':'Chat title unavailable','채팅':'Chat','채팅 ID':'Chat ID','작업자 ID':'Worker ID','구분':'Type','자식 작업':'Child task','main 또는 부모 정보 미기록':'main / parent not recorded','역할':'Role','작업 이름':'Task name','부모 ID':'Parent ID','작업 경로':'Task path','제목 출처':'Title source','제목 확인 시각':'Title checked','호출 ID':'Call ID','활동 종류':'Activity type','맡긴 일':'Assigned task','작업 설명 출처':'Task source','활동 근거':'Activity evidence','요청 설정':'Requested settings','이유 호출 ID':'Rationale call ID','감지 시각':'Detected','원본 기록 시각':'Original record time','기록 종류':'Record type','공개 이유 원문':'Original public rationale','모델·추론 강도 선택 이유':'Model / reasoning selection rationale','근거 수준':'Evidence level','선택 설정 관측 근거':'Selection evidence','표시 기록':'Presentation record','앱 표시 요청; 사용자 수신 미확인':'Presentation requested; user receipt unconfirmed','로컬 기록과 공개 이유의 연결 근거입니다. 서버 모델 신원이나 비공개 추론을 증명하지 않습니다.':'Links local records to public explanations. Does not verify server model identity or private reasoning.',
'상세 이력 열기':'Open change history','종료':'Quit','언어':'Language','닫기':'Close','알림 닫기 · 이력은 유지됩니다':'Dismiss notification · history is preserved','이 변경 자세히 보기  ›':'View this change  ›','현재 설정 · ':'Current settings · ','→ 변경 후 · ':'→ After · ','확인되지 않음':'Unconfirmed','공개 설명: ':'Public explanation: ','변경 이유: ':'Change rationale: ','기록 다시 보기 · ':'History replay · ',
'Codex Orbit · 로컬 모델 변경 기록':'Codex Orbit · Local model change history','사용 한도 미확인':'Usage limit unknown','사용 한도':'Usage limits','계정 사용 한도':'Account usage limits','새로고침':'Refresh','계정 사용 한도 새로고침':'Refresh account usage limits','잔량 조회 준비 · 30초마다 자동 갱신':'Preparing usage lookup · refreshes every 30 seconds','계정 한도 미확인':'Account limit unknown','아직 조회하지 않음':'Not checked yet','조회 지연 · 이전 조회 값 · ':'Delayed lookup · previous value · ','  ·  최종 조회: ':'  ·  Last checked: ','  ·  30초 자동 갱신':'  ·  Refreshes every 30 seconds','잔량 미확인':'Usage unknown','초기화: ':'Resets: ',' · 이전 조회 값':' · Previous value','  ·  이전 조회 값':'  ·  Previous value',' · 이전 조회':' · Previous lookup','이전 조회 · ':'Previous lookup · ','계정 한도 미확인 · 남은 토큰 개수가 아닌 사용 한도 비율입니다.':'Account limit unknown · percentage of usage allowance, not a token count.',
'감시 준비 중':'Preparing monitor','알림 대기 0건':'No pending notifications','변경을 기다리고 있습니다':'Waiting for changes','변경 전  ·  —':'Before  ·  —','변경 후  ·  —':'After  ·  —','공개된 작업 설명을 기다립니다.':'Waiting for a public task description.','왜 맡겼나요? · 공개 설명':'Why this assignment? · Public explanation','첫 실행은 과거 기록을 기준선으로 읽으며 과거 알림을 만들지 않습니다.':'On first launch, existing records form the baseline without historical notifications.','변경 기록':'Change history','▸ 원문 · ID · 근거 펼치기':'▸ Expand original / IDs / evidence','▾ 원문 · ID · 근거 접기':'▾ Collapse original / IDs / evidence','변경을 감지하면 이곳에서 전후 값과 공개 이유를 확인할 수 있습니다.\n첫 실행은 과거 기록을 기준선으로 읽으며 과거 알림을 만들지 않습니다.':'Changes show before / after values and public explanations here.\nExisting records form the initial baseline without historical notifications.','모델·추론 강도가 바뀌었습니다':'Model and reasoning effort changed','모델이 바뀌었습니다':'Model changed','추론 강도가 바뀌었습니다':'Reasoning effort changed','감시 진단\n':'Monitor diagnostics\n',
'새 변경':'New change','감시 중':'Monitoring','확인 필요':'Check needed','잔량 ':'Remaining ','잔량 지연':'Usage delayed','위치 정보 없음':'Location unavailable','기온 미확인':'Temperature unknown','기온 조회 중':'Loading temperature','이전 {temperature:g}℃':'Previous {temperature:g}℃','네트워크 추정 지역: ':'Network-estimated region: ','\n지역 원문: ':'\nOriginal region: ','\n기온 출처: Open-Meteo · 위치: ipwho.is':'\nTemperature: Open-Meteo · Location: ipwho.is','\n제공 시각: ':'\nObservation time: ','\n조회 시각: ':'\nChecked: ','\n지명 출처: ':'\nPlace names: ','\n감시 상태: ':'\nMonitor status: ','Codex Orbit · 계정 한도 ':'Codex Orbit · Account allowance ','\n클릭: 기간별 잔량과 변경 이력 · 드래그: 이동':'\nClick: usage and history · Drag: move','Codex Orbit · 클릭: 상세 · 드래그: 이동 · 오른쪽/아래 가장자리: 크기 조절 · 우클릭: 기록/종료':'Codex Orbit · Click: details · Drag: move · Right/bottom edge: resize · Right-click: menu',
'조회 완료':'Lookup complete','잔량 조회 준비':'Preparing usage lookup','잔량 연결 중':'Connecting usage lookup','잔량 조회 중':'Loading usage','조회 지연 · 이전 조회 값':'Delayed lookup · previous value','초기화 미확인':'Reset time unknown','주간':'Weekly','5시간':'5 hours','기간 미확인':'Period unknown','제공된 계정 한도가 없습니다.':'No account limits provided.','계정 정보 갱신 · 잔량 다시 조회 중':'Account updated · reloading usage','기온 조회 준비':'Preparing weather lookup','기온 조회 완료':'Temperature updated','기온 정보 없음':'Temperature unavailable','위치 조회 중':'Loading location','위치 조회 실패':'Location lookup failed','네트워크 오류':'Network error','입체 이미지 준비 중':'Preparing 3D image','입체 이미지 표시 오류: ':'3D image display error: ','Codex Orbit 로고':'Codex Orbit logo','Codex Orbit · 실제3D 모션':'Codex Orbit · Real 3D motion','시각':'Time','공개 근거':'Public evidence',
'위치:':'Location:','파일 이름:':'File name:','파일 형식:':'File type:','취소':'Cancel','선택':'Choose','저장':'Save','열기':'Open','폴더:':'Folder:',
'감시 재시작 대기 · 이전 작업자 종료 후 최종 설정으로 자동 시작합니다.':'Monitor restart pending · starts after the previous worker stops.','감시 지연 · 이전 작업자가 종료 중입니다. 종료 후 다시 시작하세요.':'Monitor delayed · previous worker is stopping. Restart after it stops.','감시 준비 중 · 첫 진행 확인 대기':'Preparing monitor · waiting for first progress','감시 시작 실패 · 변경 기록의 진단을 확인하세요.':'Monitor startup failed · see history diagnostics.','감시 중단 · ':'Monitor stopped · ','자동 재시도 대기':'Waiting to retry','앱 다시 실행 필요':'Restart the app','감시 지연 · 20초 이상 진행 확인 없음. 작업자는 실행 중이며 강제 재시작하지 않습니다.':'Monitor delayed · no progress for over 20 seconds; worker remains running.','종료 중 · 감시 작업자의 안전한 종료를 기다리고 있습니다.':'Quitting · waiting for monitor worker to stop safely.',
'잔량 {percent}% ':'Remaining {percent}% ','{percent:g}% 남음':'{percent:g}% remaining','알림 표시 {count}건 · 새 변경은 즉시 표시':'{count} notifications · new changes appear immediately',' · 표시 상한으로 숨긴 {count}건은 변경 이력에서 확인하세요.':' · See history for {count} notifications hidden by the display limit.',
'기존 {role} 작업자에게 다시 맡겼어요.':'Resumed work with the existing {role} worker.','{role} 작업자에게 새 작업을 맡겼어요.':'Assigned new work to the {role} worker.'
}


# 기존 날짜 카탈로그의 124개 대상명에 대응하는 영어 표시입니다.
_EN.update({'장미': 'Rose', '튤립': 'Tulip', '수선화': 'Daffodil', '백합': 'Lily', '연꽃': 'Lotus', '벚꽃': 'Cherry blossom', '매화': 'Plum blossom', '동백꽃': 'Camellia', '목련': 'Magnolia', '무궁화': 'Hibiscus', '해바라기': 'Sunflower', '데이지': 'Daisy', '코스모스': 'Cosmos', '국화': 'Chrysanthemum', '거베라': 'Gerbera', '달리아': 'Dahlia', '백일홍': 'Zinnia', '금잔화': 'Marigold', '카네이션': 'Carnation', '모란': 'Peony', '양귀비': 'Poppy', '아네모네': 'Anemone', '라넌큘러스': 'Ranunculus', '도라지꽃': 'Bellflower', '나팔꽃': 'Morning glory', '페튜니아': 'Petunia', '디기탈리스': 'Foxglove', '라벤더': 'Lavender', '수국': 'Hydrangea', '라일락': 'Lilac', '구절초': 'Gujeolcho', '사과': 'Apple', '배': 'Pear', '모과': 'Quince', '복숭아': 'Peach', '살구': 'Apricot', '자두': 'Plum', '체리': 'Cherry', '포도': 'Grape', '청포도': 'Green grapes', '오렌지': 'Orange', '귤': 'Mandarin', '레몬': 'Lemon', '라임': 'Lime', '자몽': 'Grapefruit', '딸기': 'Strawberry', '라즈베리': 'Raspberry', '블랙베리': 'Blackberry', '블루베리': 'Blueberry', '바나나': 'Banana', '파인애플': 'Pineapple', '망고': 'Mango', '파파야': 'Papaya', '키위': 'Kiwi', '수박': 'Watermelon', '멜론': 'Melon', '감': 'Persimmon', '석류': 'Pomegranate', '무화과': 'Fig', '스타프루트': 'Starfruit', '용과': 'Dragonfruit', '코코넛': 'Coconut', '단풍나무 잎': 'Maple leaf', '은행나무 잎': 'Ginkgo leaf', '참나무 잎': 'Oak leaf', '자작나무 잎': 'Birch leaf', '너도밤나무 잎': 'Beech leaf', '느릅나무 잎': 'Elm leaf', '버드나무 잎': 'Willow leaf', '올리브 잎': 'Olive leaf', '유칼립투스 잎': 'Eucalyptus leaf', '포플러 잎': 'Poplar leaf', '보리수 잎': 'Linden leaf', '담쟁이 잎': 'Ivy leaf', '포도나무 잎': 'Grape leaf', '무화과 잎': 'Fig leaf', '몬스테라 잎': 'Monstera leaf', '필로덴드론 잎': 'Philodendron leaf', '연잎': 'Lotus leaf', '한련화 잎': 'Nasturtium leaf', '클로버': 'Clover', '괭이밥': 'Oxalis', '칠엽수 잎': 'Horse chestnut leaf', '물푸레나무 잎': 'Ash leaf', '마가목 잎': 'Rowan leaf', '고사리 잎': 'Fern leaf', '야자수 잎': 'Palm leaf', '대나무 잎': 'Bamboo leaf', '소나무 바늘잎': 'Pine needles', '전나무 가지': 'Fir branch', '로즈메리 가지': 'Rosemary sprig', '민트 잎': 'Mint leaf', '세이지 잎': 'Sage leaf', '바이올린': 'Violin', '비올라': 'Viola', '첼로': 'Cello', '콘트라베이스': 'Double bass', '기타': 'Guitar', '우쿨렐레': 'Ukulele', '만돌린': 'Mandolin', '류트': 'Lute', '하프': 'Harp', '리라': 'Lyre', '그랜드 피아노': 'Grand piano', '아코디언': 'Accordion', '실로폰': 'Xylophone', '마림바': 'Marimba', '칼림바': 'Kalimba', '플루트': 'Flute', '리코더': 'Recorder', '클라리넷': 'Clarinet', '오보에': 'Oboe', '바순': 'Bassoon', '색소폰': 'Saxophone', '트럼펫': 'Trumpet', '트롬본': 'Trombone', '호른': 'Horn', '튜바': 'Tuba', '스네어 드럼': 'Snare drum', '봉고': 'Bongo', '팀파니': 'Timpani', '탬버린': 'Tambourine', '트라이앵글': 'Triangle', '핸드벨': 'Handbell'})
_EN.update({'이전 모델': 'Previous model', '새 모델': 'New model', '이전 추론 강도': 'Previous reasoning effort', '새 추론 강도': 'New reasoning effort', ' (시간대 미기록)': ' (time zone not recorded)', 'Codex EXE를 찾지 못했습니다. 설정에서 설치된 codex.exe를 선택하세요.': 'Codex executable not found. Select the installed codex.exe in settings.', '잔량 요청을 전달하지 못했습니다.': 'Unable to send usage request.', '잔량 응답이 허용 크기를 넘었습니다.': 'Usage response exceeds the size limit.', '잔량 서버 진단이 허용 크기를 넘었습니다.': 'Usage server diagnostics exceed the size limit.', '잔량 응답 형식을 확인할 수 없습니다.': 'Unrecognized usage response format.', '설치된 Codex의 ChatGPT 로그인을 확인하세요.': 'Check the ChatGPT login in the installed Codex app.', '계정 한도 조회가 거부됐습니다. Codex 연결을 확인하세요.': 'Account limit lookup denied. Check the Codex connection.', '잔량 응답 결과를 확인할 수 없습니다.': 'Unrecognized usage result.', '잔량 조회 응답 시간이 초과됐습니다.': 'Usage lookup timed out.', 'Codex 잔량 연결을 실행할 수 없습니다. 설정의 EXE와 설치 상태를 확인하세요.': 'Unable to start the Codex usage connection. Check the executable and installation.', 'Codex 잔량 연결이 종료됐습니다.': 'Codex usage connection closed.', '위치 또는 기온 네트워크 조회 실패': 'Location / temperature network request failed', '기온 조회 응답이 너무 큽니다': 'Weather response exceeds the size limit', '위치 또는 기온 응답을 확인할 수 없습니다': 'Unrecognized location / weather response', '네트워크 위치를 확인할 수 없습니다': 'Network location unavailable', '기온 제공 자료 지연 · 이전 값': 'Weather data delayed · previous value', '기온 조회 지연 · 이전 값': 'Weather lookup delayed · previous value', '지역명 번역 조회 중': 'Looking up localized place name', '지역명 번역 실패 · 원문 표시': 'Place-name translation unavailable · original name shown', '앱 표시 요청; 사용자 수신 미확인': 'Presentation requested; user receipt unconfirmed', '감시 실패': 'Monitor failed', '감시 중단': 'Monitor stopped', '감시 지연': 'Monitor delayed', '과거 기록 읽는 중': 'Reading existing records', '감시 준비': 'Preparing monitor'})

_EN.update({'기준선 준비 중': 'Preparing baseline', '오류 · 진단 기록 실패 · 다음 주기 재시도': 'Error · diagnostics failed · retrying next cycle', '감시 중단 · 상태 점검 필요': 'Monitor stopped · check status', '오류 · 다음 주기 재시도': 'Error · retrying next cycle', '감시 중단 · 상태 점검 필요 · 진단 기록 실패': 'Monitor stopped · check status · diagnostics failed', '오류 · 다음 주기 재시도 · 진단 기록 실패': 'Error · retrying next cycle · diagnostics failed', 'ipwho.is · 원문': 'ipwho.is · original name', 'ipwho.is · 원문 또는 국내 사전': 'ipwho.is · original name / Korean fallback dictionary', 'ipwho.is · 지명 검색 미일치 · 원문 보존': 'ipwho.is · no matching place name · original retained', 'ipwho.is · 지역 번역 실패 · 원문 보존': 'ipwho.is · translation unavailable · original retained'})

_EN.update({'수소': 'Hydrogen', '헬륨': 'Helium', '리튬': 'Lithium', '베릴륨': 'Beryllium', '붕소': 'Boron', '탄소': 'Carbon', '질소': 'Nitrogen', '산소': 'Oxygen', '플루오린': 'Fluorine', '네온': 'Neon', '나트륨': 'Sodium', '마그네슘': 'Magnesium', '알루미늄': 'Aluminium', '규소': 'Silicon', '인': 'Phosphorus', '황': 'Sulfur', '염소': 'Chlorine', '아르곤': 'Argon', '칼륨': 'Potassium', '칼슘': 'Calcium', '스칸듐': 'Scandium', '타이타늄': 'Titanium', '바나듐': 'Vanadium', '크로뮴': 'Chromium', '망가니즈': 'Manganese', '철': 'Iron', '코발트': 'Cobalt', '니켈': 'Nickel', '구리': 'Copper', '아연': 'Zinc', '갈륨': 'Gallium'})


def get_language():
    return _language


def set_language(language):
    global _language
    _language = language if language in ('ko', 'en') else 'ko'
    return _language


def translate(text, **values):
    """명시한 앱 문구만 번역하고 전달된 값은 번역하지 않습니다."""
    result = _EN.get(text, text) if _language == 'en' else text
    if _language == 'en' and result == text and isinstance(text, str):
        minutes = re.fullmatch(r'([0-9]+(?:\.[0-9]+)?)분', text)
        if minutes:
            result = minutes.group(1) + ' minutes'
    if values:
        return result.format(**values)
    return result


def remember_translations(root):
    """생성 당시 정적인 앱 문구만 기록하여 사용자 원문과 구분합니다."""
    from PySide6.QtWidgets import QWidget
    reverse = {value: key for key, value in _EN.items()}
    for widget in [root, *root.findChildren(QWidget)]:
        for getter in ('text', 'toolTip', 'accessibleName', 'windowTitle'):
            method = getattr(widget, getter, None)
            if not callable(method):
                continue
            value = method()
            source = value if value in _EN else reverse.get(value)
            if source is not None:
                widget.setProperty('orbit_i18n_' + getter, source)


def retranslate_widgets(root):
    from PySide6.QtWidgets import QWidget
    for widget in [root, *root.findChildren(QWidget)]:
        for getter, setter in (('text','setText'), ('toolTip','setToolTip'),
                               ('accessibleName','setAccessibleName'), ('windowTitle','setWindowTitle')):
            source = widget.property('orbit_i18n_' + getter)
            if source is not None:
                getattr(widget, setter)(translate(source))
