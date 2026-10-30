# 24차 공개 보존 설명

비교 대상: 23차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:1268](src/app.py#L1268) `Controller` 정의 본문 변경; [src/app.py:429](src/app.py#L429) `OrbitWidget` 정의 본문 변경; [src/app.py:506](src/app.py#L506) `paintEvent` 정의 본문 변경; [src/app.py:1338](src/app.py#L1338) `update_weather` 정의 본문 변경; [src/calendar_renderer.py:378](src/calendar_renderer.py#L378) `CalendarRenderer` 정의 본문 변경; [src/calendar_renderer.py:323](src/calendar_renderer.py#L323) `_ring_geometry` 정의 추가; [src/calendar_renderer.py:334](src/calendar_renderer.py#L334) `build_geometry` 정의 본문 변경; [src/calendar_renderer.py:363](src/calendar_renderer.py#L363) `matrices` 정의 본문 변경; [src/calendar_renderer.py:411](src/calendar_renderer.py#L411) `render` 정의 본문 변경; [src/visuals.py:175](src/visuals.py#L175) `desktop_widget_layout` 정의 본문 변경; [src/visuals.py:211](src/visuals.py#L211) `draw_desktop_orbit` 정의 본문 변경.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** 지정한 위젯 생성·라벨 호출에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 103035바이트, SHA-256 `b5a797db3021df14053b12b82cab8034febe57f417770da8ca7bf010d3eacbac`; 현재 103190바이트, SHA-256 `14011eab43bde0ac5a70f8f28b0fcaea6a81ac275c80027b4bbd239b35eefe50`.
- **수정** `src/calendar_renderer.py`: 이전 26714바이트, SHA-256 `95993486dfe841e29a7f01c6f21d3b9c217b4a1a47289743184940da72248c5b`; 현재 27178바이트, SHA-256 `230f965d7e430a117451ba60c7f0c1e05b99d4e4cd416b8dc8b7766206de7050`.
  - Python 정의 이름: 추가 `_ring_geometry`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.
- **수정** `src/visuals.py`: 이전 12413바이트, SHA-256 `904fe83dc9cb06ac769a706059665aa211f5300f2ffb8c19c70b054ad0a74d4e`; 현재 13225바이트, SHA-256 `6b8845e2c8bc60b3131f79d80400ecfd1c9574e677284796099aac54e4759161`.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
