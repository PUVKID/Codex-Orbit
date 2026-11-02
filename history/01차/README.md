# 1차 공개 보존 설명

비교 대상: 없음. 공개 보존 범위는 이 폴더의 `src/`와 `requirements.txt`입니다. 원본 프로젝트 전체의 차이는 아닙니다.

텍스트는 엄격 UTF-8로 판정하며 [전체 텍스트 차이](직전차수.diff)에는 주석과 공백을 포함합니다. 파일별 바이트 수와 SHA-256 및 바이너리 여부는 [비교 명세](공개파일_비교.json)에 기록합니다.

## 확인한 변경 범위

- **기능 코드:** [src/notifier.py:410](src/notifier.py#L410) `InstanceLock` 정의 추가; [src/notifier.py:369](src/notifier.py#L369) `NativeToast` 정의 추가; [src/notifier.py:45](src/notifier.py#L45) `Watcher` 정의 추가; [src/notifier.py:373](src/notifier.py#L373) `__call__` 정의 추가; [src/notifier.py:415](src/notifier.py#L415) `__enter__` 정의 추가; [src/notifier.py:430](src/notifier.py#L430) `__exit__` 정의 추가; [src/notifier.py:411](src/notifier.py#L411) `__init__` 정의 추가; [src/notifier.py:37](src/notifier.py#L37) `append_log` 정의 추가; [src/notifier.py:30](src/notifier.py#L30) `atomic_json` 정의 추가; [src/notifier.py:66](src/notifier.py#L66) `diagnostic` 정의 추가; [src/notifier.py:69](src/notifier.py#L69) `event` 정의 추가; [src/notifier.py:389](src/notifier.py#L389) `label` 정의 추가 외 9건은 전체 차이 참조.
- **설정:** `src/notifier.py:20`의 숫자·불리언 상수 `MAX_FILES = 4096` (추가 또는 현재 값); `src/notifier.py:23`의 숫자·불리언 상수 `MAX_PENDING = 256` (추가 또는 현재 값).
- **화면 코드:** 지정한 위젯 생성·라벨 호출에서 이 요약 조건에 맞는 변경은 확인되지 않았습니다.
- **문서:** 이번 보완에서 당시 문서·도구·자산의 원문 또는 정제본을 별도 [보존 목록](보존자료.md)에 연결했습니다. 파일별 원본 해시와 정제 사유를 구분하며 실제 실행 결과를 새로 추정하지 않습니다.
- **검증:** 당시 실행 결과는 이 공개 이력에 보존되지 않아 실행 여부를 확인할 수 없습니다. 여기서는 공개 소스 바이트만 비교했습니다.

아래 요약은 대표 코드 위치이며 전체 변경은 비교 파일에서 확인할 수 있습니다.

## 파일별 차이

- **추가** `src/notifier.py`: 이전 없음; 현재 26813바이트, SHA-256 `2059fcac37723f34535eba05d83443a9dbd7e3dfb771200f190f2c8ed2ffb9a8`.
  - Python 정의 이름: 추가 `InstanceLock`, `NativeToast`, `Watcher`, `__call__`, `__enter__`, `__exit__`, `__init__`, `append_log`, `atomic_json`, `diagnostic`, `event`, `label`, `limited`, `main`, `poll`, `powershell`, `public_reason`, `read_file`, `record`, `stamp`, `units`; 삭제 없음. 이름의 변화는 기능 효과를 보장하지 않습니다.

동일 이름 정의 내부의 변경, 설정값, 주석과 공백은 전체 차이에서 확인할 수 있습니다. 실행이나 성능 검증 결과는 이 비교에서 추론하지 않습니다.


## 역사 자료 추가 보존

당시의 [문서·제작 도구·자산·시안 목록](보존자료.md)과 [원본/공개 해시·정제·제외 대응](부가자료_보존.json)을 제공합니다. 같은 SHA의 파일은 공통 보관 파일을 참조하며 실제 원본 경로와 버전을 보존합니다. 운영 기억·실제 계정/채팅 원문·비공개 검증은 제외하고 이유를 명시합니다. 보존 문서는 당시 내용이며 현재 안내는 저장소 첫 화면을 사용하십시오.

[실행 소스 전체 Git 비교](직전차수.diff)와 [실제 바이트 명세](공개파일_비교.json)는 Python뿐 아니라 존재하는 보조 PowerShell과 의존성 목록을 포함합니다. `git -c core.autocrlf=false apply --reverse --binary -p1`로 현재 소스 사본에서 직전 소스의 파일 부재·신규·삭제 상태까지 복원해 원문 바이트를 대조했습니다. 부가 자료는 이 소스 비교에 섞지 않고 위 명세로 구분합니다.

이번에 실제 전체 비교로 확인한 변경 파일: `src/notifier.py`, `src/toast.ps1`.

`src/toast.ps1`은 당시 `src/notifier.py`가 참조한 알림 전송·설치·제거 보조 런타임입니다. 누락되었던 7,245바이트 원문을 추가했으며 현재 Windows에서 다시 실행하거나 전송 성공을 확인했다는 뜻은 아닙니다.
