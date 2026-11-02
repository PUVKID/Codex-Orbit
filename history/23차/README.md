# 23차 공개 보존 설명

비교 대상: 22차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:1267](src/app.py#L1267) `Controller` 정의 본문 변경; [src/app.py:876](src/app.py#L876) `Details` 정의 본문 변경; [src/app.py:326](src/app.py#L326) `Monitor` 정의 본문 변경; [src/app.py:589](src/app.py#L589) `Notice` 정의 본문 변경; [src/app.py:291](src/app.py#L291) `NoticeDelivery` 정의 추가; [src/app.py:316](src/app.py#L316) `NoticeTicket` 정의 추가; [src/app.py:429](src/app.py#L429) `OrbitWidget` 정의 본문 변경; [src/app.py:1268](src/app.py#L1268) `__init__` 정의 본문 변경; [src/app.py:692](src/app.py#L692) `_content_fit_signature` 정의 추가; [src/app.py:1192](src/app.py#L1192) `_history_items_by_id` 정의 추가; [src/app.py:298](src/app.py#L298) `acquire` 정의 추가; [src/app.py:306](src/app.py#L306) `available` 정의 추가 외 65건은 전체 차이 참조.
- **설정:** `src/weather.py:15`의 숫자·불리언 상수 `INTERVAL_MS = 300000` (추가 또는 현재 값); `src/weather.py:13`의 숫자·불리언 상수 `LIMIT = 65536` (추가 또는 현재 값); `src/weather.py:14`의 숫자·불리언 상수 `TIMEOUT_MS = 8000` (추가 또는 현재 값).
- **화면 코드:** `src/app.py:1183`의 `setToolTip` 호출 (이전 코드); `src/app.py:503`의 `setToolTip` 호출 (현재 코드); `src/app.py:472`의 `setToolTip` 호출 (현재 코드); `src/app.py:413`의 `setToolTip` 호출 (이전 코드).
- **문서:** 이번 보완에서 당시 문서·도구·자산의 원문 또는 정제본을 별도 [보존 목록](보존자료.md)에 연결했습니다. 파일별 원본 해시와 정제 사유를 구분하며 실제 실행 결과를 새로 추정하지 않습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 90256바이트, SHA-256 `29241222e3f3447e0a62607c05dd2f7bec6fbb8a8539ffb855546b7d95c8fc11`; 현재 103035바이트, SHA-256 `b5a797db3021df14053b12b82cab8034febe57f417770da8ca7bf010d3eacbac`.
  - Python 정의 이름: 추가 `NoticeDelivery`, `NoticeTicket`, `_content_fit_signature`, `_history_items_by_id`, `acquire`, `available`, `clock_text`, `close_notice_delivery`, `deliver_next_notice`, `queue_delivery`, `queue_receive`, `refresh_tooltip`, `release`, `update_weather`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/calendar_art.py`: 이전 2055바이트, SHA-256 `95046b3a95e36da023a6630f1b61634561e32156e1334da0a1ef9d527482cc2a`; 현재 4132바이트, SHA-256 `5495a4f01dc6a30b47d94730f311f340aad081a658d8133f5bf2b0d112a54dc0`.
  - Python 정의 이름: 추가 `_month_palette`, `_raw_accent`, `_seed_for_date`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/calendar_catalog.py`: 이전 없음; 현재 16113바이트, SHA-256 `99e0b12a22a6c13cb10d7920781844844951abd469c96ad0bb8022936528b960`.
  - Python 정의 이름: 추가 `Collection`, `ObjectSpec`, `_objects`, `all_collections`, `collection_for_month`, `joining_particle`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/calendar_motion.py`: 이전 9270바이트, SHA-256 `25068bb3de9b72f14a06ba145654f8b79871b5283a3a75a4ec88ce05b10bfb2a`; 현재 10836바이트, SHA-256 `1212c2a51abd840070a4b8b3912dfbcf5f5f6ed2b3d78dfd6dbc825257ed3d0d`.
  - Python 정의 이름: 추가 `prepare_calendar_motion`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/calendar_renderer.py`: 이전 23148바이트, SHA-256 `f421f842ae08f4fb079be0fcab924ef2918400b2d6a6fe8c4df426b6cdeadbd5`; 현재 26714바이트, SHA-256 `95993486dfe841e29a7f01c6f21d3b9c217b4a1a47289743184940da72248c5b`.
  - Python 정의 이름: 추가 `_object_geometry`, `petal`, `radial`, `stem`; 삭제 `leaf`. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/visuals.py`: 이전 8089바이트, SHA-256 `43e9dc8030b72771abbaafea952c2d5796d43d86f324fe8755b59ab41d0bb14a`; 현재 12413바이트, SHA-256 `904fe83dc9cb06ac769a706059665aa211f5300f2ffb8c19c70b054ad0a74d4e`.
  - Python 정의 이름: 추가 `desktop_widget_layout`, `draw_desktop_orbit`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/weather.py`: 이전 없음; 현재 7032바이트, SHA-256 `835caa4e16462dc09801aae984ee34e84ea163e809532f5522851939e67884b3`.
  - Python 정의 이름: 추가 `WeatherClient`, `__init__`, `_check_age`, `_check_size`, `_fail`, `_finish`, `_get`, `_location_done`, `_publish`, `_timeout`, `_valid_number`, `_weather_done`, `close`, `refresh`, `start`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.


## 역사 자료 추가 보존

당시의 [문서·제작 도구·자산·시안 목록](보존자료.md)과 [원본/공개 해시·정제·제외 대응](부가자료_보존.json)을 제공합니다. 같은 SHA의 파일은 공통 보관 파일을 참조하며 실제 원본 경로와 버전을 보존합니다. 운영 기억·실제 계정/채팅 원문·비공개 검증은 제외하고 이유를 명시합니다. 보존 문서는 당시 내용이며 현재 안내는 저장소 첫 화면을 사용하십시오.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

이번에 실제 전체 비교로 확인한 변경 파일: `src/app.py`, `src/calendar_art.py`, `src/calendar_catalog.py`, `src/calendar_motion.py`, `src/calendar_renderer.py`, `src/visuals.py`, `src/weather.py`.
