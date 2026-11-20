"""사용자 색상 원값과 읽기용 의미색, 저장과 분리한 미리보기를 제공합니다.

색상 설정 내부의 알 수 없는 키는 거절합니다. 전체 앱 설정의 다른 키와
원자 저장·실제 화면 복원은 적용 콜백을 제공하는 호출자가 책임집니다.
"""
import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QFrame, QGraphicsDropShadowEffect,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QSlider,
    QVBoxLayout, QWidget, QColorDialog,
)
from ui_layout import OrbitComboBox as QComboBox


_DEFAULT_VALUES = (
    ('accent', '#73F936'), ('dark_bg', '#0B0D0C'),
    ('light_bg', '#F7F8F7'), ('glow', 25),
)
DEFAULTS = dict(_DEFAULT_VALUES)


def _preset(ko, en, accent, dark, light):
    return dict(name_ko=ko, name_en=en,
                values=dict(accent=accent, dark_bg=dark, light_bg=light, glow=25))


PRESETS = (
    _preset('레이저 그린', 'Laser green', '#73F936', '#0B0D0C', '#F7F8F7'),
    _preset('에메랄드', 'Emerald', '#19E68C', '#0C1010', '#F5F9F7'),
    _preset('시안', 'Cyan', '#38D9FF', '#0B1014', '#F5F9FC'),
    _preset('바이올렛', 'Violet', '#BA8AFF', '#100D16', '#F9F6FC'),
    _preset('앰버', 'Amber', '#FFBF47', '#141008', '#FCF9F3'),
    _preset('무채색', 'Monochrome', '#A9B5BE', '#0D1012', '#F7F8FA'),
)


def _hex(value):
    if not isinstance(value, str):
        raise ValueError('색상은 6자리 HEX 문자열이어야 합니다.')
    value = value.strip()
    if not re.fullmatch(r'#?[0-9a-fA-F]{6}', value):
        raise ValueError('색상은 #RRGGBB 형식의 6자리 HEX여야 합니다.')
    result = '#' + value.lstrip('#').upper()
    if not QColor(result).isValid():
        raise ValueError('사용할 수 없는 색상입니다.')
    return result


def normalize_config(value):
    """부분 설정을 기본값과 합치며 항상 독립된 정규화 사본을 반환합니다."""
    if value is None:
        value = {}
    if not isinstance(value, dict):
        raise ValueError('색상 설정은 객체여야 합니다.')
    if set(value).difference(dict(_DEFAULT_VALUES)):
        raise ValueError('지원하지 않는 색상 설정 키가 있습니다.')
    result = dict(_DEFAULT_VALUES)
    result.update(value)
    for key in ('accent', 'dark_bg', 'light_bg'):
        result[key] = _hex(result[key])
    if type(result['glow']) is not int or not 0 <= result['glow'] <= 100:
        raise ValueError('조명 강도는 0부터 100까지의 정수여야 합니다.')
    return result


def _rgb(color):
    value = _hex(color)
    return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))


def _luminance(color):
    values = []
    for component in _rgb(color):
        value = component / 255
        values.append(value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4)
    return sum(a * b for a, b in zip(values, (.2126, .7152, .0722)))


def contrast_ratio(foreground, background):
    """sRGB 상대 휘도로 WCAG 명암비를 계산합니다."""
    light, dark = sorted((_luminance(foreground), _luminance(background)), reverse=True)
    return (light + .05) / (dark + .05)


def _mix(first, second, amount):
    channels = [round(a * (1 - amount) + b * amount) for a, b in zip(_rgb(first), _rgb(second))]
    return '#' + ''.join(f'{value:02X}' for value in channels)


def _best_text(background):
    return max(('#000000', '#FFFFFF'), key=lambda value: contrast_ratio(value, background))


def _safe_surface(background, proposed, text):
    # 배경 계층을 만들되 본문 대비를 잃으면 변화량을 줄입니다.
    for step in range(11):
        candidate = _mix(background, proposed, .5 ** step)
        if contrast_ratio(text, candidate) >= 4.5:
            return candidate
    return background


def _readable(seed, backgrounds, fallback):
    # 저장 원색은 건드리지 않고 읽기용 색만 공통 본문 방향으로 보정합니다.
    for step in range(256):
        candidate = _mix(seed, fallback, step / 255)
        if all(contrast_ratio(candidate, background) >= 4.5 for background in backgrounds):
            return candidate
    return fallback


def palette_for(mode, config):
    """해석된 라이트·다크 모드의 의미색을 반환하며 입력 원값은 유지합니다."""
    if mode not in ('light', 'dark'):
        raise ValueError('팔레트 모드는 light 또는 dark여야 합니다.')
    value = normalize_config(config)
    background = value['dark_bg' if mode == 'dark' else 'light_bg']
    text = _best_text(background)
    surface = _safe_surface(background, _mix(background, text, .045), text)
    raised = _safe_surface(background, _mix(background, text, .085), text)
    selected = _safe_surface(background, _mix(background, value['accent'], .18), text)
    surfaces = (background, surface, raised, selected)
    accent = _readable(value['accent'], surfaces, text)
    return dict(
        bg=background, surface=surface, raised=raised, text=text,
        muted=_readable(_mix(background, text, .70), surfaces, text),
        disabled=_readable(_mix(background, text, .58), surfaces, text),
        border=_mix(background, text, .32), accent=accent,
        selected=selected, focus=accent, track=raised,
        accent_raw=value['accent'], accent_text=_best_text(accent),
        glow=value['glow'],
        error=_readable('#D93C4B', surfaces, text),
        warning=_readable('#B66A00', surfaces, text),
    )


class AppearanceDialog(QDialog):
    """전역 테마를 변경하지 않고 독립 미리보기와 적용 콜백을 제공합니다."""

    def __init__(self, config, on_apply, parent=None, language='ko'):
        super().__init__(parent)
        if not callable(on_apply):
            raise ValueError('적용 콜백이 필요합니다.')
        self.language = 'en' if language == 'en' else 'ko'
        self.original_config = normalize_config(config)
        self.applied_config = None
        self.on_apply = on_apply
        self._loading = False
        font = self.font()
        font.setWeight(QFont.Weight.Bold)
        self.setFont(font)
        self.setWindowTitle(self.tr_text('색상 꾸미기', 'Customize colors'))
        self.resize(680, 580)
        self.setMinimumSize(380, 360)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(self.scroll, 1)
        page = QWidget()
        page.setMinimumWidth(0)
        self.scroll.setWidget(page)
        body = QVBoxLayout(page)
        body.setSpacing(12)
        description = QLabel(self.tr_text(
            '원하는 색을 입력하거나 색 조합을 고르세요. 미리보기는 이 창에만 적용됩니다.',
            'Enter colors or choose a palette. The preview changes only this dialog.'))
        description.setWordWrap(True)
        body.addWidget(description)
        self.preset_combo = QComboBox()
        for row in PRESETS:
            self.preset_combo.addItem(row['name_en' if self.language == 'en' else 'name_ko'])
        self.preset_combo.setAccessibleName(self.tr_text('색 조합', 'Color palette'))
        body.addWidget(QLabel(self.tr_text('색 조합', 'Color palette')))
        body.addWidget(self.preset_combo)
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.fields = {}
        self.field_errors = {}
        self.color_buttons = {}
        self._labels = dict(accent=self.tr_text('포인트색', 'Accent'),
                            dark_bg=self.tr_text('다크 배경', 'Dark background'),
                            light_bg=self.tr_text('라이트 배경', 'Light background'))
        for key, title in self._labels.items():
            field_group = QWidget()
            column = QVBoxLayout(field_group)
            column.setContentsMargins(0, 0, 0, 0)
            row = QHBoxLayout()
            field = QLineEdit()
            field.setMaxLength(32)
            field.setAccessibleName(title + ' HEX')
            field.setPlaceholderText('#RRGGBB')
            field.setMinimumWidth(100)
            row.addWidget(field, 1)
            button = QPushButton(self.tr_text('색 선택', 'Choose'))
            button.setAccessibleName(title + ' ' + self.tr_text('선택', 'picker'))
            button.clicked.connect(lambda checked=False, name=key: self.choose_color(name))
            row.addWidget(button)
            column.addLayout(row)
            error = QLabel()
            error.setWordWrap(True)
            column.addWidget(error)
            self.fields[key], self.field_errors[key], self.color_buttons[key] = field, error, button
            field.textChanged.connect(self.update_preview)
            label = QLabel(title)
            label.setWordWrap(True)
            label.setBuddy(field)
            form.addRow(label, field_group)
        body.addLayout(form)
        self.glow_slider = QSlider(Qt.Orientation.Horizontal)
        self.glow_slider.setRange(0, 100)
        self.glow_slider.setAccessibleName(self.tr_text('조명 강도', 'Ambient light strength'))
        self.glow_value = QLabel()
        body.addWidget(self.glow_value)
        body.addWidget(self.glow_slider)
        self.glow_slider.valueChanged.connect(self.update_preview)
        self.preview_mode = QComboBox()
        self.preview_mode.addItem(self.tr_text('다크 미리보기', 'Dark preview'), 'dark')
        self.preview_mode.addItem(self.tr_text('라이트 미리보기', 'Light preview'), 'light')
        self.preview_mode.setAccessibleName(self.tr_text('미리보기 모드', 'Preview mode'))
        body.addWidget(self.preview_mode)
        self.preview_mode.currentIndexChanged.connect(self.update_preview)
        self.preview = QFrame()
        self.preview.setObjectName('appearancePreview')
        preview_layout = QVBoxLayout(self.preview)
        preview_layout.setContentsMargins(18, 18, 18, 18)
        self.preview_card = QFrame()
        self.preview_card.setObjectName('appearanceCard')
        card = QVBoxLayout(self.preview_card)
        self.preview_title = QLabel(self.tr_text('오늘의 작업', 'Today’s work'))
        self.preview_title.setObjectName('previewTitle')
        self.preview_description = QLabel(self.tr_text('선택한 색상으로 읽기 편한 화면을 만듭니다.',
                                                       'Reading colors adapt while the original accent is kept.'))
        self.preview_description.setObjectName('previewMuted')
        self.preview_description.setWordWrap(True)
        card.addWidget(self.preview_title)
        card.addWidget(self.preview_description)
        selected = QPushButton(self.tr_text('선택됨', 'Selected'))
        selected.setObjectName('previewSelected')
        selected.setCheckable(True)
        selected.setChecked(True)
        card.addWidget(selected)
        disabled = QPushButton(self.tr_text('사용할 수 없음', 'Unavailable'))
        disabled.setObjectName('previewDisabled')
        disabled.setEnabled(False)
        card.addWidget(disabled)
        self.preview_error = QLabel(self.tr_text('오류 예시 · 다시 확인해 주세요.',
                                                'Error example · Please check again.'))
        self.preview_error.setObjectName('previewError')
        self.preview_error.setWordWrap(True)
        card.addWidget(self.preview_error)
        preview_layout.addWidget(self.preview_card)
        body.addWidget(self.preview)
        note = QLabel(self.tr_text(
            '입력한 원색은 그대로 저장합니다. 읽기용 색은 대비에 맞춰 보정합니다. 날짜 조형의 색은 바꾸지 않습니다.',
            'Your original colors are saved. Reading colors are adjusted for contrast. Daily sculpture colors stay unchanged.'))
        note.setWordWrap(True)
        body.addWidget(note)
        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        outer.addWidget(self.error_label)
        self.footer = QWidget()
        footer = QHBoxLayout(self.footer)
        footer.setContentsMargins(0, 0, 0, 0)
        self.reset_button = QPushButton(self.tr_text('기본값 복원', 'Restore defaults'))
        self.cancel_button = QPushButton(self.tr_text('취소', 'Cancel'))
        self.apply_button = QPushButton(self.tr_text('적용', 'Apply'))
        footer.addWidget(self.reset_button)
        footer.addStretch(1)
        footer.addWidget(self.cancel_button)
        footer.addWidget(self.apply_button)
        outer.addWidget(self.footer)
        self.reset_button.clicked.connect(lambda: self.load_values(normalize_config(None)))
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.apply_candidate)
        self.preset_combo.currentIndexChanged.connect(self.select_preset)
        self.load_values(self.original_config)

    def tr_text(self, ko, en):
        return en if self.language == 'en' else ko

    def load_values(self, value):
        value = normalize_config(value)
        self._loading = True
        try:
            for key, field in self.fields.items():
                field.setText(value[key])
            self.glow_slider.setValue(value['glow'])
            matching = next((i for i, row in enumerate(PRESETS) if normalize_config(row['values']) == value), -1)
            self.preset_combo.blockSignals(True)
            self.preset_combo.setCurrentIndex(matching)
            self.preset_combo.blockSignals(False)
        finally:
            self._loading = False
        self.error_label.clear()
        self.update_preview()

    def select_preset(self, index):
        if 0 <= index < len(PRESETS):
            self.load_values(PRESETS[index]['values'])

    def candidate(self):
        return normalize_config(dict({key: field.text() for key, field in self.fields.items()},
                                     glow=self.glow_slider.value()))

    def choose_color(self, key):
        if key not in self.fields:
            raise ValueError('지원하지 않는 색상 필드입니다.')
        try:
            initial = _hex(self.fields[key].text())
        except ValueError:
            initial = dict(_DEFAULT_VALUES)[key]
        chosen = QColorDialog.getColor(QColor(initial), self, self._labels[key],
                                       QColorDialog.ColorDialogOption.DontUseNativeDialog)
        if chosen.isValid():
            self.fields[key].setText(chosen.name().upper())

    def update_preview(self, *_):
        if self._loading:
            return
        valid = True
        for key, field in self.fields.items():
            try:
                _hex(field.text())
                self.field_errors[key].clear()
                field.setProperty('appearanceInvalid', False)
            except ValueError:
                valid = False
                self.field_errors[key].setText(self.tr_text('6자리 HEX를 입력해 주세요.', 'Enter a six-digit HEX color.'))
                field.setProperty('appearanceInvalid', True)
        self.apply_button.setEnabled(valid)
        self.glow_value.setText(self.tr_text('조명 강도', 'Ambient light strength') + f' · {self.glow_slider.value()} / 100')
        if not valid:
            return
        colors = palette_for(self.preview_mode.currentData(), self.candidate())
        self.preview.setStyleSheet(
            '#appearancePreview {background:' + colors['bg'] + ';border:1px solid ' + colors['border'] + ';border-radius:12px;}'
            '#appearanceCard {background:' + colors['surface'] + ';border:1px solid ' + colors['focus'] + ';border-radius:9px;}'
            '#appearancePreview QLabel {background:transparent;color:' + colors['text'] + ';}'
            '#appearancePreview #previewMuted {color:' + colors['muted'] + ';}'
            '#appearancePreview #previewError {color:' + colors['error'] + ';}'
            '#appearancePreview QPushButton {padding:7px;border:1px solid ' + colors['border'] + ';border-radius:6px;}'
            '#appearancePreview #previewSelected {background:' + colors['selected'] + ';color:' + colors['text'] + ';}'
            '#appearancePreview #previewDisabled {background:' + colors['raised'] + ';color:' + colors['disabled'] + ';}'
        )
        self.preview_card.setGraphicsEffect(None)
        if colors['glow']:
            effect = QGraphicsDropShadowEffect(self.preview_card)
            light = QColor(colors['accent_raw'])
            light.setAlpha(round(140 * colors['glow'] / 100))
            effect.setColor(light)
            effect.setOffset(0, 0)
            effect.setBlurRadius(24)
            self.preview_card.setGraphicsEffect(effect)

    def apply_candidate(self):
        try:
            candidate = self.candidate()
            result = self.on_apply(dict(candidate))
            if result is False:
                raise ValueError(self.tr_text('설정을 적용하지 못했습니다.', 'Could not apply these settings.'))
        except Exception as error:
            self.error_label.setText(self.tr_text('적용 실패: ', 'Apply failed: ') + str(error))
            return
        self.applied_config = dict(candidate)
        self.accept()
