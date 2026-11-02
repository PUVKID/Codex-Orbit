# 2차 공개 보존 설명

비교 대상: 1차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:488](src/app.py#L488) `Controller` 정의 추가; [src/app.py:255](src/app.py#L255) `Details` 정의 추가; [src/app.py:70](src/app.py#L70) `Monitor` 정의 추가; [src/app.py:215](src/app.py#L215) `Notice` 정의 추가; [src/app.py:113](src/app.py#L113) `OrbitWidget` 정의 추가; [src/app.py:53](src/app.py#L53) `Settings` 정의 추가; [src/app.py:489](src/app.py#L489) `__init__` 정의 추가; [src/app.py:304](src/app.py#L304) `add_event` 정의 추가; [src/app.py:449](src/app.py#L449) `apply_md` 정의 추가; [src/app.py:23](src/app.py#L23) `asset` 정의 추가; [src/app.py:280](src/app.py#L280) `build_history` 정의 추가; [src/app.py:358](src/app.py#L358) `build_instructions` 정의 추가 외 49건은 전체 차이 참조.
- **설정:** `requirements.txt` 의존성 내용이 변경되었습니다. 값은 [전체 차이](직전차수.diff)에서 확인할 수 있습니다..
- **화면 코드:** `src/app.py:327`의 `QCheckBox` 호출 (현재 코드 · 라벨 `변경 시 클릭 가능한 말풍선 표시`); `src/app.py:323`의 `QComboBox` 호출 (현재 코드); `src/app.py:361`의 `QLabel` 호출 (현재 코드); `src/app.py:336`의 `QLabel` 호출 (현재 코드); `src/app.py:268`의 `QLabel` 호출 (현재 코드); `src/app.py:224`의 `QLabel` 호출 (현재 코드); `src/app.py:225`의 `QLabel` 호출 (현재 코드); `src/app.py:265`의 `QLabel` 호출 (현재 코드 · 라벨 `Codex Orbit`); `src/app.py:283`의 `QLabel` 호출 (현재 코드 · 라벨 `감시 준비 중`); `src/app.py:231`의 `QLabel` 호출 (현재 코드 · 라벨 `클릭하여 전체 이유와 근거 보기`); `src/app.py:393`의 `QPushButton` 호출 (현재 코드); `src/app.py:331`의 `QPushButton` 호출 (현재 코드) 외 18건은 전체 차이 참조.
- **문서:** 이번 보완에서 당시 문서·도구·자산의 원문 또는 정제본을 별도 [보존 목록](보존자료.md)에 연결했습니다. 파일별 원본 해시와 정제 사유를 구분하며 실제 실행 결과를 새로 추정하지 않습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **추가** `requirements.txt`: 이전 없음; 현재 47바이트, SHA-256 `0277c326e594b9e8ec8027fc240eda62a146295c2115466e872ab475d5699121`.
- **추가** `src/app.py`: 이전 없음; 현재 29190바이트, SHA-256 `87f6314b529e5831384703c6cd0fe97b212bb751eac632c0e7b422d1026f75da`.
  - Python 정의 이름: 추가 `Controller`, `Details`, `Monitor`, `Notice`, `OrbitWidget`, `Settings`, `__init__`, `add_event`, `apply_md`, `asset`, `build_history`, `build_instructions`, `build_settings`, `choose_sessions`, `close`, `contextMenuEvent`, `display`, `error`, `event_description`, `export_md`, `finish`, `import_md`, `invalidate_plan`, `load_default`, `main`, `model_label`, `mouseMoveEvent`, `mousePressEvent`, `mouseReleaseEvent`, `paintEvent`, `preferences`, `preview_md`, `project_target`, `receive`, `restore_md`, `restore_position`, `run`, `save`, `save_settings`, `select_event`, `send`, `show`, `start_monitor`, `status`, `stop_monitor`, `user_target`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **추가** `src/core.py`: 이전 없음; 현재 8223바이트, SHA-256 `6e6ae64f8d21cb1af9972916c8cbbeb9fa9e43d76d69fa723521803370a7b970`.
  - Python 정의 이름: 추가 `InstructionStore`, `__init__`, `_replace`, `_target`, `_unchanged`, `apply`, `clamp_position`, `digest`, `preview`, `read_jsonl_tail`, `read_text_strict`, `receipts`, `restore`, `safe_path`, `session_titles`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.


## 역사 자료 추가 보존

당시의 [문서·제작 도구·자산·시안 목록](보존자료.md)과 [원본/공개 해시·정제·제외 대응](부가자료_보존.json)을 제공합니다. 같은 SHA의 파일은 공통 보관 파일을 참조하며 실제 원본 경로와 버전을 보존합니다. 운영 기억·실제 계정/채팅 원문·비공개 검증은 제외하고 이유를 명시합니다. 보존 문서는 당시 내용이며 현재 안내는 저장소 첫 화면을 사용하십시오.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

이번에 실제 전체 비교로 확인한 변경 파일: `requirements.txt`, `src/app.py`, `src/core.py`, `src/toast.ps1`.
