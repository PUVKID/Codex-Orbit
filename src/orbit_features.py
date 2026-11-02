"""원문 이벤트와 표시를 분리하는 관측소 기록·관심 항목·개인정보 제외 진단입니다."""
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
import zipfile

from activity import safe_public_text


_EMOJI = re.compile('[\U0001f000-\U0001faff\u2600-\u27bf\u2300-\u23ff\u2b05-\u2b07\u2b1b\u2b1c\u2b50\u2b55\u00a9\u00ae\u203c\u2049\u2122\u2139\u2194-\u2199\u21a9\u21aa\u2934\u2935\u3030\u303d\u3297\u3299]')
_KEYCAP = re.compile('[0-9#*]\ufe0f?\u20e3')
_STATUS = {'running', 'completed', 'waiting', 'error', 'aborted'}
_LIFECYCLE_FIELDS = {'id', 'target', 'status', 'time', 'source_time', 'role', 'parent', 'parent_id'}
_IDENTITY = re.compile(r'[A-Za-z0-9_.-]{1,128}\Z')
_LIFECYCLE_LIMIT = 1048576
_EVENT_FIELDS = {'id', 'target', 'title', 'chat_title', 'chat_name', 'before', 'after', 'time',
                 'source_time', 'reason', 'kind', 'role', 'parent', 'parent_id', 'agent_path',
                 'task_summary', 'task_name', 'activity_action', 'activity_type', 'status',
                 'turn_id', 'evidence', 'requested', 'source', 'short_reason', 'task_source'}


def clean_chat_title(text):
    """장식 이모지 시퀀스만 표시에서 제거하고 일반 숫자·문자는 유지합니다."""
    if not isinstance(text, str):
        return ''
    if not (_KEYCAP.search(text) or _EMOJI.search(text)):
        return text
    text = _KEYCAP.sub(' ', text)
    text = _EMOJI.sub(' ', text)
    text = re.sub('[\u200d\ufe0e\ufe0f\U000e0020-\U000e007f]', '', text)
    return ' '.join(text.split())


def changed_fields(event):
    before = event.get('before') if isinstance(event.get('before'), dict) else {}
    after = event.get('after') if isinstance(event.get('after'), dict) else {}
    return {key for key in ('model', 'effort') if before.get(key) != after.get(key)}


def task_hint(event, language='ko'):
    """명시한 공개 작업 요약만 사용하며 모델 이름이나 변경 이유로 작업을 만들지 않습니다."""
    value = safe_public_text(event.get('task_summary') or event.get('task_name'), 240)
    return ' '.join(value.split()) if value else ('Task not observed' if language == 'en' else '확인된 작업 정보 없음')


def _instant(value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ValueError('재생 시각에는 시간대가 필요합니다.')
        return value.timestamp()
    if type(value) in (int, float):
        if not math.isfinite(value):
            raise ValueError('재생 시각은 유한해야 합니다.')
        return float(value)
    if isinstance(value, str):
        return _instant(datetime.fromisoformat(value.replace('Z', '+00:00')))
    raise ValueError('재생 시각은 시간대가 있는 시각 또는 Unix 초여야 합니다.')


def _atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix='.features-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(handle, 'w', encoding='utf-8', newline='\n') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def _lifecycle_row(value):
    """복원 가능한 식별·상태·시각만 검증하며 본문 필드는 받지 않습니다."""
    if not isinstance(value, dict) or set(value) - _LIFECYCLE_FIELDS:
        raise ValueError('생명주기 상태의 허용 필드가 아닙니다. 원본을 초기화하지 않습니다.')
    for key in ('id', 'target', 'parent', 'parent_id'):
        item = value.get(key)
        if item is None and key in ('parent', 'parent_id'):
            continue
        if not isinstance(item, str) or not _IDENTITY.fullmatch(item):
            raise ValueError('생명주기 ID는 1~128자의 영문·숫자·밑줄·점·하이픈이어야 합니다.')
    if not isinstance(value.get('status'), str) or value['status'] not in _STATUS:
        raise ValueError('명시된 생명주기 상태가 필요합니다.')
    for key in ('time', 'source_time'):
        item = value.get(key)
        if item is None and key == 'source_time':
            continue
        if not isinstance(item, str) or len(item) > 64:
            raise ValueError('생명주기 시각은 64자 이하의 시간대가 있는 문자열이어야 합니다.')
        _instant(item)
    role = value.get('role')
    if role is not None and (not isinstance(role, str) or not role or len(role) > 64
                             or any(ord(char) < 32 or 127 <= ord(char) <= 159
                                    or 0xD800 <= ord(char) <= 0xDFFF for char in role)):
        raise ValueError('생명주기 역할은 제어문자 없는 1~64자 문자열이어야 합니다.')
    return deepcopy(value)


class FeatureStore:
    """본문은 메모리에 두고 관심 ID·읽음·허용된 생명주기 상태만 개인 폴더에 저장합니다."""
    def __init__(self, directory):
        self.directory = Path(directory)
        self.path = self.directory / 'features-v1.json'
        self.lifecycle_path = self.directory / 'lifecycle-v1.json'
        self._state = {'schema_version': 1, 'pins': [], 'bookmarks': [], 'seen_ids': []}
        if self.path.exists():
            if self.path.stat().st_size > 262144:
                raise ValueError('관심 항목 상태 파일이 상한을 초과했습니다.')
            state = json.loads(self.path.read_text(encoding='utf-8'))
            if (not isinstance(state, dict) or state.get('schema_version') != 1
                    or any(not isinstance(state.get(key), list)
                           or any(not isinstance(value, str) or len(value) > 256 for value in state[key])
                           for key in ('pins', 'bookmarks', 'seen_ids'))):
                raise ValueError('관심 항목 상태 오류입니다. 원본을 초기화하지 않습니다.')
            self._state = state
        self._events = OrderedDict()
        self._lifecycles = OrderedDict()
        if self.lifecycle_path.exists():
            if self.lifecycle_path.stat().st_size > _LIFECYCLE_LIMIT:
                raise ValueError('생명주기 상태 파일이 상한을 초과했습니다.')
            state = json.loads(self.lifecycle_path.read_text(encoding='utf-8'))
            if (not isinstance(state, dict) or set(state) != {'schema_version', 'events'}
                    or type(state.get('schema_version')) is not int or state['schema_version'] != 1
                    or not isinstance(state.get('events'), list) or len(state['events']) > 512):
                raise ValueError('생명주기 상태 오류입니다. 원본을 초기화하지 않습니다.')
            for item in state['events']:
                row = _lifecycle_row(item)
                if row['id'] in self._lifecycles:
                    raise ValueError('생명주기 ID가 중복됩니다. 원본을 초기화하지 않습니다.')
                self._lifecycles[row['id']] = row

    @property
    def pins(self):
        return frozenset(self._state['pins'])

    @property
    def bookmarks(self):
        return frozenset(self._state['bookmarks'])

    def _preference(self, key, identity, enabled, limit):
        if not isinstance(identity, str) or not identity or len(identity) > 256:
            raise ValueError('관심 항목 ID는 1~256자 문자열이어야 합니다.')
        if type(enabled) is not bool:
            raise TypeError('관심 항목 설정은 bool이어야 합니다.')
        state = deepcopy(self._state)
        values = [value for value in state[key] if value != identity]
        if enabled:
            if len(values) >= limit:
                raise ValueError('관심 항목 저장 상한을 초과했습니다.')
            values.append(identity)
        state[key] = values
        _atomic(self.path, state)
        self._state = state

    def set_pin(self, target, enabled):
        self._preference('pins', target, enabled, 64)

    def set_bookmark(self, event_id, enabled):
        self._preference('bookmarks', event_id, enabled, 256)

    def ingest(self, event):
        if not isinstance(event, dict):
            raise TypeError('이벤트는 객체여야 합니다.')
        # payload/content/messages 같은 대화 원문은 새 저장소에 복제하지 않습니다.
        value = {key: deepcopy(item) for key, item in event.items() if key in _EVENT_FIELDS}
        if not isinstance(value.get('target'), str) or not value['target']:
            raise ValueError('이벤트 대상이 필요합니다.')
        identity = value.get('id')
        if not isinstance(identity, str) or not identity:
            identity = hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
            value['id'] = identity
        previous = self._events.get(identity)
        if previous is None:
            previous = ({'kind': 'lifecycle', **self._lifecycles[identity]}
                        if identity in self._lifecycles else {})
        merged = {**previous, **value}
        if merged.get('kind') == 'lifecycle':
            row = _lifecycle_row({key: deepcopy(item) for key, item in merged.items()
                                  if key in _LIFECYCLE_FIELDS})
            if self._lifecycles.get(identity) != row:
                lifecycles = self._lifecycles.copy()
                lifecycles[identity] = row
                while len(lifecycles) > 512:
                    lifecycles.popitem(last=False)
                state = {'schema_version': 1, 'events': list(lifecycles.values())}
                if len(json.dumps(state, ensure_ascii=False, indent=2).encode('utf-8')) > _LIFECYCLE_LIMIT:
                    raise ValueError('생명주기 상태 파일이 상한을 초과했습니다.')
                _atomic(self.lifecycle_path, state)
                self._lifecycles = lifecycles
        self._events[identity] = merged
        while len(self._events) > 512:
            self._events.popitem(last=False)

    def load_history(self, events):
        # 상세 정보가 보강된 같은 ID는 교체하고 이미 관측한 생명주기는 유지합니다.
        for event in events:
            self.ingest(event)

    @staticmethod
    def _time(event):
        for key in ('source_time', 'time'):
            try:
                return _instant(event.get(key))
            except (ValueError, TypeError, OverflowError):
                pass
        return None

    def snapshot(self, at=None, through=None):
        cutoff = None if at is None else _instant(at)
        combined = {identity: {'kind': 'lifecycle', **row} for identity, row in self._lifecycles.items()}
        for identity, event in self._events.items():
            combined[identity] = {**combined.get(identity, {}), **event}
        rows = [event for event in combined.values()
                if cutoff is None or (self._time(event) is not None and self._time(event) <= cutoff)]
        rows.sort(key=lambda event: self._time(event) if self._time(event) is not None else float('-inf'))
        if through is not None:
            # 감지 지연이나 같은 시각의 기록도 선택한 이벤트 다음 상태가 섞이지 않게 합니다.
            boundary = next((index for index, event in enumerate(rows) if event['id'] == through), None)
            if boundary is None:
                raise ValueError('재생할 기록 ID를 현재 저장 기록에서 찾을 수 없습니다.')
            rows = rows[:boundary + 1]
        selected, executed, agents = {}, {}, {}
        for event in rows:
            target = event['target']
            agent = agents.setdefault(target, {'target': target, 'status': 'unknown', 'pinned': target in self.pins})
            raw_title = event.get('chat_name') or event.get('chat_title') or event.get('title')
            if isinstance(raw_title, str) and raw_title:
                agent['title'] = agent['chat_name'] = clean_chat_title(raw_title)
            agent.setdefault('title', target)
            agent.setdefault('chat_name', agent['title'])
            for key in ('role', 'parent', 'parent_id', 'agent_path', 'time'):
                if key in event:
                    agent[key] = deepcopy(event[key])
            if event.get('task_summary') or event.get('task_name'):
                agent['task_hint'] = task_hint(event)
            if event.get('kind') == 'lifecycle' and event.get('status') in _STATUS:
                agent['status'] = event['status']
            if isinstance(event.get('after'), dict):
                if event.get('kind') == 'settings':
                    selected[target] = deepcopy(event['after'])
                elif event.get('kind') == 'observed':
                    executed[target] = deepcopy(event['after'])
            observed = executed.get(target) or selected.get(target) or {}
            agent.update(model=observed.get('model'), effort=observed.get('effort'))
        ordered = sorted(agents.values(), key=lambda agent: (not agent['pinned'], agent['target']))
        return deepcopy({'agents': ordered, 'events': rows[-512:], 'selected': selected, 'executed': executed})

    def mark_seen(self):
        state = deepcopy(self._state)
        state['seen_ids'] = [event['id'] for event in self.snapshot()['events']]
        _atomic(self.path, state)
        self._state = state

    def away_summary(self, since=None):
        rows = self.snapshot()['events']
        if since is None:
            rows = [event for event in rows if event['id'] not in self._state['seen_ids']]
        else:
            cutoff = _instant(since)
            rows = [event for event in rows if self._time(event) is not None and self._time(event) > cutoff]
        return {'count': len(rows), 'total': len(rows), 'events': deepcopy(rows),
                'completed': sum(event.get('status') == 'completed' for event in rows),
                'waiting': sum(event.get('status') == 'waiting' for event in rows),
                'errors': sum(event.get('status') == 'error' for event in rows)}

    def write_diagnostics(self, path, health, render):
        """대화·제목·대상·경로·에러 원문 없이 숫자와 bool 지표만 내보냅니다."""
        allowed_health = {'running', 'watcher_running', 'connected', 'retries', 'pending', 'events_count'}
        allowed_render = {'render_count', 'fps', 'target_fps', 'dispatch_count', 'presentation_count',
                          'owners', 'images', 'running', 'render_seconds', 'dropped_frames'}
        def metrics(source, allowed):
            return {key: value for key, value in source.items() if key in allowed
                    and (type(value) is bool or (type(value) in (int, float) and math.isfinite(value)))}
        data = {'schema_version': 1, 'health': metrics(health, allowed_health),
                'render': metrics(render, allowed_render)}
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        handle, name = tempfile.mkstemp(prefix='.diagnostics-', suffix='.zip', dir=destination.parent)
        os.close(handle)
        try:
            with zipfile.ZipFile(name, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('diagnostics.json', json.dumps(data, ensure_ascii=False, indent=2))
            os.replace(name, destination)
        finally:
            Path(name).unlink(missing_ok=True)
        return destination
