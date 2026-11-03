<div align="center">

# 🪐 Codex Orbit · 26차

상세창 슬라이더와 위젯 메뉴에서 회전 속도를 조절하고 저장합니다. 모션 배율과 실제 시계·날짜·날씨·계정 한도 갱신은 별개입니다.

**기술 분류:** Windows 데스크톱 · Python · PySide6

[핵심 기능](#features) · [사용 흐름](#usage) · [자료 구성](#structure) · [준비와 실행](#setup) · [결과 읽기](#results) · [직전 변경](#changes)

</div>

[🏠 프로젝트](../../README.md) · [🗂️ 전체 차수](../../docs/REVISION_INDEX.md) · [📁 원본 자료](.) · [← 이전: 25차](../25/README.md) · [다음: 27차 →](../27/README.md)

## 🎯 목적과 이 차수의 역할

상세창 슬라이더와 위젯 메뉴에서 회전 속도를 조절하고 저장합니다. 모션 배율과 실제 시계·날짜·날씨·계정 한도 갱신은 별개입니다.

<a name="features"></a>

## ✨ 핵심 기능과 보존 범위

| 항목 | 이 차수에서 확인할 내용 |
|---|---|
| 1 | 상세창 슬라이더와 위젯 메뉴에서 회전 속도를 조절하고 저장합니다. 모션 배율과 실제 시계·날짜·날씨·계정 한도 갱신은 별개입니다. |
| 2 | 로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다. |
| 3 | 공개 협업 호출과 소유자가 확인된 native 활동을 연결합니다. |
| 4 | 검증된 금속 원자 프레임을 추출 없이 읽는 제한 메모리 재생기입니다. |
| 5 | 같은 실제3D 자산을 공유하는 정적 마크와 가시성 기반 내부 모션입니다. |
| 6 | 2026~2099년의 날짜별 조형 규칙입니다. 외부 데이터와 계정 정보를 사용하지 않습니다. |
| 7 | 실제 대상 이름과 조형 특징을 연결하는 편집 사전입니다. |
| 8 | 한 GPU 작업 스레드와 최대 네 이미지로 날짜별 모션을 공유합니다. |
| 9 | 현재 날짜의 실제 메시를 소유 스레드의 오프스크린 GPU에서 렌더합니다. |
| 10 | 한국 날짜의1~31일에 대응하는 원소와 디자인 영감 팔레트입니다. |
| 11 | 오늘 원소 하나의 압축 프레임만 여는 제한 메모리 재생기입니다. |
| 12 | 원본3D 자산을 변경하지 않는 제한 메모리 Qt 색 합성입니다. |
| 13 | 프로세스 전용 고해상도 대기로 전역 타이머 설정 없이 프레임을 조율합니다. |
| 14 | 앱이 소유한 문구만 번역하며 이벤트 원문은 호출자가 그대로 보존합니다. |
| 15 | Codex App Server의 `account/rateLimits/read`를 읽기 전용으로 조회합니다. 표시값은 남은 토큰 개수가 아니라 계정 사용 한도 비율입니다. |
| 16 | 지역·기온 조회 모듈은 네트워크를 사용합니다. 로컬 감시기의 외부 통신 여부와 앱 전체의 날씨 조회를 구분합니다. |

## 🔄 입력·처리·출력

| 단계 | 내용 |
|---|---|
| 📥 입력 | 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정 |
| ⚙️ 처리 | 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시 |
| 📤 출력 | 알림·변경 이력·로컬 진단 기록 |

<a name="usage"></a>

## 🖐️ 화면과 사용 흐름

1. 이 차수의 소스·requirements와 필요한 자산을 한 작업 폴더에 준비합니다.
2. 앱을 열고 위젯·상세창에서 감시 경로와 표시되는 기록을 확인합니다.
3. 새 변경이 기록되면 이전·이후 값과 이유를 비교하고, 기록 종류와 근거 수준을 함께 읽습니다.
4. 설정·이력은 개인 운영자료로 관리하고 다른 사용자에게 공유하기 전에 내용을 확인합니다.

<a name="structure"></a>

## 📁 실제 자료 구성

| 경로 | 자료 종류 |
|---|---|
| [src/](src) | 하위 자료 폴더 |
| [README.md](README.md) | MD 파일 |
| [requirements.txt](requirements.txt) | TXT 파일 |
| [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json) | JSON 파일 |
| [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md) | MD 파일 |
| [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json) | JSON 파일 |
| [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) | DIFF 파일 |

## 🧩 주요 모듈과 코드 읽기

| 파일 | 원문에 정의된 역할·구성 |
|---|---|
| [src/app.py](src/app.py) | Codex Orbit: 독립 회전 위젯과 로컬 변경 기록·사용 한도. |
| [src/notifier.py](src/notifier.py) | 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다. |
| [src/activity.py](src/activity.py) | 공개 협업 호출과 소유자가 확인된 native 활동을 연결합니다. |
| [src/atom_frames.py](src/atom_frames.py) | 검증된 금속 원자 프레임을 추출 없이 읽는 제한 메모리 재생기입니다. |
| [src/brand.py](src/brand.py) | 같은 실제3D 자산을 공유하는 정적 마크와 가시성 기반 내부 모션입니다. |
| [src/calendar_art.py](src/calendar_art.py) | 2026~2099년의 날짜별 조형 규칙입니다. 외부 데이터와 계정 정보를 사용하지 않습니다. |
| [src/calendar_catalog.py](src/calendar_catalog.py) | 실제 대상 이름과 조형 특징을 연결하는 편집 사전입니다. |
| [src/calendar_motion.py](src/calendar_motion.py) | 한 GPU 작업 스레드와 최대 네 이미지로 날짜별 모션을 공유합니다. |
| [src/calendar_renderer.py](src/calendar_renderer.py) | 현재 날짜의 실제 메시를 소유 스레드의 오프스크린 GPU에서 렌더합니다. |

<a name="setup"></a>

## 🚀 설치 환경과 실행·사용법

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다. 날짜별 실제 메시 렌더에는 ModernGL과 OpenGL 3.3을 지원하는 그래픽 드라이버가 필요합니다.

자산과 의존성을 준비한 이 차수 폴더에서 `python src/app.py`를 실행합니다. history 소스만으로 과거 배포 EXE와 동일한 화면·자산이 모두 복원되지는 않습니다.

### 📖 이 차수 원래 안내의 세부 조건

### 사용하는 사람에게 달라진 점

상세창 슬라이더와 위젯 우클릭 메뉴에서 회전 속도를 0.25~3배로 선택하고 1배로 복원할 수 있습니다. 선택값은 저장되어 다음 실행에도 적용됩니다. 속도를 바꿔도 조형의 회전 각도를 이어서 재생하며 날짜·시계·기온·계정 조회 간격은 그대로입니다. 저장이 실패하면 이전 배율로 복원하고 선택한 한국어·영어로 오류를 안내합니다. 정적 정보와 움직이는 조형을 나누어 갱신하는 변경도 포함합니다.

[26차 검증 요약](../../docs/%EA%B3%B5%EA%B0%9C%EA%B2%80%EC%A6%9D_26%EC%B0%A8.md)에서 개발 전체·공개본·중앙 소스 검사와 배포 실행 결과를 구분합니다. 고정 240fps는 달성하지 못했으며 추가 달성 작업은 제외됐습니다. 26차 변경 기록의 실측 생성 약 227~230fps, 고유 Qt 그리기 약 214~229fps를 모니터 표시율로 해석하지 않습니다.

### 📦 이 보관본의 의존성 목록

[requirements.txt](requirements.txt)의 실제 항목입니다. 외부 실행 도구와 GPU 드라이버는 별도로 준비합니다.

```text
PySide6-Essentials==6.12.0
PyInstaller==6.22.3
moderngl==5.13.0
glcontext==3.1.0
numpy==2.5.4
Pillow==13.0.0
```

### ⚙️ 소스에서 제공하는 CLI 옵션

| 진입 소스 | 정의된 옵션 이름 |
|---|---|
| [app.py](src/app.py) | `--data-dir`, `--sessions`, `--smoke-test`, `--usage-smoke-test`, `--smoke-report`, `--show-details`, `--show-event` |
| [notifier.py](src/notifier.py) | `--sessions`, `--work` |

각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>🔬 함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

### [src/activity.py](src/activity.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`safe_public_text`](src/activity.py#L15) | 보호문·비공개 표식·긴 인코딩 덩어리는 해석하거나 노출하지 않습니다. |
| [`configuration`](src/activity.py#L76) | 원본 시각이 있는 자기 관측만 전역 256개로 제한해 보존합니다. |
| [`defer`](src/activity.py#L160) | 원본 본문 없이 검증에 필요한 native 필드만 전역 32개까지 기다립니다. |
| [`observe`](src/activity.py#L273) | 그 활동의 첫 관측만 보강하며 이후 모델 변경은 별도 감지를 유지합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`MAX_ACTIVITY_EVENTS`](src/activity.py#L7) | `정의=128` |
| [`MAX_ACTIVITY_SEEN`](src/activity.py#L8) | `정의=8192` |
| [`MAX_ACTIVITY_CALLS`](src/activity.py#L9) | `정의=32` |
| [`MAX_PUBLIC_CALLS`](src/activity.py#L10) | `정의=128` |
| [`MAX_DEFERRED_ACTIVITIES`](src/activity.py#L11) | `정의=32` |
| [`MAX_CONFIGURATION_SNAPSHOTS`](src/activity.py#L12) | `정의=256` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`not isinstance(self.data['calls'], dict) or not isinstance(self.data['deferred'], list)`](src/activity.py#L66) | 활동 호출/지연 상태 구조 오류입니다. 원본을 자동 초기화하지 않습니다. |
| [`not isinstance(self.data['configurations'], list)`](src/activity.py#L68) | 활동 관측 시각 구조 오류입니다. 원본을 자동 초기화하지 않습니다. |

### [src/app.py](src/app.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`validated_motion_speed`](src/app.py#L42) | 설정과 UI의 속도는 유한한 실제 숫자 범위로 제한합니다. |
| [`_application_gui_root`](src/app.py#L49) | Python 순환 수집과 무관하게 살아 있는 GUI 소유자를 앱에 보관합니다. |
| [`operation_record`](src/app.py#L67) | 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다. |
| [`previous_field`](src/app.py#L106) | 이전 기록 전체 부재와 개별 필드 미기록을 구분하고 관측값만 표시합니다. |
| [`short_reason`](src/app.py#L130) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |
| [`public_text`](src/app.py#L182) | 공개 문장만 표시하며 보호된 도구 페이로드를 해석하거나 노출하지 않습니다. |
| [`selection_explanation`](src/app.py#L203) | 공개된 작업 목적을 모델 선택 이유로 바꾸어 말하지 않습니다. |
| [`NoticeDelivery`](src/app.py#L309) | Qt 예약 호출을 포함한 미처리 전달 수를 스레드 사이에서 제한합니다. |
| [`NoticeTicket`](src/app.py#L334) | 중복 반환과 종료 뒤 도착한 신호도 같은 한도를 다시 늘리지 않습니다. |
| [`DiagnosticLabel`](src/app.py#L918) | 오류가 있을 때 변경 기록 안에 원문을 보여 주는 읽기 전용 라벨입니다. |
| [`QuitGuard`](src/app.py#L1394) | 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다. |
| [`usage_smoke_state`](src/app.py#L1956) | 지연된 신호 인자 대신 최신 스냅샷과 현재 레이아웃의 실제 표시를 대조합니다. |
| [`motion_smoke_stage`](src/app.py#L1980) | 실제 GPU 렌더 수를 기준으로 준비·비교 단계를 판정합니다. |
| [`_content_fit_signature`](src/app.py#L759) | 말줄임 전 제목과 실제 높이에 영향을 주는 표시 조건만 비교합니다. |
| [`promote_first_observation`](src/app.py#L1363) | 실제 첫 관측 한 행만 안정된 활동 ID로 보강하며 다른 변경은 보존합니다. |
| [`change_motion_speed`](src/app.py#L1484) | 사용자 조작의 실패는 실제 속도를 복원한 뒤 상세창에서 안내합니다. |
| [`_finish_closed_gui`](src/app.py#L1948) | 외부 QThread 참조를 무효화하지 않고 종료된 감시기와 GUI 소유자를 해제합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`--data-dir`](src/app.py#L1996) | `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'` |
| [`--sessions`](src/app.py#L1997) | `type=Path` |
| [`--smoke-test`](src/app.py#L1998) | `action='store_true'` |
| [`--usage-smoke-test`](src/app.py#L1999) | `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'` |
| [`--smoke-report`](src/app.py#L2000) | `type=Path` |
| [`--show-details`](src/app.py#L2001) | `action='store_true'` |
| [`--show-event`](src/app.py#L2002) | `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'` |
| [`EMPTY_HISTORY_GUIDANCE`](src/app.py#L39) | `정의='변경을 감지하면 이곳에서 전후 값과 공개 이유를 확인할 수 있습니다.\n첫 실행은 과거 기록을 기준선으로 읽으며 과거 알림을 만들지 않습니다.'` |
| [`ROLE_LABELS`](src/app.py#L116) | `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`application is None or QThread.currentThread() != application.thread()`](src/app.py#L52) | GUI 소유자는 QApplication의 메인 스레드에서 생성해야 합니다. |
| [`QThread.currentThread() != application.thread()`](src/app.py#L1523) | 언어는 GUI 메인 스레드에서만 변경할 수 있습니다. |
| [`not lock.tryLock(100)`](src/app.py#L2024) | 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다. |
| [`not isinstance(value, dict)`](src/app.py#L295) | 앱 설정은 JSON 객체여야 합니다. |
| [`self.closed or len(self.tickets) &gt;= MAX_PENDING`](src/app.py#L318) | 알림 전달 대기 한도 또는 종료 상태: 다음 감시 주기에 재시도합니다. |

### [src/atom_frames.py](src/atom_frames.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`AtomAssetError`](src/atom_frames.py#L27) | 필수 시각 자산 오류를 시작 실패 경로에 전달합니다. |
| [`AtomFrames`](src/atom_frames.py#L50) | 시작 시 전체 무결성을 검사하고 해제된 QImage는 최대24장만 보존합니다. |
| [`close_runtime_frames`](src/atom_frames.py#L172) | 프로세스 공유 ZIP을 한 번 닫으며 중복 종료 호출도 안전하게 처리합니다. |
| [`get_atom_frames`](src/atom_frames.py#L183) | 제품의 고정 경로는 프로세스에서 한 번 검증하고 모든 창이 공유합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`FRAME_COUNT`](src/atom_frames.py#L16) | `정의=540` |
| [`FRAME_SIZE`](src/atom_frames.py#L17) | `정의=296` |
| [`FPS`](src/atom_frames.py#L18) | `정의=30` |
| [`PERIOD_SECONDS`](src/atom_frames.py#L19) | `정의=18` |
| [`CACHE_LIMIT`](src/atom_frames.py#L20) | `정의=24` |
| [`MAX_ARCHIVE_BYTES`](src/atom_frames.py#L21) | `정의=128 * 1024 * 1024` |
| [`MAX_FRAME_BYTES`](src/atom_frames.py#L22) | `정의=1024 * 1024` |
| [`MAX_TOTAL_BYTES`](src/atom_frames.py#L23) | `정의=256 * 1024 * 1024` |
| [`MAX_MANIFEST_BYTES`](src/atom_frames.py#L24) | `정의=64 * 1024` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`key in value`](src/atom_frames.py#L44) | 원자 자산 매니페스트에 중복 필드가 있습니다. |
| [`not 0 &lt; manifest_path.stat().st_size &lt;= MAX_MANIFEST_BYTES`](src/atom_frames.py#L69) | 원자 자산 매니페스트 크기가 허용 범위를 벗어났습니다. |
| [`not isinstance(self.manifest, dict)`](src/atom_frames.py#L75) | 원자 자산 매니페스트는 객체여야 합니다. |
| [`not isinstance(digest, str) or re.fullmatch('[0-9a-f]{64}', digest) is None`](src/atom_frames.py#L85) | 원자 프레임 ZIP의 SHA256 형식이 잘못됐습니다. |
| [`not 0 &lt; archive_path.stat().st_size &lt;= MAX_ARCHIVE_BYTES`](src/atom_frames.py#L87) | 원자 프레임 ZIP 크기가 허용 범위를 벗어났습니다. |
| [`hasher.hexdigest() != digest`](src/atom_frames.py#L94) | 원자 프레임 ZIP의 SHA256이 일치하지 않습니다. |
| [`len(members) != FRAME_COUNT or {item.filename for item in members} != names`](src/atom_frames.py#L100) | 원자 프레임 ZIP의 정확한540개 이름·목록이 일치하지 않습니다. |
| [`sum(item.file_size for item in members) &gt; MAX_TOTAL_BYTES`](src/atom_frames.py#L102) | 원자 프레임 전체 읽기 상한을 초과했습니다. |
| [`actual != self.identities`](src/atom_frames.py#L133) | 검증 뒤 원자 자산이 변경됐습니다. 앱을 다시 실행해 주세요. |
| [`isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed)`](src/atom_frames.py#L138) | 원자 프레임의 재생 시각이 유한한 숫자가 아닙니다. |
| [`item.is_dir() or item.flag_bits & 1 or item.compress_type not in                     (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED) or                     not 0 &lt; item.file_size &lt;= MAX_FRAME_BYTES`](src/atom_frames.py#L105) | 원자 프레임 멤버의 형식·크기가 허용 범위를 벗어났습니다. |

### [src/brand.py](src/brand.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`motion_brand_source`](src/brand.py#L32) | 원소 프레임의 실제 크기에 비례해 여백만 줄이며 영역 밖을 복사하지 않습니다. |
| [`BrandClock`](src/brand.py#L40) | 보이는 로고만 단일 시계에서 같은 프레임으로 갱신합니다. |
| [`AnimatedBrand`](src/brand.py#L106) | 닫힘·숨김 이벤트에 맞춰 재생 구독을 끝내는 실제3D 로고입니다. |
| [`validate_symbols`](src/brand.py#L137) | 실제 메시에서 제작한 고정 기호 일곱 개를 창 생성 전에 검증합니다. |
| [`symbol_image`](src/brand.py#L181) | 실제 메시 렌더만 축소하고 새로운 도형이나 글자를 덧그리지 않습니다. |
| [`with_symbol`](src/brand.py#L209) | 원문 QLabel을 유지하며 기능 의미를 읽기 쉬운 기호로 보조합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`SYMBOL_NAMES`](src/brand.py#L133) | `정의=('model', 'reasoning', 'time', 'reason', 'usage', 'refresh', 'history')` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`not 1 &lt;= size &lt;= 512`](src/brand.py#L22) | 브랜드 이미지 크기는1~512px여야 합니다. |
| [`name not in SYMBOL_NAMES or not 1 &lt;= size &lt;= 96`](src/brand.py#L184) | 3D 기능 기호의 종류나 크기가 올바르지 않습니다. |
| [`not 0 &lt; path.stat().st_size &lt;= 65536`](src/brand.py#L142) | 3D 기능 기호 매니페스트 크기 오류입니다. |
| [`type(metadata.get('schema_version')) is not int or metadata['schema_version'] != 1`](src/brand.py#L145) | 3D 기능 기호 매니페스트 버전 오류입니다. |
| [`not isinstance(files, dict) or set(files) != set(SYMBOL_NAMES)`](src/brand.py#L148) | 3D 기능 기호 일곱 개 목록이 일치하지 않습니다. |
| [`not isinstance(record, dict) or record.get('filename') != name+'.png'`](src/brand.py#L153) | 3D 기능 기호의 고정 파일 이름이 일치하지 않습니다. |
| [`not isinstance(digest, str) or re.fullmatch('[0-9a-f]{64}', digest) is None`](src/brand.py#L156) | 3D 기능 기호의 SHA256 형식 오류입니다. |
| [`not 0 &lt; path.stat().st_size &lt;= 262144`](src/brand.py#L159) | 3D 기능 기호 읽기 크기 상한 오류입니다. |

### [src/calendar_art.py](src/calendar_art.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`current_date`](src/calendar_art.py#L33) | 호스트의 현지 시간대와 무관하게 한국 날짜를 사용합니다. |
| [`_month_palette`](src/calendar_art.py#L50) | 반올림 충돌만 가장 가까운 미사용 RGB로 옮기고 월별 결과를 불변 보관합니다. |
| [`design_for_date`](src/calendar_art.py#L78) | 유효한 날짜만 허용하며 지원 범위 밖을 다른 날짜로 몰래 대체하지 않습니다. |
| [`all_designs`](src/calendar_art.py#L95) | 현재 모델만 렌더하며 이 반복자는 작은 카탈로그를 작성할 때만 사용합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`FIRST_DATE`](src/calendar_art.py#L10) | `정의=date(2026,1,1)` |
| [`LAST_DATE`](src/calendar_art.py#L11) | `정의=date(2099,12,31)` |
| [`KST`](src/calendar_art.py#L12) | `정의=timezone(timedelta(hours=9))` |
| [`THEMES`](src/calendar_art.py#L13) | `정의=tuple(row.title for row in all_collections())` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`type(value) is not date`](src/calendar_art.py#L80) | 조형 날짜는 datetime.date여야 합니다. |
| [`not FIRST_DATE &lt;= value &lt;= LAST_DATE`](src/calendar_art.py#L82) | 날짜별 조형 지원 범위는 2026-01-01부터 2099-12-31까지입니다. |

### [src/calendar_catalog.py](src/calendar_catalog.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`joining_particle`](src/calendar_catalog.py#L208) | 마지막 한글 음절의 받침에 맞춰 대상 이름을 연결합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`POOLS`](src/calendar_catalog.py#L166) | `정의={'꽃': _objects(_FLOWERS,'꽃'), '열매': _objects(_FRUITS,'열매'),          '잎': _objects(_LEAVES,'잎'), '악기': _objects(_MUSIC,'악기')}` |
| [`OBJECTS`](src/calendar_catalog.py#L168) | `정의={obj.key:obj for pool in POOLS.values() for obj in pool}` |
| [`COMPOSITION_NAMES`](src/calendar_catalog.py#L193) | `정의={'bouquet':'꽃다발형','diagonal':'대각선형','shelter':'감싸는 형태',                      'stage':'연주대형','triangle':'삼각형 정물','fan':'부채형'}` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`not 0 &lt;= index &lt; 888 or not 1 &lt;= month &lt;= 12`](src/calendar_catalog.py#L217) | 연월 컬렉션은 2026년 1월부터 2099년 12월까지입니다. |

### [src/calendar_motion.py](src/calendar_motion.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`next_frame_deadline`](src/calendar_motion.py#L21) | 정상 슬롯을 유지하고 늦은 프레임은 추가 대기나 누적 추격 없이 이어갑니다. |
| [`fallback_image`](src/calendar_motion.py#L26) | GPU 준비·실패 때만 쓰는 월 주제의 정적 평면 표식입니다. 3D 성공으로 가장하지 않습니다. |
| [`_Worker`](src/calendar_motion.py#L60) | Qt 객체나 UI를 조작하지 않고 복사된 최신 이미지 하나만 전달합니다. |
| [`prepare_calendar_motion`](src/calendar_motion.py#L232) | 창 표시 전에 같은 작업자의 첫 실제 프레임을 최대 5초 준비합니다. |
| [`set_calendar_motion_speed`](src/calendar_motion.py#L262) | 현재 위상을 유지하고 이후 모션의 배율만 바꿉니다. 실제 시계와 날짜는 바꾸지 않습니다. |
| [`set_calendar_motion_size`](src/calendar_motion.py#L268) | 현재 보이는 각 소유자의 실제 픽셀 요구 중 최대 크기만 전달합니다. |
| [`record_calendar_presentation`](src/calendar_motion.py#L276) | Qt 그리기 경로가 실제로 소비한 서로 다른 프레임만 셉니다. |
| [`get_calendar_error`](src/calendar_motion.py#L285) | 제품은 이 문자열을 상태나 툴팁에 표시해 대체 표식과 실제 3D를 구분할 수 있습니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`FPS`](src/calendar_motion.py#L15) | `정의=240` |
| [`SIZE`](src/calendar_motion.py#L16) | `정의=384` |
| [`RENDER_SIZE`](src/calendar_motion.py#L17) | `정의=(3840, 2160)` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`app is None or QThread.currentThread()!=app.thread()`](src/calendar_motion.py#L211) | 날짜별 모션 API는 Qt 메인 스레드에서 호출해야 합니다. |
| [`type(timeout_seconds) not in (int,float) or not 0 &lt; timeout_seconds &lt;= 5`](src/calendar_motion.py#L234) | 3D 준비 제한은 0초 초과 5초 이하여야 합니다. |
| [`type(visible) is not bool`](src/calendar_motion.py#L258) | 표시 상태는 bool이어야 합니다. |
| [`type(size) is not int or not 32&lt;=size&lt;=2160`](src/calendar_motion.py#L270) | 전달 크기는32~2160 정수여야 합니다. |
| [`self.closed`](src/calendar_motion.py#L167) | 날짜별 모션 서비스가 닫혔습니다. |
| [`self.closed`](src/calendar_motion.py#L180) | 날짜별 모션 서비스가 닫혔습니다. |
| [`type(elapsed) not in (int,float)`](src/calendar_motion.py#L181) | 재생 시각은 유한한 숫자여야 합니다. |
| [`not valid`](src/calendar_motion.py#L184) | 재생 시각은 유한한 숫자여야 합니다. |
| [`_retiring.worker.isRunning()`](src/calendar_motion.py#L221) | 이전 GPU 작업 스레드가 종료 중입니다. |

### [src/calendar_renderer.py](src/calendar_renderer.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`rotation`](src/calendar_renderer.py#L24) | 정규화된 실제 3D축을 중심으로 로드리게스 회전행렬을 만듭니다. |
| [`finish`](src/calendar_renderer.py#L48) | 표면 법선과 삼각형 winding을 일치시킵니다. |
| [`box`](src/calendar_renderer.py#L58) | 육면체 면을 실제 둥근 모서리와 구면 꼭짓점으로 투영합니다. |
| [`lathe`](src/calendar_renderer.py#L84) | 회전체의 실제 앞뒤·옆면을 만들며 다각 단면은 평면 법선을 보존합니다. |
| [`tube`](src/calendar_renderer.py#L104) | 3D 경로를 따라 원형 단면을 운반합니다. 코일은 실제 깊이를 가집니다. |
| [`_object_geometry`](src/calendar_renderer.py#L145) | 대상 이름에 연결된 주요 구조를 실제 삼각형 부품으로 구성합니다. |
| [`_ring_geometry`](src/calendar_renderer.py#L323) | 날짜와 무관한 세 링만 읽기 전용 배열로 한 번 생성합니다. |
| [`build_geometry`](src/calendar_renderer.py#L334) | 날짜별 주연과 서로 다른 두 월 모티프를 명시적 대상 사전에서 렌더합니다. |
| [`CalendarRenderer`](src/calendar_renderer.py#L378) | 컨텍스트를 만든 스레드에서만 사용하고 현재 날짜의 버퍼만 보유합니다. |
| [`render_date`](src/calendar_renderer.py#L489) | 미리보기와 직접 검증용 동기 렌더입니다. 앱은 공유 작업 스레드를 사용합니다. |
| [`set_output_size`](src/calendar_renderer.py#L425) | 원본 타깃은 유지하고 중앙 정사각형의 GPU 전달 크기만 변경합니다. |
| [`render_original`](src/calendar_renderer.py#L470) | 검증·내보내기 때만 실제 직사각형 원본 전체를 CPU로 읽습니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`PERIOD`](src/calendar_renderer.py#L132) | `정의=12.0` |
| [`SIZE`](src/calendar_renderer.py#L133) | `정의=384` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`subject.recipe!=design.shape_recipe`](src/calendar_renderer.py#L338) | 대상과 형상 규칙이 일치하지 않습니다. |
| [`type(elapsed) not in (int,float)`](src/calendar_renderer.py#L364) | 모션 시각은 유한한 숫자여야 합니다. |
| [`not valid`](src/calendar_renderer.py#L367) | 모션 시각은 유한한 숫자여야 합니다. |
| [`threading.get_ident()!=self.thread_id`](src/calendar_renderer.py#L423) | GPU 컨텍스트는 생성 스레드에서만 사용할 수 있습니다. |
| [`type(size) is not int or not 32&lt;=size&lt;=2160`](src/calendar_renderer.py#L428) | 전달 크기는32~2160 정수여야 합니다. |

### [src/core.py](src/core.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`read_jsonl_tail`](src/core.py#L19) | 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| [`title_catalog`](src/core.py#L56) | 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| [`resolve_title`](src/core.py#L86) | 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| [`safe_path`](src/core.py#L110) | 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`MAX_TEXT_BYTES`](src/core.py#L10) | `정의=2 * 1024 * 1024` |
| [`BEGIN`](src/core.py#L11) | `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| [`END`](src/core.py#L12) | `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L125) | 문서가 2 MiB 상한을 초과했습니다. |
| [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L65) | 제목 캐시 구조가 올바르지 않습니다. |
| [`target.name.lower() != 'agents.md'`](src/core.py#L136) | 적용 대상은 AGENTS.md 파일이어야 합니다. |
| [`not target.parent.is_dir()`](src/core.py#L138) | 대상 폴더가 존재하지 않습니다. |
| [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L140) | 대상은 2 MiB 이하의 일반 파일이어야 합니다. |
| [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L147) | 빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다. |
| [`BEGIN in added or END in added`](src/core.py#L149) | 지침 내용에 앱 관리구역 표식을 넣을 수 없습니다. |
| [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L163) | 적용 결과가 2 MiB 상한을 초과합니다. |
| [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L170) | 대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다. |
| [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L190) | 미리보기 데이터가 변경되었습니다. |
| [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L210) | 유효한 앱 원문 백업이 아닙니다. |
| [`digest(raw) != receipt['before_hash']`](src/core.py#L213) | 백업 해시가 일치하지 않습니다. |
| [`not isinstance(row, dict)`](src/core.py#L41) | JSON 객체가 아닙니다. |
| [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L156) | 기존 관리구역 표식이 손상되었거나 중복되었습니다. |

### [src/element_frames.py](src/element_frames.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`ElementAssetError`](src/element_frames.py#L24) | 필수 원소 자산 실패를 숨기지 않고 앱의 시작·표시 오류로 전달합니다. |
| [`preflight_element_frames`](src/element_frames.py#L132) | 활성 원소의 해시·목록·첫 프레임을 확인합니다.31개를 적재하지 않습니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`CACHE_LIMIT`](src/element_frames.py#L15) | `정의=24` |
| [`FRAME_SIZE`](src/element_frames.py#L16) | `정의=192` |
| [`FRAME_COUNT`](src/element_frames.py#L17) | `정의=540` |
| [`FPS`](src/element_frames.py#L18) | `정의=30` |
| [`PERIOD_SECONDS`](src/element_frames.py#L19) | `정의=18` |
| [`MAX_ARCHIVE_BYTES`](src/element_frames.py#L20) | `정의=64*1024*1024` |
| [`MAX_FRAME_BYTES`](src/element_frames.py#L21) | `정의=512*1024` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`type(number) is not int or not 1&lt;=number&lt;=31`](src/element_frames.py#L34) | 원소 번호는1~31 정수여야 합니다. |
| [`not 0&lt;manifest.stat().st_size&lt;=64*1024`](src/element_frames.py#L65) | 원소 매니페스트 크기 오류 |
| [`not isinstance(self.manifest,dict)`](src/element_frames.py#L69) | 원소 매니페스트는 객체여야 합니다. |
| [`not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest)`](src/element_frames.py#L74) | 원소 해시 형식 오류 |
| [`not 0&lt;archive.stat().st_size&lt;=MAX_ARCHIVE_BYTES`](src/element_frames.py#L75) | 원소 압축파일 크기 초과 |
| [`hasher.hexdigest()!=digest`](src/element_frames.py#L78) | 원소 ZIP 해시 불일치 |
| [`len(members)!=540 or {m.filename for m in members}!={f'frame_{i:04d}.png' for i in range(540)}`](src/element_frames.py#L80) | 원소 ZIP 정확한540프레임 목록 불일치 |
| [`sum(m.file_size for m in members)&gt;128*1024*1024`](src/element_frames.py#L82) | 원소 해제 크기 초과 |
| [`actual!=self.identities`](src/element_frames.py#L91) | 실행 중 원소 자산이 변경됐습니다. |
| [`isinstance(elapsed,bool) or not isinstance(elapsed,(int,float)) or not math.isfinite(elapsed)`](src/element_frames.py#L106) | 원소 재생 시각은 유한한 숫자여야 합니다. |
| [`self.archive is None`](src/element_frames.py#L107) | 원소 재생기가 닫혔습니다. |
| [`member.is_dir() or member.flag_bits&1 or member.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED)                     or not 0&lt;member.file_size&lt;=MAX_FRAME_BYTES`](src/element_frames.py#L84) | 원소 ZIP 멤버 형식 오류 |
| [`len(data)&gt;MAX_FRAME_BYTES or len(data)&lt;33 or data[:8]!=b'\x89PNG\r\n\x1a\n' or data[12:16]!=b'IHDR'                     or struct.unpack('&gt;II',data[16:24])!=(192,192) or data[24:26]!=bytes((8,6))`](src/element_frames.py#L96) | 원소 PNG 형식 오류 |
| [`image.isNull() or image.size().width()!=192 or image.height()!=192 or not image.hasAlphaChannel()`](src/element_frames.py#L99) | 원소 PNG 디코딩 오류 |
| [`any(image.pixelColor(x,y).alpha() for x,y in ((0,0),(191,0),(0,191),(191,191)))`](src/element_frames.py#L100) | 원소 PNG 투명 모서리 오류 |

### [src/element_visuals.py](src/element_visuals.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`colorize_atom`](src/element_visuals.py#L5) | SourceAtop은 원본 알파를 유지하며 명암에 부드러운 영감색을 더합니다. |

### [src/elements.py](src/elements.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`daily_element`](src/elements.py#L43) | 매 호출 실제 날짜를 다시 읽어 자정·절전 복귀·시계 되돌림을 반영합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`KST`](src/elements.py#L5) | `정의=timezone(timedelta(hours=9))` |
| [`PALETTE_NOTE`](src/elements.py#L8) | `정의='원소에서 영감받은 디자인 색이며 실제 원소·불꽃색이나 전자배치 재현이 아닙니다.'` |
| [`ELEMENTS`](src/elements.py#L39) | `정의=tuple(Element(index,symbol,name,color,accent)                  for index,(symbol,name,color,accent) in enumerate(_ROWS,1))` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`value.tzinfo is None or value.utcoffset() is None`](src/elements.py#L46) | 원소 날짜에는 시간대가 있는 datetime이 필요합니다. |

### [src/frame_pacing.py](src/frame_pacing.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`validate_motion_speed`](src/frame_pacing.py#L7) | 유한한 0.25~3배 숫자만 받아 bool과 잘못된 설정을 거부합니다. |
| [`MotionClock`](src/frame_pacing.py#L20) | 실제 날짜·시계와 분리하여 배율별 경과 시간을 연속 적분합니다. |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`type(value) not in (int, float)`](src/frame_pacing.py#L9) | 회전 속도는 0.25~3배의 유한한 숫자여야 합니다. |
| [`not valid`](src/frame_pacing.py#L15) | 회전 속도는 0.25~3배의 유한한 숫자여야 합니다. |

### [src/i18n.py](src/i18n.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`translate`](src/i18n.py#L51) | 명시한 앱 문구만 번역하고 전달된 값은 번역하지 않습니다. |
| [`remember_translations`](src/i18n.py#L63) | 생성 당시 정적인 앱 문구만 기록하여 사용자 원문과 구분합니다. |

### [src/motion_label.py](src/motion_label.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`MotionImageLabel`](src/motion_label.py#L6) | 최신 이미지 한 개를 보관하고 크기·DPR 변경 때만 기본 크기 힌트를 갱신합니다. |

### [src/notifier.py](src/notifier.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`atomic_json`](src/notifier.py#L33) | 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다. |
| [`source_datetime`](src/notifier.py#L63) | 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다. |
| [`duplicate_record`](src/notifier.py#L212) | 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다. |
| [`settings_record`](src/notifier.py#L223) | 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다. |
| [`lookup_parent_reason`](src/notifier.py#L376) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L423) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |
| [`replay_activity_prefix`](src/notifier.py#L445) | 고정된 과거 소비 구간의 활동 메타만 파일별 기존 예산 안에서 복원합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`--sessions`](src/notifier.py#L739) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L740) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L18) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L19) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L20) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L21) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L22) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L23) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L24) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L25) | `정의=256` |
| [`POLL_INTERVAL_SECONDS`](src/notifier.py#L26) | `정의=0.2` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L90) | 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다. |
| [`self.state.get('schema_version') not in (2, 3)`](src/notifier.py#L94) | 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다. |
| [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L96) | 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다. |
| [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L98) | 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다. |
| [`not isinstance(self.state.get('settings'), dict)`](src/notifier.py#L117) | 채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다. |
| [`backup.read_bytes() != original`](src/notifier.py#L105) | 이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다. |
| [`any(isinstance(v, bool) or not isinstance(v, int) or v &lt; 0 for v in (offset, end))`](src/notifier.py#L112) | 이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다. |
| [`backup.read_bytes() != original`](src/notifier.py#L123) | 활동 이행 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다. |
| [`isinstance(end, bool) or not isinstance(end, int) or end &lt; 0`](src/notifier.py#L131) | 활동 기준선의 파일 위치가 올바르지 않습니다. |
| [`not isinstance(record, dict)`](src/notifier.py#L523) | JSON 객체가 아닙니다. |
| [`path.stat().st_size &gt; 20000`](src/notifier.py#L603) | 명시 알림 파일 상한 초과 |
| [`not isinstance(record, dict)`](src/notifier.py#L467) | JSON 객체가 아닙니다. |

### [src/theme.py](src/theme.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`MonochromeStyle`](src/theme.py#L53) | 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다. |
| [`KoreanDialogs`](src/theme.py#L78) | 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다. |
| [`DialogLayout`](src/theme.py#L94) | 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다. |

### [src/typography.py](src/typography.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`register_fonts`](src/typography.py#L8) | 필수 파일이나 Qt 등록 실패를 숨기지 않고 시작 오류로 전달합니다. |

### [src/usage.py](src/usage.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`number`](src/usage.py#L16) | 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다. |
| [`normalize_limits`](src/usage.py#L35) | 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다. |
| [`discover_codex`](src/usage.py#L69) | 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`MAX_BYTES`](src/usage.py#L12) | `정의=1024 * 1024` |
| [`KST`](src/usage.py#L13) | `정의=timezone(timedelta(hours=9))` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`not isinstance(message, dict)`](src/usage.py#L226) | 객체가 아닌 응답 |

### [src/usage_frames.py](src/usage_frames.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`UsageAssetError`](src/usage_frames.py#L27) | 조형 표시 오류를 호출자에게 전달하며 계정 조회 흐름과 분리합니다. |
| [`UsageFrames`](src/usage_frames.py#L50) | 시작 시 전체 무결성을 검사하고 해제된 QImage는 최대16장만 보존합니다. |
| [`close_usage_frames`](src/usage_frames.py#L183) | 프로세스 공유 ZIP을 한 번 닫으며 중복 종료 호출도 안전하게 처리합니다. |
| [`preflight_usage_frames`](src/usage_frames.py#L194) | 제품의 고정 경로는 프로세스에서 한 번 검증하고 모든 창이 공유합니다. |
| [`get_usage_frame`](src/usage_frames.py#L207) | 공유 팩의 한 프레임을 반환하며 계정 조회 상태에는 관여하지 않습니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`FRAME_COUNT`](src/usage_frames.py#L16) | `정의=360` |
| [`FRAME_SIZE`](src/usage_frames.py#L17) | `정의=384` |
| [`FPS`](src/usage_frames.py#L18) | `정의=30` |
| [`PERIOD_SECONDS`](src/usage_frames.py#L19) | `정의=12` |
| [`CACHE_LIMIT`](src/usage_frames.py#L20) | `정의=16` |
| [`MAX_ARCHIVE_BYTES`](src/usage_frames.py#L21) | `정의=128 * 1024 * 1024` |
| [`MAX_FRAME_BYTES`](src/usage_frames.py#L22) | `정의=1024 * 1024` |
| [`MAX_TOTAL_BYTES`](src/usage_frames.py#L23) | `정의=256 * 1024 * 1024` |
| [`MAX_MANIFEST_BYTES`](src/usage_frames.py#L24) | `정의=64 * 1024` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`key in value`](src/usage_frames.py#L44) | 대시보드 조형 자산 매니페스트에 중복 필드가 있습니다. |
| [`not 0 &lt; manifest_path.stat().st_size &lt;= MAX_MANIFEST_BYTES`](src/usage_frames.py#L69) | 대시보드 조형 자산 매니페스트 크기가 허용 범위를 벗어났습니다. |
| [`not isinstance(self.manifest, dict)`](src/usage_frames.py#L75) | 대시보드 조형 자산 매니페스트는 객체여야 합니다. |
| [`not isinstance(digest, str) or re.fullmatch('[0-9a-f]{64}', digest) is None`](src/usage_frames.py#L85) | 대시보드 조형 프레임 ZIP의 SHA256 형식이 잘못됐습니다. |
| [`not 0 &lt; archive_path.stat().st_size &lt;= MAX_ARCHIVE_BYTES`](src/usage_frames.py#L87) | 대시보드 조형 프레임 ZIP 크기가 허용 범위를 벗어났습니다. |
| [`hasher.hexdigest() != digest`](src/usage_frames.py#L94) | 대시보드 조형 프레임 ZIP의 SHA256이 일치하지 않습니다. |
| [`len(members) != FRAME_COUNT or {item.filename for item in members} != names`](src/usage_frames.py#L100) | 대시보드 조형 프레임 ZIP의 정확한360개 이름·목록이 일치하지 않습니다. |
| [`sum(item.file_size for item in members) &gt; MAX_TOTAL_BYTES`](src/usage_frames.py#L102) | 대시보드 조형 프레임 전체 읽기 상한을 초과했습니다. |
| [`actual != self.identities`](src/usage_frames.py#L133) | 검증 뒤 대시보드 조형 자산이 변경됐습니다. 앱을 다시 실행해 주세요. |
| [`type(elapsed) not in (int, float)`](src/usage_frames.py#L138) | 조형 재생 시각은 유한한 숫자여야 합니다. |
| [`not finite`](src/usage_frames.py#L144) | 대시보드 조형 프레임의 재생 시각이 유한한 숫자가 아닙니다. |
| [`self.archive is None`](src/usage_frames.py#L149) | 조형 재생기가 닫혔습니다. |
| [`item.is_dir() or item.flag_bits & 1 or item.compress_type not in                     (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED) or                     not 0 &lt; item.file_size &lt;= MAX_FRAME_BYTES`](src/usage_frames.py#L105) | 대시보드 조형 프레임 멤버의 형식·크기가 허용 범위를 벗어났습니다. |

### [src/usage_widgets.py](src/usage_widgets.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`CalendarHero`](src/usage_widgets.py#L9) | 사용 한도 화면에서만 날짜별 입체 이미지를 갱신합니다. |

### [src/visuals.py](src/visuals.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`rotate_point`](src/visuals.py#L12) | X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다. |
| [`axis_rotate`](src/visuals.py#L40) | 로드리게스 식으로 고유 축 주위를 회전하며 공통 Z 변환을 쓰지 않습니다. |
| [`orbit_segments`](src/visuals.py#L63) | 제작 매니페스트와 일치하는 기하 검증용 메타입니다. GUI 드로잉에는 쓰지 않습니다. |
| [`status_label`](src/visuals.py#L80) | 읽지 않은 변경을 우선 표시하며 감시 상태는 실제 플래그에서만 읽습니다. |
| [`element_labels`](src/visuals.py#L85) | 원자번호와 계정 퍼센트를 서로 다른 명시적 라벨로 구분합니다. |
| [`usage_bar`](src/visuals.py#L99) | 숫자와 채움에 같은 실제 비율을 쓰며 최소 채움 폭을 강제하지 않습니다. |
| [`_frame_for_element`](src/visuals.py#L111) | 원소별 실제 제작 프레임을 읽습니다. 이전 형상으로 대체하지 않습니다. |
| [`draw_orbit`](src/visuals.py#L117) | 달력 조형·날짜 도크·실제 잔량을 분리하고 명시한 원소 미리보기도 보존합니다. |
| [`desktop_widget_layout`](src/visuals.py#L176) | 이름을 화면 픽셀 크기로 줄 바꿈하고 조형·잔량 영역을 분리합니다. |
| [`draw_desktop_orbit`](src/visuals.py#L212) | 위젯의 조형과 글자를 별개 영역에 그려 작은 글자 축소를 막습니다. |
| [`_draw_desktop_information`](src/visuals.py#L227) | 움직이는 GPU 이미지와 분리한 도크·시계·지역·기온·잔량을 그립니다. |
| [`DesktopOverlayCache`](src/visuals.py#L278) | 한 위젯의 완전 입력이 같을 때만 단일 투명 정보 레이어를 재사용합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`MOTION_PERIOD`](src/visuals.py#L27) | `정의=18` |
| [`RING_TURNS`](src/visuals.py#L28) | `정의=(1, -2, 3)` |
| [`RING_AZIMUTHS`](src/visuals.py#L29) | `정의=(8., 128., 248.)` |
| [`RING_AXIS_TILTS`](src/visuals.py#L30) | `정의=(42., 46., 49.)` |
| [`RING_RADII`](src/visuals.py#L35) | `정의=(45., 51., 57.)` |
| [`BASE_ANGLES`](src/visuals.py#L36) | `정의=tuple((math.radians(tilt), 0., math.radians(azimuth))                     for tilt, azimuth in zip((52., 58., 62.), RING_AZIMUTHS))` |
| [`ATOM_RECT`](src/visuals.py#L92) | `정의=QRectF(-48,-74,96,96)` |
| [`DOCK_RECT`](src/visuals.py#L93) | `정의=QRectF(-68,25,136,27)` |
| [`USAGE_RECT`](src/visuals.py#L94) | `정의=QRectF(-68,56,136,16)` |
| [`USAGE_TRACK_RECT`](src/visuals.py#L95) | `정의=QRectF(-61,62,62,4)` |
| [`SYMBOL_PIXELS`](src/visuals.py#L96) | `정의=24` |

### [src/weather.py](src/weather.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`localized_region`](src/weather.py#L27) | 검색 전 임시 표시에는 검증된 국내 사전 또는 실제 원문 지명을 사용합니다. |
| [`select_geocoded_region`](src/weather.py#L67) | 동일 국가이면서 IP 추정 좌표에서30km 이내인 가장 가까운 검색 결과만 수락합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`_COUNTRIES`](src/weather.py#L23) | `정의={'US': '미국', 'JP': '일본', 'CN': '중국', 'GB': '영국', 'DE': '독일',               'FR': '프랑스', 'CA': '캐나다', 'AU': '호주', 'SG': '싱가포르', 'TW': '대만'}` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`language not in ('ko', 'en')`](src/weather.py#L29) | 지원 언어는 ko 또는 en입니다. |
| [`language not in ('ko', 'en')`](src/weather.py#L111) | 지원 언어는 ko 또는 en입니다. |
| [`language not in ('ko', 'en')`](src/weather.py#L155) | 지원 언어는 ko 또는 en입니다. |
| [`not self._valid_number(latitude, -90, 90) or not self._valid_number(longitude, -180, 180)`](src/weather.py#L249) | 위치 범위 |
| [`not self._valid_number(temperature, -100, 70)`](src/weather.py#L321) | 기온 범위 |
| [`not self._valid_number(observed, 0, now + 300)`](src/weather.py#L325) | 기온 제공 시각 |
| [`not isinstance(data, dict)`](src/weather.py#L232) | 응답 형식 |

</details>

<a name="results"></a>

## 📊 처리 결과와 출력 읽기

변경 전·후 모델과 추론 강도, 공개된 이유, 관측 시각과 근거 수준을 함께 읽습니다. 기록되지 않은 값은 미확인으로 남깁니다. 로컬 기록은 서버 모델 신원 증명이 아닙니다.

## 🛠️ 제약과 문제 해결

| 상황 | 확인할 내용 |
|---|---|
| 알림이 나타나지 않음 | 감시하는 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 확인합니다. 최초 기준선 읽기와 새 변경 감지는 다릅니다. |
| 자산 또는 글꼴 오류 | 이 차수에서 참조하는 assets와 라이선스를 준비합니다. 소스 이력에는 과거 대용량 프레임 자산이 없을 수 있습니다. |
| 이유 또는 이전값이 없음 | 원문 기록에 해당 필드가 있는지 확인합니다. 누락된 동기를 추정해서 채우지 않습니다. |

<a name="changes"></a>

## 🔍 직전 자료와 전체 비교

25차에서 26차로 이어지는 실제 파일 비교입니다.

[📄 전체 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff)

추가·수정·삭제, 주석·공백·개행과 바이너리 크기·해시는 연결된 원래 비교 자료에서 확인합니다.

<details>
<summary>📚 파일별 비교·크기·해시 자세히 보기</summary>

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

- **검증:** 이 폴더의 diff는 소스 바이트 비교입니다. 이후 로컬 원본 검증 자료를 대조해 작성한 [공개 검증 요약](../../docs/공개검증_26차.md)을 함께 제공합니다. 비공개 원본 로그는 공개하지 않으며 소스 비교 자체를 실행 결과로 해석하지 않습니다.

- **수정** `src/app.py`: 이전 110155바이트, SHA-256 `bb0421143d08d6930d62f19252819ca26a91444466002c1a559b0dc87895ac3b`; 현재 116115바이트, SHA-256 `ccb4c5771ab1a01e416e81dcc3678629cd5a5a2613e50d5e7c4a3e4263da964f`.

- **수정** `src/calendar_motion.py`: 이전 15710바이트, SHA-256 `fcd254efc4bf9e4a15eb9a1d75177323d34763716cea207e2bd95348b93463a0`; 현재 16207바이트, SHA-256 `ddb3e8afdf5f46f7bb8f997e75c39234550f28bade6223e19f81e37579765791`.

- **수정** `src/frame_pacing.py`: 이전 2625바이트, SHA-256 `6ca862a2eaa6707665f19514315de584424ab66017eff8f7898e3a4f6c6a9cb5`; 현재 3692바이트, SHA-256 `09cd3768e4baa326bb0e08e4d7fd8130f05526024686b88f8ef2f9b0366b1bb1`.

- **수정** `src/i18n.py`: 이전 19942바이트, SHA-256 `2dbea990824fb7107019228d5ecf6a75d7ce1a7062d0984f2a00908c7e26cec1`; 현재 20538바이트, SHA-256 `091208c023ccecdefd7957dcc3bacd8acc5c44324dd587ac36986ac3dc81106a`.

- **추가** `src/motion_label.py`: 이전 없음; 현재 2380바이트, SHA-256 `f76a05b63a676282ff4816c25ce0d7bc4aa01396889559c76021d5f858a0c60d`.

- **수정** `src/usage_widgets.py`: 이전 2471바이트, SHA-256 `a5e8de93da797f5f269551061d30878d8c0f86cae8824e89ba052bd6b28aeee2`; 현재 2516바이트, SHA-256 `9ad1be24d27cbf072db6892a2bc3c431304002f90f9a9d46d59494a91b74814c`.

- **수정** `src/visuals.py`: 이전 13297바이트, SHA-256 `d4bb20ebbfa421b5f05a482aedbb0b2202b7f7ffc2e6f7e22916ace3d0d72e1d`; 현재 15915바이트, SHA-256 `13a8d20b188ac2e82bc57771263dd6c2bef7cb3ab96ef259d51fd73fa380a57a`.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

</details>

[🏠 프로젝트](../../README.md) · [🗂️ 전체 차수](../../docs/REVISION_INDEX.md) · [📁 원본 자료](.) · [← 이전: 25차](../25/README.md) · [다음: 27차 →](../27/README.md)
