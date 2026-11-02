# 3차 공개 보존 설명

비교 대상: 2차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:636](src/app.py#L636) `Controller` 정의 본문 변경; [src/app.py:337](src/app.py#L337) `Details` 정의 본문 변경; [src/app.py:122](src/app.py#L122) `Monitor` 정의 본문 변경; [src/app.py:277](src/app.py#L277) `Notice` 정의 본문 변경; [src/app.py:105](src/app.py#L105) `Settings` 정의 본문 변경; [src/app.py:446](src/app.py#L446) `add_event` 정의 본문 변경; [src/app.py:362](src/app.py#L362) `build_history` 정의 본문 변경; [src/app.py:456](src/app.py#L456) `build_settings` 정의 본문 변경; [src/app.py:316](src/app.py#L316) `display` 정의 본문 변경; [src/app.py:82](src/app.py#L82) `event_description` 정의 본문 변경; [src/app.py:74](src/app.py#L74) `event_kind` 정의 추가; [src/app.py:308](src/app.py#L308) `fit_content` 정의 추가 외 25건은 전체 차이 참조.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** `src/app.py:474`의 `QCheckBox` 호출 (현재 코드 · 라벨 `알림을 직접 닫을 때까지 유지`); `src/app.py:393`의 `QLabel` 호출 (현재 코드); `src/app.py:380`의 `QLabel` 호출 (현재 코드); `src/app.py:386`의 `QLabel` 호출 (현재 코드); `src/app.py:387`의 `QLabel` 호출 (현재 코드); `src/app.py:389`의 `QLabel` 호출 (현재 코드 · 라벨 `공개 이유`); `src/app.py:382`의 `QLabel` 호출 (현재 코드 · 라벨 `변경을 기다리고 있습니다`); `src/app.py:384`의 `QLabel` 호출 (현재 코드 · 라벨 `채팅 제목과 작업 이름이 여기에 표시됩니다.`); `src/app.py:391`의 `QLabel` 호출 (현재 코드 · 라벨 `첫 실행은 과거 기록을 기준선으로 읽으며 과거 알림을 만들지 않습니다.`); `src/app.py:295`의 `QPushButton` 호출 (현재 코드); `src/app.py:402`의 `QPushButton` 호출 (현재 코드); `src/app.py:689`의 `setText` 호출 (현재 코드) 외 18건은 전체 차이 참조.
- **문서:** 이번 보완에서 당시 문서·도구·자산의 원문 또는 정제본을 별도 [보존 목록](보존자료.md)에 연결했습니다. 파일별 원본 해시와 정제 사유를 구분하며 실제 실행 결과를 새로 추정하지 않습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 29190바이트, SHA-256 `87f6314b529e5831384703c6cd0fe97b212bb751eac632c0e7b422d1026f75da`; 현재 39580바이트, SHA-256 `93d5ba9d617c35f5e547642ddf31199791b462f1530856124ae65c780d2e7929`.
  - Python 정의 이름: 추가 `event_kind`, `fit_content`, `kst_label`, `model_card_label`, `refresh_history`, `replay_event`, `short_reason`, `toggle_evidence`, `update_event`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/core.py`: 이전 8223바이트, SHA-256 `6e6ae64f8d21cb1af9972916c8cbbeb9fa9e43d76d69fa723521803370a7b970`; 현재 10204바이트, SHA-256 `0da59ecbba81ad77544766fa50f0b24bd5abbd8d8f8da37f269a8ff08979b981`.
  - Python 정의 이름: 추가 `resolve_title`, `title_catalog`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/notifier.py`: 이전 26813바이트, SHA-256 `2059fcac37723f34535eba05d83443a9dbd7e3dfb771200f190f2c8ed2ffb9a8`; 현재 30682바이트, SHA-256 `00b619819040824cf816bb95536385e8af190967933b7912498d3edbc7f3cb89`.
  - Python 정의 이름: 추가 `_lookup_parent_reason`, `enrich_event`, `lookup_parent_reason`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.


## 역사 자료 추가 보존

당시의 [문서·제작 도구·자산·시안 목록](보존자료.md)과 [원본/공개 해시·정제·제외 대응](부가자료_보존.json)을 제공합니다. 같은 SHA의 파일은 공통 보관 파일을 참조하며 실제 원본 경로와 버전을 보존합니다. 운영 기억·실제 계정/채팅 원문·비공개 검증은 제외하고 이유를 명시합니다. 보존 문서는 당시 내용이며 현재 안내는 저장소 첫 화면을 사용하십시오.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

이번에 실제 전체 비교로 확인한 변경 파일: `src/app.py`, `src/core.py`, `src/notifier.py`.
