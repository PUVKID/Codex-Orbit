<div align="center">

<a name="-codex-orbit--8차"></a>
# Codex Orbit · 8차

감시 폴링 간격을 0.2초 상수로 두고 중복 기록 감지와 이벤트 보강·읽기 경로를 바꿉니다. 빠른 폴링 설정이 모든 부하에서 즉시 알림을 보장하지는 않습니다.

**기술 분류:** Windows 데스크톱 · Python · PySide6

[핵심 기능](#features) · [사용 흐름](#usage) · [자료 구성](#structure) · [준비와 실행](#setup) · [결과 읽기](#results) · [직전 변경](#changes)

</div>
<!-- reading-levels:start -->
[LEVEL 1 - Beginner](#reading-level-1) · [LEVEL 2 - Explorer](#reading-level-2) · [LEVEL 3 - Practitioner](#reading-level-3) · [LEVEL 4 - Advanced](#reading-level-4) · [LEVEL 5 - Expert](#reading-level-5)

프로젝트 전체의 설명은 [LEVEL 1 - Beginner](../../docs/%EC%9D%BD%EA%B8%B0%EC%95%88%EB%82%B4/%EB%A0%88%EB%B2%A81.md)부터 [LEVEL 5 - Expert](../../docs/%EC%9D%BD%EA%B8%B0%EC%95%88%EB%82%B4/%EB%A0%88%EB%B2%A85.md)까지 같은 범위로 연결됩니다.

<a id="reading-level-1"></a>
## LEVEL 1 - Beginner

### LEVEL 1 · 이 자료가 하는 일과 달라진 점

감시 폴링 간격을 0.2초 상수로 두고 중복 기록 감지와 이벤트 보강·읽기 경로를 바꿉니다. 빠른 폴링 설정이 모든 부하에서 즉시 알림을 보장하지는 않습니다.

### LEVEL 1 · 실제 동작을 따라 읽기

감시 폴링 간격을 0.2초 상수로 두고 중복 기록 감지와 이벤트 보강·읽기 경로를 바꿉니다. 빠른 폴링 설정이 모든 부하에서 즉시 알림을 보장하지는 않습니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

Codex App Server의 `account/rateLimits/read`를 읽기 전용으로 조회합니다. 표시값은 남은 토큰 개수가 아니라 계정 사용 한도 비율입니다.

JSONL은 한 줄마다 하나의 JSON 기록을 담은 파일입니다. CLI는 명령어와 옵션을 입력해 프로그램을 실행하는 방식입니다.

입력 — 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

처리 — 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시

출력 — 알림·변경 이력·로컬 진단 기록

### LEVEL 1 · 준비하고 확인할 것

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다.

자산과 의존성을 준비한 이 차수 폴더에서 `python src/app.py`를 실행합니다. history 소스만으로 과거 배포 EXE와 동일한 화면·자산이 모두 복원되지는 않습니다.

#### LEVEL 1 · 이 보관본의 의존성 목록

[requirements.txt](requirements.txt)의 실제 항목입니다. 외부 실행 도구와 GPU 드라이버는 별도로 준비합니다.

```text
PySide6-Essentials==6.12.0
PyInstaller==6.22.3
```

#### LEVEL 1 · 소스에서 제공하는 CLI 옵션

**진입 소스:** [app.py](src/app.py)

**정의된 옵션 이름:** `--data-dir`, `--sessions`, `--smoke-test`, `--usage-smoke-test`, `--smoke-report`, `--show-details`, `--show-event`

**진입 소스:** [notifier.py](src/notifier.py)

**정의된 옵션 이름:** `--sessions`, `--work`


각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 1 · [src/app.py](src/app.py)

| 정의 | 역할 |
| --- | --- |
| [`operation_record`](src/app.py#L33) | 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다. |
| [`short_reason`](src/app.py#L75) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |
| [`QuitGuard`](src/app.py#L801) | 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L1108)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L1109)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L1110)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--usage-smoke-test`](src/app.py#L1111)

**코드의 선언:** `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`

**설정·옵션:** [`--smoke-report`](src/app.py#L1112)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L1113)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L1114)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L61)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


**거부 조건:** [`not lock.tryLock(100)`](src/app.py#L1139)

**오류 메시지:** 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

**거부 조건:** [`not isinstance(value, dict)`](src/app.py#L146)

**오류 메시지:** 앱 설정은 JSON 객체여야 합니다.

**거부 조건:** [`not path.is_dir()`](src/app.py#L654)

**오류 메시지:** 존재하는 sessions 폴더를 선택하세요.

**거부 조건:** [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L659)

**오류 메시지:** 존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.

**거부 조건:** [`self.plan is None`](src/app.py#L764)

**오류 메시지:** 새 미리보기가 필요합니다.

**거부 조건:** [`not receipts`](src/app.py#L776)

**오류 메시지:** 앱이 만든 적용 백업이 없습니다.


#### LEVEL 1 · [src/core.py](src/core.py)

| 정의 | 역할 |
| --- | --- |
| [`read_jsonl_tail`](src/core.py#L18) | 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| [`title_catalog`](src/core.py#L55) | 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| [`resolve_title`](src/core.py#L73) | 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| [`safe_path`](src/core.py#L97) | 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`MAX_TEXT_BYTES`](src/core.py#L9) | `정의=2 * 1024 * 1024` |
| [`BEGIN`](src/core.py#L10) | `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| [`END`](src/core.py#L11) | `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

**거부 조건:** [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112)

**오류 메시지:** 문서가 2 MiB 상한을 초과했습니다.

**거부 조건:** [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64)

**오류 메시지:** 제목 캐시 구조가 올바르지 않습니다.

**거부 조건:** [`target.name.lower() != 'agents.md'`](src/core.py#L123)

**오류 메시지:** 적용 대상은 AGENTS.md 파일이어야 합니다.

**거부 조건:** [`not target.parent.is_dir()`](src/core.py#L125)

**오류 메시지:** 대상 폴더가 존재하지 않습니다.

**거부 조건:** [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127)

**오류 메시지:** 대상은 2 MiB 이하의 일반 파일이어야 합니다.

**거부 조건:** [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134)

**오류 메시지:** 빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.

**거부 조건:** [`BEGIN in added or END in added`](src/core.py#L136)

**오류 메시지:** 지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.

**거부 조건:** [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150)

**오류 메시지:** 적용 결과가 2 MiB 상한을 초과합니다.

**거부 조건:** [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157)

**오류 메시지:** 대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.

**거부 조건:** [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177)

**오류 메시지:** 미리보기 데이터가 변경되었습니다.

**거부 조건:** [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197)

**오류 메시지:** 유효한 앱 원문 백업이 아닙니다.

**거부 조건:** [`digest(raw) != receipt['before_hash']`](src/core.py#L200)

**오류 메시지:** 백업 해시가 일치하지 않습니다.

**거부 조건:** [`not isinstance(row, dict)`](src/core.py#L40)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143)

**오류 메시지:** 기존 관리구역 표식이 손상되었거나 중복되었습니다.


#### LEVEL 1 · [src/notifier.py](src/notifier.py)

| 정의 | 역할 |
| --- | --- |
| [`atomic_json`](src/notifier.py#L32) | 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다. |
| [`source_datetime`](src/notifier.py#L62) | 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다. |
| [`duplicate_record`](src/notifier.py#L184) | 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다. |
| [`settings_record`](src/notifier.py#L195) | 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다. |
| [`lookup_parent_reason`](src/notifier.py#L335) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L382) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L636) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L637) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L17) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L18) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L19) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L20) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L21) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L22) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L23) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L24) | `정의=256` |
| [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25) | `정의=0.2` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L89)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') not in (2, 3)`](src/notifier.py#L93)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L95)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L97)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('settings'), dict)`](src/notifier.py#L116)

**오류 메시지:** 채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`backup.read_bytes() != original`](src/notifier.py#L104)

**오류 메시지:** 이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다.

**거부 조건:** [`any(isinstance(v, bool) or not isinstance(v, int) or v &lt; 0 for v in (offset, end))`](src/notifier.py#L111)

**오류 메시지:** 이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L435)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L500)

**오류 메시지:** 명시 알림 파일 상한 초과


#### LEVEL 1 · [src/theme.py](src/theme.py)

| 정의 | 역할 |
| --- | --- |
| [`MonochromeStyle`](src/theme.py#L46) | 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다. |
| [`KoreanDialogs`](src/theme.py#L71) | 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다. |
| [`DialogLayout`](src/theme.py#L87) | 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다. |

#### LEVEL 1 · [src/usage.py](src/usage.py)

| 정의 | 역할 |
| --- | --- |
| [`number`](src/usage.py#L16) | 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다. |
| [`normalize_limits`](src/usage.py#L35) | 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다. |
| [`discover_codex`](src/usage.py#L69) | 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`MAX_BYTES`](src/usage.py#L12) | `정의=1024 * 1024` |
| [`KST`](src/usage.py#L13) | `정의=timezone(timedelta(hours=9))` |

| 거부 조건 | 오류 메시지 |
| --- | --- |
| [`not isinstance(message, dict)`](src/usage.py#L226) | 객체가 아닌 응답 |

#### LEVEL 1 · [src/visuals.py](src/visuals.py)

| 정의 | 역할 |
| --- | --- |
| [`rotate_point`](src/visuals.py#L8) | X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다. |
| [`orbit_segments`](src/visuals.py#L23) | 세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다. |
| [`draw_orbit`](src/visuals.py#L54) | 장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다. |

</details>

1. 이 차수의 소스·requirements와 필요한 자산을 한 작업 폴더에 준비합니다.
2. 앱을 열고 위젯·상세창에서 감시 경로와 표시되는 기록을 확인합니다.
3. 새 변경이 기록되면 이전·이후 값과 이유를 비교하고, 기록 종류와 근거 수준을 함께 읽습니다.
4. 설정·이력은 개인 운영자료로 관리하고 다른 사용자에게 공유하기 전에 내용을 확인합니다.

### LEVEL 1 · 결과와 주의할 범위

변경 전·후 모델과 추론 강도, 공개된 이유, 관측 시각과 근거 수준을 함께 읽습니다. 기록되지 않은 값은 미확인으로 남깁니다. 로컬 기록은 서버 모델 신원 증명이 아닙니다.

**상황:** 알림이 나타나지 않음

**확인할 내용:** 감시하는 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 확인합니다. 최초 기준선 읽기와 새 변경 감지는 다릅니다.

**상황:** 자산 또는 글꼴 오류

**확인할 내용:** 이 차수에서 참조하는 assets와 라이선스를 준비합니다. 소스 이력에는 과거 대용량 프레임 자산이 없을 수 있습니다.

**상황:** 이유 또는 이전값이 없음

**확인할 내용:** 원문 기록에 해당 필드가 있는지 확인합니다. 누락된 동기를 추정해서 채우지 않습니다.


[자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)



### LEVEL 1 · 8차의 구체적인 기능과 확인

기록 폴더에 새 내용이 생겼는지 되풀이해 확인하는 것을 폴링이라고 합니다. 이 차수는 그 간격을 0.2초로 두고, 같은 기록을 또 알리지 않도록 판별하고 사건 정보를 보강하는 읽기 경로를 바꿨습니다. 0.2초는 확인 간격 설정이며 모든 알림이 그 안에 보인다는 약속은 아닙니다.

**입력은 기록 파일, 출력은 알림과 이력입니다.** Codex의 sessions 폴더에는 이 사용자의 작업 기록이 쌓입니다. 앱이 새 기록을 읽으면 이전·이후 모델과 추론 강도, 적혀 있는 이유를 정리해 보여 줍니다. JSON은 항목 이름과 값을 짝으로 저장하는 자료 형식입니다. 처음 읽은 기록을 출발점으로 삼는 것과 그 뒤 새로 생긴 변경을 알리는 것은 다릅니다.

Windows에서 이 차수의 [requirements.txt](requirements.txt)에 맞는 Python 의존성과 해당 자산을 준비한 뒤 **이 차수 폴더에서** `python src/app.py`를 실행합니다. 현재 루트의 assets가 과거 모든 차수와 호환되는 것은 아니며, history 소스만으로 과거 EXE의 화면·자산 전체가 복원되는 것도 아닙니다.

확인 순서는 **같은 차수 자료 준비 → 감시 경로 확인 → 새 기록과 알림·상세 대조 → 누락값과 오류 확인**입니다. 예를 들어 기록에 모델 변경이 남았다면 알림의 이전·현재 값과 상세 이력을 비교합니다. 원문에 이유나 이전값이 없다면 모르는 상태로 읽고 채워 넣지 않습니다.

**함께 준비할 도구 버전**: PySide6-Essentials==6.12.0 · PyInstaller==6.22.3. PySide6는 창을 만드는 도구이고 PyInstaller는 실행 파일을 묶는 도구입니다. 외부 실행 도구·GPU 드라이버는 별도 조건입니다.

**자료를 찾는 순서**

- [src/](src): 관련 파일을 모아 둔 폴더.

- [README.md](README.md#reading-level-1): 설명을 읽는 Markdown 문서.

- [requirements.txt](requirements.txt): 문자로 적은 목록 파일.

- [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json): 항목별 값을 저장한 자료.

- [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md): 설명을 읽는 Markdown 문서.

- [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json): 항목별 값을 저장한 자료.

- [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff): 전후 파일의 달라진 줄을 기록한 비교 자료.

- [src/app.py](src/app.py): 이 부분이 맡는 일은 다음과 같습니다. Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용.

- [src/notifier.py](src/notifier.py): 이 부분이 맡는 일은 다음과 같습니다. 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다.

- [src/core.py](src/core.py): 이 부분이 맡는 일은 다음과 같습니다. 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용.

- [src/theme.py](src/theme.py): 이 부분이 맡는 일은 다음과 같습니다. 앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

- [src/usage.py](src/usage.py): 이 부분이 맡는 일은 다음과 같습니다. Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

- [src/visuals.py](src/visuals.py): 이 부분이 맡는 일은 다음과 같습니다. 실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

**실제 입력·설정과 기본값**

아래 이름은 설정을 소스에서 찾기 위한 표지입니다. 각 항목의 역할·단위·적용 상황을 먼저 읽고 뒤의 원문 선언으로 정확한 숫자를 확인합니다. 식에 1024가 쓰이면 바이트 단위 크기 계산이며 1 KiB=1,024바이트, 1 MiB=1,048,576바이트입니다. 이 설명은 설정을 임의로 바꾸라는 실행 지시가 아닙니다.

- [`--data-dir`](src/app.py#L1108) (src/app.py)

  앱 설정·이력을 저장할 폴더를 고릅니다. 기본은 LOCALAPPDATA 아래 CodexOrbit이며 그 환경값이 없으면 사용자 홈을 기준으로 합니다. 같은 폴더 중복 실행 잠금과 연결됩니다. 원문 선언: `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`.

- [`--sessions`](src/app.py#L1109) (src/app.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path`.

- [`--smoke-test`](src/app.py#L1110) (src/app.py)

  점검 실행을 켜는 스위치입니다. 숫자를 넣는 옵션이 아니라 이름을 붙여 켭니다. 옵션 존재 자체가 검사를 실행해 통과했다는 증거는 아닙니다. 원문 선언: `action='store_true'`.

- [`--usage-smoke-test`](src/app.py#L1111) (src/app.py)

  실제 계정 한도와 표시를 조회한 뒤 종료하는 점검 스위치입니다. 로컬 그림만 확인하는 검사와 달리 계정 연결 조건이 필요하고 비율을 잔여 토큰 개수로 읽지 않습니다. 원문 선언: `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`.

- [`--smoke-report`](src/app.py#L1112) (src/app.py)

  점검 결과를 저장할 파일 경로입니다. 폴더를 고르는 세션 옵션과 달리 보고서 파일을 지정합니다. 원문 선언: `type=Path`.

- [`--show-details`](src/app.py#L1113) (src/app.py)

  처음부터 상세창을 보여 주는 스위치입니다. 숨겨진 원문 값을 새로 만들어 주는 기능이 아닙니다. 원문 선언: `action='store_true'`.

- [`--show-event`](src/app.py#L1114) (src/app.py)

  이미 있는 이력의 사건 ID 또는 대상 ID를 지정해 다시 표시합니다. 실제 저장된 ID와 맞춰 읽고 새 사건 생성과 구분합니다. 원문 선언: `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`.

- [`ROLE_LABELS`](src/app.py#L61) (src/app.py)

  역할 코드와 사용자용 한글 이름의 대응표입니다. 예를 들어 build는 구현, verifier는 독립 검증으로 읽습니다. 화면 설명을 바꾸는 표이며 서버 모델을 바꾸는 설정은 아닙니다. 원문 선언: `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`.

- [`MAX_TEXT_BYTES`](src/core.py#L9) (src/core.py)

  읽거나 적용할 지침 문서의 크기 상한입니다. 원문·추가 지침·최종 결과의 제한과 연결되며 큰 문서 쓰기를 무제한 허용하지 않습니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`BEGIN`](src/core.py#L10) (src/core.py)

  앱이 관리하는 지침 구간이 시작되는 정확한 표시 문자열입니다. 문서의 나머지 부분과 구분하기 때문에 추가할 지침 안에 같은 표식을 넣지 못하게 합니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'`.

- [`END`](src/core.py#L11) (src/core.py)

  앱 관리 구간이 끝나는 정확한 표시 문자열입니다. 시작 표시보다 먼저 있거나 여러 번 있으면 원래 구간이 불명확해 적용을 거부하는 조건과 연결됩니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'`.

- [`--sessions`](src/notifier.py#L636) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L637) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L17) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L18) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L19) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게 하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L20) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록 하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L21) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게 합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L22) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L23) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료량을 제한합니다. 파일 하나의 상한과 별개인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L24) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

- [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25) (src/notifier.py)

  새 기록이 있는지 다시 확인하는 간격이며 단위는 초입니다. 0.2초는 1초의 5분의 1마다 확인하려는 설정이고 실제 알림이 그 시간 안에 반드시 뜬다는 보장은 아닙니다. 선언 숫자는 0.2입니다. 원문 선언: `정의=0.2`.

- [`MAX_BYTES`](src/usage.py#L12) (src/usage.py)

  계정 응답에서 읽을 최대 자료량입니다. 단위는 바이트이며 응답이 너무 클 때 무제한으로 받아들이지 않게 하는 경계입니다. 계산한 값은 1,048,576이며 바이트 제한에서는 1,024 KiB입니다. 원문 선언: `정의=1024 * 1024`.

- [`KST`](src/usage.py#L13) (src/usage.py)

  한국 표준시를 나타냅니다. UTC보다 9시간 빠른 시간대로 날짜·시각을 읽는 기준이며 컴퓨터 지역 시간과 구별합니다. 원문 선언: `정의=timezone(timedelta(hours=9))`.

**처리 책임과 원문에 명시된 함수 동작**

- [`operation_record`](src/app.py#L33) (src/app.py)

  앱 시작과 감시 진행을 조사해야 하는 경우, 대화 본문을 넣지 않고 진행 단계와 실제 실행 중인 프로그램의 위치를 기록합니다. 운영 단계를 확인하는 기록이 남습니다 단계 진단에 필요하지 않은 대화 내용까지 복제하지 않기 위해서입니다

- [`short_reason`](src/app.py#L75) (src/app.py)

  변경 알림에서 짧은 이유가 필요한 경우, 기록에 명시된 이유 또는 배정·선택 목적 문장을 우선 골라 짧게 보여 줍니다 원문에 있는 이유를 읽을 수 있고 없는 이유는 만들어지지 않습니다. 공개된 문장과 앱이 추측한 동기를 혼동하지 않도록 하기 위해서입니다

- [`QuitGuard`](src/app.py#L801) (src/app.py)

  감시가 일하는 도중 사용자가 앱 종료를 누른 경우, 종료 요청을 곧바로 끝내지 않고 감시 작업자가 따로 정리 작업을 마친 뒤 종료를 처리합니다. 작업 정리와 창 종료의 순서가 유지됩니다. 아직 실행 중인 감시 작업을 남겨 둔 채 화면만 없애지 않도록 하기 위해서입니다

- [`read_jsonl_tail`](src/core.py#L18) (src/core.py)

  기록 파일의 끝부분만 읽어 첫 줄이나 마지막 줄이 중간에 잘려 들어온 경우, 파일에서 실제 줄바꿈을 뜻하는 LF 바이트로만 한 건씩 나누고 완성되지 않은 양끝 조각은 해석하지 않습니다. 온전한 줄만 기록 한 건으로 읽습니다. 예를 들어 읽어 온 끝에 {"model": 뒤까지만 있고 닫는 부분이 없다면 그 조각을 새 변경 한 건으로 해석하지 않습니다. 이 문자열은 잘린 자료를 설명하는 예시이며 실제 세션을 수정하라는 지시가 아닙니다. 문장 안의 다른 줄바꿈 모양 문자나 반쪽 기록을 새 사건으로 잘못 세지 않기 위해서입니다

- [`title_catalog`](src/core.py#L55) (src/core.py)

  같은 작업에 제목 정보가 여러 출처로 남아 있는 경우, 공식 앱에서 확인해 저장한 제목과 컴퓨터 안의 제목 목록이 어디서 왔는지 함께 보존합니다. 제목과 그 제목을 얻은 출처를 대조할 수 있습니다. 제목 문자열만 같다는 이유로 근거 수준까지 같다고 보지 않기 위해서입니다

- [`resolve_title`](src/core.py#L73) (src/core.py)

  한 채팅에서 별도 자식 작업이 실행된 기록을 표시하는 경우, 실제 부모 채팅 제목과 자식 작업명을 서로 다른 정보로 다룹니다 어느 대화에서 생긴 어떤 작업인지 구별됩니다. 작업명을 새 채팅 제목이나 다른 부모 채팅으로 오해하지 않기 위해서입니다

- [`safe_path`](src/core.py#L97) (src/core.py)

  지침을 적용할 파일이나 그 파일에 이르는 상위 폴더가 다른 곳으로 연결된 경우, 파일 자체뿐 아니라 이미 존재하는 상위 폴더까지 확인해 바로가기처럼 다른 위치로 보내는 링크·재분석 지점을 거부합니다. 연결을 통해 의도 밖의 위치를 수정하는 경로는 허용되지 않습니다. 예를 들어 선택한 작업 폴더가 실은 다른 폴더로 보내는 연결이라면, 그 안의 AGENTS.md를 선택해도 그 연결을 따라 쓰기를 진행하지 않습니다. 겉으로 고른 폴더와 실제 쓰는 위치가 달라지는 일을 막기 위해서입니다

- [`atomic_json`](src/notifier.py#L32) (src/notifier.py)

  앱 상태를 저장하는 도중 다른 프로그램이 파일을 잠깐 사용하는 경우, 같은 폴더에 따로 임시 파일을 완성한 뒤 교체하고 Windows의 짧은 파일 공유 충돌만 다시 시도합니다. 반쯤 쓴 상태를 원래 파일처럼 노출하지 않도록 저장 경로를 구성합니다. 파일 저장 전체를 무제한 재시도하거나 모든 오류를 정상으로 감추지 않기 위해서입니다

- [`source_datetime`](src/notifier.py#L62) (src/notifier.py)

  사건 순서를 원본 시각으로 비교하는 경우, 어느 시간대인지 포함한 올바른 원본 시각만 비교에 사용합니다. 시각이 없으면 새 시각을 추측해 채우지 않습니다. 출처 불명확한 시각으로 사건 순서를 확정하지 않기 위해서입니다

- [`duplicate_record`](src/notifier.py#L184) (src/notifier.py)

  같은 기록이 복사되어 다시 발견된 경우, 원본 시각이 있는 복제만 중복으로 제외하고 과거 기준선을 다시 읽을 때의 순서는 복원합니다. 복제 제거와 순서 복원이 서로 다른 처리로 유지됩니다. 시각이 없는 기록을 추측만으로 중복이라 지워 버리지 않기 위해서입니다

- [`settings_record`](src/notifier.py#L195) (src/notifier.py)

  현재 채팅의 앱 자체 설정 기록을 읽는 경우, 그 채팅에 실제로 저장된 native 설정 항목만 관측합니다. 설정값은 읽지만 누가 바꿨는지와 실제 실행 모델은 추정하지 않습니다. 설정 선택과 서버에서 수행한 모델 실행을 같은 증거로 보지 않기 위해서입니다

- [`lookup_parent_reason`](src/notifier.py#L335) (src/notifier.py)

  자식 사건의 배정 이유가 큰 부모 기록에 남아 있는 경우, 부모 기록의 최근 공개 호출만 정해진 양 안에서 찾아보고 정기 감시의 읽기 위치는 그대로 둡니다 이유를 찾는 보조 읽기가 다음 감시 출발점을 옮기지 않습니다. 부모 이유를 찾다가 새 사건을 건너뛰거나 전체 큰 파일을 무제한 읽지 않기 위해서입니다

- [`enrich_event`](src/notifier.py#L382) (src/notifier.py)

  이력이 이미 전달됐지만 첫 배정 이유가 뒤늦게 확인된 경우, 정확히 연결된 사건의 첫 배정 이유만 기존 이력에 덧붙이고 새 알림은 띄우지 않습니다. 같은 사건의 설명이 보강되고 중복 알림은 만들어지지 않습니다. 이유 보강과 새 모델 변경 사건을 구분하기 위해서입니다

- [`MonochromeStyle`](src/theme.py#L46) (src/theme.py)

  앱 안의 파일·메시지 표준 아이콘이 표시되는 경우, 운영체제 기본 기호도 앱 안에서는 색이 없는 표현으로 맞춥니다 앱 소유 화면 안의 기호 표현이 정리됩니다. 앱 바깥 운영체제의 아이콘까지 바꾸는 설정으로 확대하지 않도록 범위를 구분해야 합니다

- [`KoreanDialogs`](src/theme.py#L71) (src/theme.py)

  배포 앱에 Qt의 별도 번역 파일이 없는 경우, 기본 파일 선택창의 정해진 문구를 한국어로 제공합니다. 번역 묶음이 없어도 기본 파일 선택 안내를 읽을 수 있습니다. 앱 안내 문구와 사용자가 고르는 파일 이름을 구분하기 위해서입니다

- [`DialogLayout`](src/theme.py#L87) (src/theme.py)

  파일 선택창에 긴 이름과 한글 버튼이 함께 있는 경우, 파일 이름 열과 한글 버튼에 필요한 표시 공간을 확보합니다. 이름과 버튼을 구별해서 읽는 배치가 됩니다. 번역 문구를 넣기만 하고 화면 공간은 그대로 두는 문제를 피하기 위해서입니다

- [`number`](src/usage.py#L16) (src/usage.py)

  한도 응답에 숫자 대신 참·거짓, 문자열 또는 무한대 같은 값이 들어온 경우, 그 값을 올바른 한도 숫자로 받아들이지 않습니다. 잘못된 입력이 사용 가능한 비율로 표시되지 않습니다. 예를 들어 숫자 1과 참 값 true, 숫자 모양 문자열 "1", 무한대는 종류가 다릅니다. 불리언은 참·거짓 값이고 비유한은 무한대나 숫자 아님 같은 값이므로 한도 숫자로 바꿔 채우지 않습니다. 예를 들어 참을 숫자 1처럼 읽어 정상 비율로 오해하지 않기 위해서입니다

- [`normalize_limits`](src/usage.py#L35) (src/usage.py)

  계정 한도가 기간별 여러 묶음으로 응답한 경우, 공식 응답의 여러 한도 묶음을 우선 읽고 빠진 기간이나 수치를 덧만들지 않습니다. 존재하는 기간의 실제 비율만 표시 근거가 됩니다. 없는 주간·단기 한도를 다른 값으로 추정해 채우지 않기 위해서입니다

- [`discover_codex`](src/usage.py#L69) (src/usage.py)

  계정 한도를 읽을 Codex 실행 프로그램을 찾는 경우, 사용자가 고른 위치, 명령 검색 경로 PATH, 공식 데스크톱 앱 묶음 위치 순서로 실행 파일 EXE만 찾습니다 선택 순서에 맞는 실제 실행 파일이 연결 후보가 됩니다. 동명이름의 문서·폴더를 실행 프로그램으로 잘못 사용하지 않기 위해서입니다

- [`rotate_point`](src/visuals.py#L8) (src/visuals.py)

  입체 점의 방향을 바꾸는 경우, 가로 X축·세로 Y축·깊이 Z축 순서로 회전시키고 깊이값도 남깁니다. 평면 위치뿐 아니라 앞뒤를 나타내는 좌표가 유지됩니다. 회전 순서를 바꾸면 같은 각도여도 물체 방향이 달라질 수 있기 때문입니다

- [`orbit_segments`](src/visuals.py#L23) (src/visuals.py)

  구의 중심을 지나는 큰 원 세 개를 화면에 그리는 경우, 원들을 작은 선 조각으로 나누고 먼 곳은 작게 보이는 원근 계산으로 옮긴 뒤 뒤쪽부터 정렬합니다. 앞쪽 선이 뒤쪽 선 위에 그려질 순서가 나옵니다 겹침과 깊이감을 화면의 실제 그리기 순서에 연결하기 위해서입니다

- [`draw_orbit`](src/visuals.py#L54) (src/visuals.py)

  입체 관 모양 궤도와 실제 계정 숫자를 합성하는 경우, 움직이는 장식과 실제 숫자를 별도로 다루고 원문에 정한 앞쪽 관이 중심을 가리는 순서로 그립니다 이 차수의 가림 규칙이 반영된 합성이 나옵니다 후속 차수의 중심 숫자 고정·가림 방지 규칙을 과거 차수에 거꾸로 적용하지 않기 위해서입니다

**멈추거나 거부되는 조건과 읽는 방법**

- 오류 “같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.”

  같은 저장 폴더를 이미 다른 Codex Orbit가 쓰거나 잠금 파일에 접근할 수 없으면 시작을 거부합니다. 한 설정·상태 파일을 두 실행이 동시에 바꾸지 않도록 하며, 이 메시지만으로 어느 쪽 원인인지 확정하지 않습니다. 정확한 조건은 [`not lock.tryLock(100)`](src/app.py#L1139) (src/app.py)에서 확인할 수 있습니다.

- 오류 “앱 설정은 JSON 객체여야 합니다.”

  앱 설정이 항목 이름과 값을 가진 사전이어야 합니다. 예를 들어 목록만 저장돼 있으면 설정 이름으로 값을 찾을 수 없어 거부합니다. 정확한 조건은 [`not isinstance(value, dict)`](src/app.py#L146) (src/app.py)에서 확인할 수 있습니다.

- 오류 “존재하는 sessions 폴더를 선택하세요.”

  선택한 기록 경로가 실제 폴더가 아니면 거부합니다. 오타가 있는 위치나 파일 하나를 감시 폴더로 잘못 지정했는지 먼저 확인합니다. 정확한 조건은 [`not path.is_dir()`](src/app.py#L654) (src/app.py)에서 확인할 수 있습니다.

- 오류 “존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.”

  수동으로 지정한 경로가 실제 .exe 실행 파일이 아니면 거부합니다. 실제 Codex 실행 파일을 고르거나 값을 비워 정해진 자동 탐색을 사용해야 합니다. 정확한 조건은 [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L659) (src/app.py)에서 확인할 수 있습니다.

- 오류 “새 미리보기가 필요합니다.”

  아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다. 대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다. 정확한 조건은 [`self.plan is None`](src/app.py#L764) (src/app.py)에서 확인할 수 있습니다.

- 오류 “앱이 만든 적용 백업이 없습니다.”

  앱이 지침 적용 전에 만든 백업이 없으면 그 백업을 이용한 되돌리기를 할 수 없습니다. 임의의 다른 문서를 원래 내용이라고 추정하지 않습니다. 정확한 조건은 [`not receipts`](src/app.py#L776) (src/app.py)에서 확인할 수 있습니다.

- 오류 “문서가 2 MiB 상한을 초과했습니다.”

  지침 원본 문서가 2 MiB보다 크면 읽기 범위를 벗어나 거부합니다. 작은 설명으로 예상한 입력을 대용량 파일 읽기로 확대하지 않는 제한입니다. 정확한 조건은 [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112) (src/core.py)에서 확인할 수 있습니다.

- 오류 “제목 캐시 구조가 올바르지 않습니다.”

  보관한 제목 목록이 기대한 이름별 저장 형식이 아니면 거부합니다. 제목의 출처와 연결을 알 수 없는데도 빈 목록으로 자동 덮어쓰지 않습니다. 정확한 조건은 [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64) (src/core.py)에서 확인할 수 있습니다.

- 오류 “적용 대상은 AGENTS.md 파일이어야 합니다.”

  선택한 파일 이름이 AGENTS.md가 아니면 적용하지 않습니다. 다른 문서나 데이터 파일을 지침 대상이라고 잘못 수정하지 않기 위한 이름 확인입니다. 정확한 조건은 [`target.name.lower() != 'agents.md'`](src/core.py#L123) (src/core.py)에서 확인할 수 있습니다.

- 오류 “대상 폴더가 존재하지 않습니다.”

  대상 파일을 둘 상위 폴더가 없으면 적용하지 않습니다. 앱이 의도하지 않은 위치의 폴더를 새로 만들어 결과를 숨기는 대신 선택 경로부터 확인하게 합니다. 정확한 조건은 [`not target.parent.is_dir()`](src/core.py#L125) (src/core.py)에서 확인할 수 있습니다.

- 오류 “대상은 2 MiB 이하의 일반 파일이어야 합니다.”

  기존 대상이 일반 파일이 아니거나 2 MiB보다 크면 적용하지 않습니다. 폴더·특수 파일을 문서처럼 취급하거나 대용량 원본을 바꾸지 않게 합니다. 정확한 조건은 [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127) (src/core.py)에서 확인할 수 있습니다.

- 오류 “빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.”

  내용이 공백뿐이거나 새로 붙일 지침이 2 MiB보다 크면 거부합니다. 아무 내용 없는 적용이나 과도한 추가 입력을 정상 변경으로 보지 않습니다. 정확한 조건은 [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134) (src/core.py)에서 확인할 수 있습니다.

- 오류 “지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.”

  추가 지침 안에 앱의 시작·끝 관리 표시가 들어 있으면 거부합니다. 내용 속 표시를 실제 관리 경계로 잘못 읽어 원문 구간을 혼동하지 않도록 합니다. 정확한 조건은 [`BEGIN in added or END in added`](src/core.py#L136) (src/core.py)에서 확인할 수 있습니다.

- 오류 “적용 결과가 2 MiB 상한을 초과합니다.”

  원본과 새 지침을 합친 최종 문서가 2 MiB보다 크면 쓰지 않습니다. 원본과 추가분이 각각 작더라도 합쳐진 결과는 별도 크기 제한을 만족해야 합니다. 정확한 조건은 [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150) (src/core.py)에서 확인할 수 있습니다.

- 오류 “대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.”

  아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다. 대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다. 정확한 조건은 [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157) (src/core.py)에서 확인할 수 있습니다.

- 오류 “미리보기 데이터가 변경되었습니다.”

  미리보기 계획 안의 원문·결과 바이트가 저장된 지문과 다르면 거부합니다. 사용자가 확인했던 변경 계획과 실제 쓸 내용이 같은지 확인하는 경계입니다. 정확한 조건은 [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177) (src/core.py)에서 확인할 수 있습니다.

- 오류 “유효한 앱 원문 백업이 아닙니다.”

  백업이 앱이 정한 백업 폴더 안의 정상 파일이 아니거나 크기 제한을 넘으면 복원에 쓰지 않습니다. 아무 파일이나 원래 문서라고 덮어쓰지 않기 위한 확인입니다. 정확한 조건은 [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197) (src/core.py)에서 확인할 수 있습니다.

- 오류 “백업 해시가 일치하지 않습니다.”

  백업 내용의 지문이 적용 때 기록한 원본 지문과 다르면 되돌리기를 거부합니다. 파일 이름이 같더라도 내용이 달라졌다면 안전한 원본으로 보지 않습니다. 정확한 조건은 [`digest(raw) != receipt['before_hash']`](src/core.py#L200) (src/core.py)에서 확인할 수 있습니다.

- 오류 “JSON 객체가 아닙니다.”

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다. 정확한 조건은 [`not isinstance(row, dict)`](src/core.py#L40) (src/core.py)에서 확인할 수 있습니다.

- 오류 “기존 관리구역 표식이 손상되었거나 중복되었습니다.”

  시작·끝 표시가 정확히 한 쌍이 아니거나 순서가 뒤집혔다면 적용할 구간이 불명확해 거부합니다. 여러 구간 중 임의의 하나를 골라 원문을 바꾸지 않습니다. 정확한 조건은 [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143) (src/core.py)에서 확인할 수 있습니다.

- 오류 “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”

  이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다. 큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다. 정확한 조건은 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L89) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.”

  옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다. 이를 새 관측 이력으로 자동 해석하지 않습니다. 명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다. 정확한 조건은 [`self.state.get('schema_version') not in (2, 3)`](src/notifier.py#L93) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”

  저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다. 자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다. 정확한 조건은 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L95) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”

  어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다. 이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다. 정확한 조건은 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L97) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”

  채팅별 선택 설정 항목이 기대한 사전 형태가 아니면 저장 상태를 거부합니다. 설정 요청을 실제 관측 변경으로 잘못 바꾸는 자동 초기화를 하지 않습니다. 정확한 조건은 [`not isinstance(self.state.get('settings'), dict)`](src/notifier.py#L116) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다.”

  활동 상태 형식을 옮기기 전의 백업 내용이 원본과 다르면 덮어쓰지 않습니다. 이행은 저장 형식을 바꾸는 과정이며 다른 원본을 같은 자료처럼 취급하지 않습니다. 정확한 조건은 [`backup.read_bytes() != original`](src/notifier.py#L104) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다.”

  이전 기록에서 읽어 둔 시작·끝 위치가 참·거짓, 정수가 아닌 값 또는 음수라면 거부합니다. 파일의 몇 번째 바이트부터 읽을지를 알 수 없으므로 0으로 임의 초기화하지 않습니다. 정확한 조건은 [`any(isinstance(v, bool) or not isinstance(v, int) or v &lt; 0 for v in (offset, end))`](src/notifier.py#L111) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “JSON 객체가 아닙니다.”

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다. 정확한 조건은 [`not isinstance(record, dict)`](src/notifier.py#L435) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “명시 알림 파일 상한 초과”

  명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다. 짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게 하기 위한 크기 제한입니다. 정확한 조건은 [`path.stat().st_size &gt; 20000`](src/notifier.py#L500) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “객체가 아닌 응답”

  계정 서버의 응답이 이름별 값을 가진 객체가 아니면 한도 자료로 읽지 않습니다. 숫자·문자열만 온 응답에서 비율을 임의로 만들지 않습니다. 정확한 조건은 [`not isinstance(message, dict)`](src/usage.py#L226) (src/usage.py)에서 확인할 수 있습니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다. 최초 기준선 읽기와 새 변경은 다릅니다. 자산·글꼴 오류라면 이 차수 assets와 라이선스를 대조합니다. 과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다. 이유·이전값이 없으면 원문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

7차 → 8차의 실제 파일 비교입니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **수정** [src/app.py](src/app.py): 이름 옆의 변화 종류를 기준으로 원래 파일과 달라진 내용을 읽습니다.

- **수정** [src/notifier.py](src/notifier.py): 이름 옆의 변화 종류를 기준으로 원래 파일과 달라진 내용을 읽습니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다. 원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다. 이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다. Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.

<a id="reading-level-2"></a>
## LEVEL 2 - Explorer

### LEVEL 2 · 목적과 구성의 연결

감시 폴링 간격을 0.2초 상수로 두고 중복 기록 감지와 이벤트 보강·읽기 경로를 바꿉니다. 빠른 폴링 설정이 모든 부하에서 즉시 알림을 보장하지는 않습니다.

감시 폴링 간격을 0.2초 상수로 두고 중복 기록 감지와 이벤트 보강·읽기 경로를 바꿉니다. 빠른 폴링 설정이 모든 부하에서 즉시 알림을 보장하지는 않습니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

Codex App Server의 `account/rateLimits/read`를 읽기 전용으로 조회합니다. 표시값은 남은 토큰 개수가 아니라 계정 사용 한도 비율입니다.

### LEVEL 2 · 입력에서 출력으로

| 단계 | 내용 |
| --- | --- |
| 입력 | 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정 |
| 처리 | 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시 |
| 출력 | 알림·변경 이력·로컬 진단 기록 |


입력·처리·출력은 위의 같은 자료 흐름을 다른 단계에서 읽는 기준입니다. 처리 조건과 출력의 의미를 함께 확인합니다.

### LEVEL 2 · 설정과 처리 순서의 관계

1. 이 차수의 소스·requirements와 필요한 자산을 한 작업 폴더에 준비합니다.
2. 앱을 열고 위젯·상세창에서 감시 경로와 표시되는 기록을 확인합니다.
3. 새 변경이 기록되면 이전·이후 값과 이유를 비교하고, 기록 종류와 근거 수준을 함께 읽습니다.
4. 설정·이력은 개인 운영자료로 관리하고 다른 사용자에게 공유하기 전에 내용을 확인합니다.

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다.

자산과 의존성을 준비한 이 차수 폴더에서 `python src/app.py`를 실행합니다. history 소스만으로 과거 배포 EXE와 동일한 화면·자산이 모두 복원되지는 않습니다.

#### LEVEL 2 · 이 보관본의 의존성 목록

[requirements.txt](requirements.txt)의 실제 항목입니다. 외부 실행 도구와 GPU 드라이버는 별도로 준비합니다.

```text
PySide6-Essentials==6.12.0
PyInstaller==6.22.3
```

#### LEVEL 2 · 소스에서 제공하는 CLI 옵션

**진입 소스:** [app.py](src/app.py)

**정의된 옵션 이름:** `--data-dir`, `--sessions`, `--smoke-test`, `--usage-smoke-test`, `--smoke-report`, `--show-details`, `--show-event`

**진입 소스:** [notifier.py](src/notifier.py)

**정의된 옵션 이름:** `--sessions`, `--work`


각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 2 · [src/app.py](src/app.py)

| 정의 | 역할 |
| --- | --- |
| [`operation_record`](src/app.py#L33) | 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다. |
| [`short_reason`](src/app.py#L75) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |
| [`QuitGuard`](src/app.py#L801) | 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L1108)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L1109)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L1110)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--usage-smoke-test`](src/app.py#L1111)

**코드의 선언:** `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`

**설정·옵션:** [`--smoke-report`](src/app.py#L1112)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L1113)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L1114)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L61)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


**거부 조건:** [`not lock.tryLock(100)`](src/app.py#L1139)

**오류 메시지:** 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

**거부 조건:** [`not isinstance(value, dict)`](src/app.py#L146)

**오류 메시지:** 앱 설정은 JSON 객체여야 합니다.

**거부 조건:** [`not path.is_dir()`](src/app.py#L654)

**오류 메시지:** 존재하는 sessions 폴더를 선택하세요.

**거부 조건:** [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L659)

**오류 메시지:** 존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.

**거부 조건:** [`self.plan is None`](src/app.py#L764)

**오류 메시지:** 새 미리보기가 필요합니다.

**거부 조건:** [`not receipts`](src/app.py#L776)

**오류 메시지:** 앱이 만든 적용 백업이 없습니다.


#### LEVEL 2 · [src/core.py](src/core.py)

| 정의 | 역할 |
| --- | --- |
| [`read_jsonl_tail`](src/core.py#L18) | 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| [`title_catalog`](src/core.py#L55) | 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| [`resolve_title`](src/core.py#L73) | 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| [`safe_path`](src/core.py#L97) | 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`MAX_TEXT_BYTES`](src/core.py#L9) | `정의=2 * 1024 * 1024` |
| [`BEGIN`](src/core.py#L10) | `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| [`END`](src/core.py#L11) | `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

**거부 조건:** [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112)

**오류 메시지:** 문서가 2 MiB 상한을 초과했습니다.

**거부 조건:** [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64)

**오류 메시지:** 제목 캐시 구조가 올바르지 않습니다.

**거부 조건:** [`target.name.lower() != 'agents.md'`](src/core.py#L123)

**오류 메시지:** 적용 대상은 AGENTS.md 파일이어야 합니다.

**거부 조건:** [`not target.parent.is_dir()`](src/core.py#L125)

**오류 메시지:** 대상 폴더가 존재하지 않습니다.

**거부 조건:** [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127)

**오류 메시지:** 대상은 2 MiB 이하의 일반 파일이어야 합니다.

**거부 조건:** [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134)

**오류 메시지:** 빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.

**거부 조건:** [`BEGIN in added or END in added`](src/core.py#L136)

**오류 메시지:** 지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.

**거부 조건:** [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150)

**오류 메시지:** 적용 결과가 2 MiB 상한을 초과합니다.

**거부 조건:** [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157)

**오류 메시지:** 대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.

**거부 조건:** [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177)

**오류 메시지:** 미리보기 데이터가 변경되었습니다.

**거부 조건:** [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197)

**오류 메시지:** 유효한 앱 원문 백업이 아닙니다.

**거부 조건:** [`digest(raw) != receipt['before_hash']`](src/core.py#L200)

**오류 메시지:** 백업 해시가 일치하지 않습니다.

**거부 조건:** [`not isinstance(row, dict)`](src/core.py#L40)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143)

**오류 메시지:** 기존 관리구역 표식이 손상되었거나 중복되었습니다.


#### LEVEL 2 · [src/notifier.py](src/notifier.py)

| 정의 | 역할 |
| --- | --- |
| [`atomic_json`](src/notifier.py#L32) | 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다. |
| [`source_datetime`](src/notifier.py#L62) | 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다. |
| [`duplicate_record`](src/notifier.py#L184) | 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다. |
| [`settings_record`](src/notifier.py#L195) | 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다. |
| [`lookup_parent_reason`](src/notifier.py#L335) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L382) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L636) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L637) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L17) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L18) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L19) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L20) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L21) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L22) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L23) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L24) | `정의=256` |
| [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25) | `정의=0.2` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L89)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') not in (2, 3)`](src/notifier.py#L93)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L95)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L97)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('settings'), dict)`](src/notifier.py#L116)

**오류 메시지:** 채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`backup.read_bytes() != original`](src/notifier.py#L104)

**오류 메시지:** 이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다.

**거부 조건:** [`any(isinstance(v, bool) or not isinstance(v, int) or v &lt; 0 for v in (offset, end))`](src/notifier.py#L111)

**오류 메시지:** 이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L435)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L500)

**오류 메시지:** 명시 알림 파일 상한 초과


#### LEVEL 2 · [src/theme.py](src/theme.py)

| 정의 | 역할 |
| --- | --- |
| [`MonochromeStyle`](src/theme.py#L46) | 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다. |
| [`KoreanDialogs`](src/theme.py#L71) | 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다. |
| [`DialogLayout`](src/theme.py#L87) | 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다. |

#### LEVEL 2 · [src/usage.py](src/usage.py)

| 정의 | 역할 |
| --- | --- |
| [`number`](src/usage.py#L16) | 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다. |
| [`normalize_limits`](src/usage.py#L35) | 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다. |
| [`discover_codex`](src/usage.py#L69) | 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`MAX_BYTES`](src/usage.py#L12) | `정의=1024 * 1024` |
| [`KST`](src/usage.py#L13) | `정의=timezone(timedelta(hours=9))` |

| 거부 조건 | 오류 메시지 |
| --- | --- |
| [`not isinstance(message, dict)`](src/usage.py#L226) | 객체가 아닌 응답 |

#### LEVEL 2 · [src/visuals.py](src/visuals.py)

| 정의 | 역할 |
| --- | --- |
| [`rotate_point`](src/visuals.py#L8) | X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다. |
| [`orbit_segments`](src/visuals.py#L23) | 세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다. |
| [`draw_orbit`](src/visuals.py#L54) | 장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다. |

</details>

### LEVEL 2 · 관측과 해석을 구분하기

변경 전·후 모델과 추론 강도, 공개된 이유, 관측 시각과 근거 수준을 함께 읽습니다. 기록되지 않은 값은 미확인으로 남깁니다. 로컬 기록은 서버 모델 신원 증명이 아닙니다.

**상황:** 알림이 나타나지 않음

**확인할 내용:** 감시하는 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 확인합니다. 최초 기준선 읽기와 새 변경 감지는 다릅니다.

**상황:** 자산 또는 글꼴 오류

**확인할 내용:** 이 차수에서 참조하는 assets와 라이선스를 준비합니다. 소스 이력에는 과거 대용량 프레임 자산이 없을 수 있습니다.

**상황:** 이유 또는 이전값이 없음

**확인할 내용:** 원문 기록에 해당 필드가 있는지 확인합니다. 누락된 동기를 추정해서 채우지 않습니다.


[자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)



### LEVEL 2 · 8차의 구체적인 기능과 확인

짧은 확인 주기, 중복 판별, 뒤에 도착하는 정보의 보강은 함께 작동합니다. 자주 읽기만 하면 같은 사건을 여러 번 알릴 수 있으므로 중복과 보강을 나누는 것이 중요합니다. 실제 표시 시간에는 파일 생성·읽기·처리·알림 표시가 모두 영향을 줍니다.

**수집·해석·표시·보존**을 연결해 읽습니다. 로컬 JSONL의 관측 변경과 명시된 배정은 다른 종류의 근거입니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다. 별도 usage 모듈의 계정 한도 조회는 App Server 읽기 전용 경로이므로 이 로컬 감시와 구별합니다.

Windows에서 이 차수의 [requirements.txt](requirements.txt)에 맞는 Python 의존성과 해당 자산을 준비한 뒤 **이 차수 폴더에서** `python src/app.py`를 실행합니다. 현재 루트의 assets가 과거 모든 차수와 호환되는 것은 아니며, history 소스만으로 과거 EXE의 화면·자산 전체가 복원되는 것도 아닙니다.

아래 구성·설정·거부 조건은 이 연결이 성립하는 실제 조건입니다. 자료가 처음 기준선으로 읽힌 것인지 새 변경인지, 표시에 필요한 이전값이 존재하는지를 함께 판단합니다.

**이 보관본 의존성 선언**: PySide6-Essentials==6.12.0 · PyInstaller==6.22.3. PySide6는 창을 만드는 도구이고 PyInstaller는 실행 파일을 묶는 도구입니다. 외부 실행 도구·GPU 드라이버는 별도 조건입니다.

**자료 경계와 모듈 연결**

- [src/](src): 관련 파일을 모아 둔 폴더.

- [README.md](README.md#reading-level-2): 설명을 읽는 Markdown 문서.

- [requirements.txt](requirements.txt): 문자로 적은 목록 파일.

- [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json): 항목별 값을 저장한 자료.

- [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md): 설명을 읽는 Markdown 문서.

- [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json): 항목별 값을 저장한 자료.

- [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff): 전후 파일의 달라진 줄을 기록한 비교 자료.

- [src/app.py](src/app.py): 연결 구조에서의 역할은 Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용.

- [src/notifier.py](src/notifier.py): 연결 구조에서의 역할은 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다.

- [src/core.py](src/core.py): 연결 구조에서의 역할은 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용.

- [src/theme.py](src/theme.py): 연결 구조에서의 역할은 앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

- [src/usage.py](src/usage.py): 연결 구조에서의 역할은 Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

- [src/visuals.py](src/visuals.py): 연결 구조에서의 역할은 실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

**실제 입력·설정과 기본값**

- [`--data-dir`](src/app.py#L1108) (src/app.py)

  앱 설정·이력을 저장할 폴더를 고릅니다. 기본은 LOCALAPPDATA 아래 CodexOrbit이며 그 환경값이 없으면 사용자 홈을 기준으로 합니다. 같은 폴더 중복 실행 잠금과 연결됩니다. 원문 선언: `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`.

- [`--sessions`](src/app.py#L1109) (src/app.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path`.

- [`--smoke-test`](src/app.py#L1110) (src/app.py)

  점검 실행을 켜는 스위치입니다. 숫자를 넣는 옵션이 아니라 이름을 붙여 켭니다. 옵션 존재 자체가 검사를 실행해 통과했다는 증거는 아닙니다. 원문 선언: `action='store_true'`.

- [`--usage-smoke-test`](src/app.py#L1111) (src/app.py)

  실제 계정 한도와 표시를 조회한 뒤 종료하는 점검 스위치입니다. 로컬 그림만 확인하는 검사와 달리 계정 연결 조건이 필요하고 비율을 잔여 토큰 개수로 읽지 않습니다. 원문 선언: `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`.

- [`--smoke-report`](src/app.py#L1112) (src/app.py)

  점검 결과를 저장할 파일 경로입니다. 폴더를 고르는 세션 옵션과 달리 보고서 파일을 지정합니다. 원문 선언: `type=Path`.

- [`--show-details`](src/app.py#L1113) (src/app.py)

  처음부터 상세창을 보여 주는 스위치입니다. 숨겨진 원문 값을 새로 만들어 주는 기능이 아닙니다. 원문 선언: `action='store_true'`.

- [`--show-event`](src/app.py#L1114) (src/app.py)

  이미 있는 이력의 사건 ID 또는 대상 ID를 지정해 다시 표시합니다. 실제 저장된 ID와 맞춰 읽고 새 사건 생성과 구분합니다. 원문 선언: `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`.

- [`ROLE_LABELS`](src/app.py#L61) (src/app.py)

  역할 코드와 사용자용 한글 이름의 대응표입니다. 예를 들어 build는 구현, verifier는 독립 검증으로 읽습니다. 화면 설명을 바꾸는 표이며 서버 모델을 바꾸는 설정은 아닙니다. 원문 선언: `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`.

- [`MAX_TEXT_BYTES`](src/core.py#L9) (src/core.py)

  읽거나 적용할 지침 문서의 크기 상한입니다. 원문·추가 지침·최종 결과의 제한과 연결되며 큰 문서 쓰기를 무제한 허용하지 않습니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`BEGIN`](src/core.py#L10) (src/core.py)

  앱이 관리하는 지침 구간이 시작되는 정확한 표시 문자열입니다. 문서의 나머지 부분과 구분하기 때문에 추가할 지침 안에 같은 표식을 넣지 못하게 합니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'`.

- [`END`](src/core.py#L11) (src/core.py)

  앱 관리 구간이 끝나는 정확한 표시 문자열입니다. 시작 표시보다 먼저 있거나 여러 번 있으면 원래 구간이 불명확해 적용을 거부하는 조건과 연결됩니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'`.

- [`--sessions`](src/notifier.py#L636) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L637) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L17) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L18) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L19) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게 하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L20) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록 하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L21) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게 합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L22) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L23) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료량을 제한합니다. 파일 하나의 상한과 별개인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L24) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

- [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25) (src/notifier.py)

  새 기록이 있는지 다시 확인하는 간격이며 단위는 초입니다. 0.2초는 1초의 5분의 1마다 확인하려는 설정이고 실제 알림이 그 시간 안에 반드시 뜬다는 보장은 아닙니다. 선언 숫자는 0.2입니다. 원문 선언: `정의=0.2`.

- [`MAX_BYTES`](src/usage.py#L12) (src/usage.py)

  계정 응답에서 읽을 최대 자료량입니다. 단위는 바이트이며 응답이 너무 클 때 무제한으로 받아들이지 않게 하는 경계입니다. 계산한 값은 1,048,576이며 바이트 제한에서는 1,024 KiB입니다. 원문 선언: `정의=1024 * 1024`.

- [`KST`](src/usage.py#L13) (src/usage.py)

  한국 표준시를 나타냅니다. UTC보다 9시간 빠른 시간대로 날짜·시각을 읽는 기준이며 컴퓨터 지역 시간과 구별합니다. 원문 선언: `정의=timezone(timedelta(hours=9))`.

**처리 책임과 원문에 명시된 함수 동작**

- [`operation_record`](src/app.py#L33) (src/app.py)

  앱 시작과 감시 진행을 조사해야 하는 경우에는 결과가 다음처럼 제한됩니다. 운영 단계를 확인하는 기록이 남습니다 단계 진단에 필요하지 않은 대화 내용까지 복제하지 않기 위해서입니다

- [`short_reason`](src/app.py#L75) (src/app.py)

  변경 알림에서 짧은 이유가 필요한 경우에는 결과가 다음처럼 제한됩니다. 원문에 있는 이유를 읽을 수 있고 없는 이유는 만들어지지 않습니다. 공개된 문장과 앱이 추측한 동기를 혼동하지 않도록 하기 위해서입니다

- [`QuitGuard`](src/app.py#L801) (src/app.py)

  감시가 일하는 도중 사용자가 앱 종료를 누른 경우에는 결과가 다음처럼 제한됩니다. 작업 정리와 창 종료의 순서가 유지됩니다. 아직 실행 중인 감시 작업을 남겨 둔 채 화면만 없애지 않도록 하기 위해서입니다

- [`read_jsonl_tail`](src/core.py#L18) (src/core.py)

  기록 파일의 끝부분만 읽어 첫 줄이나 마지막 줄이 중간에 잘려 들어온 경우에는 결과가 다음처럼 제한됩니다. 온전한 줄만 기록 한 건으로 읽습니다. 문장 안의 다른 줄바꿈 모양 문자나 반쪽 기록을 새 사건으로 잘못 세지 않기 위해서입니다

- [`title_catalog`](src/core.py#L55) (src/core.py)

  같은 작업에 제목 정보가 여러 출처로 남아 있는 경우에는 결과가 다음처럼 제한됩니다. 제목과 그 제목을 얻은 출처를 대조할 수 있습니다. 제목 문자열만 같다는 이유로 근거 수준까지 같다고 보지 않기 위해서입니다

- [`resolve_title`](src/core.py#L73) (src/core.py)

  한 채팅에서 별도 자식 작업이 실행된 기록을 표시하는 경우에는 결과가 다음처럼 제한됩니다. 어느 대화에서 생긴 어떤 작업인지 구별됩니다. 작업명을 새 채팅 제목이나 다른 부모 채팅으로 오해하지 않기 위해서입니다

- [`safe_path`](src/core.py#L97) (src/core.py)

  지침을 적용할 파일이나 그 파일에 이르는 상위 폴더가 다른 곳으로 연결된 경우에는 결과가 다음처럼 제한됩니다. 연결을 통해 의도 밖의 위치를 수정하는 경로는 허용되지 않습니다. 겉으로 고른 폴더와 실제 쓰는 위치가 달라지는 일을 막기 위해서입니다

- [`atomic_json`](src/notifier.py#L32) (src/notifier.py)

  앱 상태를 저장하는 도중 다른 프로그램이 파일을 잠깐 사용하는 경우에는 결과가 다음처럼 제한됩니다. 반쯤 쓴 상태를 원래 파일처럼 노출하지 않도록 저장 경로를 구성합니다. 파일 저장 전체를 무제한 재시도하거나 모든 오류를 정상으로 감추지 않기 위해서입니다

- [`source_datetime`](src/notifier.py#L62) (src/notifier.py)

  사건 순서를 원본 시각으로 비교하는 경우에는 결과가 다음처럼 제한됩니다. 시각이 없으면 새 시각을 추측해 채우지 않습니다. 출처 불명확한 시각으로 사건 순서를 확정하지 않기 위해서입니다

- [`duplicate_record`](src/notifier.py#L184) (src/notifier.py)

  같은 기록이 복사되어 다시 발견된 경우에는 결과가 다음처럼 제한됩니다. 복제 제거와 순서 복원이 서로 다른 처리로 유지됩니다. 시각이 없는 기록을 추측만으로 중복이라 지워 버리지 않기 위해서입니다

- [`settings_record`](src/notifier.py#L195) (src/notifier.py)

  현재 채팅의 앱 자체 설정 기록을 읽는 경우에는 결과가 다음처럼 제한됩니다. 설정값은 읽지만 누가 바꿨는지와 실제 실행 모델은 추정하지 않습니다. 설정 선택과 서버에서 수행한 모델 실행을 같은 증거로 보지 않기 위해서입니다

- [`lookup_parent_reason`](src/notifier.py#L335) (src/notifier.py)

  자식 사건의 배정 이유가 큰 부모 기록에 남아 있는 경우에는 결과가 다음처럼 제한됩니다. 이유를 찾는 보조 읽기가 다음 감시 출발점을 옮기지 않습니다. 부모 이유를 찾다가 새 사건을 건너뛰거나 전체 큰 파일을 무제한 읽지 않기 위해서입니다

- [`enrich_event`](src/notifier.py#L382) (src/notifier.py)

  이력이 이미 전달됐지만 첫 배정 이유가 뒤늦게 확인된 경우에는 결과가 다음처럼 제한됩니다. 같은 사건의 설명이 보강되고 중복 알림은 만들어지지 않습니다. 이유 보강과 새 모델 변경 사건을 구분하기 위해서입니다

- [`MonochromeStyle`](src/theme.py#L46) (src/theme.py)

  앱 안의 파일·메시지 표준 아이콘이 표시되는 경우에는 결과가 다음처럼 제한됩니다. 앱 소유 화면 안의 기호 표현이 정리됩니다. 앱 바깥 운영체제의 아이콘까지 바꾸는 설정으로 확대하지 않도록 범위를 구분해야 합니다

- [`KoreanDialogs`](src/theme.py#L71) (src/theme.py)

  배포 앱에 Qt의 별도 번역 파일이 없는 경우에는 결과가 다음처럼 제한됩니다. 번역 묶음이 없어도 기본 파일 선택 안내를 읽을 수 있습니다. 앱 안내 문구와 사용자가 고르는 파일 이름을 구분하기 위해서입니다

- [`DialogLayout`](src/theme.py#L87) (src/theme.py)

  파일 선택창에 긴 이름과 한글 버튼이 함께 있는 경우에는 결과가 다음처럼 제한됩니다. 이름과 버튼을 구별해서 읽는 배치가 됩니다. 번역 문구를 넣기만 하고 화면 공간은 그대로 두는 문제를 피하기 위해서입니다

- [`number`](src/usage.py#L16) (src/usage.py)

  한도 응답에 숫자 대신 참·거짓, 문자열 또는 무한대 같은 값이 들어온 경우에는 결과가 다음처럼 제한됩니다. 잘못된 입력이 사용 가능한 비율로 표시되지 않습니다. 예를 들어 참을 숫자 1처럼 읽어 정상 비율로 오해하지 않기 위해서입니다

- [`normalize_limits`](src/usage.py#L35) (src/usage.py)

  계정 한도가 기간별 여러 묶음으로 응답한 경우에는 결과가 다음처럼 제한됩니다. 존재하는 기간의 실제 비율만 표시 근거가 됩니다. 없는 주간·단기 한도를 다른 값으로 추정해 채우지 않기 위해서입니다

- [`discover_codex`](src/usage.py#L69) (src/usage.py)

  계정 한도를 읽을 Codex 실행 프로그램을 찾는 경우에는 결과가 다음처럼 제한됩니다. 선택 순서에 맞는 실제 실행 파일이 연결 후보가 됩니다. 동명이름의 문서·폴더를 실행 프로그램으로 잘못 사용하지 않기 위해서입니다

- [`rotate_point`](src/visuals.py#L8) (src/visuals.py)

  입체 점의 방향을 바꾸는 경우에는 결과가 다음처럼 제한됩니다. 평면 위치뿐 아니라 앞뒤를 나타내는 좌표가 유지됩니다. 회전 순서를 바꾸면 같은 각도여도 물체 방향이 달라질 수 있기 때문입니다

- [`orbit_segments`](src/visuals.py#L23) (src/visuals.py)

  구의 중심을 지나는 큰 원 세 개를 화면에 그리는 경우에는 다음 출력 조건이 있습니다. 앞쪽 선이 뒤쪽 선 위에 그려질 순서가 나옵니다 겹침과 깊이감을 화면의 실제 그리기 순서에 연결하기 위해서입니다

- [`draw_orbit`](src/visuals.py#L54) (src/visuals.py)

  입체 관 모양 궤도와 실제 계정 숫자를 합성하는 경우에는 다음 출력 조건이 있습니다. 이 차수의 가림 규칙이 반영된 합성이 나옵니다 후속 차수의 중심 숫자 고정·가림 방지 규칙을 과거 차수에 거꾸로 적용하지 않기 위해서입니다

**멈추거나 거부되는 조건과 읽는 방법**

- [`not lock.tryLock(100)`](src/app.py#L1139) (src/app.py)

  같은 저장 폴더를 이미 다른 Codex Orbit가 쓰거나 잠금 파일에 접근할 수 없으면 시작을 거부합니다. 한 설정·상태 파일을 두 실행이 동시에 바꾸지 않도록 하며, 이 메시지만으로 어느 쪽 원인인지 확정하지 않습니다. 원문 오류: “같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.”입니다.

- [`not isinstance(value, dict)`](src/app.py#L146) (src/app.py)

  앱 설정이 항목 이름과 값을 가진 사전이어야 합니다. 예를 들어 목록만 저장돼 있으면 설정 이름으로 값을 찾을 수 없어 거부합니다. 원문 오류: “앱 설정은 JSON 객체여야 합니다.”입니다.

- [`not path.is_dir()`](src/app.py#L654) (src/app.py)

  선택한 기록 경로가 실제 폴더가 아니면 거부합니다. 오타가 있는 위치나 파일 하나를 감시 폴더로 잘못 지정했는지 먼저 확인합니다. 원문 오류: “존재하는 sessions 폴더를 선택하세요.”입니다.

- [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L659) (src/app.py)

  수동으로 지정한 경로가 실제 .exe 실행 파일이 아니면 거부합니다. 실제 Codex 실행 파일을 고르거나 값을 비워 정해진 자동 탐색을 사용해야 합니다. 원문 오류: “존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.”입니다.

- [`self.plan is None`](src/app.py#L764) (src/app.py)

  아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다. 대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다. 원문 오류: “새 미리보기가 필요합니다.”입니다.

- [`not receipts`](src/app.py#L776) (src/app.py)

  앱이 지침 적용 전에 만든 백업이 없으면 그 백업을 이용한 되돌리기를 할 수 없습니다. 임의의 다른 문서를 원래 내용이라고 추정하지 않습니다. 원문 오류: “앱이 만든 적용 백업이 없습니다.”입니다.

- [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112) (src/core.py)

  지침 원본 문서가 2 MiB보다 크면 읽기 범위를 벗어나 거부합니다. 작은 설명으로 예상한 입력을 대용량 파일 읽기로 확대하지 않는 제한입니다. 원문 오류: “문서가 2 MiB 상한을 초과했습니다.”입니다.

- [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64) (src/core.py)

  보관한 제목 목록이 기대한 이름별 저장 형식이 아니면 거부합니다. 제목의 출처와 연결을 알 수 없는데도 빈 목록으로 자동 덮어쓰지 않습니다. 원문 오류: “제목 캐시 구조가 올바르지 않습니다.”입니다.

- [`target.name.lower() != 'agents.md'`](src/core.py#L123) (src/core.py)

  선택한 파일 이름이 AGENTS.md가 아니면 적용하지 않습니다. 다른 문서나 데이터 파일을 지침 대상이라고 잘못 수정하지 않기 위한 이름 확인입니다. 원문 오류: “적용 대상은 AGENTS.md 파일이어야 합니다.”입니다.

- [`not target.parent.is_dir()`](src/core.py#L125) (src/core.py)

  대상 파일을 둘 상위 폴더가 없으면 적용하지 않습니다. 앱이 의도하지 않은 위치의 폴더를 새로 만들어 결과를 숨기는 대신 선택 경로부터 확인하게 합니다. 원문 오류: “대상 폴더가 존재하지 않습니다.”입니다.

- [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127) (src/core.py)

  기존 대상이 일반 파일이 아니거나 2 MiB보다 크면 적용하지 않습니다. 폴더·특수 파일을 문서처럼 취급하거나 대용량 원본을 바꾸지 않게 합니다. 원문 오류: “대상은 2 MiB 이하의 일반 파일이어야 합니다.”입니다.

- [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134) (src/core.py)

  내용이 공백뿐이거나 새로 붙일 지침이 2 MiB보다 크면 거부합니다. 아무 내용 없는 적용이나 과도한 추가 입력을 정상 변경으로 보지 않습니다. 원문 오류: “빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.”입니다.

- [`BEGIN in added or END in added`](src/core.py#L136) (src/core.py)

  추가 지침 안에 앱의 시작·끝 관리 표시가 들어 있으면 거부합니다. 내용 속 표시를 실제 관리 경계로 잘못 읽어 원문 구간을 혼동하지 않도록 합니다. 원문 오류: “지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.”입니다.

- [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150) (src/core.py)

  원본과 새 지침을 합친 최종 문서가 2 MiB보다 크면 쓰지 않습니다. 원본과 추가분이 각각 작더라도 합쳐진 결과는 별도 크기 제한을 만족해야 합니다. 원문 오류: “적용 결과가 2 MiB 상한을 초과합니다.”입니다.

- [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157) (src/core.py)

  아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다. 대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다. 원문 오류: “대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.”입니다.

- [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177) (src/core.py)

  미리보기 계획 안의 원문·결과 바이트가 저장된 지문과 다르면 거부합니다. 사용자가 확인했던 변경 계획과 실제 쓸 내용이 같은지 확인하는 경계입니다. 원문 오류: “미리보기 데이터가 변경되었습니다.”입니다.

- [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197) (src/core.py)

  백업이 앱이 정한 백업 폴더 안의 정상 파일이 아니거나 크기 제한을 넘으면 복원에 쓰지 않습니다. 아무 파일이나 원래 문서라고 덮어쓰지 않기 위한 확인입니다. 원문 오류: “유효한 앱 원문 백업이 아닙니다.”입니다.

- [`digest(raw) != receipt['before_hash']`](src/core.py#L200) (src/core.py)

  백업 내용의 지문이 적용 때 기록한 원본 지문과 다르면 되돌리기를 거부합니다. 파일 이름이 같더라도 내용이 달라졌다면 안전한 원본으로 보지 않습니다. 원문 오류: “백업 해시가 일치하지 않습니다.”입니다.

- [`not isinstance(row, dict)`](src/core.py#L40) (src/core.py)

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다. 원문 오류: “JSON 객체가 아닙니다.”입니다.

- [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143) (src/core.py)

  시작·끝 표시가 정확히 한 쌍이 아니거나 순서가 뒤집혔다면 적용할 구간이 불명확해 거부합니다. 여러 구간 중 임의의 하나를 골라 원문을 바꾸지 않습니다. 원문 오류: “기존 관리구역 표식이 손상되었거나 중복되었습니다.”입니다.

- [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L89) (src/notifier.py)

  이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다. 큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다. 원문 오류: “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”입니다.

- [`self.state.get('schema_version') not in (2, 3)`](src/notifier.py#L93) (src/notifier.py)

  옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다. 이를 새 관측 이력으로 자동 해석하지 않습니다. 명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다. 원문 오류: “구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.”입니다.

- [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L95) (src/notifier.py)

  저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다. 자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다. 원문 오류: “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”입니다.

- [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L97) (src/notifier.py)

  어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다. 이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다. 원문 오류: “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”입니다.

- [`not isinstance(self.state.get('settings'), dict)`](src/notifier.py#L116) (src/notifier.py)

  채팅별 선택 설정 항목이 기대한 사전 형태가 아니면 저장 상태를 거부합니다. 설정 요청을 실제 관측 변경으로 잘못 바꾸는 자동 초기화를 하지 않습니다. 원문 오류: “채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”입니다.

- [`backup.read_bytes() != original`](src/notifier.py#L104) (src/notifier.py)

  활동 상태 형식을 옮기기 전의 백업 내용이 원본과 다르면 덮어쓰지 않습니다. 이행은 저장 형식을 바꾸는 과정이며 다른 원본을 같은 자료처럼 취급하지 않습니다. 원문 오류: “이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다.”입니다.

- [`any(isinstance(v, bool) or not isinstance(v, int) or v &lt; 0 for v in (offset, end))`](src/notifier.py#L111) (src/notifier.py)

  이전 기록에서 읽어 둔 시작·끝 위치가 참·거짓, 정수가 아닌 값 또는 음수라면 거부합니다. 파일의 몇 번째 바이트부터 읽을지를 알 수 없으므로 0으로 임의 초기화하지 않습니다. 원문 오류: “이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다.”입니다.

- [`not isinstance(record, dict)`](src/notifier.py#L435) (src/notifier.py)

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다. 원문 오류: “JSON 객체가 아닙니다.”입니다.

- [`path.stat().st_size &gt; 20000`](src/notifier.py#L500) (src/notifier.py)

  명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다. 짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게 하기 위한 크기 제한입니다. 원문 오류: “명시 알림 파일 상한 초과”입니다.

- [`not isinstance(message, dict)`](src/usage.py#L226) (src/usage.py)

  계정 서버의 응답이 이름별 값을 가진 객체가 아니면 한도 자료로 읽지 않습니다. 숫자·문자열만 온 응답에서 비율을 임의로 만들지 않습니다. 원문 오류: “객체가 아닌 응답”입니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다. 최초 기준선 읽기와 새 변경은 다릅니다. 자산·글꼴 오류라면 이 차수 assets와 라이선스를 대조합니다. 과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다. 이유·이전값이 없으면 원문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

7차 → 8차의 실제 파일 비교입니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **수정** [src/app.py](src/app.py): 전체 비교에서 기능 연결의 실제 변경을 확인합니다.

- **수정** [src/notifier.py](src/notifier.py): 전체 비교에서 기능 연결의 실제 변경을 확인합니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다. 원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다. 이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다. Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


**이 수준에서 연결·실행·설계를 대조하는 순서**

선언의 정확한 코드와 전체 역할 원문은 LEVEL 5 및 연결된 소스에 보존합니다. 입력 사례는 검토 방법을 설명하며 실제 실행 결과가 아닙니다. 옵션 지정·기본값과 정상·거부 사례를 구분하고, 변경 시 호출자·공유 상태·표시 조건에 미치는 영향을 대조합니다.

- [src/app.py](src/app.py): 사용자 동작과 감시 상태가 UI에서 만납니다. 이전·현재 표시, 알림 수명, 원문 접근, 감시 종료의 순서가 서로 연결되지만 같은 상태값은 아닙니다.

- [src/core.py](src/core.py): 로컬 기록·제목 입력은 이력과 알림의 근거가 되고, 문서 적용 입력은 미리보기·원본 대조를 거쳐 쓰기로 연결됩니다. 읽기와 쓰기의 경계를 구분해야 합니다.

- [src/notifier.py](src/notifier.py): 순차 감시의 읽기 위치, 복제 판별, 부모 이유 보조 조회가 연결됩니다. 뒤늦은 보강이 새 알림·새 모델 변경으로 바뀌지 않는 점이 중요합니다.

- [src/theme.py](src/theme.py): 앱의 공통 스타일이 메뉴·표준 아이콘·대화상자의 표시로 이어집니다. 번역·배치·색의 책임은 구분합니다.

- [src/usage.py](src/usage.py): 한도 값은 로컬 세션 감시와 다른 읽기 입력입니다. 실행 파일 탐색→App Server 응답→기간별 한도 묶음→화면 비율로 연결됩니다.

- [src/visuals.py](src/visuals.py): 입체·그림 자산과 실제 상태·한도·이름이 합성 단계에서 만납니다. 좌표·회전은 물체 표현이며 숫자 라벨과 실제 비율은 데이터 표현입니다.

<a id="reading-level-3"></a>
## LEVEL 3 - Practitioner

### LEVEL 3 · 이 차수를 준비하는 범위

감시 폴링 간격을 0.2초 상수로 두고 중복 기록 감지와 이벤트 보강·읽기 경로를 바꿉니다. 빠른 폴링 설정이 모든 부하에서 즉시 알림을 보장하지는 않습니다.

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다.

자산과 의존성을 준비한 이 차수 폴더에서 `python src/app.py`를 실행합니다. history 소스만으로 과거 배포 EXE와 동일한 화면·자산이 모두 복원되지는 않습니다.

#### LEVEL 3 · 이 보관본의 의존성 목록

[requirements.txt](requirements.txt)의 실제 항목입니다. 외부 실행 도구와 GPU 드라이버는 별도로 준비합니다.

```text
PySide6-Essentials==6.12.0
PyInstaller==6.22.3
```

#### LEVEL 3 · 소스에서 제공하는 CLI 옵션

**진입 소스:** [app.py](src/app.py)

**정의된 옵션 이름:** `--data-dir`, `--sessions`, `--smoke-test`, `--usage-smoke-test`, `--smoke-report`, `--show-details`, `--show-event`

**진입 소스:** [notifier.py](src/notifier.py)

**정의된 옵션 이름:** `--sessions`, `--work`


각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 3 · [src/app.py](src/app.py)

| 정의 | 역할 |
| --- | --- |
| [`operation_record`](src/app.py#L33) | 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다. |
| [`short_reason`](src/app.py#L75) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |
| [`QuitGuard`](src/app.py#L801) | 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L1108)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L1109)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L1110)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--usage-smoke-test`](src/app.py#L1111)

**코드의 선언:** `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`

**설정·옵션:** [`--smoke-report`](src/app.py#L1112)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L1113)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L1114)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L61)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


**거부 조건:** [`not lock.tryLock(100)`](src/app.py#L1139)

**오류 메시지:** 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

**거부 조건:** [`not isinstance(value, dict)`](src/app.py#L146)

**오류 메시지:** 앱 설정은 JSON 객체여야 합니다.

**거부 조건:** [`not path.is_dir()`](src/app.py#L654)

**오류 메시지:** 존재하는 sessions 폴더를 선택하세요.

**거부 조건:** [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L659)

**오류 메시지:** 존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.

**거부 조건:** [`self.plan is None`](src/app.py#L764)

**오류 메시지:** 새 미리보기가 필요합니다.

**거부 조건:** [`not receipts`](src/app.py#L776)

**오류 메시지:** 앱이 만든 적용 백업이 없습니다.


#### LEVEL 3 · [src/core.py](src/core.py)

| 정의 | 역할 |
| --- | --- |
| [`read_jsonl_tail`](src/core.py#L18) | 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| [`title_catalog`](src/core.py#L55) | 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| [`resolve_title`](src/core.py#L73) | 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| [`safe_path`](src/core.py#L97) | 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`MAX_TEXT_BYTES`](src/core.py#L9) | `정의=2 * 1024 * 1024` |
| [`BEGIN`](src/core.py#L10) | `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| [`END`](src/core.py#L11) | `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

**거부 조건:** [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112)

**오류 메시지:** 문서가 2 MiB 상한을 초과했습니다.

**거부 조건:** [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64)

**오류 메시지:** 제목 캐시 구조가 올바르지 않습니다.

**거부 조건:** [`target.name.lower() != 'agents.md'`](src/core.py#L123)

**오류 메시지:** 적용 대상은 AGENTS.md 파일이어야 합니다.

**거부 조건:** [`not target.parent.is_dir()`](src/core.py#L125)

**오류 메시지:** 대상 폴더가 존재하지 않습니다.

**거부 조건:** [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127)

**오류 메시지:** 대상은 2 MiB 이하의 일반 파일이어야 합니다.

**거부 조건:** [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134)

**오류 메시지:** 빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.

**거부 조건:** [`BEGIN in added or END in added`](src/core.py#L136)

**오류 메시지:** 지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.

**거부 조건:** [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150)

**오류 메시지:** 적용 결과가 2 MiB 상한을 초과합니다.

**거부 조건:** [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157)

**오류 메시지:** 대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.

**거부 조건:** [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177)

**오류 메시지:** 미리보기 데이터가 변경되었습니다.

**거부 조건:** [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197)

**오류 메시지:** 유효한 앱 원문 백업이 아닙니다.

**거부 조건:** [`digest(raw) != receipt['before_hash']`](src/core.py#L200)

**오류 메시지:** 백업 해시가 일치하지 않습니다.

**거부 조건:** [`not isinstance(row, dict)`](src/core.py#L40)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143)

**오류 메시지:** 기존 관리구역 표식이 손상되었거나 중복되었습니다.


#### LEVEL 3 · [src/notifier.py](src/notifier.py)

| 정의 | 역할 |
| --- | --- |
| [`atomic_json`](src/notifier.py#L32) | 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다. |
| [`source_datetime`](src/notifier.py#L62) | 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다. |
| [`duplicate_record`](src/notifier.py#L184) | 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다. |
| [`settings_record`](src/notifier.py#L195) | 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다. |
| [`lookup_parent_reason`](src/notifier.py#L335) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L382) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L636) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L637) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L17) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L18) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L19) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L20) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L21) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L22) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L23) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L24) | `정의=256` |
| [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25) | `정의=0.2` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L89)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') not in (2, 3)`](src/notifier.py#L93)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L95)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L97)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('settings'), dict)`](src/notifier.py#L116)

**오류 메시지:** 채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`backup.read_bytes() != original`](src/notifier.py#L104)

**오류 메시지:** 이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다.

**거부 조건:** [`any(isinstance(v, bool) or not isinstance(v, int) or v &lt; 0 for v in (offset, end))`](src/notifier.py#L111)

**오류 메시지:** 이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L435)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L500)

**오류 메시지:** 명시 알림 파일 상한 초과


#### LEVEL 3 · [src/theme.py](src/theme.py)

| 정의 | 역할 |
| --- | --- |
| [`MonochromeStyle`](src/theme.py#L46) | 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다. |
| [`KoreanDialogs`](src/theme.py#L71) | 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다. |
| [`DialogLayout`](src/theme.py#L87) | 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다. |

#### LEVEL 3 · [src/usage.py](src/usage.py)

| 정의 | 역할 |
| --- | --- |
| [`number`](src/usage.py#L16) | 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다. |
| [`normalize_limits`](src/usage.py#L35) | 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다. |
| [`discover_codex`](src/usage.py#L69) | 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`MAX_BYTES`](src/usage.py#L12) | `정의=1024 * 1024` |
| [`KST`](src/usage.py#L13) | `정의=timezone(timedelta(hours=9))` |

| 거부 조건 | 오류 메시지 |
| --- | --- |
| [`not isinstance(message, dict)`](src/usage.py#L226) | 객체가 아닌 응답 |

#### LEVEL 3 · [src/visuals.py](src/visuals.py)

| 정의 | 역할 |
| --- | --- |
| [`rotate_point`](src/visuals.py#L8) | X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다. |
| [`orbit_segments`](src/visuals.py#L23) | 세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다. |
| [`draw_orbit`](src/visuals.py#L54) | 장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다. |

</details>

### LEVEL 3 · 실제 사용·실험 순서

1. 이 차수의 소스·requirements와 필요한 자산을 한 작업 폴더에 준비합니다.
2. 앱을 열고 위젯·상세창에서 감시 경로와 표시되는 기록을 확인합니다.
3. 새 변경이 기록되면 이전·이후 값과 이유를 비교하고, 기록 종류와 근거 수준을 함께 읽습니다.
4. 설정·이력은 개인 운영자료로 관리하고 다른 사용자에게 공유하기 전에 내용을 확인합니다.

| 단계 | 내용 |
| --- | --- |
| 입력 | 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정 |
| 처리 | 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시 |
| 출력 | 알림·변경 이력·로컬 진단 기록 |


### LEVEL 3 · 결과와 실패를 확인하기

변경 전·후 모델과 추론 강도, 공개된 이유, 관측 시각과 근거 수준을 함께 읽습니다. 기록되지 않은 값은 미확인으로 남깁니다. 로컬 기록은 서버 모델 신원 증명이 아닙니다.

**상황:** 알림이 나타나지 않음

**확인할 내용:** 감시하는 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 확인합니다. 최초 기준선 읽기와 새 변경 감지는 다릅니다.

**상황:** 자산 또는 글꼴 오류

**확인할 내용:** 이 차수에서 참조하는 assets와 라이선스를 준비합니다. 소스 이력에는 과거 대용량 프레임 자산이 없을 수 있습니다.

**상황:** 이유 또는 이전값이 없음

**확인할 내용:** 원문 기록에 해당 필드가 있는지 확인합니다. 누락된 동기를 추정해서 채우지 않습니다.


### LEVEL 3 · 실행 전 대조할 차수 조건

감시 폴링 간격을 0.2초 상수로 두고 중복 기록 감지와 이벤트 보강·읽기 경로를 바꿉니다. 빠른 폴링 설정이 모든 부하에서 즉시 알림을 보장하지는 않습니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

Codex App Server의 `account/rateLimits/read`를 읽기 전용으로 조회합니다. 표시값은 남은 토큰 개수가 아니라 계정 사용 한도 비율입니다.

[자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)



### LEVEL 3 · 8차의 구체적인 기능과 확인

0.2초 상수와 해당 app.py·notifier.py 변경을 확인합니다. 새 사건과 같은 사건의 보강이 이력에서 어떻게 보이는지 비교하고, 알림 지연은 감시 경로·새 기록 생성 여부·앱 상태를 나눠 확인합니다. 주기 값만 보고 실제 지연 측정을 끝내지 않습니다.

Windows에서 이 차수의 [requirements.txt](requirements.txt)에 맞는 Python 의존성과 해당 자산을 준비한 뒤 **이 차수 폴더에서** `python src/app.py`를 실행합니다. 현재 루트의 assets가 과거 모든 차수와 호환되는 것은 아니며, history 소스만으로 과거 EXE의 화면·자산 전체가 복원되는 것도 아닙니다.

입력은 현재 사용자의 sessions JSONL과 앱 설정입니다. **경로·자산·설정 먼저 확인한 뒤 실행**하고, 알림·변경 이력·로컬 진단을 원본 사건과 대조합니다. 동작 확인에서 모델 전후·추론 전후·이유·시각·근거 수준을 함께 읽고 미기록은 미확인으로 남깁니다.

아래 옵션은 실제 소스에 선언된 이름입니다. CLI는 명령 뒤에 옵션을 붙이는 방식이며 각 기본값·부작용은 해당 선언과 함께 확인합니다. smoke라는 이름은 점검용 실행을 뜻하며 이 문서가 그 실행을 대신 수행했다는 뜻은 아닙니다.

**이 보관본 의존성 선언**: PySide6-Essentials==6.12.0 · PyInstaller==6.22.3. PySide6는 창을 만드는 도구이고 PyInstaller는 실행 파일을 묶는 도구입니다. 외부 실행 도구·GPU 드라이버는 별도 조건입니다.

**자료를 찾는 순서**

- [src/](src): 관련 파일을 모아 둔 폴더.

- [README.md](README.md#reading-level-3): 설명을 읽는 Markdown 문서.

- [requirements.txt](requirements.txt): 문자로 적은 목록 파일.

- [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json): 항목별 값을 저장한 자료.

- [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md): 설명을 읽는 Markdown 문서.

- [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json): 항목별 값을 저장한 자료.

- [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff): 전후 파일의 달라진 줄을 기록한 비교 자료.

- [src/app.py](src/app.py): 실행 자료를 점검할 때 확인할 책임은 Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용.

- [src/notifier.py](src/notifier.py): 실행 자료를 점검할 때 확인할 책임은 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다.

- [src/core.py](src/core.py): 실행 자료를 점검할 때 확인할 책임은 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용.

- [src/theme.py](src/theme.py): 실행 자료를 점검할 때 확인할 책임은 앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

- [src/usage.py](src/usage.py): 실행 자료를 점검할 때 확인할 책임은 Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

- [src/visuals.py](src/visuals.py): 실행 자료를 점검할 때 확인할 책임은 실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

**실제 입력·설정과 기본값**

- [`--data-dir`](src/app.py#L1108) (src/app.py)

  앱 설정·이력을 저장할 폴더를 고릅니다. 기본은 LOCALAPPDATA 아래 CodexOrbit이며 그 환경값이 없으면 사용자 홈을 기준으로 합니다. 같은 폴더 중복 실행 잠금과 연결됩니다. 원문 선언: `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`.

- [`--sessions`](src/app.py#L1109) (src/app.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path`.

- [`--smoke-test`](src/app.py#L1110) (src/app.py)

  점검 실행을 켜는 스위치입니다. 숫자를 넣는 옵션이 아니라 이름을 붙여 켭니다. 옵션 존재 자체가 검사를 실행해 통과했다는 증거는 아닙니다. 원문 선언: `action='store_true'`.

- [`--usage-smoke-test`](src/app.py#L1111) (src/app.py)

  실제 계정 한도와 표시를 조회한 뒤 종료하는 점검 스위치입니다. 로컬 그림만 확인하는 검사와 달리 계정 연결 조건이 필요하고 비율을 잔여 토큰 개수로 읽지 않습니다. 원문 선언: `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`.

- [`--smoke-report`](src/app.py#L1112) (src/app.py)

  점검 결과를 저장할 파일 경로입니다. 폴더를 고르는 세션 옵션과 달리 보고서 파일을 지정합니다. 원문 선언: `type=Path`.

- [`--show-details`](src/app.py#L1113) (src/app.py)

  처음부터 상세창을 보여 주는 스위치입니다. 숨겨진 원문 값을 새로 만들어 주는 기능이 아닙니다. 원문 선언: `action='store_true'`.

- [`--show-event`](src/app.py#L1114) (src/app.py)

  이미 있는 이력의 사건 ID 또는 대상 ID를 지정해 다시 표시합니다. 실제 저장된 ID와 맞춰 읽고 새 사건 생성과 구분합니다. 원문 선언: `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`.

- [`ROLE_LABELS`](src/app.py#L61) (src/app.py)

  역할 코드와 사용자용 한글 이름의 대응표입니다. 예를 들어 build는 구현, verifier는 독립 검증으로 읽습니다. 화면 설명을 바꾸는 표이며 서버 모델을 바꾸는 설정은 아닙니다. 원문 선언: `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`.

- [`MAX_TEXT_BYTES`](src/core.py#L9) (src/core.py)

  읽거나 적용할 지침 문서의 크기 상한입니다. 원문·추가 지침·최종 결과의 제한과 연결되며 큰 문서 쓰기를 무제한 허용하지 않습니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`BEGIN`](src/core.py#L10) (src/core.py)

  앱이 관리하는 지침 구간이 시작되는 정확한 표시 문자열입니다. 문서의 나머지 부분과 구분하기 때문에 추가할 지침 안에 같은 표식을 넣지 못하게 합니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'`.

- [`END`](src/core.py#L11) (src/core.py)

  앱 관리 구간이 끝나는 정확한 표시 문자열입니다. 시작 표시보다 먼저 있거나 여러 번 있으면 원래 구간이 불명확해 적용을 거부하는 조건과 연결됩니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'`.

- [`--sessions`](src/notifier.py#L636) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L637) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L17) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L18) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L19) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게 하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L20) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록 하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L21) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게 합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L22) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L23) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료량을 제한합니다. 파일 하나의 상한과 별개인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L24) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

- [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25) (src/notifier.py)

  새 기록이 있는지 다시 확인하는 간격이며 단위는 초입니다. 0.2초는 1초의 5분의 1마다 확인하려는 설정이고 실제 알림이 그 시간 안에 반드시 뜬다는 보장은 아닙니다. 선언 숫자는 0.2입니다. 원문 선언: `정의=0.2`.

- [`MAX_BYTES`](src/usage.py#L12) (src/usage.py)

  계정 응답에서 읽을 최대 자료량입니다. 단위는 바이트이며 응답이 너무 클 때 무제한으로 받아들이지 않게 하는 경계입니다. 계산한 값은 1,048,576이며 바이트 제한에서는 1,024 KiB입니다. 원문 선언: `정의=1024 * 1024`.

- [`KST`](src/usage.py#L13) (src/usage.py)

  한국 표준시를 나타냅니다. UTC보다 9시간 빠른 시간대로 날짜·시각을 읽는 기준이며 컴퓨터 지역 시간과 구별합니다. 원문 선언: `정의=timezone(timedelta(hours=9))`.

**처리 책임과 원문에 명시된 함수 동작**

- [`operation_record`](src/app.py#L33) (src/app.py)

  확인할 입력 사례: 앱 시작과 감시 진행을 조사해야 하는 경우. 원문에서 확인할 처리: 대화 본문을 넣지 않고 진행 단계와 실제 실행 중인 프로그램의 위치를 기록합니다. 결과 판독 기준: 운영 단계를 확인하는 기록이 남습니다

- [`short_reason`](src/app.py#L75) (src/app.py)

  확인할 입력 사례: 변경 알림에서 짧은 이유가 필요한 경우. 원문에서 확인할 처리: 기록에 명시된 이유 또는 배정·선택 목적 문장을 우선 골라 짧게 보여 줍니다 결과 판독 기준: 원문에 있는 이유를 읽을 수 있고 없는 이유는 만들어지지 않습니다

- [`QuitGuard`](src/app.py#L801) (src/app.py)

  확인할 입력 사례: 감시가 일하는 도중 사용자가 앱 종료를 누른 경우. 원문에서 확인할 처리: 종료 요청을 곧바로 끝내지 않고 감시 작업자가 따로 정리 작업을 마친 뒤 종료를 처리합니다. 결과 판독 기준: 작업 정리와 창 종료의 순서가 유지됩니다

- [`read_jsonl_tail`](src/core.py#L18) (src/core.py)

  확인할 입력 사례: 기록 파일의 끝부분만 읽어 첫 줄이나 마지막 줄이 중간에 잘려 들어온 경우. 원문에서 확인할 처리: 파일에서 실제 줄바꿈을 뜻하는 LF 바이트로만 한 건씩 나누고 완성되지 않은 양끝 조각은 해석하지 않습니다. 결과 판독 기준: 온전한 줄만 기록 한 건으로 읽습니다

- [`title_catalog`](src/core.py#L55) (src/core.py)

  확인할 입력 사례: 같은 작업에 제목 정보가 여러 출처로 남아 있는 경우. 원문에서 확인할 처리: 공식 앱에서 확인해 저장한 제목과 컴퓨터 안의 제목 목록이 어디서 왔는지 함께 보존합니다. 결과 판독 기준: 제목과 그 제목을 얻은 출처를 대조할 수 있습니다

- [`resolve_title`](src/core.py#L73) (src/core.py)

  확인할 입력 사례: 한 채팅에서 별도 자식 작업이 실행된 기록을 표시하는 경우. 원문에서 확인할 처리: 실제 부모 채팅 제목과 자식 작업명을 서로 다른 정보로 다룹니다 결과 판독 기준: 어느 대화에서 생긴 어떤 작업인지 구별됩니다

- [`safe_path`](src/core.py#L97) (src/core.py)

  확인할 입력 사례: 지침을 적용할 파일이나 그 파일에 이르는 상위 폴더가 다른 곳으로 연결된 경우. 원문에서 확인할 처리: 파일 자체뿐 아니라 이미 존재하는 상위 폴더까지 확인해 바로가기처럼 다른 위치로 보내는 링크·재분석 지점을 거부합니다. 결과 판독 기준: 연결을 통해 의도 밖의 위치를 수정하는 경로는 허용되지 않습니다

- [`atomic_json`](src/notifier.py#L32) (src/notifier.py)

  확인할 입력 사례: 앱 상태를 저장하는 도중 다른 프로그램이 파일을 잠깐 사용하는 경우. 원문에서 확인할 처리: 같은 폴더에 따로 임시 파일을 완성한 뒤 교체하고 Windows의 짧은 파일 공유 충돌만 다시 시도합니다. 결과 판독 기준: 반쯤 쓴 상태를 원래 파일처럼 노출하지 않도록 저장 경로를 구성합니다

- [`source_datetime`](src/notifier.py#L62) (src/notifier.py)

  확인할 입력 사례: 사건 순서를 원본 시각으로 비교하는 경우. 원문에서 확인할 처리: 어느 시간대인지 포함한 올바른 원본 시각만 비교에 사용합니다. 결과 판독 기준: 시각이 없으면 새 시각을 추측해 채우지 않습니다

- [`duplicate_record`](src/notifier.py#L184) (src/notifier.py)

  확인할 입력 사례: 같은 기록이 복사되어 다시 발견된 경우. 원문에서 확인할 처리: 원본 시각이 있는 복제만 중복으로 제외하고 과거 기준선을 다시 읽을 때의 순서는 복원합니다. 결과 판독 기준: 복제 제거와 순서 복원이 서로 다른 처리로 유지됩니다

- [`settings_record`](src/notifier.py#L195) (src/notifier.py)

  확인할 입력 사례: 현재 채팅의 앱 자체 설정 기록을 읽는 경우. 원문에서 확인할 처리: 그 채팅에 실제로 저장된 native 설정 항목만 관측합니다. 결과 판독 기준: 설정값은 읽지만 누가 바꿨는지와 실제 실행 모델은 추정하지 않습니다

- [`lookup_parent_reason`](src/notifier.py#L335) (src/notifier.py)

  확인할 입력 사례: 자식 사건의 배정 이유가 큰 부모 기록에 남아 있는 경우. 원문에서 확인할 처리: 부모 기록의 최근 공개 호출만 정해진 양 안에서 찾아보고 정기 감시의 읽기 위치는 그대로 둡니다 결과 판독 기준: 이유를 찾는 보조 읽기가 다음 감시 출발점을 옮기지 않습니다

- [`enrich_event`](src/notifier.py#L382) (src/notifier.py)

  확인할 입력 사례: 이력이 이미 전달됐지만 첫 배정 이유가 뒤늦게 확인된 경우. 원문에서 확인할 처리: 정확히 연결된 사건의 첫 배정 이유만 기존 이력에 덧붙이고 새 알림은 띄우지 않습니다. 결과 판독 기준: 같은 사건의 설명이 보강되고 중복 알림은 만들어지지 않습니다

- [`MonochromeStyle`](src/theme.py#L46) (src/theme.py)

  확인할 입력 사례: 앱 안의 파일·메시지 표준 아이콘이 표시되는 경우. 원문에서 확인할 처리: 운영체제 기본 기호도 앱 안에서는 색이 없는 표현으로 맞춥니다 결과 판독 기준: 앱 소유 화면 안의 기호 표현이 정리됩니다

- [`KoreanDialogs`](src/theme.py#L71) (src/theme.py)

  확인할 입력 사례: 배포 앱에 Qt의 별도 번역 파일이 없는 경우. 원문에서 확인할 처리: 기본 파일 선택창의 정해진 문구를 한국어로 제공합니다. 결과 판독 기준: 번역 묶음이 없어도 기본 파일 선택 안내를 읽을 수 있습니다

- [`DialogLayout`](src/theme.py#L87) (src/theme.py)

  확인할 입력 사례: 파일 선택창에 긴 이름과 한글 버튼이 함께 있는 경우. 원문에서 확인할 처리: 파일 이름 열과 한글 버튼에 필요한 표시 공간을 확보합니다. 결과 판독 기준: 이름과 버튼을 구별해서 읽는 배치가 됩니다

- [`number`](src/usage.py#L16) (src/usage.py)

  확인할 입력 사례: 한도 응답에 숫자 대신 참·거짓, 문자열 또는 무한대 같은 값이 들어온 경우. 원문에서 확인할 처리: 그 값을 올바른 한도 숫자로 받아들이지 않습니다. 결과 판독 기준: 잘못된 입력이 사용 가능한 비율로 표시되지 않습니다

- [`normalize_limits`](src/usage.py#L35) (src/usage.py)

  확인할 입력 사례: 계정 한도가 기간별 여러 묶음으로 응답한 경우. 원문에서 확인할 처리: 공식 응답의 여러 한도 묶음을 우선 읽고 빠진 기간이나 수치를 덧만들지 않습니다. 결과 판독 기준: 존재하는 기간의 실제 비율만 표시 근거가 됩니다

- [`discover_codex`](src/usage.py#L69) (src/usage.py)

  확인할 입력 사례: 계정 한도를 읽을 Codex 실행 프로그램을 찾는 경우. 원문에서 확인할 처리: 사용자가 고른 위치, 명령 검색 경로 PATH, 공식 데스크톱 앱 묶음 위치 순서로 실행 파일 EXE만 찾습니다 결과 판독 기준: 선택 순서에 맞는 실제 실행 파일이 연결 후보가 됩니다

- [`rotate_point`](src/visuals.py#L8) (src/visuals.py)

  확인할 입력 사례: 입체 점의 방향을 바꾸는 경우. 원문에서 확인할 처리: 가로 X축·세로 Y축·깊이 Z축 순서로 회전시키고 깊이값도 남깁니다. 결과 판독 기준: 평면 위치뿐 아니라 앞뒤를 나타내는 좌표가 유지됩니다

- [`orbit_segments`](src/visuals.py#L23) (src/visuals.py)

  확인할 입력 사례: 구의 중심을 지나는 큰 원 세 개를 화면에 그리는 경우.처리 대조 지점: 원들을 작은 선 조각으로 나누고 먼 곳은 작게 보이는 원근 계산으로 옮긴 뒤 뒤쪽부터 정렬합니다. 결과 판독 기준: 앞쪽 선이 뒤쪽 선 위에 그려질 순서가 나옵니다

- [`draw_orbit`](src/visuals.py#L54) (src/visuals.py)

  확인할 입력 사례: 입체 관 모양 궤도와 실제 계정 숫자를 합성하는 경우.처리 대조 지점: 움직이는 장식과 실제 숫자를 별도로 다루고 원문에 정한 앞쪽 관이 중심을 가리는 순서로 그립니다 결과 판독 기준: 이 차수의 가림 규칙이 반영된 합성이 나옵니다

**멈추거나 거부되는 조건과 읽는 방법**

- 오류 “같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.”

  입력 사례와 확인 순서: 같은 저장 폴더를 이미 다른 Codex Orbit가 쓰거나 잠금 파일에 접근할 수 없으면 시작을 거부합니다. 한 설정·상태 파일을 두 실행이 동시에 바꾸지 않도록 하며, 이 메시지만으로 어느 쪽 원인인지 확정하지 않습니다. 원문 조건 [`not lock.tryLock(100)`](src/app.py#L1139) (src/app.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “앱 설정은 JSON 객체여야 합니다.”

  입력 사례와 확인 순서: 앱 설정이 항목 이름과 값을 가진 사전이어야 합니다. 예를 들어 목록만 저장돼 있으면 설정 이름으로 값을 찾을 수 없어 거부합니다. 원문 조건 [`not isinstance(value, dict)`](src/app.py#L146) (src/app.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “존재하는 sessions 폴더를 선택하세요.”

  입력 사례와 확인 순서: 선택한 기록 경로가 실제 폴더가 아니면 거부합니다. 오타가 있는 위치나 파일 하나를 감시 폴더로 잘못 지정했는지 먼저 확인합니다. 원문 조건 [`not path.is_dir()`](src/app.py#L654) (src/app.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.”

  입력 사례와 확인 순서: 수동으로 지정한 경로가 실제 .exe 실행 파일이 아니면 거부합니다. 실제 Codex 실행 파일을 고르거나 값을 비워 정해진 자동 탐색을 사용해야 합니다. 원문 조건 [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L659) (src/app.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “새 미리보기가 필요합니다.”

  입력 사례와 확인 순서: 아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다. 대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다. 원문 조건 [`self.plan is None`](src/app.py#L764) (src/app.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “앱이 만든 적용 백업이 없습니다.”

  입력 사례와 확인 순서: 앱이 지침 적용 전에 만든 백업이 없으면 그 백업을 이용한 되돌리기를 할 수 없습니다. 임의의 다른 문서를 원래 내용이라고 추정하지 않습니다. 원문 조건 [`not receipts`](src/app.py#L776) (src/app.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “문서가 2 MiB 상한을 초과했습니다.”

  입력 사례와 확인 순서: 지침 원본 문서가 2 MiB보다 크면 읽기 범위를 벗어나 거부합니다. 작은 설명으로 예상한 입력을 대용량 파일 읽기로 확대하지 않는 제한입니다. 원문 조건 [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “제목 캐시 구조가 올바르지 않습니다.”

  입력 사례와 확인 순서: 보관한 제목 목록이 기대한 이름별 저장 형식이 아니면 거부합니다. 제목의 출처와 연결을 알 수 없는데도 빈 목록으로 자동 덮어쓰지 않습니다. 원문 조건 [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “적용 대상은 AGENTS.md 파일이어야 합니다.”

  입력 사례와 확인 순서: 선택한 파일 이름이 AGENTS.md가 아니면 적용하지 않습니다. 다른 문서나 데이터 파일을 지침 대상이라고 잘못 수정하지 않기 위한 이름 확인입니다. 원문 조건 [`target.name.lower() != 'agents.md'`](src/core.py#L123) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “대상 폴더가 존재하지 않습니다.”

  입력 사례와 확인 순서: 대상 파일을 둘 상위 폴더가 없으면 적용하지 않습니다. 앱이 의도하지 않은 위치의 폴더를 새로 만들어 결과를 숨기는 대신 선택 경로부터 확인하게 합니다. 원문 조건 [`not target.parent.is_dir()`](src/core.py#L125) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “대상은 2 MiB 이하의 일반 파일이어야 합니다.”

  입력 사례와 확인 순서: 기존 대상이 일반 파일이 아니거나 2 MiB보다 크면 적용하지 않습니다. 폴더·특수 파일을 문서처럼 취급하거나 대용량 원본을 바꾸지 않게 합니다. 원문 조건 [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.”

  입력 사례와 확인 순서: 내용이 공백뿐이거나 새로 붙일 지침이 2 MiB보다 크면 거부합니다. 아무 내용 없는 적용이나 과도한 추가 입력을 정상 변경으로 보지 않습니다. 원문 조건 [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.”

  입력 사례와 확인 순서: 추가 지침 안에 앱의 시작·끝 관리 표시가 들어 있으면 거부합니다. 내용 속 표시를 실제 관리 경계로 잘못 읽어 원문 구간을 혼동하지 않도록 합니다. 원문 조건 [`BEGIN in added or END in added`](src/core.py#L136) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “적용 결과가 2 MiB 상한을 초과합니다.”

  입력 사례와 확인 순서: 원본과 새 지침을 합친 최종 문서가 2 MiB보다 크면 쓰지 않습니다. 원본과 추가분이 각각 작더라도 합쳐진 결과는 별도 크기 제한을 만족해야 합니다. 원문 조건 [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.”

  입력 사례와 확인 순서: 아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다. 대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다. 원문 조건 [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “미리보기 데이터가 변경되었습니다.”

  입력 사례와 확인 순서: 미리보기 계획 안의 원문·결과 바이트가 저장된 지문과 다르면 거부합니다. 사용자가 확인했던 변경 계획과 실제 쓸 내용이 같은지 확인하는 경계입니다. 원문 조건 [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “유효한 앱 원문 백업이 아닙니다.”

  입력 사례와 확인 순서: 백업이 앱이 정한 백업 폴더 안의 정상 파일이 아니거나 크기 제한을 넘으면 복원에 쓰지 않습니다. 아무 파일이나 원래 문서라고 덮어쓰지 않기 위한 확인입니다. 원문 조건 [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “백업 해시가 일치하지 않습니다.”

  입력 사례와 확인 순서: 백업 내용의 지문이 적용 때 기록한 원본 지문과 다르면 되돌리기를 거부합니다. 파일 이름이 같더라도 내용이 달라졌다면 안전한 원본으로 보지 않습니다. 원문 조건 [`digest(raw) != receipt['before_hash']`](src/core.py#L200) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “JSON 객체가 아닙니다.”

  입력 사례와 확인 순서: 한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다. 원문 조건 [`not isinstance(row, dict)`](src/core.py#L40) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “기존 관리구역 표식이 손상되었거나 중복되었습니다.”

  입력 사례와 확인 순서: 시작·끝 표시가 정확히 한 쌍이 아니거나 순서가 뒤집혔다면 적용할 구간이 불명확해 거부합니다. 여러 구간 중 임의의 하나를 골라 원문을 바꾸지 않습니다. 원문 조건 [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”

  입력 사례와 확인 순서: 이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다. 큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다. 원문 조건 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L89) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.”

  입력 사례와 확인 순서: 옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다. 이를 새 관측 이력으로 자동 해석하지 않습니다. 명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다. 원문 조건 [`self.state.get('schema_version') not in (2, 3)`](src/notifier.py#L93) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”

  입력 사례와 확인 순서: 저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다. 자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다. 원문 조건 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L95) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”

  입력 사례와 확인 순서: 어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다. 이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다. 원문 조건 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L97) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”

  입력 사례와 확인 순서: 채팅별 선택 설정 항목이 기대한 사전 형태가 아니면 저장 상태를 거부합니다. 설정 요청을 실제 관측 변경으로 잘못 바꾸는 자동 초기화를 하지 않습니다. 원문 조건 [`not isinstance(self.state.get('settings'), dict)`](src/notifier.py#L116) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다.”

  입력 사례와 확인 순서: 활동 상태 형식을 옮기기 전의 백업 내용이 원본과 다르면 덮어쓰지 않습니다. 이행은 저장 형식을 바꾸는 과정이며 다른 원본을 같은 자료처럼 취급하지 않습니다. 원문 조건 [`backup.read_bytes() != original`](src/notifier.py#L104) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다.”

  입력 사례와 확인 순서: 이전 기록에서 읽어 둔 시작·끝 위치가 참·거짓, 정수가 아닌 값 또는 음수라면 거부합니다. 파일의 몇 번째 바이트부터 읽을지를 알 수 없으므로 0으로 임의 초기화하지 않습니다. 원문 조건 [`any(isinstance(v, bool) or not isinstance(v, int) or v &lt; 0 for v in (offset, end))`](src/notifier.py#L111) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “JSON 객체가 아닙니다.”

  입력 사례와 확인 순서: 한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다. 원문 조건 [`not isinstance(record, dict)`](src/notifier.py#L435) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “명시 알림 파일 상한 초과”

  입력 사례와 확인 순서: 명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다. 짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게 하기 위한 크기 제한입니다. 원문 조건 [`path.stat().st_size &gt; 20000`](src/notifier.py#L500) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “객체가 아닌 응답”

  입력 사례와 확인 순서: 계정 서버의 응답이 이름별 값을 가진 객체가 아니면 한도 자료로 읽지 않습니다. 숫자·문자열만 온 응답에서 비율을 임의로 만들지 않습니다. 원문 조건 [`not isinstance(message, dict)`](src/usage.py#L226) (src/usage.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다. 최초 기준선 읽기와 새 변경은 다릅니다. 자산·글꼴 오류라면 이 차수 assets와 라이선스를 대조합니다. 과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다. 이유·이전값이 없으면 원문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

7차 → 8차의 실제 파일 비교입니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **수정** [src/app.py](src/app.py): 실행 자료에 이 변경이 반영되어 있는지 대조합니다.

- **수정** [src/notifier.py](src/notifier.py): 실행 자료에 이 변경이 반영되어 있는지 대조합니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다. 원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다. 이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다. Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


**이 수준에서 연결·실행·설계를 대조하는 순서**

선언의 정확한 코드와 전체 역할 원문은 LEVEL 5 및 연결된 소스에 보존합니다. 입력 사례는 검토 방법을 설명하며 실제 실행 결과가 아닙니다. 옵션 지정·기본값과 정상·거부 사례를 구분하고, 변경 시 호출자·공유 상태·표시 조건에 미치는 영향을 대조합니다.

- [src/app.py](src/app.py): 원문 사건·실제 화면·종료 상태를 따로 확인합니다. 이력에 있다고 알림이 떴다고 보지 않고 창이 닫혔다고 작업자 정리가 끝났다고 가정하지 않습니다.

- [src/core.py](src/core.py): 기록 파일과 지침 대상은 별도 준비물입니다. 기록은 온전한 줄·출처를, 지침은 대상·미리보기·백업을 확인하는 사례로 나눠 대조합니다.

- [src/notifier.py](src/notifier.py): 기준선·새 사건·같은 사건 보강을 다른 입력 사례로 준비합니다. 원본 시각이 있는지, 원문 읽기 위치가 유지되는지, 기존 이력에 이유만 붙는지 대조합니다.

- [src/theme.py](src/theme.py): 한글 파일 선택창의 이름 열·버튼·기본 문구를 각 조건으로 대조합니다. 앱 바깥 시스템 설정이 바뀌는 것으로 읽지 않습니다.

- [src/usage.py](src/usage.py): 선택한 EXE·실제 계정 연결·원본 한도 응답을 준비합니다. 숫자 1과 참 값, 비어 있는 기간과 실제 0 비율을 구분해 표시와 대조합니다.

- [src/visuals.py](src/visuals.py): 그림에 합성되는 수치·상태가 원문 값과 맞는지 대조하고, 회전하는 그림과 고정 문구의 표시를 별도로 확인할 사례를 준비합니다. 형상 좌표와 실제 계정 비율은 다른 단위입니다.

<a id="reading-level-4"></a>
## LEVEL 4 - Advanced

### LEVEL 4 · 설계 의도와 검토 경계

감시 폴링 간격을 0.2초 상수로 두고 중복 기록 감지와 이벤트 보강·읽기 경로를 바꿉니다. 빠른 폴링 설정이 모든 부하에서 즉시 알림을 보장하지는 않습니다.

감시 폴링 간격을 0.2초 상수로 두고 중복 기록 감지와 이벤트 보강·읽기 경로를 바꿉니다. 빠른 폴링 설정이 모든 부하에서 즉시 알림을 보장하지는 않습니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

Codex App Server의 `account/rateLimits/read`를 읽기 전용으로 조회합니다. 표시값은 남은 토큰 개수가 아니라 계정 사용 한도 비율입니다.

### LEVEL 4 · 이 차수 구현의 실제 근거

| 파일 | 역할·구성 |
| --- | --- |
| [src/app.py](src/app.py) | Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용. |
| [src/notifier.py](src/notifier.py) | 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다. |
| [src/core.py](src/core.py) | 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용. |
| [src/theme.py](src/theme.py) | 앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다. |
| [src/usage.py](src/usage.py) | Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다. |
| [src/visuals.py](src/visuals.py) | 실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다. |

| 단계 | 내용 |
| --- | --- |
| 입력 | 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정 |
| 처리 | 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시 |
| 출력 | 알림·변경 이력·로컬 진단 기록 |


### LEVEL 4 · 조건·변경·결과를 함께 검토하기

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다.

자산과 의존성을 준비한 이 차수 폴더에서 `python src/app.py`를 실행합니다. history 소스만으로 과거 배포 EXE와 동일한 화면·자산이 모두 복원되지는 않습니다.

#### LEVEL 4 · 이 보관본의 의존성 목록

[requirements.txt](requirements.txt)의 실제 항목입니다. 외부 실행 도구와 GPU 드라이버는 별도로 준비합니다.

```text
PySide6-Essentials==6.12.0
PyInstaller==6.22.3
```

#### LEVEL 4 · 소스에서 제공하는 CLI 옵션

**진입 소스:** [app.py](src/app.py)

**정의된 옵션 이름:** `--data-dir`, `--sessions`, `--smoke-test`, `--usage-smoke-test`, `--smoke-report`, `--show-details`, `--show-event`

**진입 소스:** [notifier.py](src/notifier.py)

**정의된 옵션 이름:** `--sessions`, `--work`


각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 4 · [src/app.py](src/app.py)

| 정의 | 역할 |
| --- | --- |
| [`operation_record`](src/app.py#L33) | 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다. |
| [`short_reason`](src/app.py#L75) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |
| [`QuitGuard`](src/app.py#L801) | 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L1108)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L1109)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L1110)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--usage-smoke-test`](src/app.py#L1111)

**코드의 선언:** `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`

**설정·옵션:** [`--smoke-report`](src/app.py#L1112)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L1113)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L1114)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L61)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


**거부 조건:** [`not lock.tryLock(100)`](src/app.py#L1139)

**오류 메시지:** 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

**거부 조건:** [`not isinstance(value, dict)`](src/app.py#L146)

**오류 메시지:** 앱 설정은 JSON 객체여야 합니다.

**거부 조건:** [`not path.is_dir()`](src/app.py#L654)

**오류 메시지:** 존재하는 sessions 폴더를 선택하세요.

**거부 조건:** [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L659)

**오류 메시지:** 존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.

**거부 조건:** [`self.plan is None`](src/app.py#L764)

**오류 메시지:** 새 미리보기가 필요합니다.

**거부 조건:** [`not receipts`](src/app.py#L776)

**오류 메시지:** 앱이 만든 적용 백업이 없습니다.


#### LEVEL 4 · [src/core.py](src/core.py)

| 정의 | 역할 |
| --- | --- |
| [`read_jsonl_tail`](src/core.py#L18) | 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| [`title_catalog`](src/core.py#L55) | 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| [`resolve_title`](src/core.py#L73) | 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| [`safe_path`](src/core.py#L97) | 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`MAX_TEXT_BYTES`](src/core.py#L9) | `정의=2 * 1024 * 1024` |
| [`BEGIN`](src/core.py#L10) | `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| [`END`](src/core.py#L11) | `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

**거부 조건:** [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112)

**오류 메시지:** 문서가 2 MiB 상한을 초과했습니다.

**거부 조건:** [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64)

**오류 메시지:** 제목 캐시 구조가 올바르지 않습니다.

**거부 조건:** [`target.name.lower() != 'agents.md'`](src/core.py#L123)

**오류 메시지:** 적용 대상은 AGENTS.md 파일이어야 합니다.

**거부 조건:** [`not target.parent.is_dir()`](src/core.py#L125)

**오류 메시지:** 대상 폴더가 존재하지 않습니다.

**거부 조건:** [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127)

**오류 메시지:** 대상은 2 MiB 이하의 일반 파일이어야 합니다.

**거부 조건:** [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134)

**오류 메시지:** 빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.

**거부 조건:** [`BEGIN in added or END in added`](src/core.py#L136)

**오류 메시지:** 지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.

**거부 조건:** [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150)

**오류 메시지:** 적용 결과가 2 MiB 상한을 초과합니다.

**거부 조건:** [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157)

**오류 메시지:** 대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.

**거부 조건:** [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177)

**오류 메시지:** 미리보기 데이터가 변경되었습니다.

**거부 조건:** [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197)

**오류 메시지:** 유효한 앱 원문 백업이 아닙니다.

**거부 조건:** [`digest(raw) != receipt['before_hash']`](src/core.py#L200)

**오류 메시지:** 백업 해시가 일치하지 않습니다.

**거부 조건:** [`not isinstance(row, dict)`](src/core.py#L40)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143)

**오류 메시지:** 기존 관리구역 표식이 손상되었거나 중복되었습니다.


#### LEVEL 4 · [src/notifier.py](src/notifier.py)

| 정의 | 역할 |
| --- | --- |
| [`atomic_json`](src/notifier.py#L32) | 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다. |
| [`source_datetime`](src/notifier.py#L62) | 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다. |
| [`duplicate_record`](src/notifier.py#L184) | 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다. |
| [`settings_record`](src/notifier.py#L195) | 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다. |
| [`lookup_parent_reason`](src/notifier.py#L335) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L382) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L636) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L637) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L17) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L18) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L19) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L20) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L21) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L22) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L23) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L24) | `정의=256` |
| [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25) | `정의=0.2` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L89)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') not in (2, 3)`](src/notifier.py#L93)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L95)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L97)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('settings'), dict)`](src/notifier.py#L116)

**오류 메시지:** 채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`backup.read_bytes() != original`](src/notifier.py#L104)

**오류 메시지:** 이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다.

**거부 조건:** [`any(isinstance(v, bool) or not isinstance(v, int) or v &lt; 0 for v in (offset, end))`](src/notifier.py#L111)

**오류 메시지:** 이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L435)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L500)

**오류 메시지:** 명시 알림 파일 상한 초과


#### LEVEL 4 · [src/theme.py](src/theme.py)

| 정의 | 역할 |
| --- | --- |
| [`MonochromeStyle`](src/theme.py#L46) | 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다. |
| [`KoreanDialogs`](src/theme.py#L71) | 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다. |
| [`DialogLayout`](src/theme.py#L87) | 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다. |

#### LEVEL 4 · [src/usage.py](src/usage.py)

| 정의 | 역할 |
| --- | --- |
| [`number`](src/usage.py#L16) | 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다. |
| [`normalize_limits`](src/usage.py#L35) | 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다. |
| [`discover_codex`](src/usage.py#L69) | 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`MAX_BYTES`](src/usage.py#L12) | `정의=1024 * 1024` |
| [`KST`](src/usage.py#L13) | `정의=timezone(timedelta(hours=9))` |

| 거부 조건 | 오류 메시지 |
| --- | --- |
| [`not isinstance(message, dict)`](src/usage.py#L226) | 객체가 아닌 응답 |

#### LEVEL 4 · [src/visuals.py](src/visuals.py)

| 정의 | 역할 |
| --- | --- |
| [`rotate_point`](src/visuals.py#L8) | X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다. |
| [`orbit_segments`](src/visuals.py#L23) | 세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다. |
| [`draw_orbit`](src/visuals.py#L54) | 장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다. |

</details>

변경 전·후 모델과 추론 강도, 공개된 이유, 관측 시각과 근거 수준을 함께 읽습니다. 기록되지 않은 값은 미확인으로 남깁니다. 로컬 기록은 서버 모델 신원 증명이 아닙니다.

**상황:** 알림이 나타나지 않음

**확인할 내용:** 감시하는 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 확인합니다. 최초 기준선 읽기와 새 변경 감지는 다릅니다.

**상황:** 자산 또는 글꼴 오류

**확인할 내용:** 이 차수에서 참조하는 assets와 라이선스를 준비합니다. 소스 이력에는 과거 대용량 프레임 자산이 없을 수 있습니다.

**상황:** 이유 또는 이전값이 없음

**확인할 내용:** 원문 기록에 해당 필드가 있는지 확인합니다. 누락된 동기를 추정해서 채우지 않습니다.


### LEVEL 4 · 재현과 전체 비교

1. 이 차수의 소스·requirements와 필요한 자산을 한 작업 폴더에 준비합니다.
2. 앱을 열고 위젯·상세창에서 감시 경로와 표시되는 기록을 확인합니다.
3. 새 변경이 기록되면 이전·이후 값과 이유를 비교하고, 기록 종류와 근거 수준을 함께 읽습니다.
4. 설정·이력은 개인 운영자료로 관리하고 다른 사용자에게 공유하기 전에 내용을 확인합니다.

위 구성요소의 입력·출력과 실패 조건을 같은 차수 소스에 연결해 검토합니다. 전체 비교는 추가·수정·삭제와 원래 보관 범위를 구분하는 근거입니다.

[자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)


### LEVEL 4 · 8차의 구체적인 기능과 확인

app.py·notifier.py의 폴링 주기와 이벤트 중복·보강 경로가 수정 대상입니다. 상수의 시간 단위와 대기열·읽기량 제한을 함께 검토해야 하며, 빠른 폴링을 이벤트 처리 완료 시간과 동일시할 수 없습니다. 원본 이벤트와 보강된 정보를 연결하는 상태 경계가 변경 영향의 핵심입니다.

**로컬 수집 경계와 UI·명시적 파일 작업의 경계**를 분리합니다. JSONL 입력에서 변경 감지·공개 이유 정리·알림·상세 표시로 이어지고, 설정·이력·진단은 로컬 운영 자료입니다. 관측된 변경과 명시 배정의 근거를 혼합하지 않습니다.

Windows에서 이 차수의 [requirements.txt](requirements.txt)에 맞는 Python 의존성과 해당 자산을 준비한 뒤 **이 차수 폴더에서** `python src/app.py`를 실행합니다. 현재 루트의 assets가 과거 모든 차수와 호환되는 것은 아니며, history 소스만으로 과거 EXE의 화면·자산 전체가 복원되는 것도 아닙니다.

아래 모듈·선언·거부 조건은 변경 영향 검토의 출발점입니다. 이름·상수만으로 전체 호출 순서나 예외 전파를 추정하지 말고 연결된 코드에서 분기와 호출자를 대조합니다.

**이 보관본 의존성 선언**: PySide6-Essentials==6.12.0 · PyInstaller==6.22.3. PySide6는 창을 만드는 도구이고 PyInstaller는 실행 파일을 묶는 도구입니다. 외부 실행 도구·GPU 드라이버는 별도 조건입니다.

**자료 경계와 모듈 연결**

- [src/](src): 관련 파일을 모아 둔 폴더.

- [README.md](README.md#reading-level-4): 설명을 읽는 Markdown 문서.

- [requirements.txt](requirements.txt): 문자로 적은 목록 파일.

- [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json): 항목별 값을 저장한 자료.

- [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md): 설명을 읽는 Markdown 문서.

- [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json): 항목별 값을 저장한 자료.

- [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff): 전후 파일의 달라진 줄을 기록한 비교 자료.

- [src/app.py](src/app.py): 모듈 책임: Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용.

- [src/notifier.py](src/notifier.py): 모듈 책임: 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다.

- [src/core.py](src/core.py): 모듈 책임: 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용.

- [src/theme.py](src/theme.py): 모듈 책임: 앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

- [src/usage.py](src/usage.py): 모듈 책임: Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

- [src/visuals.py](src/visuals.py): 모듈 책임: 실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

**실제 입력·설정과 기본값**

- [`--data-dir`](src/app.py#L1108) (src/app.py)

  앱 설정·이력을 저장할 폴더를 고릅니다. 기본은 LOCALAPPDATA 아래 CodexOrbit이며 그 환경값이 없으면 사용자 홈을 기준으로 합니다. 같은 폴더 중복 실행 잠금과 연결됩니다. 원문 선언: `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`.

- [`--sessions`](src/app.py#L1109) (src/app.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path`.

- [`--smoke-test`](src/app.py#L1110) (src/app.py)

  점검 실행을 켜는 스위치입니다. 숫자를 넣는 옵션이 아니라 이름을 붙여 켭니다. 옵션 존재 자체가 검사를 실행해 통과했다는 증거는 아닙니다. 원문 선언: `action='store_true'`.

- [`--usage-smoke-test`](src/app.py#L1111) (src/app.py)

  실제 계정 한도와 표시를 조회한 뒤 종료하는 점검 스위치입니다. 로컬 그림만 확인하는 검사와 달리 계정 연결 조건이 필요하고 비율을 잔여 토큰 개수로 읽지 않습니다. 원문 선언: `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`.

- [`--smoke-report`](src/app.py#L1112) (src/app.py)

  점검 결과를 저장할 파일 경로입니다. 폴더를 고르는 세션 옵션과 달리 보고서 파일을 지정합니다. 원문 선언: `type=Path`.

- [`--show-details`](src/app.py#L1113) (src/app.py)

  처음부터 상세창을 보여 주는 스위치입니다. 숨겨진 원문 값을 새로 만들어 주는 기능이 아닙니다. 원문 선언: `action='store_true'`.

- [`--show-event`](src/app.py#L1114) (src/app.py)

  이미 있는 이력의 사건 ID 또는 대상 ID를 지정해 다시 표시합니다. 실제 저장된 ID와 맞춰 읽고 새 사건 생성과 구분합니다. 원문 선언: `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`.

- [`ROLE_LABELS`](src/app.py#L61) (src/app.py)

  역할 코드와 사용자용 한글 이름의 대응표입니다. 예를 들어 build는 구현, verifier는 독립 검증으로 읽습니다. 화면 설명을 바꾸는 표이며 서버 모델을 바꾸는 설정은 아닙니다. 원문 선언: `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`.

- [`MAX_TEXT_BYTES`](src/core.py#L9) (src/core.py)

  읽거나 적용할 지침 문서의 크기 상한입니다. 원문·추가 지침·최종 결과의 제한과 연결되며 큰 문서 쓰기를 무제한 허용하지 않습니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`BEGIN`](src/core.py#L10) (src/core.py)

  앱이 관리하는 지침 구간이 시작되는 정확한 표시 문자열입니다. 문서의 나머지 부분과 구분하기 때문에 추가할 지침 안에 같은 표식을 넣지 못하게 합니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'`.

- [`END`](src/core.py#L11) (src/core.py)

  앱 관리 구간이 끝나는 정확한 표시 문자열입니다. 시작 표시보다 먼저 있거나 여러 번 있으면 원래 구간이 불명확해 적용을 거부하는 조건과 연결됩니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'`.

- [`--sessions`](src/notifier.py#L636) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L637) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L17) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L18) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L19) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게 하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L20) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록 하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L21) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게 합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L22) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L23) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료량을 제한합니다. 파일 하나의 상한과 별개인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L24) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

- [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25) (src/notifier.py)

  새 기록이 있는지 다시 확인하는 간격이며 단위는 초입니다. 0.2초는 1초의 5분의 1마다 확인하려는 설정이고 실제 알림이 그 시간 안에 반드시 뜬다는 보장은 아닙니다. 선언 숫자는 0.2입니다. 원문 선언: `정의=0.2`.

- [`MAX_BYTES`](src/usage.py#L12) (src/usage.py)

  계정 응답에서 읽을 최대 자료량입니다. 단위는 바이트이며 응답이 너무 클 때 무제한으로 받아들이지 않게 하는 경계입니다. 계산한 값은 1,048,576이며 바이트 제한에서는 1,024 KiB입니다. 원문 선언: `정의=1024 * 1024`.

- [`KST`](src/usage.py#L13) (src/usage.py)

  한국 표준시를 나타냅니다. UTC보다 9시간 빠른 시간대로 날짜·시각을 읽는 기준이며 컴퓨터 지역 시간과 구별합니다. 원문 선언: `정의=timezone(timedelta(hours=9))`.

**처리 책임과 원문에 명시된 함수 동작**

- [`operation_record`](src/app.py#L33) (src/app.py)

  이 분기의 설계 책임은 대화 본문을 넣지 않고 진행 단계와 실제 실행 중인 프로그램의 위치를 기록합니다. 이를 바꾸면 보존해야 할 결과는 “운영 단계를 확인하는 기록이 남습니다”입니다. 단계 진단에 필요하지 않은 대화 내용까지 복제하지 않기 위해서입니다

- [`short_reason`](src/app.py#L75) (src/app.py)

  이 분기의 설계 책임은 기록에 명시된 이유 또는 배정·선택 목적 문장을 우선 골라 짧게 보여 줍니다 이를 바꾸면 보존해야 할 결과는 “원문에 있는 이유를 읽을 수 있고 없는 이유는 만들어지지 않습니다”입니다. 공개된 문장과 앱이 추측한 동기를 혼동하지 않도록 하기 위해서입니다

- [`QuitGuard`](src/app.py#L801) (src/app.py)

  이 분기의 설계 책임은 종료 요청을 곧바로 끝내지 않고 감시 작업자가 따로 정리 작업을 마친 뒤 종료를 처리합니다. 이를 바꾸면 보존해야 할 결과는 “작업 정리와 창 종료의 순서가 유지됩니다”입니다. 아직 실행 중인 감시 작업을 남겨 둔 채 화면만 없애지 않도록 하기 위해서입니다

- [`read_jsonl_tail`](src/core.py#L18) (src/core.py)

  이 분기의 설계 책임은 파일에서 실제 줄바꿈을 뜻하는 LF 바이트로만 한 건씩 나누고 완성되지 않은 양끝 조각은 해석하지 않습니다. 이를 바꾸면 보존해야 할 결과는 “온전한 줄만 기록 한 건으로 읽습니다”입니다. 문장 안의 다른 줄바꿈 모양 문자나 반쪽 기록을 새 사건으로 잘못 세지 않기 위해서입니다

- [`title_catalog`](src/core.py#L55) (src/core.py)

  이 분기의 설계 책임은 공식 앱에서 확인해 저장한 제목과 컴퓨터 안의 제목 목록이 어디서 왔는지 함께 보존합니다. 이를 바꾸면 보존해야 할 결과는 “제목과 그 제목을 얻은 출처를 대조할 수 있습니다”입니다. 제목 문자열만 같다는 이유로 근거 수준까지 같다고 보지 않기 위해서입니다

- [`resolve_title`](src/core.py#L73) (src/core.py)

  이 분기의 설계 책임은 실제 부모 채팅 제목과 자식 작업명을 서로 다른 정보로 다룹니다 이를 바꾸면 보존해야 할 결과는 “어느 대화에서 생긴 어떤 작업인지 구별됩니다”입니다. 작업명을 새 채팅 제목이나 다른 부모 채팅으로 오해하지 않기 위해서입니다

- [`safe_path`](src/core.py#L97) (src/core.py)

  이 분기의 설계 책임은 파일 자체뿐 아니라 이미 존재하는 상위 폴더까지 확인해 바로가기처럼 다른 위치로 보내는 링크·재분석 지점을 거부합니다. 이를 바꾸면 보존해야 할 결과는 “연결을 통해 의도 밖의 위치를 수정하는 경로는 허용되지 않습니다”입니다. 겉으로 고른 폴더와 실제 쓰는 위치가 달라지는 일을 막기 위해서입니다

- [`atomic_json`](src/notifier.py#L32) (src/notifier.py)

  이 분기의 설계 책임은 같은 폴더에 따로 임시 파일을 완성한 뒤 교체하고 Windows의 짧은 파일 공유 충돌만 다시 시도합니다. 이를 바꾸면 보존해야 할 결과는 “반쯤 쓴 상태를 원래 파일처럼 노출하지 않도록 저장 경로를 구성합니다”입니다. 파일 저장 전체를 무제한 재시도하거나 모든 오류를 정상으로 감추지 않기 위해서입니다

- [`source_datetime`](src/notifier.py#L62) (src/notifier.py)

  이 분기의 설계 책임은 어느 시간대인지 포함한 올바른 원본 시각만 비교에 사용합니다. 이를 바꾸면 보존해야 할 결과는 “시각이 없으면 새 시각을 추측해 채우지 않습니다”입니다. 출처 불명확한 시각으로 사건 순서를 확정하지 않기 위해서입니다

- [`duplicate_record`](src/notifier.py#L184) (src/notifier.py)

  이 분기의 설계 책임은 원본 시각이 있는 복제만 중복으로 제외하고 과거 기준선을 다시 읽을 때의 순서는 복원합니다. 이를 바꾸면 보존해야 할 결과는 “복제 제거와 순서 복원이 서로 다른 처리로 유지됩니다”입니다. 시각이 없는 기록을 추측만으로 중복이라 지워 버리지 않기 위해서입니다

- [`settings_record`](src/notifier.py#L195) (src/notifier.py)

  이 분기의 설계 책임은 그 채팅에 실제로 저장된 native 설정 항목만 관측합니다. 이를 바꾸면 보존해야 할 결과는 “설정값은 읽지만 누가 바꿨는지와 실제 실행 모델은 추정하지 않습니다”입니다. 설정 선택과 서버에서 수행한 모델 실행을 같은 증거로 보지 않기 위해서입니다

- [`lookup_parent_reason`](src/notifier.py#L335) (src/notifier.py)

  이 분기의 설계 책임은 부모 기록의 최근 공개 호출만 정해진 양 안에서 찾아보고 정기 감시의 읽기 위치는 그대로 둡니다 이를 바꾸면 보존해야 할 결과는 “이유를 찾는 보조 읽기가 다음 감시 출발점을 옮기지 않습니다”입니다. 부모 이유를 찾다가 새 사건을 건너뛰거나 전체 큰 파일을 무제한 읽지 않기 위해서입니다

- [`enrich_event`](src/notifier.py#L382) (src/notifier.py)

  이 분기의 설계 책임은 정확히 연결된 사건의 첫 배정 이유만 기존 이력에 덧붙이고 새 알림은 띄우지 않습니다. 이를 바꾸면 보존해야 할 결과는 “같은 사건의 설명이 보강되고 중복 알림은 만들어지지 않습니다”입니다. 이유 보강과 새 모델 변경 사건을 구분하기 위해서입니다

- [`MonochromeStyle`](src/theme.py#L46) (src/theme.py)

  이 분기의 설계 책임은 운영체제 기본 기호도 앱 안에서는 색이 없는 표현으로 맞춥니다 이를 바꾸면 보존해야 할 결과는 “앱 소유 화면 안의 기호 표현이 정리됩니다”입니다. 앱 바깥 운영체제의 아이콘까지 바꾸는 설정으로 확대하지 않도록 범위를 구분해야 합니다

- [`KoreanDialogs`](src/theme.py#L71) (src/theme.py)

  이 분기의 설계 책임은 기본 파일 선택창의 정해진 문구를 한국어로 제공합니다. 이를 바꾸면 보존해야 할 결과는 “번역 묶음이 없어도 기본 파일 선택 안내를 읽을 수 있습니다”입니다. 앱 안내 문구와 사용자가 고르는 파일 이름을 구분하기 위해서입니다

- [`DialogLayout`](src/theme.py#L87) (src/theme.py)

  이 분기의 설계 책임은 파일 이름 열과 한글 버튼에 필요한 표시 공간을 확보합니다. 이를 바꾸면 보존해야 할 결과는 “이름과 버튼을 구별해서 읽는 배치가 됩니다”입니다. 번역 문구를 넣기만 하고 화면 공간은 그대로 두는 문제를 피하기 위해서입니다

- [`number`](src/usage.py#L16) (src/usage.py)

  이 분기의 설계 책임은 그 값을 올바른 한도 숫자로 받아들이지 않습니다. 이를 바꾸면 보존해야 할 결과는 “잘못된 입력이 사용 가능한 비율로 표시되지 않습니다”입니다. 예를 들어 참을 숫자 1처럼 읽어 정상 비율로 오해하지 않기 위해서입니다

- [`normalize_limits`](src/usage.py#L35) (src/usage.py)

  이 분기의 설계 책임은 공식 응답의 여러 한도 묶음을 우선 읽고 빠진 기간이나 수치를 덧만들지 않습니다. 이를 바꾸면 보존해야 할 결과는 “존재하는 기간의 실제 비율만 표시 근거가 됩니다”입니다. 없는 주간·단기 한도를 다른 값으로 추정해 채우지 않기 위해서입니다

- [`discover_codex`](src/usage.py#L69) (src/usage.py)

  이 분기의 설계 책임은 사용자가 고른 위치, 명령 검색 경로 PATH, 공식 데스크톱 앱 묶음 위치 순서로 실행 파일 EXE만 찾습니다 이를 바꾸면 보존해야 할 결과는 “선택 순서에 맞는 실제 실행 파일이 연결 후보가 됩니다”입니다. 동명이름의 문서·폴더를 실행 프로그램으로 잘못 사용하지 않기 위해서입니다

- [`rotate_point`](src/visuals.py#L8) (src/visuals.py)

  이 분기의 설계 책임은 가로 X축·세로 Y축·깊이 Z축 순서로 회전시키고 깊이값도 남깁니다. 이를 바꾸면 보존해야 할 결과는 “평면 위치뿐 아니라 앞뒤를 나타내는 좌표가 유지됩니다”입니다. 회전 순서를 바꾸면 같은 각도여도 물체 방향이 달라질 수 있기 때문입니다

- [`orbit_segments`](src/visuals.py#L23) (src/visuals.py)

  이 구현의 책임은 원들을 작은 선 조각으로 나누고 먼 곳은 작게 보이는 원근 계산으로 옮긴 뒤 뒤쪽부터 정렬합니다. 변경 시 유지할 결과는“앞쪽 선이 뒤쪽 선 위에 그려질 순서가 나옵니다”입니다.겹침과 깊이감을 화면의 실제 그리기 순서에 연결하기 위해서입니다

- [`draw_orbit`](src/visuals.py#L54) (src/visuals.py)

  이 구현의 책임은 움직이는 장식과 실제 숫자를 별도로 다루고 원문에 정한 앞쪽 관이 중심을 가리는 순서로 그립니다 변경 시 유지할 결과는“이 차수의 가림 규칙이 반영된 합성이 나옵니다”입니다.후속 차수의 중심 숫자 고정·가림 방지 규칙을 과거 차수에 거꾸로 적용하지 않기 위해서입니다

**멈추거나 거부되는 조건과 읽는 방법**

- 거부 분기 [`not lock.tryLock(100)`](src/app.py#L1139) (src/app.py) → 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

  같은 저장 폴더를 이미 다른 Codex Orbit가 쓰거나 잠금 파일에 접근할 수 없으면 시작을 거부합니다. 한 설정·상태 파일을 두 실행이 동시에 바꾸지 않도록 하며, 이 메시지만으로 어느 쪽 원인인지 확정하지 않습니다.

- 거부 분기 [`not isinstance(value, dict)`](src/app.py#L146) (src/app.py) → 앱 설정은 JSON 객체여야 합니다.

  앱 설정이 항목 이름과 값을 가진 사전이어야 합니다. 예를 들어 목록만 저장돼 있으면 설정 이름으로 값을 찾을 수 없어 거부합니다.

- 거부 분기 [`not path.is_dir()`](src/app.py#L654) (src/app.py) → 존재하는 sessions 폴더를 선택하세요.

  선택한 기록 경로가 실제 폴더가 아니면 거부합니다. 오타가 있는 위치나 파일 하나를 감시 폴더로 잘못 지정했는지 먼저 확인합니다.

- 거부 분기 [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L659) (src/app.py) → 존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.

  수동으로 지정한 경로가 실제 .exe 실행 파일이 아니면 거부합니다. 실제 Codex 실행 파일을 고르거나 값을 비워 정해진 자동 탐색을 사용해야 합니다.

- 거부 분기 [`self.plan is None`](src/app.py#L764) (src/app.py) → 새 미리보기가 필요합니다.

  아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다. 대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다.

- 거부 분기 [`not receipts`](src/app.py#L776) (src/app.py) → 앱이 만든 적용 백업이 없습니다.

  앱이 지침 적용 전에 만든 백업이 없으면 그 백업을 이용한 되돌리기를 할 수 없습니다. 임의의 다른 문서를 원래 내용이라고 추정하지 않습니다.

- 거부 분기 [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112) (src/core.py) → 문서가 2 MiB 상한을 초과했습니다.

  지침 원본 문서가 2 MiB보다 크면 읽기 범위를 벗어나 거부합니다. 작은 설명으로 예상한 입력을 대용량 파일 읽기로 확대하지 않는 제한입니다.

- 거부 분기 [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64) (src/core.py) → 제목 캐시 구조가 올바르지 않습니다.

  보관한 제목 목록이 기대한 이름별 저장 형식이 아니면 거부합니다. 제목의 출처와 연결을 알 수 없는데도 빈 목록으로 자동 덮어쓰지 않습니다.

- 거부 분기 [`target.name.lower() != 'agents.md'`](src/core.py#L123) (src/core.py) → 적용 대상은 AGENTS.md 파일이어야 합니다.

  선택한 파일 이름이 AGENTS.md가 아니면 적용하지 않습니다. 다른 문서나 데이터 파일을 지침 대상이라고 잘못 수정하지 않기 위한 이름 확인입니다.

- 거부 분기 [`not target.parent.is_dir()`](src/core.py#L125) (src/core.py) → 대상 폴더가 존재하지 않습니다.

  대상 파일을 둘 상위 폴더가 없으면 적용하지 않습니다. 앱이 의도하지 않은 위치의 폴더를 새로 만들어 결과를 숨기는 대신 선택 경로부터 확인하게 합니다.

- 거부 분기 [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127) (src/core.py) → 대상은 2 MiB 이하의 일반 파일이어야 합니다.

  기존 대상이 일반 파일이 아니거나 2 MiB보다 크면 적용하지 않습니다. 폴더·특수 파일을 문서처럼 취급하거나 대용량 원본을 바꾸지 않게 합니다.

- 거부 분기 [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134) (src/core.py) → 빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.

  내용이 공백뿐이거나 새로 붙일 지침이 2 MiB보다 크면 거부합니다. 아무 내용 없는 적용이나 과도한 추가 입력을 정상 변경으로 보지 않습니다.

- 거부 분기 [`BEGIN in added or END in added`](src/core.py#L136) (src/core.py) → 지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.

  추가 지침 안에 앱의 시작·끝 관리 표시가 들어 있으면 거부합니다. 내용 속 표시를 실제 관리 경계로 잘못 읽어 원문 구간을 혼동하지 않도록 합니다.

- 거부 분기 [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150) (src/core.py) → 적용 결과가 2 MiB 상한을 초과합니다.

  원본과 새 지침을 합친 최종 문서가 2 MiB보다 크면 쓰지 않습니다. 원본과 추가분이 각각 작더라도 합쳐진 결과는 별도 크기 제한을 만족해야 합니다.

- 거부 분기 [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157) (src/core.py) → 대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.

  아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다. 대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다.

- 거부 분기 [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177) (src/core.py) → 미리보기 데이터가 변경되었습니다.

  미리보기 계획 안의 원문·결과 바이트가 저장된 지문과 다르면 거부합니다. 사용자가 확인했던 변경 계획과 실제 쓸 내용이 같은지 확인하는 경계입니다.

- 거부 분기 [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197) (src/core.py) → 유효한 앱 원문 백업이 아닙니다.

  백업이 앱이 정한 백업 폴더 안의 정상 파일이 아니거나 크기 제한을 넘으면 복원에 쓰지 않습니다. 아무 파일이나 원래 문서라고 덮어쓰지 않기 위한 확인입니다.

- 거부 분기 [`digest(raw) != receipt['before_hash']`](src/core.py#L200) (src/core.py) → 백업 해시가 일치하지 않습니다.

  백업 내용의 지문이 적용 때 기록한 원본 지문과 다르면 되돌리기를 거부합니다. 파일 이름이 같더라도 내용이 달라졌다면 안전한 원본으로 보지 않습니다.

- 거부 분기 [`not isinstance(row, dict)`](src/core.py#L40) (src/core.py) → JSON 객체가 아닙니다.

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다.

- 거부 분기 [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143) (src/core.py) → 기존 관리구역 표식이 손상되었거나 중복되었습니다.

  시작·끝 표시가 정확히 한 쌍이 아니거나 순서가 뒤집혔다면 적용할 구간이 불명확해 거부합니다. 여러 구간 중 임의의 하나를 골라 원문을 바꾸지 않습니다.

- 거부 분기 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L89) (src/notifier.py) → 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

  이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다. 큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다.

- 거부 분기 [`self.state.get('schema_version') not in (2, 3)`](src/notifier.py#L93) (src/notifier.py) → 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

  옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다. 이를 새 관측 이력으로 자동 해석하지 않습니다. 명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다.

- 거부 분기 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L95) (src/notifier.py) → 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

  저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다. 자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다.

- 거부 분기 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L97) (src/notifier.py) → 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

  어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다. 이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다.

- 거부 분기 [`not isinstance(self.state.get('settings'), dict)`](src/notifier.py#L116) (src/notifier.py) → 채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

  채팅별 선택 설정 항목이 기대한 사전 형태가 아니면 저장 상태를 거부합니다. 설정 요청을 실제 관측 변경으로 잘못 바꾸는 자동 초기화를 하지 않습니다.

- 거부 분기 [`backup.read_bytes() != original`](src/notifier.py#L104) (src/notifier.py) → 이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다.

  활동 상태 형식을 옮기기 전의 백업 내용이 원본과 다르면 덮어쓰지 않습니다. 이행은 저장 형식을 바꾸는 과정이며 다른 원본을 같은 자료처럼 취급하지 않습니다.

- 거부 분기 [`any(isinstance(v, bool) or not isinstance(v, int) or v &lt; 0 for v in (offset, end))`](src/notifier.py#L111) (src/notifier.py) → 이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다.

  이전 기록에서 읽어 둔 시작·끝 위치가 참·거짓, 정수가 아닌 값 또는 음수라면 거부합니다. 파일의 몇 번째 바이트부터 읽을지를 알 수 없으므로 0으로 임의 초기화하지 않습니다.

- 거부 분기 [`not isinstance(record, dict)`](src/notifier.py#L435) (src/notifier.py) → JSON 객체가 아닙니다.

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다.

- 거부 분기 [`path.stat().st_size &gt; 20000`](src/notifier.py#L500) (src/notifier.py) → 명시 알림 파일 상한 초과

  명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다. 짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게 하기 위한 크기 제한입니다.

- 거부 분기 [`not isinstance(message, dict)`](src/usage.py#L226) (src/usage.py) → 객체가 아닌 응답

  계정 서버의 응답이 이름별 값을 가진 객체가 아니면 한도 자료로 읽지 않습니다. 숫자·문자열만 온 응답에서 비율을 임의로 만들지 않습니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다. 최초 기준선 읽기와 새 변경은 다릅니다. 자산·글꼴 오류라면 이 차수 assets와 라이선스를 대조합니다. 과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다. 이유·이전값이 없으면 원문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

7차 → 8차의 실제 파일 비교입니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **수정** [src/app.py](src/app.py): 변경 영향은 연결된 전체 diff의 실제 분기로 한정합니다.

- **수정** [src/notifier.py](src/notifier.py): 변경 영향은 연결된 전체 diff의 실제 분기로 한정합니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다. 원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다. 이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다. Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


**이 수준에서 연결·실행·설계를 대조하는 순서**

선언의 정확한 코드와 전체 역할 원문은 LEVEL 5 및 연결된 소스에 보존합니다. 입력 사례는 검토 방법을 설명하며 실제 실행 결과가 아닙니다. 옵션 지정·기본값과 정상·거부 사례를 구분하고, 변경 시 호출자·공유 상태·표시 조건에 미치는 영향을 대조합니다.

- [src/app.py](src/app.py): UI 소유 관계와 작업자 수명이 연결됩니다. 표시용 이름 변경이 원문 의미를 바꾸거나 이벤트 요약이 전후 필드·근거를 덮지 않는지 검토해야 합니다.

- [src/core.py](src/core.py): LF 경계·경로 확인을 바꾸면 사건 판독 또는 실제 파일 쓰기 위치가 달라집니다. 문서 해시·관리 표식·백업 검증을 약화하는 변경과 화면 문구 수정은 다른 영향 범위입니다.

- [src/notifier.py](src/notifier.py): 상태 저장과 파일 읽기 위치 변경은 과거 사건 재생·누락·중복에 영향을 줄 수 있습니다. 보조 조회가 순차 위치를 이동하지 않는 경계와 손상 상태의 원본 보존이 핵심입니다.

- [src/theme.py](src/theme.py): 전역 앱 스타일 변경은 여러 창에 영향을 주므로 개별 창 배치와 상호작용을 함께 확인해야 합니다. 시스템 전체 아이콘 변경으로 확대하지 않습니다.

- [src/usage.py](src/usage.py): 응답 정규화가 기간이나 수치를 만들어 넣으면 자료 의미가 바뀝니다. 잘못된 숫자 거부·공식 복수 한도 우선·읽기 전용 경계를 UI 비율 계산과 함께 검토합니다.

- [src/visuals.py](src/visuals.py): 회전 순서·고유 축·합성 영역 변경은 보이는 형태에 영향을 줍니다. 자산 선택과 상태 데이터는 분리해 원소번호·계정 퍼센트가 같은 숫자로 섞이지 않게 해야 합니다.

<a id="reading-level-5"></a>
## LEVEL 5 - Expert


### LEVEL 5 · 8차의 구체적인 기능과 확인

7차→8차 비교에서 0.2초 설정과 수집 경로 변경을 추적합니다. end-to-end 알림 지연의 시작·끝, 부하·파일 수·중복 입력 분모가 보존되지 않았으므로 지연 보장은 불가합니다. 당시 실행 결과도 미확인이어서 빠른 설정을 실측 성능 우위로 바꾸지 않습니다.

**증거의 범위는 이 차수 공개 원문과 보존 소스입니다.** 로컬 기록의 모델·추론 값은 서버가 보증한 모델 신원 인증이 아닙니다. 원문에 없는 이유·이전값·실행 성과는 보간하지 않습니다. 입력은 현재 사용자 JSONL과 설정, 출력은 알림·이력·로컬 진단이며 관측 변경과 명시 배정은 다른 증거 종류입니다.

Windows에서 이 차수의 [requirements.txt](requirements.txt)에 맞는 Python 의존성과 해당 자산을 준비한 뒤 **이 차수 폴더에서** `python src/app.py`를 실행합니다. 현재 루트의 assets가 과거 모든 차수와 호환되는 것은 아니며, history 소스만으로 과거 EXE의 화면·자산 전체가 복원되는 것도 아닙니다.

재현에는 동일 차수 의존성·자산·입력·설정·실행 표면이 필요합니다. 아래 선언의 상한·스키마·거부 분기는 검토 가능한 소스 조건이며, 실제 부하·종료·화면 동작의 성공 증거와 구분합니다.

**이 보관본 의존성 선언**: PySide6-Essentials==6.12.0 · PyInstaller==6.22.3. PySide6는 창을 만드는 도구이고 PyInstaller는 실행 파일을 묶는 도구입니다. 외부 실행 도구·GPU 드라이버는 별도 조건입니다.

**자료 경계와 모듈 연결**

- [src/](src): 관련 파일을 모아 둔 폴더.

- [README.md](README.md): 설명을 읽는 Markdown 문서.

- [requirements.txt](requirements.txt): 문자로 적은 목록 파일.

- [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json): 항목별 값을 저장한 자료.

- [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md): 설명을 읽는 Markdown 문서.

- [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json): 항목별 값을 저장한 자료.

- [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff): 전후 파일의 달라진 줄을 기록한 비교 자료.

- [src/app.py](src/app.py): 원문 모듈 역할 선언: Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용.

- [src/notifier.py](src/notifier.py): 원문 모듈 역할 선언: 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다.

- [src/core.py](src/core.py): 원문 모듈 역할 선언: 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용.

- [src/theme.py](src/theme.py): 원문 모듈 역할 선언: 앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

- [src/usage.py](src/usage.py): 원문 모듈 역할 선언: Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

- [src/visuals.py](src/visuals.py): 원문 모듈 역할 선언: 실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

**실제 입력·설정과 기본값**

- [app.py](src/app.py)에서 사용할 수 있는 옵션: `--data-dir`, `--sessions`, `--smoke-test`, `--usage-smoke-test`, `--smoke-report`, `--show-details`, `--show-event`.

- [notifier.py](src/notifier.py)에서 사용할 수 있는 옵션: `--sessions`, `--work`.

- 재현 시 대조할 원문 선언 [`--data-dir`](src/app.py#L1108) (src/app.py): `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`.

- 재현 시 대조할 원문 선언 [`--sessions`](src/app.py#L1109) (src/app.py): `type=Path`.

- 재현 시 대조할 원문 선언 [`--smoke-test`](src/app.py#L1110) (src/app.py): `action='store_true'`.

- 재현 시 대조할 원문 선언 [`--usage-smoke-test`](src/app.py#L1111) (src/app.py): `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`.

- 재현 시 대조할 원문 선언 [`--smoke-report`](src/app.py#L1112) (src/app.py): `type=Path`.

- 재현 시 대조할 원문 선언 [`--show-details`](src/app.py#L1113) (src/app.py): `action='store_true'`.

- 재현 시 대조할 원문 선언 [`--show-event`](src/app.py#L1114) (src/app.py): `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`.

- 재현 시 대조할 원문 선언 [`ROLE_LABELS`](src/app.py#L61) (src/app.py): `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`.

- 재현 시 대조할 원문 선언 [`MAX_TEXT_BYTES`](src/core.py#L9) (src/core.py): `정의=2 * 1024 * 1024`.

- 재현 시 대조할 원문 선언 [`BEGIN`](src/core.py#L10) (src/core.py): `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'`.

- 재현 시 대조할 원문 선언 [`END`](src/core.py#L11) (src/core.py): `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'`.

- 재현 시 대조할 원문 선언 [`--sessions`](src/notifier.py#L636) (src/notifier.py): `type=Path; default=Path.home() / '.codex/sessions'`.

- 재현 시 대조할 원문 선언 [`--work`](src/notifier.py#L637) (src/notifier.py): `type=Path; default=ROOT / 'work'`.

- 재현 시 대조할 원문 선언 [`ROOT`](src/notifier.py#L17) (src/notifier.py): `정의=Path(__file__).resolve().parents[1]`.

- 재현 시 대조할 원문 선언 [`APP_ID`](src/notifier.py#L18) (src/notifier.py): `정의='Yunseok.Codex.ModelChangeNotifier'`.

- 재현 시 대조할 원문 선언 [`READ_BYTES`](src/notifier.py#L19) (src/notifier.py): `정의=512 * 1024`.

- 재현 시 대조할 원문 선언 [`MAX_RECORD`](src/notifier.py#L20) (src/notifier.py): `정의=2 * 1024 * 1024`.

- 재현 시 대조할 원문 선언 [`MAX_FILES`](src/notifier.py#L21) (src/notifier.py): `정의=4096`.

- 재현 시 대조할 원문 선언 [`LOG_BYTES`](src/notifier.py#L22) (src/notifier.py): `정의=2 * 1024 * 1024`.

- 재현 시 대조할 원문 선언 [`POLL_READ_BYTES`](src/notifier.py#L23) (src/notifier.py): `정의=8 * 1024 * 1024`.

- 재현 시 대조할 원문 선언 [`MAX_PENDING`](src/notifier.py#L24) (src/notifier.py): `정의=256`.

- 재현 시 대조할 원문 선언 [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25) (src/notifier.py): `정의=0.2`.

- 재현 시 대조할 원문 선언 [`MAX_BYTES`](src/usage.py#L12) (src/usage.py): `정의=1024 * 1024`.

- 재현 시 대조할 원문 선언 [`KST`](src/usage.py#L13) (src/usage.py): `정의=timezone(timedelta(hours=9))`.

**처리 책임과 원문에 명시된 함수 동작**

- [`operation_record`](src/app.py#L33) (src/app.py): 원문이 명시한 동작 계약은 다음과 같습니다. 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다.

- [`short_reason`](src/app.py#L75) (src/app.py): 원문이 명시한 동작 계약은 다음과 같습니다. 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다.

- [`QuitGuard`](src/app.py#L801) (src/app.py): 원문이 명시한 동작 계약은 다음과 같습니다. 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다.

- [`read_jsonl_tail`](src/core.py#L18) (src/core.py): 원문이 명시한 동작 계약은 다음과 같습니다. 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다.

- [`title_catalog`](src/core.py#L55) (src/core.py): 원문이 명시한 동작 계약은 다음과 같습니다. 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다.

- [`resolve_title`](src/core.py#L73) (src/core.py): 원문이 명시한 동작 계약은 다음과 같습니다. 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다.

- [`safe_path`](src/core.py#L97) (src/core.py): 원문이 명시한 동작 계약은 다음과 같습니다. 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다.

- [`atomic_json`](src/notifier.py#L32) (src/notifier.py): 원문이 명시한 동작 계약은 다음과 같습니다. 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다.

- [`source_datetime`](src/notifier.py#L62) (src/notifier.py): 원문이 명시한 동작 계약은 다음과 같습니다. 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다.

- [`duplicate_record`](src/notifier.py#L184) (src/notifier.py): 원문이 명시한 동작 계약은 다음과 같습니다. 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다.

- [`settings_record`](src/notifier.py#L195) (src/notifier.py): 원문이 명시한 동작 계약은 다음과 같습니다. 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다.

- [`lookup_parent_reason`](src/notifier.py#L335) (src/notifier.py): 원문이 명시한 동작 계약은 다음과 같습니다. 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다.

- [`enrich_event`](src/notifier.py#L382) (src/notifier.py): 원문이 명시한 동작 계약은 다음과 같습니다. 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다.

- [`MonochromeStyle`](src/theme.py#L46) (src/theme.py): 원문이 명시한 동작 계약은 다음과 같습니다. 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다.

- [`KoreanDialogs`](src/theme.py#L71) (src/theme.py): 원문이 명시한 동작 계약은 다음과 같습니다. 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다.

- [`DialogLayout`](src/theme.py#L87) (src/theme.py): 원문이 명시한 동작 계약은 다음과 같습니다. 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다.

- [`number`](src/usage.py#L16) (src/usage.py): 원문이 명시한 동작 계약은 다음과 같습니다. 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다.

- [`normalize_limits`](src/usage.py#L35) (src/usage.py): 원문이 명시한 동작 계약은 다음과 같습니다. 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다.

- [`discover_codex`](src/usage.py#L69) (src/usage.py): 원문이 명시한 동작 계약은 다음과 같습니다. 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다.

- [`rotate_point`](src/visuals.py#L8) (src/visuals.py): 원문이 명시한 동작 계약은 다음과 같습니다. X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다.

- [`orbit_segments`](src/visuals.py#L23) (src/visuals.py): 원문이 명시한 동작 계약은 다음과 같습니다. 세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다.

- [`draw_orbit`](src/visuals.py#L54) (src/visuals.py): 원문이 명시한 동작 계약은 다음과 같습니다. 장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다.

**멈추거나 거부되는 조건과 읽는 방법**

- 경계 사례 [`not lock.tryLock(100)`](src/app.py#L1139) (src/app.py): 원문 오류는 “같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(value, dict)`](src/app.py#L146) (src/app.py): 원문 오류는 “앱 설정은 JSON 객체여야 합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not path.is_dir()`](src/app.py#L654) (src/app.py): 원문 오류는 “존재하는 sessions 폴더를 선택하세요.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L659) (src/app.py): 원문 오류는 “존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`self.plan is None`](src/app.py#L764) (src/app.py): 원문 오류는 “새 미리보기가 필요합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not receipts`](src/app.py#L776) (src/app.py): 원문 오류는 “앱이 만든 적용 백업이 없습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112) (src/core.py): 원문 오류는 “문서가 2 MiB 상한을 초과했습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64) (src/core.py): 원문 오류는 “제목 캐시 구조가 올바르지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`target.name.lower() != 'agents.md'`](src/core.py#L123) (src/core.py): 원문 오류는 “적용 대상은 AGENTS.md 파일이어야 합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not target.parent.is_dir()`](src/core.py#L125) (src/core.py): 원문 오류는 “대상 폴더가 존재하지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127) (src/core.py): 원문 오류는 “대상은 2 MiB 이하의 일반 파일이어야 합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134) (src/core.py): 원문 오류는 “빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`BEGIN in added or END in added`](src/core.py#L136) (src/core.py): 원문 오류는 “지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150) (src/core.py): 원문 오류는 “적용 결과가 2 MiB 상한을 초과합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157) (src/core.py): 원문 오류는 “대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177) (src/core.py): 원문 오류는 “미리보기 데이터가 변경되었습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197) (src/core.py): 원문 오류는 “유효한 앱 원문 백업이 아닙니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`digest(raw) != receipt['before_hash']`](src/core.py#L200) (src/core.py): 원문 오류는 “백업 해시가 일치하지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(row, dict)`](src/core.py#L40) (src/core.py): 원문 오류는 “JSON 객체가 아닙니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143) (src/core.py): 원문 오류는 “기존 관리구역 표식이 손상되었거나 중복되었습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L89) (src/notifier.py): 원문 오류는 “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`self.state.get('schema_version') not in (2, 3)`](src/notifier.py#L93) (src/notifier.py): 원문 오류는 “구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L95) (src/notifier.py): 원문 오류는 “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L97) (src/notifier.py): 원문 오류는 “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(self.state.get('settings'), dict)`](src/notifier.py#L116) (src/notifier.py): 원문 오류는 “채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`backup.read_bytes() != original`](src/notifier.py#L104) (src/notifier.py): 원문 오류는 “이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`any(isinstance(v, bool) or not isinstance(v, int) or v &lt; 0 for v in (offset, end))`](src/notifier.py#L111) (src/notifier.py): 원문 오류는 “이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(record, dict)`](src/notifier.py#L435) (src/notifier.py): 원문 오류는 “JSON 객체가 아닙니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`path.stat().st_size &gt; 20000`](src/notifier.py#L500) (src/notifier.py): 원문 오류는 “명시 알림 파일 상한 초과”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(message, dict)`](src/usage.py#L226) (src/usage.py): 원문 오류는 “객체가 아닌 응답”. 허용 입력과 구분해 재현할 조건입니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다. 최초 기준선 읽기와 새 변경은 다릅니다. 자산·글꼴 오류라면 이 차수 assets와 라이선스를 대조합니다. 과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다. 이유·이전값이 없으면 원문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

7차 → 8차의 실제 파일 비교입니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **수정** [src/app.py](src/app.py): 공개 바이트 비교에서 분류된 변경이며 의도·성능을 추정하지 않습니다.

- **수정** [src/notifier.py](src/notifier.py): 공개 바이트 비교에서 분류된 변경이며 의도·성능을 추정하지 않습니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다. 원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다. 이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다. Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


기존의 전체 설명·표·코드·함수 참조·파일별 비교는 아래에 그대로 이어집니다. [자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)
<!-- reading-levels:end -->



[프로젝트](../../README.md) · [전체 차수](../../docs/REVISION_INDEX.md) · [원본 자료](.) · [← 이전: 7차](../07%EC%B0%A8/README.md) · [다음: 9차 →](../09%EC%B0%A8/README.md)

<a name="-목적과-이-차수의-역할"></a>
## 목적과 이 차수의 역할

감시 폴링 간격을 0.2초 상수로 두고 중복 기록 감지와 이벤트 보강·읽기 경로를 바꿉니다. 빠른 폴링 설정이 모든 부하에서 즉시 알림을 보장하지는 않습니다.

<a name="features"></a>

<a name="-핵심-기능과-보존-범위"></a>
## 핵심 기능과 보존 범위

**항목:** 1

**이 차수에서 확인할 내용:** 감시 폴링 간격을 0.2초 상수로 두고 중복 기록 감지와 이벤트 보강·읽기 경로를 바꿉니다. 빠른 폴링 설정이 모든 부하에서 즉시 알림을 보장하지는 않습니다.

**항목:** 2

**이 차수에서 확인할 내용:** 로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

**항목:** 3

**이 차수에서 확인할 내용:** 앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

**항목:** 4

**이 차수에서 확인할 내용:** Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

**항목:** 5

**이 차수에서 확인할 내용:** 실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

**항목:** 6

**이 차수에서 확인할 내용:** Codex App Server의 `account/rateLimits/read`를 읽기 전용으로 조회합니다. 표시값은 남은 토큰 개수가 아니라 계정 사용 한도 비율입니다.


<a name="-입력처리출력"></a>
## 입력·처리·출력

| 단계 | 내용 |
| --- | --- |
| 입력 | 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정 |
| 처리 | 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시 |
| 출력 | 알림·변경 이력·로컬 진단 기록 |


<a name="usage"></a>

<a name="️-화면과-사용-흐름"></a>
## 화면과 사용 흐름

1. 이 차수의 소스·requirements와 필요한 자산을 한 작업 폴더에 준비합니다.
2. 앱을 열고 위젯·상세창에서 감시 경로와 표시되는 기록을 확인합니다.
3. 새 변경이 기록되면 이전·이후 값과 이유를 비교하고, 기록 종류와 근거 수준을 함께 읽습니다.
4. 설정·이력은 개인 운영자료로 관리하고 다른 사용자에게 공유하기 전에 내용을 확인합니다.

<a name="structure"></a>

<a name="-실제-자료-구성"></a>
## 실제 자료 구성

| 경로 | 자료 종류 |
| --- | --- |
| [src/](src) | 하위 자료 폴더 |
| [README.md](README.md) | MD 파일 |
| [requirements.txt](requirements.txt) | TXT 파일 |
| [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json) | JSON 파일 |
| [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md) | MD 파일 |
| [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json) | JSON 파일 |
| [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) | DIFF 파일 |

<a name="-주요-모듈과-코드-읽기"></a>
## 주요 모듈과 코드 읽기

| 파일 | 역할·구성 |
| --- | --- |
| [src/app.py](src/app.py) | Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용. |
| [src/notifier.py](src/notifier.py) | 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다. |
| [src/core.py](src/core.py) | 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용. |
| [src/theme.py](src/theme.py) | 앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다. |
| [src/usage.py](src/usage.py) | Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다. |
| [src/visuals.py](src/visuals.py) | 실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다. |

<a name="setup"></a>

<a name="-설치-환경과-실행사용법"></a>
## 설치 환경과 실행·사용법

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다.

자산과 의존성을 준비한 이 차수 폴더에서 `python src/app.py`를 실행합니다. history 소스만으로 과거 배포 EXE와 동일한 화면·자산이 모두 복원되지는 않습니다.

<a name="-이-보관본의-의존성-목록"></a>
### 이 보관본의 의존성 목록

[requirements.txt](requirements.txt)의 실제 항목입니다. 외부 실행 도구와 GPU 드라이버는 별도로 준비합니다.

```text
PySide6-Essentials==6.12.0
PyInstaller==6.22.3
```

<a name="️-소스에서-제공하는-cli-옵션"></a>
### 소스에서 제공하는 CLI 옵션

**진입 소스:** [app.py](src/app.py)

**정의된 옵션 이름:** `--data-dir`, `--sessions`, `--smoke-test`, `--usage-smoke-test`, `--smoke-report`, `--show-details`, `--show-event`

**진입 소스:** [notifier.py](src/notifier.py)

**정의된 옵션 이름:** `--sessions`, `--work`


각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

### [src/app.py](src/app.py)

| 정의 | 역할 |
| --- | --- |
| [`operation_record`](src/app.py#L33) | 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다. |
| [`short_reason`](src/app.py#L75) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |
| [`QuitGuard`](src/app.py#L801) | 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L1108)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L1109)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L1110)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--usage-smoke-test`](src/app.py#L1111)

**코드의 선언:** `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`

**설정·옵션:** [`--smoke-report`](src/app.py#L1112)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L1113)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L1114)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L61)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


**거부 조건:** [`not lock.tryLock(100)`](src/app.py#L1139)

**오류 메시지:** 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

**거부 조건:** [`not isinstance(value, dict)`](src/app.py#L146)

**오류 메시지:** 앱 설정은 JSON 객체여야 합니다.

**거부 조건:** [`not path.is_dir()`](src/app.py#L654)

**오류 메시지:** 존재하는 sessions 폴더를 선택하세요.

**거부 조건:** [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L659)

**오류 메시지:** 존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.

**거부 조건:** [`self.plan is None`](src/app.py#L764)

**오류 메시지:** 새 미리보기가 필요합니다.

**거부 조건:** [`not receipts`](src/app.py#L776)

**오류 메시지:** 앱이 만든 적용 백업이 없습니다.


### [src/core.py](src/core.py)

| 정의 | 역할 |
| --- | --- |
| [`read_jsonl_tail`](src/core.py#L18) | 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| [`title_catalog`](src/core.py#L55) | 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| [`resolve_title`](src/core.py#L73) | 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| [`safe_path`](src/core.py#L97) | 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`MAX_TEXT_BYTES`](src/core.py#L9) | `정의=2 * 1024 * 1024` |
| [`BEGIN`](src/core.py#L10) | `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| [`END`](src/core.py#L11) | `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

**거부 조건:** [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112)

**오류 메시지:** 문서가 2 MiB 상한을 초과했습니다.

**거부 조건:** [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64)

**오류 메시지:** 제목 캐시 구조가 올바르지 않습니다.

**거부 조건:** [`target.name.lower() != 'agents.md'`](src/core.py#L123)

**오류 메시지:** 적용 대상은 AGENTS.md 파일이어야 합니다.

**거부 조건:** [`not target.parent.is_dir()`](src/core.py#L125)

**오류 메시지:** 대상 폴더가 존재하지 않습니다.

**거부 조건:** [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127)

**오류 메시지:** 대상은 2 MiB 이하의 일반 파일이어야 합니다.

**거부 조건:** [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134)

**오류 메시지:** 빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.

**거부 조건:** [`BEGIN in added or END in added`](src/core.py#L136)

**오류 메시지:** 지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.

**거부 조건:** [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150)

**오류 메시지:** 적용 결과가 2 MiB 상한을 초과합니다.

**거부 조건:** [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157)

**오류 메시지:** 대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.

**거부 조건:** [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177)

**오류 메시지:** 미리보기 데이터가 변경되었습니다.

**거부 조건:** [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197)

**오류 메시지:** 유효한 앱 원문 백업이 아닙니다.

**거부 조건:** [`digest(raw) != receipt['before_hash']`](src/core.py#L200)

**오류 메시지:** 백업 해시가 일치하지 않습니다.

**거부 조건:** [`not isinstance(row, dict)`](src/core.py#L40)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143)

**오류 메시지:** 기존 관리구역 표식이 손상되었거나 중복되었습니다.


### [src/notifier.py](src/notifier.py)

| 정의 | 역할 |
| --- | --- |
| [`atomic_json`](src/notifier.py#L32) | 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다. |
| [`source_datetime`](src/notifier.py#L62) | 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다. |
| [`duplicate_record`](src/notifier.py#L184) | 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다. |
| [`settings_record`](src/notifier.py#L195) | 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다. |
| [`lookup_parent_reason`](src/notifier.py#L335) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L382) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L636) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L637) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L17) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L18) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L19) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L20) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L21) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L22) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L23) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L24) | `정의=256` |
| [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25) | `정의=0.2` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L89)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') not in (2, 3)`](src/notifier.py#L93)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L95)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L97)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('settings'), dict)`](src/notifier.py#L116)

**오류 메시지:** 채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`backup.read_bytes() != original`](src/notifier.py#L104)

**오류 메시지:** 이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다.

**거부 조건:** [`any(isinstance(v, bool) or not isinstance(v, int) or v &lt; 0 for v in (offset, end))`](src/notifier.py#L111)

**오류 메시지:** 이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L435)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L500)

**오류 메시지:** 명시 알림 파일 상한 초과


### [src/theme.py](src/theme.py)

| 정의 | 역할 |
| --- | --- |
| [`MonochromeStyle`](src/theme.py#L46) | 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다. |
| [`KoreanDialogs`](src/theme.py#L71) | 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다. |
| [`DialogLayout`](src/theme.py#L87) | 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다. |

### [src/usage.py](src/usage.py)

| 정의 | 역할 |
| --- | --- |
| [`number`](src/usage.py#L16) | 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다. |
| [`normalize_limits`](src/usage.py#L35) | 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다. |
| [`discover_codex`](src/usage.py#L69) | 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`MAX_BYTES`](src/usage.py#L12) | `정의=1024 * 1024` |
| [`KST`](src/usage.py#L13) | `정의=timezone(timedelta(hours=9))` |

| 거부 조건 | 오류 메시지 |
| --- | --- |
| [`not isinstance(message, dict)`](src/usage.py#L226) | 객체가 아닌 응답 |

### [src/visuals.py](src/visuals.py)

| 정의 | 역할 |
| --- | --- |
| [`rotate_point`](src/visuals.py#L8) | X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다. |
| [`orbit_segments`](src/visuals.py#L23) | 세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다. |
| [`draw_orbit`](src/visuals.py#L54) | 장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다. |

</details>

<a name="results"></a>

<a name="-처리-결과와-출력-읽기"></a>
## 처리 결과와 출력 읽기

변경 전·후 모델과 추론 강도, 공개된 이유, 관측 시각과 근거 수준을 함께 읽습니다. 기록되지 않은 값은 미확인으로 남깁니다. 로컬 기록은 서버 모델 신원 증명이 아닙니다.

<a name="️-제약과-문제-해결"></a>
## 제약과 문제 해결

**상황:** 알림이 나타나지 않음

**확인할 내용:** 감시하는 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 확인합니다. 최초 기준선 읽기와 새 변경 감지는 다릅니다.

**상황:** 자산 또는 글꼴 오류

**확인할 내용:** 이 차수에서 참조하는 assets와 라이선스를 준비합니다. 소스 이력에는 과거 대용량 프레임 자산이 없을 수 있습니다.

**상황:** 이유 또는 이전값이 없음

**확인할 내용:** 원문 기록에 해당 필드가 있는지 확인합니다. 누락된 동기를 추정해서 채우지 않습니다.


<a name="changes"></a>

<a name="-직전-자료와-전체-비교"></a>
## 직전 자료와 전체 비교

7차에서 8차로 이어지는 실제 파일 비교입니다.

[전체 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff)

추가·수정·삭제, 주석·공백·개행과 바이너리 크기·해시는 연결된 원래 비교 자료에서 확인합니다.

<details>
<summary>파일별 비교·크기·해시 자세히 보기</summary>

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

- **수정** `src/app.py`: 이전 62775바이트, SHA-256 `2e961caa97a0aecc6b26d0948d53f72369451e6af01bd9124c759c66875a3398`; 현재 63254바이트, SHA-256 `694f3cbe443ee55bd6b07557517e8d1d38ddbc8f6d06ebd7a2777003e02fbf6a`.

- **수정** `src/notifier.py`: 이전 33077바이트, SHA-256 `bb9659e678dcdb5d214c2a3b7201d42785dd287f317d3ac854ef39ca5f41edb6`; 현재 38231바이트, SHA-256 `5ebefd6304fee2279d53203c492a0c7452d2b363a74d03f52b20039487849321`.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

</details>

[프로젝트](../../README.md) · [전체 차수](../../docs/REVISION_INDEX.md) · [원본 자료](.) · [← 이전: 7차](../07%EC%B0%A8/README.md) · [다음: 9차 →](../09%EC%B0%A8/README.md)
