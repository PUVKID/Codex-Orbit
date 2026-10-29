"""제작된 실제3D 금속 프레임과 고정된 실제 잔량·상태를 합성합니다."""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QPainter
from atom_frames import get_atom_frames


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
RING_AXES = ((.06, -.025, 1.), (-.04, .04, 1.), (.03, .06, 1.))
RING_RADII = (45., 51., 57.)
BASE_ANGLES = tuple((math.radians(tilt), 0., math.radians(azimuth))
                    for tilt, azimuth in zip((50., 52., 54.), (8., 70., 132.)))


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


def draw_orbit(painter, elapsed, badge='—', fraction=None, state='unknown', healthy=False, unread=False, light=False):
    """숫자가 없는 실제3D 프레임 위에 현재 계정 값과 상태만 고정 합성합니다."""
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawImage(QRectF(-74, -80, 148, 148), get_atom_frames().frame(elapsed))
    painter.translate(0, -6)
    font = QFont(painter.font())
    font.setWeight(QFont.Weight.Bold)
    # 투명 위젯의 Windows 렌더에서도 숫자와 한글에 색 프린지를 만들지 않습니다.
    font.setStyleStrategy(font.styleStrategy() | QFont.StyleStrategy.NoSubpixelAntialias)
    font.setPointSizeF(13 if len(badge) <= 4 else 8 if len(badge) <= 6 else 6)
    measured = QFontMetricsF(font).horizontalAdvance(badge)
    if measured > 42:
        font.setPointSizeF(font.pointSizeF() * 42 / measured)
    painter.setFont(font)
    # Windows 위젯 엔진이 글꼴 힌트를 무시하더라도 투명 ARGB 표면은 회색조로 합성합니다.
    scale = max(1., abs(painter.combinedTransform().m11()) * painter.device().devicePixelRatioF())
    text_layer = QImage(math.ceil(48 * scale), math.ceil(44 * scale), QImage.Format.Format_ARGB32_Premultiplied)
    text_layer.setDevicePixelRatio(scale)
    text_layer.fill(Qt.GlobalColor.transparent)
    text_painter = QPainter(text_layer)
    text_painter.translate(24, 22)
    text_painter.setFont(font)
    # 구체의 실제 반사 위에서도 숫자 윤곽이 읽히도록 얇은 검정 그림자만 더합니다.
    text_painter.setPen(gray(0))
    for x, y in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        text_painter.drawText(QRectF(-22+x, -13+y, 44, 25), Qt.AlignmentFlag.AlignCenter, badge)
    text_painter.setPen(gray(248))
    text_painter.drawText(QRectF(-22, -13, 44, 25), Qt.AlignmentFlag.AlignCenter, badge)
    text_painter.setPen(gray(170))
    font.setPointSizeF(5.2)
    text_painter.setFont(font)
    text_painter.drawText(QRectF(-20, 10, 40, 9), Qt.AlignmentFlag.AlignCenter,
                          '잔량' if state == 'fresh' else '지연' if state == 'stale' else '미확인')
    text_painter.end()
    painter.drawImage(QRectF(-24, -22, 48, 44), text_layer)
    painter.translate(0, 6)
    # 작은 점 대신 한글 상태를 읽을 수 있는 고대비 표지를 캔버스 안에 둡니다.
    status_layer = QImage(math.ceil(86 * scale), math.ceil(20 * scale), QImage.Format.Format_ARGB32_Premultiplied)
    status_layer.setDevicePixelRatio(scale)
    status_layer.fill(Qt.GlobalColor.transparent)
    status_painter = QPainter(status_layer)
    status_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    status_font = QFont(font)
    status_font.setPixelSize(11)
    status_painter.setFont(status_font)
    for x, y in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        status_painter.setPen(gray(10))
        status_painter.drawText(QRectF(1+x, 1+y, 84, 18), Qt.AlignmentFlag.AlignCenter, status_label(healthy, unread))
    status_painter.setPen(gray(210))
    status_painter.drawText(QRectF(1, 1, 84, 18), Qt.AlignmentFlag.AlignCenter, status_label(healthy, unread))
    status_painter.end()
    painter.drawImage(QRectF(-43, 51, 86, 20), status_layer)
