# 25차 공개 보존 설명

비교 대상: 24차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:1338](src/app.py#L1338) `Controller` 정의 본문 변경; [src/app.py:918](src/app.py#L918) `Details` 정의 본문 변경; [src/app.py:893](src/app.py#L893) `DiagnosticLabel` 정의 본문 변경; [src/app.py:630](src/app.py#L630) `Notice` 정의 본문 변경; [src/app.py:435](src/app.py#L435) `OrbitWidget` 정의 본문 변경; [src/app.py:278](src/app.py#L278) `Settings` 정의 본문 변경; [src/app.py:1339](src/app.py#L1339) `__init__` 정의 본문 변경; [src/app.py:734](src/app.py#L734) `_content_fit_signature` 정의 본문 변경; [src/app.py:514](src/app.py#L514) `_refresh_static_clock` 정의 추가; [src/app.py:523](src/app.py#L523) `_request_motion_size` 정의 추가; [src/app.py:213](src/app.py#L213) `activity_message` 정의 본문 변경; [src/app.py:1094](src/app.py#L1094) `build_history` 정의 본문 변경 외 117건은 전체 차이 참조.
- **설정:** `src/calendar_motion.py:15`의 숫자·불리언 상수 `FPS = 240` (추가 또는 현재 값); `src/calendar_motion.py:13`의 숫자·불리언 상수 `FPS = 30` (삭제 또는 이전 값).
- **화면 코드:** `src/app.py:936`의 `QComboBox` 호출 (현재 코드); `src/app.py:1074`의 `QLabel` 호출 (현재 코드); `src/app.py:1084`의 `QLabel` 호출 (현재 코드); `src/app.py:1015`의 `QLabel` 호출 (이전 코드); `src/app.py:1099`의 `QLabel` 호출 (현재 코드); `src/app.py:998`의 `QLabel` 호출 (현재 코드); `src/app.py:1026`의 `QLabel` 호출 (현재 코드); `src/app.py:1146`의 `QLabel` 호출 (현재 코드); `src/app.py:644`의 `QLabel` 호출 (현재 코드); `src/app.py:1147`의 `QLabel` 호출 (현재 코드); `src/app.py:1138`의 `QLabel` 호출 (현재 코드); `src/app.py:1139`의 `QLabel` 호출 (현재 코드) 외 102건은 전체 차이 참조.
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 103190바이트, SHA-256 `14011eab43bde0ac5a70f8f28b0fcaea6a81ac275c80027b4bbd239b35eefe50`; 현재 110155바이트, SHA-256 `bb0421143d08d6930d62f19252819ca26a91444466002c1a559b0dc87895ac3b`.
  - Python 정의 이름: 추가 `_refresh_static_clock`, `_request_motion_size`, `calendar_frame_ready`, `resizeEvent`, `retranslate`, `set_language`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/brand.py`: 이전 9612바이트, SHA-256 `8169160d69da479a9a58f49882ecfae2b8f5e068f1c42f542d9d7d7cc2039d20`; 현재 10147바이트, SHA-256 `bec1e0eff2b42da530b779b48fae0f0ceba56ff83a2872a8b7912d3939153852`.
  - Python 정의 이름: 추가 `calendar_frame_ready`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/calendar_motion.py`: 이전 10836바이트, SHA-256 `1212c2a51abd840070a4b8b3912dfbcf5f5f6ed2b3d78dfd6dbc825257ed3d0d`; 현재 15710바이트, SHA-256 `fcd254efc4bf9e4a15eb9a1d75177323d34763716cea207e2bd95348b93463a0`.
  - Python 정의 이름: 추가 `_configure_size`, `_dispatch_frame`, `next_frame_deadline`, `record_calendar_presentation`, `set_calendar_motion_size`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/calendar_renderer.py`: 이전 27178바이트, SHA-256 `230f965d7e430a117451ba60c7f0c1e05b99d4e4cd416b8dc8b7766206de7050`; 현재 30110바이트, SHA-256 `ca461e46f983969d9e06ba2f238b2b86e5a44f84a87570431993b1bfff25f03a`.
  - Python 정의 이름: 추가 `_draw`, `_image`, `render_original`, `set_output_size`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/frame_pacing.py`: 이전 없음; 현재 2625바이트, SHA-256 `6ca862a2eaa6707665f19514315de584424ab66017eff8f7898e3a4f6c6a9cb5`.
  - Python 정의 이름: 추가 `FrameWaiter`, `__init__`, `close`, `wait`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/i18n.py`: 이전 없음; 현재 19942바이트, SHA-256 `2dbea990824fb7107019228d5ecf6a75d7ce1a7062d0984f2a00908c7e26cec1`.
  - Python 정의 이름: 추가 `get_language`, `remember_translations`, `retranslate_widgets`, `set_language`, `translate`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/theme.py`: 이전 9195바이트, SHA-256 `e72f8620bd18a100492a45cc71ed49770f169310b800f90307bbd40a542dcf6b`; 현재 9297바이트, SHA-256 `cafeb00fa1b52f9ca342d224c64bb51cfe1e9aea13161f1a57fb6ea99e94dc7f`.
- **수정** `src/usage_widgets.py`: 이전 1671바이트, SHA-256 `77215ae54bbc0b5f60906e9ba1785e6e1f5cb57489cc225dde7d9427f7434226`; 현재 2471바이트, SHA-256 `a5e8de93da797f5f269551061d30878d8c0f86cae8824e89ba052bd6b28aeee2`.
  - Python 정의 이름: 추가 `_refresh_error`, `_request_motion_size`, `calendar_frame_ready`, `resizeEvent`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/visuals.py`: 이전 13225바이트, SHA-256 `6b8845e2c8bc60b3131f79d80400ecfd1c9574e677284796099aac54e4759161`; 현재 13297바이트, SHA-256 `d4bb20ebbfa421b5f05a482aedbb0b2202b7f7ffc2e6f7e22916ace3d0d72e1d`.
- **수정** `src/weather.py`: 이전 7032바이트, SHA-256 `835caa4e16462dc09801aae984ee34e84ea163e809532f5522851939e67884b3`; 현재 17524바이트, SHA-256 `acbb6804da7bde516461c739ed3e5c17bd26edee4f299b995822853dddd1b5e4`.
  - Python 정의 이름: 추가 `_abort_request`, `_cache_key`, `_geocode_done`, `_guard`, `_lookup_region`, `_request_failed`, `_request_weather`, `accept`, `clean`, `korean`, `localized_region`, `select_geocoded_region`, `set_language`, `valid`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
