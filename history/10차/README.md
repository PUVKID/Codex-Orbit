# 10차 공개 보존 설명

비교 대상: 9차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:908](src/app.py#L908) `Controller` 정의 본문 변경; [src/app.py:485](src/app.py#L485) `Details` 정의 본문 변경; [src/app.py:328](src/app.py#L328) `Notice` 정의 본문 변경; [src/app.py:909](src/app.py#L909) `__init__` 정의 본문 변경; [src/app.py:756](src/app.py#L756) `build_instructions` 정의 본문 변경; [src/app.py:1032](src/app.py#L1032) `check_monitor_health` 정의 본문 변경; [src/app.py:1230](src/app.py#L1230) `close` 정의 본문 변경; [src/app.py:431](src/app.py#L431) `display` 정의 본문 변경; [src/app.py:394](src/app.py#L394) `fit_content` 정의 본문 변경; [src/app.py:1079](src/app.py#L1079) `layout_notices` 정의 본문 변경; [src/app.py:1201](src/app.py#L1201) `request_quit` 정의 본문 변경; [src/app.py:734](src/app.py#L734) `save_settings` 정의 본문 변경 외 2건은 전체 차이 참조.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** `src/app.py:1041`의 `setText` 호출 (현재 코드); `src/app.py:997`의 `setText` 호출 (현재 코드); `src/app.py:426`의 `setText` 호출 (현재 코드); `src/app.py:421`의 `setText` 호출 (현재 코드); `src/app.py:404`의 `setText` 호출 (현재 코드); `src/app.py:403`의 `setToolTip` 호출 (현재 코드).
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 66922바이트, SHA-256 `95c1db95d8b2310db03353c12ae03854c4c101092465563e36e727eeb5164522`; 현재 70594바이트, SHA-256 `b6eb55394e32a9270f44b0d717f9a69b851f93a09782821386d7eb2e351b58e0`.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
