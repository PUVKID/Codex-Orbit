"""Qt 화면과 Windows 알림이 공유하는 공개 정보 표시 함수입니다."""
import re
from i18n import translate as t, get_language


def notice_model_label(value):
    """확인된 모델 계열의 이모지만 붙이고 정확한 모델 ID를 보존합니다."""
    raw = str(value or t('확인 불가'))
    family = re.fullmatch(r'gpt-\d+(?:\.\d+)?-(sol|astra|terra|luna)', raw)
    emoji = {'sol': '☀️', 'astra': '✨', 'terra': '🌍', 'luna': '🌙'}.get(family.group(1) if family else '', '🤖')
    return emoji + ' ' + raw


def notice_previous_model(value):
    """전체 이전 기록이 없으면 모델 계열을 추정하지 않습니다."""
    if value is None or not isinstance(value, dict) or not value.get('model'):
        return previous_field(value, 'model')
    return notice_model_label(value['model'])


def notice_reason(event, limit=210, *, max_sentences=2):
    """공개 목적 문장만 한두 개 골라 보여 주며 원문과 선택 동기는 새로 만들지 않습니다."""
    raw = public_text(event.get('reason'), '', 1000000)
    missing = raw in ('', '확인 불가', '확인되지 않음')
    text = '' if missing else raw
    marked = re.search(r'(?:핵심 이유|모델(?:·추론 강도)? 선택 이유|선택 이유|이유)\s*[:：]\s*', text)
    if marked:
        text = text[marked.end():]
    # 실행 식별자와 운영 메타 행은 선택 이유로 해석하지 않습니다.
    text = re.sub(r'([\U0001f300-\U0001faff])\1{3,}', r'\1', text)
    text = re.sub(r'[\x00-\x08\x0b-\x1f]', ' ', text)
    sentences = re.split(r'(?<=[.!?。])\s+|\n+', text)
    # 실패나 명시 목적을 먼저 읽되 앞뒤 원문 자체는 별도로 보존합니다.
    observed_problem = [sentence for sentence in sentences if re.search(r'실패했|실패하였|오류가|겹쳐|잘렸', sentence)]
    if observed_problem:
        sentences = [sentence for sentence in sentences if sentence in observed_problem or not re.search(r'(?:\d+개|\d+건).*(?:직접 실행|회귀|검증|확인)', sentence)]
    important = [sentence for sentence in sentences if re.search(r'이유|때문|위해|겹쳐|실패했|실패하였|오류가', sentence)]
    sentences = important + [sentence for sentence in sentences if sentence not in important]
    selected = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or re.search(r'(?:^|[ /·,])(?:role|task|session|target|repair_used|input_fix_used|argv|cwd)\s*[:=]', sentence, re.I):
            continue
        if re.fullmatch(r'(?:gpt-[\w.-]+|(?:main|build|verifier|deep|escalate)\s*[/·]\s*\w+)[.!]?', sentence):
            continue
        if sentence in selected:
            continue
        for original, plain in ((r'\bUI\b', '화면'), (r'\bfixture\b', '검사용 예시'), (r'\bassert\b', '검사 조건'), (r'회귀(?:\s*검사)?를', '기존 기능 확인을'), (r'회귀(?:\s*검사)?', '기존 기능 확인'), (r'파서', '기록 읽기'), (r'스키마', '자료 형식'), (r'\bIPC\b', '앱 내부 통신'), (r'\bverifier\b', '확인 작업')) if get_language() == 'ko' else ():
            sentence = re.sub(original, plain, sentence)
        if len(' '.join(selected + [sentence])) <= limit:
            selected.append(sentence)
        if len(selected) == max_sentences:
            break
    result = ' '.join(selected)
    if not result:
        result = (t('이유가 기록되지 않았습니다.') if missing else t('설명이 길어 원문에서 전체 내용을 확인해 주세요.') if any(len(x.strip()) > limit for x in sentences) else t('공개된 선택 이유를 확인할 수 없습니다.'))
    if event.get('kind') == 'activity':
        task = public_text(event.get('task_summary'), '', 1000000)
        if task and task not in result:
            short_task = next((x.strip() for x in re.split(r'(?<=[.!?。])\s+|\n+', task) if x.strip() and len(x.strip()) <= 100), '')
            if short_task:
                result += '\n' + t('맡긴 일: ') + short_task
    return result


def notice_reason_original(event):
    """공개로 판정된 전체 문장만 툴팁에 보존하고 보호된 본문은 제외합니다."""
    parts = [public_reason_original(event)]
    task = public_text(event.get('task_summary'), '', 1000000)
    if event.get('kind') == 'activity' and task:
        parts.append(t('맡긴 일: ') + task)
    return '\n'.join(parts)


def friendly_effort(value):
    labels = {'none': t('없음'), 'minimal': t('최소'), 'low': t('낮음'), 'medium': t('보통'),
              'high': t('높음'), 'xhigh': t('매우 높음'), 'ultra': t('최고')}
    # 기존 풀이와 정확한 원문 값 뒤에 강도별 이모지만 덧붙입니다.
    icons = {'none': '⚪', 'minimal': '💧', 'low': '🌱', 'medium': '⚖️',
             'high': '🔥', 'xhigh': '🚀', 'ultra': '⚡'}
    return (t(labels.get(value, str(value or '미확인'))) + (f' ({value})' if value in labels else '')
            + ' ' + icons.get(value, '❔'))


def previous_field(value, key):
    """이전 기록 전체 부재와 개별 필드 미기록을 구분하고 관측값만 표시합니다."""
    if value is None:
        return t('이전 기록 없음') + (' ❔' if key == 'effort' else '')
    raw = value.get(key) if isinstance(value, dict) else None
    if not isinstance(raw, str) or not raw:
        return t('확인 불가') + (' ❔' if key == 'effort' else '')
    return friendly_effort(raw) if key == 'effort' else raw


def short_reason(event, limit=180):
    """명시 이유와 배정·선택 목적 문장을 우선 발췌하며 추정 요약은 만들지 않습니다."""
    text = str(event.get('short_reason') or event.get('reason') or '확인 불가').strip()
    marked = re.search(r'(?:핵심 이유|선택 이유|이유)\s*[:：]\s*([^\n]+)', text)
    if marked:
        text = marked.group(1)
    else:
        sentences = [sentence for sentence in re.split(r'(?<=[.!?。])\s+|\n', text) if sentence.strip()]
        purpose = None if event.get('short_reason') else next((sentence for sentence in sentences if re.search(
            r'위한\s+(?:배정|선택|변경|교체)|(?:배정|선택|변경|교체)(?:의|한)?\s*(?:이유|목적)'
            r'|(?:때문|확인돼|확인되어).*(?:배정|선택|변경|교체)', sentence)), None)
        if not purpose and not event.get('short_reason'):
            for index, sentence in enumerate(sentences[:-1]):
                if re.search(r'(?:배정합니다|배정하겠습니다|맡기겠습니다)[.!]?$', sentence.replace('**', '').strip()):
                    candidate = sentences[index + 1].strip()
                    if re.search(r'(?:대조|검사|확인|검토|검증|구현|수정)', candidate):
                        purpose = candidate
                        break
        text = purpose or (sentences[0] if sentences else '확인 불가')
        if not purpose and len(sentences) > 1 and len(text) < 70 and re.search(r'(?:맡기겠습니다|배정하겠습니다)[.!]?$', text):
            text = sentences[1]
    text = text.replace('**', '')
    return text if len(text) <= limit else text[:limit - 1] + '…'


def public_text(value, fallback='공개된 설명이 기록되지 않았습니다.', limit=600):
    """공개 문장만 표시하며 보호된 도구 페이로드를 해석하거나 노출하지 않습니다."""
    if not isinstance(value, str) or not value.strip():
        return t(fallback)
    text = value.strip()
    if (re.search(r'gAAAA[A-Za-z0-9_=-]{40,}|[A-Za-z0-9_+/=-]{160,}', text)
            or re.search(r'encrypted_content\s*[:=]|BEGIN ENCRYPTED|<analysis>|<private>', text, re.I)):
        return t(fallback)
    text = text.replace('**', '').replace('`', '')
    return text if len(text) <= limit else text[:limit-1].rstrip()+'…'


def public_reason_original(event):
    value = event.get('reason')
    return str(value) if public_text(value, '', 1) else t('공개된 설명이 기록되지 않았습니다.')


def notice_reason_caption(event):
    """공개 선택 이유와 단순 작업 설명을 같은 의미로 표시하지 않습니다."""
    raw = public_text(event.get('reason'), '', 1000000)
    explained = re.search(r'이유|때문|위해|겹쳐|확인해|발견해', raw)
    return t('이유: ') if explained or raw in ('', '확인 불가', '확인되지 않음') else t('작업 설명: ')
