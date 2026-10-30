# 16차 공개 보존 설명

비교 대상: 15차. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/app.py:566](src/app.py#L566) `Details` 정의 본문 변경; [src/app.py:350](src/app.py#L350) `Notice` 정의 본문 변경; [src/app.py:135](src/app.py#L135) `event_description` 정의 본문 변경; [src/app.py:123](src/app.py#L123) `event_kind` 정의 본문 변경; [src/app.py:74](src/app.py#L74) `previous_field` 정의 추가; [src/app.py:770](src/app.py#L770) `select_event` 정의 본문 변경; [src/app.py:526](src/app.py#L526) `setting_label` 정의 본문 변경.
- **설정:** 숫자·불리언 상수 또는 의존성 파일에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **화면 코드:** `src/app.py:509`의 `setText` 호출 (이전 코드); `src/app.py:773`의 `setText` 호출 (이전 코드); `src/app.py:789`의 `setText` 호출 (현재 코드); `src/app.py:768`의 `setText` 호출 (이전 코드); `src/app.py:784`의 `setText` 호출 (현재 코드); `src/app.py:507`의 `setText` 호출 (이전 코드); `src/app.py:517`의 `setText` 호출 (현재 코드); `src/app.py:771`의 `setText` 호출 (이전 코드); `src/app.py:787`의 `setText` 호출 (현재 코드); `src/app.py:506`의 `setText` 호출 (이전 코드); `src/app.py:516`의 `setText` 호출 (현재 코드); `src/app.py:505`의 `setText` 호출 (이전 코드) 외 3건은 전체 차이 참조.
- **문서:** 이 공개 이력에는 비교할 문서를 보존하지 않아 문서 변경은 확인할 수 없습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **수정** `src/app.py`: 이전 66680바이트, SHA-256 `ee151f176fc0035b441ac69bb0a6ea449f82034afcc270e72f2e412d29b4f177`; 현재 67544바이트, SHA-256 `cb630d296cc6fa01fe50ace11358ba4a3ed12f7d2940a055195566dc7613b415`.
  - Python 정의 이름: 추가 `previous_field`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.
