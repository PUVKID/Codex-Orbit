"""앱 소유 조작부의 폭 대응과 명확한 콤보 펼침 표시입니다."""
from PySide6.QtCore import QPointF,Qt
from PySide6.QtGui import QPainter,QPen,QPolygonF
from PySide6.QtWidgets import QWidget,QComboBox,QGridLayout,QSizePolicy,QLayout,QStackedWidget


class OrbitComboBox(QComboBox):
    def paintEvent(self,event):
        super().paintEvent(event)
        painter=QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen=QPen(self.palette().buttonText().color(),1.7);pen.setCapStyle(Qt.PenCapStyle.RoundCap);pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin);painter.setPen(pen)
            x=self.width()-17;y=self.height()/2
            painter.drawPolyline(QPolygonF([QPointF(x-4,y-2),QPointF(x,y+2),QPointF(x+4,y-2)]))
        finally:painter.end()


class ResponsiveRow(QWidget):
    """사용 가능한 폭에 맞춰 조작 그룹을 여러 줄로 배치합니다."""
    def __init__(self,widgets,minimum_columns=1):
        super().__init__();self.widgets=widgets;self.columns=0;self.minimum_columns=minimum_columns
        self.grid=QGridLayout(self);self.grid.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint);self.grid.setContentsMargins(0,0,0,0);self.grid.setSpacing(8)
        self.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred)
        self.reflow()
    def resizeEvent(self,event):
        super().resizeEvent(event);self.reflow()
    def reflow(self):
        widths=[widget.minimumSizeHint().width() for widget in self.widgets]
        columns=len(self.widgets)
        while columns>self.minimum_columns and sum(sorted(widths,reverse=True)[:columns])+8*(columns-1)>max(100,self.width()):columns-=1
        if columns==self.columns:return
        self.columns=columns
        while self.grid.count():self.grid.takeAt(0)
        for index,widget in enumerate(self.widgets):self.grid.addWidget(widget,index//columns,index%columns)


class PageStack(QStackedWidget):
    """페이지 내부의 스크롤이 긴 내용의 높이를 담당하고 바깥 창은 작게 줄일 수 있습니다."""
    def hasHeightForWidth(self):return False
    def heightForWidth(self,width):return -1
