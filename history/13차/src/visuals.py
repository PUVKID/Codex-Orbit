"""최초 참고의 세 교차 타원과 검은 중심을 가볍게 그리는 선형 모션입니다."""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QPainter, QPainterPath, QPen


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
    """서로 다른 세 타원을 닫힌 3차원 원의 투영으로 만들고 깊이순으로 정렬합니다."""
    phase = math.tau * (elapsed % 12) / 12
    segments = []
    for index, orientation in enumerate((.16, 1.35, -.8)):
        angles = (1.04 + index * .035 + .08 * math.sin(phase + index * 1.3),
                  .10 * math.sin(phase + index * 1.5), orientation + phase)
        radius, count = 56, 96
        points = [rotate_point((radius * math.cos(n * math.tau / count),
                                radius * math.sin(n * math.tau / count), 0), angles)
                  for n in range(count)]
        for number, point in enumerate(points):
            following = points[(number + 1) % count]
            segments.append(((point[2] + following[2]) / 2, project_point(point),
                             project_point(following), index, (0, 0), (0, 0)))
    return sorted(segments, key=lambda segment: segment[0])


def gray(level, alpha=255):
    level = max(0, min(255, int(level)))
    return QColor(level, level, level, alpha)


def status_label(healthy, unread):
    """읽지 않은 변경을 우선 표시하며 감시 상태는 실제 플래그에서만 읽습니다."""
    return '새 변경' if unread else '감시 중' if healthy else '확인 필요'


def draw_orbit(painter, elapsed, badge='—', fraction=None, state='unknown', healthy=False, unread=False, light=False):
    """3~5px의 선형 타원과 깊이 가림을 그리고 실제 숫자는 고정합니다."""
    elapsed %= 12
    painter.translate(0, -6)
    groups = {}
    for depth, start, end, index, *_ in orbit_segments(elapsed):
        bucket = max(0, min(3, int((depth + 56) / 28)))
        angle = math.atan2(start[1], start[0])
        highlight = math.cos(angle - elapsed * math.tau / 12 - index * 1.2)
        shade = max(0, min(3, int((highlight + 1) * 1.99)))
        key = (bucket, shade)
        if key not in groups:
            groups[key] = QPainterPath()
        groups[key].moveTo(QPointF(*start))
        groups[key].lineTo(QPointF(*end))

    def lines(front):
        paths = [(depth, shade, path) for (depth, shade), path in sorted(groups.items())
                 if (depth >= 2) == front]
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # 모든 대비 경계를 먼저 그려 밝기 묶음 사이에 검은 마디가 생기지 않게 합니다.
        painter.setPen(QPen(gray(20), 5.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        for _, _, path in paths:
            painter.drawPath(path)
        for depth, shade, path in paths:
            painter.setPen(QPen(gray((152 if front else 115) + shade * 24), 3.6,
                                Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPath(path)

    lines(False)
    painter.setBrush(gray(20))
    painter.setPen(QPen(gray(130), .7))
    painter.drawEllipse(QPointF(0, 0), 24, 24)
    lines(True)
    # 검은 중심과 숫자는 앞쪽 궤도에 가려지지 않는 고정 영역입니다.
    painter.setBrush(gray(20))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QPointF(0, 0), 22, 22)
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
    painter.translate(0, 6)
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
