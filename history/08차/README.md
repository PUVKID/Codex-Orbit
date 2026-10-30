# 8차 공개 보존 설명

비교 대상: 7차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:154](src/app.py#L154) `Monitor` 정의 본문 변경; [src/app.py:243](src/app.py#L243) `OrbitWidget` 정의 본문 변경; [src/app.py:112](src/app.py#L112) `event_description` 정의 본문 변경; [src/app.py:100](src/app.py#L100) `event_kind` 정의 본문 변경; [src/app.py:175](src/app.py#L175) `run` 정의 본문 변경; [src/notifier.py:81](src/notifier.py#L81) `Watcher` 정의 본문 변경; [src/notifier.py:184](src/notifier.py#L184) `duplicate_record` 정의 추가; [src/notifier.py:382](src/notifier.py#L382) `enrich_event` 정의 본문 변경; [src/notifier.py:136](src/notifier.py#L136) `event` 정의 본문 변경; [src/notifier.py:634](src/notifier.py#L634) `main` 정의 본문 변경; [src/notifier.py:445](src/notifier.py#L445) `poll` 정의 본문 변경; [src/notifier.py:402](src/notifier.py#L402) `read_file` 정의 본문 변경 외 2건은 전체 차이 참조.
- **설정:** `src/notifier.py:25`의 숫자·불리언 상수 `POLL_INTERVAL_SECONDS = 0.2` (추가 또는 현재 값).
- **화면 코드:** 지정한 위젯 생성·라벨 호출에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 62775바이트, SHA-256 `2e961caa97a0aecc6b26d0948d53f72369451e6af01bd9124c759c66875a3398`; 현재 63254바이트, SHA-256 `694f3cbe443ee55bd6b07557517e8d1d38ddbc8f6d06ebd7a2777003e02fbf6a`.
- **수정** `src/notifier.py`: 이전 33077바이트, SHA-256 `bb9659e678dcdb5d214c2a3b7201d42785dd287f317d3ac854ef39ca5f41edb6`; 현재 38231바이트, SHA-256 `5ebefd6304fee2279d53203c492a0c7452d2b363a74d03f52b20039487849321`.
  - Python 정의 이름: 추가 `duplicate_record`, `settings_record`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
