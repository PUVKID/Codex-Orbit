"""수리9 이전 원본 픽셀과 단일 정적 레이어의 완전 입력 무효화를 검사합니다."""
from dataclasses import replace
from datetime import date
import math
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QPainter, QLinearGradient, QTextLayout, QTextOption
from PySide6.QtWidgets import QApplication
from calendar_art import design_for_date
from i18n import translate as t, set_language
from typography import app_font
import visuals
from visuals import gray, usage_bar, USAGE_TRACK_RECT

# 수리9 제품 변경 전 원본에서 보존한 독립 기준입니다. 현재 제품에서 다시 생성하지 않습니다.
BASELINE_SOURCE_SHA256 = 'd4bb20ebbfa421b5f05a482aedbb0b2202b7f7ffc2e6f7e22916ace3d0d72e1d'

def _baseline_layout(width, height, title, show_weather=False, show_location=False):
    """이름을 화면 픽셀 크기로 줄 바꿈하고 조형·잔량 영역을 분리합니다."""
    name_font = app_font(weight=QFont.Weight.Bold)
    name_font.setPixelSize(16)
    date_font = app_font(weight=QFont.Weight.Bold)
    date_font.setPixelSize(14)
    metrics = QFontMetricsF(name_font)
    text_width = max(1, width - 32)
    layout = QTextLayout(title, name_font)
    option = QTextOption()
    option.setWrapMode(QTextOption.WrapMode.WrapAnywhere)
    layout.setTextOption(option)
    layout.beginLayout()
    lines = []
    while True:
        line = layout.createLine()
        if not line.isValid():
            break
        line.setLineWidth(text_width)
        lines.append(title[line.textStart():line.textStart()+line.textLength()])
    layout.endLayout()
    line_height = math.ceil(metrics.height())
    dock_height = 24 + line_height * max(1, len(lines)) + 8
    usage = QRectF(8, height - 34, width - 16, 26)
    weather = QRectF(8, usage.top() - 32, width - 16, 26) if show_weather else QRectF()
    info_bottom = weather.top() - 6 if show_weather else usage.top() - 6
    location = QRectF(8, info_bottom - 26, width - 16, 26) if show_location else QRectF()
    dock_bottom = location.top() - 6 if show_location else info_bottom
    dock = QRectF(8, dock_bottom - dock_height, width - 16, dock_height)
    art_bottom = max(0, dock.top() - 5)
    side = max(0, min(width - 20, art_bottom - 6))
    art = QRectF((width-side)/2, max(0, (art_bottom-side)/2), side, side)
    return {'art': art, 'dock': dock, 'location': location, 'weather': weather, 'usage': usage, 'lines': lines, 'name_font': name_font,
            'date_font': date_font, 'line_height': line_height}


def _baseline_draw(painter, width, height, source, design, fraction, state, clock_text=None, weather_text=None, location_text=None):
    """위젯의 조형과 글자를 별개 영역에 그려 작은 글자 축소를 막습니다."""
    layout = _baseline_layout(width, height, t(design.title), weather_text is not None, location_text is not None)
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawImage(layout['art'], source)
    def surface(rect, radius):
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0, QColor('#34414f'))
        gradient.setColorAt(.48, QColor('#202b37'))
        gradient.setColorAt(1, QColor('#101923'))
        painter.setPen(QColor('#778b9f'))
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, radius, radius)
    dock, usage = layout['dock'], layout['usage']
    surface(dock, 8)
    painter.setFont(layout['date_font'])
    painter.setPen(QColor(design.accent))
    painter.drawText(QRectF(dock.left()+8, dock.top()+3, dock.width()-16, 20),
                     Qt.AlignmentFlag.AlignCenter, f'{design.date.month}/{design.date.day}' + ('  ' + clock_text if clock_text else ''))
    painter.setFont(layout['name_font'])
    painter.setPen(gray(248))
    for index, line in enumerate(layout['lines']):
        painter.drawText(QRectF(dock.left()+8, dock.top()+24+index*layout['line_height'],
                               dock.width()-16, layout['line_height']), Qt.AlignmentFlag.AlignCenter, line)
    if location_text is not None:
        surface(layout['location'], 6)
        painter.setFont(layout['date_font'])
        painter.setPen(gray(248))
        # 전체 지역명은 위젯 툴팁에 보존하고 화면에는 한 줄만 배치합니다.
        layout['location_text'] = QFontMetricsF(layout['date_font']).elidedText(
            location_text, Qt.TextElideMode.ElideRight, max(0, layout['location'].width()-16))
        painter.drawText(layout['location'].adjusted(8, 0, -8, 0), Qt.AlignmentFlag.AlignCenter, layout['location_text'])
    if weather_text is not None:
        surface(layout['weather'], 6)
        painter.setFont(layout['date_font'])
        painter.setPen(gray(248))
        painter.drawText(layout['weather'], Qt.AlignmentFlag.AlignCenter, weather_text)
    surface(usage, 6)
    fill, label = usage_bar('', fraction, state)
    track = QRectF(usage.left()+8, usage.bottom()-7, max(0, usage.width()-16), 3)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor('#445364'))
    painter.drawRect(track)
    painter.setBrush(QColor(design.accent))
    fill_rect = QRectF(track.left(), track.top(), track.width()*fill.width()/USAGE_TRACK_RECT.width(), track.height())
    painter.drawRect(fill_rect)
    layout['track'], layout['fill'] = track, fill_rect
    font = app_font(weight=QFont.Weight.Bold)
    font.setPixelSize(14)
    painter.setFont(font)
    painter.setPen(gray(248))
    painter.drawText(QRectF(usage.left()+5, usage.top()+1, usage.width()-10, 18), Qt.AlignmentFlag.AlignCenter, label)
    painter.restore()
    return layout


class DesktopOverlayCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        set_language('ko')
        self.addCleanup(set_language, 'ko')

    def cache(self):
        kind = getattr(visuals, 'DesktopOverlayCache', None)
        self.assertIsNotNone(kind, '위젯 소유 단일 정적 레이어 캐시가 없습니다.')
        return kind()

    def values(self):
        return dict(width=220, height=332, dpr=1.0,
                    design=design_for_date(date(2026, 10, 30)), fraction=.4325,
                    state='fresh', clock_text='23:59:58', weather_text='18.5℃',
                    location_text='대한민국 · 예시 지역')

    def paint(self, values, cache=None, baseline=False, source_color='#7198C0'):
        width, height, dpr = values['width'], values['height'], values['dpr']
        image = QImage(math.ceil(width*dpr), math.ceil(height*dpr), QImage.Format.Format_ARGB32_Premultiplied)
        image.setDevicePixelRatio(dpr)
        image.fill(Qt.GlobalColor.transparent)
        source = QImage(96, 96, QImage.Format.Format_ARGB32_Premultiplied)
        source.fill(QColor(source_color))
        painter = QPainter(image)
        args = (painter, width, height, source, values['design'], values['fraction'],
                values['state'], values['clock_text'], values['weather_text'], values['location_text'])
        try:
            if baseline:
                layout = _baseline_draw(*args)
            else:
                layout = visuals.draw_desktop_orbit(*args, cache=cache)
        finally:
            painter.end()
        return image, layout

    def pixels(self, image):
        rgba = image.convertToFormat(QImage.Format.Format_RGBA8888)
        return bytes(rgba.constBits())

    def assert_matches_baseline(self, values, cache):
        expected, expected_layout = self.paint(values, baseline=True)
        actual, actual_layout = self.paint(values, cache)
        self.assertEqual(self.pixels(actual), self.pixels(expected))
        for key in ('art', 'dock', 'weather', 'location', 'usage', 'track', 'fill', 'lines', 'line_height'):
            self.assertEqual(actual_layout[key], expected_layout[key])

    def test_pixels_match_preserved_drawing_for_sizes_values_languages_and_dpr(self):
        cache = self.cache()
        for language in ('ko', 'en'):
            set_language(language)
            for size in ((180, 250), (220, 332), (420, 270)):
                for dpr in (1.0, 1.25, 2.0):
                    for fraction, state in ((None, 'unknown'), (0.0, 'fresh'), (.4325, 'fresh'), (1.0, 'fresh'), (.4, 'stale')):
                        with self.subTest(language=language, size=size, dpr=dpr, fraction=fraction, state=state):
                            values = dict(self.values(), width=size[0], height=size[1], dpr=dpr, fraction=fraction, state=state)
                            self.assert_matches_baseline(values, cache)

    def test_same_inputs_reuse_overlay_while_real_source_pixels_change(self):
        cache = self.cache()
        values = self.values()
        images = []
        with patch.object(visuals, 'desktop_widget_layout', wraps=visuals.desktop_widget_layout) as layout:
            for color in ('#7198C0', '#B8C8D4', '#223344'):
                image, _ = self.paint(values, cache, source_color=color)
                expected, _ = self.paint(values, baseline=True, source_color=color)
                self.assertEqual(self.pixels(image), self.pixels(expected))
                images.append(self.pixels(image))
            self.assertEqual(layout.call_count, 1)
        self.assertEqual(len(set(images)), 3, '오버레이 재사용이 실제 모션 이미지를 고정하면 안 됩니다.')

    def test_every_display_input_invalidates_the_single_overlay_immediately(self):
        base = self.values()
        changes = ({'width': 260}, {'height': 380}, {'dpr': 1.5},
                   {'design': replace(base['design'], title='긴 새 조형 이름')},
                   {'design': replace(base['design'], date=date(2026, 10, 31))},
                   {'design': replace(base['design'], accent='#DCC771')},
                   {'fraction': .91}, {'state': 'stale'}, {'clock_text': '23:59:59'},
                   {'weather_text': '이전 10.5℃'}, {'location_text': '아주 긴 새 지역 이름'},
                   {'weather_text': None}, {'location_text': None}, {'language': 'en'})
        for changed in changes:
            with self.subTest(changed=changed):
                set_language('ko')
                cache = self.cache()
                with patch.object(visuals, 'desktop_widget_layout', wraps=visuals.desktop_widget_layout) as layout:
                    self.paint(base, cache)
                    values = dict(base)
                    if 'language' in changed:
                        set_language(changed['language'])
                    else:
                        values.update(changed)
                    self.assert_matches_baseline(values, cache)
                    self.assertEqual(layout.call_count, 2)


if __name__ == '__main__':
    unittest.main()
