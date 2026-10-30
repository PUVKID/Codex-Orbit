# 17차 공개 보존 설명

비교 대상: 16차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:838](src/app.py#L838) `Controller` 정의 본문 변경; [src/app.py:562](src/app.py#L562) `Details` 정의 본문 변경; [src/app.py:350](src/app.py#L350) `Notice` 정의 본문 변경; [src/app.py:266](src/app.py#L266) `OrbitWidget` 정의 본문 변경; [src/app.py:839](src/app.py#L839) `__init__` 정의 본문 변경; [src/app.py:658](src/app.py#L658) `build_history` 정의 본문 변경; [src/app.py:595](src/app.py#L595) `build_usage` 정의 본문 변경; [src/app.py:1179](src/app.py#L1179) `main` 정의 본문 변경; [src/brand.py:84](src/brand.py#L84) `AnimatedBrand` 정의 추가; [src/brand.py:29](src/brand.py#L29) `BrandClock` 정의 추가; [src/brand.py:86](src/brand.py#L86) `__init__` 정의 추가; [src/brand.py:40](src/brand.py#L40) `active_count` 정의 추가 외 12건은 전체 차이 참조.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** `src/app.py:581`의 `setToolTip` 호출 (이전 코드 · 라벨 `Codex Orbit`); `src/brand.py:190`의 `QLabel` 호출 (현재 코드); `src/brand.py:91`의 `setToolTip` 호출 (현재 코드).
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 67544바이트, SHA-256 `cb630d296cc6fa01fe50ace11358ba4a3ed12f7d2940a055195566dc7613b415`; 현재 67834바이트, SHA-256 `e475770e239c4bf0affbf36d2453faa16f9a29fc2a6c0c579d81235a4b9672e8`.
- **수정** `src/brand.py`: 이전 782바이트, SHA-256 `e940a95924da591064168b20f8486fd11026f6979f51db42d7a608e696bae48c`; 현재 8905바이트, SHA-256 `735283d9736dac88c819deaf7d342804dbf248c71535bc1b848ca6edb7b9f191`.
  - Python 정의 이름: 추가 `AnimatedBrand`, `BrandClock`, `__init__`, `active_count`, `brand_clock`, `closeEvent`, `hideEvent`, `prune`, `showEvent`, `symbol_icon`, `symbol_image`, `tick`, `unwatch`, `validate_symbols`, `watch`, `with_symbol`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/visuals.py`: 이전 6413바이트, SHA-256 `22db5d1f5aa30cb9ff8a4bf18c8d44f99a88893a6579f821b08b03f270a033ff`; 현재 6707바이트, SHA-256 `265e0872b25cf94cc9752cb8fef5886e46cc3a32aa240c1f712260c99f17b660`.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
