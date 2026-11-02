"""공개 협업 호출과 소유자가 확인된 native 활동을 연결합니다."""
from datetime import datetime, timezone
import hashlib
import json
import re

MAX_ACTIVITY_EVENTS = 128
MAX_ACTIVITY_SEEN = 8192
MAX_ACTIVITY_CALLS = 32
MAX_PUBLIC_CALLS = 128
MAX_DEFERRED_ACTIVITIES = 32
MAX_CONFIGURATION_SNAPSHOTS = 256


def explicit_lifecycle(record, info):
    """소유자가 확인된 명시 이벤트의 상태만 반환하며 메시지 본문은 복제하지 않습니다."""
    payload = record.get('payload')
    sid = _text(info.get('sid'))
    if (not sid or not info.get('owner_active') or not isinstance(payload, dict)
            or payload.get('thread_id') not in (None, sid)):
        return None
    event_type = payload.get('type')
    states = {'task_started': 'running', 'task_complete': 'completed',
              'turn_aborted': 'aborted', 'error': 'error', 'request_user_input': 'waiting'}
    status = states.get(event_type) if record.get('type') == 'event_msg' else None
    if (record.get('type') == 'response_item' and event_type == 'function_call'
            and payload.get('name') in ('request_user_input', 'functions.request_user_input',
                                        'request_user_input_async', 'functions.request_user_input_async')):
        event_type, status = 'request_user_input', 'waiting'
    if status is None:
        return None
    source_time = record.get('timestamp') if _instant(record.get('timestamp')) is not None else None
    turn_id = _text(payload.get('turn_id'), 256)
    identity = [sid, event_type, turn_id, source_time, _text(payload.get('call_id'), 128)]
    if not source_time and not turn_id and not identity[-1]:
        identity.append(info.get('offset', 0))
    digest = hashlib.sha256(json.dumps(identity, ensure_ascii=False).encode('utf-8')).hexdigest()
    return {'id': 'lifecycle-' + digest, 'kind': 'lifecycle', 'target': sid,
            'status': status, 'source_time': source_time, 'turn_id': turn_id,
            'role': _text(info.get('role'), 64), 'parent': _text(info.get('parent')),
            'agent_path': _text(info.get('agent_path')), 'evidence': '명시 ' + event_type + ' 기록'}


def safe_public_text(value, limit=12000):
    """보호문·비공개 표식·긴 인코딩 덩어리는 해석하거나 노출하지 않습니다."""
    if not isinstance(value, str) or not value.strip():
        return ''
    if (re.search(r'gAAAA[A-Za-z0-9_=-]{24,}', value)
            or re.search(r'[A-Za-z0-9+/_-]{160,}={0,2}', value)
            or re.search(r'<\s*(?:private|encrypted|reasoning)\b', value, re.I)):
        return ''
    if any(ord(character) < 32 and character not in '\n\r\t' for character in value):
        return ''
    return value.strip()[:limit]


def _text(value, limit=256):
    return (value if isinstance(value, str) and value.strip() and len(value) <= limit
            and safe_public_text(value, limit) == value else None)


def _instant(value):
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return result.astimezone(timezone.utc) if result.tzinfo is not None else None
    except (ValueError, OverflowError):
        return None


def _failed(value):
    return bool(value.get('error') or value.get('isError') is True
                or value.get('status') in ('error', 'failed', 'cancelled', 'canceled'))


def _trim(mapping, limit):
    while len(mapping) > limit:
        del mapping[next(iter(mapping))]


class ActivityTracker:
    def __init__(self, state):
        self.state = state
        self.data = state.setdefault('activity', {'schema_version': 1, 'seen': [],
            'events': {}, 'latest': {}, 'agents': {}, 'first_observations': {}})
        if (not isinstance(self.data, dict) or self.data.get('schema_version') != 1
                or not isinstance(self.data.get('seen'), list)
                or any(not isinstance(self.data.get(key), dict)
                       for key in ('events', 'latest', 'agents', 'first_observations'))):
            raise ValueError('활동 상태 구조 오류입니다. 원본을 자동 초기화하지 않습니다.')
        self.data.setdefault('calls', {})
        self.data.setdefault('deferred', [])
        self.data.setdefault('configurations', [])
        if not isinstance(self.data['calls'], dict) or not isinstance(self.data['deferred'], list):
            raise ValueError('활동 호출/지연 상태 구조 오류입니다. 원본을 자동 초기화하지 않습니다.')
        if not isinstance(self.data['configurations'], list):
            raise ValueError('활동 관측 시각 구조 오류입니다. 원본을 자동 초기화하지 않습니다.')
        self.seen = set(self.data['seen'])

    def note_meta(self, sid, info):
        self.data['agents'][sid] = {key: info.get(key) for key in ('parent', 'agent_path', 'role')}
        _trim(self.data['agents'], MAX_ACTIVITY_SEEN)

    def configuration(self, sid, value, info, source_time):
        """원본 시각이 있는 자기 관측만 전역 256개로 제한해 보존합니다."""
        if not info.get('owner_active'):
            return
        rows = self.data['configurations']
        if _instant(source_time) is None:
            # 시각 없는 새 값 뒤에서 과거 캐시를 현재 과거값인 것처럼 재사용하지 않습니다.
            rows[:] = [row for row in rows if row['target'] != sid]
            return
        row = {'target': sid, 'value': dict(value), 'source_time': source_time,
               'parent': info.get('parent'), 'agent_path': info.get('agent_path')}
        if row not in rows:
            rows.append(row)
            del rows[:-MAX_CONFIGURATION_SNAPSHOTS]

    def configuration_pair(self, target, parent, path, source_time):
        instant = _instant(source_time)
        rows = [row for row in self.data['configurations']
                if row.get('target') == target and row.get('parent') == parent
                and row.get('agent_path') == path and _instant(row.get('source_time')) is not None]
        earlier = [row for row in rows if _instant(row['source_time']) < instant]
        later = [row for row in rows if _instant(row['source_time']) >= instant]
        before = max(earlier, key=lambda row: _instant(row['source_time'])) if earlier else None
        after = min(later, key=lambda row: _instant(row['source_time'])) if later else None
        return before, after

    def response(self, payload, info):
        kind = payload.get('type')
        if kind == 'message' and payload.get('role') == 'assistant' and payload.get('phase') == 'commentary':
            parts = [part.get('text', '') for part in payload.get('content', [])
                     if isinstance(part, dict) and part.get('type') in ('output_text', 'text')
                     and isinstance(part.get('text'), str)]
            info['activity_commentary'] = safe_public_text('\n'.join(parts))
            return
        calls = self.data['calls']
        parent = str(info.get('sid'))
        if kind == 'function_call_output':
            call_id = payload.get('call_id')
            key = parent + '|' + str(call_id)
            if key in calls:
                try:
                    result = json.loads(payload.get('output', '{}'))
                except (ValueError, TypeError):
                    return
                if isinstance(result, dict) and _failed(result):
                    del calls[key]
            return
        if kind != 'function_call':
            return
        commentary = info.pop('activity_commentary', '')
        name, namespace = payload.get('name'), payload.get('namespace')
        if isinstance(name, str) and name.startswith('collaboration.'):
            name = name[len('collaboration.'):]
            namespace = namespace or 'collaboration'
        call_id = _text(payload.get('call_id'), 128)
        if namespace != 'collaboration' or name not in ('spawn_agent', 'followup_task') or not call_id:
            return
        raw = payload.get('arguments')
        if not isinstance(raw, str) or len(raw) > 20000:
            return
        try:
            arguments = json.loads(raw)
        except (ValueError, TypeError):
            return
        if not isinstance(arguments, dict):
            return
        target = _text(arguments.get('target'))
        task = _text(arguments.get('task_name'))
        if name == 'followup_task' and not target:
            return
        if name == 'spawn_agent' and (not task or '/' in task or '\\' in task):
            return
        message = safe_public_text(arguments.get('message'))
        reason = safe_public_text(commentary)
        summary = reason or message
        calls[parent + '|' + call_id] = {'operation': name, 'target': target, 'task_name': task,
            'reason': reason, 'task_summary': re.sub(r'\s+', ' ', summary)[:600],
            'task_source': ('정확한 호출 직전 공개 commentary' if reason else
                            '읽을 수 있는 공개 호출 message' if message else '확인 불가'),
            'requested': {'model': _text(arguments.get('model')),
                          'effort': _text(arguments.get('reasoning_effort'), 64),
                          'role': _text(arguments.get('agent_type'), 64)}}
        _trim(calls, MAX_PUBLIC_CALLS)

    def defer(self, record, info):
        """원본 본문 없이 검증에 필요한 native 필드만 전역 32개까지 기다립니다."""
        payload, item = record['payload'], record['payload']['item']
        minimal = {'type': 'event_msg', 'timestamp': record.get('timestamp'), 'payload': {
            'type': 'item_completed', 'thread_id': info['sid'], 'item': {
                key: _text(item.get(key)) for key in
                ('type', 'id', 'kind', 'agent_thread_id', 'agent_path', 'model', 'reasoning_effort')}}}
        queue = self.data['deferred']
        if any(value['record'] == minimal for value in queue):
            return True
        if len(queue) >= MAX_DEFERRED_ACTIVITIES:
            return False
        queue.append({'record': minimal, 'owner': {'sid': info['sid'], 'owner_active': True}})
        return True

    def retry_deferred(self, finished_parents=()):
        for value in list(self.data['deferred']):
            result = self.complete(value['record'], value['owner'], False)
            if result != 'unmatched' or value['owner']['sid'] in finished_parents:
                self.data['deferred'].remove(value)

    def complete(self, record, info, baseline):
        payload = record['payload']
        if not info.get('owner_active') or payload.get('thread_id') != info.get('sid'):
            return
        item = payload.get('item')
        if not isinstance(item, dict) or item.get('type') != 'SubAgentActivity':
            return
        call_id = _text(item.get('id'), 128)
        target, path = _text(item.get('agent_thread_id')), _text(item.get('agent_path'))
        parent = info['sid']
        if (not call_id or not target or not re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', target)
                or target == parent or not path or not path.startswith('/')
                or _failed(item) or _failed(payload) or _instant(record.get('timestamp')) is None):
            return
        if item.get('kind') not in ('started', 'interacted'):
            return
        call_key = parent + '|' + call_id
        call = self.data['calls'].get(call_key)
        if not call:
            return 'unmatched'
        assigned = call['operation'] == 'spawn_agent'
        if item.get('kind') != ('started' if assigned else 'interacted'):
            return
        if assigned:
            if path.rsplit('/', 1)[-1] != call['task_name']:
                return
        elif call['target'] not in (target, path):
            return
        del self.data['calls'][call_key]
        identity = [parent, target, 'assigned' if assigned else 'resumed', call_id]
        event_id = hashlib.sha256(json.dumps(identity).encode('utf-8')).hexdigest()[:32]
        if event_id in self.seen:
            return
        self.seen.add(event_id)
        self.data['seen'].append(event_id)
        if len(self.data['seen']) > MAX_ACTIVITY_SEEN:
            self.seen.discard(self.data['seen'].pop(0))
        if baseline:
            return
        previous = self.data['latest'].get(target)
        if previous in self.data['events']:
            self.data['events'][previous]['waiting'] = False
        previous_configuration, next_configuration = self.configuration_pair(target, parent, path, record['timestamp'])
        unknown = {'model': None, 'effort': None}
        known_before = dict(previous_configuration['value']) if previous_configuration else dict(unknown)
        known_after = (dict(next_configuration['value']) if next_configuration else
                       None if assigned else dict(known_before))
        metadata = self.data['agents'].get(target, {})
        metadata = metadata if metadata.get('parent') == parent and metadata.get('agent_path') == path else {}
        requested = dict(call['requested'])
        native_request = {'model': _text(item.get('model')),
                          'effort': _text(item.get('reasoning_effort'), 64)}
        evidence = ('소유 parent/thread_id와 collaboration.' + call['operation']
                    + ' call_id 및 native SubAgentActivity.' + item['kind'] + ' target의 정확 연결; '
                    + ('새 작업자 배정 완료 기록' if assigned else '기존 작업자에게 재개 요청 전달 기록; 새 turn 시작 보장 아님'))
        event = {'id': event_id, 'time': datetime.now(timezone.utc).isoformat(),
            'source_time': record['timestamp'], 'kind': 'activity',
            'activity_type': 'assigned' if assigned else 'resumed', 'parent': parent,
            'target': target, 'agent_path': path, 'task_name': path.rsplit('/', 1)[-1],
            'role': metadata.get('role') or requested.get('role') or '확인 불가',
            'call_id': call_id, 'reason_call_id': call_id,
            'before': None if assigned else known_before, 'after': known_after,
            'requested': requested, 'native_request': native_request,
            'reason': call['reason'] or '확인 불가', 'reason_raw': call['reason'] or '확인 불가',
            'reason_source': '정확한 호출 직전 공개 commentary' if call['reason'] else '확인 불가',
            'task_summary': call['task_summary'] or '확인 불가', 'task_source': call['task_source'],
            'assignment_evidence': evidence, 'evidence': evidence,
            'model_evidence': '활동 원본시각 전 마지막/후 첫 소유 채팅 설정·실행 관측만 연결; 시각 근거 없는 필드는 확인 불가'}
        first = self.data['first_observations'].get(target)
        if assigned and first and self._matches(first, event):
            event.update(after=first['after'], role=first.get('role') or event['role'],
                         first_observation_id=first['id'], observation_source_time=first['source_time'])
            pending = self.state['pending']
            original = next((value for value in pending if value['id'] == first['id']), None)
            if original is not None:
                pending.remove(original)
            else:
                event['first_observation_already_delivered'] = True
        self.data['events'][event_id] = {'event': event, 'waiting': not bool(
            next_configuration or (first and assigned and self._matches(first, event)))}
        self.data['latest'][target] = event_id
        _trim(self.data['events'], MAX_ACTIVITY_EVENTS)
        _trim(self.data['latest'], MAX_ACTIVITY_SEEN)
        self.state['pending'].append(event)

    @staticmethod
    def _matches(observation, event):
        observed_at, assigned_at = _instant(observation.get('source_time')), _instant(event.get('source_time'))
        return (observation.get('parent') == event.get('parent')
                and observation.get('agent_path') == event.get('agent_path')
                and observed_at is not None and assigned_at is not None and observed_at >= assigned_at)

    def observe(self, sid, after, before, **extra):
        """그 활동의 첫 관측만 보강하며 이후 모델 변경은 별도 감지를 유지합니다."""
        latest = self.data['events'].get(self.data['latest'].get(sid))
        if not latest or not latest['waiting']:
            return False
        event = latest['event']
        if not self._matches(extra, event):
            return False
        event.update(after=dict(after), observation_source_time=extra['source_time'],
                     model_evidence='해당 활동 뒤 첫 로컬 설정/실행 관측; 서버 실행 신원 인증 아님')
        if extra.get('role') not in (None, 'main', '확인 불가'):
            event['role'] = extra['role']
        latest['waiting'] = False
        return event['activity_type'] == 'assigned' and before is None

    def note_first_observation(self, event):
        if event.get('before') is None and event.get('parent') and event.get('agent_path'):
            self.data['first_observations'][event['target']] = {key: event.get(key) for key in
                ('id', 'after', 'source_time', 'parent', 'agent_path', 'role')}
            _trim(self.data['first_observations'], MAX_ACTIVITY_SEEN)

    def enrich(self, event):
        stored = self.data['events'].get(event.get('id')) if event.get('kind') == 'activity' else None
        return dict(stored['event']) if stored else dict(event)
