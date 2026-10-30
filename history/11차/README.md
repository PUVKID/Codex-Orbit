# 11차 공개 보존 설명

비교 대상: 10차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:1019](src/app.py#L1019) `Controller` 정의 본문 변경; [src/app.py:525](src/app.py#L525) `Details` 정의 본문 변경; [src/app.py:339](src/app.py#L339) `Notice` 정의 본문 변경; [src/app.py:623](src/app.py#L623) `build_history` 정의 본문 변경; [src/app.py:839](src/app.py#L839) `build_instructions` 정의 본문 변경; [src/app.py:761](src/app.py#L761) `build_settings` 정의 본문 변경; [src/app.py:563](src/app.py#L563) `build_usage` 정의 본문 변경; [src/app.py:460](src/app.py#L460) `display` 정의 본문 변경; [src/app.py:593](src/app.py#L593) `display_usage` 정의 본문 변경; [src/app.py:66](src/app.py#L66) `friendly_effort` 정의 추가; [src/app.py:61](src/app.py#L61) `friendly_model` 정의 추가; [src/app.py:1308](src/app.py#L1308) `preferences` 정의 본문 변경 외 5건은 전체 차이 참조.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** `src/app.py:765`의 `QLabel` 호출 (이전 코드); `src/app.py:667`의 `QLabel` 호출 (현재 코드); `src/app.py:498`의 `QLabel` 호출 (이전 코드); `src/app.py:675`의 `QLabel` 호출 (현재 코드); `src/app.py:874`의 `QLabel` 호출 (현재 코드); `src/app.py:604`의 `QLabel` 호출 (이전 코드 · 라벨 `공개 이유`); `src/app.py:850`의 `QLabel` 호출 (현재 코드 · 라벨 `내 지침`); `src/app.py:541`의 `QLabel` 호출 (현재 코드 · 라벨 `사용 한도 미확인`); `src/app.py:853`의 `QLabel` 호출 (현재 코드 · 라벨 `작성한 내용을 확인한 뒤 적용하세요. 파일은 명시 적용할 때만 바뀝니다.`); `src/app.py:900`의 `QLabel` 호출 (현재 코드 · 라벨 `적용 전 원문을 자동 백업합니다. 적용 후 대상이 바뀌면 충돌을 거부합니다.`); `src/app.py:857`의 `QLabel` 호출 (현재 코드 · 라벨 `적용할 파일`); `src/app.py:798`의 `QPushButton` 호출 (이전 코드) 외 15건은 전체 차이 참조.
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 70594바이트, SHA-256 `b6eb55394e32a9270f44b0d717f9a69b851f93a09782821386d7eb2e351b58e0`; 현재 77206바이트, SHA-256 `aa9ab7a95f5b34f136ad7633b540290a6e1b3583e6bdebcccd9f71252e53204a`.
  - Python 정의 이름: 추가 `friendly_effort`, `friendly_model`, `resizeEvent`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/theme.py`: 이전 8014바이트, SHA-256 `6ac4f4457b8a7f2cbaddeb15e8a6858bc6e506eb962175099565d5af970e74d0`; 현재 8578바이트, SHA-256 `e3b834f71c3af854ef23aa411ddeec07c959a6547c219d318b60b627445d3243`.
- **수정** `src/visuals.py`: 이전 6995바이트, SHA-256 `60af8348b66e84a9c37c11f3c700579db137fd6b5b5ef2ad25f748253071e05e`; 현재 7287바이트, SHA-256 `6c1102f74fb8b1c9cd551ac05931465852e5815a088421aec11ec60e8fb88132`.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
