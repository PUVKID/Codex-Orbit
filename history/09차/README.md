# 9차 공개 보존 설명

비교 대상: 8차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:868](src/app.py#L868) `Controller` 정의 본문 변경; [src/app.py:328](src/app.py#L328) `Notice` 정의 본문 변경; [src/app.py:869](src/app.py#L869) `__init__` 정의 본문 변경; `src/app.py`의 이전 코드 `advance_notice` 정의 삭제; [src/app.py:1165](src/app.py#L1165) `close` 정의 본문 변경; [src/app.py:390](src/app.py#L390) `closeEvent` 정의 추가; [src/app.py:402](src/app.py#L402) `display` 정의 본문 변경; [src/app.py:1060](src/app.py#L1060) `display_notice` 정의 본문 변경; [src/app.py:1042](src/app.py#L1042) `enqueue_notice` 정의 본문 변경; [src/app.py:1019](src/app.py#L1019) `layout_notices` 정의 추가; [src/app.py:1094](src/app.py#L1094) `refresh_history` 정의 본문 변경; [src/app.py:1078](src/app.py#L1078) `remove_notice` 정의 추가 외 4건은 전체 차이 참조.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** `src/app.py:372`의 `QLabel` 호출 (현재 코드); `src/app.py:355`의 `QLabel` 호출 (이전 코드 · 라벨 `클릭하여 전체 이유와 근거 보기`); `src/app.py:348`의 `QPushButton` 호출 (이전 코드); `src/app.py:350`의 `QPushButton` 호출 (현재 코드 · 라벨 `닫기`); `src/app.py:957`의 `setText` 호출 (이전 코드); `src/app.py:1024`의 `setText` 호출 (이전 코드); `src/app.py:1023`의 `setText` 호출 (이전 코드); `src/app.py:1015`의 `setText` 호출 (현재 코드); `src/app.py:433`의 `setText` 호출 (현재 코드); `src/app.py:432`의 `setText` 호출 (현재 코드); `src/app.py:431`의 `setText` 호출 (현재 코드); `src/app.py:385`의 `setText` 호출 (이전 코드) 외 1건은 전체 차이 참조.
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 63254바이트, SHA-256 `694f3cbe443ee55bd6b07557517e8d1d38ddbc8f6d06ebd7a2777003e02fbf6a`; 현재 66922바이트, SHA-256 `95c1db95d8b2310db03353c12ae03854c4c101092465563e36e727eeb5164522`.
  - Python 정의 이름: 추가 `closeEvent`, `layout_notices`, `remove_notice`, `setting_label`; 삭제 `advance_notice`. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
