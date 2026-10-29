"""바탕화면 위젯 크기 조절과 저장 계약을 검증합니다."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtCore import QCoreApplication, QEvent, QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication
from app import OrbitWidget, Settings

class WidgetResizeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_independent_resize_persists_and_does_not_open_details(self):
        with tempfile.TemporaryDirectory() as folder:
            settings = Settings(folder)
            opened = []
            widget = OrbitWidget(settings, lambda: opened.append(True), lambda: None)
            try:
                self.assertEqual((widget.width(), widget.height()), (220, 332))
                start = QPoint(widget.width()-2, widget.height()//2)
                origin = widget.mapToGlobal(start)
                def event(kind, point, global_point, button, buttons):
                    return QMouseEvent(kind, point, global_point, button, buttons, Qt.KeyboardModifier.NoModifier)
                widget.mousePressEvent(event(QEvent.Type.MouseButtonPress, start, origin, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton))
                widget.mouseMoveEvent(event(QEvent.Type.MouseMove, start+QPoint(60,0), origin+QPoint(60,0), Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton))
                widget.mouseReleaseEvent(event(QEvent.Type.MouseButtonRelease, start+QPoint(60,0), origin+QPoint(60,0), Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton))
                self.assertEqual((widget.width(), widget.height()), (280, 332))
                self.assertEqual(settings.values['size'], [280,332])
                self.assertFalse(opened)
                start = QPoint(widget.width()//2, widget.height()-2)
                origin = widget.mapToGlobal(start)
                widget.mousePressEvent(event(QEvent.Type.MouseButtonPress, start, origin, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton))
                widget.mouseMoveEvent(event(QEvent.Type.MouseMove, start+QPoint(0,35), origin+QPoint(0,35), Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton))
                widget.mouseReleaseEvent(event(QEvent.Type.MouseButtonRelease, start+QPoint(0,35), origin+QPoint(0,35), Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton))
                self.assertEqual((widget.width(), widget.height()), (280, 367))
                self.assertEqual(settings.values['size'], [280,367])
                self.assertFalse(opened)
                middle = QPoint(widget.width()//2, widget.height()//2)
                global_middle = widget.mapToGlobal(middle)
                widget.mousePressEvent(event(QEvent.Type.MouseButtonPress, middle, global_middle, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton))
                widget.mouseReleaseEvent(event(QEvent.Type.MouseButtonRelease, middle, global_middle, Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton))
                self.assertEqual(opened, [True])
                again = OrbitWidget(Settings(folder), lambda: None, lambda: None)
                try:
                    self.assertEqual((again.width(), again.height()), (280,367))
                finally:
                    again.close(); again.deleteLater()
                    QCoreApplication.sendPostedEvents(again, QEvent.Type.DeferredDelete)
            finally:
                widget.close(); widget.deleteLater()
                QCoreApplication.sendPostedEvents(widget, QEvent.Type.DeferredDelete)
                self.qt.processEvents()

    def test_invalid_saved_size_and_offscreen_position_are_recovered(self):
        with tempfile.TemporaryDirectory() as folder:
            settings = Settings(folder)
            settings.values.update({'size': ['bad', 300], 'position': [900000, 900000]})
            widget = OrbitWidget(settings, lambda: None, lambda: None)
            try:
                self.assertEqual((widget.width(), widget.height()), (220, 332))
                screen = self.qt.primaryScreen().availableGeometry()
                self.assertTrue(screen.contains(widget.geometry()))
            finally:
                widget.close(); widget.deleteLater()
                QCoreApplication.sendPostedEvents(widget, QEvent.Type.DeferredDelete)
                self.qt.processEvents()

    def test_readable_long_name_and_actual_bar_at_multiple_sizes(self):
        from datetime import date
        from types import SimpleNamespace
        from PySide6.QtGui import QFontMetricsF, QImage, QPainter, QColor
        from visuals import draw_desktop_orbit
        name = '열여섯글자까지길어지는실제꽃이름입니다'
        design = SimpleNamespace(title=name, date=date(2026, 10, 28), accent='#8EDCCB')
        frame = QImage(240, 240, QImage.Format.Format_ARGB32_Premultiplied)
        frame.fill(QColor('#698b98'))
        for width, height in ((180,210), (220,260), (640,210), (180,500)):
            for fraction in (0, .4325, 1):
                image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
                image.fill(Qt.GlobalColor.transparent)
                painter = QPainter(image)
                result = draw_desktop_orbit(painter, width, height, frame, design, fraction, 'fresh')
                painter.end()
                self.assertEqual(''.join(result['lines']), name)
                self.assertEqual(result['name_font'].pixelSize(), 16)
                self.assertEqual(result['date_font'].pixelSize(), 14)
                self.assertTrue(all(QFontMetricsF(result['name_font']).horizontalAdvance(line) <= width-32 for line in result['lines']))
                self.assertLessEqual(result['art'].bottom(), result['dock'].top())
                self.assertLessEqual(result['dock'].bottom(), result['usage'].top())
                self.assertAlmostEqual(result['fill'].width(), result['track'].width()*fraction)
                self.assertGreater(result['art'].width(), 0)

if __name__ == '__main__':
    unittest.main()
