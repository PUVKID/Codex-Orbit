# 18차 공개 보존 설명

비교 대상: 17차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/activity.py:53](src/activity.py#L53) `ActivityTracker` 정의 추가; [src/activity.py:54](src/activity.py#L54) `__init__` 정의 추가; [src/activity.py:43](src/activity.py#L43) `_failed` 정의 추가; [src/activity.py:33](src/activity.py#L33) `_instant` 정의 추가; [src/activity.py:267](src/activity.py#L267) `_matches` 정의 추가; [src/activity.py:28](src/activity.py#L28) `_text` 정의 추가; [src/activity.py:48](src/activity.py#L48) `_trim` 정의 추가; [src/activity.py:181](src/activity.py#L181) `complete` 정의 추가; [src/activity.py:76](src/activity.py#L76) `configuration` 정의 추가; [src/activity.py:91](src/activity.py#L91) `configuration_pair` 정의 추가; [src/activity.py:160](src/activity.py#L160) `defer` 정의 추가; [src/activity.py:294](src/activity.py#L294) `enrich` 정의 추가 외 53건은 전체 차이 참조.
- **설정:** `src/activity.py:9`의 숫자·불리언 상수 `MAX_ACTIVITY_CALLS = 32` (추가 또는 현재 값); `src/activity.py:7`의 숫자·불리언 상수 `MAX_ACTIVITY_EVENTS = 128` (추가 또는 현재 값); `src/activity.py:8`의 숫자·불리언 상수 `MAX_ACTIVITY_SEEN = 8192` (추가 또는 현재 값); `src/activity.py:12`의 숫자·불리언 상수 `MAX_CONFIGURATION_SNAPSHOTS = 256` (추가 또는 현재 값); `src/activity.py:11`의 숫자·불리언 상수 `MAX_DEFERRED_ACTIVITIES = 32` (추가 또는 현재 값); `src/activity.py:10`의 숫자·불리언 상수 `MAX_PUBLIC_CALLS = 128` (추가 또는 현재 값).
- **화면 코드:** `src/app.py:823`의 `QLabel` 호출 (현재 코드); `src/app.py:706`의 `QLabel` 호출 (이전 코드); `src/app.py:826`의 `QLabel` 호출 (현재 코드); `src/app.py:822`의 `QLabel` 호출 (현재 코드 · 라벨 `공개된 작업 설명을 기다립니다.`); `src/app.py:910`의 `setText` 호출 (현재 코드); `src/app.py:792`의 `setText` 호출 (이전 코드); `src/app.py:515`의 `setText` 호출 (이전 코드); `src/app.py:626`의 `setText` 호출 (현재 코드); `src/app.py:920`의 `setText` 호출 (현재 코드); `src/app.py:922`의 `setText` 호출 (현재 코드); `src/app.py:793`의 `setText` 호출 (이전 코드); `src/app.py:620`의 `setText` 호출 (현재 코드) 외 8건은 전체 차이 참조.
- **문서:** 이번 보완에서 당시 문서·도구·자산의 원문 또는 정제본을 별도 [보존 목록](보존자료.md)에 연결했습니다. 파일별 원본 해시와 정제 사유를 구분하며 실제 실행 결과를 새로 추정하지 않습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **추가** `src/activity.py`: 이전 없음; 현재 15832바이트, SHA-256 `e1c17d720b16e14c328dade574c0d945486ccfb4d93260d2e022a3a17be876ad`.
  - Python 정의 이름: 추가 `ActivityTracker`, `__init__`, `_failed`, `_instant`, `_matches`, `_text`, `_trim`, `complete`, `configuration`, `configuration_pair`, `defer`, `enrich`, `note_first_observation`, `note_meta`, `observe`, `response`, `retry_deferred`, `safe_public_text`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/app.py`: 이전 67834바이트, SHA-256 `e475770e239c4bf0affbf36d2453faa16f9a29fc2a6c0c579d81235a4b9672e8`; 현재 77286바이트, SHA-256 `d1b5290ece7327f7421fd7cff5aa11c873bde5601ad6edbe95639088c4596608`.
  - Python 정의 이름: 추가 `activity_message`, `configuration_change_label`, `event_accent`, `event_icon`, `history_label`, `promote_first_observation`, `public_reason_original`, `public_text`, `selection_explanation`, `task_explanation`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/brand.py`: 이전 8905바이트, SHA-256 `735283d9736dac88c819deaf7d342804dbf248c71535bc1b848ca6edb7b9f191`; 현재 9066바이트, SHA-256 `956c1cbeb6a17a114cda3377b2788d5efb198fff55444c6891d16155b7931135`.
- **수정** `src/core.py`: 이전 10204바이트, SHA-256 `0da59ecbba81ad77544766fa50f0b24bd5abbd8d8f8da37f269a8ff08979b981`; 현재 11186바이트, SHA-256 `6578aa45d58a7e2d501d52c52689b233f993c6bc7af6196428efdc03338641bf`.
  - Python 정의 이름: 추가 `confirmed_time`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/element_visuals.py`: 이전 없음; 현재 800바이트, SHA-256 `a482d214b0cd73259d28561452bff4e5140a675e480301c90fcea84e3f4dd46f`.
  - Python 정의 이름: 추가 `colorize_atom`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/elements.py`: 이전 없음; 현재 2484바이트, SHA-256 `598145f03922718a1a453ca585d7f19f93d90bca204dcfebbd2016e35f79e865`.
  - Python 정의 이름: 추가 `Element`, `daily_element`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/notifier.py`: 이전 38231바이트, SHA-256 `5ebefd6304fee2279d53203c492a0c7452d2b363a74d03f52b20039487849321`; 현재 44672바이트, SHA-256 `6a16752a4874bc4c74e8f967bae76bb4f2c3e41af543e621cadc43b843330dd7`.
  - Python 정의 이름: 추가 `replay_activity_prefix`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/theme.py`: 이전 8578바이트, SHA-256 `e3b834f71c3af854ef23aa411ddeec07c959a6547c219d318b60b627445d3243`; 현재 9000바이트, SHA-256 `dbeca97f9a88b79de748171de4dd70f1251e6f54b517413f269b435f75c8f857`.
- **수정** `src/visuals.py`: 이전 6707바이트, SHA-256 `265e0872b25cf94cc9752cb8fef5886e46cc3a32aa240c1f712260c99f17b660`; 현재 6227바이트, SHA-256 `b1bc638467f4aac52d6679df8ea8bfb933dcc227a7c232f6f05036ffe29a5ce3`.
  - Python 정의 이름: 추가 `element_labels`, `label`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.


## 역사 자료 추가 보존

당시의 [문서·제작 도구·자산·시안 목록](보존자료.md)과 [원본/공개 해시·정제·제외 대응](부가자료_보존.json)을 제공합니다. 같은 SHA의 파일은 공통 보관 파일을 참조하며 실제 원본 경로와 버전을 보존합니다. 운영 기억·실제 계정/채팅 원문·비공개 검증은 제외하고 이유를 명시합니다. 보존 문서는 당시 내용이며 현재 안내는 저장소 첫 화면을 사용하십시오.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

이번에 실제 전체 비교로 확인한 변경 파일: `src/activity.py`, `src/app.py`, `src/brand.py`, `src/core.py`, `src/element_visuals.py`, `src/elements.py`, `src/notifier.py`, `src/theme.py`, `src/visuals.py`.
