# 9차 공개 보존 설명

비교 대상: 8차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:868](src/app.py#L868) `Controller` 정의 본문 변경; [src/app.py:328](src/app.py#L328) `Notice` 정의 본문 변경; [src/app.py:869](src/app.py#L869) `__init__` 정의 본문 변경; `src/app.py`의 이전 코드 `advance_notice` 정의 삭제; [src/app.py:1165](src/app.py#L1165) `close` 정의 본문 변경; [src/app.py:390](src/app.py#L390) `closeEvent` 정의 추가; [src/app.py:402](src/app.py#L402) `display` 정의 본문 변경; [src/app.py:1060](src/app.py#L1060) `display_notice` 정의 본문 변경; [src/app.py:1042](src/app.py#L1042) `enqueue_notice` 정의 본문 변경; [src/app.py:1019](src/app.py#L1019) `layout_notices` 정의 추가; [src/app.py:1094](src/app.py#L1094) `refresh_history` 정의 본문 변경; [src/app.py:1078](src/app.py#L1078) `remove_notice` 정의 추가 외 4건은 전체 차이 참조.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** `src/app.py:372`의 `QLabel` 호출 (현재 코드); `src/app.py:355`의 `QLabel` 호출 (이전 코드 · 라벨 `클릭하여 전체 이유와 근거 보기`); `src/app.py:348`의 `QPushButton` 호출 (이전 코드); `src/app.py:350`의 `QPushButton` 호출 (현재 코드 · 라벨 `닫기`); `src/app.py:957`의 `setText` 호출 (이전 코드); `src/app.py:1024`의 `setText` 호출 (이전 코드); `src/app.py:1023`의 `setText` 호출 (이전 코드); `src/app.py:1015`의 `setText` 호출 (현재 코드); `src/app.py:433`의 `setText` 호출 (현재 코드); `src/app.py:432`의 `setText` 호출 (현재 코드); `src/app.py:431`의 `setText` 호출 (현재 코드); `src/app.py:385`의 `setText` 호출 (이전 코드) 외 1건은 전체 차이 참조.
- **문서:** 이번 보완에서 당시 문서·도구·자산의 원문 또는 정제본을 별도 [보존 목록](보존자료.md)에 연결했습니다. 파일별 원본 해시와 정제 사유를 구분하며 실제 실행 결과를 새로 추정하지 않습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 63254바이트, SHA-256 `694f3cbe443ee55bd6b07557517e8d1d38ddbc8f6d06ebd7a2777003e02fbf6a`; 현재 66922바이트, SHA-256 `95c1db95d8b2310db03353c12ae03854c4c101092465563e36e727eeb5164522`.
  - Python 정의 이름: 추가 `closeEvent`, `layout_notices`, `remove_notice`, `setting_label`; 삭제 `advance_notice`. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.


## 역사 자료 추가 보존

당시의 [문서·제작 도구·자산·시안 목록](보존자료.md)과 [원본/공개 해시·정제·제외 대응](부가자료_보존.json)을 제공합니다. 같은 SHA의 파일은 공통 보관 파일을 참조하며 실제 원본 경로와 버전을 보존합니다. 운영 기억·실제 계정/채팅 원문·비공개 검증은 제외하고 이유를 명시합니다. 보존 문서는 당시 내용이며 현재 안내는 저장소 첫 화면을 사용하십시오.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

이번에 실제 전체 비교로 확인한 변경 파일: `src/app.py`.
