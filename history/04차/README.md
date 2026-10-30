# 4차 공개 보존 설명

비교 대상: 3차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:749](src/app.py#L749) `Controller` 정의 본문 변경; [src/app.py:354](src/app.py#L354) `Details` 정의 본문 변경; [src/app.py:280](src/app.py#L280) `Notice` 정의 본문 변경; [src/app.py:177](src/app.py#L177) `OrbitWidget` 정의 본문 변경; [src/app.py:735](src/app.py#L735) `QuitGuard` 정의 추가; [src/app.py:750](src/app.py#L750) `__init__` 정의 본문 변경; [src/app.py:896](src/app.py#L896) `advance_notice` 정의 추가; [src/app.py:439](src/app.py#L439) `build_history` 정의 본문 변경; [src/app.py:536](src/app.py#L536) `build_settings` 정의 본문 변경; [src/app.py:380](src/app.py#L380) `build_usage` 정의 추가; [src/app.py:839](src/app.py#L839) `check_monitor_health` 정의 추가; [src/app.py:580](src/app.py#L580) `choose_codex` 정의 추가 외 49건은 전체 차이 참조.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** `src/app.py:385`의 `QLabel` 호출 (현재 코드); `src/app.py:392`의 `QLabel` 호출 (현재 코드); `src/app.py:396`의 `QLabel` 호출 (현재 코드 · 라벨 `계정 한도 미확인`); `src/app.py:447`의 `QLabel` 호출 (현재 코드 · 라벨 `알림 대기 0건`); `src/app.py:551`의 `QPushButton` 호출 (현재 코드 · 라벨 `Codex EXE 선택`); `src/app.py:388`의 `QPushButton` 호출 (현재 코드 · 라벨 `새로고침`); `src/app.py:872`의 `setText` 호출 (현재 코드); `src/app.py:873`의 `setText` 호출 (현재 코드); `src/app.py:844`의 `setText` 호출 (현재 코드); `src/app.py:849`의 `setText` 호출 (현재 코드); `src/app.py:819`의 `setText` 호출 (현재 코드); `src/app.py:970`의 `setText` 호출 (현재 코드) 외 4건은 전체 차이 참조.
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 39580바이트, SHA-256 `93d5ba9d617c35f5e547642ddf31199791b462f1530856124ae65c780d2e7929`; 현재 54704바이트, SHA-256 `6fee6fa67549f53b670f621c24fcc190ddd4801e01c6c816649e1414e84ee546`.
  - Python 정의 이름: 추가 `QuitGuard`, `advance_notice`, `build_usage`, `check_monitor_health`, `choose_codex`, `dismiss`, `display_usage`, `enqueue_notice`, `eventFilter`, `finish_quit`, `finish_usage`, `request_quit`, `restart_dead_monitor`, `restart_usage`, `update_notice_count`, `update_usage`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/usage.py`: 이전 없음; 현재 15245바이트, SHA-256 `dddcd5beef9281e9652c0cceff77f0240df669396a2bae18370ef30144a1406e`.
  - Python 정의 이름: 추가 `UsageClient`, `__init__`, `_accept`, `_check_age`, `_failed`, `_finished`, `_launch`, `_message`, `_process_error`, `_publish`, `_retry`, `_send`, `_started`, `_stderr`, `_stdout`, `_timeout`, `close`, `discover_codex`, `feed_bytes`, `manual_refresh`, `normalize_limits`, `number`, `refresh`, `reset_label`, `start`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
