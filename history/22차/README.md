# 22차 공개 보존 설명

비교 대상: 21차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:1103](src/app.py#L1103) `Controller` 정의 본문 변경; [src/app.py:729](src/app.py#L729) `Details` 정의 본문 변경; [src/app.py:481](src/app.py#L481) `Notice` 정의 본문 변경; [src/app.py:379](src/app.py#L379) `OrbitWidget` 정의 본문 변경; [src/app.py:1104](src/app.py#L1104) `__init__` 정의 본문 변경; [src/app.py:35](src/app.py#L35) `_application_gui_root` 정의 추가; [src/app.py:1491](src/app.py#L1491) `_finish_closed_gui` 정의 추가; [src/app.py:877](src/app.py#L877) `build_history` 정의 본문 변경; [src/app.py:774](src/app.py#L774) `build_usage` 정의 본문 변경; [src/app.py:1242](src/app.py#L1242) `check_monitor_health` 정의 본문 변경; [src/app.py:1460](src/app.py#L1460) `close` 정의 본문 변경; [src/app.py:1352](src/app.py#L1352) `display_notice` 정의 본문 변경 외 89건은 전체 차이 참조.
- **설정:** `requirements.txt` 의존성 내용이 변경되었습니다. 값은 [전체 차이](직전차수.diff)에서 확인할 수 있습니다.; `src/calendar_motion.py:13`의 숫자·불리언 상수 `FPS = 30` (추가 또는 현재 값); `src/calendar_motion.py:14`의 숫자·불리언 상수 `SIZE = 384` (추가 또는 현재 값); `src/calendar_renderer.py:131`의 숫자·불리언 상수 `PERIOD = 12.0` (추가 또는 현재 값); `src/calendar_renderer.py:132`의 숫자·불리언 상수 `SIZE = 384` (추가 또는 현재 값); `src/usage_frames.py:20`의 숫자·불리언 상수 `CACHE_LIMIT = 16` (추가 또는 현재 값); `src/usage_frames.py:18`의 숫자·불리언 상수 `FPS = 30` (추가 또는 현재 값); `src/usage_frames.py:16`의 숫자·불리언 상수 `FRAME_COUNT = 360` (추가 또는 현재 값); `src/usage_frames.py:17`의 숫자·불리언 상수 `FRAME_SIZE = 384` (추가 또는 현재 값); `src/usage_frames.py:19`의 숫자·불리언 상수 `PERIOD_SECONDS = 12` (추가 또는 현재 값).
- **화면 코드:** `src/app.py:867`의 `QLabel` 호출 (현재 코드); `src/app.py:717`의 `QLabel` 호출 (이전 코드); `src/app.py:857`의 `QLabel` 호출 (현재 코드); `src/app.py:862`의 `QLabel` 호출 (현재 코드); `src/app.py:783`의 `QLabel` 호출 (현재 코드 · 라벨 `계정 사용 한도`); `src/app.py:531`의 `QLabel` 호출 (현재 코드 · 라벨 `변경 후`); `src/app.py:672`의 `setText` 호출 (현재 코드); `src/app.py:829`의 `setText` 호출 (현재 코드); `src/app.py:749`의 `setText` 호출 (이전 코드); `src/app.py:1024`의 `setText` 호출 (현재 코드); `src/usage_widgets.py:35`의 `setText` 호출 (현재 코드).
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `requirements.txt`: 이전 47바이트, SHA-256 `0277c326e594b9e8ec8027fc240eda62a146295c2115466e872ab475d5699121`; 현재 109바이트, SHA-256 `76b74752d8b722fc13167e416df61ed80798286ac4762a5a8668b21ab4d93024`.
- **수정** `src/app.py`: 이전 77768바이트, SHA-256 `27b7ae6fa48e57d0f042667eb2ba16ffd2a4a4d4b188681df1b30517a11e5519`; 현재 90256바이트, SHA-256 `29241222e3f3447e0a62607c05dd2f7bec6fbb8a8539ffb855546b7d95c8fc11`.
  - Python 정의 이름: 추가 `_application_gui_root`, `_finish_closed_gui`, `hideEvent`, `motion_smoke_stage`, `showEvent`, `update_usage_motion`, `usage_smoke_state`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/brand.py`: 이전 9343바이트, SHA-256 `a04c41ac93f2256689e00ccc2c94469eb02e77af24faf6666a49d18dbee8164c`; 현재 9612바이트, SHA-256 `8169160d69da479a9a58f49882ecfae2b8f5e068f1c42f542d9d7d7cc2039d20`.
- **추가** `src/calendar_art.py`: 이전 없음; 현재 2055바이트, SHA-256 `95046b3a95e36da023a6630f1b61634561e32156e1334da0a1ef9d527482cc2a`.
  - Python 정의 이름: 추가 `Design`, `all_designs`, `current_date`, `design_for_date`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/calendar_motion.py`: 이전 없음; 현재 9270바이트, SHA-256 `25068bb3de9b72f14a06ba145654f8b79871b5283a3a75a4ec88ce05b10bfb2a`.
  - Python 정의 이름: 추가 `CalendarMotion`, `_Worker`, `__init__`, `_get_service`, `_main_thread`, `calendar_motion_status`, `close`, `close_calendar_motion`, `configure`, `fallback_image`, `frame`, `get_calendar_error`, `get_calendar_frame`, `gone`, `run`, `set_calendar_motion_visible`, `stop`, `visible`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/calendar_renderer.py`: 이전 없음; 현재 23148바이트, SHA-256 `f421f842ae08f4fb079be0fcab924ef2918400b2d6a6fe8c4df426b6cdeadbd5`.
  - Python 정의 이름: 추가 `CalendarRenderer`, `__init__`, `_assert_thread`, `_clear_meshes`, `_transformed`, `add`, `box`, `build_geometry`, `close`, `finish`, `lathe`, `leaf`, `matrices`, `orb`, `render`, `render_date`, `rod`, `rotation`, `set_date`, `sphere_mesh`, `tube`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/theme.py`: 이전 9033바이트, SHA-256 `c6c36da153e120f6683b53dccf95ee5174e3c197a547ab118d493bcaa2a48732`; 현재 9195바이트, SHA-256 `e72f8620bd18a100492a45cc71ed49770f169310b800f90307bbd40a542dcf6b`.
- **추가** `src/usage_frames.py`: 이전 없음; 현재 9564바이트, SHA-256 `a141ce6eaeefefbe942cf04116c032ec3c8ab383bbb07a028e5961c5026c9957`.
  - Python 정의 이름: 추가 `UsageAssetError`, `UsageFrames`, `__init__`, `_check_unchanged`, `_decode`, `_identity`, `_json_object`, `_prepare`, `asset_directory`, `cache_bytes`, `close`, `close_usage_frames`, `frame`, `frame_index`, `get_usage_frame`, `preflight_usage_frames`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/usage_widgets.py`: 이전 없음; 현재 1671바이트, SHA-256 `77215ae54bbc0b5f60906e9ba1785e6e1f5cb57489cc225dde7d9427f7434226`.
  - Python 정의 이름: 추가 `CalendarHero`, `__init__`, `refresh_frame`, `set_active`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/visuals.py`: 이전 7461바이트, SHA-256 `2a9004efcde7367ce9324655c384863e5b7ec07fab5816efdd5be6bdb3fd9c17`; 현재 8089바이트, SHA-256 `43e9dc8030b72771abbaafea952c2d5796d43d86f324fe8755b59ab41d0bb14a`.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
