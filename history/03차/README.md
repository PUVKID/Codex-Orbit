<div align="center">

<a name="-codex-orbit--3차"></a>
# Codex Orbit·3차

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

**기술 분류:** Windows 데스크톱 · Python · PySide6

[핵심 기능](#features) · [사용 흐름](#usage) · [자료 구성](#structure) · [준비와 실행](#setup) · [결과 읽기](#results) · [직전 변경](#changes)

</div>
<!-- reading-levels:start -->
[LEVEL 1 - Beginner](#reading-level-1) · [LEVEL 2 - Explorer](#reading-level-2) · [LEVEL 3 - Practitioner](#reading-level-3) · [LEVEL 4 - Advanced](#reading-level-4) · [LEVEL 5 - Expert](#reading-level-5)

프로젝트 전체의 설명은 [LEVEL 1 - Beginner](../../docs/%EC%9D%BD%EA%B8%B0%EC%95%88%EB%82%B4/%EB%A0%88%EB%B2%A81.md)부터 [LEVEL 5 - Expert](../../docs/%EC%9D%BD%EA%B8%B0%EC%95%88%EB%82%B4/%EB%A0%88%EB%B2%A85.md)까지 같은 범위로 연결됩니다.

<a id="reading-level-1"></a>
## LEVEL 1 - Beginner

### LEVEL 1 · 이 자료가 하는 일과 달라진 점

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

### LEVEL 1 · 실제 동작을 따라 읽기

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

JSONL은 한 줄마다 하나의 JSON 기록을 담은 파일입니다. CLI는 명령어와 옵션을 입력해 프로그램을 실행하는 방식입니다.

입력 — 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

처리 — 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시

출력 — 알림·변경 이력·로컬 진단 기록

### LEVEL 1 · 준비하고 확인할 것

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존 본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다.

자산과 의존성을 준비한 이 차수 폴더에서 `python src/app.py`를 실행합니다. history 소스만으로 과거 배포 EXE와 동일한 화면·자산이 모두 복원되지는 않습니다.

#### LEVEL 1 · 이 보관본의 의존성 목록

[requirements.txt](requirements.txt)의 실제 항목입니다. 외부 실행 도구와 GPU 드라이버는 별도로 준비합니다.

```text
PySide6-Essentials==6.12.0
PyInstaller==6.22.3
```

#### LEVEL 1 · 소스에서 제공하는 CLI 옵션

**진입 소스:** [app.py](src/app.py)

**정의된 옵션 이름:** `--data-dir`, `--sessions`, `--smoke-test`, `--smoke-report`, `--show-details`, `--show-event`

**진입 소스:** [notifier.py](src/notifier.py)

**정의된 옵션 이름:** `--sessions`, `--work`


각 옵션의 기본 값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 1 · [src/app.py](src/app.py)

| 정의 | 역할 |
| --- | --- |
| [`short_reason`](src/app.py#L56) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L723)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L724)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L725)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--smoke-report`](src/app.py#L726)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L727)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L728)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L42)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


| 거부 조건 | 오류 메시지 |
| --- | --- |
| [`not lock.tryLock(100)`](src/app.py#L743) | 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다. |
| [`not isinstance(value, dict)`](src/app.py#L114) | 앱 설정은 JSON 객체여야 합니다. |
| [`not path.is_dir()`](src/app.py#L495) | 존재하는 sessions 폴더를 선택하세요. |
| [`self.plan is None`](src/app.py#L599) | 새 미리보기가 필요합니다. |
| [`not receipts`](src/app.py#L611) | 앱이 만든 적용 백업이 없습니다. |

#### LEVEL 1 · [src/core.py](src/core.py)

| 정의 | 역할 |
| --- | --- |
| [`read_jsonl_tail`](src/core.py#L18) | 물리적 LF만 나누며 잘 린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
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
| [`lookup_parent_reason`](src/notifier.py#L219) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L266) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L506) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L507) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L17) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L18) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L19) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L20) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L21) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L22) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L23) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L24) | `정의=256` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L54)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') != 2`](src/notifier.py#L57)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L59)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L61)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L315)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L378)

**오류 메시지:** 명시 알림 파일 상한 초과


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


### LEVEL 1·3차의 구체적인 기능과 확인

알림이 빨리 사라져 내용을 놓치지 않도록 직접 닫을 때까지 남기는 설정을 다루는 단계입니다. 알림 내용에 맞춰 높이를 계산하고 기록 종류·상세 설명·감시 상태를 나눠 보여 줍니다. 이유는 실제 기록에서 가져오며, 적혀 있지 않은 생각이나 동기를 만들어 넣지 않습니다.

**입력은 기록 파일, 출력은 알림과 이력입니다.** Codex의 sessions 폴더에는 이 사용자의 작업 기록이 쌓입니다.

앱이 새 기록을 읽으면 이전·이후 모델과 추론 강도, 적혀 있는 이유를 정리해 보여 줍니다.

JSON은 항목 이름과 값을 짝으로 저장하는 자료 형식입니다.

처음 읽은 기록을 출발점으로 삼는 것과 그 뒤 새로 생긴 변경을 알리는 것은 다릅니다.

Windows에서 이 차수의 [requirements.txt](requirements.txt)에 맞는 Python 의존성과 해당 자산을 준비한 뒤 **이 차수 폴더에서** `python src/app.py`를 실행합니다.

현재 루트의 assets가 과거 모든 차수와 호환되는 것은 아니며, history 소스만으로 과거 EXE의 화면·자산 전체가 복원되는 것도 아닙니다.

확인 순서는 **같은 차수 자료 준비 → 감시 경로 확인 → 새 기록과 알림·상세 대조 → 누락값과 오류 확인**입니다. 예를 들어 기록에 모델 변경이 남았다면 알림의 이전·현재 값과 상세 이력을 비교합니다. 원문에 이유나 이전값이 없다면 모르는 상태로 읽고 채워 넣지 않습니다.

**함께 준비할 도구 버전**: PySide6-Essentials ==6.12.0·PyInstaller ==6.22.3. PySide6는 창을 만드는 도구이고 PyInstaller는 실행 파일을 묶는 도구입니다. 외부 실행 도구·GPU 드라이버는 별도 조건입니다.

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

**실제 입력·설정과 기본값**

아래 이름은 설정을 소스에서 찾기 위한 표지입니다.

각 항목의 역할·단위·적용 상황을 먼저 읽고 뒤의 원문 선언으로 정확한 숫자를 확인합니다.

식에 1024가 쓰이면 바이트 단위 크기 계산이며 1 KiB =1,024 바이트, 1 MiB =1,048,576 바이트입니다.

이 설명은 설정을 임의로 바꾸라는 실행 지시가 아닙니다.

- [`--data-dir`](src/app.py#L723) (src/app.py)

  앱 설정·이력을 저장할 폴더를 고릅니다.

기본은 LOCALAPPDATA 아래 CodexOrbit이며 그 환경 값이 없으면 사용자 홈을 기준으로 합니다.

같은 폴더 중복 실행 잠금과 연결됩니다.

원문 선언: `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`.

- [`--sessions`](src/app.py#L724) (src/app.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path`.

- [`--smoke-test`](src/app.py#L725) (src/app.py)

  점검 실행을 켜는 스위치입니다. 숫자를 넣는 옵션이 아니라 이름을 붙여 켭니다. 옵션 존재 자체가 검사를 실행해 통과했다는 증거는 아닙니다. 원문 선언: `action='store_true'`.

- [`--smoke-report`](src/app.py#L726) (src/app.py)

  점검 결과를 저장할 파일 경로입니다. 폴더를 고르는 세션 옵션과 달리 보고서 파일을 지정합니다. 원문 선언: `type=Path`.

- [`--show-details`](src/app.py#L727) (src/app.py)

  처음부터 상세창을 보여 주는 스위치입니다. 숨겨진 원문 값을 새로 만들어 주는 기능이 아닙니다. 원문 선언: `action='store_true'`.

- [`--show-event`](src/app.py#L728) (src/app.py)

  이미 있는 이력의 사건 ID 또는 대상 ID를 지정해 다시 표시합니다. 실제 저장된 ID와 맞춰 읽고 새 사건 생성과 구분합니다. 원문 선언: `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`.

- [`ROLE_LABELS`](src/app.py#L42) (src/app.py)

  역할 코드와 사용자용 한글 이름의 대응 표입니다.

예를 들어 build는 구현, verifier는 독립 검증으로 읽습니다.

화면 설명을 바꾸는 표이며 서버 모델을 바꾸는 설정은 아닙니다.

원문 선언: `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`.

- [`MAX_TEXT_BYTES`](src/core.py#L9) (src/core.py)

  읽거나 적용할 지침 문서의 크기 상한입니다. 원문·추가 지침·최종 결과의 제한과 연결되며 큰 문서 쓰기를 무제한 허용하지 않습니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`BEGIN`](src/core.py#L10) (src/core.py)

  앱이 관리하는 지침 구간이 시작되는 정확한 표시 문자열입니다. 문서의 나머지 부분과 구분하기 때문에 추가할 지침 안에 같은 표식을 넣지 못하게 합니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'`.

- [`END`](src/core.py#L11) (src/core.py)

  앱 관리 구간이 끝나는 정확한 표시 문자열입니다. 시작 표시보다 먼저 있거나 여러 번 있으면 원래 구간이 불명확해 적용을 거부하는 조건과 연결됩니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'`.

- [`--sessions`](src/notifier.py#L506) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L507) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L17) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L18) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L19) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L20) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L21) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대 값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L22) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L23) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료 량을 제한합니다. 파일 하나의 상한과 별개 인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L24) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개 수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

**처리 책임과 원문에 명시된 함수 동작**

- [`short_reason`](src/app.py#L56) (src/app.py)

  변경 알림에서 짧은 이유가 필요한 경우, 기록에 명시된 이유 또는 배정·선택 목적 문장을 우선 골라 짧게 보여 줍니다 원문에 있는 이유를 읽을 수 있고 없는 이유는 만들어지지 않습니다. 공개된 문장과 앱이 추측한 동기를 혼동하지 않도록 하기 위해서입니다

- [`read_jsonl_tail`](src/core.py#L18) (src/core.py)

  기록 파일의 끝부분만 읽어 첫 줄이나 마지막 줄이 중간에 잘려 들어온 경우, 파일에서 실제 줄바꿈을 뜻하는 LF 바이트로만 한 건씩 나누고 완성되지 않은 양끝 조각은 해석하지 않습니다.

온전한 줄만 기록 한 건으로 읽습니다.

예를 들어 읽어 온 끝에 {"model": 뒤까지만 있고 닫는 부분이 없다면 그 조각을 새 변경 한 건으로 해석하지 않습니다.

이 문자열은 잘린 자료를 설명하는 예시이며 실제 세션을 수정하라는 지시가 아닙니다.

문장 안의 다른 줄바꿈 모양 문자나 반쪽 기록을 새 사건으로 잘못 세지 않기 위해서입니다

- [`title_catalog`](src/core.py#L55) (src/core.py)

  같은 작업에 제목 정보가 여러 출처로 남아 있는 경우, 공식 앱에서 확인해 저장한 제목과 컴퓨터 안의 제목 목록이 어디서 왔는지 함께 보존합니다. 제목과 그 제목을 얻은 출처를 대조할 수 있습니다. 제목 문자열만 같다는 이유로 근거 수준까지 같다고 보지 않기 위해서입니다

- [`resolve_title`](src/core.py#L73) (src/core.py)

  한 채팅에서 별도 자식 작업이 실행된 기록을 표시하는 경우, 실제 부모 채팅 제목과 자식 작업명을 서로 다른 정보로 다룹니다 어느 대화에서 생긴 어떤 작업인지 구별됩니다. 작업명을 새 채팅 제목이나 다른 부모 채팅으로 오해하지 않기 위해서입니다

- [`safe_path`](src/core.py#L97) (src/core.py)

  지침을 적용할 파일이나 그 파일에 이르는 상위 폴더가 다른 곳으로 연결된 경우, 파일 자체뿐 아니라 이미 존재하는 상위 폴더까지 확인해 바로 가기처럼 다른 위치로 보내는 링크·재분석 지점을 거부합니다.

연결을 통해 의도 밖의 위치를 수정하는 경로는 허용되지 않습니다.

예를 들어 선택한 작업 폴더가 실은 다른 폴더로 보내는 연결이라면, 그 안의 AGENTS.md를 선택해도 그 연결을 따라 쓰기를 진행하지 않습니다.

겉으로 고른 폴더와 실제 쓰는 위치가 달라지는 일을 막기 위해서입니다

- [`lookup_parent_reason`](src/notifier.py#L219) (src/notifier.py)

  자식 사건의 배정 이유가 큰 부모 기록에 남아 있는 경우, 부모 기록의 최근 공개 호출만 정해진 양 안에서 찾아보고 정기 감시의 읽기 위치는 그대로 둡니다 이유를 찾는 보조 읽기가 다음 감시 출발점을 옮기지 않습니다. 부모 이유를 찾다가 새 사건을 건너뛰거나 전체 큰 파일을 무제한 읽지 않기 위해서입니다

- [`enrich_event`](src/notifier.py#L266) (src/notifier.py)

  이력이 이미 전달됐지만 첫 배정 이유가 뒤늦게 확인된 경우, 정확히 연결된 사건의 첫 배정 이유만 기존 이력에 덧붙이고 새 알림은 띄우지 않습니다. 같은 사건의 설명이 보강되고 중복 알림은 만들어지지 않습니다. 이유 보강과 새 모델 변경 사건을 구분하기 위해서입니다

**멈추거나 거부되는 조건과 읽는 방법**

- 오류 “같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.”

  같은 저장 폴더를 이미 다른 Codex Orbit가 쓰거나 잠금 파일에 접근할 수 없으면 시작을 거부합니다.

한 설정·상태 파일을 두 실행이 동시에 바꾸지 않도록하며, 이 메시지만으로 어느 쪽 원인인지 확정하지 않습니다.

정확한 조건은 [`not lock.tryLock(100)`](src/app.py#L743) (src/app.py)에서 확인할 수 있습니다.

- 오류 “앱 설정은 JSON 객체여야 합니다.”

  앱 설정이 항목 이름과 값을 가진 사전이어야 합니다. 예를 들어 목록만 저장돼 있으면 설정 이름으로 값을 찾을 수 없어 거부합니다. 정확한 조건은 [`not isinstance(value, dict)`](src/app.py#L114) (src/app.py)에서 확인할 수 있습니다.

- 오류 “존재하는 sessions 폴더를 선택하세요.”

  선택한 기록 경로가 실제 폴더가 아니면 거부합니다. 오타가 있는 위치나 파일 하나를 감시 폴더로 잘못 지정했는지 먼저 확인합니다. 정확한 조건은 [`not path.is_dir()`](src/app.py#L495) (src/app.py)에서 확인할 수 있습니다.

- 오류 “새 미리보기가 필요합니다.”

  아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다. 대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다. 정확한 조건은 [`self.plan is None`](src/app.py#L599) (src/app.py)에서 확인할 수 있습니다.

- 오류 “앱이 만든 적용 백업이 없습니다.”

  앱이 지침 적용 전에 만든 백업이 없으면 그 백업을 이용한 되돌리기를 할 수 없습니다. 임의의 다른 문서를 원래 내용이라고 추정하지 않습니다. 정확한 조건은 [`not receipts`](src/app.py#L611) (src/app.py)에서 확인할 수 있습니다.

- 오류 “문서가 2 MiB 상한을 초과했습니다.”

  지침 원본 문서가 2 MiB보다 크면 읽기 범위를 벗어나 거부합니다. 작은 설명으로 예상한 입력을 대용량 파일 읽기로 확대하지 않는 제한입니다. 정확한 조건은 [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112) (src/core.py)에서 확인할 수 있습니다.

- 오류 “제목 캐시 구조가 올바르지 않습니다.”

  보관한 제목 목록이 기대한 이름별 저장 형식이 아니면 거부합니다.

제목의 출처와 연결을 알 수 없는데도 빈 목록으로 자동 덮어쓰지 않습니다.

정확한 조건은 [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64) (src/core.py)에서 확인할 수 있습니다.

- 오류 “적용 대상은 AGENTS.md 파일이어야 합니다.”

  선택한 파일 이름이 AGENTS.md가 아니면 적용하지 않습니다. 다른 문서나 데이터 파일을 지침 대상이라고 잘못 수정하지 않기 위한 이름 확인입니다. 정확한 조건은 [`target.name.lower() != 'agents.md'`](src/core.py#L123) (src/core.py)에서 확인할 수 있습니다.

- 오류 “대상 폴더가 존재하지 않습니다.”

  대상 파일을 둘 상위 폴더가 없으면 적용하지 않습니다. 앱이 의도하지 않은 위치의 폴더를 새로 만들어 결과를 숨기는 대신 선택 경로부터 확인하게 합니다. 정확한 조건은 [`not target.parent.is_dir()`](src/core.py#L125) (src/core.py)에서 확인할 수 있습니다.

- 오류 “대상은 2 MiB 이하의 일반 파일이어야 합니다.”

  기존 대상이 일반 파일이 아니거나 2 MiB보다 크면 적용하지 않습니다.

폴더·특수 파일을 문서처럼 취급하거나 대용량 원본을 바꾸지 않게합니다.

정확한 조건은 [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127) (src/core.py)에서 확인할 수 있습니다.

- 오류 “빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.”

  내용이 공백뿐이거나 새로 붙일 지침이 2 MiB보다 크면 거부합니다.

아무 내용 없는 적용이나 과도한 추가 입력을 정상 변경으로 보지 않습니다.

정확한 조건은 [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134) (src/core.py)에서 확인할 수 있습니다.

- 오류 “지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.”

  추가 지침 안에 앱의 시작·끝 관리 표시가 들어 있으면 거부합니다. 내용 속 표시를 실제 관리 경계로 잘못 읽어 원문 구간을 혼동하지 않도록 합니다. 정확한 조건은 [`BEGIN in added or END in added`](src/core.py#L136) (src/core.py)에서 확인할 수 있습니다.

- 오류 “적용 결과가 2 MiB 상한을 초과합니다.”

  원본과 새 지침을 합친 최종 문서가 2 MiB보다 크면 쓰지 않습니다. 원본과 추가분이 각각 작더라도 합쳐진 결과는 별도 크기 제한을 만족해야 합니다. 정확한 조건은 [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150) (src/core.py)에서 확인할 수 있습니다.

- 오류 “대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.”

  아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다.

대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다.

정확한 조건은 [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157) (src/core.py)에서 확인할 수 있습니다.

- 오류 “미리보기 데이터가 변경되었습니다.”

  미리보기 계획 안의 원문·결과 바이트가 저장된 지문과 다르면 거부합니다.

사용자가 확인했던 변경 계획과 실제 쓸 내용이 같은지 확인하는 경계입니다.

정확한 조건은 [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177) (src/core.py)에서 확인할 수 있습니다.

- 오류 “유효한 앱 원문 백업이 아닙니다.”

  백업이 앱이 정한 백업 폴더 안의 정상 파일이 아니거나 크기 제한을 넘으면 복원에 쓰지 않습니다.

아무 파일이나 원래 문서라고 덮어쓰지 않기 위한 확인입니다.

정확한 조건은 [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197) (src/core.py)에서 확인할 수 있습니다.

- 오류 “백업 해시가 일치하지 않습니다.”

  백업 내용의 지문이 적용 때 기록한 원본 지문과 다르면 되돌리기를 거부합니다.

파일 이름이 같더라도 내용이 달라졌다면 안전한 원본으로 보지 않습니다.

정확한 조건은 [`digest(raw) != receipt['before_hash']`](src/core.py#L200) (src/core.py)에서 확인할 수 있습니다.

- 오류 “JSON 객체가 아닙니다.”

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다. 정확한 조건은 [`not isinstance(row, dict)`](src/core.py#L40) (src/core.py)에서 확인할 수 있습니다.

- 오류 “기존 관리구역 표식이 손상되었거나 중복되었습니다.”

  시작·끝 표시가 정확히 한 쌍이 아니거나 순서가 뒤집혔다면 적용할 구간이 불명확해 거부합니다.

여러 구간 중 임의의 하나를 골라 원문을 바꾸지 않습니다.

정확한 조건은 [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143) (src/core.py)에서 확인할 수 있습니다.

- 오류 “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”

  이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다.

큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다.

정확한 조건은 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L54) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.”

  옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다.

이를 새 관측 이력으로 자동 해석하지 않습니다.

명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다.

정확한 조건은 [`self.state.get('schema_version') != 2`](src/notifier.py#L57) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”

  저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다.

자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다.

정확한 조건은 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L59) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”

  어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다.

이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다.

정확한 조건은 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L61) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “JSON 객체가 아닙니다.”

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다.

예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다.

정확한 조건은 [`not isinstance(record, dict)`](src/notifier.py#L315) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “명시 알림 파일 상한 초과”

  명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다. 짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게하기 위한 크기 제한입니다. 정확한 조건은 [`path.stat().st_size &gt; 20000`](src/notifier.py#L378) (src/notifier.py)에서 확인할 수 있습니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다.

최초 기준 선 읽기와 새 변경은 다릅니다.

자산·글 꼴 오류라면 이 차수 assets와 라이선스를 대조합니다.

과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다.

이유·이전 값이 없으면 원 문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

2차 → 3차의 실제 파일 비교입니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **수정** [src/app.py](src/app.py): 이름 옆의 변화 종류를 기준으로 원래 파일과 달라진 내용을 읽습니다.

- **수정** [src/core.py](src/core.py): 이름 옆의 변화 종류를 기준으로 원래 파일과 달라진 내용을 읽습니다.

- **수정** [src/notifier.py](src/notifier.py): 이름 옆의 변화 종류를 기준으로 원래 파일과 달라진 내용을 읽습니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다.

원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다.

이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다.

Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.

<a id="reading-level-2"></a>
## LEVEL 2 - Explorer

### LEVEL 2 · 목적과 구성의 연결

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

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

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존 본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다.

자산과 의존성을 준비한 이 차수 폴더에서 `python src/app.py`를 실행합니다. history 소스만으로 과거 배포 EXE와 동일한 화면·자산이 모두 복원되지는 않습니다.

#### LEVEL 2 · 이 보관본의 의존성 목록

[requirements.txt](requirements.txt)의 실제 항목입니다. 외부 실행 도구와 GPU 드라이버는 별도로 준비합니다.

```text
PySide6-Essentials==6.12.0
PyInstaller==6.22.3
```

#### LEVEL 2 · 소스에서 제공하는 CLI 옵션

**진입 소스:** [app.py](src/app.py)

**정의된 옵션 이름:** `--data-dir`, `--sessions`, `--smoke-test`, `--smoke-report`, `--show-details`, `--show-event`

**진입 소스:** [notifier.py](src/notifier.py)

**정의된 옵션 이름:** `--sessions`, `--work`


각 옵션의 기본 값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 2 · [src/app.py](src/app.py)

| 정의 | 역할 |
| --- | --- |
| [`short_reason`](src/app.py#L56) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L723)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L724)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L725)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--smoke-report`](src/app.py#L726)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L727)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L728)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L42)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


| 거부 조건 | 오류 메시지 |
| --- | --- |
| [`not lock.tryLock(100)`](src/app.py#L743) | 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다. |
| [`not isinstance(value, dict)`](src/app.py#L114) | 앱 설정은 JSON 객체여야 합니다. |
| [`not path.is_dir()`](src/app.py#L495) | 존재하는 sessions 폴더를 선택하세요. |
| [`self.plan is None`](src/app.py#L599) | 새 미리보기가 필요합니다. |
| [`not receipts`](src/app.py#L611) | 앱이 만든 적용 백업이 없습니다. |

#### LEVEL 2 · [src/core.py](src/core.py)

| 정의 | 역할 |
| --- | --- |
| [`read_jsonl_tail`](src/core.py#L18) | 물리적 LF만 나누며 잘 린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
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
| [`lookup_parent_reason`](src/notifier.py#L219) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L266) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L506) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L507) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L17) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L18) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L19) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L20) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L21) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L22) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L23) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L24) | `정의=256` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L54)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') != 2`](src/notifier.py#L57)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L59)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L61)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L315)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L378)

**오류 메시지:** 명시 알림 파일 상한 초과


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


### LEVEL 2·3차의 구체적인 기능과 확인

알림 수명과 내용 배치는 연결되지만 별개의 조건입니다. 오래 남겨도 내용 높이가 부족하면 읽기 어려우므로 유지 설정과 높이 계산을 함께 봅니다. short_reason은 명시된 이유·배정 목적을 발췌하고, 기록 종류에 맞춰 표시 분기를 고릅니다.

**수집·해석·표시·보존**을 연결해 읽습니다. 로컬 JSONL의 관측 변경과 명시된 배정은 다른 종류의 근거입니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

Windows에서 이 차수의 [requirements.txt](requirements.txt)에 맞는 Python 의존성과 해당 자산을 준비한 뒤 **이 차수 폴더에서** `python src/app.py`를 실행합니다.

현재 루트의 assets가 과거 모든 차수와 호환되는 것은 아니며, history 소스만으로 과거 EXE의 화면·자산 전체가 복원되는 것도 아닙니다.

아래 구성·설정·거부 조건은 이 연결이 성립하는 실제 조건입니다. 자료가 처음 기준선으로 읽힌 것인지 새 변경인지, 표시에 필요한 이전값이 존재하는지를 함께 판단합니다.

**이 보관본 의존성 선언**: PySide6-Essentials ==6.12.0·PyInstaller ==6.22.3. PySide6는 창을 만드는 도구이고 PyInstaller는 실행 파일을 묶는 도구입니다. 외부 실행 도구·GPU 드라이버는 별도 조건입니다.

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

**실제 입력·설정과 기본값**

- [`--data-dir`](src/app.py#L723) (src/app.py)

  앱 설정·이력을 저장할 폴더를 고릅니다.

기본은 LOCALAPPDATA 아래 CodexOrbit이며 그 환경 값이 없으면 사용자 홈을 기준으로 합니다.

같은 폴더 중복 실행 잠금과 연결됩니다.

원문 선언: `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`.

- [`--sessions`](src/app.py#L724) (src/app.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path`.

- [`--smoke-test`](src/app.py#L725) (src/app.py)

  점검 실행을 켜는 스위치입니다. 숫자를 넣는 옵션이 아니라 이름을 붙여 켭니다. 옵션 존재 자체가 검사를 실행해 통과했다는 증거는 아닙니다. 원문 선언: `action='store_true'`.

- [`--smoke-report`](src/app.py#L726) (src/app.py)

  점검 결과를 저장할 파일 경로입니다. 폴더를 고르는 세션 옵션과 달리 보고서 파일을 지정합니다. 원문 선언: `type=Path`.

- [`--show-details`](src/app.py#L727) (src/app.py)

  처음부터 상세창을 보여 주는 스위치입니다. 숨겨진 원문 값을 새로 만들어 주는 기능이 아닙니다. 원문 선언: `action='store_true'`.

- [`--show-event`](src/app.py#L728) (src/app.py)

  이미 있는 이력의 사건 ID 또는 대상 ID를 지정해 다시 표시합니다. 실제 저장된 ID와 맞춰 읽고 새 사건 생성과 구분합니다. 원문 선언: `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`.

- [`ROLE_LABELS`](src/app.py#L42) (src/app.py)

  역할 코드와 사용자용 한글 이름의 대응 표입니다.

예를 들어 build는 구현, verifier는 독립 검증으로 읽습니다.

화면 설명을 바꾸는 표이며 서버 모델을 바꾸는 설정은 아닙니다.

원문 선언: `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`.

- [`MAX_TEXT_BYTES`](src/core.py#L9) (src/core.py)

  읽거나 적용할 지침 문서의 크기 상한입니다. 원문·추가 지침·최종 결과의 제한과 연결되며 큰 문서 쓰기를 무제한 허용하지 않습니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`BEGIN`](src/core.py#L10) (src/core.py)

  앱이 관리하는 지침 구간이 시작되는 정확한 표시 문자열입니다. 문서의 나머지 부분과 구분하기 때문에 추가할 지침 안에 같은 표식을 넣지 못하게 합니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'`.

- [`END`](src/core.py#L11) (src/core.py)

  앱 관리 구간이 끝나는 정확한 표시 문자열입니다. 시작 표시보다 먼저 있거나 여러 번 있으면 원래 구간이 불명확해 적용을 거부하는 조건과 연결됩니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'`.

- [`--sessions`](src/notifier.py#L506) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L507) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L17) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L18) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L19) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L20) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L21) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대 값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L22) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L23) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료 량을 제한합니다. 파일 하나의 상한과 별개 인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L24) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개 수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

**처리 책임과 원문에 명시된 함수 동작**

- [`short_reason`](src/app.py#L56) (src/app.py)

  변경 알림에서 짧은 이유가 필요한 경우에는 결과가 다음처럼 제한됩니다. 원문에 있는 이유를 읽을 수 있고 없는 이유는 만들어지지 않습니다. 공개된 문장과 앱이 추측한 동기를 혼동하지 않도록 하기 위해서입니다

- [`read_jsonl_tail`](src/core.py#L18) (src/core.py)

  기록 파일의 끝부분만 읽어 첫 줄이나 마지막 줄이 중간에 잘려 들어온 경우에는 결과가 다음처럼 제한됩니다. 온전한 줄만 기록 한 건으로 읽습니다. 문장 안의 다른 줄바꿈 모양 문자나 반쪽 기록을 새 사건으로 잘못 세지 않기 위해서입니다

- [`title_catalog`](src/core.py#L55) (src/core.py)

  같은 작업에 제목 정보가 여러 출처로 남아 있는 경우에는 결과가 다음처럼 제한됩니다. 제목과 그 제목을 얻은 출처를 대조할 수 있습니다. 제목 문자열만 같다는 이유로 근거 수준까지 같다고 보지 않기 위해서입니다

- [`resolve_title`](src/core.py#L73) (src/core.py)

  한 채팅에서 별도 자식 작업이 실행된 기록을 표시하는 경우에는 결과가 다음처럼 제한됩니다. 어느 대화에서 생긴 어떤 작업인지 구별됩니다. 작업명을 새 채팅 제목이나 다른 부모 채팅으로 오해하지 않기 위해서입니다

- [`safe_path`](src/core.py#L97) (src/core.py)

  지침을 적용할 파일이나 그 파일에 이르는 상위 폴더가 다른 곳으로 연결된 경우에는 결과가 다음처럼 제한됩니다. 연결을 통해 의도 밖의 위치를 수정하는 경로는 허용되지 않습니다. 겉으로 고른 폴더와 실제 쓰는 위치가 달라지는 일을 막기 위해서입니다

- [`lookup_parent_reason`](src/notifier.py#L219) (src/notifier.py)

  자식 사건의 배정 이유가 큰 부모 기록에 남아 있는 경우에는 결과가 다음처럼 제한됩니다. 이유를 찾는 보조 읽기가 다음 감시 출발점을 옮기지 않습니다. 부모 이유를 찾다가 새 사건을 건너뛰거나 전체 큰 파일을 무제한 읽지 않기 위해서입니다

- [`enrich_event`](src/notifier.py#L266) (src/notifier.py)

  이력이 이미 전달됐지만 첫 배정 이유가 뒤늦게 확인된 경우에는 결과가 다음처럼 제한됩니다. 같은 사건의 설명이 보강되고 중복 알림은 만들어지지 않습니다. 이유 보강과 새 모델 변경 사건을 구분하기 위해서입니다

**멈추거나 거부되는 조건과 읽는 방법**

- [`not lock.tryLock(100)`](src/app.py#L743) (src/app.py)

  같은 저장 폴더를 이미 다른 Codex Orbit가 쓰거나 잠금 파일에 접근할 수 없으면 시작을 거부합니다.

한 설정·상태 파일을 두 실행이 동시에 바꾸지 않도록하며, 이 메시지만으로 어느 쪽 원인인지 확정하지 않습니다.

원문 오류: “같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.”입니다.

- [`not isinstance(value, dict)`](src/app.py#L114) (src/app.py)

  앱 설정이 항목 이름과 값을 가진 사전이어야 합니다. 예를 들어 목록만 저장돼 있으면 설정 이름으로 값을 찾을 수 없어 거부합니다. 원문 오류: “앱 설정은 JSON 객체여야 합니다.”입니다.

- [`not path.is_dir()`](src/app.py#L495) (src/app.py)

  선택한 기록 경로가 실제 폴더가 아니면 거부합니다. 오타가 있는 위치나 파일 하나를 감시 폴더로 잘못 지정했는지 먼저 확인합니다. 원문 오류: “존재하는 sessions 폴더를 선택하세요.”입니다.

- [`self.plan is None`](src/app.py#L599) (src/app.py)

  아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다. 대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다. 원문 오류: “새 미리보기가 필요합니다.”입니다.

- [`not receipts`](src/app.py#L611) (src/app.py)

  앱이 지침 적용 전에 만든 백업이 없으면 그 백업을 이용한 되돌리기를 할 수 없습니다. 임의의 다른 문서를 원래 내용이라고 추정하지 않습니다. 원문 오류: “앱이 만든 적용 백업이 없습니다.”입니다.

- [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112) (src/core.py)

  지침 원본 문서가 2 MiB보다 크면 읽기 범위를 벗어나 거부합니다. 작은 설명으로 예상한 입력을 대용량 파일 읽기로 확대하지 않는 제한입니다. 원문 오류: “문서가 2 MiB 상한을 초과했습니다.”입니다.

- [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64) (src/core.py)

  보관한 제목 목록이 기대한 이름별 저장 형식이 아니면 거부합니다. 제목의 출처와 연결을 알 수 없는데도 빈 목록으로 자동 덮어쓰지 않습니다. 원문 오류: “제목 캐시 구조가 올바르지 않습니다.”입니다.

- [`target.name.lower() != 'agents.md'`](src/core.py#L123) (src/core.py)

  선택한 파일 이름이 AGENTS.md가 아니면 적용하지 않습니다. 다른 문서나 데이터 파일을 지침 대상이라고 잘못 수정하지 않기 위한 이름 확인입니다. 원문 오류: “적용 대상은 AGENTS.md 파일이어야합니다.”입니다.

- [`not target.parent.is_dir()`](src/core.py#L125) (src/core.py)

  대상 파일을 둘 상위 폴더가 없으면 적용하지 않습니다. 앱이 의도하지 않은 위치의 폴더를 새로 만들어 결과를 숨기는 대신 선택 경로부터 확인하게 합니다. 원문 오류: “대상 폴더가 존재하지 않습니다.”입니다.

- [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127) (src/core.py)

  기존 대상이 일반 파일이 아니거나 2 MiB보다 크면 적용하지 않습니다. 폴더·특수 파일을 문서처럼 취급하거나 대용량 원본을 바꾸지 않게합니다. 원문 오류: “대상은 2 MiB 이하의 일반 파일이어야합니다.”입니다.

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

- [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L54) (src/notifier.py)

  이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다. 큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다. 원문 오류: “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”입니다.

- [`self.state.get('schema_version') != 2`](src/notifier.py#L57) (src/notifier.py)

  옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다.

이를 새 관측 이력으로 자동 해석하지 않습니다.

명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다.

원문 오류: “구형 상태는 요청과 관측이 혼합되어 있습니다.

원본 보존 후 명시적 재기준선이 필요합니다.”입니다.

- [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L59) (src/notifier.py)

  저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다. 자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다. 원문 오류: “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”입니다.

- [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L61) (src/notifier.py)

  어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다. 이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다. 원문 오류: “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”입니다.

- [`not isinstance(record, dict)`](src/notifier.py#L315) (src/notifier.py)

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다. 원문 오류: “JSON 객체가 아닙니다.”입니다.

- [`path.stat().st_size &gt; 20000`](src/notifier.py#L378) (src/notifier.py)

  명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다. 짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게하기 위한 크기 제한입니다. 원문 오류: “명 시 알림 파일 상한 초과”입니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다.

최초 기준 선 읽기와 새 변경은 다릅니다.

자산·글 꼴 오류라면 이 차수 assets와 라이선스를 대조합니다.

과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다.

이유·이전 값이 없으면 원 문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

2차 → 3차의 실제 파일 비교입니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **수정** [src/app.py](src/app.py): 전체 비교에서 기능 연결의 실제 변경을 확인합니다.

- **수정** [src/core.py](src/core.py): 전체 비교에서 기능 연결의 실제 변경을 확인합니다.

- **수정** [src/notifier.py](src/notifier.py): 전체 비교에서 기능 연결의 실제 변경을 확인합니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다.

원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다.

이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다.

Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


**이 수준에서 연결·실행·설계를 대조하는 순서**

선언의 정확한 코드와 전체 역할 원문은 LEVEL 5 및 연결된 소스에 보존합니다. 입력 사례는 검토 방법을 설명하며 실제 실행 결과가 아닙니다. 옵션 지정·기본값과 정상·거부 사례를 구분하고, 변경 시 호출자·공유 상태·표시 조건에 미치는 영향을 대조합니다.

- [src/app.py](src/app.py): 사용자 동작과 감시 상태가 UI에서 만납니다. 이전·현재 표시, 알림 수명, 원문 접근, 감시 종료의 순서가 서로 연결되지만 같은 상태 값은 아닙니다.

- [src/core.py](src/core.py): 로컬 기록·제목 입력은 이력과 알림의 근거가 되고, 문서 적용 입력은 미리보기·원본 대조를 거쳐 쓰기로 연결됩니다. 읽기와 쓰기의 경계를 구분해야 합니다.

- [src/notifier.py](src/notifier.py): 순차 감시의 읽기 위치, 복제 판별, 부모 이유 보조 조회가 연결됩니다. 뒤늦은 보강이 새 알림·새 모델 변경으로 바뀌지 않는 점이 중요합니다.

<a id="reading-level-3"></a>
## LEVEL 3 - Practitioner

### LEVEL 3 · 이 차수를 준비하는 범위

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존 본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다.

자산과 의존성을 준비한 이 차수 폴더에서 `python src/app.py`를 실행합니다. history 소스만으로 과거 배포 EXE와 동일한 화면·자산이 모두 복원되지는 않습니다.

#### LEVEL 3 · 이 보관본의 의존성 목록

[requirements.txt](requirements.txt)의 실제 항목입니다. 외부 실행 도구와 GPU 드라이버는 별도로 준비합니다.

```text
PySide6-Essentials==6.12.0
PyInstaller==6.22.3
```

#### LEVEL 3 · 소스에서 제공하는 CLI 옵션

**진입 소스:** [app.py](src/app.py)

**정의된 옵션 이름:** `--data-dir`, `--sessions`, `--smoke-test`, `--smoke-report`, `--show-details`, `--show-event`

**진입 소스:** [notifier.py](src/notifier.py)

**정의된 옵션 이름:** `--sessions`, `--work`


각 옵션의 기본 값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 3 · [src/app.py](src/app.py)

| 정의 | 역할 |
| --- | --- |
| [`short_reason`](src/app.py#L56) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L723)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L724)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L725)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--smoke-report`](src/app.py#L726)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L727)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L728)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L42)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


| 거부 조건 | 오류 메시지 |
| --- | --- |
| [`not lock.tryLock(100)`](src/app.py#L743) | 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다. |
| [`not isinstance(value, dict)`](src/app.py#L114) | 앱 설정은 JSON 객체여야 합니다. |
| [`not path.is_dir()`](src/app.py#L495) | 존재하는 sessions 폴더를 선택하세요. |
| [`self.plan is None`](src/app.py#L599) | 새 미리보기가 필요합니다. |
| [`not receipts`](src/app.py#L611) | 앱이 만든 적용 백업이 없습니다. |

#### LEVEL 3 · [src/core.py](src/core.py)

| 정의 | 역할 |
| --- | --- |
| [`read_jsonl_tail`](src/core.py#L18) | 물리적 LF만 나누며 잘 린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
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
| [`lookup_parent_reason`](src/notifier.py#L219) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L266) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L506) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L507) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L17) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L18) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L19) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L20) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L21) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L22) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L23) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L24) | `정의=256` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L54)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') != 2`](src/notifier.py#L57)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L59)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L61)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L315)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L378)

**오류 메시지:** 명시 알림 파일 상한 초과


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

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

[자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)


### LEVEL 3·3차의 구체적인 기능과 확인

알림 유지 설정을 확인한 뒤 긴 내용과 짧은 내용을 각각 엽니다. 이력의 특정 이벤트를 다시 표시하는 --show-event가 추가되어 있으므로 ID와 실제 기록을 대조합니다. 상세창에 나온 이유는 원문에서 확인하고, 알림이 오래 남는다는 사실을 새 변경 감시 성공으로 대신하지 않습니다.

Windows에서 이 차수의 [requirements.txt](requirements.txt)에 맞는 Python 의존성과 해당 자산을 준비한 뒤 **이 차수 폴더에서** `python src/app.py`를 실행합니다.

현재 루트의 assets가 과거 모든 차수와 호환되는 것은 아니며, history 소스만으로 과거 EXE의 화면·자산 전체가 복원되는 것도 아닙니다.

입력은 현재 사용자의 sessions JSONL과 앱 설정입니다. **경로·자산·설정 먼저 확인한 뒤 실행**하고, 알림·변경 이력·로컬 진단을 원본 사건과 대조합니다. 동작 확인에서 모델 전후·추론 전후·이유·시각·근거 수준을 함께 읽고 미기록은 미확인으로 남깁니다.

아래 옵션은 실제 소스에 선언된 이름입니다. CLI는 명령 뒤에 옵션을 붙이는 방식이며 각 기본값·부작용은 해당 선언과 함께 확인합니다. smoke라는 이름은 점검용 실행을 뜻하며 이 문서가 그 실행을 대신 수행했다는 뜻은 아닙니다.

**이 보관본 의존성 선언**: PySide6-Essentials ==6.12.0·PyInstaller ==6.22.3. PySide6는 창을 만드는 도구이고 PyInstaller는 실행 파일을 묶는 도구입니다. 외부 실행 도구·GPU 드라이버는 별도 조건입니다.

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

**실제 입력·설정과 기본값**

- [`--data-dir`](src/app.py#L723) (src/app.py)

  앱 설정·이력을 저장할 폴더를 고릅니다.

기본은 LOCALAPPDATA 아래 CodexOrbit이며 그 환경 값이 없으면 사용자 홈을 기준으로 합니다.

같은 폴더 중복 실행 잠금과 연결됩니다.

원문 선언: `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`.

- [`--sessions`](src/app.py#L724) (src/app.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path`.

- [`--smoke-test`](src/app.py#L725) (src/app.py)

  점검 실행을 켜는 스위치입니다. 숫자를 넣는 옵션이 아니라 이름을 붙여 켭니다. 옵션 존재 자체가 검사를 실행해 통과했다는 증거는 아닙니다. 원문 선언: `action='store_true'`.

- [`--smoke-report`](src/app.py#L726) (src/app.py)

  점검 결과를 저장할 파일 경로입니다. 폴더를 고르는 세션 옵션과 달리 보고서 파일을 지정합니다. 원문 선언: `type=Path`.

- [`--show-details`](src/app.py#L727) (src/app.py)

  처음부터 상세창을 보여 주는 스위치입니다. 숨겨진 원문 값을 새로 만들어 주는 기능이 아닙니다. 원문 선언: `action='store_true'`.

- [`--show-event`](src/app.py#L728) (src/app.py)

  이미 있는 이력의 사건 ID 또는 대상 ID를 지정해 다시 표시합니다. 실제 저장된 ID와 맞춰 읽고 새 사건 생성과 구분합니다. 원문 선언: `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`.

- [`ROLE_LABELS`](src/app.py#L42) (src/app.py)

  역할 코드와 사용자용 한글 이름의 대응 표입니다.

예를 들어 build는 구현, verifier는 독립 검증으로 읽습니다.

화면 설명을 바꾸는 표이며 서버 모델을 바꾸는 설정은 아닙니다.

원문 선언: `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`.

- [`MAX_TEXT_BYTES`](src/core.py#L9) (src/core.py)

  읽거나 적용할 지침 문서의 크기 상한입니다. 원문·추가 지침·최종 결과의 제한과 연결되며 큰 문서 쓰기를 무제한 허용하지 않습니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`BEGIN`](src/core.py#L10) (src/core.py)

  앱이 관리하는 지침 구간이 시작되는 정확한 표시 문자열입니다. 문서의 나머지 부분과 구분하기 때문에 추가할 지침 안에 같은 표식을 넣지 못하게 합니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'`.

- [`END`](src/core.py#L11) (src/core.py)

  앱 관리 구간이 끝나는 정확한 표시 문자열입니다. 시작 표시보다 먼저 있거나 여러 번 있으면 원래 구간이 불명확해 적용을 거부하는 조건과 연결됩니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'`.

- [`--sessions`](src/notifier.py#L506) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L507) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L17) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L18) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L19) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L20) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L21) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대 값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L22) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L23) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료 량을 제한합니다. 파일 하나의 상한과 별개 인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L24) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개 수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

**처리 책임과 원문에 명시된 함수 동작**

- [`short_reason`](src/app.py#L56) (src/app.py)

  확인할 입력 사례: 변경 알림에서 짧은 이유가 필요한 경우. 원문에서 확인할 처리: 기록에 명시된 이유 또는 배정·선택 목적 문장을 우선 골라 짧게 보여 줍니다 결과 판독 기준: 원문에 있는 이유를 읽을 수 있고 없는 이유는 만들어지지 않습니다

- [`read_jsonl_tail`](src/core.py#L18) (src/core.py)

  확인할 입력 사례: 기록 파일의 끝부분만 읽어 첫 줄이나 마지막 줄이 중간에 잘려 들어온 경우. 원문에서 확인할 처리: 파일에서 실제 줄바꿈을 뜻하는 LF 바이트로만 한 건씩 나누고 완성되지 않은 양끝 조각은 해석하지 않습니다. 결과 판독 기준: 온전한 줄만 기록 한 건으로 읽습니다

- [`title_catalog`](src/core.py#L55) (src/core.py)

  확인할 입력 사례: 같은 작업에 제목 정보가 여러 출처로 남아 있는 경우. 원문에서 확인할 처리: 공식 앱에서 확인해 저장한 제목과 컴퓨터 안의 제목 목록이 어디서 왔는지 함께 보존합니다. 결과 판독 기준: 제목과 그 제목을 얻은 출처를 대조할 수 있습니다

- [`resolve_title`](src/core.py#L73) (src/core.py)

  확인할 입력 사례: 한 채팅에서 별도 자식 작업이 실행된 기록을 표시하는 경우. 원문에서 확인할 처리: 실제 부모 채팅 제목과 자식 작업명을 서로 다른 정보로 다룹니다 결과 판독 기준: 어느 대화에서 생긴 어떤 작업인지 구별됩니다

- [`safe_path`](src/core.py#L97) (src/core.py)

  확인할 입력 사례: 지침을 적용할 파일이나 그 파일에 이르는 상위 폴더가 다른 곳으로 연결된 경우.

원문에서 확인할 처리: 파일 자체뿐 아니라 이미 존재하는 상위 폴더까지 확인해 바로가기처럼 다른 위치로 보내는 링크·재분석 지점을 거부합니다.

결과 판독 기준: 연결을 통해 의도 밖의 위치를 수정하는 경로는 허용되지 않습니다

- [`lookup_parent_reason`](src/notifier.py#L219) (src/notifier.py)

  확인할 입력 사례: 자식 사건의 배정 이유가 큰 부모 기록에 남아 있는 경우. 원문에서 확인할 처리: 부모 기록의 최근 공개 호출만 정해진 양 안에서 찾아보고 정기 감시의 읽기 위치는 그대로 둡니다 결과 판독 기준: 이유를 찾는 보조 읽기가 다음 감시 출발점을 옮기지 않습니다

- [`enrich_event`](src/notifier.py#L266) (src/notifier.py)

  확인할 입력 사례: 이력이 이미 전달됐지만 첫 배정 이유가 뒤늦게 확인된 경우. 원문에서 확인할 처리: 정확히 연결된 사건의 첫 배정 이유만 기존 이력에 덧붙이고 새 알림은 띄우지 않습니다. 결과 판독 기준: 같은 사건의 설명이 보강되고 중복 알림은 만들어지지 않습니다

**멈추거나 거부되는 조건과 읽는 방법**

- 오류 “같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.”

  입력 사례와 확인 순서: 같은 저장 폴더를 이미 다른 Codex Orbit가 쓰거나 잠금 파일에 접근할 수 없으면 시작을 거부합니다.

한 설정·상태 파일을 두 실행이 동시에 바꾸지 않도록하며, 이 메시지만으로 어느 쪽 원인인지 확정하지 않습니다.

원문 조건 [`not lock.tryLock(100)`](src/app.py#L743) (src/app.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “앱 설정은 JSON 객체여야 합니다.”

  입력 사례와 확인 순서: 앱 설정이 항목 이름과 값을 가진 사전이어야 합니다.

예를 들어 목록만 저장돼 있으면 설정 이름으로 값을 찾을 수 없어 거부합니다.

원문 조건 [`not isinstance(value, dict)`](src/app.py#L114) (src/app.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “존재하는 sessions 폴더를 선택하세요.”

  입력 사례와 확인 순서: 선택한 기록 경로가 실제 폴더가 아니면 거부합니다.

오타가 있는 위치나 파일 하나를 감시 폴더로 잘못 지정했는지 먼저 확인합니다.

원문 조건 [`not path.is_dir()`](src/app.py#L495) (src/app.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “새 미리보기가 필요합니다.”

  입력 사례와 확인 순서: 아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다.

대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다.

원문 조건 [`self.plan is None`](src/app.py#L599) (src/app.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “앱이 만든 적용 백업이 없습니다.”

  입력 사례와 확인 순서: 앱이 지침 적용 전에 만든 백업이 없으면 그 백업을 이용한 되돌리기를 할 수 없습니다.

임의의 다른 문서를 원래 내용이라고 추정하지 않습니다.

원문 조건 [`not receipts`](src/app.py#L611) (src/app.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “문서가 2 MiB 상한을 초과했습니다.”

  입력 사례와 확인 순서: 지침 원본 문서가 2 MiB보다 크면 읽기 범위를 벗어나 거부합니다.

작은 설명으로 예상한 입력을 대용량 파일 읽기로 확대하지 않는 제한입니다.

원문 조건 [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “제목 캐시 구조가 올바르지 않습니다.”

  입력 사례와 확인 순서: 보관한 제목 목록이 기대한 이름별 저장 형식이 아니면 거부합니다.

제목의 출처와 연결을 알 수 없는데도 빈 목록으로 자동 덮어쓰지 않습니다.

원문 조건 [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “적용 대상은 AGENTS.md 파일이어야 합니다.”

  입력 사례와 확인 순서: 선택한 파일 이름이 AGENTS.md가 아니면 적용하지 않습니다.

다른 문서나 데이터 파일을 지침 대상이라고 잘못 수정하지 않기 위한 이름 확인입니다.

원문 조건 [`target.name.lower() != 'agents.md'`](src/core.py#L123) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “대상 폴더가 존재하지 않습니다.”

  입력 사례와 확인 순서: 대상 파일을 둘 상위 폴더가 없으면 적용하지 않습니다.

앱이 의도하지 않은 위치의 폴더를 새로 만들어 결과를 숨기는 대신 선택 경로부터 확인하게 합니다.

원문 조건 [`not target.parent.is_dir()`](src/core.py#L125) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “대상은 2 MiB 이하의 일반 파일이어야 합니다.”

  입력 사례와 확인 순서: 기존 대상이 일반 파일이 아니거나 2 MiB보다 크면 적용하지 않습니다.

폴더·특수 파일을 문서처럼 취급하거나 대용량 원본을 바꾸지 않게합니다.

원문 조건 [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다.”

  입력 사례와 확인 순서: 내용이 공백뿐이거나 새로 붙일 지침이 2 MiB보다 크면 거부합니다.

아무 내용 없는 적용이나 과도한 추가 입력을 정상 변경으로 보지 않습니다.

원문 조건 [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “지침 내용에 앱 관리구역 표식을 넣을 수 없습니다.”

  입력 사례와 확인 순서: 추가 지침 안에 앱의 시작·끝 관리 표시가 들어 있으면 거부합니다.

내용 속 표시를 실제 관리 경계로 잘못 읽어 원문 구간을 혼동하지 않도록 합니다.

원문 조건 [`BEGIN in added or END in added`](src/core.py#L136) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “적용 결과가 2 MiB 상한을 초과합니다.”

  입력 사례와 확인 순서: 원본과 새 지침을 합친 최종 문서가 2 MiB보다 크면 쓰지 않습니다.

원본과 추가분이 각각 작더라도 합쳐진 결과는 별도 크기 제한을 만족해야 합니다.

원문 조건 [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다.”

  입력 사례와 확인 순서: 아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다.

대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다.

원문 조건 [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “미리보기 데이터가 변경되었습니다.”

  입력 사례와 확인 순서: 미리보기 계획 안의 원문·결과 바이트가 저장된 지문과 다르면 거부합니다.

사용자가 확인했던 변경 계획과 실제 쓸 내용이 같은지 확인하는 경계입니다.

원문 조건 [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “유효한 앱 원문 백업이 아닙니다.”

  입력 사례와 확인 순서: 백업이 앱이 정한 백업 폴더 안의 정상 파일이 아니거나 크기 제한을 넘으면 복원에 쓰지 않습니다.

아무 파일이나 원래 문서라고 덮어쓰지 않기 위한 확인입니다.

원문 조건 [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “백업 해시가 일치하지 않습니다.”

  입력 사례와 확인 순서: 백업 내용의 지문이 적용 때 기록한 원본 지문과 다르면 되돌리기를 거부합니다.

파일 이름이 같더라도 내용이 달라졌다면 안전한 원본으로 보지 않습니다.

원문 조건 [`digest(raw) != receipt['before_hash']`](src/core.py#L200) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “JSON 객체가 아닙니다.”

  입력 사례와 확인 순서: 한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다.

예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다.

원문 조건 [`not isinstance(row, dict)`](src/core.py#L40) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “기존 관리구역 표식이 손상되었거나 중복되었습니다.”

  입력 사례와 확인 순서: 시작·끝 표시가 정확히 한 쌍이 아니거나 순서가 뒤집혔다면 적용할 구간이 불명확해 거부합니다.

여러 구간 중 임의의 하나를 골라 원문을 바꾸지 않습니다.

원문 조건 [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143) (src/core.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”

  입력 사례와 확인 순서: 이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다.

큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다.

원문 조건 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L54) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.”

  입력 사례와 확인 순서: 옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다.

이를 새 관측 이력으로 자동 해석하지 않습니다.

명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다.

원문 조건 [`self.state.get('schema_version') != 2`](src/notifier.py#L57) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”

  입력 사례와 확인 순서: 저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다.

자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다.

원문 조건 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L59) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”

  입력 사례와 확인 순서: 어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다.

이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다.

원문 조건 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L61) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “JSON 객체가 아닙니다.”

  입력 사례와 확인 순서: 한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다.

예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다.

원문 조건 [`not isinstance(record, dict)`](src/notifier.py#L315) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “명시 알림 파일 상한 초과”

  입력 사례와 확인 순서: 명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다.

짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게하기 위한 크기 제한입니다.

원문 조건 [`path.stat().st_size &gt; 20000`](src/notifier.py#L378) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다.

최초 기준 선 읽기와 새 변경은 다릅니다.

자산·글 꼴 오류라면 이 차수 assets와 라이선스를 대조합니다.

과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다.

이유·이전 값이 없으면 원 문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

2차 → 3차의 실제 파일 비교입니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **수정** [src/app.py](src/app.py): 실행 자료에 이 변경이 반영되어 있는지 대조합니다.

- **수정** [src/core.py](src/core.py): 실행 자료에 이 변경이 반영되어 있는지 대조합니다.

- **수정** [src/notifier.py](src/notifier.py): 실행 자료에 이 변경이 반영되어 있는지 대조합니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다.

원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다.

이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다.

Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


**이 수준에서 연결·실행·설계를 대조하는 순서**

선언의 정확한 코드와 전체 역할 원문은 LEVEL 5 및 연결된 소스에 보존합니다. 입력 사례는 검토 방법을 설명하며 실제 실행 결과가 아닙니다. 옵션 지정·기본값과 정상·거부 사례를 구분하고, 변경 시 호출자·공유 상태·표시 조건에 미치는 영향을 대조합니다.

- [src/app.py](src/app.py): 원문 사건·실제 화면·종료 상태를 따로 확인합니다. 이력에 있다고 알림이 떴다고 보지 않고 창이 닫혔다고 작업자 정리가 끝났다고 가정하지 않습니다.

- [src/core.py](src/core.py): 기록 파일과 지침 대상은 별도 준비물입니다. 기록은 온전한 줄·출처를, 지침은 대상·미리보기·백업을 확인하는 사례로 나눠 대조합니다.

- [src/notifier.py](src/notifier.py): 기준선·새 사건·같은 사건 보강을 다른 입력 사례로 준비합니다. 원본 시각이 있는지, 원문 읽기 위치가 유지되는지, 기존 이력에 이유만 붙는지 대조합니다.

<a id="reading-level-4"></a>
## LEVEL 4 - Advanced

### LEVEL 4 · 설계 의도와 검토 경계

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

### LEVEL 4 · 이 차수 구현의 실제 근거

| 파일 | 역할·구성 |
| --- | --- |
| [src/app.py](src/app.py) | Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용. |
| [src/notifier.py](src/notifier.py) | 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기.<br>외부 통신은 하지 않습니다. |
| [src/core.py](src/core.py) | 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용. |

| 단계 | 내용 |
| --- | --- |
| 입력 | 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정 |
| 처리 | 변경 감시 → 공개 이유·전후 모델 정리 → 알림·상세창 표시 |
| 출력 | 알림·변경 이력·로컬 진단 기록 |


### LEVEL 4 · 조건·변경·결과를 함께 검토하기

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존 본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다.

자산과 의존성을 준비한 이 차수 폴더에서 `python src/app.py`를 실행합니다. history 소스만으로 과거 배포 EXE와 동일한 화면·자산이 모두 복원되지는 않습니다.

#### LEVEL 4 · 이 보관본의 의존성 목록

[requirements.txt](requirements.txt)의 실제 항목입니다. 외부 실행 도구와 GPU 드라이버는 별도로 준비합니다.

```text
PySide6-Essentials==6.12.0
PyInstaller==6.22.3
```

#### LEVEL 4 · 소스에서 제공하는 CLI 옵션

**진입 소스:** [app.py](src/app.py)

**정의된 옵션 이름:** `--data-dir`, `--sessions`, `--smoke-test`, `--smoke-report`, `--show-details`, `--show-event`

**진입 소스:** [notifier.py](src/notifier.py)

**정의된 옵션 이름:** `--sessions`, `--work`


각 옵션의 기본 값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 4 · [src/app.py](src/app.py)

| 정의 | 역할 |
| --- | --- |
| [`short_reason`](src/app.py#L56) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L723)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L724)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L725)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--smoke-report`](src/app.py#L726)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L727)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L728)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L42)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


| 거부 조건 | 오류 메시지 |
| --- | --- |
| [`not lock.tryLock(100)`](src/app.py#L743) | 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다. |
| [`not isinstance(value, dict)`](src/app.py#L114) | 앱 설정은 JSON 객체여야 합니다. |
| [`not path.is_dir()`](src/app.py#L495) | 존재하는 sessions 폴더를 선택하세요. |
| [`self.plan is None`](src/app.py#L599) | 새 미리보기가 필요합니다. |
| [`not receipts`](src/app.py#L611) | 앱이 만든 적용 백업이 없습니다. |

#### LEVEL 4 · [src/core.py](src/core.py)

| 정의 | 역할 |
| --- | --- |
| [`read_jsonl_tail`](src/core.py#L18) | 물리적 LF만 나누며 잘 린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
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
| [`lookup_parent_reason`](src/notifier.py#L219) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L266) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L506) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L507) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L17) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L18) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L19) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L20) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L21) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L22) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L23) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L24) | `정의=256` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L54)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') != 2`](src/notifier.py#L57)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L59)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L61)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L315)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L378)

**오류 메시지:** 명시 알림 파일 상한 초과


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


### LEVEL 4·3차의 구체적인 기능과 확인

app.py의 알림 수명·높이·기록 종류 분기와 short_reason을 먼저 읽고 core.py·notifier.py의 실제 변경을 전체 diff에서 추적합니다. 요약은 원문 발췌라는 경계를 가지며 추정 생성이 아닙니다. 지속 알림·재표시·감시 상태 전이는 각각 영향을 받는 경로입니다.

**로컬 수집 경계와 UI·명시적 파일 작업의 경계**를 분리합니다. JSONL 입력에서 변경 감지·공개 이유 정리·알림·상세 표시로 이어지고, 설정·이력·진단은 로컬 운영 자료입니다. 관측된 변경과 명시 배정의 근거를 혼합하지 않습니다.

Windows에서 이 차수의 [requirements.txt](requirements.txt)에 맞는 Python 의존성과 해당 자산을 준비한 뒤 **이 차수 폴더에서** `python src/app.py`를 실행합니다.

현재 루트의 assets가 과거 모든 차수와 호환되는 것은 아니며, history 소스만으로 과거 EXE의 화면·자산 전체가 복원되는 것도 아닙니다.

아래 모듈·선언·거부 조건은 변경 영향 검토의 출발점입니다. 이름·상수만으로 전체 호출 순서나 예외 전파를 추정하지 말고 연결된 코드에서 분기와 호출자를 대조합니다.

**이 보관본 의존성 선언**: PySide6-Essentials ==6.12.0·PyInstaller ==6.22.3. PySide6는 창을 만드는 도구이고 PyInstaller는 실행 파일을 묶는 도구입니다. 외부 실행 도구·GPU 드라이버는 별도 조건입니다.

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

**실제 입력·설정과 기본값**

- [`--data-dir`](src/app.py#L723) (src/app.py)

  앱 설정·이력을 저장할 폴더를 고릅니다.

기본은 LOCALAPPDATA 아래 CodexOrbit이며 그 환경 값이 없으면 사용자 홈을 기준으로 합니다.

같은 폴더 중복 실행 잠금과 연결됩니다.

원문 선언: `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`.

- [`--sessions`](src/app.py#L724) (src/app.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path`.

- [`--smoke-test`](src/app.py#L725) (src/app.py)

  점검 실행을 켜는 스위치입니다. 숫자를 넣는 옵션이 아니라 이름을 붙여 켭니다. 옵션 존재 자체가 검사를 실행해 통과했다는 증거는 아닙니다. 원문 선언: `action='store_true'`.

- [`--smoke-report`](src/app.py#L726) (src/app.py)

  점검 결과를 저장할 파일 경로입니다. 폴더를 고르는 세션 옵션과 달리 보고서 파일을 지정합니다. 원문 선언: `type=Path`.

- [`--show-details`](src/app.py#L727) (src/app.py)

  처음부터 상세창을 보여 주는 스위치입니다. 숨겨진 원문 값을 새로 만들어 주는 기능이 아닙니다. 원문 선언: `action='store_true'`.

- [`--show-event`](src/app.py#L728) (src/app.py)

  이미 있는 이력의 사건 ID 또는 대상 ID를 지정해 다시 표시합니다. 실제 저장된 ID와 맞춰 읽고 새 사건 생성과 구분합니다. 원문 선언: `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`.

- [`ROLE_LABELS`](src/app.py#L42) (src/app.py)

  역할 코드와 사용자용 한글 이름의 대응 표입니다.

예를 들어 build는 구현, verifier는 독립 검증으로 읽습니다.

화면 설명을 바꾸는 표이며 서버 모델을 바꾸는 설정은 아닙니다.

원문 선언: `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`.

- [`MAX_TEXT_BYTES`](src/core.py#L9) (src/core.py)

  읽거나 적용할 지침 문서의 크기 상한입니다. 원문·추가 지침·최종 결과의 제한과 연결되며 큰 문서 쓰기를 무제한 허용하지 않습니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`BEGIN`](src/core.py#L10) (src/core.py)

  앱이 관리하는 지침 구간이 시작되는 정확한 표시 문자열입니다. 문서의 나머지 부분과 구분하기 때문에 추가할 지침 안에 같은 표식을 넣지 못하게 합니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'`.

- [`END`](src/core.py#L11) (src/core.py)

  앱 관리 구간이 끝나는 정확한 표시 문자열입니다. 시작 표시보다 먼저 있거나 여러 번 있으면 원래 구간이 불명확해 적용을 거부하는 조건과 연결됩니다. 원문 선언: `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'`.

- [`--sessions`](src/notifier.py#L506) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L507) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L17) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L18) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L19) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L20) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L21) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대 값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L22) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L23) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료 량을 제한합니다. 파일 하나의 상한과 별개 인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L24) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개 수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

**처리 책임과 원문에 명시된 함수 동작**

- [`short_reason`](src/app.py#L56) (src/app.py)

  이 분기의 설계 책임은 기록에 명시된 이유 또는 배정·선택 목적 문장을 우선 골라 짧게 보여 줍니다 이를 바꾸면 보존해야 할 결과는 “원문에 있는 이유를 읽을 수 있고 없는 이유는 만들어지지 않습니다”입니다. 공개된 문장과 앱이 추측한 동기를 혼동하지 않도록 하기 위해서입니다

- [`read_jsonl_tail`](src/core.py#L18) (src/core.py)

  이 분기의 설계 책임은 파일에서 실제 줄바꿈을 뜻하는 LF 바이트로만 한 건씩 나누고 완성되지 않은 양끝 조각은 해석하지 않습니다. 이를 바꾸면 보존해야 할 결과는 “온전한 줄만 기록 한 건으로 읽습니다”입니다. 문장 안의 다른 줄바꿈 모양 문자나 반쪽 기록을 새 사건으로 잘못 세지 않기 위해서입니다

- [`title_catalog`](src/core.py#L55) (src/core.py)

  이 분기의 설계 책임은 공식 앱에서 확인해 저장한 제목과 컴퓨터 안의 제목 목록이 어디서 왔는지 함께 보존합니다. 이를 바꾸면 보존해야 할 결과는 “제목과 그 제목을 얻은 출처를 대조할 수 있습니다”입니다. 제목 문자열만 같다는 이유로 근거 수준까지 같다고 보지 않기 위해서입니다

- [`resolve_title`](src/core.py#L73) (src/core.py)

  이 분기의 설계 책임은 실제 부모 채팅 제목과 자식 작업명을 서로 다른 정보로 다룹니다 이를 바꾸면 보존해야 할 결과는 “어느 대화에서 생긴 어떤 작업인지 구별됩니다”입니다. 작업명을 새 채팅 제목이나 다른 부모 채팅으로 오해하지 않기 위해서입니다

- [`safe_path`](src/core.py#L97) (src/core.py)

  이 분기의 설계 책임은 파일 자체뿐 아니라 이미 존재하는 상위 폴더까지 확인해 바로가기처럼 다른 위치로 보내는 링크·재분석 지점을 거부합니다. 이를 바꾸면 보존해야 할 결과는 “연결을 통해 의도 밖의 위치를 수정하는 경로는 허용되지 않습니다”입니다. 겉으로 고른 폴더와 실제 쓰는 위치가 달라지는 일을 막기 위해서입니다

- [`lookup_parent_reason`](src/notifier.py#L219) (src/notifier.py)

  이 분기의 설계 책임은 부모 기록의 최근 공개 호출만 정해진 양 안에서 찾아보고 정기 감시의 읽기 위치는 그대로 둡니다 이를 바꾸면 보존해야 할 결과는 “이유를 찾는 보조 읽기가 다음 감시 출발점을 옮기지 않습니다”입니다. 부모 이유를 찾다가 새 사건을 건너뛰거나 전체 큰 파일을 무제한 읽지 않기 위해서입니다

- [`enrich_event`](src/notifier.py#L266) (src/notifier.py)

  이 분기의 설계 책임은 정확히 연결된 사건의 첫 배정 이유만 기존 이력에 덧붙이고 새 알림은 띄우지 않습니다. 이를 바꾸면 보존해야 할 결과는 “같은 사건의 설명이 보강되고 중복 알림은 만들어지지 않습니다”입니다. 이유 보강과 새 모델 변경 사건을 구분하기 위해서입니다

**멈추거나 거부되는 조건과 읽는 방법**

- 거부 분기 [`not lock.tryLock(100)`](src/app.py#L743) (src/app.py) → 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.

  같은 저장 폴더를 이미 다른 Codex Orbit가 쓰거나 잠금 파일에 접근할 수 없으면 시작을 거부합니다. 한 설정·상태 파일을 두 실행이 동시에 바꾸지 않도록하며, 이 메시지만으로 어느 쪽 원인인지 확정하지 않습니다.

- 거부 분기 [`not isinstance(value, dict)`](src/app.py#L114) (src/app.py) → 앱 설정은 JSON 객체여야 합니다.

  앱 설정이 항목 이름과 값을 가진 사전이어야 합니다. 예를 들어 목록만 저장돼 있으면 설정 이름으로 값을 찾을 수 없어 거부합니다.

- 거부 분기 [`not path.is_dir()`](src/app.py#L495) (src/app.py) → 존재하는 sessions 폴더를 선택하세요.

  선택한 기록 경로가 실제 폴더가 아니면 거부합니다. 오타가 있는 위치나 파일 하나를 감시 폴더로 잘못 지정했는지 먼저 확인합니다.

- 거부 분기 [`self.plan is None`](src/app.py#L599) (src/app.py) → 새 미리보기가 필요합니다.

  아직 적용 계획을 만들지 않았다면 지침을 쓸 수 없습니다. 대상과 바뀔 내용을 먼저 미리 본 뒤 적용하게 해 원문을 보지 않고 쓰는 일을 막습니다.

- 거부 분기 [`not receipts`](src/app.py#L611) (src/app.py) → 앱이 만든 적용 백업이 없습니다.

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

  기존 대상이 일반 파일이 아니거나 2 MiB보다 크면 적용하지 않습니다. 폴더·특수 파일을 문서처럼 취급하거나 대용량 원본을 바꾸지 않게합니다.

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

- 거부 분기 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L54) (src/notifier.py) → 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

  이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다. 큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다.

- 거부 분기 [`self.state.get('schema_version') != 2`](src/notifier.py#L57) (src/notifier.py) → 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

  옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다. 이를 새 관측 이력으로 자동 해석하지 않습니다. 명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다.

- 거부 분기 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L59) (src/notifier.py) → 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

  저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다. 자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다.

- 거부 분기 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L61) (src/notifier.py) → 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

  어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다. 이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다.

- 거부 분기 [`not isinstance(record, dict)`](src/notifier.py#L315) (src/notifier.py) → JSON 객체가 아닙니다.

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다.

- 거부 분기 [`path.stat().st_size &gt; 20000`](src/notifier.py#L378) (src/notifier.py) → 명시 알림 파일 상한 초과

  명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다. 짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게하기 위한 크기 제한입니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다.

최초 기준 선 읽기와 새 변경은 다릅니다.

자산·글 꼴 오류라면 이 차수 assets와 라이선스를 대조합니다.

과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다.

이유·이전 값이 없으면 원 문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

2차 → 3차의 실제 파일 비교입니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **수정** [src/app.py](src/app.py): 변경 영향은 연결된 전체 diff의 실제 분기로 한정합니다.

- **수정** [src/core.py](src/core.py): 변경 영향은 연결된 전체 diff의 실제 분기로 한정합니다.

- **수정** [src/notifier.py](src/notifier.py): 변경 영향은 연결된 전체 diff의 실제 분기로 한정합니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다.

원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다.

이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다.

Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


**이 수준에서 연결·실행·설계를 대조하는 순서**

선언의 정확한 코드와 전체 역할 원문은 LEVEL 5 및 연결된 소스에 보존합니다. 입력 사례는 검토 방법을 설명하며 실제 실행 결과가 아닙니다. 옵션 지정·기본값과 정상·거부 사례를 구분하고, 변경 시 호출자·공유 상태·표시 조건에 미치는 영향을 대조합니다.

- [src/app.py](src/app.py): UI 소유 관계와 작업자 수명이 연결됩니다. 표시용 이름 변경이 원문 의미를 바꾸거나 이벤트 요약이 전후 필드·근거를 덮지 않는지 검토해야 합니다.

- [src/core.py](src/core.py): LF 경계·경로 확인을 바꾸면 사건 판독 또는 실제 파일 쓰기 위치가 달라집니다. 문서 해시·관리 표식·백업 검증을 약화하는 변경과 화면 문구 수정은 다른 영향 범위입니다.

- [src/notifier.py](src/notifier.py): 상태 저장과 파일 읽기 위치 변경은 과거 사건 재생·누락·중복에 영향을 줄 수 있습니다. 보조 조회가 순차 위치를 이동하지 않는 경계와 손상 상태의 원본 보존이 핵심입니다.

<a id="reading-level-5"></a>
## LEVEL 5 - Expert


### LEVEL 5·3차의 구체적인 기능과 확인

2차 →3차의 app.py·core.py·notifier.py 수정이 비교 범위입니다. 유지 설정, 내용 높이, show-event의 ID 대응, 명시 이유 발췌를 분리한 검토가 필요합니다. 당시 UI 실행 결과가 공개 이력에 없어 이 문서는 장시간 유지나 모든 길이의 가독성을 실측 보증하지 않습니다.

**증거의 범위는 이 차수 공개 원문과 보존 소스입니다.** 로컬 기록의 모델·추론 값은 서버가 보증한 모델 신원 인증이 아닙니다. 원문에 없는 이유·이전 값·실행 성과는 보 간하지 않습니다. 입력은 현재 사용자 JSONL과 설정, 출력은 알림·이력·로컬 진단이며 관측 변경과 명시 배정은 다른 증거 종류입니다.

Windows에서 이 차수의 [requirements.txt](requirements.txt)에 맞는 Python 의존성과 해당 자산을 준비한 뒤 **이 차수 폴더에서** `python src/app.py`를 실행합니다.

현재 루트의 assets가 과거 모든 차수와 호환되는 것은 아니며, history 소스만으로 과거 EXE의 화면·자산 전체가 복원되는 것도 아닙니다.

재현에는 동일 차수 의존성·자산·입력·설정·실행 표면이 필요합니다. 아래 선언의 상한·스키마·거부 분기는 검토 가능한 소스 조건이며, 실제 부하·종료·화면 동작의 성공 증거와 구분합니다.

**이 보관본 의존성 선언**: PySide6-Essentials ==6.12.0·PyInstaller ==6.22.3. PySide6는 창을 만드는 도구이고 PyInstaller는 실행 파일을 묶는 도구입니다. 외부 실행 도구·GPU 드라이버는 별도 조건입니다.

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

**실제 입력·설정과 기본값**

- [app.py](src/app.py)에서 사용할 수 있는 옵션: `--data-dir`, `--sessions`, `--smoke-test`, `--smoke-report`, `--show-details`, `--show-event`.

- [notifier.py](src/notifier.py)에서 사용할 수 있는 옵션: `--sessions`, `--work`.

- 재현 시 대조할 원문 선언 [`--data-dir`](src/app.py#L723) (src/app.py): `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`.

- 재현 시 대조할 원문 선언 [`--sessions`](src/app.py#L724) (src/app.py): `type=Path`.

- 재현 시 대조할 원문 선언 [`--smoke-test`](src/app.py#L725) (src/app.py): `action='store_true'`.

- 재현 시 대조할 원문 선언 [`--smoke-report`](src/app.py#L726) (src/app.py): `type=Path`.

- 재현 시 대조할 원문 선언 [`--show-details`](src/app.py#L727) (src/app.py): `action='store_true'`.

- 재현 시 대조할 원문 선언 [`--show-event`](src/app.py#L728) (src/app.py): `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`.

- 재현 시 대조할 원문 선언 [`ROLE_LABELS`](src/app.py#L42) (src/app.py): `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`.

- 재현 시 대조할 원문 선언 [`MAX_TEXT_BYTES`](src/core.py#L9) (src/core.py): `정의=2 * 1024 * 1024`.

- 재현 시 대조할 원문 선언 [`BEGIN`](src/core.py#L10) (src/core.py): `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'`.

- 재현 시 대조할 원문 선언 [`END`](src/core.py#L11) (src/core.py): `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'`.

- 재현 시 대조할 원문 선언 [`--sessions`](src/notifier.py#L506) (src/notifier.py): `type=Path; default=Path.home() / '.codex/sessions'`.

- 재현 시 대조할 원문 선언 [`--work`](src/notifier.py#L507) (src/notifier.py): `type=Path; default=ROOT / 'work'`.

- 재현 시 대조할 원문 선언 [`ROOT`](src/notifier.py#L17) (src/notifier.py): `정의=Path(__file__).resolve().parents[1]`.

- 재현 시 대조할 원문 선언 [`APP_ID`](src/notifier.py#L18) (src/notifier.py): `정의='Yunseok.Codex.ModelChangeNotifier'`.

- 재현 시 대조할 원문 선언 [`READ_BYTES`](src/notifier.py#L19) (src/notifier.py): `정의=512 * 1024`.

- 재현 시 대조할 원문 선언 [`MAX_RECORD`](src/notifier.py#L20) (src/notifier.py): `정의=2 * 1024 * 1024`.

- 재현 시 대조할 원문 선언 [`MAX_FILES`](src/notifier.py#L21) (src/notifier.py): `정의=4096`.

- 재현 시 대조할 원문 선언 [`LOG_BYTES`](src/notifier.py#L22) (src/notifier.py): `정의=2 * 1024 * 1024`.

- 재현 시 대조할 원문 선언 [`POLL_READ_BYTES`](src/notifier.py#L23) (src/notifier.py): `정의=8 * 1024 * 1024`.

- 재현 시 대조할 원문 선언 [`MAX_PENDING`](src/notifier.py#L24) (src/notifier.py): `정의=256`.

**처리 책임과 원문에 명시된 함수 동작**

- [`short_reason`](src/app.py#L56) (src/app.py): 원문이 명시한 동작 계약은 다음과 같습니다. 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다.

- [`read_jsonl_tail`](src/core.py#L18) (src/core.py): 원문이 명시한 동작 계약은 다음과 같습니다. 물리적 LF만 나누며 잘 린 앞/뒤 조각은 레코드로 해석하지 않습니다.

- [`title_catalog`](src/core.py#L55) (src/core.py): 원문이 명시한 동작 계약은 다음과 같습니다. 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다.

- [`resolve_title`](src/core.py#L73) (src/core.py): 원문이 명시한 동작 계약은 다음과 같습니다. 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다.

- [`safe_path`](src/core.py#L97) (src/core.py): 원문이 명시한 동작 계약은 다음과 같습니다. 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다.

- [`lookup_parent_reason`](src/notifier.py#L219) (src/notifier.py): 원문이 명시한 동작 계약은 다음과 같습니다. 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다.

- [`enrich_event`](src/notifier.py#L266) (src/notifier.py): 원문이 명시한 동작 계약은 다음과 같습니다. 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다.

**멈추거나 거부되는 조건과 읽는 방법**

- 경계 사례 [`not lock.tryLock(100)`](src/app.py#L743) (src/app.py): 원문 오류는 “같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(value, dict)`](src/app.py#L114) (src/app.py): 원문 오류는 “앱 설정은 JSON 객체여야 합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not path.is_dir()`](src/app.py#L495) (src/app.py): 원문 오류는 “존재하는 sessions 폴더를 선택하세요.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`self.plan is None`](src/app.py#L599) (src/app.py): 원문 오류는 “새 미리보기가 필요합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not receipts`](src/app.py#L611) (src/app.py): 원문 오류는 “앱이 만든 적용 백업이 없습니다.”. 허용 입력과 구분해 재현할 조건입니다.

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

- 경계 사례 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L54) (src/notifier.py): 원문 오류는 “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`self.state.get('schema_version') != 2`](src/notifier.py#L57) (src/notifier.py): 원문 오류는 “구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L59) (src/notifier.py): 원문 오류는 “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L61) (src/notifier.py): 원문 오류는 “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(record, dict)`](src/notifier.py#L315) (src/notifier.py): 원문 오류는 “JSON 객체가 아닙니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`path.stat().st_size &gt; 20000`](src/notifier.py#L378) (src/notifier.py): 원문 오류는 “명시 알림 파일 상한 초과”. 허용 입력과 구분해 재현할 조건입니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다.

최초 기준 선 읽기와 새 변경은 다릅니다.

자산·글 꼴 오류라면 이 차수 assets와 라이선스를 대조합니다.

과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다.

이유·이전 값이 없으면 원 문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

2차 → 3차의 실제 파일 비교입니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **수정** [src/app.py](src/app.py): 공개 바이트 비교에서 분류된 변경이며 의도·성능을 추정하지 않습니다.

- **수정** [src/core.py](src/core.py): 공개 바이트 비교에서 분류된 변경이며 의도·성능을 추정하지 않습니다.

- **수정** [src/notifier.py](src/notifier.py): 공개 바이트 비교에서 분류된 변경이며 의도·성능을 추정하지 않습니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다.

원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다.

이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다.

Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


기존의 전체 설명·표·코드·함수 참조·파일별 비교는 아래에 그대로 이어집니다. [자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)
<!-- reading-levels:end -->


[프로젝트](../../README.md) · [전체 차수](../../docs/REVISION_INDEX.md) · [원본 자료](.) · [← 이전: 2차](../02%EC%B0%A8/README.md) · [다음: 4차 →](../04%EC%B0%A8/README.md)

<a name="-목적과-이-차수의-역할"></a>
## 목적과 이 차수의 역할

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

<a name="features"></a>

<a name="-핵심-기능과-보존-범위"></a>
## 핵심 기능과 보존 범위

**항목:** 1

**이 차수에서 확인할 내용:** 알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

**항목:** 2

**이 차수에서 확인할 내용:** 로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.


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
| [src/notifier.py](src/notifier.py) | 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기.<br>외부 통신은 하지 않습니다. |
| [src/core.py](src/core.py) | 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용. |

<a name="setup"></a>

<a name="-설치-환경과-실행사용법"></a>
## 설치 환경과 실행·사용법

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존 본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다.

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

**정의된 옵션 이름:** `--data-dir`, `--sessions`, `--smoke-test`, `--smoke-report`, `--show-details`, `--show-event`

**진입 소스:** [notifier.py](src/notifier.py)

**정의된 옵션 이름:** `--sessions`, `--work`


각 옵션의 기본 값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

### [src/app.py](src/app.py)

| 정의 | 역할 |
| --- | --- |
| [`short_reason`](src/app.py#L56) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |

**설정·옵션:** [`--data-dir`](src/app.py#L723)

**코드의 선언:** `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'`

**설정·옵션:** [`--sessions`](src/app.py#L724)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--smoke-test`](src/app.py#L725)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--smoke-report`](src/app.py#L726)

**코드의 선언:** `type=Path`

**설정·옵션:** [`--show-details`](src/app.py#L727)

**코드의 선언:** `action='store_true'`

**설정·옵션:** [`--show-event`](src/app.py#L728)

**코드의 선언:** `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'`

**설정·옵션:** [`ROLE_LABELS`](src/app.py#L42)

**코드의 선언:** `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}`


| 거부 조건 | 오류 메시지 |
| --- | --- |
| [`not lock.tryLock(100)`](src/app.py#L743) | 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다. |
| [`not isinstance(value, dict)`](src/app.py#L114) | 앱 설정은 JSON 객체여야 합니다. |
| [`not path.is_dir()`](src/app.py#L495) | 존재하는 sessions 폴더를 선택하세요. |
| [`self.plan is None`](src/app.py#L599) | 새 미리보기가 필요합니다. |
| [`not receipts`](src/app.py#L611) | 앱이 만든 적용 백업이 없습니다. |

### [src/core.py](src/core.py)

| 정의 | 역할 |
| --- | --- |
| [`read_jsonl_tail`](src/core.py#L18) | 물리적 LF만 나누며 잘 린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
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
| [`lookup_parent_reason`](src/notifier.py#L219) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L266) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L506) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L507) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L17) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L18) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L19) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L20) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L21) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L22) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L23) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L24) | `정의=256` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L54)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') != 2`](src/notifier.py#L57)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L59)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L61)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L315)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L378)

**오류 메시지:** 명시 알림 파일 상한 초과


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

2차에서 3차로 이어지는 실제 파일 비교입니다.

[전체 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff)

추가·수정·삭제, 주석·공백·개행과 바이너리 크기·해시는 연결된 원래 비교 자료에서 확인합니다.

<details>
<summary>파일별 비교·크기·해시 자세히 보기</summary>

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

- **수정** `src/app.py`: 이 전 29190바이트, SHA-256 `87f6314b529e5831384703c6cd0fe97b212bb751eac632c0e7b422d1026f75da`; 현재 39580바이트, SHA-256 `93d5ba9d617c35f5e547642ddf31199791b462f1530856124ae65c780d2e7929`.

- **수정** `src/core.py`: 이 전 8223바이트, SHA-256 `6e6ae64f8d21cb1af9972916c8cbbeb9fa9e43d76d69fa723521803370a7b970`; 현재 10204바이트, SHA-256 `0da59ecbba81ad77544766fa50f0b24bd5abbd8d8f8da37f269a8ff08979b981`.

- **수정** `src/notifier.py`: 이 전 26813바이트, SHA-256 `2059fcac37723f34535eba05d83443a9dbd7e3dfb771200f190f2c8ed2ffb9a8`; 현재 30682바이트, SHA-256 `00b619819040824cf816bb95536385e8af190967933b7912498d3edbc7f3cb89`.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다.

부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

</details>

[프로젝트](../../README.md) · [전체 차수](../../docs/REVISION_INDEX.md) · [원본 자료](.) · [← 이전: 2차](../02%EC%B0%A8/README.md) · [다음: 4차 →](../04%EC%B0%A8/README.md)
