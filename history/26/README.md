# 26차 공개 보존 설명

비교 대상: 25차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:1408](src/app.py#L1408) `Controller` 정의 본문 변경; [src/app.py:943](src/app.py#L943) `Details` 정의 본문 변경; [src/app.py:447](src/app.py#L447) `OrbitWidget` 정의 본문 변경; [src/app.py:286](src/app.py#L286) `Settings` 정의 본문 변경; [src/app.py:1409](src/app.py#L1409) `__init__` 정의 본문 변경; [src/app.py:1484](src/app.py#L1484) `change_motion_speed` 정의 추가; [src/app.py:633](src/app.py#L633) `create_menu` 정의 본문 변경; [src/app.py:552](src/app.py#L552) `paintEvent` 정의 본문 변경; [src/app.py:1029](src/app.py#L1029) `retranslate` 정의 본문 변경; [src/app.py:1496](src/app.py#L1496) `set_motion_speed` 정의 추가; [src/app.py:1022](src/app.py#L1022) `show_motion_speed_error` 정의 추가; [src/app.py:1015](src/app.py#L1015) `update_motion_speed` 정의 추가 외 24건은 전체 차이 참조.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** `src/app.py:974`의 `QLabel` 호출 (현재 코드); `src/app.py:987`의 `QPushButton` 호출 (현재 코드); `src/app.py:976`의 `QSlider` 호출 (현재 코드); `src/app.py:1026`의 `setText` 호출 (현재 코드); `src/app.py:1020`의 `setText` 호출 (현재 코드); `src/app.py:982`의 `setToolTip` 호출 (현재 코드); `src/motion_label.py:37`의 `setText` 호출 (현재 코드).
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 110155바이트, SHA-256 `bb0421143d08d6930d62f19252819ca26a91444466002c1a559b0dc87895ac3b`; 현재 116115바이트, SHA-256 `ccb4c5771ab1a01e416e81dcc3678629cd5a5a2613e50d5e7c4a3e4263da964f`.
  - Python 정의 이름: 추가 `change_motion_speed`, `set_motion_speed`, `show_motion_speed_error`, `update_motion_speed`, `validated_motion_speed`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/calendar_motion.py`: 이전 15710바이트, SHA-256 `fcd254efc4bf9e4a15eb9a1d75177323d34763716cea207e2bd95348b93463a0`; 현재 16207바이트, SHA-256 `ddb3e8afdf5f46f7bb8f997e75c39234550f28bade6223e19f81e37579765791`.
  - Python 정의 이름: 추가 `set_calendar_motion_speed`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/frame_pacing.py`: 이전 2625바이트, SHA-256 `6ca862a2eaa6707665f19514315de584424ab66017eff8f7898e3a4f6c6a9cb5`; 현재 3692바이트, SHA-256 `09cd3768e4baa326bb0e08e4d7fd8130f05526024686b88f8ef2f9b0366b1bb1`.
  - Python 정의 이름: 추가 `MotionClock`, `sample`, `set_speed`, `validate_motion_speed`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/i18n.py`: 이전 19942바이트, SHA-256 `2dbea990824fb7107019228d5ecf6a75d7ce1a7062d0984f2a00908c7e26cec1`; 현재 20538바이트, SHA-256 `091208c023ccecdefd7957dcc3bacd8acc5c44324dd587ac36986ac3dc81106a`.
- **추가** `src/motion_label.py`: 이전 없음; 현재 2380바이트, SHA-256 `f76a05b63a676282ff4816c25ce0d7bc4aa01396889559c76021d5f858a0c60d`.
  - Python 정의 이름: 추가 `MotionImageLabel`, `__init__`, `clear`, `paintEvent`, `pixmap`, `setPixmap`, `setText`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/usage_widgets.py`: 이전 2471바이트, SHA-256 `a5e8de93da797f5f269551061d30878d8c0f86cae8824e89ba052bd6b28aeee2`; 현재 2516바이트, SHA-256 `9ad1be24d27cbf072db6892a2bc3c431304002f90f9a9d46d59494a91b74814c`.
- **수정** `src/visuals.py`: 이전 13297바이트, SHA-256 `d4bb20ebbfa421b5f05a482aedbb0b2202b7f7ffc2e6f7e22916ace3d0d72e1d`; 현재 15915바이트, SHA-256 `13a8d20b188ac2e82bc57771263dd6c2bef7cb3ab96ef259d51fd73fa380a57a`.
  - Python 정의 이름: 추가 `DesktopOverlayCache`, `__init__`, `_draw_desktop_information`, `draw`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
