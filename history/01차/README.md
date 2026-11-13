<div align="center">

<a name="-codex-orbit--1차"></a>
# Codex Orbit · 1차

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령행 감시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

**기술 분류:** Windows 데스크톱 · Python · 로컬 JSONL 감시

[핵심 기능](#features) · [사용 흐름](#usage) · [자료 구성](#structure) · [준비와 실행](#setup) · [결과 읽기](#results) · [직전 변경](#changes)

</div>
<!-- reading-levels:start -->
[LEVEL 1 - Beginner](#reading-level-1) · [LEVEL 2 - Explorer](#reading-level-2) · [LEVEL 3 - Practitioner](#reading-level-3) · [LEVEL 4 - Advanced](#reading-level-4) · [LEVEL 5 - Expert](#reading-level-5)

프로젝트 전체의 설명은 [LEVEL 1 - Beginner](../../docs/%EC%9D%BD%EA%B8%B0%EC%95%88%EB%82%B4/%EB%A0%88%EB%B2%A81.md)부터 [LEVEL 5 - Expert](../../docs/%EC%9D%BD%EA%B8%B0%EC%95%88%EB%82%B4/%EB%A0%88%EB%B2%A85.md)까지 같은 범위로 연결됩니다.

<a id="reading-level-1"></a>
## LEVEL 1 - Beginner

### LEVEL 1 · 이 자료가 하는 일과 달라진 점

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령행 감시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

### LEVEL 1 · 실제 동작을 따라 읽기

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령행 감시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

JSONL은 한 줄마다 하나의 JSON 기록을 담은 파일입니다. CLI는 명령어와 옵션을 입력해 프로그램을 실행하는 방식입니다.

입력 — 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

처리 — 변경 감시 → 공개 이유·전후 모델 정리 → 알림

출력 — 알림·변경 이력·로컬 진단 기록

### LEVEL 1 · 준비하고 확인할 것

Windows에서 Python과 PowerShell을 준비합니다. 1차의 `src/notifier.py`는 Python 표준 라이브러리만 사용하므로 별도 pip 패키지를 설치하지 않습니다. 알림은 같은 차수의 `src/toast.ps1`을 호출하며, 이 보존본에는 `requirements.txt`와 GUI `app.py`가 없습니다.

이 차수에는 GUI app.py가 없습니다. `src/notifier.py`의 CLI에서 지정하는 경로로 감시기를 사용합니다. 인자 목록과 기본 경로는 아래 소스 설정 표에서 확인합니다.

#### LEVEL 1 · 소스에서 제공하는 CLI 옵션

| 진입 소스 · 정의된 옵션 이름 |
| --- |
| **진입 소스:** [notifier.py](src/notifier.py)<br>**정의된 옵션 이름:** `--sessions`, `--work` |

각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 1 · [src/notifier.py](src/notifier.py)


| 설정·옵션 · 코드의 선언 |
| --- |
| **설정·옵션:** [`--sessions`](src/notifier.py#L436)<br>**코드의 선언:** `type=Path; default=Path.home() / '.codex/sessions'` |
| **설정·옵션:** [`--work`](src/notifier.py#L437)<br>**코드의 선언:** `type=Path; default=ROOT / 'work'` |
| **설정·옵션:** [`ROOT`](src/notifier.py#L16)<br>**코드의 선언:** `정의=Path(__file__).resolve().parents[1]` |
| **설정·옵션:** [`APP_ID`](src/notifier.py#L17)<br>**코드의 선언:** `정의='Yunseok.Codex.ModelChangeNotifier'` |
| **설정·옵션:** [`READ_BYTES`](src/notifier.py#L18)<br>**코드의 선언:** `정의=512 * 1024` |
| **설정·옵션:** [`MAX_RECORD`](src/notifier.py#L19)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`MAX_FILES`](src/notifier.py#L20)<br>**코드의 선언:** `정의=4096` |
| **설정·옵션:** [`LOG_BYTES`](src/notifier.py#L21)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`POLL_READ_BYTES`](src/notifier.py#L22)<br>**코드의 선언:** `정의=8 * 1024 * 1024` |
| **설정·옵션:** [`MAX_PENDING`](src/notifier.py#L23)<br>**코드의 선언:** `정의=256` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L53)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') != 2`](src/notifier.py#L56)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L58)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L60)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L244)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L306)

**오류 메시지:** 명시 알림 파일 상한 초과


</details>

1. `src/notifier.py`의 main과 CLI 인자를 읽어 sessions·work 경로를 확인합니다.
2. 본인 로컬 기록을 대상으로 시작하며 상태 파일과 진단 파일의 저장 위치를 구분합니다.
3. 첫 기준선 읽기 이후 새 변경을 관측하고 알림 기록을 확인합니다.

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

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령행 감시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령행 감시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

### LEVEL 2 · 입력에서 출력으로

**단계:** 입력

**내용:** 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

**단계:** 처리

**내용:** 변경 감시 → 공개 이유·전후 모델 정리 → 알림

**단계:** 출력

**내용:** 알림·변경 이력·로컬 진단 기록


입력·처리·출력은 위의 같은 자료 흐름을 다른 단계에서 읽는 기준입니다. 처리 조건과 출력의 의미를 함께 확인합니다.

### LEVEL 2 · 설정과 처리 순서의 관계

1. `src/notifier.py`의 main과 CLI 인자를 읽어 sessions·work 경로를 확인합니다.
2. 본인 로컬 기록을 대상으로 시작하며 상태 파일과 진단 파일의 저장 위치를 구분합니다.
3. 첫 기준선 읽기 이후 새 변경을 관측하고 알림 기록을 확인합니다.

Windows에서 Python과 PowerShell을 준비합니다. 1차의 `src/notifier.py`는 Python 표준 라이브러리만 사용하므로 별도 pip 패키지를 설치하지 않습니다. 알림은 같은 차수의 `src/toast.ps1`을 호출하며, 이 보존본에는 `requirements.txt`와 GUI `app.py`가 없습니다.

이 차수에는 GUI app.py가 없습니다. `src/notifier.py`의 CLI에서 지정하는 경로로 감시기를 사용합니다. 인자 목록과 기본 경로는 아래 소스 설정 표에서 확인합니다.

#### LEVEL 2 · 소스에서 제공하는 CLI 옵션

| 진입 소스 · 정의된 옵션 이름 |
| --- |
| **진입 소스:** [notifier.py](src/notifier.py)<br>**정의된 옵션 이름:** `--sessions`, `--work` |

각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 2 · [src/notifier.py](src/notifier.py)


| 설정·옵션 · 코드의 선언 |
| --- |
| **설정·옵션:** [`--sessions`](src/notifier.py#L436)<br>**코드의 선언:** `type=Path; default=Path.home() / '.codex/sessions'` |
| **설정·옵션:** [`--work`](src/notifier.py#L437)<br>**코드의 선언:** `type=Path; default=ROOT / 'work'` |
| **설정·옵션:** [`ROOT`](src/notifier.py#L16)<br>**코드의 선언:** `정의=Path(__file__).resolve().parents[1]` |
| **설정·옵션:** [`APP_ID`](src/notifier.py#L17)<br>**코드의 선언:** `정의='Yunseok.Codex.ModelChangeNotifier'` |
| **설정·옵션:** [`READ_BYTES`](src/notifier.py#L18)<br>**코드의 선언:** `정의=512 * 1024` |
| **설정·옵션:** [`MAX_RECORD`](src/notifier.py#L19)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`MAX_FILES`](src/notifier.py#L20)<br>**코드의 선언:** `정의=4096` |
| **설정·옵션:** [`LOG_BYTES`](src/notifier.py#L21)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`POLL_READ_BYTES`](src/notifier.py#L22)<br>**코드의 선언:** `정의=8 * 1024 * 1024` |
| **설정·옵션:** [`MAX_PENDING`](src/notifier.py#L23)<br>**코드의 선언:** `정의=256` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L53)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') != 2`](src/notifier.py#L56)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L58)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L60)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L244)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L306)

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

<a id="reading-level-3"></a>
## LEVEL 3 - Practitioner

### LEVEL 3 · 이 차수를 준비하는 범위

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령행 감시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

Windows에서 Python과 PowerShell을 준비합니다. 1차의 `src/notifier.py`는 Python 표준 라이브러리만 사용하므로 별도 pip 패키지를 설치하지 않습니다. 알림은 같은 차수의 `src/toast.ps1`을 호출하며, 이 보존본에는 `requirements.txt`와 GUI `app.py`가 없습니다.

이 차수에는 GUI app.py가 없습니다. `src/notifier.py`의 CLI에서 지정하는 경로로 감시기를 사용합니다. 인자 목록과 기본 경로는 아래 소스 설정 표에서 확인합니다.

#### LEVEL 3 · 소스에서 제공하는 CLI 옵션

| 진입 소스 · 정의된 옵션 이름 |
| --- |
| **진입 소스:** [notifier.py](src/notifier.py)<br>**정의된 옵션 이름:** `--sessions`, `--work` |

각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 3 · [src/notifier.py](src/notifier.py)


| 설정·옵션 · 코드의 선언 |
| --- |
| **설정·옵션:** [`--sessions`](src/notifier.py#L436)<br>**코드의 선언:** `type=Path; default=Path.home() / '.codex/sessions'` |
| **설정·옵션:** [`--work`](src/notifier.py#L437)<br>**코드의 선언:** `type=Path; default=ROOT / 'work'` |
| **설정·옵션:** [`ROOT`](src/notifier.py#L16)<br>**코드의 선언:** `정의=Path(__file__).resolve().parents[1]` |
| **설정·옵션:** [`APP_ID`](src/notifier.py#L17)<br>**코드의 선언:** `정의='Yunseok.Codex.ModelChangeNotifier'` |
| **설정·옵션:** [`READ_BYTES`](src/notifier.py#L18)<br>**코드의 선언:** `정의=512 * 1024` |
| **설정·옵션:** [`MAX_RECORD`](src/notifier.py#L19)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`MAX_FILES`](src/notifier.py#L20)<br>**코드의 선언:** `정의=4096` |
| **설정·옵션:** [`LOG_BYTES`](src/notifier.py#L21)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`POLL_READ_BYTES`](src/notifier.py#L22)<br>**코드의 선언:** `정의=8 * 1024 * 1024` |
| **설정·옵션:** [`MAX_PENDING`](src/notifier.py#L23)<br>**코드의 선언:** `정의=256` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L53)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') != 2`](src/notifier.py#L56)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L58)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L60)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L244)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L306)

**오류 메시지:** 명시 알림 파일 상한 초과


</details>

### LEVEL 3 · 실제 사용·실험 순서

1. `src/notifier.py`의 main과 CLI 인자를 읽어 sessions·work 경로를 확인합니다.
2. 본인 로컬 기록을 대상으로 시작하며 상태 파일과 진단 파일의 저장 위치를 구분합니다.
3. 첫 기준선 읽기 이후 새 변경을 관측하고 알림 기록을 확인합니다.

**단계:** 입력

**내용:** 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

**단계:** 처리

**내용:** 변경 감시 → 공개 이유·전후 모델 정리 → 알림

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

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령행 감시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

[자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)

<a id="reading-level-4"></a>
## LEVEL 4 - Advanced

### LEVEL 4 · 설계 의도와 검토 경계

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령행 감시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령행 감시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

### LEVEL 4 · 이 차수 구현의 실제 근거

| 파일 · 원문에 정의된 역할·구성 |
| --- |
| **파일:** [src/notifier.py](src/notifier.py)<br>**원문에 정의된 역할·구성:** 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다. |

**단계:** 입력

**내용:** 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

**단계:** 처리

**내용:** 변경 감시 → 공개 이유·전후 모델 정리 → 알림

**단계:** 출력

**내용:** 알림·변경 이력·로컬 진단 기록


### LEVEL 4 · 조건·변경·결과를 함께 검토하기

Windows에서 Python과 PowerShell을 준비합니다. 1차의 `src/notifier.py`는 Python 표준 라이브러리만 사용하므로 별도 pip 패키지를 설치하지 않습니다. 알림은 같은 차수의 `src/toast.ps1`을 호출하며, 이 보존본에는 `requirements.txt`와 GUI `app.py`가 없습니다.

이 차수에는 GUI app.py가 없습니다. `src/notifier.py`의 CLI에서 지정하는 경로로 감시기를 사용합니다. 인자 목록과 기본 경로는 아래 소스 설정 표에서 확인합니다.

#### LEVEL 4 · 소스에서 제공하는 CLI 옵션

| 진입 소스 · 정의된 옵션 이름 |
| --- |
| **진입 소스:** [notifier.py](src/notifier.py)<br>**정의된 옵션 이름:** `--sessions`, `--work` |

각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 4 · [src/notifier.py](src/notifier.py)


| 설정·옵션 · 코드의 선언 |
| --- |
| **설정·옵션:** [`--sessions`](src/notifier.py#L436)<br>**코드의 선언:** `type=Path; default=Path.home() / '.codex/sessions'` |
| **설정·옵션:** [`--work`](src/notifier.py#L437)<br>**코드의 선언:** `type=Path; default=ROOT / 'work'` |
| **설정·옵션:** [`ROOT`](src/notifier.py#L16)<br>**코드의 선언:** `정의=Path(__file__).resolve().parents[1]` |
| **설정·옵션:** [`APP_ID`](src/notifier.py#L17)<br>**코드의 선언:** `정의='Yunseok.Codex.ModelChangeNotifier'` |
| **설정·옵션:** [`READ_BYTES`](src/notifier.py#L18)<br>**코드의 선언:** `정의=512 * 1024` |
| **설정·옵션:** [`MAX_RECORD`](src/notifier.py#L19)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`MAX_FILES`](src/notifier.py#L20)<br>**코드의 선언:** `정의=4096` |
| **설정·옵션:** [`LOG_BYTES`](src/notifier.py#L21)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`POLL_READ_BYTES`](src/notifier.py#L22)<br>**코드의 선언:** `정의=8 * 1024 * 1024` |
| **설정·옵션:** [`MAX_PENDING`](src/notifier.py#L23)<br>**코드의 선언:** `정의=256` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L53)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') != 2`](src/notifier.py#L56)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L58)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L60)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L244)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L306)

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

1. `src/notifier.py`의 main과 CLI 인자를 읽어 sessions·work 경로를 확인합니다.
2. 본인 로컬 기록을 대상으로 시작하며 상태 파일과 진단 파일의 저장 위치를 구분합니다.
3. 첫 기준선 읽기 이후 새 변경을 관측하고 알림 기록을 확인합니다.

위 구성요소의 입력·출력과 실패 조건을 같은 차수 소스에 연결해 검토합니다. 전체 비교는 추가·수정·삭제와 원래 보관 범위를 구분하는 근거입니다.

[자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)
<a id="reading-level-5"></a>
## LEVEL 5 - Expert

기존의 전체 설명·표·코드·함수 참조·파일별 비교는 아래에 그대로 이어집니다. [자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)
<!-- reading-levels:end -->



[프로젝트](../../README.md) · [전체 차수](../../docs/REVISION_INDEX.md) · [원본 자료](.) · [다음: 2차 →](../02%EC%B0%A8/README.md)

<a name="-목적과-이-차수의-역할"></a>
## 목적과 이 차수의 역할

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령행 감시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

<a name="features"></a>

<a name="-핵심-기능과-보존-범위"></a>
## 핵심 기능과 보존 범위

**항목:** 1

**이 차수에서 확인할 내용:** 현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령행 감시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

**항목:** 2

**이 차수에서 확인할 내용:** 로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.


<a name="-입력처리출력"></a>
## 입력·처리·출력

**단계:** 입력

**내용:** 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

**단계:** 처리

**내용:** 변경 감시 → 공개 이유·전후 모델 정리 → 알림

**단계:** 출력

**내용:** 알림·변경 이력·로컬 진단 기록


<a name="usage"></a>

<a name="️-화면과-사용-흐름"></a>
## 화면과 사용 흐름

1. `src/notifier.py`의 main과 CLI 인자를 읽어 sessions·work 경로를 확인합니다.
2. 본인 로컬 기록을 대상으로 시작하며 상태 파일과 진단 파일의 저장 위치를 구분합니다.
3. 첫 기준선 읽기 이후 새 변경을 관측하고 알림 기록을 확인합니다.

<a name="structure"></a>

<a name="-실제-자료-구성"></a>
## 실제 자료 구성

| 경로 · 자료 종류 |
| --- |
| **경로:** [src/](src)<br>**자료 종류:** 하위 자료 폴더 |
| **경로:** [README.md](README.md)<br>**자료 종류:** MD 파일 |
| **경로:** [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json)<br>**자료 종류:** JSON 파일 |
| **경로:** [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md)<br>**자료 종류:** MD 파일 |
| **경로:** [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json)<br>**자료 종류:** JSON 파일 |
| **경로:** [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff)<br>**자료 종류:** DIFF 파일 |

<a name="-주요-모듈과-코드-읽기"></a>
## 주요 모듈과 코드 읽기

| 파일 · 원문에 정의된 역할·구성 |
| --- |
| **파일:** [src/notifier.py](src/notifier.py)<br>**원문에 정의된 역할·구성:** 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다. |

<a name="setup"></a>

<a name="-설치-환경과-실행사용법"></a>
## 설치 환경과 실행·사용법

Windows에서 Python과 PowerShell을 준비합니다. 1차의 `src/notifier.py`는 Python 표준 라이브러리만 사용하므로 별도 pip 패키지를 설치하지 않습니다. 알림은 같은 차수의 `src/toast.ps1`을 호출하며, 이 보존본에는 `requirements.txt`와 GUI `app.py`가 없습니다.

이 차수에는 GUI app.py가 없습니다. `src/notifier.py`의 CLI에서 지정하는 경로로 감시기를 사용합니다. 인자 목록과 기본 경로는 아래 소스 설정 표에서 확인합니다.

<a name="️-소스에서-제공하는-cli-옵션"></a>
### 소스에서 제공하는 CLI 옵션

| 진입 소스 · 정의된 옵션 이름 |
| --- |
| **진입 소스:** [notifier.py](src/notifier.py)<br>**정의된 옵션 이름:** `--sessions`, `--work` |

각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

### [src/notifier.py](src/notifier.py)


| 설정·옵션 · 코드의 선언 |
| --- |
| **설정·옵션:** [`--sessions`](src/notifier.py#L436)<br>**코드의 선언:** `type=Path; default=Path.home() / '.codex/sessions'` |
| **설정·옵션:** [`--work`](src/notifier.py#L437)<br>**코드의 선언:** `type=Path; default=ROOT / 'work'` |
| **설정·옵션:** [`ROOT`](src/notifier.py#L16)<br>**코드의 선언:** `정의=Path(__file__).resolve().parents[1]` |
| **설정·옵션:** [`APP_ID`](src/notifier.py#L17)<br>**코드의 선언:** `정의='Yunseok.Codex.ModelChangeNotifier'` |
| **설정·옵션:** [`READ_BYTES`](src/notifier.py#L18)<br>**코드의 선언:** `정의=512 * 1024` |
| **설정·옵션:** [`MAX_RECORD`](src/notifier.py#L19)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`MAX_FILES`](src/notifier.py#L20)<br>**코드의 선언:** `정의=4096` |
| **설정·옵션:** [`LOG_BYTES`](src/notifier.py#L21)<br>**코드의 선언:** `정의=2 * 1024 * 1024` |
| **설정·옵션:** [`POLL_READ_BYTES`](src/notifier.py#L22)<br>**코드의 선언:** `정의=8 * 1024 * 1024` |
| **설정·옵션:** [`MAX_PENDING`](src/notifier.py#L23)<br>**코드의 선언:** `정의=256` |

**거부 조건:** [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L53)

**오류 메시지:** 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

**거부 조건:** [`self.state.get('schema_version') != 2`](src/notifier.py#L56)

**오류 메시지:** 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

**거부 조건:** [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L58)

**오류 메시지:** 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L60)

**오류 메시지:** 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

**거부 조건:** [`not isinstance(record, dict)`](src/notifier.py#L244)

**오류 메시지:** JSON 객체가 아닙니다.

**거부 조건:** [`path.stat().st_size &gt; 20000`](src/notifier.py#L306)

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

이 자료의 보존 범위와 기준 파일을 연결합니다.

[전체 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff)

추가·수정·삭제, 주석·공백·개행과 바이너리 크기·해시는 연결된 원래 비교 자료에서 확인합니다.

<details>
<summary>파일별 비교·크기·해시 자세히 보기</summary>

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

- **추가** `src/notifier.py`: 이전 없음; 현재 26813바이트, SHA-256 `2059fcac37723f34535eba05d83443a9dbd7e3dfb771200f190f2c8ed2ffb9a8`.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

</details>

[프로젝트](../../README.md) · [전체 차수](../../docs/REVISION_INDEX.md) · [원본 자료](.) · [다음: 2차 →](../02%EC%B0%A8/README.md)
