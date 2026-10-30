# 19차 공개 보존 설명

비교 대상: 18차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:677](src/app.py#L677) `Details` 정의 본문 변경; [src/app.py:448](src/app.py#L448) `Notice` 정의 본문 변경; [src/app.py:362](src/app.py#L362) `OrbitWidget` 정의 본문 변경; [src/app.py:773](src/app.py#L773) `build_history` 정의 본문 변경; [src/app.py:710](src/app.py#L710) `build_usage` 정의 본문 변경; [src/app.py:1347](src/app.py#L1347) `main` 정의 본문 변경; [src/app.py:397](src/app.py#L397) `paintEvent` 정의 본문 변경; [src/element_visuals.py:5](src/element_visuals.py#L5) `colorize_atom` 정의 본문 변경; [src/typography.py:22](src/typography.py#L22) `app_font` 정의 추가; [src/typography.py:8](src/typography.py#L8) `register_fonts` 정의 추가; [src/visuals.py:97](src/visuals.py#L97) `draw_orbit` 정의 본문 변경.
- **설정:** `src/visuals.py:94`의 숫자·불리언 상수 `SYMBOL_PIXELS = 30` (추가 또는 현재 값).
- **화면 코드:** `src/app.py:399`의 `setToolTip` 호출 (현재 코드).
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 77286바이트, SHA-256 `d1b5290ece7327f7421fd7cff5aa11c873bde5601ad6edbe95639088c4596608`; 현재 77255바이트, SHA-256 `7985e516248d9b840bf6d375e28025b3b5be8a63317170654659dac9445678e4`.
- **수정** `src/element_visuals.py`: 이전 800바이트, SHA-256 `a482d214b0cd73259d28561452bff4e5140a675e480301c90fcea84e3f4dd46f`; 현재 819바이트, SHA-256 `33ceea060b073d5a03af097d8e35e7f38ad5ec2252534402bd6a965328276f94`.
- **수정** `src/elements.py`: 이전 2484바이트, SHA-256 `598145f03922718a1a453ca585d7f19f93d90bca204dcfebbd2016e35f79e865`; 현재 2532바이트, SHA-256 `6357b9dce67a557de08eff0f7fd6cebfd9c08dfae2bf276e9d84610358aafe91`.
- **수정** `src/theme.py`: 이전 9000바이트, SHA-256 `dbeca97f9a88b79de748171de4dd70f1251e6f54b517413f269b435f75c8f857`; 현재 9033바이트, SHA-256 `c6c36da153e120f6683b53dccf95ee5174e3c197a547ab118d493bcaa2a48732`.
- **추가** `src/typography.py`: 이전 없음; 현재 1195바이트, SHA-256 `9f34c52a2178b2603aa789ced06ea4f98cf83cd263d6272122ceb64c747b41cf`.
  - Python 정의 이름: 추가 `app_font`, `register_fonts`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/visuals.py`: 이전 6227바이트, SHA-256 `b1bc638467f4aac52d6679df8ea8bfb933dcc227a7c232f6f05036ffe29a5ce3`; 현재 6495바이트, SHA-256 `c58a8a7bfb9b2fe9bd3643ad06fd07fd87ac683741d96a318a1a69a0fb4a7a8f`.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
