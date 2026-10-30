# 5차 공개 보존 설명

비교 대상: 4차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:809](src/app.py#L809) `Controller` 정의 본문 변경; [src/app.py:404](src/app.py#L404) `Details` 정의 본문 변경; [src/app.py:141](src/app.py#L141) `Monitor` 정의 본문 변경; [src/app.py:227](src/app.py#L227) `OrbitWidget` 정의 본문 변경; [src/app.py:810](src/app.py#L810) `__init__` 정의 본문 변경; [src/app.py:986](src/app.py#L986) `advance_notice` 정의 본문 변경; [src/app.py:489](src/app.py#L489) `build_history` 정의 본문 변경; [src/app.py:972](src/app.py#L972) `display_notice` 정의 추가; [src/app.py:953](src/app.py#L953) `enqueue_notice` 정의 본문 변경; [src/app.py:100](src/app.py#L100) `event_description` 정의 본문 변경; [src/app.py:1097](src/app.py#L1097) `main` 정의 본문 변경; [src/app.py:32](src/app.py#L32) `operation_record` 정의 추가 외 11건은 전체 차이 참조.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** `src/app.py:890`의 `setText` 호출 (현재 코드); `src/app.py:567`의 `setText` 호출 (현재 코드); `src/app.py:507`의 `setText` 호출 (이전 코드).
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 54704바이트, SHA-256 `6fee6fa67549f53b670f621c24fcc190ddd4801e01c6c816649e1414e84ee546`; 현재 61692바이트, SHA-256 `8e2621c486a0ae9da8f05968e861afe0b9e580397bbdeb3c9bfc77fad949adbb`.
  - Python 정의 이름: 추가 `display_notice`, `operation_record`, `report_failure`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/notifier.py`: 이전 30682바이트, SHA-256 `00b619819040824cf816bb95536385e8af190967933b7912498d3edbc7f3cb89`; 현재 33077바이트, SHA-256 `bb9659e678dcdb5d214c2a3b7201d42785dd287f317d3ac854ef39ca5f41edb6`.
  - Python 정의 이름: 추가 `source_datetime`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
