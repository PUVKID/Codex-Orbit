"""실제 3차원 궤도 좌표와 무채색 금속 렌더링입니다."""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPen, QPolygonF, QRadialGradient


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
    for index in range(3):
        angles = (0.65 + index * 1.02 + elapsed * .29,
                  .42 + index * .83 + elapsed * .37,
                  index * 1.03 + elapsed * .23)
        # 중심선 반지름 간격 9는 튜브 지름 7.6과 가장자리 0.65보다 큽니다.
        radius = 42 + index * 9
        points = [rotate_point((radius * math.cos(a * math.tau / 96),
                                radius * math.sin(a * math.tau / 96), 0), angles) for a in range(96)]
        projected = [project_point(point) for point in points]
        normals = []
        for number in range(96):
            previous, following = projected[(number - 1) % 96], projected[(number + 1) % 96]
            dx, dy = following[0] - previous[0], following[1] - previous[1]
            length = max(.001, math.hypot(dx, dy))
            normals.append((-dy / length * 3.8, dx / length * 3.8))
        for number, a in enumerate(points):
            following = (number + 1) % 96
            b = points[following]
            depth = (a[2] + b[2]) / 2
            segments.append((depth, projected[number], projected[following], index, normals[number], normals[following]))
    return sorted(segments, key=lambda segment: segment[0])


def gray(level, alpha=255):
    level = max(0, min(255, int(level)))
    return QColor(level, level, level, alpha)


def draw_orbit(painter, elapsed, badge='—', fraction=None, state='unknown', healthy=False, unread=False, light=False):
    """장식 모션과 실제 계정 숫자를 분리하고 앞쪽 튜브로 중심을 가립니다."""
    # 원형 외곽 눈금은 모든 프레임에서 같은 1:1 경계를 유지합니다.
    painter.setPen(QPen(gray(180 if light else 105, 180), .8))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(QPointF(0, 0), 67, 67)
    for tick in range(48):
        angle = tick * math.tau / 48
        inner = 62 if tick % 4 == 0 else 64
        painter.setPen(QPen(gray(130 + 85 * math.sin(angle - elapsed * .6), 190), 1))
        painter.drawLine(QPointF(inner * math.cos(angle), inner * math.sin(angle)),
                         QPointF(66 * math.cos(angle), 66 * math.sin(angle)))
    segments = orbit_segments(elapsed)

    def tubes(front):
        for z, a, b, index, normal_a, normal_b in segments:
            if (z >= 0) != front:
                continue
            first, last = QPointF(*a), QPointF(*b)
            luminosity = 130 + z * 1.45 + 22 * math.sin(elapsed * .8 + index * 2 + a[0] * .03)
            dx, dy = last.x() - first.x(), last.y() - first.y()
            length = math.hypot(dx, dy)
            if length < .001:
                continue
            # 이웃 분할선이 끝점과 법선을 공유하여 닫힌 링의 접합 각짐을 막습니다.
            start_normal, end_normal = QPointF(*normal_a), QPointF(*normal_b)
            normal = (start_normal + end_normal) / 2
            middle = (first + last) / 2
            gradient = QLinearGradient(middle - normal, middle + normal)
            for position, shade in ((0, 20), (.2, luminosity * .65), (.42, luminosity + 68),
                                    (.6, luminosity), (1, 22)):
                gradient.setColorAt(position, gray(shade))
            painter.setPen(QPen(gradient, .65))
            painter.setBrush(gradient)
            painter.drawPolygon(QPolygonF([first - start_normal, last - end_normal, last + end_normal, first + start_normal]))

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
    painter.drawArc(QRectF(-24, -24, 48, 48), int((90 - elapsed * 18) * 16), -int(arc * 16))
    painter.setPen(gray(248))
    font = QFont(painter.font())
    font.setWeight(QFont.Weight.Bold)
    # 투명 위젯의 Windows 렌더에서도 숫자와 한글에 색 프린지를 만들지 않습니다.
    font.setStyleStrategy(font.styleStrategy() | QFont.StyleStrategy.NoSubpixelAntialias)
    font.setPointSizeF(10 if len(badge) <= 4 else 8 if len(badge) <= 6 else 6)
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
    painter.setBrush(gray(245 if unread else 165 if healthy else 30))
    painter.setPen(QPen(gray(235), 1))
    painter.drawEllipse(QPointF(0, 33), 3, 3)
    if not healthy:
        painter.drawLine(QPointF(-2, 33), QPointF(2, 33))
