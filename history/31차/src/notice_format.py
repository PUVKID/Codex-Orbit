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


def notice_reason(event, limit=210):
    """공개 이유와 실제 맡긴 일만 짧게 연결하며 없는 선택 동기를 만들지 않습니다."""
    reason = public_text(event.get('reason'), '', 1000000)
    # 감지기의 명시적인 미기록 표식만 처리하며 정상 문장 속 같은 단어는 보존합니다.
    if reason in ('확인 불가', '확인되지 않음'):
        reason = ''
    text = public_text(short_reason({**event, 'reason': reason, 'short_reason': ''}, limit), '', limit) if reason else t('이유가 기록되지 않았습니다.')
    if get_language() == 'ko':
        # 뜻이 분명한 표시 용어만 풀어 쓰며 전체 원문은 툴팁과 상세에 남깁니다.
        for original, plain in ((r'\bUI\b', '화면'), (r'\bfixture\b', '검사용 예시'), (r'\bassert\b', '검사 조건')):
            text = re.sub(original, plain, text)
    if event.get('kind') == 'activity':
        task = public_text(event.get('task_summary'), '', 1000000)
        if task and task not in text:
            text += '\n' + t('맡긴 일: ') + task
    return text if len(text) <= limit else text[:limit-1].rstrip() + '…'


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
