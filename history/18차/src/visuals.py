"""제작된 실제3D 금속 프레임과 고정된 실제 잔량·상태를 합성합니다."""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QPainter
from atom_frames import get_atom_frames
from elements import daily_element
from element_visuals import colorize_atom


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


def draw_orbit(painter, elapsed, badge='—', fraction=None, state='unknown', healthy=False, unread=False, light=False, element=None):
    """같은3D 프레임 위에 오늘 원소·별도 실제 잔량·상태를 합성합니다."""
    element = daily_element() if element is None else element
    labels = element_labels(element,badge,state,healthy,unread)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawImage(QRectF(-74,-80,148,148),colorize_atom(get_atom_frames().frame(elapsed),element))
    font = QFont(painter.font())
    font.setWeight(QFont.Weight.Bold)
    font.setStyleStrategy(font.styleStrategy() | QFont.StyleStrategy.NoSubpixelAntialias)
    painter.setFont(font)
    scale = max(1.,abs(painter.combinedTransform().m11())*painter.device().devicePixelRatioF())
    # 투명 ARGB에서 글자를 그려 Windows에서도 서브픽셀 색 프린지를 방지합니다.
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
        text.setPen(gray(8))
        for x,y in ((-1,0),(1,0),(0,-1),(0,1)):
            text.drawText(rect.translated(x,y),Qt.AlignmentFlag.AlignCenter,value)
        text.setPen(color)
        text.drawText(rect,Qt.AlignmentFlag.AlignCenter,value)
    label(QRectF(-22,-28,44,12),labels[0],9,QColor(element.accent))
    label(QRectF(-24,-18,48,25),labels[1],23)
    label(QRectF(-26,7,52,12),labels[2],10,QColor(element.accent))
    # 사용률은 중앙 원소번호와 분리된 표지에만 표시합니다.
    text.setPen(Qt.PenStyle.NoPen)
    text.setBrush(QColor(15,19,23,225))
    text.drawRoundedRect(QRectF(-47,33,94,18),7,7)
    label(QRectF(-45,33,90,18),labels[3],11)
    label(QRectF(-43,51,86,20),labels[4],11,gray(220))
    text.end()
    painter.drawImage(QRectF(-74,-74,148,148),layer)
