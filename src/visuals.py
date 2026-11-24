"""제작된 실제3D 금속 프레임과 고정된 실제 잔량·상태를 합성합니다."""
import math

from i18n import translate as t, get_language
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QPainter, QLinearGradient, QTextLayout, QTextOption
from atom_frames import get_atom_frames
from elements import daily_element
from typography import app_font
from percentage_display import percentage_text
from theme import colors


def rotate_point(point, angles):
    """X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다."""
    x, y, z = point
    ax, ay, az = angles
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    return (x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az), z)


def project_point(point):
    x, y, z = point
    scale = 700 / (700 - z) * 74 / 77
    return x * scale, -y * scale


MOTION_PERIOD = 18
RING_TURNS = (1, -2, 3)
RING_AZIMUTHS = (8., 128., 248.)
RING_AXIS_TILTS = (42., 46., 49.)
RING_AXES = tuple((math.sin(math.radians(azimuth))*math.sin(math.radians(tilt)),
                   -math.cos(math.radians(azimuth))*math.sin(math.radians(tilt)),
                   math.cos(math.radians(tilt)))
                  for azimuth, tilt in zip(RING_AZIMUTHS, RING_AXIS_TILTS))
RING_RADII = (45., 51., 57.)
BASE_ANGLES = tuple((math.radians(tilt), 0., math.radians(azimuth))
                    for tilt, azimuth in zip((52., 58., 62.), RING_AZIMUTHS))


def axis_rotate(point, axis, angle):
    """로드리게스 식으로 고유 축 주위를 회전하며 공통 Z 변환을 쓰지 않습니다."""
    length = math.sqrt(sum(v*v for v in axis))
    u, v, w = (item/length for item in axis)
    x, y, z = point
    c, q = math.cos(angle), math.sin(angle)
    dot = u*x + v*y + w*z
    return (x*c + (v*z-w*y)*q + u*dot*(1-c),
            y*c + (w*x-u*z)*q + v*dot*(1-c),
            z*c + (u*y-v*x)*q + w*dot*(1-c))


def ring_normal(index, elapsed):
    normal = rotate_point((0, 0, 1), BASE_ANGLES[index])
    return axis_rotate(normal, RING_AXES[index], math.tau*(elapsed % MOTION_PERIOD)/MOTION_PERIOD*RING_TURNS[index])


def ring_points(index, elapsed, count=96):
    angle = math.tau*(elapsed % MOTION_PERIOD)/MOTION_PERIOD*RING_TURNS[index]
    return [axis_rotate(rotate_point((RING_RADII[index]*math.cos(n*math.tau/count), RING_RADII[index]*math.sin(n*math.tau/count), 0),
                                     BASE_ANGLES[index]), RING_AXES[index], angle) for n in range(count)]


def orbit_segments(elapsed):
    """제작 매니페스트와 일치하는 기하 검증용 메타입니다. GUI 드로잉에는 쓰지 않습니다."""
    segments = []
    for index in range(3):
        points = ring_points(index, elapsed)
        for number, point in enumerate(points):
            following = points[(number+1) % len(points)]
            segments.append(((point[2]+following[2])/2, project_point(point), project_point(following),
                             index, (0,0), (0,0)))
    return sorted(segments, key=lambda segment: segment[0])


def gray(level, alpha=255):
    level = max(0, min(255, int(level)))
    return QColor(level, level, level, alpha)


def status_label(healthy, unread):
    """읽지 않은 변경을 우선 표시하며 감시 상태는 실제 플래그에서만 읽습니다."""
    return t('새 변경') if unread else t('감시 중') if healthy else t('확인 필요')


def element_labels(element, badge, state, healthy, unread):
    """원자번호와 계정 퍼센트를 서로 다른 명시적 라벨로 구분합니다."""
    usage = (t('잔량 ') + badge) if state == 'fresh' else t('잔량 지연') if state == 'stale' else t('잔량 미확인')
    return str(element.number), element.symbol, t(element.name), usage, status_label(healthy, unread)


# 움직이는 조형물·원소 도크·계정 잔량은 서로 독립된 화면 영역입니다.
ATOM_RECT = QRectF(-48,-74,96,96)
DOCK_RECT = QRectF(-68,25,136,27)
USAGE_RECT = QRectF(-68,56,136,16)
USAGE_TRACK_RECT = QRectF(-61,62,62,4)
SYMBOL_PIXELS = 24


def usage_bar(badge, fraction, state):
    """숫자와 채움에 같은 실제 비율을 쓰며 최소 채움 폭을 강제하지 않습니다."""
    rect = QRectF(USAGE_TRACK_RECT)
    valid = (isinstance(fraction,(int,float)) and not isinstance(fraction,bool)
             and math.isfinite(fraction) and 0 <= fraction <= 1)
    if state != 'fresh' or not valid:
        rect.setWidth(0)
        return rect, t('잔량 지연') if state == 'stale' else t('잔량 미확인')
    rect.setWidth(USAGE_TRACK_RECT.width()*fraction)
    return rect, t('잔량 ')+percentage_text(fraction*100)


def _frame_for_element(element, elapsed):
    """원소별 실제 제작 프레임을 읽습니다. 이전 형상으로 대체하지 않습니다."""
    from element_frames import get_element_frame
    return get_element_frame(element,elapsed)


def draw_orbit(painter, elapsed, badge='—', fraction=None, state='unknown', healthy=False, unread=False, light=False, element=None):
    """달력 조형·날짜 도크·실제 잔량을 분리하고 명시한 원소 미리보기도 보존합니다."""
    calendar = None
    if element is None:
        from calendar_art import design_for_date, current_date
        from calendar_motion import get_calendar_frame
        calendar = design_for_date(current_date())
        source = get_calendar_frame(elapsed)
        accent = calendar.accent
    else:
        source = _frame_for_element(element,elapsed)
        accent = element.accent
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawImage(ATOM_RECT,source)
    font = app_font(weight=QFont.Weight.Bold)
    painter.setFont(font)
    scale = max(1.,abs(painter.combinedTransform().m11())*painter.device().devicePixelRatioF())
    # 투명 ARGB 글자층은 서브픽셀 색 프린지 없이 모션과 독립적으로 고정됩니다.
    layer = QImage(math.ceil(148*scale),math.ceil(148*scale),QImage.Format.Format_ARGB32_Premultiplied)
    layer.setDevicePixelRatio(scale)
    layer.fill(Qt.GlobalColor.transparent)
    text = QPainter(layer)
    text.setRenderHint(QPainter.RenderHint.Antialiasing)
    text.translate(74,74)
    def label(rect,value,pixels,color=gray(248)):
        local=QFont(font);local.setPixelSize(pixels)
        measured=QFontMetricsF(local).horizontalAdvance(value)
        if measured>rect.width()-2:local.setPixelSize(max(7,int(pixels*(rect.width()-2)/measured)))
        text.setFont(local)
        text.setPen(color)
        text.drawText(rect,Qt.AlignmentFlag.AlignCenter,value)
    def surface(rect,radius):
        gradient=QLinearGradient(rect.topLeft(),rect.bottomLeft())
        gradient.setColorAt(0,QColor('#34414f'));gradient.setColorAt(.48,QColor('#202b37'));gradient.setColorAt(1,QColor('#101923'))
        text.setPen(QColor('#778b9f'))
        text.setBrush(gradient);text.drawRoundedRect(rect,radius,radius)
    surface(DOCK_RECT,8)
    if calendar is not None:
        today = calendar.date
        label(QRectF(-64,25,128,13),today.strftime('%Y/%m/%d'),10,QColor(accent))
        label(QRectF(-64,38,128,14),t(calendar.title),11)
    else:
        label(QRectF(-64,28,22,20),str(element.number),12,QColor(accent))
        label(QRectF(-39,24,50,28),element.symbol,SYMBOL_PIXELS)
        label(QRectF(17,28,46,20),t(element.name),12)
        text.setPen(QColor('#657587'))
        for x in (-40,13):text.drawLine(QPointF(x,32),QPointF(x,45))
    surface(USAGE_RECT,5)
    text.setPen(Qt.PenStyle.NoPen);text.setBrush(QColor('#445364'));text.drawRect(USAGE_TRACK_RECT)
    fill,usage=usage_bar(badge,fraction,state)
    if fill.width()>0:
        text.setBrush(QColor(accent));text.drawRect(fill)
    label(QRectF(5,56,60,16),usage,10)
    text.end()
    painter.drawImage(QRectF(-74,-74,148,148),layer)


def _wrapped_lines(value, font, width):
    """글꼴 크기를 유지한 채 실제 너비로 한 줄씩 배치합니다."""
    value = str(value)
    layout = QTextLayout(value, font)
    option = QTextOption()
    option.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
    layout.setTextOption(option)
    layout.beginLayout()
    lines = []
    while True:
        line = layout.createLine()
        if not line.isValid():
            break
        line.setLineWidth(max(1, width))
        lines.append(value[line.textStart():line.textStart()+line.textLength()].strip())
    layout.endLayout()
    return lines or ['']


def desktop_widget_layout(width, height, title, show_weather=False, show_location=False, text_scale=1.0, weather_extras=(), *, clock_text=None, weather_text=None, fraction=None, state='unknown', calendar_date='2026/12/31'):
    """실제 글자 폭과 조형 최소 영역으로 안정된 읽기 높이를 계산합니다."""
    if type(text_scale) not in (int,float) or not math.isfinite(text_scale) or not .9 <= text_scale <= 1.5:
        raise ValueError('위젯 글자 배율은 0.9~1.5 범위여야 합니다.')
    name_font = app_font(round(16*text_scale), weight=QFont.Weight.Bold)
    date_font = app_font(round(14*text_scale), weight=QFont.Weight.Bold)
    weather_font = app_font(round(13*text_scale), weight=QFont.Weight.Bold)
    text_width = max(1, width-32)
    lines = _wrapped_lines(title, name_font, text_width)
    line_height = math.ceil(QFontMetricsF(name_font).height())
    info_line_height = math.ceil(QFontMetricsF(date_font).height())+2*text_scale
    extra_height = math.ceil(QFontMetricsF(weather_font).height())+2*text_scale
    # 매초 바뀌는 숫자의 너비로 날짜·시간 행 수가 출렁이지 않게 고정 표본으로 결정합니다.
    split_clock = clock_text is not None and QFontMetricsF(date_font).horizontalAdvance('8888/88/88  88:88:88') > text_width
    clock_lines = ([calendar_date, clock_text] if split_clock else [calendar_date+('  '+clock_text if clock_text else '')])
    dock_height = len(clock_lines)*info_line_height + line_height*len(lines)+8
    primary_lines = _wrapped_lines(weather_text if weather_text is not None else '—', date_font, text_width) if show_weather else []
    weather_lines = [line for extra in weather_extras for line in _wrapped_lines(extra,weather_font,text_width)]
    weather_height = len(primary_lines)*info_line_height + len(weather_lines)*extra_height+4*text_scale
    _, usage_label = usage_bar('', fraction, state)
    usage_lines = _wrapped_lines(usage_label, date_font, text_width)
    usage_height = len(usage_lines)*info_line_height + 10*text_scale
    location_height = info_line_height+4*text_scale if show_location else 0
    minimum_art = min(max(0,width-20),96*text_scale)
    content_height = dock_height+usage_height+6+(weather_height+6 if show_weather else 0)+(location_height+6 if show_location else 0)
    minimum_height = math.ceil(max(250,6+minimum_art+5+content_height+8))
    usage = QRectF(8,height-8-usage_height,width-16,usage_height)
    weather = QRectF(8,usage.top()-6-weather_height,width-16,weather_height) if show_weather else QRectF()
    bottom = weather.top()-6 if show_weather else usage.top()-6
    location = QRectF(8,bottom-location_height,width-16,location_height) if show_location else QRectF()
    dock_bottom = location.top()-6 if show_location else bottom
    dock = QRectF(8,dock_bottom-dock_height,width-16,dock_height)
    side = max(0,min(width-20,dock.top()-11))
    art = QRectF((width-side)/2,max(0,(dock.top()-5-side)/2),side,side)
    extra_rects = [QRectF(16,weather.top()+len(primary_lines)*info_line_height+i*extra_height,text_width,extra_height) for i in range(len(weather_lines))]
    return {'art':art,'dock':dock,'location':location,'weather':weather,'usage':usage,'lines':lines,
            'name_font':name_font,'date_font':date_font,'line_height':line_height,'text_scale':text_scale,
            'weather_font':weather_font,'weather_lines':weather_lines,'weather_extra_rects':extra_rects,
            'minimum_height':minimum_height,'clock_lines':clock_lines,'info_line_height':info_line_height,
            'primary_weather_lines':primary_lines,'usage_lines':usage_lines,'usage_label':usage_label}


def draw_desktop_orbit(painter, width, height, source, design, fraction, state, clock_text=None, weather_text=None, location_text=None, cache=None, text_scale=1.0, weather_extras=()):
    """위젯의 조형과 글자를 별개 영역에 그려 작은 글자 축소를 막습니다."""
    if cache is not None:
        return cache.draw(painter, width, height, source, design, fraction, state,
                          clock_text, weather_text, location_text, text_scale=text_scale, weather_extras=weather_extras)
    layout = desktop_widget_layout(width, height, t(design.title), weather_text is not None, location_text is not None,text_scale=text_scale,weather_extras=weather_extras,clock_text=clock_text,weather_text=weather_text,fraction=fraction,state=state,calendar_date=design.date.strftime('%Y/%m/%d'))
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawImage(layout['art'], source)
    _draw_desktop_information(painter, layout, design, fraction, state, clock_text, weather_text, location_text)
    painter.restore()
    return layout


def _draw_desktop_information(painter, layout, design, fraction, state, clock_text, weather_text, location_text):
    """움직이는 GPU 이미지와 분리한 도크·시계·지역·기온·잔량을 그립니다."""
    palette = colors()
    def surface(rect, radius):
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0, QColor(palette['raised']))
        gradient.setColorAt(.48, QColor(palette['surface']))
        gradient.setColorAt(1, QColor(palette['bg']))
        border = QColor(palette['border'])
        glow = max(0, min(100, int(palette['glow'])))
        if glow:
            accent = QColor(palette['accent_raw'])
            amount = glow / 100 * .35
            border = QColor(*(round(border.getRgb()[i] * (1 - amount) + accent.getRgb()[i] * amount) for i in range(3)))
        painter.setPen(border)
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, radius, radius)
    dock, usage = layout['dock'], layout['usage']
    scale=layout.get('text_scale',1.0)
    surface(dock, 8)
    painter.setFont(layout['date_font'])
    painter.setPen(QColor(palette['accent']))
    for index,line in enumerate(layout['clock_lines']):
        painter.drawText(QRectF(dock.left()+8,dock.top()+3+index*layout['info_line_height'],dock.width()-16,layout['info_line_height']),Qt.AlignmentFlag.AlignCenter,line)
    painter.setFont(layout['name_font'])
    painter.setPen(QColor(palette['text']))
    for index, line in enumerate(layout['lines']):
        painter.drawText(QRectF(dock.left()+8, dock.top()+3+len(layout['clock_lines'])*layout['info_line_height']+index*layout['line_height'],
                               dock.width()-16, layout['line_height']), Qt.AlignmentFlag.AlignCenter, line)
    if location_text is not None:
        surface(layout['location'], 6)
        painter.setFont(layout['date_font'])
        painter.setPen(QColor(palette['text']))
        # 전체 지역명은 위젯 툴팁에 보존하고 화면에는 한 줄만 배치합니다.
        layout['location_text'] = QFontMetricsF(layout['date_font']).elidedText(
            location_text, Qt.TextElideMode.ElideRight, max(0, layout['location'].width()-16))
        painter.drawText(layout['location'].adjusted(8, 0, -8, 0), Qt.AlignmentFlag.AlignCenter, layout['location_text'])
    if weather_text is not None:
        surface(layout['weather'], 6)
        painter.setFont(layout['date_font'])
        painter.setPen(QColor(palette['text']))
        for index,line in enumerate(layout['primary_weather_lines']):
            painter.drawText(QRectF(16,layout['weather'].top()+index*layout['info_line_height'],layout['weather'].width()-16,layout['info_line_height']),Qt.AlignmentFlag.AlignCenter,line)
        painter.setFont(layout['weather_font'])
        for line,rect in zip(layout['weather_lines'],layout['weather_extra_rects']):
            painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,line)
    surface(usage, 6)
    fill, label = usage_bar('', fraction, state)
    track = QRectF(usage.left()+8, usage.bottom()-7, max(0, usage.width()-16), 3)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(palette['track']))
    painter.drawRect(track)
    painter.setBrush(QColor(palette['accent']))
    fill_rect = QRectF(track.left(), track.top(), track.width()*fill.width()/USAGE_TRACK_RECT.width(), track.height())
    painter.drawRect(fill_rect)
    layout['track'], layout['fill'] = track, fill_rect
    painter.setFont(layout['date_font'])
    painter.setPen(QColor(palette['text']))
    for index,line in enumerate(layout['usage_lines']):
        painter.drawText(QRectF(usage.left()+8,usage.top()+1+index*layout['info_line_height'],usage.width()-16,layout['info_line_height']),Qt.AlignmentFlag.AlignCenter,line)



class DesktopOverlayCache:
    """한 위젯의 완전 입력이 같을 때만 단일 투명 정보 레이어를 재사용합니다."""
    def __init__(self):
        self.key = None
        self.layout = None
        self.image = None

    def draw(self, painter, width, height, source, design, fraction, state,
             clock_text, weather_text, location_text, text_scale=1.0, weather_extras=()):
        dpr = painter.device().devicePixelRatioF()
        title = t(design.title)
        font_key = app_font(weight=QFont.Weight.Bold).key()
        key = (width, height, dpr, design.date, title, design.accent,
               fraction, state, clock_text, weather_text, location_text,
               get_language(), font_key, text_scale, tuple(weather_extras),
               tuple(sorted(colors().items())))
        if self.key != key:
            layout = desktop_widget_layout(width, height, title,
                                           weather_text is not None, location_text is not None,text_scale=text_scale,weather_extras=weather_extras,clock_text=clock_text,weather_text=weather_text,fraction=fraction,state=state,calendar_date=design.date.strftime('%Y/%m/%d'))
            image = QImage(math.ceil(width*dpr), math.ceil(height*dpr),
                           QImage.Format.Format_ARGB32_Premultiplied)
            image.setDevicePixelRatio(dpr)
            image.fill(Qt.GlobalColor.transparent)
            layer = QPainter(image)
            try:
                layer.setRenderHint(QPainter.RenderHint.Antialiasing)
                layer.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                _draw_desktop_information(layer, layout, design, fraction, state,
                                          clock_text, weather_text, location_text)
            finally:
                layer.end()
            self.key, self.layout, self.image = key, layout, image
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        # 모션 이미지는 매번 새로 그리고 정적 정보만 한 장으로 합성합니다.
        painter.drawImage(self.layout['art'], source)
        painter.drawImage(QPointF(0, 0), self.image)
        painter.restore()
        return self.layout
