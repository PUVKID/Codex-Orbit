"""제작된 실제3D 금속 프레임과 고정된 실제 잔량·상태를 합성합니다."""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QPainter, QLinearGradient
from atom_frames import get_atom_frames
from elements import daily_element
from typography import app_font


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
    return '새 변경' if unread else '감시 중' if healthy else '확인 필요'


def element_labels(element, badge, state, healthy, unread):
    """원자번호와 계정 퍼센트를 서로 다른 명시적 라벨로 구분합니다."""
    usage = ('잔량 ' + badge) if state == 'fresh' else '잔량 지연' if state == 'stale' else '잔량 미확인'
    return str(element.number), element.symbol, element.name, usage, status_label(healthy, unread)


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
        return rect, '잔량 지연' if state == 'stale' else '잔량 미확인'
    rect.setWidth(USAGE_TRACK_RECT.width()*fraction)
    return rect, '잔량 '+format(fraction*100,'g')+'%'


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
    font = app_font(weight=QFont.Weight.DemiBold)
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
        label(QRectF(-64,27,32,21),f'{today.month}/{today.day}',11,QColor(accent))
        label(QRectF(-27,28,90,20),calendar.title,12)
        text.setPen(QColor('#657587'))
        text.drawLine(QPointF(-30,32),QPointF(-30,45))
    else:
        label(QRectF(-64,28,22,20),str(element.number),12,QColor(accent))
        label(QRectF(-39,24,50,28),element.symbol,SYMBOL_PIXELS)
        label(QRectF(17,28,46,20),element.name,12)
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
