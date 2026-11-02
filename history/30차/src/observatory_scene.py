"""관측소 스냅샷 검증과 렌더·클릭이 공유하는 실제 3D 배치입니다."""
import math
import re

MAX_AGENTS = 24
CAMERA = 700.0
EXTENT = 69.0


def _number(value, low, high, name):
    if type(value) not in (int, float):
        raise ValueError(name + ' 값은 유한한 숫자여야 합니다.')
    try:
        valid = math.isfinite(value) and low <= value <= high
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(name + ' 값이 허용 범위를 벗어났습니다.')
    return float(value)


def normalize_scene(scene):
    """개인 기록을 추가 수집하지 않고 전달받은 최신 값만 독립 복사합니다."""
    if not isinstance(scene, dict):
        raise TypeError('관측소 장면은 dict여야 합니다.')
    result = {}
    for key in ('model', 'effort'):
        value = scene.get(key)
        if value is not None and (not isinstance(value, str) or len(value) > 128):
            raise ValueError(key + ' 값은 짧은 원문 문자열 또는 None이어야 합니다.')
        result[key] = value
    quality = scene.get('quality', 'balanced')
    if quality not in ('eco', 'balanced', 'high'):
        raise ValueError('품질은 eco, balanced, high 중 하나여야 합니다.')
    result['quality'] = quality
    for key in ('paused', 'reduced_motion'):
        value = scene.get(key, False)
        if type(value) is not bool:
            raise ValueError(key + ' 값은 bool이어야 합니다.')
        result[key] = value
    usage = scene.get('usage_fraction')
    result['usage_fraction'] = None if usage is None else _number(usage, 0, 1, '사용 한도')
    pointer = scene.get('pointer', (0, 0))
    if not isinstance(pointer, (tuple, list)) or len(pointer) != 2:
        raise ValueError('포인터는 두 정규 좌표여야 합니다.')
    result['pointer'] = [_number(v, -1, 1, '포인터') for v in pointer]
    result['transition'] = _number(scene.get('transition', 1), 0, 1, '전환')
    result['press'] = _number(scene.get('press', 0), 0, 1, '눌림')
    agents = scene.get('agents', [])
    if not isinstance(agents, (list, tuple)) or len(agents) > MAX_AGENTS:
        raise ValueError('GPU 작업자 위성은 최대 24개여야 합니다.')
    result['agents'] = []
    targets = set()
    for agent in agents:
        if not isinstance(agent, dict):
            raise ValueError('작업자 항목은 dict여야 합니다.')
        target = agent.get('target')
        status = agent.get('status', 'unknown')
        pinned = agent.get('pinned', False)
        if not isinstance(target, str) or not target or len(target) > 200 or target in targets:
            raise ValueError('작업자 target은 중복 없는 원문 ID여야 합니다.')
        if not isinstance(status, str) or len(status) > 64 or type(pinned) is not bool:
            raise ValueError('작업자 상태와 고정 여부를 확인할 수 없습니다.')
        targets.add(target)
        result['agents'].append({'target': target, 'status': status, 'pinned': pinned})
    return result


def model_family(model):
    match = re.fullmatch(r'gpt-\d+(?:\.\d+)?-(sol|astra|terra|luna)', model or '')
    return match.group(1) if match else 'unknown'


def particle_count(effort):
    return {'none': 0, 'minimal': 3, 'low': 6, 'medium': 12,
            'high': 20, 'xhigh': 32, 'ultra': 48}.get(effort, 0)


def scene_fps(scene):
    return {'eco': 20, 'balanced': 30, 'high': 60}[scene.get('quality', 'balanced')]


def scene_time(scene, elapsed):
    value = _number(elapsed, -1e12, 1e12, '모션 시각')
    return 0.0 if scene.get('reduced_motion') else value


def world_matrix(scene):
    """렌더와 클릭 위치에 동일한 미세 시점 이동·눌림 배율을 적용합니다."""
    x, y = scene.get('pointer', (0, 0))
    ax, ay = y * .09, x * .09
    cx, sx, cy, sy = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay)
    scale = 1 - .08 * scene.get('press', 0)
    return [[scale * cy, scale * sy * sx, scale * sy * cx, 0],
            [0, scale * cx, -scale * sx, 0],
            [-scale * sy, scale * cy * sx, scale * cy * cx, 0],
            [0, 0, 0, 1]]


def transform_point(scene, point):
    matrix = world_matrix(scene)
    return tuple(sum(matrix[i][j] * point[j] for j in range(3)) for i in range(3))


def project_point(point):
    """실제 카메라와 중앙 정사각 crop에 대응하는 0..1 좌표입니다."""
    x, y, z = point
    perspective = CAMERA / (CAMERA - z)
    return .5 + x * perspective / (2 * EXTENT), .5 - y * perspective / (2 * EXTENT), .5 + z / 140


def agent_world_positions(scene, elapsed):
    scene = normalize_scene(scene)
    elapsed = scene_time(scene, elapsed)
    result = []
    count = len(scene['agents'])
    for index, agent in enumerate(scene['agents']):
        phase = math.tau * index / max(1, count)
        if not agent['pinned']:
            phase += elapsed * .22
        radius = 52 if agent['pinned'] else 57
        status = agent['status']
        bob = 2 * math.sin(elapsed * (4 if status in ('retrying', 'retry') else 1.3) + index)
        shake = 1.2 * math.sin(elapsed * 10) if status == 'error' else 0
        x = radius * math.cos(phase) + shake
        y = radius * .66 * math.sin(phase) + bob
        # 용기 윗부분을 가리는 중앙 하단 구역에서는 궤도를 부드럽게 들어 올립니다.
        weight = min(1., max(0., (26 - abs(x)) / 10))
        weight = weight * weight * (3 - 2 * weight)
        y += max(0., -22 - y) * weight
        result.append({**agent, 'position': (x, y,
                                           21 * math.sin(phase + .4))})
    return result


def observatory_positions(scene, elapsed):
    """같은 표시 프레임의 scene_elapsed를 받아 위성의 정확한 클릭 중심을 돌려줍니다."""
    scene = normalize_scene(scene)
    result = []
    for agent in agent_world_positions(scene, elapsed):
        x, y, depth = project_point(transform_point(scene, agent['position']))
        result.append({'target': agent['target'], 'status': agent['status'], 'pinned': agent['pinned'],
                       'x': x, 'y': y, 'depth': depth})
    return result
