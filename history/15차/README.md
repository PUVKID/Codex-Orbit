# 15차 공개 보존 설명

비교 대상: 14차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:820](src/app.py#L820) `Controller` 정의 본문 변경; [src/app.py:821](src/app.py#L821) `__init__` 정의 본문 변경; [src/app.py:1160](src/app.py#L1160) `main` 정의 본문 변경; [src/atom_frames.py:27](src/atom_frames.py#L27) `AtomAssetError` 정의 추가; [src/atom_frames.py:50](src/atom_frames.py#L50) `AtomFrames` 정의 추가; [src/atom_frames.py:52](src/atom_frames.py#L52) `__init__` 정의 추가; [src/atom_frames.py:131](src/atom_frames.py#L131) `_check_unchanged` 정의 추가; [src/atom_frames.py:115](src/atom_frames.py#L115) `_decode` 정의 추가; [src/atom_frames.py:36](src/atom_frames.py#L36) `_identity` 정의 추가; [src/atom_frames.py:41](src/atom_frames.py#L41) `_json_object` 정의 추가; [src/atom_frames.py:66](src/atom_frames.py#L66) `_prepare` 정의 추가; [src/atom_frames.py:31](src/atom_frames.py#L31) `asset_directory` 정의 추가 외 12건은 전체 차이 참조.
- **설정:** `src/atom_frames.py:20`의 숫자·불리언 상수 `CACHE_LIMIT = 24` (추가 또는 현재 값); `src/atom_frames.py:18`의 숫자·불리언 상수 `FPS = 30` (추가 또는 현재 값); `src/atom_frames.py:16`의 숫자·불리언 상수 `FRAME_COUNT = 540` (추가 또는 현재 값); `src/atom_frames.py:17`의 숫자·불리언 상수 `FRAME_SIZE = 296` (추가 또는 현재 값); `src/atom_frames.py:19`의 숫자·불리언 상수 `PERIOD_SECONDS = 18` (추가 또는 현재 값).
- **화면 코드:** 지정한 위젯 생성·라벨 호출에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 66311바이트, SHA-256 `b676ddee99746c0ea1b439cb9636fe6190db0f01017d71e830473534be871d2f`; 현재 66680바이트, SHA-256 `ee151f176fc0035b441ac69bb0a6ea449f82034afcc270e72f2e412d29b4f177`.
- **추가** `src/atom_frames.py`: 이전 없음; 현재 8515바이트, SHA-256 `af5b5331068fb58b1daf33d124bd4d8bb33b76bc017435aa79b4ed701b7ed962`.
  - Python 정의 이름: 추가 `AtomAssetError`, `AtomFrames`, `__init__`, `_check_unchanged`, `_decode`, `_identity`, `_json_object`, `_prepare`, `asset_directory`, `cache_bytes`, `close`, `close_runtime_frames`, `frame`, `frame_index`, `get_atom_frames`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/brand.py`: 이전 1382바이트, SHA-256 `cfb51d3ce075e0ab59852f92c37efcaea28a04c2af6d5a2cee97c9ff006d6c00`; 현재 782바이트, SHA-256 `e940a95924da591064168b20f8486fd11026f6979f51db42d7a608e696bae48c`.
- **수정** `src/visuals.py`: 이전 7619바이트, SHA-256 `fdc1b3703573d3751fb91591f12b5262a89fcab8b48a6915bff1a600b2294784`; 현재 6413바이트, SHA-256 `22db5d1f5aa30cb9ff8a4bf18c8d44f99a88893a6579f821b08b03f270a033ff`.
  - Python 정의 이름: 추가 없음; 삭제 `lines`. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
