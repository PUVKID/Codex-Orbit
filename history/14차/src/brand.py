"""실시간 캐릭터와 같은 세 링을 사용하는 절제된 정적 마크입니다."""
from functools import lru_cache
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen
from visuals import ring_points, project_point

@lru_cache(maxsize=7)
def brand_image(size):
    size = int(size)
    padding = 164 if size <= 32 else 148
    image = QImage(size,size,QImage.Format.Format_RGBA8888)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.translate(size/2,size/2)
    painter.scale(size/padding,size/padding)
    paths=[]
    for index in range(3):
        points=[project_point(point) for point in ring_points(index,0)]
        path=QPainterPath(QPointF(*points[0]))
        for point in points[1:]:path.lineTo(QPointF(*point))
        path.closeSubpath();paths.append(path)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    for color,width in (('#111111',max(8,padding/size*4)),('#eeeeee',max(3.6,padding/size*1.4))):
        painter.setPen(QPen(QColor(color),width))
        for path in paths:painter.drawPath(path)
    painter.setBrush(QColor('#141414'));painter.setPen(QPen(QColor('#a0a0a0'),max(.7,padding/size*.4)))
    painter.drawEllipse(QPointF(0,0),15,15)
    painter.end();return image
