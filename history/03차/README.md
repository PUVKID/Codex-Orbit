<div align="center">

# 🪐 Codex Orbit · 3차

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

**기술 분류:** Windows 데스크톱 · Python · PySide6

[핵심 기능](#features) · [사용 흐름](#usage) · [자료 구성](#structure) · [준비와 실행](#setup) · [결과 읽기](#results) · [직전 변경](#changes)

</div>

[🏠 프로젝트](../../README.md) · [🗂️ 전체 차수](../../docs/REVISION_INDEX.md) · [📁 원본 자료](.) · [← 이전: 2차](../02%EC%B0%A8/README.md) · [다음: 4차 →](../04%EC%B0%A8/README.md)

## 🎯 목적과 이 차수의 역할

알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다.

<a name="features"></a>

## ✨ 핵심 기능과 보존 범위

| 항목 | 이 차수에서 확인할 내용 |
|---|---|
| 1 | 알림을 직접 닫을 때까지 유지하는 설정과 내용 높이 계산을 확장하고, 기록 종류·상세 표시·감시 상태의 분기를 다룹니다. |
| 2 | 로컬 세션 기록에서 모델·추론 강도의 변경과 명시된 배정을 구분합니다. 감시기는 외부 통신 없이 로컬 자료를 읽습니다. |

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
| [src/app.py](src/app.py) | Codex Orbit: 투명 궤도와 로컬 감시, 명시적 Markdown 지침 적용. |
| [src/notifier.py](src/notifier.py) | 현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다. |
| [src/core.py](src/core.py) | 외부 통신 없는 로컬 자료 읽기와 명시적 지침 적용. |

<a name="setup"></a>

## 🚀 설치 환경과 실행·사용법

Windows와 해당 폴더의 requirements.txt를 기준으로 Python 의존성을 준비합니다. history는 공개 소스 보존본이며 현재 루트 assets가 과거 모든 차수의 자산과 호환된다는 뜻은 아닙니다.

자산과 의존성을 준비한 이 차수 폴더에서 `python src/app.py`를 실행합니다. history 소스만으로 과거 배포 EXE와 동일한 화면·자산이 모두 복원되지는 않습니다.

### 📦 이 보관본의 의존성 목록

[requirements.txt](requirements.txt)의 실제 항목입니다. 외부 실행 도구와 GPU 드라이버는 별도로 준비합니다.

```text
PySide6-Essentials==6.12.0
PyInstaller==6.22.3
```

### ⚙️ 소스에서 제공하는 CLI 옵션

| 진입 소스 | 정의된 옵션 이름 |
|---|---|
| [app.py](src/app.py) | `--data-dir`, `--sessions`, `--smoke-test`, `--smoke-report`, `--show-details`, `--show-event` |
| [notifier.py](src/notifier.py) | `--sessions`, `--work` |

각 옵션의 기본값·필수값·부작용은 해당 main과 인자 정의를 함께 확인합니다.


<details>
<summary>🔬 함수 역할·기본값·입력 거부 조건의 세부 참조</summary>

다음 항목은 이 자료의 Python 소스에 명시된 선언입니다. 전체 분기와 호출 순서는 각 행의 코드 위치에서 이어서 읽을 수 있습니다.

### [src/app.py](src/app.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`short_reason`](src/app.py#L56) | 명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`--data-dir`](src/app.py#L723) | `type=Path; default=Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CodexOrbit'` |
| [`--sessions`](src/app.py#L724) | `type=Path` |
| [`--smoke-test`](src/app.py#L725) | `action='store_true'` |
| [`--smoke-report`](src/app.py#L726) | `type=Path` |
| [`--show-details`](src/app.py#L727) | `action='store_true'` |
| [`--show-event`](src/app.py#L728) | `help='기존 이력의 이벤트 ID 또는 대상 ID를 다시 표시'` |
| [`ROLE_LABELS`](src/app.py#L42) | `정의={'main': '부모 조율', 'triage': '작업 분류', 'quick': '간단한 수정',                'build': '구현', 'deep': '심층 검토·구현', 'verifier': '독립 검증', 'escalate': '판단 재검토·수리'}` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`not lock.tryLock(100)`](src/app.py#L743) | 같은 데이터 폴더의 Codex Orbit가 이미 실행 중이거나 잠금 파일에 접근할 수 없습니다. |
| [`not isinstance(value, dict)`](src/app.py#L114) | 앱 설정은 JSON 객체여야 합니다. |
| [`not path.is_dir()`](src/app.py#L495) | 존재하는 sessions 폴더를 선택하세요. |
| [`self.plan is None`](src/app.py#L599) | 새 미리보기가 필요합니다. |
| [`not receipts`](src/app.py#L611) | 앱이 만든 적용 백업이 없습니다. |

### [src/core.py](src/core.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`read_jsonl_tail`](src/core.py#L18) | 물리적 LF만 나누며 잘린 앞/뒤 조각은 레코드로 해석하지 않습니다. |
| [`title_catalog`](src/core.py#L55) | 공식 앱에서 확인해 저장한 제목과 로컬 색인의 출처를 보존합니다. |
| [`resolve_title`](src/core.py#L73) | 자식 작업은 실제 부모 채팅 제목과 작업명을 분리합니다. |
| [`safe_path`](src/core.py#L97) | 적용 파일과 모든 기존 조상 경로의 링크/재분석 지점을 거부합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
| [`MAX_TEXT_BYTES`](src/core.py#L9) | `정의=2 * 1024 * 1024` |
| [`BEGIN`](src/core.py#L10) | `정의=b'&lt;!-- CODEX-ORBIT:BEGIN --&gt;'` |
| [`END`](src/core.py#L11) | `정의=b'&lt;!-- CODEX-ORBIT:END --&gt;'` |

| 거부 조건 | 오류 메시지 |
|---|---|
| [`path.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L112) | 문서가 2 MiB 상한을 초과했습니다. |
| [`not isinstance(cache, dict) or not isinstance(cache.get('titles'), dict)`](src/core.py#L64) | 제목 캐시 구조가 올바르지 않습니다. |
| [`target.name.lower() != 'agents.md'`](src/core.py#L123) | 적용 대상은 AGENTS.md 파일이어야 합니다. |
| [`not target.parent.is_dir()`](src/core.py#L125) | 대상 폴더가 존재하지 않습니다. |
| [`target.exists() and (not target.is_file() or target.stat().st_size &gt; MAX_TEXT_BYTES)`](src/core.py#L127) | 대상은 2 MiB 이하의 일반 파일이어야 합니다. |
| [`not content.strip() or len(added) &gt; MAX_TEXT_BYTES`](src/core.py#L134) | 빈 지침 또는 2 MiB 초과 지침은 적용할 수 없습니다. |
| [`BEGIN in added or END in added`](src/core.py#L136) | 지침 내용에 앱 관리구역 표식을 넣을 수 없습니다. |
| [`len(result) &gt; MAX_TEXT_BYTES`](src/core.py#L150) | 적용 결과가 2 MiB 상한을 초과합니다. |
| [`target.exists() != existed or digest(target.read_bytes() if existed else b'') != expected`](src/core.py#L157) | 대상 파일이 미리보기/적용 이후 변경되었습니다. 새 미리보기가 필요합니다. |
| [`digest(plan['original']) != plan['before_hash'] or digest(plan['applied_bytes']) != plan['after_hash']`](src/core.py#L177) | 미리보기 데이터가 변경되었습니다. |
| [`backup.parent != safe_path(self.data_dir / 'backups') or not backup.is_file() or backup.stat().st_size &gt; MAX_TEXT_BYTES`](src/core.py#L197) | 유효한 앱 원문 백업이 아닙니다. |
| [`digest(raw) != receipt['before_hash']`](src/core.py#L200) | 백업 해시가 일치하지 않습니다. |
| [`not isinstance(row, dict)`](src/core.py#L40) | JSON 객체가 아닙니다. |
| [`original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(BEGIN) &gt;= original.index(END)`](src/core.py#L143) | 기존 관리구역 표식이 손상되었거나 중복되었습니다. |

### [src/notifier.py](src/notifier.py)

| 정의 | 소스에 적힌 역할 |
|---|---|
| [`lookup_parent_reason`](src/notifier.py#L219) | 큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다. |
| [`enrich_event`](src/notifier.py#L266) | 이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다. |

| 설정·옵션 | 코드의 선언 |
|---|---|
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

| 거부 조건 | 오류 메시지 |
|---|---|
| [`self.state_path.stat().st_size &gt; 16 * 1024 * 1024`](src/notifier.py#L54) | 상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다. |
| [`self.state.get('schema_version') != 2`](src/notifier.py#L57) | 구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다. |
| [`not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict)`](src/notifier.py#L59) | 상태 파일 구조 오류입니다. 자동 초기화하지 않습니다. |
| [`not isinstance(self.state.get('declarations'), dict)`](src/notifier.py#L61) | 명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다. |
| [`not isinstance(record, dict)`](src/notifier.py#L315) | JSON 객체가 아닙니다. |
| [`path.stat().st_size &gt; 20000`](src/notifier.py#L378) | 명시 알림 파일 상한 초과 |

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

2차에서 3차로 이어지는 실제 파일 비교입니다.

[📄 전체 비교·자료 범위](%EC%A7%81%EC%A0%84%EC%B0%A8%EC%88%98.diff)

추가·수정·삭제, 주석·공백·개행과 바이너리 크기·해시는 연결된 원래 비교 자료에서 확인합니다.

<details>
<summary>📚 파일별 비교·크기·해시 자세히 보기</summary>

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

- **수정** `src/app.py`: 이전 29190바이트, SHA-256 `87f6314b529e5831384703c6cd0fe97b212bb751eac632c0e7b422d1026f75da`; 현재 39580바이트, SHA-256 `93d5ba9d617c35f5e547642ddf31199791b462f1530856124ae65c780d2e7929`.

- **수정** `src/core.py`: 이전 8223바이트, SHA-256 `6e6ae64f8d21cb1af9972916c8cbbeb9fa9e43d76d69fa723521803370a7b970`; 현재 10204바이트, SHA-256 `0da59ecbba81ad77544766fa50f0b24bd5abbd8d8f8da37f269a8ff08979b981`.

- **수정** `src/notifier.py`: 이전 26813바이트, SHA-256 `2059fcac37723f34535eba05d83443a9dbd7e3dfb771200f190f2c8ed2ffb9a8`; 현재 30682바이트, SHA-256 `00b619819040824cf816bb95536385e8af190967933b7912498d3edbc7f3cb89`.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

</details>

[🏠 프로젝트](../../README.md) · [🗂️ 전체 차수](../../docs/REVISION_INDEX.md) · [📁 원본 자료](.) · [← 이전: 2차](../02%EC%B0%A8/README.md) · [다음: 4차 →](../04%EC%B0%A8/README.md)
