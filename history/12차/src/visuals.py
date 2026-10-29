"""실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다."""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QLinearGradient, QPainter, QPen, QPolygonF, QRadialGradient


def rotate_point(point, angles):
    """X·Y·Z 순서로 회전하며 깊이 좌표를 보존합니다."""
    x, y, z = point
    ax, ay, az = angles
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    return (x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az), z)


def project_point(point):
    x, y, z = point
    scale = 290 / (290 - z)
    return x * scale, y * scale


def orbit_segments(elapsed):
    """세 대원의 분할선을 원근 투영한 뒤 뒤에서 앞으로 정렬합니다."""
    segments = []
    phase = math.tau * (elapsed % 12) / 12
    for index in range(3):
        angles = (.65 + index * .23 + .18 * math.sin(phase + index),
                  .2 + index * .28 + .22 * math.sin(phase + index * 1.5),
                  index * 1.05 + phase)
        radius = 42 + index * 8
        count = 192
        points = []
        normals = []
        for number in range(count):
            angle = number * math.tau / count
            point = rotate_point((radius * math.cos(angle), radius * math.sin(angle), 0), angles)
            outer = rotate_point(((radius + 6) * math.cos(angle), (radius + 6) * math.sin(angle), 0), angles)
            projected, edge = project_point(point), project_point(outer)
            points.append((point, projected))
            normals.append((edge[0] - projected[0], edge[1] - projected[1]))
        for number, (point, projected) in enumerate(points):
            following = (number + 1) % count
            other, end = points[following]
            segments.append(((point[2] + other[2]) / 2, projected, end, index,
                             normals[number], normals[following]))
    return sorted(segments, key=lambda segment: segment[0])


def gray(level, alpha=255):
    level = max(0, min(255, int(level)))
    return QColor(level, level, level, alpha)


def status_label(healthy, unread):
    """읽지 않은 변경을 우선 표시하며 감시 상태는 실제 플래그에서만 읽습니다."""
    return '새 변경' if unread else '감시 중' if healthy else '확인 필요'


def draw_orbit(painter, elapsed, badge='—', fraction=None, state='unknown', healthy=False, unread=False, light=False):
    """장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다."""
    # 눈금 없는 크롬 리본만 투명 정사각형 캔버스에 그립니다.
    elapsed = elapsed % 12
    segments = orbit_segments(elapsed)

    def tubes(front):
        for z, a, b, index, normal_a, normal_b in segments:
            if (z >= 0) != front:
                continue
            first, last = QPointF(*a), QPointF(*b)
            dx, dy = last.x() - first.x(), last.y() - first.y()
            length = math.hypot(dx, dy)
            if length < .001:
                continue
            # 이웃 분할선이 끝점과 법선을 공유하여 닫힌 링의 접합 각짐을 막습니다.
            start_normal, end_normal = QPointF(*normal_a), QPointF(*normal_b)
            # 같은 리본은 하나의 조명 좌표를 공유해 분할 수와 무관한 매끈한 반사를 만듭니다.
            light_angle = elapsed * math.tau / 12 + index * 1.05
            axis = QPointF(math.cos(light_angle) * 68, math.sin(light_angle) * 68)
            gradient = QLinearGradient(-axis, axis)
            for position, shade in ((0, 24), (.12, 78), (.25, 245), (.35, 142),
                                    (.48, 42), (.6, 115), (.72, 255), (.82, 172), (1, 35)):
                gradient.setColorAt(position, gray(shade))
            # 분할선의 가로 윤곽은 생략하고 이웃 면을 조금 겹쳐 금속 면을 이어 줍니다.
            tangent = QPointF(dx / length * .4, dy / length * .4)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            painter.drawPolygon(QPolygonF([first - start_normal - tangent, last - end_normal + tangent,
                                           last + end_normal + tangent, first + start_normal - tangent]))
            # 리본의 안팎 두 경계만 비추고 각 면의 접합선은 드러내지 않습니다.
            painter.setPen(QPen(gray(190), .38))
            painter.drawLine(first + start_normal, last + end_normal)
            painter.setPen(QPen(gray(48), .4))
            painter.drawLine(first - start_normal, last - end_normal)

    tubes(False)
    gradient = QRadialGradient(QPointF(-8, -11), 40)
    gradient.setColorAt(0, gray(73))
    gradient.setColorAt(.5, gray(35))
    gradient.setColorAt(1, gray(9))
    painter.setBrush(gradient)
    painter.setPen(QPen(gray(170), 1))
    painter.drawEllipse(QPointF(0, 0), 27, 27)
    tubes(True)
    # 숫자 가독성을 위한 작은 원형 렌즈는 중심에서 고정합니다.
    painter.setBrush(gray(19, 242))
    painter.setPen(QPen(gray(120), .7))
    painter.drawEllipse(QPointF(0, 0), 22, 22)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(gray(85), 1.8))
    painter.drawEllipse(QPointF(0, 0), 24, 24)
    painter.setPen(QPen(gray(233 if state == 'fresh' else 130), 2,
                        Qt.PenStyle.SolidLine if state == 'fresh' else Qt.PenStyle.DotLine))
    arc = fraction * 360 if fraction is not None and state == 'fresh' else 68
    painter.drawArc(QRectF(-24, -24, 48, 48), int((90 - elapsed * 30) * 16), -int(arc * 16))
    painter.setPen(gray(248))
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
    text_painter.setPen(gray(248))
    text_painter.drawText(QRectF(-22, -13, 44, 25), Qt.AlignmentFlag.AlignCenter, badge)
    text_painter.setPen(gray(170))
    font.setPointSizeF(5.2)
    text_painter.setFont(font)
    text_painter.drawText(QRectF(-20, 10, 40, 9), Qt.AlignmentFlag.AlignCenter,
                          '잔량' if state == 'fresh' else '지연' if state == 'stale' else '미확인')
    text_painter.end()
    painter.drawImage(QRectF(-24, -22, 48, 44), text_layer)
    # 작은 점 대신 한글 상태를 읽을 수 있는 고대비 표지를 캔버스 안에 둡니다.
    status_layer = QImage(math.ceil(86 * scale), math.ceil(20 * scale), QImage.Format.Format_ARGB32_Premultiplied)
    status_layer.setDevicePixelRatio(scale)
    status_layer.fill(Qt.GlobalColor.transparent)
    status_painter = QPainter(status_layer)
    status_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    status_painter.setPen(QPen(gray(10), 1))
    status_painter.setBrush(gray(250))
    status_painter.drawRoundedRect(QRectF(1, 1, 84, 18), 8, 8)
    status_font = QFont(font)
    status_font.setPixelSize(11)
    status_painter.setFont(status_font)
    status_painter.setPen(gray(10))
    status_painter.drawText(QRectF(1, 1, 84, 18), Qt.AlignmentFlag.AlignCenter, status_label(healthy, unread))
    status_painter.end()
    painter.drawImage(QRectF(-43, 51, 86, 20), status_layer)
