# 5차 공개 보존 설명

비교 대상: 4차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:809](src/app.py#L809) `Controller` 정의 본문 변경; [src/app.py:404](src/app.py#L404) `Details` 정의 본문 변경; [src/app.py:141](src/app.py#L141) `Monitor` 정의 본문 변경; [src/app.py:227](src/app.py#L227) `OrbitWidget` 정의 본문 변경; [src/app.py:810](src/app.py#L810) `__init__` 정의 본문 변경; [src/app.py:986](src/app.py#L986) `advance_notice` 정의 본문 변경; [src/app.py:489](src/app.py#L489) `build_history` 정의 본문 변경; [src/app.py:972](src/app.py#L972) `display_notice` 정의 추가; [src/app.py:953](src/app.py#L953) `enqueue_notice` 정의 본문 변경; [src/app.py:100](src/app.py#L100) `event_description` 정의 본문 변경; [src/app.py:1097](src/app.py#L1097) `main` 정의 본문 변경; [src/app.py:32](src/app.py#L32) `operation_record` 정의 추가 외 11건은 전체 차이 참조.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** `src/app.py:890`의 `setText` 호출 (현재 코드); `src/app.py:567`의 `setText` 호출 (현재 코드); `src/app.py:507`의 `setText` 호출 (이전 코드).
- **문서:** 이번 보완에서 당시 문서·도구·자산의 원문 또는 정제본을 별도 [보존 목록](보존자료.md)에 연결했습니다. 파일별 원본 해시와 정제 사유를 구분하며 실제 실행 결과를 새로 추정하지 않습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 54704바이트, SHA-256 `6fee6fa67549f53b670f621c24fcc190ddd4801e01c6c816649e1414e84ee546`; 현재 61692바이트, SHA-256 `8e2621c486a0ae9da8f05968e861afe0b9e580397bbdeb3c9bfc77fad949adbb`.
  - Python 정의 이름: 추가 `display_notice`, `operation_record`, `report_failure`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/notifier.py`: 이전 30682바이트, SHA-256 `00b619819040824cf816bb95536385e8af190967933b7912498d3edbc7f3cb89`; 현재 33077바이트, SHA-256 `bb9659e678dcdb5d214c2a3b7201d42785dd287f317d3ac854ef39ca5f41edb6`.
  - Python 정의 이름: 추가 `source_datetime`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.


## 역사 자료 추가 보존

당시의 [문서·제작 도구·자산·시안 목록](보존자료.md)과 [원본/공개 해시·정제·제외 대응](부가자료_보존.json)을 제공합니다. 같은 SHA의 파일은 공통 보관 파일을 참조하며 실제 원본 경로와 버전을 보존합니다. 운영 기억·실제 계정/채팅 원문·비공개 검증은 제외하고 이유를 명시합니다. 보존 문서는 당시 내용이며 현재 안내는 저장소 첫 화면을 사용하십시오.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

이번에 실제 전체 비교로 확인한 변경 파일: `src/app.py`, `src/notifier.py`.
