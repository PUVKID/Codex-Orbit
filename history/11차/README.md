<div align="center">

<a name="-codex-orbit--11차"></a>
# Codex Orbit · 11차

모델과 추론 강도의 이전·현재를 각각 두 칸으로 보여 주고 쉬운 추론 강도 이름을 사용합니다. 사용 한도 요약과 큰 변경 제목의 화면 구성을 정리합니다.

**기술 분류:** Windows 데스크톱 · Python · PySide6

[핵심 기능](#features) · [사용 흐름](#usage) · [자료 구성](#structure) · [준비와 실행](#setup) · [결과 읽기](#results) · [직전 변경](#changes)

</div>
<!-- reading-levels:start -->
[LEVEL 1 - Beginner](#reading-level-1) · [LEVEL 2 - Explorer](#reading-level-2) · [LEVEL 3 - Practitioner](#reading-level-3) · [LEVEL 4 - Advanced](#reading-level-4) · [LEVEL 5 - Expert](#reading-level-5)

프로젝트 전체의 설명은 [LEVEL 1 - Beginner](../../docs/%EC%9D%BD%EA%B8%B0%EC%95%88%EB%82%B4/%EB%A0%88%EB%B2%A81.md)부터 [LEVEL 5 - Expert](../../docs/%EC%9D%BD%EA%B8%B0%EC%95%88%EB%82%B4/%EB%A0%88%EB%B2%A85.md)까지 같은 범위로 연결됩니다.

<a id="reading-level-1"></a>
## LEVEL 1 - Beginner

### LEVEL 1 · 이 자료가 하는 일과 달라진 점

모델과 추론 강도의 이전·현재를 각각 두 칸으로 보여 주고 쉬운 추론 강도 이름을 사용합니다. 사용 한도 요약과 큰 변경 제목의 화면 구성을 정리합니다.

### LEVEL 1 · 실제 동작을 따라 읽기

모델과 추론 강도의 이전·현재를 각각 두 칸으로 보여 주고 쉬운 추론 강도 이름을 사용합니다. 사용 한도 요약과 큰 변경 제목의 화면 구성을 정리합니다.

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

| 내용 |
| --- |
| **정의:** [`operation_record`](src/app.py#L33)<br>**소스에 적힌 역할:** 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다. |
| **정의:** [`short_reason`](src/app.py#L86)<br>**소스에 적힌 역할:** 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |
| **정의:** [`QuitGuard`](src/app.py#L1005)<br>**소스에 적힌 역할:** 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L1363)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L1364)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L1365)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--usage-smoke-test`](src/app.py#L1366)

**코드의 선언:** `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`

**설정·옵션:** [`--smoke-report`](src/app.py#L1367)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L1368)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L1369)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L72)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


**거부 조건:** [`not lock.tryLock(100)`](src/app.py#L1394)

**오류 메시지:** 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

**거부 조건:** [`not isinstance(value, dict)`](src/app.py#L157)

**오류 메시지:** 앱 설정은 JSON 객체여야 합니다.

**거부 조건:** [`not path.is_dir()`](src/app.py#L820)

**오류 메시지:** 존재하는 sessions 폴더를 선택하세요.

**거부 조건:** [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L825)

**오류 메시지:** 존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.

**거부 조건:** [`self.plan is None`](src/app.py#L968)

**오류 메시지:** 새 미리보기가 필요합니다.

**거부 조건:** [`not receipts`](src/app.py#L980)

**오류 메시지:** 앱이 만든 적용 백업이 없습니다.


#### LEVEL 1 · [src/core.py](src/core.py)

| 내용 |
| --- |
| **정의:** [`read_jsonl_tail`](src/core.py#L18)<br>**소스에 적힌 역할:** 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| **정의:** [`title_catalog`](src/core.py#L55)<br>**소스에 적힌 역할:** 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| **정의:** [`resolve_title`](src/core.py#L73)<br>**소스에 적힌 역할:** 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| **정의:** [`safe_path`](src/core.py#L97)<br>**소스에 적힌 역할:** 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 내용 |
| --- |
| **설정·옵션:** [`MAX_TEXT_BYTES`](src/core.py#L9)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`BEGIN`](src/core.py#L10)<br>**코드의 선언:** `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| **설정·옵션:** [`END`](src/core.py#L11)<br>**코드의 선언:** `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

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

| 내용 |
| --- |
| **정의:** [`atomic_json`](src/notifier.py#L32)<br>**소스에 적힌 역할:** 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다. |
| **정의:** [`source_datetime`](src/notifier.py#L62)<br>**소스에 적힌 역할:** 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다. |
| **정의:** [`duplicate_record`](src/notifier.py#L184)<br>**소스에 적힌 역할:** 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다. |
| **정의:** [`settings_record`](src/notifier.py#L195)<br>**소스에 적힌 역할:** 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다. |
| **정의:** [`lookup_parent_reason`](src/notifier.py#L335)<br>**소스에 적힌 역할:** 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| **정의:** [`enrich_event`](src/notifier.py#L382)<br>**소스에 적힌 역할:** 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 내용 |
| --- |
| **설정·옵션:** [`--sessions`](src/notifier.py#L636)<br>**코드의 선언:** `type=Path; default=Path.home() / '.codex/sessions'` |
| **설정·옵션:** [`--work`](src/notifier.py#L637)<br>**코드의 선언:** `type=Path; default=ROOT / 'work'` |
| **설정·옵션:** [`ROOT`](src/notifier.py#L17)<br>**코드의 선언:** `정의=Path(__file__).resolve().parents[1]` |
| **설정·옵션:** [`APP_ID`](src/notifier.py#L18)<br>**코드의 선언:** `정의='Yunseok.Codex.ModelChangeNotifier'` |
| **설정·옵션:** [`READ_BYTES`](src/notifier.py#L19)<br>**코드의 선언:** `정의=512 * 1024` |
| **설정·옵션:** [`MAX_RECORD`](src/notifier.py#L20)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`MAX_FILES`](src/notifier.py#L21)<br>**코드의 선언:** `정의=4096` |
| **설정·옵션:** [`LOG_BYTES`](src/notifier.py#L22)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`POLL_READ_BYTES`](src/notifier.py#L23)<br>**코드의 선언:** `정의=8 * 1024 * 1024` |
| **설정·옵션:** [`MAX_PENDING`](src/notifier.py#L24)<br>**코드의 선언:** `정의=256` |
| **설정·옵션:** [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25)<br>**코드의 선언:** `정의=0.2` |

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

| 내용 |
| --- |
| **정의:** [`MonochromeStyle`](src/theme.py#L51)<br>**소스에 적힌 역할:** 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다. |
| **정의:** [`KoreanDialogs`](src/theme.py#L76)<br>**소스에 적힌 역할:** 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다. |
| **정의:** [`DialogLayout`](src/theme.py#L92)<br>**소스에 적힌 역할:** 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다. |

#### LEVEL 1 · [src/usage.py](src/usage.py)

| 내용 |
| --- |
| **정의:** [`number`](src/usage.py#L16)<br>**소스에 적힌 역할:** 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다. |
| **정의:** [`normalize_limits`](src/usage.py#L35)<br>**소스에 적힌 역할:** 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다. |
| **정의:** [`discover_codex`](src/usage.py#L69)<br>**소스에 적힌 역할:** 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다. |

| 내용 |
| --- |
| **설정·옵션:** [`MAX_BYTES`](src/usage.py#L12)<br>**코드의 선언:** `정의=1024 * 1024` |
| **설정·옵션:** [`KST`](src/usage.py#L13)<br>**코드의 선언:** `정의=timezone(timedelta(hours=9))` |

| 내용 |
| --- |
| **거부 조건:** [`not isinstance(message, dict)`](src/usage.py#L226)<br>**오류 메시지:** 객체가 아닌 응답 |

#### LEVEL 1 · [src/visuals.py](src/visuals.py)

| 내용 |
| --- |
| **정의:** [`rotate_point`](src/visuals.py#L8)<br>**소스에 적힌 역할:** X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다. |
| **정의:** [`orbit_segments`](src/visuals.py#L23)<br>**소스에 적힌 역할:** 세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다. |
| **정의:** [`draw_orbit`](src/visuals.py#L55)<br>**소스에 적힌 역할:** 장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다. |

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

<a id="reading-level-2"></a>
## LEVEL 2 - Explorer

### LEVEL 2 · 목적과 구성의 연결

모델과 추론 강도의 이전·현재를 각각 두 칸으로 보여 주고 쉬운 추론 강도 이름을 사용합니다. 사용 한도 요약과 큰 변경 제목의 화면 구성을 정리합니다.

모델과 추론 강도의 이전·현재를 각각 두 칸으로 보여 주고 쉬운 추론 강도 이름을 사용합니다. 사용 한도 요약과 큰 변경 제목의 화면 구성을 정리합니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

Codex App Server의 `account/rateLimits/read`를 읽기 전용으로 조회합니다. 표시값은 남은 토큰 개수가 아니라 계정 사용 한도 비율입니다.

### LEVEL 2 · 입력에서 출력으로

**단계:** 입력

**내용:** 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

**단계:** 처리

**내용:** 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시

**단계:** 출력

**내용:** 알림·변경 이력·로컬 진단 기록


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

| 내용 |
| --- |
| **정의:** [`operation_record`](src/app.py#L33)<br>**소스에 적힌 역할:** 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다. |
| **정의:** [`short_reason`](src/app.py#L86)<br>**소스에 적힌 역할:** 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |
| **정의:** [`QuitGuard`](src/app.py#L1005)<br>**소스에 적힌 역할:** 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L1363)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L1364)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L1365)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--usage-smoke-test`](src/app.py#L1366)

**코드의 선언:** `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`

**설정·옵션:** [`--smoke-report`](src/app.py#L1367)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L1368)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L1369)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L72)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


**거부 조건:** [`not lock.tryLock(100)`](src/app.py#L1394)

**오류 메시지:** 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

**거부 조건:** [`not isinstance(value, dict)`](src/app.py#L157)

**오류 메시지:** 앱 설정은 JSON 객체여야 합니다.

**거부 조건:** [`not path.is_dir()`](src/app.py#L820)

**오류 메시지:** 존재하는 sessions 폴더를 선택하세요.

**거부 조건:** [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L825)

**오류 메시지:** 존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.

**거부 조건:** [`self.plan is None`](src/app.py#L968)

**오류 메시지:** 새 미리보기가 필요합니다.

**거부 조건:** [`not receipts`](src/app.py#L980)

**오류 메시지:** 앱이 만든 적용 백업이 없습니다.


#### LEVEL 2 · [src/core.py](src/core.py)

| 내용 |
| --- |
| **정의:** [`read_jsonl_tail`](src/core.py#L18)<br>**소스에 적힌 역할:** 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| **정의:** [`title_catalog`](src/core.py#L55)<br>**소스에 적힌 역할:** 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| **정의:** [`resolve_title`](src/core.py#L73)<br>**소스에 적힌 역할:** 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| **정의:** [`safe_path`](src/core.py#L97)<br>**소스에 적힌 역할:** 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 내용 |
| --- |
| **설정·옵션:** [`MAX_TEXT_BYTES`](src/core.py#L9)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`BEGIN`](src/core.py#L10)<br>**코드의 선언:** `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| **설정·옵션:** [`END`](src/core.py#L11)<br>**코드의 선언:** `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

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

| 내용 |
| --- |
| **정의:** [`atomic_json`](src/notifier.py#L32)<br>**소스에 적힌 역할:** 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다. |
| **정의:** [`source_datetime`](src/notifier.py#L62)<br>**소스에 적힌 역할:** 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다. |
| **정의:** [`duplicate_record`](src/notifier.py#L184)<br>**소스에 적힌 역할:** 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다. |
| **정의:** [`settings_record`](src/notifier.py#L195)<br>**소스에 적힌 역할:** 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다. |
| **정의:** [`lookup_parent_reason`](src/notifier.py#L335)<br>**소스에 적힌 역할:** 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| **정의:** [`enrich_event`](src/notifier.py#L382)<br>**소스에 적힌 역할:** 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 내용 |
| --- |
| **설정·옵션:** [`--sessions`](src/notifier.py#L636)<br>**코드의 선언:** `type=Path; default=Path.home() / '.codex/sessions'` |
| **설정·옵션:** [`--work`](src/notifier.py#L637)<br>**코드의 선언:** `type=Path; default=ROOT / 'work'` |
| **설정·옵션:** [`ROOT`](src/notifier.py#L17)<br>**코드의 선언:** `정의=Path(__file__).resolve().parents[1]` |
| **설정·옵션:** [`APP_ID`](src/notifier.py#L18)<br>**코드의 선언:** `정의='Yunseok.Codex.ModelChangeNotifier'` |
| **설정·옵션:** [`READ_BYTES`](src/notifier.py#L19)<br>**코드의 선언:** `정의=512 * 1024` |
| **설정·옵션:** [`MAX_RECORD`](src/notifier.py#L20)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`MAX_FILES`](src/notifier.py#L21)<br>**코드의 선언:** `정의=4096` |
| **설정·옵션:** [`LOG_BYTES`](src/notifier.py#L22)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`POLL_READ_BYTES`](src/notifier.py#L23)<br>**코드의 선언:** `정의=8 * 1024 * 1024` |
| **설정·옵션:** [`MAX_PENDING`](src/notifier.py#L24)<br>**코드의 선언:** `정의=256` |
| **설정·옵션:** [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25)<br>**코드의 선언:** `정의=0.2` |

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

| 내용 |
| --- |
| **정의:** [`MonochromeStyle`](src/theme.py#L51)<br>**소스에 적힌 역할:** 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다. |
| **정의:** [`KoreanDialogs`](src/theme.py#L76)<br>**소스에 적힌 역할:** 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다. |
| **정의:** [`DialogLayout`](src/theme.py#L92)<br>**소스에 적힌 역할:** 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다. |

#### LEVEL 2 · [src/usage.py](src/usage.py)

| 내용 |
| --- |
| **정의:** [`number`](src/usage.py#L16)<br>**소스에 적힌 역할:** 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다. |
| **정의:** [`normalize_limits`](src/usage.py#L35)<br>**소스에 적힌 역할:** 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다. |
| **정의:** [`discover_codex`](src/usage.py#L69)<br>**소스에 적힌 역할:** 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다. |

| 내용 |
| --- |
| **설정·옵션:** [`MAX_BYTES`](src/usage.py#L12)<br>**코드의 선언:** `정의=1024 * 1024` |
| **설정·옵션:** [`KST`](src/usage.py#L13)<br>**코드의 선언:** `정의=timezone(timedelta(hours=9))` |

| 내용 |
| --- |
| **거부 조건:** [`not isinstance(message, dict)`](src/usage.py#L226)<br>**오류 메시지:** 객체가 아닌 응답 |

#### LEVEL 2 · [src/visuals.py](src/visuals.py)

| 내용 |
| --- |
| **정의:** [`rotate_point`](src/visuals.py#L8)<br>**소스에 적힌 역할:** X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다. |
| **정의:** [`orbit_segments`](src/visuals.py#L23)<br>**소스에 적힌 역할:** 세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다. |
| **정의:** [`draw_orbit`](src/visuals.py#L55)<br>**소스에 적힌 역할:** 장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다. |

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

<a id="reading-level-3"></a>
## LEVEL 3 - Practitioner

### LEVEL 3 · 이 차수를 준비하는 범위

모델과 추론 강도의 이전·현재를 각각 두 칸으로 보여 주고 쉬운 추론 강도 이름을 사용합니다. 사용 한도 요약과 큰 변경 제목의 화면 구성을 정리합니다.

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

| 내용 |
| --- |
| **정의:** [`operation_record`](src/app.py#L33)<br>**소스에 적힌 역할:** 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다. |
| **정의:** [`short_reason`](src/app.py#L86)<br>**소스에 적힌 역할:** 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |
| **정의:** [`QuitGuard`](src/app.py#L1005)<br>**소스에 적힌 역할:** 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L1363)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L1364)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L1365)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--usage-smoke-test`](src/app.py#L1366)

**코드의 선언:** `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`

**설정·옵션:** [`--smoke-report`](src/app.py#L1367)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L1368)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L1369)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L72)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


**거부 조건:** [`not lock.tryLock(100)`](src/app.py#L1394)

**오류 메시지:** 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

**거부 조건:** [`not isinstance(value, dict)`](src/app.py#L157)

**오류 메시지:** 앱 설정은 JSON 객체여야 합니다.

**거부 조건:** [`not path.is_dir()`](src/app.py#L820)

**오류 메시지:** 존재하는 sessions 폴더를 선택하세요.

**거부 조건:** [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L825)

**오류 메시지:** 존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.

**거부 조건:** [`self.plan is None`](src/app.py#L968)

**오류 메시지:** 새 미리보기가 필요합니다.

**거부 조건:** [`not receipts`](src/app.py#L980)

**오류 메시지:** 앱이 만든 적용 백업이 없습니다.


#### LEVEL 3 · [src/core.py](src/core.py)

| 내용 |
| --- |
| **정의:** [`read_jsonl_tail`](src/core.py#L18)<br>**소스에 적힌 역할:** 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| **정의:** [`title_catalog`](src/core.py#L55)<br>**소스에 적힌 역할:** 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| **정의:** [`resolve_title`](src/core.py#L73)<br>**소스에 적힌 역할:** 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| **정의:** [`safe_path`](src/core.py#L97)<br>**소스에 적힌 역할:** 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 내용 |
| --- |
| **설정·옵션:** [`MAX_TEXT_BYTES`](src/core.py#L9)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`BEGIN`](src/core.py#L10)<br>**코드의 선언:** `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| **설정·옵션:** [`END`](src/core.py#L11)<br>**코드의 선언:** `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

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

| 내용 |
| --- |
| **정의:** [`atomic_json`](src/notifier.py#L32)<br>**소스에 적힌 역할:** 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다. |
| **정의:** [`source_datetime`](src/notifier.py#L62)<br>**소스에 적힌 역할:** 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다. |
| **정의:** [`duplicate_record`](src/notifier.py#L184)<br>**소스에 적힌 역할:** 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다. |
| **정의:** [`settings_record`](src/notifier.py#L195)<br>**소스에 적힌 역할:** 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다. |
| **정의:** [`lookup_parent_reason`](src/notifier.py#L335)<br>**소스에 적힌 역할:** 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| **정의:** [`enrich_event`](src/notifier.py#L382)<br>**소스에 적힌 역할:** 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 내용 |
| --- |
| **설정·옵션:** [`--sessions`](src/notifier.py#L636)<br>**코드의 선언:** `type=Path; default=Path.home() / '.codex/sessions'` |
| **설정·옵션:** [`--work`](src/notifier.py#L637)<br>**코드의 선언:** `type=Path; default=ROOT / 'work'` |
| **설정·옵션:** [`ROOT`](src/notifier.py#L17)<br>**코드의 선언:** `정의=Path(__file__).resolve().parents[1]` |
| **설정·옵션:** [`APP_ID`](src/notifier.py#L18)<br>**코드의 선언:** `정의='Yunseok.Codex.ModelChangeNotifier'` |
| **설정·옵션:** [`READ_BYTES`](src/notifier.py#L19)<br>**코드의 선언:** `정의=512 * 1024` |
| **설정·옵션:** [`MAX_RECORD`](src/notifier.py#L20)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`MAX_FILES`](src/notifier.py#L21)<br>**코드의 선언:** `정의=4096` |
| **설정·옵션:** [`LOG_BYTES`](src/notifier.py#L22)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`POLL_READ_BYTES`](src/notifier.py#L23)<br>**코드의 선언:** `정의=8 * 1024 * 1024` |
| **설정·옵션:** [`MAX_PENDING`](src/notifier.py#L24)<br>**코드의 선언:** `정의=256` |
| **설정·옵션:** [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25)<br>**코드의 선언:** `정의=0.2` |

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

| 내용 |
| --- |
| **정의:** [`MonochromeStyle`](src/theme.py#L51)<br>**소스에 적힌 역할:** 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다. |
| **정의:** [`KoreanDialogs`](src/theme.py#L76)<br>**소스에 적힌 역할:** 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다. |
| **정의:** [`DialogLayout`](src/theme.py#L92)<br>**소스에 적힌 역할:** 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다. |

#### LEVEL 3 · [src/usage.py](src/usage.py)

| 내용 |
| --- |
| **정의:** [`number`](src/usage.py#L16)<br>**소스에 적힌 역할:** 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다. |
| **정의:** [`normalize_limits`](src/usage.py#L35)<br>**소스에 적힌 역할:** 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다. |
| **정의:** [`discover_codex`](src/usage.py#L69)<br>**소스에 적힌 역할:** 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다. |

| 내용 |
| --- |
| **설정·옵션:** [`MAX_BYTES`](src/usage.py#L12)<br>**코드의 선언:** `정의=1024 * 1024` |
| **설정·옵션:** [`KST`](src/usage.py#L13)<br>**코드의 선언:** `정의=timezone(timedelta(hours=9))` |

| 내용 |
| --- |
| **거부 조건:** [`not isinstance(message, dict)`](src/usage.py#L226)<br>**오류 메시지:** 객체가 아닌 응답 |

#### LEVEL 3 · [src/visuals.py](src/visuals.py)

| 내용 |
| --- |
| **정의:** [`rotate_point`](src/visuals.py#L8)<br>**소스에 적힌 역할:** X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다. |
| **정의:** [`orbit_segments`](src/visuals.py#L23)<br>**소스에 적힌 역할:** 세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다. |
| **정의:** [`draw_orbit`](src/visuals.py#L55)<br>**소스에 적힌 역할:** 장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다. |

</details>

### LEVEL 3 · 실제 사용·실험 순서

1. 이 차수의 소스·requirements와 필요한 자산을 한 작업 폴더에 준비합니다.
2. 앱을 열고 위젯·상세창에서 감시 경로와 표시되는 기록을 확인합니다.
3. 새 변경이 기록되면 이전·이후 값과 이유를 비교하고, 기록 종류와 근거 수준을 함께 읽습니다.
4. 설정·이력은 개인 운영자료로 관리하고 다른 사용자에게 공유하기 전에 내용을 확인합니다.

**단계:** 입력

**내용:** 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

**단계:** 처리

**내용:** 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시

**단계:** 출력

**내용:** 알림·변경 이력·로컬 진단 기록


### LEVEL 3 · 결과와 실패를 확인하기

변경 전·후 모델과 추론 강도, 공개된 이유, 관측 시각과 근거 수준을 함께 읽습니다. 기록되지 않은 값은 미확인으로 남깁니다. 로컬 기록은 서버 모델 신원 증명이 아닙니다.

**상황:** 알림이 나타나지 않음

**확인할 내용:** 감시하는 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 확인합니다. 최초 기준선 읽기와 새 변경 감지는 다릅니다.

**상황:** 자산 또는 글꼴 오류

**확인할 내용:** 이 차수에서 참조하는 assets와 라이선스를 준비합니다. 소스 이력에는 과거 대용량 프레임 자산이 없을 수 있습니다.

**상황:** 이유 또는 이전값이 없음

**확인할 내용:** 원문 기록에 해당 필드가 있는지 확인합니다. 누락된 동기를 추정해서 채우지 않습니다.


### LEVEL 3 · 실행 전 대조할 차수 조건

모델과 추론 강도의 이전·현재를 각각 두 칸으로 보여 주고 쉬운 추론 강도 이름을 사용합니다. 사용 한도 요약과 큰 변경 제목의 화면 구성을 정리합니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

Codex App Server의 `account/rateLimits/read`를 읽기 전용으로 조회합니다. 표시값은 남은 토큰 개수가 아니라 계정 사용 한도 비율입니다.

[자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)

<a id="reading-level-4"></a>
## LEVEL 4 - Advanced

### LEVEL 4 · 설계 의도와 검토 경계

모델과 추론 강도의 이전·현재를 각각 두 칸으로 보여 주고 쉬운 추론 강도 이름을 사용합니다. 사용 한도 요약과 큰 변경 제목의 화면 구성을 정리합니다.

모델과 추론 강도의 이전·현재를 각각 두 칸으로 보여 주고 쉬운 추론 강도 이름을 사용합니다. 사용 한도 요약과 큰 변경 제목의 화면 구성을 정리합니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다.

Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다.

실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다.

Codex App Server의 `account/rateLimits/read`를 읽기 전용으로 조회합니다. 표시값은 남은 토큰 개수가 아니라 계정 사용 한도 비율입니다.

### LEVEL 4 · 이 차수 구현의 실제 근거

| 내용 |
| --- |
| **파일:** [src/app.py](src/app.py)<br>**원문에 정의된 역할·구성:** Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용. |
| **파일:** [src/notifier.py](src/notifier.py)<br>**원문에 정의된 역할·구성:** 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다. |
| **파일:** [src/core.py](src/core.py)<br>**원문에 정의된 역할·구성:** 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용. |
| **파일:** [src/theme.py](src/theme.py)<br>**원문에 정의된 역할·구성:** 앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다. |
| **파일:** [src/usage.py](src/usage.py)<br>**원문에 정의된 역할·구성:** Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다. |
| **파일:** [src/visuals.py](src/visuals.py)<br>**원문에 정의된 역할·구성:** 실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다. |

**단계:** 입력

**내용:** 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

**단계:** 처리

**내용:** 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시

**단계:** 출력

**내용:** 알림·변경 이력·로컬 진단 기록


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

| 내용 |
| --- |
| **정의:** [`operation_record`](src/app.py#L33)<br>**소스에 적힌 역할:** 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다. |
| **정의:** [`short_reason`](src/app.py#L86)<br>**소스에 적힌 역할:** 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |
| **정의:** [`QuitGuard`](src/app.py#L1005)<br>**소스에 적힌 역할:** 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L1363)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L1364)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L1365)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--usage-smoke-test`](src/app.py#L1366)

**코드의 선언:** `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`

**설정·옵션:** [`--smoke-report`](src/app.py#L1367)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L1368)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L1369)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L72)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


**거부 조건:** [`not lock.tryLock(100)`](src/app.py#L1394)

**오류 메시지:** 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

**거부 조건:** [`not isinstance(value, dict)`](src/app.py#L157)

**오류 메시지:** 앱 설정은 JSON 객체여야 합니다.

**거부 조건:** [`not path.is_dir()`](src/app.py#L820)

**오류 메시지:** 존재하는 sessions 폴더를 선택하세요.

**거부 조건:** [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L825)

**오류 메시지:** 존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.

**거부 조건:** [`self.plan is None`](src/app.py#L968)

**오류 메시지:** 새 미리보기가 필요합니다.

**거부 조건:** [`not receipts`](src/app.py#L980)

**오류 메시지:** 앱이 만든 적용 백업이 없습니다.


#### LEVEL 4 · [src/core.py](src/core.py)

| 내용 |
| --- |
| **정의:** [`read_jsonl_tail`](src/core.py#L18)<br>**소스에 적힌 역할:** 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| **정의:** [`title_catalog`](src/core.py#L55)<br>**소스에 적힌 역할:** 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| **정의:** [`resolve_title`](src/core.py#L73)<br>**소스에 적힌 역할:** 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| **정의:** [`safe_path`](src/core.py#L97)<br>**소스에 적힌 역할:** 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 내용 |
| --- |
| **설정·옵션:** [`MAX_TEXT_BYTES`](src/core.py#L9)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`BEGIN`](src/core.py#L10)<br>**코드의 선언:** `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| **설정·옵션:** [`END`](src/core.py#L11)<br>**코드의 선언:** `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

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

| 내용 |
| --- |
| **정의:** [`atomic_json`](src/notifier.py#L32)<br>**소스에 적힌 역할:** 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다. |
| **정의:** [`source_datetime`](src/notifier.py#L62)<br>**소스에 적힌 역할:** 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다. |
| **정의:** [`duplicate_record`](src/notifier.py#L184)<br>**소스에 적힌 역할:** 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다. |
| **정의:** [`settings_record`](src/notifier.py#L195)<br>**소스에 적힌 역할:** 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다. |
| **정의:** [`lookup_parent_reason`](src/notifier.py#L335)<br>**소스에 적힌 역할:** 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| **정의:** [`enrich_event`](src/notifier.py#L382)<br>**소스에 적힌 역할:** 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 내용 |
| --- |
| **설정·옵션:** [`--sessions`](src/notifier.py#L636)<br>**코드의 선언:** `type=Path; default=Path.home() / '.codex/sessions'` |
| **설정·옵션:** [`--work`](src/notifier.py#L637)<br>**코드의 선언:** `type=Path; default=ROOT / 'work'` |
| **설정·옵션:** [`ROOT`](src/notifier.py#L17)<br>**코드의 선언:** `정의=Path(__file__).resolve().parents[1]` |
| **설정·옵션:** [`APP_ID`](src/notifier.py#L18)<br>**코드의 선언:** `정의='Yunseok.Codex.ModelChangeNotifier'` |
| **설정·옵션:** [`READ_BYTES`](src/notifier.py#L19)<br>**코드의 선언:** `정의=512 * 1024` |
| **설정·옵션:** [`MAX_RECORD`](src/notifier.py#L20)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`MAX_FILES`](src/notifier.py#L21)<br>**코드의 선언:** `정의=4096` |
| **설정·옵션:** [`LOG_BYTES`](src/notifier.py#L22)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`POLL_READ_BYTES`](src/notifier.py#L23)<br>**코드의 선언:** `정의=8 * 1024 * 1024` |
| **설정·옵션:** [`MAX_PENDING`](src/notifier.py#L24)<br>**코드의 선언:** `정의=256` |
| **설정·옵션:** [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25)<br>**코드의 선언:** `정의=0.2` |

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

| 내용 |
| --- |
| **정의:** [`MonochromeStyle`](src/theme.py#L51)<br>**소스에 적힌 역할:** 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다. |
| **정의:** [`KoreanDialogs`](src/theme.py#L76)<br>**소스에 적힌 역할:** 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다. |
| **정의:** [`DialogLayout`](src/theme.py#L92)<br>**소스에 적힌 역할:** 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다. |

#### LEVEL 4 · [src/usage.py](src/usage.py)

| 내용 |
| --- |
| **정의:** [`number`](src/usage.py#L16)<br>**소스에 적힌 역할:** 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다. |
| **정의:** [`normalize_limits`](src/usage.py#L35)<br>**소스에 적힌 역할:** 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다. |
| **정의:** [`discover_codex`](src/usage.py#L69)<br>**소스에 적힌 역할:** 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다. |

| 내용 |
| --- |
| **설정·옵션:** [`MAX_BYTES`](src/usage.py#L12)<br>**코드의 선언:** `정의=1024 * 1024` |
| **설정·옵션:** [`KST`](src/usage.py#L13)<br>**코드의 선언:** `정의=timezone(timedelta(hours=9))` |

| 내용 |
| --- |
| **거부 조건:** [`not isinstance(message, dict)`](src/usage.py#L226)<br>**오류 메시지:** 객체가 아닌 응답 |

#### LEVEL 4 · [src/visuals.py](src/visuals.py)

| 내용 |
| --- |
| **정의:** [`rotate_point`](src/visuals.py#L8)<br>**소스에 적힌 역할:** X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다. |
| **정의:** [`orbit_segments`](src/visuals.py#L23)<br>**소스에 적힌 역할:** 세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다. |
| **정의:** [`draw_orbit`](src/visuals.py#L55)<br>**소스에 적힌 역할:** 장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다. |

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
<a id="reading-level-5"></a>
## LEVEL 5 - Expert

기존의 전체 설명·표·코드·함수 참조·파일별 비교는 아래에 그대로 이어집니다. [자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)
<!-- reading-levels:end -->



[프로젝트](../../README.md) · [전체 차수](../../docs/REVISION_INDEX.md) · [원본 자료](.) · [← 이전: 10차](../10%EC%B0%A8/README.md) · [다음: 12차 →](../12%EC%B0%A8/README.md)

<a name="-목적과-이-차수의-역할"></a>
## 목적과 이 차수의 역할

모델과 추론 강도의 이전·현재를 각각 두 칸으로 보여 주고 쉬운 추론 강도 이름을 사용합니다. 사용 한도 요약과 큰 변경 제목의 화면 구성을 정리합니다.

<a name="features"></a>

<a name="-핵심-기능과-보존-범위"></a>
## 핵심 기능과 보존 범위

**항목:** 1

**이 차수에서 확인할 내용:** 모델과 추론 강도의 이전·현재를 각각 두 칸으로 보여 주고 쉬운 추론 강도 이름을 사용합니다. 사용 한도 요약과 큰 변경 제목의 화면 구성을 정리합니다.

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

**단계:** 입력

**내용:** 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

**단계:** 처리

**내용:** 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시

**단계:** 출력

**내용:** 알림·변경 이력·로컬 진단 기록


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

| 내용 |
| --- |
| **경로:** [src/](src)<br>**자료 종류:** 하위 자료 폴더 |
| **경로:** [README.md](README.md)<br>**자료 종류:** MD 파일 |
| **경로:** [requirements.txt](requirements.txt)<br>**자료 종류:** TXT 파일 |
| **경로:** [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json)<br>**자료 종류:** JSON 파일 |
| **경로:** [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md)<br>**자료 종류:** MD 파일 |
| **경로:** [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json)<br>**자료 종류:** JSON 파일 |
| **경로:** [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff)<br>**자료 종류:** DIFF 파일 |

<a name="-주요-모듈과-코드-읽기"></a>
## 주요 모듈과 코드 읽기

| 내용 |
| --- |
| **파일:** [src/app.py](src/app.py)<br>**원문에 정의된 역할·구성:** Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용. |
| **파일:** [src/notifier.py](src/notifier.py)<br>**원문에 정의된 역할·구성:** 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다. |
| **파일:** [src/core.py](src/core.py)<br>**원문에 정의된 역할·구성:** 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용. |
| **파일:** [src/theme.py](src/theme.py)<br>**원문에 정의된 역할·구성:** 앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다. |
| **파일:** [src/usage.py](src/usage.py)<br>**원문에 정의된 역할·구성:** Codex App Server의 계정 사용 한도를 읽기 전용으로 조회합니다. |
| **파일:** [src/visuals.py](src/visuals.py)<br>**원문에 정의된 역할·구성:** 실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다. |

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

| 내용 |
| --- |
| **정의:** [`operation_record`](src/app.py#L33)<br>**소스에 적힌 역할:** 대화 본문 없이 시작·감시 단계와 실제 프로세스 경로를 기록합니다. |
| **정의:** [`short_reason`](src/app.py#L86)<br>**소스에 적힌 역할:** 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |
| **정의:** [`QuitGuard`](src/app.py#L1005)<br>**소스에 적힌 역할:** 직접 앱 종료 요청도 감시 작업자의 비동기 정리 뒤에 처리합니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L1363)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L1364)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L1365)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--usage-smoke-test`](src/app.py#L1366)

**코드의 선언:** `action='store_true'; help='실제 계정 잔량과 표시를 조회한 뒤 종료'`

**설정·옵션:** [`--smoke-report`](src/app.py#L1367)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L1368)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L1369)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L72)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


**거부 조건:** [`not lock.tryLock(100)`](src/app.py#L1394)

**오류 메시지:** 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

**거부 조건:** [`not isinstance(value, dict)`](src/app.py#L157)

**오류 메시지:** 앱 설정은 JSON 객체여야 합니다.

**거부 조건:** [`not path.is_dir()`](src/app.py#L820)

**오류 메시지:** 존재하는 sessions 폴더를 선택하세요.

**거부 조건:** [`chosen_exe and (not Path(chosen_exe).is_file() or Path(chosen_exe).suffix.lower() != '.exe')`](src/app.py#L825)

**오류 메시지:** 존재하는 Codex EXE를 선택하거나 비워 자동 탐색하세요.

**거부 조건:** [`self.plan is None`](src/app.py#L968)

**오류 메시지:** 새 미리보기가 필요합니다.

**거부 조건:** [`not receipts`](src/app.py#L980)

**오류 메시지:** 앱이 만든 적용 백업이 없습니다.


### [src/core.py](src/core.py)

| 내용 |
| --- |
| **정의:** [`read_jsonl_tail`](src/core.py#L18)<br>**소스에 적힌 역할:** 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| **정의:** [`title_catalog`](src/core.py#L55)<br>**소스에 적힌 역할:** 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| **정의:** [`resolve_title`](src/core.py#L73)<br>**소스에 적힌 역할:** 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| **정의:** [`safe_path`](src/core.py#L97)<br>**소스에 적힌 역할:** 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 내용 |
| --- |
| **설정·옵션:** [`MAX_TEXT_BYTES`](src/core.py#L9)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`BEGIN`](src/core.py#L10)<br>**코드의 선언:** `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| **설정·옵션:** [`END`](src/core.py#L11)<br>**코드의 선언:** `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

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

| 내용 |
| --- |
| **정의:** [`atomic_json`](src/notifier.py#L32)<br>**소스에 적힌 역할:** 같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다. |
| **정의:** [`source_datetime`](src/notifier.py#L62)<br>**소스에 적힌 역할:** 시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다. |
| **정의:** [`duplicate_record`](src/notifier.py#L184)<br>**소스에 적힌 역할:** 원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다. |
| **정의:** [`settings_record`](src/notifier.py#L195)<br>**소스에 적힌 역할:** 자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다. |
| **정의:** [`lookup_parent_reason`](src/notifier.py#L335)<br>**소스에 적힌 역할:** 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| **정의:** [`enrich_event`](src/notifier.py#L382)<br>**소스에 적힌 역할:** 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 내용 |
| --- |
| **설정·옵션:** [`--sessions`](src/notifier.py#L636)<br>**코드의 선언:** `type=Path; default=Path.home() / '.codex/sessions'` |
| **설정·옵션:** [`--work`](src/notifier.py#L637)<br>**코드의 선언:** `type=Path; default=ROOT / 'work'` |
| **설정·옵션:** [`ROOT`](src/notifier.py#L17)<br>**코드의 선언:** `정의=Path(__file__).resolve().parents[1]` |
| **설정·옵션:** [`APP_ID`](src/notifier.py#L18)<br>**코드의 선언:** `정의='Yunseok.Codex.ModelChangeNotifier'` |
| **설정·옵션:** [`READ_BYTES`](src/notifier.py#L19)<br>**코드의 선언:** `정의=512 * 1024` |
| **설정·옵션:** [`MAX_RECORD`](src/notifier.py#L20)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`MAX_FILES`](src/notifier.py#L21)<br>**코드의 선언:** `정의=4096` |
| **설정·옵션:** [`LOG_BYTES`](src/notifier.py#L22)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`POLL_READ_BYTES`](src/notifier.py#L23)<br>**코드의 선언:** `정의=8 * 1024 * 1024` |
| **설정·옵션:** [`MAX_PENDING`](src/notifier.py#L24)<br>**코드의 선언:** `정의=256` |
| **설정·옵션:** [`POLL_INTERVAL_SECONDS`](src/notifier.py#L25)<br>**코드의 선언:** `정의=0.2` |

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

| 내용 |
| --- |
| **정의:** [`MonochromeStyle`](src/theme.py#L51)<br>**소스에 적힌 역할:** 파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다. |
| **정의:** [`KoreanDialogs`](src/theme.py#L76)<br>**소스에 적힌 역할:** 별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다. |
| **정의:** [`DialogLayout`](src/theme.py#L92)<br>**소스에 적힌 역할:** 앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다. |

### [src/usage.py](src/usage.py)

| 내용 |
| --- |
| **정의:** [`number`](src/usage.py#L16)<br>**소스에 적힌 역할:** 불리언·문자열·비유한 숫자를 한도 수치로 해석하지 않습니다. |
| **정의:** [`normalize_limits`](src/usage.py#L35)<br>**소스에 적힌 역할:** 공식 복수 버킷을 우선하며 없는 기간/수치는 만들어 넣지 않습니다. |
| **정의:** [`discover_codex`](src/usage.py#L69)<br>**소스에 적힌 역할:** 사용자 선택, PATH, 공식 데스크톱 번들 위치 순으로 EXE만 찾습니다. |

| 내용 |
| --- |
| **설정·옵션:** [`MAX_BYTES`](src/usage.py#L12)<br>**코드의 선언:** `정의=1024 * 1024` |
| **설정·옵션:** [`KST`](src/usage.py#L13)<br>**코드의 선언:** `정의=timezone(timedelta(hours=9))` |

| 내용 |
| --- |
| **거부 조건:** [`not isinstance(message, dict)`](src/usage.py#L226)<br>**오류 메시지:** 객체가 아닌 응답 |

### [src/visuals.py](src/visuals.py)

| 내용 |
| --- |
| **정의:** [`rotate_point`](src/visuals.py#L8)<br>**소스에 적힌 역할:** X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다. |
| **정의:** [`orbit_segments`](src/visuals.py#L23)<br>**소스에 적힌 역할:** 세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다. |
| **정의:** [`draw_orbit`](src/visuals.py#L55)<br>**소스에 적힌 역할:** 장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다. |

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

10차에서 11차로 이어지는 실제 파일 비교입니다.

[전체 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff)

추가·수정·삭제, 주석·공백·개행과 바이너리 크기·해시는 연결된 원래 비교 자료에서 확인합니다.

<details>
<summary>파일별 비교·크기·해시 자세히 보기</summary>

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

- **수정** `src/app.py`: 이전 70594바이트, SHA-256 `b6eb55394e32a9270f44b0d717f9a69b851f93a09782821386d7eb2e351b58e0`; 현재 77206바이트, SHA-256 `aa9ab7a95f5b34f136ad7633b540290a6e1b3583e6bdebcccd9f71252e53204a`.

- **수정** `src/theme.py`: 이전 8014바이트, SHA-256 `6ac4f4457b8a7f2cbaddeb15e8a6858bc6e506eb962175099565d5af970e74d0`; 현재 8578바이트, SHA-256 `e3b834f71c3af854ef23aa411ddeec07c959a6547c219d318b60b627445d3243`.

- **수정** `src/visuals.py`: 이전 6995바이트, SHA-256 `60af8348b66e84a9c37c11f3c700579db137fd6b5b5ef2ad25f748253071e05e`; 현재 7287바이트, SHA-256 `6c1102f74fb8b1c9cd551ac05931465852e5815a088421aec11ec60e8fb88132`.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

</details>

[프로젝트](../../README.md) · [전체 차수](../../docs/REVISION_INDEX.md) · [원본 자료](.) · [← 이전: 10차](../10%EC%B0%A8/README.md) · [다음: 12차 →](../12%EC%B0%A8/README.md)
