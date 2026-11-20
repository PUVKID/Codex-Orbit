"""관측 원값과 분리한 백분율 표시만 공통으로 처리합니다."""
import math
from decimal import Decimal, ROUND_HALF_UP
from i18n import translate as t


def percentage_text(value):
    """저장값은 바꾸지 않고 백분율 요약만 소수 첫째 자리로 반올림합니다."""
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 100:
        return '—'
    rounded = Decimal(str(value)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    text = format(rounded, '.1f') + '%'
    return t('약 {value}', value=text) if (rounded == 100 and value < 100) or (rounded == 0 and value > 0) else text


def percentage_tooltip(value):
    """반올림 요약과 원래 백분율·비율을 구분해 안내합니다."""
    if type(value) not in (int, float) or not math.isfinite(value):
        return t('미확인')
    return t('백분율은 소수 첫째 자리 반올림 · 원값: ') + repr(value) + '% · ' + t('원비율: ') + repr(value / 100)
