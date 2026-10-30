# 6차 공개 보존 설명

비교 대상: 5차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:807](src/app.py#L807) `Controller` 정의 본문 변경; [src/app.py:394](src/app.py#L394) `Details` 정의 본문 변경; [src/app.py:320](src/app.py#L320) `Notice` 정의 본문 변경; [src/app.py:235](src/app.py#L235) `OrbitWidget` 정의 본문 변경; [src/app.py:808](src/app.py#L808) `__init__` 정의 본문 변경; [src/app.py:479](src/app.py#L479) `build_history` 정의 본문 변경; [src/app.py:588](src/app.py#L588) `build_settings` 정의 본문 변경; [src/app.py:420](src/app.py#L420) `build_usage` 정의 본문 변경; [src/app.py:638](src/app.py#L638) `choose_codex` 정의 본문 변경; [src/app.py:633](src/app.py#L633) `choose_sessions` 정의 본문 변경; [src/app.py:307](src/app.py#L307) `contextMenuEvent` 정의 본문 변경; [src/app.py:311](src/app.py#L311) `create_menu` 정의 추가 외 23건은 전체 차이 참조.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** 지정한 위젯 생성·라벨 호출에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 61692바이트, SHA-256 `8e2621c486a0ae9da8f05968e861afe0b9e580397bbdeb3c9bfc77fad949adbb`; 현재 62549바이트, SHA-256 `c803fe6fdda129d8910dfe5a9d608034fcd9284e56593f3935190dab39f59fa4`.
  - Python 정의 이름: 추가 `create_menu`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/theme.py`: 이전 없음; 현재 8014바이트, SHA-256 `6ac4f4457b8a7f2cbaddeb15e8a6858bc6e506eb962175099565d5af970e74d0`.
  - Python 정의 이름: 추가 `DialogLayout`, `KoreanDialogs`, `MonochromeStyle`, `__init__`, `apply_theme`, `eventFilter`, `prepare`, `standardIcon`, `translate`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/visuals.py`: 이전 없음; 현재 6995바이트, SHA-256 `60af8348b66e84a9c37c11f3c700579db137fd6b5b5ef2ad25f748253071e05e`.
  - Python 정의 이름: 추가 `draw_orbit`, `gray`, `orbit_segments`, `project_point`, `rotate_point`, `tubes`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
