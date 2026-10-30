# 14차 공개 보존 설명

비교 대상: 13차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:819](src/app.py#L819) `Controller` 정의 본문 변경; [src/app.py:556](src/app.py#L556) `Details` 정의 본문 변경; [src/app.py:531](src/app.py#L531) `DiagnosticLabel` 정의 추가; [src/app.py:339](src/app.py#L339) `Notice` 정의 본문 변경; [src/app.py:255](src/app.py#L255) `OrbitWidget` 정의 본문 변경; [src/app.py:820](src/app.py#L820) `__init__` 정의 본문 변경; `src/app.py`의 이전 코드 `apply_md` 정의 삭제; [src/app.py:652](src/app.py#L652) `build_history` 정의 본문 변경; `src/app.py`의 이전 코드 `build_instructions` 정의 삭제; `src/app.py`의 이전 코드 `build_settings` 정의 삭제; [src/app.py:943](src/app.py#L943) `check_monitor_health` 정의 본문 변경; `src/app.py`의 이전 코드 `choose_codex` 정의 삭제 외 24건은 전체 차이 참조.
- **설정:** `src/visuals.py:23`의 숫자·불리언 상수 `MOTION_PERIOD = 18` (추가 또는 현재 값).
- **화면 코드:** `src/app.py:804`의 `QCheckBox` 호출 (이전 코드 · 라벨 `변경 시 클릭 가능한 말풍선 표시`); `src/app.py:807`의 `QCheckBox` 호출 (이전 코드 · 라벨 `알림을 직접 닫을 때까지 유지`); `src/app.py:800`의 `QComboBox` 호출 (이전 코드); `src/app.py:722`의 `QLabel` 호출 (현재 코드); `src/app.py:667`의 `QLabel` 호출 (이전 코드); `src/app.py:816`의 `QLabel` 호출 (이전 코드); `src/app.py:888`의 `QLabel` 호출 (이전 코드); `src/app.py:721`의 `QLabel` 호출 (현재 코드); `src/app.py:864`의 `QLabel` 호출 (이전 코드 · 라벨 `내 지침`); `src/app.py:867`의 `QLabel` 호출 (이전 코드 · 라벨 `작성한 내용을 확인한 뒤 적용하세요. 파일은 명시 적용할 때만 바뀝니다.`); `src/app.py:914`의 `QLabel` 호출 (이전 코드 · 라벨 `적용 전 원문을 자동 백업합니다. 적용 후 대상이 바뀌면 충돌을 거부합니다.`); `src/app.py:871`의 `QLabel` 호출 (이전 코드 · 라벨 `적용할 파일`) 외 30건은 전체 차이 참조.
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 77972바이트, SHA-256 `4e467339765e8e3c2c78aa1ecac416b9bcdc8e63e7498999233cfde39f8d3ead`; 현재 66311바이트, SHA-256 `b676ddee99746c0ea1b439cb9636fe6190db0f01017d71e830473534be871d2f`.
  - Python 정의 이름: 추가 `DiagnosticLabel`, `setPlainText`, `toPlainText`; 삭제 `apply_md`, `build_instructions`, `build_settings`, `choose_codex`, `choose_sessions`, `error`, `export_md`, `import_md`, `invalidate_plan`, `load_default`, `preferences`, `preview_md`, `project_target`, `resizeEvent`, `restore_md`, `save_settings`, `user_target`. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/brand.py`: 이전 1265바이트, SHA-256 `45890a8eeb6f6b10bc1e91036bb973773633842ae2ac9799fe1f78003a19b2ca`; 현재 1382바이트, SHA-256 `cfb51d3ce075e0ab59852f92c37efcaea28a04c2af6d5a2cee97c9ff006d6c00`.
- **수정** `src/visuals.py`: 이전 6585바이트, SHA-256 `3c6d9ed9ace7377a4506e94a4eff961289e6cc1d3f372b35a8cb5591ac8b5756`; 현재 7619바이트, SHA-256 `fdc1b3703573d3751fb91591f12b5262a89fcab8b48a6915bff1a600b2294784`.
  - Python 정의 이름: 추가 `axis_rotate`, `ring_normal`, `ring_points`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
