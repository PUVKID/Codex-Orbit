# 19차 공개 보존 설명

비교 대상: 18차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:677](src/app.py#L677) `Details` 정의 본문 변경; [src/app.py:448](src/app.py#L448) `Notice` 정의 본문 변경; [src/app.py:362](src/app.py#L362) `OrbitWidget` 정의 본문 변경; [src/app.py:773](src/app.py#L773) `build_history` 정의 본문 변경; [src/app.py:710](src/app.py#L710) `build_usage` 정의 본문 변경; [src/app.py:1347](src/app.py#L1347) `main` 정의 본문 변경; [src/app.py:397](src/app.py#L397) `paintEvent` 정의 본문 변경; [src/element_visuals.py:5](src/element_visuals.py#L5) `colorize_atom` 정의 본문 변경; [src/typography.py:22](src/typography.py#L22) `app_font` 정의 추가; [src/typography.py:8](src/typography.py#L8) `register_fonts` 정의 추가; [src/visuals.py:97](src/visuals.py#L97) `draw_orbit` 정의 본문 변경.
- **설정:** `src/visuals.py:94`의 숫자·불리언 상수 `SYMBOL_PIXELS = 30` (추가 또는 현재 값).
- **화면 코드:** `src/app.py:399`의 `setToolTip` 호출 (현재 코드).
- **문서:** 이번 보완에서 당시 문서·도구·자산의 원문 또는 정제본을 별도 [보존 목록](보존자료.md)에 연결했습니다. 파일별 원본 해시와 정제 사유를 구분하며 실제 실행 결과를 새로 추정하지 않습니다.
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


## 역사 자료 추가 보존

당시의 [문서·제작 도구·자산·시안 목록](보존자료.md)과 [원본/공개 해시·정제·제외 대응](부가자료_보존.json)을 제공합니다. 같은 SHA의 파일은 공통 보관 파일을 참조하며 실제 원본 경로와 버전을 보존합니다. 운영 기억·실제 계정/채팅 원문·비공개 검증은 제외하고 이유를 명시합니다. 보존 문서는 당시 내용이며 현재 안내는 저장소 첫 화면을 사용하십시오.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

이번에 실제 전체 비교로 확인한 변경 파일: `src/app.py`, `src/element_visuals.py`, `src/elements.py`, `src/theme.py`, `src/typography.py`, `src/visuals.py`.
