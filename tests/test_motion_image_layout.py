"""실제 부모 배치에서 모션 픽셀 교체와 QLabel 표시 계약을 검사합니다."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtCore import QCoreApplication, QEvent, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from brand import AnimatedBrand, brand_image
from usage_widgets import CalendarHero


class IdleClock:
    def watch(self, mark):
        pass

    def unwatch(self, mark):
        pass

    def prune(self, *args):
        pass


class LayoutParent(QWidget):
    def __init__(self):
        super().__init__()
        self.requests = 0

    def event(self, event):
        if event.type() == QEvent.Type.LayoutRequest:
            self.requests += 1
        return super().event(event)


class MotionImageLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.clock_patch = patch('brand.brand_clock', return_value=IdleClock())
        self.clock_patch.start()
        self.addCleanup(self.clock_patch.stop)
        self.parents = []
        self.addCleanup(self.cleanup)

    def cleanup(self):
        for parent in self.parents:
            parent.close()
            parent.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.qt.processEvents()

    def flush(self):
        for _ in range(3):
            QCoreApplication.sendPostedEvents(None, QEvent.Type.LayoutRequest)
            self.qt.processEvents()

    def pixmap(self, index, width=40, height=40, dpr=1.0):
        image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.fillRect(index % max(1, width // 2), 3, max(2, width // 3), max(2, height // 3), QColor('#54B8DD'))
        painter.fillRect(width // 2, height // 2, 3, 3, QColor(220, 80, 100, 120))
        painter.end()
        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(dpr)
        return pixmap

    def pixels(self, image):
        converted = image.convertToFormat(QImage.Format.Format_RGBA8888)
        return bytes(converted.constBits())

    def mounted(self, kind):
        parent = LayoutParent()
        parent.resize(220, 220)
        parent.setStyleSheet('background:#132335;')
        layout = QVBoxLayout(parent)
        label = CalendarHero() if kind == 'hero' else AnimatedBrand(40)
        layout.addWidget(label)
        self.parents.append(parent)
        parent.show()
        self.flush()
        return parent, label

    def assert_same_size_updates_do_not_relayout(self, kind):
        parent, label = self.mounted(kind)
        label.setPixmap(self.pixmap(0))
        self.flush()
        parent.requests = 0
        latest = None
        for index in range(1, 9):
            latest = self.pixmap(index)
            label.setPixmap(latest)
            self.flush()
        self.assertEqual(self.pixels(label.pixmap().toImage()), self.pixels(latest.toImage()))
        self.assertEqual(parent.requests, 0, '같은 크기의 새 모션 픽셀이 부모 배치를 다시 요청했습니다.')

    def test_hero_same_size_frames_do_not_repeat_parent_layout(self):
        self.assert_same_size_updates_do_not_relayout('hero')

    def test_brand_same_size_frames_do_not_repeat_parent_layout(self):
        self.assert_same_size_updates_do_not_relayout('brand')

    def test_latest_transparent_pixels_alignment_and_background_match_native_label(self):
        for kind in ('hero', 'brand'):
            with self.subTest(kind=kind):
                parent, label = self.mounted(kind)
                reference = QLabel(parent)
                reference.setFixedSize(label.size())
                reference.setAlignment(label.alignment())
                reference.setStyleSheet(label.styleSheet())
                reference.move(label.pos())
                reference.show()
                for index, dpr in ((0, 1.0), (9, 1.0), (3, 2.0)):
                    pixmap = self.pixmap(index, 40, 40, dpr)
                    label.setPixmap(pixmap)
                    reference.setPixmap(pixmap)
                    self.flush()
                    self.assertEqual(self.pixels(label.grab().toImage()), self.pixels(reference.grab().toImage()))
                reference.close()

    def test_size_hint_updates_for_size_and_dpr_and_text_clear_restores_fallback(self):
        label = CalendarHero()
        reference = QLabel()
        self.parents.extend((label, reference))
        reference.setAlignment(label.alignment())
        reference.setMinimumSize(label.minimumSize())
        reference.setMaximumWidth(label.maximumWidth())
        reference.setSizePolicy(label.sizePolicy())
        reference.setStyleSheet(label.styleSheet())
        for width, height, dpr in ((40, 40, 1.0), (80, 40, 1.0), (80, 40, 2.0)):
            pixmap = self.pixmap(2, width, height, dpr)
            label.setPixmap(pixmap)
            reference.setPixmap(pixmap)
            self.assertEqual(label.sizeHint(), reference.sizeHint())
            self.assertEqual(label.minimumSizeHint(), reference.minimumSizeHint())
            self.assertEqual(label.pixmap().devicePixelRatioF(), reference.pixmap().devicePixelRatioF())
            self.assertEqual(label.pixmap().size(), reference.pixmap().size())
            self.assertEqual(self.pixels(label.pixmap().toImage()), self.pixels(reference.pixmap().toImage()))
        for text in ('입체 이미지 표시 오류: 제어된 오류', '3D image error: controlled', ''):
            pixmap = self.pixmap(1)
            label.setPixmap(pixmap)
            reference.setPixmap(pixmap)
            label.setText(text)
            reference.setText(text)
            self.assertEqual(label.text(), reference.text())
            self.assertEqual(label.pixmap().isNull(), reference.pixmap().isNull())
            if text:
                self.assertTrue(label.pixmap().isNull())
            else:
                self.assertEqual(self.pixels(label.pixmap().toImage()), self.pixels(reference.pixmap().toImage()))
            self.assertEqual(label.sizeHint(), reference.sizeHint())
        label.clear()
        self.assertTrue(label.pixmap().isNull())
        self.assertEqual(label.text(), '')

    def test_brand_initial_static_image_and_hero_error_path_are_preserved(self):
        mark = AnimatedBrand(40)
        hero = CalendarHero()
        self.parents.extend((mark, hero))
        self.assertEqual(self.pixels(mark.pixmap().toImage()), self.pixels(brand_image(40)))
        with patch('calendar_motion.get_calendar_frame', return_value=QImage(32, 32, QImage.Format.Format_ARGB32_Premultiplied)):
            with patch('calendar_motion.get_calendar_error', return_value='제어된 GPU 오류'):
                hero.refresh_frame()
        self.assertEqual(hero.text(), '입체 이미지 표시 오류: 제어된 GPU 오류')
        self.assertTrue(hero.pixmap().isNull())


if __name__ == '__main__':
    unittest.main()
