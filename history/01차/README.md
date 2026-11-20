<div align="center">

<a name="-codex-orbit--1차"></a>
# Codex Orbit·1차

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령 행 감 시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

**기술 분류:** Windows 데스크톱 · Python · 로컬 JSONL 감시

[핵심 기능](#features) · [사용 흐름](#usage) · [자료 구성](#structure) · [준비와 실행](#setup) · [결과 읽기](#results) · [직전 변경](#changes)

</div>
<!-- reading-levels:start -->
[LEVEL 1 - Beginner](#reading-level-1) · [LEVEL 2 - Explorer](#reading-level-2) · [LEVEL 3 - Practitioner](#reading-level-3) · [LEVEL 4 - Advanced](#reading-level-4) · [LEVEL 5 - Expert](#reading-level-5)

프로젝트 전체의 설명은 [LEVEL 1 - Beginner](../../docs/%EC%9D%BD%EA%B8%B0%EC%95%88%EB%82%B4/%EB%A0%88%EB%B2%A81.md)부터 [LEVEL 5 - Expert](../../docs/%EC%9D%BD%EA%B8%B0%EC%95%88%EB%82%B4/%EB%A0%88%EB%B2%A85.md)까지 같은 범위로 연결됩니다.

<a id="reading-level-1"></a>
## LEVEL 1 - Beginner

### LEVEL 1 · 이 자료가 하는 일과 달라진 점

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령 행 감 시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

### LEVEL 1 · 실제 동작을 따라 읽기

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령 행 감 시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

JSONL은 한 줄마다 하나의 JSON 기록을 담은 파일입니다. CLI는 명령어와 옵션을 입력해 프로그램을 실행하는 방식입니다.

입력 — 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정

처리 — 변경 감시 → 공개 이유·전후 모델 정리 → 알림

출력 — 알림·변경 이력·로컬 진단 기록

### LEVEL 1 · 준비하고 확인할 것

Windows에서 Python과 PowerShell을 준비합니다. 1차의 `src/notifier.py`는 Python 표준 라이브러리만 사용하므로 별도 pip 패키지를 설치하지 않습니다.

알림은 같은 차수의 `src/toast.ps1`을 호출하며, 이 보존본에는 `requirements.txt`와 GUI `app.py`가 없습니다.

이 차수에는 GUI app.py가 없습니다. `src/notifier.py`의 CLI에서 지정하는 경로로 감시기를 사용합니다. 인자 목록과 기본 경로는 아래 소스 설정 표에서 확인합니다.

#### LEVEL 1 · 소스에서 제공하는 CLI 옵션

| 진입 소스 | 옵션 |
| --- | --- |
| [notifier.py](src/notifier.py) | `--sessions`, `--work` |

각 옵션의 기본 값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 1 · [src/notifier.py](src/notifier.py)


| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L436) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L437) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L16) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L17) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L18) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L19) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L20) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L21) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L22) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L23) | `정의=256` |

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


### LEVEL 1·1차의 구체적인 기능과 확인

화면 창 없이 컴퓨터의 명령 입력 창에서 움직이는 첫 감 시기입니다.

Codex가 남기는 기록을 읽어 모델이나 생각하는 강도의 변경을 찾습니다.

JSONL은 한 줄에 한 건씩 적힌 기록 파일이고, 상태 JSON은 다음 감시 때 이어 읽기 위한 저장 자료입니다.

같은 감 시기를 겹쳐 실행하지 않도록 잠금을 두고 한 번에 읽는 양을 제한합니다.

**입력은 기록 파일, 출력은 알림과 이력입니다.** Codex의 sessions 폴더에는 이 사용자의 작업 기록이 쌓입니다.

앱이 새 기록을 읽으면 이전·이후 모델과 추론 강도, 적혀 있는 이유를 정리해 보여 줍니다.

JSON은 항목 이름과 값을 짝으로 저장하는 자료 형식입니다.

처음 읽은 기록을 출발점으로 삼는 것과 그 뒤 새로 생긴 변경을 알리는 것은 다릅니다.

Windows·Python·PowerShell을 준비합니다. 알림에는 같은 차수 [src/toast.ps1](src/toast.ps1)이 쓰입니다. 이 차수에는 requirements.txt와 GUI app.py가 없고 표준 라이브러리 감시기 [src/notifier.py](src/notifier.py)를 사용합니다.

확인 순서는 **같은 차수 자료 준비 → 감시 경로 확인 → 새 기록과 알림·상세 대조 → 누락값과 오류 확인**입니다. 예를 들어 기록에 모델 변경이 남았다면 알림의 이전·현재 값과 상세 이력을 비교합니다. 원문에 이유나 이전값이 없다면 모르는 상태로 읽고 채워 넣지 않습니다.

**자료를 찾는 순서**

- [src/](src): 관련 파일을 모아 둔 폴더.

- [README.md](README.md#reading-level-1): 설명을 읽는 Markdown 문서.

- [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json): 항목별 값을 저장한 자료.

- [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md): 설명을 읽는 Markdown 문서.

- [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json): 항목별 값을 저장한 자료.

- [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff): 전후 파일의 달라진 줄을 기록한 비교 자료.

- [src/notifier.py](src/notifier.py): 이 부분이 맡는 일은 다음과 같습니다. 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다.

**실제 입력·설정과 기본값**

아래 이름은 설정을 소스에서 찾기 위한 표지입니다.

각 항목의 역할·단위·적용 상황을 먼저 읽고 뒤의 원문 선언으로 정확한 숫자를 확인합니다.

식에 1024가 쓰이면 바이트 단위 크기 계산이며 1 KiB =1,024 바이트, 1 MiB =1,048,576 바이트입니다.

이 설명은 설정을 임의로 바꾸라는 실행 지시가 아닙니다.

- [`--sessions`](src/notifier.py#L436) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L437) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L16) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L17) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L18) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L19) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L20) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대 값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L21) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L22) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료 량을 제한합니다. 파일 하나의 상한과 별개 인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L23) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개 수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

**처리 책임과 원문에 명시된 함수 동작**

이 차수의 공개 설명에는 개별 함수 역할 표가 없습니다. 없는 함수 목록을 만들지 않고 아래 실제 CLI·읽기 상한·상태 거부 조건으로 입력과 결과를 확인합니다.

**멈추거나 거부되는 조건과 읽는 방법**

- 오류 “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”

  이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다.

큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다.

정확한 조건은 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L53) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.”

  옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다.

이를 새 관측 이력으로 자동 해석하지 않습니다.

명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다.

정확한 조건은 [`self.state.get('schema_version') != 2`](src/notifier.py#L56) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”

  저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다.

자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다.

정확한 조건은 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L58) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”

  어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다.

이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다.

정확한 조건은 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L60) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “JSON 객체가 아닙니다.”

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다.

예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다.

정확한 조건은 [`not isinstance(record, dict)`](src/notifier.py#L244) (src/notifier.py)에서 확인할 수 있습니다.

- 오류 “명시 알림 파일 상한 초과”

  명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다. 짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게하기 위한 크기 제한입니다. 정확한 조건은 [`path.stat().st_size &gt; 20000`](src/notifier.py#L306) (src/notifier.py)에서 확인할 수 있습니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다.

최초 기준 선 읽기와 새 변경은 다릅니다.

자산·글 꼴 오류라면 이 차수 assets와 라이선스를 대조합니다.

과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다.

이유·이전 값이 없으면 원 문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

최초 확인 소스로 직전 비교 대상이 없습니다. 최초 자료 범위는 연결된 비교 문서에 남아 있습니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **추가** [src/notifier.py](src/notifier.py): 이름 옆의 변화 종류를 기준으로 원래 파일과 달라진 내용을 읽습니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다.

원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다.

이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다.

Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


**지원 명령으로 읽기·저장 위치 확인하기**

1차에는 `app.py` 창이 없습니다.

이 차수 폴더의 PowerShell에서 아래 형식으로 명령행 감시기를 시작합니다. `python`은 준비한 Python 실행기를 뜻하며, `--sessions`는 읽을 기록 폴더, `--work`는 결과를 둘 폴더입니다.

아래는 사용자 홈의 기본 Codex 기록 위치를 읽고 차수 폴더의 work를 결과 위치로 고르는 사용 예이며 이 문서 작성 중 실제 실행한 명령은 아닙니다.

```powershell
python src/notifier.py --sessions "$env:USERPROFILE/.codex/sessions" --work "./work"
```

먼저 선택한 sessions 폴더에 실제 기록이 있는지, 같은 work를 쓰는 감 시기가 이미 실행 중이지 않은지 확인합니다.

같은 차수 `src/toast.ps1`도 알림 보조 파일로 필요합니다.

처음 읽은 과거 기록을 출발점으로 삼는 것과 그 뒤 새 기록을 발견하는 것은 다릅니다.

예를 들어 이후 기록에 모델 A →모델 B 변경이 실제로 생겼다면 감시기는 그 전후 값과 기록된 공개 이유를 알림·상태·진단에 연결합니다.

A와 B는 이해용 예시 이름이며 관측한 실제 모델·성능 수치가 아닙니다.

기록이 없거나 읽기 상한·형식 경계에 걸리면 새 변경이 있다고 추정하지 않습니다.

개인 세션 원본을 시험용으로 고치거나 오류를 없애려고 상태 파일을 지우지 말고 진단 원문을 먼저 확인합니다.

<a id="reading-level-2"></a>
## LEVEL 2 - Explorer

### LEVEL 2 · 목적과 구성의 연결

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령 행 감 시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령 행 감 시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

### LEVEL 2 · 입력에서 출력으로

| 단계 | 내용 |
| --- | --- |
| 입력 | 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정 |
| 처리 | 변경 감시 → 공개 이유·전후 모델 정리 → 알림 |
| 출력 | 알림·변경 이력·로컬 진단 기록 |


입력·처리·출력은 위의 같은 자료 흐름을 다른 단계에서 읽는 기준입니다. 처리 조건과 출력의 의미를 함께 확인합니다.

### LEVEL 2 · 설정과 처리 순서의 관계

1. `src/notifier.py`의 main과 CLI 인자를 읽어 sessions·work 경로를 확인합니다.
2. 본인 로컬 기록을 대상으로 시작하며 상태 파일과 진단 파일의 저장 위치를 구분합니다.
3. 첫 기준선 읽기 이후 새 변경을 관측하고 알림 기록을 확인합니다.

Windows에서 Python과 PowerShell을 준비합니다. 1차의 `src/notifier.py`는 Python 표준 라이브러리만 사용하므로 별도 pip 패키지를 설치하지 않습니다.

알림은 같은 차수의 `src/toast.ps1`을 호출하며, 이 보존본에는 `requirements.txt`와 GUI `app.py`가 없습니다.

이 차수에는 GUI app.py가 없습니다. `src/notifier.py`의 CLI에서 지정하는 경로로 감시기를 사용합니다. 인자 목록과 기본 경로는 아래 소스 설정 표에서 확인합니다.

#### LEVEL 2 · 소스에서 제공하는 CLI 옵션

| 진입 소스 | 옵션 |
| --- | --- |
| [notifier.py](src/notifier.py) | `--sessions`, `--work` |

각 옵션의 기본 값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 2 · [src/notifier.py](src/notifier.py)


| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L436) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L437) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L16) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L17) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L18) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L19) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L20) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L21) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L22) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L23) | `정의=256` |

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


### LEVEL 2·1차의 구체적인 기능과 확인

기록 수집과 알림 전달이 연결되는 최초 구조입니다. 파일의 새 기록을 읽는 경로와 명시적으로 배정을 알리는 경로를 구별하며, 상태 보존으로 다음 조회의 출발점을 관리합니다. 읽기 상한과 잠금은 여러 파일·여러 실행이 겹치는 조건의 경계입니다.

**수집·해석·표시·보존**을 연결해 읽습니다. 로컬 JSONL의 관측 변경과 명시된 배정은 다른 종류의 근거입니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

Windows·Python·PowerShell을 준비합니다. 알림에는 같은 차수 [src/toast.ps1](src/toast.ps1)이 쓰입니다. 이 차수에는 requirements.txt와 GUI app.py가 없고 표준 라이브러리 감시기 [src/notifier.py](src/notifier.py)를 사용합니다.

아래 구성·설정·거부 조건은 이 연결이 성립하는 실제 조건입니다. 자료가 처음 기준선으로 읽힌 것인지 새 변경인지, 표시에 필요한 이전값이 존재하는지를 함께 판단합니다.

**자료 경계와 모듈 연결**

- [src/](src): 관련 파일을 모아 둔 폴더.

- [README.md](README.md#reading-level-2): 설명을 읽는 Markdown 문서.

- [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json): 항목별 값을 저장한 자료.

- [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md): 설명을 읽는 Markdown 문서.

- [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json): 항목별 값을 저장한 자료.

- [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff): 전후 파일의 달라진 줄을 기록한 비교 자료.

- [src/notifier.py](src/notifier.py): 연결 구조에서의 역할은 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다.

**실제 입력·설정과 기본값**

- [`--sessions`](src/notifier.py#L436) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L437) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L16) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L17) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L18) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L19) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L20) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대 값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L21) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L22) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료 량을 제한합니다. 파일 하나의 상한과 별개 인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L23) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개 수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

**처리 책임과 원문에 명시된 함수 동작**

이 차수의 공개 설명에는 개별 함수 역할 표가 없습니다. 없는 함수 목록을 만들지 않고 아래 실제 CLI·읽기 상한·상태 거부 조건으로 입력과 결과를 확인합니다.

**멈추거나 거부되는 조건과 읽는 방법**

- [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L53) (src/notifier.py)

  이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다. 큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다. 원문 오류: “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”입니다.

- [`self.state.get('schema_version') != 2`](src/notifier.py#L56) (src/notifier.py)

  옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다.

이를 새 관측 이력으로 자동 해석하지 않습니다.

명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다.

원문 오류: “구형 상태는 요청과 관측이 혼합되어 있습니다.

원본 보존 후 명시적 재기준선이 필요합니다.”입니다.

- [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L58) (src/notifier.py)

  저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다. 자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다. 원문 오류: “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”입니다.

- [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L60) (src/notifier.py)

  어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다. 이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다. 원문 오류: “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”입니다.

- [`not isinstance(record, dict)`](src/notifier.py#L244) (src/notifier.py)

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다. 원문 오류: “JSON 객체가 아닙니다.”입니다.

- [`path.stat().st_size &gt; 20000`](src/notifier.py#L306) (src/notifier.py)

  명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다. 짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게하기 위한 크기 제한입니다. 원문 오류: “명 시 알림 파일 상한 초과”입니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다.

최초 기준 선 읽기와 새 변경은 다릅니다.

자산·글 꼴 오류라면 이 차수 assets와 라이선스를 대조합니다.

과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다.

이유·이전 값이 없으면 원 문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

최초 확인 소스로 직전 비교 대상이 없습니다. 최초 자료 범위는 연결된 비교 문서에 남아 있습니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **추가** [src/notifier.py](src/notifier.py): 전체 비교에서 기능 연결의 실제 변경을 확인합니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다.

원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다.

이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다.

Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


**이 수준에서 연결·실행·설계를 대조하는 순서**

선언의 정확한 코드와 전체 역할 원문은 LEVEL 5 및 연결된 소스에 보존합니다. 입력 사례는 검토 방법을 설명하며 실제 실행 결과가 아닙니다. 옵션 지정·기본값과 정상·거부 사례를 구분하고, 변경 시 호출자·공유 상태·표시 조건에 미치는 영향을 대조합니다.

- [src/notifier.py](src/notifier.py): 로컬 기록에서 관측한 값과 명시 배정 자료가 구분돼 알림·상태 저장으로 이어집니다. 한 번에 읽는 양과 저장 상태의 형식은 이 연결을 제한하는 조건입니다.


**지원 명령으로 읽기·저장 위치 확인하기**

1차에는 `app.py` 창이 없습니다.

이 차수 폴더의 PowerShell에서 아래 형식으로 명령행 감시기를 시작합니다. `python`은 준비한 Python 실행기를 뜻하며, `--sessions`는 읽을 기록 폴더, `--work`는 결과를 둘 폴더입니다.

아래는 사용자 홈의 기본 Codex 기록 위치를 읽고 차수 폴더의 work를 결과 위치로 고르는 사용 예이며 이 문서 작성 중 실제 실행한 명령은 아닙니다.

```powershell
python src/notifier.py --sessions "$env:USERPROFILE/.codex/sessions" --work "./work"
```

먼저 선택한 sessions 폴더에 실제 기록이 있는지, 같은 work를 쓰는 감 시기가 이미 실행 중이지 않은지 확인합니다.

같은 차수 `src/toast.ps1`도 알림 보조 파일로 필요합니다.

처음 읽은 과거 기록을 출발점으로 삼는 것과 그 뒤 새 기록을 발견하는 것은 다릅니다.

예를 들어 이후 기록에 모델 A →모델 B 변경이 실제로 생겼다면 감시기는 그 전후 값과 기록된 공개 이유를 알림·상태·진단에 연결합니다.

A와 B는 이해용 예시 이름이며 관측한 실제 모델·성능 수치가 아닙니다.

기록이 없거나 읽기 상한·형식 경계에 걸리면 새 변경이 있다고 추정하지 않습니다.

개인 세션 원본을 시험용으로 고치거나 오류를 없애려고 상태 파일을 지우지 말고 진단 원문을 먼저 확인합니다.

<a id="reading-level-3"></a>
## LEVEL 3 - Practitioner

### LEVEL 3 · 이 차수를 준비하는 범위

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령 행 감 시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

Windows에서 Python과 PowerShell을 준비합니다. 1차의 `src/notifier.py`는 Python 표준 라이브러리만 사용하므로 별도 pip 패키지를 설치하지 않습니다.

알림은 같은 차수의 `src/toast.ps1`을 호출하며, 이 보존본에는 `requirements.txt`와 GUI `app.py`가 없습니다.

이 차수에는 GUI app.py가 없습니다. `src/notifier.py`의 CLI에서 지정하는 경로로 감시기를 사용합니다. 인자 목록과 기본 경로는 아래 소스 설정 표에서 확인합니다.

#### LEVEL 3 · 소스에서 제공하는 CLI 옵션

| 진입 소스 | 옵션 |
| --- | --- |
| [notifier.py](src/notifier.py) | `--sessions`, `--work` |

각 옵션의 기본 값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 3 · [src/notifier.py](src/notifier.py)


| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L436) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L437) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L16) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L17) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L18) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L19) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L20) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L21) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L22) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L23) | `정의=256` |

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

| 단계 | 내용 |
| --- | --- |
| 입력 | 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정 |
| 처리 | 변경 감시 → 공개 이유·전후 모델 정리 → 알림 |
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

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령 행 감 시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

[자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)


### LEVEL 3·1차의 구체적인 기능과 확인

Windows의 Python·PowerShell을 준비하고 src/notifier.py와 같은 차수의 src/toast.ps1을 함께 둡니다. 별도 pip 의존성이나 GUI app.py는 없습니다. --sessions로 읽을 세션 폴더, --work로 결과 저장 위치를 지정하는 CLI 정의를 확인한 후 실행합니다.

Windows·Python·PowerShell을 준비합니다. 알림에는 같은 차수 [src/toast.ps1](src/toast.ps1)이 쓰입니다. 이 차수에는 requirements.txt와 GUI app.py가 없고 표준 라이브러리 감시기 [src/notifier.py](src/notifier.py)를 사용합니다.

입력은 현재 사용자의 sessions JSONL과 앱 설정입니다. **경로·자산·설정 먼저 확인한 뒤 실행**하고, 알림·변경 이력·로컬 진단을 원본 사건과 대조합니다. 동작 확인에서 모델 전후·추론 전후·이유·시각·근거 수준을 함께 읽고 미기록은 미확인으로 남깁니다.

아래 옵션은 실제 소스에 선언된 이름입니다. CLI는 명령 뒤에 옵션을 붙이는 방식이며 각 기본값·부작용은 해당 선언과 함께 확인합니다. smoke라는 이름은 점검용 실행을 뜻하며 이 문서가 그 실행을 대신 수행했다는 뜻은 아닙니다.

**자료를 찾는 순서**

- [src/](src): 관련 파일을 모아 둔 폴더.

- [README.md](README.md#reading-level-3): 설명을 읽는 Markdown 문서.

- [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json): 항목별 값을 저장한 자료.

- [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md): 설명을 읽는 Markdown 문서.

- [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json): 항목별 값을 저장한 자료.

- [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff): 전후 파일의 달라진 줄을 기록한 비교 자료.

- [src/notifier.py](src/notifier.py): 실행 자료를 점검할 때 확인할 책임은 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다.

**실제 입력·설정과 기본값**

- [`--sessions`](src/notifier.py#L436) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L437) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L16) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L17) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L18) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L19) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L20) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대 값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L21) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L22) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료 량을 제한합니다. 파일 하나의 상한과 별개 인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L23) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개 수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

**처리 책임과 원문에 명시된 함수 동작**

이 차수의 공개 설명에는 개별 함수 역할 표가 없습니다. 없는 함수 목록을 만들지 않고 아래 실제 CLI·읽기 상한·상태 거부 조건으로 입력과 결과를 확인합니다.

**멈추거나 거부되는 조건과 읽는 방법**

- 오류 “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”

  입력 사례와 확인 순서: 이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다.

큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다.

원문 조건 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L53) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.”

  입력 사례와 확인 순서: 옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다.

이를 새 관측 이력으로 자동 해석하지 않습니다.

명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다.

원문 조건 [`self.state.get('schema_version') != 2`](src/notifier.py#L56) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”

  입력 사례와 확인 순서: 저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다.

자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다.

원문 조건 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L58) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”

  입력 사례와 확인 순서: 어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다.

이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다.

원문 조건 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L60) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “JSON 객체가 아닙니다.”

  입력 사례와 확인 순서: 한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다.

예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다.

원문 조건 [`not isinstance(record, dict)`](src/notifier.py#L244) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

- 오류 “명시 알림 파일 상한 초과”

  입력 사례와 확인 순서: 명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다.

짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게하기 위한 크기 제한입니다.

원문 조건 [`path.stat().st_size &gt; 20000`](src/notifier.py#L306) (src/notifier.py)와 준비한 입력을 대조해, 어느 조건이 거부됐는지를 기록합니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다.

최초 기준 선 읽기와 새 변경은 다릅니다.

자산·글 꼴 오류라면 이 차수 assets와 라이선스를 대조합니다.

과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다.

이유·이전 값이 없으면 원 문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

최초 확인 소스로 직전 비교 대상이 없습니다. 최초 자료 범위는 연결된 비교 문서에 남아 있습니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **추가** [src/notifier.py](src/notifier.py): 실행 자료에 이 변경이 반영되어 있는지 대조합니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다.

원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다.

이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다.

Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


**이 수준에서 연결·실행·설계를 대조하는 순서**

선언의 정확한 코드와 전체 역할 원문은 LEVEL 5 및 연결된 소스에 보존합니다. 입력 사례는 검토 방법을 설명하며 실제 실행 결과가 아닙니다. 옵션 지정·기본값과 정상·거부 사례를 구분하고, 변경 시 호출자·공유 상태·표시 조건에 미치는 영향을 대조합니다.

- [src/notifier.py](src/notifier.py): 처음 읽는 기준선과 뒤에 새로 생긴 기록을 다른 입력 사례로 준비합니다. 감시 경로와 파일·레코드 상한, 저장 상태의 형식 거부 조건을 대조합니다.


**지원 명령으로 읽기·저장 위치 확인하기**

1차에는 `app.py` 창이 없습니다.

이 차수 폴더의 PowerShell에서 아래 형식으로 명령행 감시기를 시작합니다. `python`은 준비한 Python 실행기를 뜻하며, `--sessions`는 읽을 기록 폴더, `--work`는 결과를 둘 폴더입니다.

아래는 사용자 홈의 기본 Codex 기록 위치를 읽고 차수 폴더의 work를 결과 위치로 고르는 사용 예이며 이 문서 작성 중 실제 실행한 명령은 아닙니다.

```powershell
python src/notifier.py --sessions "$env:USERPROFILE/.codex/sessions" --work "./work"
```

먼저 선택한 sessions 폴더에 실제 기록이 있는지, 같은 work를 쓰는 감 시기가 이미 실행 중이지 않은지 확인합니다.

같은 차수 `src/toast.ps1`도 알림 보조 파일로 필요합니다.

처음 읽은 과거 기록을 출발점으로 삼는 것과 그 뒤 새 기록을 발견하는 것은 다릅니다.

예를 들어 이후 기록에 모델 A →모델 B 변경이 실제로 생겼다면 감시기는 그 전후 값과 기록된 공개 이유를 알림·상태·진단에 연결합니다.

A와 B는 이해용 예시 이름이며 관측한 실제 모델·성능 수치가 아닙니다.

기록이 없거나 읽기 상한·형식 경계에 걸리면 새 변경이 있다고 추정하지 않습니다.

개인 세션 원본을 시험용으로 고치거나 오류를 없애려고 상태 파일을 지우지 말고 진단 원문을 먼저 확인합니다.

<a id="reading-level-4"></a>
## LEVEL 4 - Advanced

### LEVEL 4 · 설계 의도와 검토 경계

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령 행 감 시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령 행 감 시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.

### LEVEL 4 · 이 차수 구현의 실제 근거

| 파일 | 역할·구성 |
| --- | --- |
| [src/notifier.py](src/notifier.py) | 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기.<br>외부 통신은 하지 않습니다. |

| 단계 | 내용 |
| --- | --- |
| 입력 | 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정 |
| 처리 | 변경 감시 → 공개 이유·전후 모델 정리 → 알림 |
| 출력 | 알림·변경 이력·로컬 진단 기록 |


### LEVEL 4 · 조건·변경·결과를 함께 검토하기

Windows에서 Python과 PowerShell을 준비합니다. 1차의 `src/notifier.py`는 Python 표준 라이브러리만 사용하므로 별도 pip 패키지를 설치하지 않습니다.

알림은 같은 차수의 `src/toast.ps1`을 호출하며, 이 보존본에는 `requirements.txt`와 GUI `app.py`가 없습니다.

이 차수에는 GUI app.py가 없습니다. `src/notifier.py`의 CLI에서 지정하는 경로로 감시기를 사용합니다. 인자 목록과 기본 경로는 아래 소스 설정 표에서 확인합니다.

#### LEVEL 4 · 소스에서 제공하는 CLI 옵션

| 진입 소스 | 옵션 |
| --- | --- |
| [notifier.py](src/notifier.py) | `--sessions`, `--work` |

각 옵션의 기본 값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

#### LEVEL 4 · [src/notifier.py](src/notifier.py)


| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L436) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L437) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L16) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L17) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L18) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L19) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L20) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L21) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L22) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L23) | `정의=256` |

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


### LEVEL 4·1차의 구체적인 기능과 확인

src/notifier.py가 수집·상태·명시 배정·알림 연계를 맡는 단일 진입 구조입니다. GUI를 전제해 app.py를 추가 실행하면 보존 본과 다른 실행 조건이 됩니다. 파일·레코드·poll 읽기량·대기량 경계와 상태 버전 검사를 함께 검토해야 합니다.

**로컬 수집 경계와 UI·명시적 파일 작업의 경계**를 분리합니다. JSONL 입력에서 변경 감지·공개 이유 정리·알림·상세 표시로 이어지고, 설정·이력·진단은 로컬 운영 자료입니다. 관측된 변경과 명시 배정의 근거를 혼합하지 않습니다.

Windows·Python·PowerShell을 준비합니다. 알림에는 같은 차수 [src/toast.ps1](src/toast.ps1)이 쓰입니다. 이 차수에는 requirements.txt와 GUI app.py가 없고 표준 라이브러리 감시기 [src/notifier.py](src/notifier.py)를 사용합니다.

아래 모듈·선언·거부 조건은 변경 영향 검토의 출발점입니다. 이름·상수만으로 전체 호출 순서나 예외 전파를 추정하지 말고 연결된 코드에서 분기와 호출자를 대조합니다.

**자료 경계와 모듈 연결**

- [src/](src): 관련 파일을 모아 둔 폴더.

- [README.md](README.md#reading-level-4): 설명을 읽는 Markdown 문서.

- [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json): 항목별 값을 저장한 자료.

- [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md): 설명을 읽는 Markdown 문서.

- [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json): 항목별 값을 저장한 자료.

- [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff): 전후 파일의 달라진 줄을 기록한 비교 자료.

- [src/notifier.py](src/notifier.py): 모듈 책임: 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다.

**실제 입력·설정과 기본값**

- [`--sessions`](src/notifier.py#L436) (src/notifier.py)

  Codex 기록이 쌓이는 폴더 경로를 지정합니다. 예시에서 고른 폴더 안에 실제 새 JSONL 기록이 있어야 하며 경로 문자열만 지정해 새 사건이 생기는 것은 아닙니다. 원문 선언: `type=Path; default=Path.home() / '.codex/sessions'`.

- [`--work`](src/notifier.py#L437) (src/notifier.py)

  감시기가 결과·상태를 둘 작업 폴더 경로를 지정합니다. 읽을 세션 위치와 쓰는 결과 위치를 구분하는 옵션입니다. 원문 선언: `type=Path; default=ROOT / 'work'`.

- [`ROOT`](src/notifier.py#L16) (src/notifier.py)

  파일을 어디서 실행했는지가 아니라 이 소스 파일의 위치를 기준으로 앱 폴더를 잡습니다. 저장·보조 파일의 기준이 작업 창의 현재 폴더 때문에 달라지지 않게 하는 설정입니다. 원문 선언: `정의=Path(__file__).resolve().parents[1]`.

- [`APP_ID`](src/notifier.py#L17) (src/notifier.py)

  Windows 알림이 어느 앱에서 온 것인지 구분하는 고정 이름입니다. 알림의 출처 표시에 쓰며 계정 이름이나 실제 실행 모델 ID가 아닙니다. 원문 선언: `정의='Yunseok.Codex.ModelChangeNotifier'`.

- [`READ_BYTES`](src/notifier.py#L18) (src/notifier.py)

  한 번에 한 파일에서 읽는 양을 제한합니다. 단위는 바이트로, 큰 기록 파일 전체를 한 번에 들이지 않게하는 경계입니다. 계산한 값은 524,288이며 바이트 제한에서는 512 KiB입니다. 원문 선언: `정의=512 * 1024`.

- [`MAX_RECORD`](src/notifier.py#L19) (src/notifier.py)

  기록 한 건이 가질 수 있는 최대 크기입니다. 커다란 한 줄을 무제한으로 해석하지 않도록하는 제한이며 단위는 바이트입니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`MAX_FILES`](src/notifier.py#L20) (src/notifier.py)

  감시에서 다룰 파일 개수의 최대 값입니다. 폴더가 커져도 파일 목록을 제한 없이 늘리지 않게합니다. 계산한 값은 4,096입니다. 원문 선언: `정의=4096`.

- [`LOG_BYTES`](src/notifier.py#L21) (src/notifier.py)

  진단 기록의 크기 상한입니다. 단위는 바이트이며 문제가 반복될 때 기록이 끝없이 커지는 경계와 관계됩니다. 계산한 값은 2,097,152이며 바이트 제한에서는 2,048 KiB입니다. 원문 선언: `정의=2 * 1024 * 1024`.

- [`POLL_READ_BYTES`](src/notifier.py#L22) (src/notifier.py)

  감시 한 차례에서 읽을 전체 자료 량을 제한합니다. 파일 하나의 상한과 별개 인 바이트 단위 총량이므로 여러 파일을 합친 부담을 구분합니다. 계산한 값은 8,388,608이며 바이트 제한에서는 8,192 KiB입니다. 원문 선언: `정의=8 * 1024 * 1024`.

- [`MAX_PENDING`](src/notifier.py#L23) (src/notifier.py)

  처리가 끝나기를 기다리는 기록 개 수의 상한입니다. 숫자는 프레임 수나 토큰 수가 아니라 대기 항목 수입니다. 선언 숫자는 256입니다. 원문 선언: `정의=256`.

**처리 책임과 원문에 명시된 함수 동작**

이 차수의 공개 설명에는 개별 함수 역할 표가 없습니다. 없는 함수 목록을 만들지 않고 아래 실제 CLI·읽기 상한·상태 거부 조건으로 입력과 결과를 확인합니다.

**멈추거나 거부되는 조건과 읽는 방법**

- 거부 분기 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L53) (src/notifier.py) → 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.

  이어 읽기 위치와 관측값을 저장한 파일이 16 MiB를 넘으면 읽기를 정상으로 계속하지 않습니다. 큰 파일을 무제한으로 처리하지 않기 위한 제한이며 원본을 남기고 왜 커졌는지 확인해야 합니다.

- 거부 분기 [`self.state.get('schema_version') != 2`](src/notifier.py#L56) (src/notifier.py) → 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.

  옛 저장 형식에는 모델을 쓰겠다는 요청과 실제로 관측한 값이 섞여 있습니다. 이를 새 관측 이력으로 자동 해석하지 않습니다. 명시적 재기준선은 원본을 보존한 상태에서 어느 기록부터 현재 관측의 출발점으로 삼을지 따로 정하는 절차이며 오류를 없애려고 상태를 삭제하는 뜻이 아닙니다.

- 거부 분기 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L58) (src/notifier.py) → 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.

  저장 자료의 files·models 같은 이름별 항목이 기대한 사전 형태가 아니면 다음 읽기 위치나 관측값을 안전하게 복원할 수 없어 거부합니다. 자료 구조는 이름과 값이 대응하는 저장 형식이며 빈 파일로 자동 바꾸지 않습니다.

- 거부 분기 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L60) (src/notifier.py) → 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.

  어떤 모델을 맡기겠다고 알린 배정 자료가 기대한 이름별 사전이 아니면 거부합니다. 이 자료를 지우고 새 실제 관측처럼 처리하지 않아 요청과 관측의 구분을 보존합니다.

- 거부 분기 [`not isinstance(record, dict)`](src/notifier.py#L244) (src/notifier.py) → JSON 객체가 아닙니다.

  한 건의 기록은 항목 이름과 값이 짝지어진 객체여야 합니다. 예를 들어 숫자 하나나 문자열만 온 경우 이름별 필드를 읽을 수 없어 정상 기록으로 받지 않습니다.

- 거부 분기 [`path.stat().st_size &gt; 20000`](src/notifier.py#L306) (src/notifier.py) → 명시 알림 파일 상한 초과

  명시 배정 알림 파일이 20,000바이트를 넘으면 거부합니다. 짧은 알림 전달 파일을 큰 본문 저장소처럼 읽지 않게하기 위한 크기 제한입니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다.

최초 기준 선 읽기와 새 변경은 다릅니다.

자산·글 꼴 오류라면 이 차수 assets와 라이선스를 대조합니다.

과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다.

이유·이전 값이 없으면 원 문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

최초 확인 소스로 직전 비교 대상이 없습니다. 최초 자료 범위는 연결된 비교 문서에 남아 있습니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **추가** [src/notifier.py](src/notifier.py): 변경 영향은 연결된 전체 diff의 실제 분기로 한정합니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다.

원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다.

이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다.

Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


**이 수준에서 연결·실행·설계를 대조하는 순서**

선언의 정확한 코드와 전체 역할 원문은 LEVEL 5 및 연결된 소스에 보존합니다. 입력 사례는 검토 방법을 설명하며 실제 실행 결과가 아닙니다. 옵션 지정·기본값과 정상·거부 사례를 구분하고, 변경 시 호출자·공유 상태·표시 조건에 미치는 영향을 대조합니다.

- [src/notifier.py](src/notifier.py): 상태 저장과 읽기 위치 변경은 과거 사건 재생·누락·중복에 영향을 줄 수 있습니다. 명시 배정과 관측의 구분 및 손상 상태의 원본 보존을 유지해야 합니다.


**지원 명령으로 읽기·저장 위치 확인하기**

1차에는 `app.py` 창이 없습니다.

이 차수 폴더의 PowerShell에서 아래 형식으로 명령행 감시기를 시작합니다. `python`은 준비한 Python 실행기를 뜻하며, `--sessions`는 읽을 기록 폴더, `--work`는 결과를 둘 폴더입니다.

아래는 사용자 홈의 기본 Codex 기록 위치를 읽고 차수 폴더의 work를 결과 위치로 고르는 사용 예이며 이 문서 작성 중 실제 실행한 명령은 아닙니다.

```powershell
python src/notifier.py --sessions "$env:USERPROFILE/.codex/sessions" --work "./work"
```

먼저 선택한 sessions 폴더에 실제 기록이 있는지, 같은 work를 쓰는 감 시기가 이미 실행 중이지 않은지 확인합니다.

같은 차수 `src/toast.ps1`도 알림 보조 파일로 필요합니다.

처음 읽은 과거 기록을 출발점으로 삼는 것과 그 뒤 새 기록을 발견하는 것은 다릅니다.

예를 들어 이후 기록에 모델 A →모델 B 변경이 실제로 생겼다면 감시기는 그 전후 값과 기록된 공개 이유를 알림·상태·진단에 연결합니다.

A와 B는 이해용 예시 이름이며 관측한 실제 모델·성능 수치가 아닙니다.

기록이 없거나 읽기 상한·형식 경계에 걸리면 새 변경이 있다고 추정하지 않습니다.

개인 세션 원본을 시험용으로 고치거나 오류를 없애려고 상태 파일을 지우지 말고 진단 원문을 먼저 확인합니다.

<a id="reading-level-5"></a>
## LEVEL 5 - Expert


### LEVEL 5·1차의 구체적인 기능과 확인

최초 확인 소스여서 직전 개발 차수의 성능 비교 기준은 없습니다. 공개 이력의 notifier.py 추가와 바이트 비교가 근거이며, 당시 실행 결과는 보존되지 않았습니다. 입력 스키마·LF 경계·상태 스키마 거부 조건의 재현과 알림 도구 의존성은 각각 독립 검토 대상입니다.

**증거의 범위는 이 차수 공개 원문과 보존 소스입니다.** 로컬 기록의 모델·추론 값은 서버가 보증한 모델 신원 인증이 아닙니다. 원문에 없는 이유·이전 값·실행 성과는 보 간하지 않습니다. 입력은 현재 사용자 JSONL과 설정, 출력은 알림·이력·로컬 진단이며 관측 변경과 명시 배정은 다른 증거 종류입니다.

Windows·Python·PowerShell을 준비합니다. 알림에는 같은 차수 [src/toast.ps1](src/toast.ps1)이 쓰입니다. 이 차수에는 requirements.txt와 GUI app.py가 없고 표준 라이브러리 감시기 [src/notifier.py](src/notifier.py)를 사용합니다.

재현에는 동일 차수 의존성·자산·입력·설정·실행 표면이 필요합니다. 아래 선언의 상한·스키마·거부 분기는 검토 가능한 소스 조건이며, 실제 부하·종료·화면 동작의 성공 증거와 구분합니다.

**자료 경계와 모듈 연결**

- [src/](src): 관련 파일을 모아 둔 폴더.

- [README.md](README.md): 설명을 읽는 Markdown 문서.

- [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json): 항목별 값을 저장한 자료.

- [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md): 설명을 읽는 Markdown 문서.

- [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json): 항목별 값을 저장한 자료.

- [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff): 전후 파일의 달라진 줄을 기록한 비교 자료.

- [src/notifier.py](src/notifier.py): 원문 모듈 역할 선언: 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다.

**실제 입력·설정과 기본값**

- [notifier.py](src/notifier.py)에서 사용할 수 있는 옵션: `--sessions`, `--work`.

- 재현 시 대조할 원문 선언 [`--sessions`](src/notifier.py#L436) (src/notifier.py): `type=Path; default=Path.home() / '.codex/sessions'`.

- 재현 시 대조할 원문 선언 [`--work`](src/notifier.py#L437) (src/notifier.py): `type=Path; default=ROOT / 'work'`.

- 재현 시 대조할 원문 선언 [`ROOT`](src/notifier.py#L16) (src/notifier.py): `정의=Path(__file__).resolve().parents[1]`.

- 재현 시 대조할 원문 선언 [`APP_ID`](src/notifier.py#L17) (src/notifier.py): `정의='Yunseok.Codex.ModelChangeNotifier'`.

- 재현 시 대조할 원문 선언 [`READ_BYTES`](src/notifier.py#L18) (src/notifier.py): `정의=512 * 1024`.

- 재현 시 대조할 원문 선언 [`MAX_RECORD`](src/notifier.py#L19) (src/notifier.py): `정의=2 * 1024 * 1024`.

- 재현 시 대조할 원문 선언 [`MAX_FILES`](src/notifier.py#L20) (src/notifier.py): `정의=4096`.

- 재현 시 대조할 원문 선언 [`LOG_BYTES`](src/notifier.py#L21) (src/notifier.py): `정의=2 * 1024 * 1024`.

- 재현 시 대조할 원문 선언 [`POLL_READ_BYTES`](src/notifier.py#L22) (src/notifier.py): `정의=8 * 1024 * 1024`.

- 재현 시 대조할 원문 선언 [`MAX_PENDING`](src/notifier.py#L23) (src/notifier.py): `정의=256`.

**처리 책임과 원문에 명시된 함수 동작**

**멈추거나 거부되는 조건과 읽는 방법**

- 경계 사례 [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L53) (src/notifier.py): 원문 오류는 “상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`self.state.get('schema_version') != 2`](src/notifier.py#L56) (src/notifier.py): 원문 오류는 “구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L58) (src/notifier.py): 원문 오류는 “상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L60) (src/notifier.py): 원문 오류는 “명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`not isinstance(record, dict)`](src/notifier.py#L244) (src/notifier.py): 원문 오류는 “JSON 객체가 아닙니다.”. 허용 입력과 구분해 재현할 조건입니다.

- 경계 사례 [`path.stat().st_size &gt; 20000`](src/notifier.py#L306) (src/notifier.py): 원문 오류는 “명시 알림 파일 상한 초과”. 허용 입력과 구분해 재현할 조건입니다.

**알림이 없거나 값이 비어 있을 때**: 감시 sessions 경로·새 JSONL 기록·중복 실행 잠금·알림 설정을 순서대로 확인합니다.

최초 기준 선 읽기와 새 변경은 다릅니다.

자산·글 꼴 오류라면 이 차수 assets와 라이선스를 대조합니다.

과거 대용량 프레임 자산이 소스 이력에 없을 수 있습니다.

이유·이전 값이 없으면 원 문 필드를 확인하며 동기를 추정하지 않습니다.

설정·이력·로컬 진단은 개인 운영자료입니다. 다른 사람에게 공유하기 전에 포함된 내용을 확인합니다. **로컬 기록은 서버 모델 신원 증명이 아닙니다.**

**직전 비교와 확인된 결과**

최초 확인 소스로 직전 비교 대상이 없습니다. 최초 자료 범위는 연결된 비교 문서에 남아 있습니다. [전체 변경](직전차수.diff)과 [파일별 바이트·해시 명세](공개파일_비교.json)를 함께 읽습니다. SHA-256은 같은 파일 내용인지 대조하는 지문이며 실행 성공 점수가 아닙니다.

이 비교에서 확인되는 추가·수정·삭제 파일은 다음과 같습니다. 한 줄·주석·공백·개행의 세부 차이는 전체 diff에, 바이너리의 크기·해시는 비교 명세에 보존됩니다.

- **추가** [src/notifier.py](src/notifier.py): 공개 바이트 비교에서 분류된 변경이며 의도·성능을 추정하지 않습니다.

**당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다.** 여기서 확인된 것은 공개 소스 바이트 비교입니다.

원문에는 현재 소스 사본에 `git -c core.autocrlf=false apply --reverse --binary -p1`을 적용해 직전 소스의 부재·추가·삭제까지 복원하여 바이트 대조했다고 적혀 있습니다.

이는 과거 앱 실행 성공이나 성능 측정을 뜻하지 않습니다.

Python 외에 존재하는 보조 PowerShell·의존성 목록도 비교에 포함하며 부가 자료는 별도 명세로 구분합니다.

[부가자료 원문 안내](보존자료.md)와 [부가자료 보존 명세](부가자료_보존.json)는 실행 소스 비교와 역할을 나눠 읽습니다.


기존의 전체 설명·표·코드·함수 참조·파일별 비교는 아래에 그대로 이어집니다. [자료 폴더](.) · [직전 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) · [이 차수의 원래 전체 상세](#reading-level-5)
<!-- reading-levels:end -->


[프로젝트](../../README.md) · [전체 차수](../../docs/REVISION_INDEX.md) · [원본 자료](.) · [다음: 2차 →](../02%EC%B0%A8/README.md)

<a name="-목적과-이-차수의-역할"></a>
## 목적과 이 차수의 역할

현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령 행 감 시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

<a name="features"></a>

<a name="-핵심-기능과-보존-범위"></a>
## 핵심 기능과 보존 범위

**항목:** 1

**이 차수에서 확인할 내용:** 현재 사용자 세션 JSONL을 감시하고 상태 JSON·알림·진단 JSONL을 관리하는 초기 명령 행 감 시기입니다. 중복 실행 잠금과 파일·레코드 읽기 상한을 둡니다.

**항목:** 2

**이 차수에서 확인할 내용:** 로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다.


<a name="-입력처리출력"></a>
## 입력·처리·출력

| 단계 | 내용 |
| --- | --- |
| 입력 | 현재 사용자 Codex의 로컬 JSONL과 이 차수의 앱 설정 |
| 처리 | 변경 감시 → 공개 이유·전후 모델 정리 → 알림 |
| 출력 | 알림·변경 이력·로컬 진단 기록 |


<a name="usage"></a>

<a name="️-화면과-사용-흐름"></a>
## 화면과 사용 흐름

1. `src/notifier.py`의 main과 CLI 인자를 읽어 sessions·work 경로를 확인합니다.
2. 본인 로컬 기록을 대상으로 시작하며 상태 파일과 진단 파일의 저장 위치를 구분합니다.
3. 첫 기준선 읽기 이후 새 변경을 관측하고 알림 기록을 확인합니다.

<a name="structure"></a>

<a name="-실제-자료-구성"></a>
## 실제 자료 구성

| 경로 | 자료 종류 |
| --- | --- |
| [src/](src) | 하위 자료 폴더 |
| [README.md](README.md) | MD 파일 |
| [공개파일_비교.json](%EA%B3%B5%EA%B0%9C%ED%8C%8C%EC%9D%BC_%EB%B9%84%EA%B5%90.json) | JSON 파일 |
| [보존자료.md](%EB%B3%B4%EC%A1%B4%EC%9E%90%EB%A3%8C.md) | MD 파일 |
| [부가자료_보존.json](%EB%B6%80%EA%B0%80%EC%9E%90%EB%A3%8C_%EB%B3%B4%EC%A1%B4.json) | JSON 파일 |
| [직전차수.diff](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff) | DIFF 파일 |

<a name="-주요-모듈과-코드-읽기"></a>
## 주요 모듈과 코드 읽기

| 파일 | 역할·구성 |
| --- | --- |
| [src/notifier.py](src/notifier.py) | 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기.<br>외부 통신은 하지 않습니다. |

<a name="setup"></a>

<a name="-설치-환경과-실행사용법"></a>
## 설치 환경과 실행·사용법

Windows에서 Python과 PowerShell을 준비합니다. 1차의 `src/notifier.py`는 Python 표준 라이브러리만 사용하므로 별도 pip 패키지를 설치하지 않습니다.

알림은 같은 차수의 `src/toast.ps1`을 호출하며, 이 보존본에는 `requirements.txt`와 GUI `app.py`가 없습니다.

이 차수에는 GUI app.py가 없습니다. `src/notifier.py`의 CLI에서 지정하는 경로로 감시기를 사용합니다. 인자 목록과 기본 경로는 아래 소스 설정 표에서 확인합니다.

<a name="️-소스에서-제공하는-cli-옵션"></a>
### 소스에서 제공하는 CLI 옵션

| 진입 소스 | 옵션 |
| --- | --- |
| [notifier.py](src/notifier.py) | `--sessions`, `--work` |

각 옵션의 기본 값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

### [src/notifier.py](src/notifier.py)


| 설정·옵션 | 선언 |
| --- | --- |
| [`--sessions`](src/notifier.py#L436) | `type=Path; default=Path.home() / '.codex/sessions'` |
| [`--work`](src/notifier.py#L437) | `type=Path; default=ROOT / 'work'` |
| [`ROOT`](src/notifier.py#L16) | `정의=Path(__file__).resolve().parents[1]` |
| [`APP_ID`](src/notifier.py#L17) | `정의='Yunseok.Codex.ModelChangeNotifier'` |
| [`READ_BYTES`](src/notifier.py#L18) | `정의=512 * 1024` |
| [`MAX_RECORD`](src/notifier.py#L19) | `정의=2 * 1024 * 1024` |
| [`MAX_FILES`](src/notifier.py#L20) | `정의=4096` |
| [`LOG_BYTES`](src/notifier.py#L21) | `정의=2 * 1024 * 1024` |
| [`POLL_READ_BYTES`](src/notifier.py#L22) | `정의=8 * 1024 * 1024` |
| [`MAX_PENDING`](src/notifier.py#L23) | `정의=256` |

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

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다.

부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

</details>

[프로젝트](../../README.md) · [전체 차수](../../docs/REVISION_INDEX.md) · [원본 자료](.) · [다음: 2차 →](../02%EC%B0%A8/README.md)
