# 21차 공개 보존 설명

비교 대상: 19차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:992](src/app.py#L992) `Controller` 정의 본문 변경; [src/app.py:679](src/app.py#L679) `Details` 정의 본문 변경; [src/app.py:993](src/app.py#L993) `__init__` 정의 본문 변경; [src/app.py:745](src/app.py#L745) `display_usage` 정의 본문 변경; [src/app.py:1410](src/app.py#L1410) `finish_usage` 정의 본문 변경; [src/app.py:1350](src/app.py#L1350) `main` 정의 본문 변경; [src/brand.py:39](src/brand.py#L39) `BrandClock` 정의 본문 변경; [src/brand.py:31](src/brand.py#L31) `motion_brand_source` 정의 추가; [src/brand.py:67](src/brand.py#L67) `tick` 정의 본문 변경; [src/element_frames.py:24](src/element_frames.py#L24) `ElementAssetError` 정의 추가; [src/element_frames.py:52](src/element_frames.py#L52) `ElementFrames` 정의 추가; [src/element_frames.py:53](src/element_frames.py#L53) `__init__` 정의 추가 외 18건은 전체 차이 참조.
- **설정:** `src/element_frames.py:15`의 숫자·불리언 상수 `CACHE_LIMIT = 24` (추가 또는 현재 값); `src/element_frames.py:18`의 숫자·불리언 상수 `FPS = 30` (추가 또는 현재 값); `src/element_frames.py:17`의 숫자·불리언 상수 `FRAME_COUNT = 540` (추가 또는 현재 값); `src/element_frames.py:16`의 숫자·불리언 상수 `FRAME_SIZE = 192` (추가 또는 현재 값); `src/element_frames.py:19`의 숫자·불리언 상수 `PERIOD_SECONDS = 18` (추가 또는 현재 값); `src/visuals.py:95`의 숫자·불리언 상수 `SYMBOL_PIXELS = 24` (추가 또는 현재 값); `src/visuals.py:94`의 숫자·불리언 상수 `SYMBOL_PIXELS = 30` (삭제 또는 이전 값).
- **화면 코드:** 지정한 위젯 생성·라벨 호출에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **문서:** 이번 보완에서 당시 문서·도구·자산의 원문 또는 정제본을 별도 [보존 목록](보존자료.md)에 연결했습니다. 파일별 원본 해시와 정제 사유를 구분하며 실제 실행 결과를 새로 추정하지 않습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 77255바이트, SHA-256 `7985e516248d9b840bf6d375e28025b3b5be8a63317170654659dac9445678e4`; 현재 77768바이트, SHA-256 `27b7ae6fa48e57d0f042667eb2ba16ffd2a4a4d4b188681df1b30517a11e5519`.
- **수정** `src/brand.py`: 이전 9066바이트, SHA-256 `956c1cbeb6a17a114cda3377b2788d5efb198fff55444c6891d16155b7931135`; 현재 9343바이트, SHA-256 `a04c41ac93f2256689e00ccc2c94469eb02e77af24faf6666a49d18dbee8164c`.
  - Python 정의 이름: 추가 `motion_brand_source`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/element_frames.py`: 이전 없음; 현재 7096바이트, SHA-256 `0d72e490fbc2680b3bd9bac16c5da13288c61d6e9a08049bb5b8bf072a0a1342`.
  - Python 정의 이름: 추가 `ElementAssetError`, `ElementFrames`, `__init__`, `_check_unchanged`, `_decode`, `_identity`, `_number`, `_object`, `_prepare`, `asset_directory`, `cache_bytes`, `close`, `close_element_frames`, `frame`, `get_element_frame`, `preflight_element_frames`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/elements.py`: 이전 2532바이트, SHA-256 `6357b9dce67a557de08eff0f7fd6cebfd9c08dfae2bf276e9d84610358aafe91`; 현재 2532바이트, SHA-256 `2f4b017f3ea1d8212dfe22b0db43e82cdf01d5ab6a298a60d446e1cc1599c90c`.
- **수정** `src/visuals.py`: 이전 6495바이트, SHA-256 `c58a8a7bfb9b2fe9bd3643ad06fd07fd87ac683741d96a318a1a69a0fb4a7a8f`; 현재 7461바이트, SHA-256 `2a9004efcde7367ce9324655c384863e5b7ec07fab5816efdd5be6bdb3fd9c17`.
  - Python 정의 이름: 추가 `_frame_for_element`, `surface`, `usage_bar`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.


## 역사 자료 추가 보존

당시의 [문서·제작 도구·자산·시안 목록](보존자료.md)과 [원본/공개 해시·정제·제외 대응](부가자료_보존.json)을 제공합니다. 같은 SHA의 파일은 공통 보관 파일을 참조하며 실제 원본 경로와 버전을 보존합니다. 운영 기억·실제 계정/채팅 원문·비공개 검증은 제외하고 이유를 명시합니다. 보존 문서는 당시 내용이며 현재 안내는 저장소 첫 화면을 사용하십시오.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

이번에 실제 전체 비교로 확인한 변경 파일: `src/app.py`, `src/brand.py`, `src/element_frames.py`, `src/elements.py`, `src/visuals.py`.

디자인 시안은 합성 예시값이 포함된 정적 이미지입니다. 실계정 잔량·현재 운영 화면·실제 애니메이션 수신 성공의 증거로 사용하지 않습니다.
