"""번들 나눔고딕 Bold 글꼴을 앱과 투명 렌더에서 동일하게 사용합니다."""
from pathlib import Path
import sys
from PySide6.QtGui import QFont,QFontDatabase

_family = None

def register_fonts():
    """필수 파일이나 Qt 등록 실패를 숨기지 않고 시작 오류로 전달합니다."""
    global _family
    if _family is None:
        root=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parents[1]))/'assets'
        for style in ('Regular','Medium','SemiBold'):
            path=root/('SUIT-'+style+'.ttf')
            if not path.is_file():raise RuntimeError('필수 SUIT 글꼴 누락: '+str(path))
            identity=QFontDatabase.addApplicationFont(str(path))
            if identity<0 or 'SUIT' not in QFontDatabase.applicationFontFamilies(identity):
                raise RuntimeError('필수 SUIT 글꼴 등록 실패: '+str(path))
        path=root/'NanumGothic-Bold.ttf'
        identity=QFontDatabase.addApplicationFont(str(path))
        families=QFontDatabase.applicationFontFamilies(identity) if identity>=0 else []
        if not families:raise RuntimeError('필수 나눔고딕 글꼴 등록 실패: '+str(path))
        _family=families[0]
    return _family

def app_font(pixels=None,weight=QFont.Weight.Bold):
    font=QFont(register_fonts(),10,weight)
    if pixels is not None:font.setPixelSize(pixels)
    font.setStyleStrategy(font.styleStrategy() | QFont.StyleStrategy.NoSubpixelAntialias)
    return font
