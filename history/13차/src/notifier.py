"""현재 사용자 로컬 JSONL을 읽는 모델 변경 감시기. 외부 통신은 하지 않습니다."""
import argparse
import base64
import ctypes
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from core import read_jsonl_tail

ROOT = Path(__file__).resolve().parents[1]
APP_ID = 'Yunseok.Codex.ModelChangeNotifier'
READ_BYTES = 512 * 1024
MAX_RECORD = 2 * 1024 * 1024
MAX_FILES = 4096
LOG_BYTES = 2 * 1024 * 1024
POLL_READ_BYTES = 8 * 1024 * 1024
MAX_PENDING = 256
POLL_INTERVAL_SECONDS = 0.2


def stamp():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    """같은 폴더의 독립 임시 파일로 교체하며 Windows의 짧은 공유 경합만 재시도합니다."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name('.' + path.name + '.' + uuid.uuid4().hex + '.tmp')
    failure = None
    try:
        with temp.open('x', encoding='utf-8') as handle:
            handle.write(json.dumps(value, ensure_ascii=False))
        delays = (0.02, 0.04, 0.08, 0.12)
        for attempt in range(len(delays) + 1):
            try:
                os.replace(temp, path)
                break
            except OSError as error:
                if getattr(error, 'winerror', None) not in (5, 32, 33) or attempt == len(delays):
                    raise
                time.sleep(delays[attempt])
    except Exception as error:
        failure = error
        raise
    finally:
        try:
            temp.unlink(missing_ok=True)
        except OSError as cleanup_error:
            if failure is None:
                raise
            failure.add_note('임시 파일 정리도 실패했습니다: ' + str(cleanup_error))


def source_datetime(value):
    """시간대가 있는 유효한 원본 시각만 비교하며 없는 시각은 추정하지 않습니다."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo is not None else None
    except (ValueError, OverflowError):
        return None


def append_log(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size >= LOG_BYTES:
        os.replace(path, path.with_suffix('.previous.jsonl'))
    with path.open('a', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + '\n')


class Watcher:
    def __init__(self, sessions, work, sender):
        self.sessions, self.work, self.sender = Path(sessions), Path(work), sender
        self.work.mkdir(parents=True, exist_ok=True)
        self.state_path = self.work / 'state.json'
        self.state = {'schema_version': 3, 'initialized': False, 'files': {}, 'models': {}, 'settings': {},
                      'declarations': {}, 'pending': [], 'reasons': {}, 'seen': []}
        if self.state_path.exists():
            if self.state_path.stat().st_size > 16 * 1024 * 1024:
                raise ValueError('상태 파일이 16 MiB 상한을 초과했습니다. 원본 보존 후 점검이 필요합니다.')
            original = self.state_path.read_bytes()
            self.state = json.loads(original.decode('utf-8'))
            if self.state.get('schema_version') not in (2, 3):
                raise ValueError('구형 상태는 요청과 관측이 혼합되어 있습니다. 원본 보존 후 명시적 재기준선이 필요합니다.')
            if not isinstance(self.state.get('files'), dict) or not isinstance(self.state.get('models'), dict):
                raise ValueError('상태 파일 구조 오류입니다. 자동 초기화하지 않습니다.')
            if not isinstance(self.state.get('declarations'), dict):
                raise ValueError('명시 배정 상태 구조 오류입니다. 자동 초기화하지 않습니다.')
            if self.state['schema_version'] == 2:
                # 이미 소비한 위치를 고정해 재생합니다. 그 뒤 추가된 선택은 새 알림입니다.
                digest = hashlib.sha256(original).hexdigest()
                backup = self.work / ('state.before-settings-v3-' + digest + '.json')
                if backup.exists():
                    if backup.read_bytes() != original:
                        raise ValueError('이전 상태 백업이 원본과 다릅니다. 자동 덮어쓰기하지 않습니다.')
                else:
                    with backup.open('xb') as handle:
                        handle.write(original)
                for info in self.state['files'].values():
                    offset, end = info['offset'], info.get('baseline_end', 0)
                    if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in (offset, end)):
                        raise ValueError('이전 상태의 파일 위치가 올바르지 않습니다. 자동 초기화하지 않습니다.')
                    info.update(offset=0, baseline_end=max(offset, end), legacy_offset=offset,
                                sid=None, skipping=False)
                self.state.update(schema_version=3, settings={})
            if not isinstance(self.state.get('settings'), dict):
                raise ValueError('채팅 선택 설정 상태 구조 오류입니다. 자동 초기화하지 않습니다.')
        self.state.setdefault('reasons', {})
        self.state.setdefault('seen', [])
        self.seen = set(self.state['seen'])
        self.reason_reads = {}
        self.reason_budget = POLL_READ_BYTES
        self.diagnostic_failures = []

    def diagnostic(self, error, **details):
        value = {'time': stamp(), 'error': str(error)[:2000], **details}
        try:
            append_log(self.work / 'diagnostics.jsonl', value)
        except Exception as diagnostic_error:
            # 오류 기록 실패가 본래 오류를 바꾸거나 감시기를 종료시키지 않도록 쌍으로 전달합니다.
            failure = {**value, 'diagnostic_error': str(diagnostic_error)[:2000]}
            self.diagnostic_failures = (self.diagnostic_failures + [failure])[-5:]
            return failure
        return None

    def event(self, sid, after, reason='확인 불가', evidence='로컬 turn_context 관측', **extra):
        before = self.state['models'].get(sid)
        declared = self.state['declarations'].get(sid)
        if extra.get('kind') == 'settings':
            # 선택의 이전값과 실행 관측의 이전값은 다를 수 있습니다.
            before = extra.pop('settings_before')
            if before == after:
                return
            self.state['models'][sid] = after
            self.state['pending'].append({'id': uuid.uuid4().hex, 'time': stamp(), 'target': sid,
                'before': before, 'after': after, 'reason': reason[:12000], 'evidence': evidence, **extra})
            return
        if 'declared_before' in extra:
            # 요청은 관측 기준선을 변경하지 않습니다. 동시에 대기하는 정확한 전후만 연결합니다.
            pending = next((e for e in reversed(self.state['pending']) if e['target'] == sid
                            and e['after'] == after and e['before'] == extra['declared_before']
                            and e.get('kind') == 'observed'), None)
            if pending is not None:
                pending['runtime_evidence'] = pending['evidence']
                pending['declared_before'] = extra['declared_before']
                pending['declared_after'] = after
                pending['declared_reason'] = reason[:12000]
                pending['reason'] = reason[:12000]
                pending['evidence'] = '로컬 관측 전후와 일치하는 명시 배정 이유; 실제 원인 인증 아님'
                return
            if before == after or (declared and declared['after'] == after):
                return
            event = {'id': uuid.uuid4().hex, 'time': stamp(), 'target': sid,
                     'before': extra['declared_before'], 'after': after, 'reason': reason[:12000],
                     'evidence': evidence, 'kind': 'declared', **extra}
            self.state['declarations'][sid] = {**event, 'observed_before': before}
            self.state['pending'].append(event)
            return
        if before == after:
            return
        self.state['models'][sid] = after
        event = {'id': uuid.uuid4().hex, 'time': stamp(), 'target': sid, 'before': before,
                 'after': after, 'reason': reason[:12000], 'evidence': evidence, 'kind': 'observed', **extra}
        if declared:
            # 다음 실제 변경에서 요청을 소비합니다. 다른 변화 뒤 오래된 요청 이유를 재사용하지 않습니다.
            del self.state['declarations'][sid]
            if declared['after'] == after and declared['before'] == before and declared['observed_before'] == before:
                event['declaration_id'] = declared['id']
                event['declared_reason'] = declared['reason']
                append_log(self.work / 'observations.jsonl', event)
                return
        self.state['pending'].append(event)

    def duplicate_record(self, identity, baseline):
        """원본 시각이 있는 복제 기록만 제외하며 기준선 재생의 순서는 복원합니다."""
        fingerprint = hashlib.sha256(json.dumps(identity, sort_keys=True).encode('utf-8')).hexdigest()
        duplicate = fingerprint in self.seen
        if not duplicate:
            self.seen.add(fingerprint)
            self.state['seen'].append(fingerprint)
            if len(self.state['seen']) > 8192:
                self.seen.discard(self.state['seen'].pop(0))
        return duplicate and not baseline

    def settings_record(self, record, payload, info, baseline):
        """자기 채팅의 native 설정 필드만 관측하며 변경 주체와 실행 모델은 추정하지 않습니다."""
        values = payload.get('thread_settings')
        if not isinstance(values, dict):
            return
        mode = values.get('collaboration_mode')
        nested = mode.get('settings') if isinstance(mode, dict) else None
        # 설치 앱의 선택기와 같이 활성 협업 모드의 모델 설정을 우선합니다.
        selection_source = 'thread_settings'
        if isinstance(nested, dict) and nested.get('model') is not None:
            values = nested
            selection_source = 'thread_settings.collaboration_mode.settings'
        model, effort = values.get('model'), values.get('reasoning_effort')
        if not isinstance(model, str) or not model.strip() or len(model) > 256:
            return
        if effort is not None and (not isinstance(effort, str) or not effort.strip() or len(effort) > 64):
            return
        sid = info['sid']
        after = {'model': model, 'effort': effort if effort is not None else '확인 불가'}
        if record.get('timestamp') and self.duplicate_record(
                ['settings', sid, record['timestamp'], after], baseline):
            return
        before = self.state['settings'].get(sid, self.state['models'].get(sid))
        self.state['settings'][sid] = after
        if baseline:
            if before != after:
                self.state['models'][sid] = after
            return
        evidence = '로컬 thread_settings_applied의 채팅 선택 설정 관측; 실행 모델 인증·변경 주체·이유 확인 불가'
        self.event(sid, after, evidence=evidence, kind='settings', settings_before=before,
                   configuration_evidence=evidence, selection_source=selection_source,
                   role=info.get('role', '확인 불가'), parent=info.get('parent'),
                   agent_path=info.get('agent_path'), source_time=record.get('timestamp'))

    def record(self, record, info, baseline):
        kind, payload = record.get('type'), record.get('payload')
        if not isinstance(payload, dict):
            return
        if kind == 'session_meta':
            sid = payload.get('id')
            if not info.get('sid'):
                if not isinstance(sid, str):
                    return
                if info.get('expected_sid') and sid != info['expected_sid']:
                    return
                info['sid'] = sid
                source = payload.get('source', {})
                source = source if isinstance(source, dict) else {}
                sub = source.get('subagent', {})
                sub = sub if isinstance(sub, dict) else {}
                spawn = sub.get('thread_spawn', {})
                spawn = spawn if isinstance(spawn, dict) else {}
                info['child'] = bool(spawn or payload.get('parent_thread_id'))
                info['role'] = spawn.get('agent_role', payload.get('agent_role', 'main'))
                info['parent'] = spawn.get('parent_thread_id', payload.get('parent_thread_id'))
                info['agent_path'] = spawn.get('agent_path', payload.get('agent_path'))
                info['owner_active'] = True
                info['turns'] = []
            elif sid != info['sid']:
                # 자식의 첫 메타를 보존하고 그 뒤의 부모 복제 기록을 제외합니다.
                info['owner_active'] = False
            return
        sid = info.get('sid')
        if not sid:
            return
        if kind == 'response_item' and info.get('owner_active'):
            self.public_reason(payload, info)
        if kind == 'event_msg':
            event_kind = payload.get('type')
            if event_kind == 'thread_settings_applied':
                info['owner_active'] = payload.get('thread_id') == sid
                if info['owner_active']:
                    self.settings_record(record, payload, info, baseline)
            if event_kind == 'token_usage_record' and payload.get('thread_id') == sid:
                turn = payload.get('turn_id')
                if turn and turn not in info['turns']:
                    info['turns'] = (info['turns'] + [turn])[-128:]
            if event_kind == 'task_started' and info.get('owner_active'):
                turn = payload.get('turn_id')
                if turn and turn not in info['turns']:
                    info['turns'] = (info['turns'] + [turn])[-128:]
            return
        # 비공개 reasoning과 임의의 메시지 본문은 수집하지 않습니다.
        if kind != 'turn_context' or not isinstance(payload.get('model'), str):
            return
        if info.get('child') and payload.get('turn_id') not in info.get('turns', []):
            return
        after = {'model': payload['model'][:256], 'effort': str(payload.get('effort') or '확인 불가')[:64]}
        if record.get('timestamp') and self.duplicate_record(
                [sid, record['timestamp'], payload.get('turn_id'), after], baseline):
            return
        if baseline:
            self.state['models'][sid] = after
        else:
            self.event(sid, after, role=info.get('role', '확인 불가'), turn_id=payload.get('turn_id'),
                       parent=info.get('parent'), agent_path=info.get('agent_path'),
                       source_time=record.get('timestamp'))

    def public_reason(self, payload, info):
        kind = payload.get('type')
        if kind == 'message' and payload.get('role') == 'assistant' and payload.get('phase') == 'commentary':
            parts = [p.get('text', '') for p in payload.get('content', []) if isinstance(p, dict) and p.get('type') in ('output_text', 'text')]
            info['commentary'] = '\n'.join(parts)[:12000]
            return
        if kind == 'function_call':
            # 다른 도구 호출이 사이에 있으면 '바로 직전 공개 설명'으로 연결하지 않습니다.
            commentary = info.pop('commentary', '')
            if payload.get('name') not in ('spawn_agent', 'collaboration.spawn_agent') or not commentary:
                return
            try:
                arguments = json.loads(payload.get('arguments', '{}'))
            except (ValueError, TypeError):
                return
            call_id = payload.get('call_id')
            if not call_id or not isinstance(arguments.get('task_name'), str):
                return
            calls = info.setdefault('spawn_calls', {})
            calls[call_id] = {'commentary': commentary, 'requested_task': arguments['task_name'],
                              'model': arguments.get('model'), 'effort': arguments.get('reasoning_effort'),
                              'role': arguments.get('agent_type')}
            while len(calls) > 16:
                del calls[next(iter(calls))]
        elif kind == 'function_call_output':
            call = info.setdefault('spawn_calls', {}).pop(payload.get('call_id'), None)
            if not call:
                return
            try:
                result = json.loads(payload.get('output', '{}'))
            except (ValueError, TypeError):
                return
            task = result.get('task_name')
            if not isinstance(task, str) or not task.startswith('/') or task.rsplit('/', 1)[-1] != call['requested_task']:
                return
            key = info['sid'] + '|' + task
            self.state['reasons'][key] = {'text': call['commentary'], 'call_id': payload.get('call_id'),
                                        'model': call.get('model'), 'effort': call.get('effort'),
                                        'role': call.get('role')}
            while len(self.state['reasons']) > 128:
                del self.state['reasons'][next(iter(self.state['reasons']))]

    def lookup_parent_reason(self, event):
        """큰 부모 기록의 최근 공개 호출만 제한해서 읽으며 순차 감시 위치는 바꾸지 않습니다."""
        try:
            self._lookup_parent_reason(event)
        except (OSError, ValueError, TypeError) as error:
            self.diagnostic(error, parent=event.get('parent'), context='부모 이유 조회 실패; 관측 알림은 유지')

    def _lookup_parent_reason(self, event):
        parent = event.get('parent')
        if not parent or not event.get('agent_path') or event.get('before') is not None:
            return
        for filename, known in self.state['files'].items():
            if known.get('sid') != parent and known.get('expected_sid') != parent:
                continue
            path = Path(filename)
            stat = path.stat()
            signature = (stat.st_mtime_ns, stat.st_size)
            if self.reason_reads.get(filename) == signature or self.reason_budget <= 0:
                continue
            limit = min(4 * 1024 * 1024, self.reason_budget)
            self.reason_budget -= limit
            # 파일 이름만 믿지 않고 첫 메타의 실제 소유자를 대조합니다.
            with path.open('rb') as handle:
                first = handle.readline(MAX_RECORD + 1)
            if len(first) > MAX_RECORD:
                continue
            meta = json.loads(first.decode('utf-8'))
            if meta.get('type') != 'session_meta' or meta.get('payload', {}).get('id') != parent:
                continue
            rows, problems = read_jsonl_tail(path, max_bytes=limit, max_records=10000)
            info = {'sid': parent, 'owner_active': True}
            for row in rows:
                payload = row.get('payload', {})
                if not isinstance(payload, dict):
                    continue
                if row.get('type') == 'session_meta':
                    info['owner_active'] = payload.get('id') == parent
                elif row.get('type') == 'event_msg' and payload.get('type') == 'thread_settings_applied':
                    info['owner_active'] = payload.get('thread_id') == parent
                elif row.get('type') == 'response_item' and info['owner_active']:
                    self.public_reason(payload, info)
            self.reason_reads[filename] = signature
            # 잘린 앞부분은 정상적인 제한 조회이며 잘못된 중간 레코드는 진단에 남깁니다.
            for problem in problems:
                if not problem.startswith('앞부분 생략:'):
                    self.diagnostic(problem, path=filename, context='부모 공개 이유 제한 조회')

    def enrich_event(self, event):
        """이미 전송한 이력도 새 알림 없이 정확히 연결된 첫 배정 이유만 보강합니다."""
        value = dict(event)
        if value.get('before') is not None or value.get('reason') != '확인 불가':
            return value
        reason = self.state['reasons'].get(str(value.get('parent')) + '|' + str(value.get('agent_path')))
        if not reason:
            return value
        after = value.get('after') or {}
        if any(reason.get(key) and reason[key] != after.get(key) for key in ('model', 'effort')):
            return value
        if reason.get('role') and value.get('role') not in (None, 'main', '확인 불가', reason['role']):
            return value
        value.update(reason=reason['text'], reason_call_id=reason['call_id'],
                     evidence='배정 전 공개 설명: 부모 call_id/호출 결과/자식 경로 정확 연결; 서버 변경 원인 미확인')
        if value.get('kind') == 'settings':
            # 첫 자식 배정의 공개 이유를 연결해도 설정 관측 근거는 별도로 유지합니다.
            value['evidence'] = str(value.get('configuration_evidence', '')) + '; ' + value['evidence']
        return value

    def read_file(self, path, info):
        stat = path.stat()
        identity = [stat.st_dev, stat.st_ino]
        if info.get('identity') != identity or stat.st_size < max(info['offset'], info.get('legacy_offset', 0)):
            changed = info.get('identity') is not None
            info.update(offset=0, identity=identity, sid=None, skipping=False)
            info.pop('legacy_offset', None)
            if changed:
                info['baseline_end'] = 0
                self.diagnostic('파일 교체 또는 잘림: 현재 모델과 비교하여 재검사합니다.', path=str(path))
        total = 0
        with path.open('rb') as handle:
            handle.seek(info['offset'])
            while total < READ_BYTES and len(self.state['pending']) < MAX_PENDING:
                position = handle.tell()
                raw = handle.readline(MAX_RECORD + 1)
                total += len(raw)
                if not raw:
                    break
                if info.get('skipping'):
                    info['offset'] = handle.tell()
                    info['skipping'] = not raw.endswith(b'\n')
                    continue
                if len(raw) > MAX_RECORD:
                    info['offset'] = handle.tell()
                    info['skipping'] = not raw.endswith(b'\n')
                    self.diagnostic('레코드가 2 MiB 상한을 초과하여 LF까지 건너뜁니다.', path=str(path), offset=position)
                    continue
                if not raw.endswith(b'\n'):
                    # 완전한 LF 전까지 offset을 고정하여 분할 UTF-8을 다시 읽습니다.
                    break
                try:
                    record = json.loads(raw[:-1].decode('utf-8'))
                    if not isinstance(record, dict):
                        raise ValueError('JSON 객체가 아닙니다.')
                    self.record(record, info, position < info.get('baseline_end', 0))
                except (ValueError, TypeError, KeyError) as error:
                    self.diagnostic('레코드 오류: ' + str(error), path=str(path), offset=position, bytes=len(raw))
                info['offset'] = handle.tell()
        if info['offset'] >= info.get('legacy_offset', 0):
            info.pop('legacy_offset', None)
        return total

    def poll(self):
        self.reason_budget = POLL_READ_BYTES
        paths = []
        if not self.sessions.is_dir():
            self.diagnostic('세션 폴더에 접근할 수 없습니다.', path=str(self.sessions))
            return []
        # 디렉터리 순서는 최신 연/월/일부터 우선하며 탐색 수도 제한합니다.
        for directory, dirs, files in os.walk(self.sessions):
            dirs.sort(reverse=True)
            for name in sorted(files, reverse=True):
                if name.endswith('.jsonl'):
                    paths.append(Path(directory) / name)
                    if len(paths) >= MAX_FILES:
                        break
            if len(paths) >= MAX_FILES:
                break
        known = self.state['files']
        current = {str(p) for p in paths}
        for stale in list(known):
            if stale not in current:
                del known[stale]
        for path in paths:
            key = str(path)
            if key not in known:
                try:
                    baseline_end = path.stat().st_size if not self.state['initialized'] else 0
                except OSError as error:
                    self.diagnostic(error, path=key)
                    continue
                match = re.search(r'([0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12})\.jsonl$', path.name)
                known[key] = {'offset': 0, 'baseline_end': baseline_end, 'identity': None,
                              'expected_sid': match.group(1) if match else None}
        # 파일별 예산과 총 예산을 두고 다음 파일부터 이어가므로 큰 과거 파일이 독점하지 않습니다.
        cursor = self.state.get('cursor', 0) % max(1, len(paths))
        rotated = paths[cursor:] + paths[:cursor]
        total = 0
        visited = 0
        for path in rotated:
            key = str(path)
            if key not in known:
                continue
            try:
                total += self.read_file(path, known[key]) or 0
            except OSError as error:
                self.diagnostic(error, path=key)
            visited += 1
            if total >= POLL_READ_BYTES or len(self.state['pending']) >= MAX_PENDING:
                break
        self.state['cursor'] = (cursor + visited) % max(1, len(paths))
        self.state['initialized'] = True
        # 명시적 배정 요청은 별도 상태에 기록하고 실제 관측 기준선을 유지합니다.
        queue = self.work / 'announce'
        if queue.exists():
            for path in sorted(queue.glob('*.json'))[:max(0, min(32, MAX_PENDING - len(self.state['pending'])))]:
                try:
                    if path.stat().st_size > 20000:
                        raise ValueError('명시 알림 파일 상한 초과')
                    item = json.loads(path.read_text(encoding='utf-8'))
                    details = {key: item[key] for key in ('parent', 'agent_path', 'role', 'task_name', 'short_reason',
                               'reason_call_id', 'assignment_type', 'replaces_target') if key in item}
                    self.event(item['target'], item['after'], item['reason'], '사용자/부모의 명시적 배정 기록', declared_before=item['before'], **details)
                    atomic_json(self.state_path, self.state)
                    path.unlink()
                except (OSError, ValueError, KeyError) as error:
                    self.diagnostic(error, path=str(path))
        # 같은 대기 묶음에서 비교 가능한 시각만 정렬하고 미확인 항목의 위치는 고정합니다.
        dated = [(index, source_datetime(event.get('source_time')), event)
                 for index, event in enumerate(self.state['pending'])]
        dated = [(index, source_time, event) for index, source_time, event in dated if source_time is not None]
        for (index, _, _), (_, _, event) in zip(dated, sorted(dated, key=lambda item: item[1])):
            self.state['pending'][index] = event
        atomic_json(self.state_path, self.state)
        sent = []
        # 영속 pending 후 API를 호출합니다. API 성공과 상태 저장 사이 강제 종료는 재알림 가능성이 있습니다.
        for event in list(self.state['pending'])[:16]:
            try:
                self.lookup_parent_reason(event)
                event.update(self.enrich_event(event))
                result = self.sender(event)
                append_log(self.work / 'history.jsonl', {**event, 'delivery': result or '전송 함수 반환 성공; 화면 수신 미확인'})
                self.state['pending'].remove(event)
                atomic_json(self.state_path, self.state)
                sent.append(event)
            except Exception as error:
                self.diagnostic(error, event_id=event['id'])
                break
        # 삭제된 오래된 세션 상태는 제한된 수만 보존합니다.
        if len(self.state['models']) > MAX_FILES * 2:
            self.state['models'] = dict(list(self.state['models'].items())[-MAX_FILES * 2:])
        if len(self.state['declarations']) > MAX_FILES * 2:
            self.state['declarations'] = dict(list(self.state['declarations'].items())[-MAX_FILES * 2:])
        if len(self.state['settings']) > MAX_FILES * 2:
            self.state['settings'] = dict(list(self.state['settings'].items())[-MAX_FILES * 2:])
        atomic_json(self.state_path, self.state)
        return sent


def powershell(args, timeout=15):
    exe = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    parameters = {args[i].lstrip('-'): args[i + 1] for i in range(0, len(args), 2)}
    # 고정 명령은 UTF-8 로컬 스크립트를 읽고 구조화 인자만 전달합니다. 실행 정책은 변경하지 않습니다.
    command = "$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; [Console]::OutputEncoding=[Text.UTF8Encoding]::new($false); $OutputEncoding=[Console]::OutputEncoding; try {$p=@{}; (ConvertFrom-Json $env:CODEx_NOTIFY_ARGUMENTS).PSObject.Properties | ForEach-Object {$p[$_.Name]=$_.Value}; & ([scriptblock]::Create([IO.File]::ReadAllText($env:CODEx_NOTIFY_SCRIPT,[Text.Encoding]::UTF8))) @p} catch {[Console]::Error.WriteLine($_.Exception.ToString()); exit 1}"
    encoded = base64.b64encode(command.encode('utf-16-le')).decode('ascii')
    env = dict(os.environ, CODEx_NOTIFY_ARGUMENTS=json.dumps(parameters, ensure_ascii=False), CODEx_NOTIFY_SCRIPT=str(ROOT / 'src' / 'toast.ps1'))
    result = subprocess.run([str(exe), '-NoProfile', '-NonInteractive', '-STA', '-EncodedCommand', encoded], env=env,
                            capture_output=True, timeout=timeout, shell=False,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if result.returncode:
        # 디코딩 전 원본을 상한과 함께 보존하여 잘못된 바이트와 표시 잘림을 구분합니다.
        failure_path = ROOT / 'work' / 'transport-last-error.json'
        limit = 65536
        atomic_json(failure_path, {'time': stamp(), 'returncode': result.returncode,
                    'stderr_bytes': len(result.stderr), 'stdout_bytes': len(result.stdout),
                    'capture_limit_per_stream': limit, 'truncated': len(result.stderr) > limit or len(result.stdout) > limit,
                    'stderr_base64': base64.b64encode(result.stderr[:limit]).decode('ascii'),
                    'stdout_base64': base64.b64encode(result.stdout[:limit]).decode('ascii')})
        try:
            message = result.stderr.decode('utf-8', errors='strict')
        except UnicodeDecodeError:
            message = 'stderr에 엄격 UTF-8로 해석할 수 없는 바이트가 있습니다. 원본 base64를 확인하세요.'
        raise RuntimeError(f'Windows 알림 API 실패(exit={result.returncode}): {message[:4000]}\n표시상한 4000자; 원본 바이트/상한: {failure_path}')
    return result.stdout.decode('utf-8', errors='replace').strip()


class NativeToast:
    def __init__(self, work):
        self.work = Path(work)

    def __call__(self, event):
        import xml.etree.ElementTree as ET
        def units(value):
            return len(value.encode('utf-16-le')) // 2

        def limited(value, maximum):
            # Shell의 UTF-16 길이 제한 안에서 끝의 서로게이트 쌍을 보존합니다.
            value = ''.join(c for c in value if c >= ' ' or c in '\n\t\r')
            raw = value.encode('utf-16-le')
            if len(raw) // 2 <= maximum:
                return value
            raw = raw[:max(0, maximum - 1) * 2]
            if raw and 0xD800 <= int.from_bytes(raw[-2:], 'little') <= 0xDBFF:
                raw = raw[:-2]
            return raw.decode('utf-16-le') + '…'

        def label(value):
            return '미배정' if value is None else limited(f"{value['model']} / {value['effort']}", 64)
        toast = ET.Element('toast', {'duration': 'long'})
        visual = ET.SubElement(toast, 'visual')
        binding = ET.SubElement(visual, 'binding', {'template': 'ToastGeneric'})
        target = event['target'][:80]
        if event.get('agent_path'):
            target = f"{event['agent_path'][:80]} ({event.get('role', '확인 불가')})"
        context = f"{limited(target, 32)}\n{label(event['before'])} → {label(event['after'])}"
        evidence = '근거: ' + limited(event['evidence'], 28)
        reason_budget = 255 - units(context + '\n이유: \n' + evidence)
        reason = limited(event['reason'], reason_budget)
        for text in ['Codex 모델·추론 강도 변경', context, f"이유: {reason}\n{evidence}"]:
            # XML 1.0에서 허용하지 않는 제어 문자는 제거합니다.
            ET.SubElement(binding, 'text').text = ''.join(c for c in text if c >= ' ' or c in '\n\t\r')
        path = self.work / 'toast.xml'
        path.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(toast).write(path, encoding='utf-8', xml_declaration=True)
        return powershell(['-Action', 'Send', '-XmlPath', str(path), '-Tag', event['id'][:16]])


class InstanceLock:
    def __init__(self, work):
        self.path = Path(work) / 'watch.lock'
        self.handle = None

    def __enter__(self):
        import msvcrt
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open('a+b')
        try:
            if os.fstat(self.handle.fileno()).st_size == 0:
                self.handle.write(b'0')
                self.handle.flush()
            self.handle.seek(0)
            msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            self.handle.close()
            raise RuntimeError('이미 감시 프로그램이 실행 중입니다.')
        return self

    def __exit__(self, *args):
        self.handle.close()


def main():
    parser = argparse.ArgumentParser(description='현재 사용자 Codex 모델 변경 Windows 알림')
    parser.add_argument('--sessions', type=Path, default=Path.home() / '.codex/sessions')
    parser.add_argument('--work', type=Path, default=ROOT / 'work')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('watch')
    sub.add_parser('stop')
    sub.add_parser('status')
    sub.add_parser('test-toast')
    sub.add_parser('history')
    announce = sub.add_parser('announce')
    for flag in ['target', 'before-model', 'before-effort', 'after-model', 'after-effort', 'reason']:
        announce.add_argument('--' + flag, required=True)
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    if args.command == 'stop':
        (args.work / 'stop.request').write_text(stamp(), encoding='utf-8')
        print('중지 요청을 저장했습니다. 감시기는 다음 주기에 종료합니다.')
    elif args.command == 'status':
        path = args.work / 'heartbeat.json'
        print(path.read_text(encoding='utf-8') if path.exists() else '실행 기록 없음')
    elif args.command == 'history':
        path = args.work / 'history.jsonl'
        print(path.read_text(encoding='utf-8') if path.exists() else '로컬 전송 이력 없음')
    elif args.command == 'test-toast':
        print(NativeToast(args.work)({'id': uuid.uuid4().hex, 'target': '사용자 요청 시험', 'before': None,
              'after': {'model': '테스트', 'effort': '테스트'}, 'reason': 'Windows 알림 API 직접 시험', 'evidence': '시험 알림'}))
    elif args.command == 'announce':
        if any(not getattr(args, field).strip() for field in ['target', 'before_model', 'before_effort', 'after_model', 'after_effort', 'reason']):
            parser.error('빈 입력은 허용되지 않습니다.')
        if len(args.reason) > 12000 or len(args.target) > 256:
            parser.error('이유 또는 대상 길이가 상한을 초과했습니다.')
        before = {'model': args.before_model, 'effort': args.before_effort}
        after = {'model': args.after_model, 'effort': args.after_effort}
        if before == after:
            print('값 유지: 알림을 만들지 않았습니다.')
            return
        atomic_json(args.work / 'announce' / (uuid.uuid4().hex + '.json'), {'target': args.target, 'before': before, 'after': after, 'reason': args.reason})
        print('명시 알림을 대기열에 저장했습니다. 실행 중인 감시기가 전송합니다.')
    else:
        with InstanceLock(args.work):
            stop = args.work / 'stop.request'
            stop.unlink(missing_ok=True)
            watcher = Watcher(args.sessions, args.work, NativeToast(args.work))
            while not stop.exists():
                try:
                    watcher.poll()
                    atomic_json(args.work / 'heartbeat.json', {'pid': os.getpid(), 'time': stamp(), 'status': '감시 중', 'pending': len(watcher.state['pending'])})
                except Exception as error:
                    watcher.diagnostic(error)
                time.sleep(POLL_INTERVAL_SECONDS)
            atomic_json(args.work / 'heartbeat.json', {'pid': os.getpid(), 'time': stamp(), 'status': '중지됨'})


if __name__ == '__main__':
    main()
