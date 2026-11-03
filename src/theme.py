"""앱이 소유하는 화면과 대화상자의 부드러운 청록 테마입니다."""
from i18n import translate as t, get_language
from PySide6.QtCore import QEvent, QObject, QTimer, QTranslator, Qt
from PySide6.QtGui import QColor, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QFileDialog, QHeaderView, QProxyStyle, QStyleFactory, QTreeView


STYLE = '''
QWidget {background:#f3faf7;color:#193c36;font-family:"NanumGothic";font-weight:700;font-size:13px;}
QDialog {background:#f3faf7;}
QFrame#usagePanel {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #e4f5ed,stop:0.55 #f6fffb,stop:1 #ffffff);border:1px solid #c2dbd0;border-radius:20px;}
QLabel {background:transparent;border:none;}
QFrame#observatoryHero {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #dbf6e9,stop:1 #fbfffd);border:1px solid #c8e5d7;border-radius:22px;}
QLabel#currentTask {font-size:23px;color:#143e30;}
QPushButton:checked {background:#cbf0dd;border-color:#269b6c;color:#114a32;}
QFrame#eventCard {background:#ffffff;border:1px solid #d0e5db;border-radius:16px;}
QLineEdit,QPlainTextEdit,QTreeView,QComboBox {background:#ffffff;border:1px solid #c1d9cf;border-radius:10px;padding:10px;selection-background-color:#caeddc;selection-color:#ffffff;}
QLineEdit,QComboBox {min-height:22px;}
QLineEdit:focus,QPlainTextEdit:focus,QComboBox:focus {border:1px solid #9bdbc9;}
QTreeView::item {min-height:24px;padding:3px;}
QListWidget {background:#ffffff;border:1px solid #d0e5db;border-radius:14px;padding:10px;outline:0;}
QListWidget::item {padding:17px 12px;border-bottom:1px solid #e3eee9;border-radius:10px;color:#45675b;}
QListWidget::item:selected {background:#d9f6e8;color:#355c50;border-left:3px solid #168565;}
QListWidget::item:hover {background:#e5f7ee;}
QPushButton,QToolButton {background:#eaf7f0;color:#193c36;border:1px solid #bfdacf;border-radius:10px;padding:8px 12px;min-height:18px;}
QPushButton:hover,QToolButton:hover {background:#d6f2e3;border-color:#88b9bd;}
QPushButton:pressed,QToolButton:pressed {background:#c0e6d5;}
QPushButton:disabled {color:#355c50;background:#f2f5f3;border-color:#344c58;}
QPushButton#disclosure {background:#eff8f3;border:1px solid #3a5560;text-align:left;padding:14px 12px;}
QTabWidget::pane {border:0;border-top:1px solid #d3e8de;}
QTabBar::tab {padding:16px 17px;background:transparent;color:#476a5d;border-bottom:2px solid transparent;font-size:15px;}
QTabBar::tab:selected {font-weight:600;background:#dcf5e8;color:#355c50;border-bottom:2px solid #168565;border-top-left-radius:10px;border-top-right-radius:10px;}
QTabBar::tab:hover {color:#355c50;}
QSplitter::handle {background:transparent;width:1px;}
QScrollArea {border:0;background:transparent;}
QCheckBox {spacing:10px;background:transparent;padding:7px;}
QCheckBox::indicator {width:18px;height:18px;border:1px solid #829da7;border-radius:5px;background:#243d48;}
QCheckBox::indicator:checked {background:#a3dfcd;border:4px solid #426d69;}
QProgressBar {border:0;border-radius:6px;text-align:center;background:#dcece4;color:#193c36;}
QProgressBar::chunk {background:#1aa676;border-radius:6px;}
QScrollBar:vertical {background:#19313b;width:8px;margin:0;}
QScrollBar::handle:vertical {background:#4c6a77;min-height:28px;border-radius:4px;}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {height:0;}
QScrollBar:horizontal {background:#213b47;height:8px;}
QScrollBar::handle:horizontal {background:#65818c;min-width:24px;border-radius:4px;}
QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal {width:0;}
QMenu {background:#ffffff;border:1px solid #bed9cc;padding:7px;}
QMenu::item {padding:10px 26px;border-radius:7px;}
QMenu::item:selected {background:#dcf6e9;color:#355c50;}
QMenu::separator {height:1px;background:#3b5662;margin:5px;}
QToolTip {background:#fafffc;color:#23483a;border:1px solid #a4c9b5;padding:8px;}
QMessageBox QLabel {min-width:300px;}
'''


class MonochromeStyle(QProxyStyle):
    """파일·메시지 등의 표준 아이콘도 앱 안에서는 무채색으로 만듭니다."""
    def __init__(self):
        super().__init__(QStyleFactory.create('Fusion'))
        self.icons = {}

    def standardIcon(self, standard_icon, option=None, widget=None):
        if standard_icon in self.icons:
            return self.icons[standard_icon]
        original = super().standardIcon(standard_icon, option, widget)
        result = QIcon()
        for size in (16, 24, 32, 48, 64):
            source = original.pixmap(size, size).toImage()
            if source.isNull():
                continue
            for y in range(source.height()):
                for x in range(source.width()):
                    color = source.pixelColor(x, y)
                    level = round(.299 * color.red() + .587 * color.green() + .114 * color.blue())
                    if effective_theme()=='dark':level=max(190,level)
                    source.setPixelColor(x, y, QColor(level, level, level, color.alpha()))
            result.addPixmap(QPixmap.fromImage(source), QIcon.Mode.Normal, QIcon.State.Off)
        self.icons[standard_icon] = result
        return result


class KoreanDialogs(QTranslator):
    """별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다."""
    labels = {'All Files (*)':'모든 파일 (*)', 'All Files':'모든 파일', 'Look in:': '위치:', 'File name:': '파일 이름:', 'Files of type:': '파일 형식:',
              'Open': '열기', '&Open': '열기', 'Save': '저장', '&Save': '저장', 'Cancel': '취소',
              '&Cancel': '취소', 'OK': '확인', '&OK': '확인', 'Yes': '예', '&Yes': '예',
              'No': '아니요', '&No': '아니요', 'Name': '이름', 'Size': '크기', 'Type': '종류',
              'Date Modified': '수정 시각', 'File Folder': '파일 폴더', 'Folder': '폴더',
              'Directory:': '폴더:', 'Choose': '선택', 'Directories': '폴더',
              'My Computer': '내 컴퓨터', 'Computer': '컴퓨터', 'Back': '뒤로', 'Forward': '앞으로',
              'Parent Directory': '상위 폴더', 'Create New Folder': '새 폴더 만들기',
              'List View': '목록 보기', 'Detail View': '자세히 보기', 'Show ': '표시 '}

    def translate(self, context, source_text, disambiguation=None, n=-1):
        return self.labels.get(source_text.replace('&', ''), source_text) if get_language() == 'ko' else source_text


class DialogLayout(QObject):
    """앱 파일 선택창의 이름 열과 한글 버튼에 충분한 공간을 확보합니다."""
    def eventFilter(self, watched, event):
        if isinstance(watched, QFileDialog) and event.type() == QEvent.Type.Show:
            QTimer.singleShot(0, lambda: self.prepare(watched))
        return False

    @staticmethod
    def prepare(dialog):
        dialog.resize(max(820, dialog.width()), max(560, dialog.height()))
        dialog.setViewMode(QFileDialog.ViewMode.Detail)
        for label, text in ((QFileDialog.DialogLabel.LookIn, '위치:'),
                            (QFileDialog.DialogLabel.FileName, '폴더:' if dialog.fileMode() == QFileDialog.FileMode.Directory else '파일 이름:'),
                            (QFileDialog.DialogLabel.FileType, '파일 형식:'),
                            (QFileDialog.DialogLabel.Reject, '취소')):
            dialog.setLabelText(label, t(text))
        dialog.setLabelText(QFileDialog.DialogLabel.Accept,
                            t('선택') if dialog.fileMode() == QFileDialog.FileMode.Directory else
                            t('저장') if dialog.acceptMode() == QFileDialog.AcceptMode.AcceptSave else t('열기'))
        for tree in dialog.findChildren(QTreeView):
            if tree.model() and tree.model().columnCount() >= 4:
                tree.header().setMinimumSectionSize(60)
                tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
                for column, width in enumerate((260, 70, 100, 180)):
                    
                    if column:tree.header().setSectionResizeMode(column,QHeaderView.ResizeMode.ResizeToContents)


# 의미색은 앱 소유 화면 전체에서 함께 바뀌며 날짜별 투명 조형에는 적용하지 않습니다.
PALETTES = {
    'light': dict(bg='#f3f8f6', surface='#ffffff', raised='#eaf5ef', text='#193c36', muted='#49665d', border='#bfd5cc', accent='#157f5e', selected='#d8f1e4', focus='#168b66', track='#e1ece6'),
    'dark': dict(bg='#121d1b', surface='#1b2b27', raised='#233b33', text='#e9f5ee', muted='#b1c9bd', border='#3e5a4e', accent='#83dcb1', selected='#294d3e', focus='#83dcb1', track='#30483c'),
}


def normalize_theme_mode(value):
    value = str(value or 'system').strip().lower()
    return {'자동':'system', 'auto':'system', 'automatic':'system', 'default':'system', '시스템':'system', '라이트':'light', '다크':'dark'}.get(value, value if value in ('light','dark','system') else 'system')


def effective_theme():
    app = QApplication.instance()
    return (app.property('orbit_effective_theme') if app else None) or 'light'


def colors():
    return PALETTES[effective_theme()]


def theme_style(css):
    """이전 지역 스타일의 색을 의미색으로 바꾸되 크기·간격은 보존합니다."""
    import re
    c = colors()
    foreground = {'#55736b', '#355c50', '#49615b', '#45675b', '#476a5d', '#55736b', '#b5c8d4'}
    def color(match):
        value = match.group(0).lower()
        if value in foreground: return c['muted']
        if value in ('#ffffff','#f9fffc','#fbfffe','#fbfffd','#fafffc'): return c['surface']
        if value in ('#f3faf7','#f2f5f3'): return c['bg']
        if value in ('#d4f3e7','#e0f4e9','#385064','#caeddc','#cbf0dd','#dcf5e8','#d9f6e8'): return c['selected']
        q = QColor(value)
        if q.lightnessF() > .72: return c['border'] if q.lightnessF() < .88 else c['raised']
        if value in ('#193c36','#183c36','#23453f','#23433f','#193a37','#143e30','#114a32','#355c50'): return c['text']
        return q.lighter(170).name() if effective_theme()=='dark' else value
    result=re.sub(r'#[0-9a-fA-F]{6}', color, css)
    return re.sub(r'selection-color:#[0-9a-fA-F]{6}', 'selection-color:'+c['text'], result)


def unscaled_font_size(widget):
    base=widget.property('baseFont31')
    if base is None:
        # 새 자식이 이미 확대된 부모 글꼴을 상속했으면 부모의 원래 크기를 사용합니다.
        parent=widget.parentWidget()
        if not widget.testAttribute(Qt.WidgetAttribute.WA_SetFont):
            while parent is not None and base is None:
                base=parent.property('baseFont31');parent=parent.parentWidget()
        if base is None:base=max(13,widget.font().pixelSize())
        widget.setProperty('baseFont31',base)
    return base


def set_ui_style(widget, css):
    widget.setProperty('orbit_style_source', css)
    # 배율 변환 결과를 원문에 되쓰지 않아 동적 변경과 반복 배율을 보존합니다.
    owner=widget
    scale=None
    while owner is not None and scale is None:
        scale=owner.property('orbit_text_scale31')
        owner=owner.parentWidget()
    styled=css
    if scale is not None:
        import re
        styled=re.sub(r'font-size:(\d+)px',lambda match:'font-size:'+str(round(int(match[1])*scale))+'px',css)
        if not re.search(r'font-size:',styled):
            base=unscaled_font_size(widget)
            styled+=';font-size:'+str(round(base*scale))+'px;font-weight:700;'
    rendered=theme_style(styled)
    if widget.styleSheet()!=rendered:
        widget.setStyleSheet(rendered)


def themed_stylesheet():
    c = colors()
    style = theme_style(STYLE)
    style += """
    QWidget {font-weight:700;}
    QComboBox {padding:5px 32px 5px 10px;min-height:26px;border:1px solid BORDER;border-radius:8px;background:SURFACE;color:TEXT;}
    QComboBox:hover {border-color:FOCUS;}
    QComboBox:focus {border:2px solid FOCUS;padding:4px 31px 4px 9px;}
    QComboBox::drop-down {subcontrol-origin:padding;subcontrol-position:top right;width:28px;border:0;background:transparent;}
    QComboBox::down-arrow {image:none;width:0;height:0;}
    QComboBox QAbstractItemView {background:SURFACE;color:TEXT;border:1px solid BORDER;outline:0;selection-background-color:SELECTED;selection-color:TEXT;padding:4px;}
    QComboBox QAbstractItemView::item {min-height:28px;padding:5px 10px;}
    QFrame#controlsBar,QFrame#observationCard,QFrame#replayBar {background:SURFACE;border:1px solid BORDER;border-radius:12px;}
    QFrame#observatoryHero {background:BG;border:1px solid BORDER;border-radius:16px;}
    QLabel#currentTask {color:TEXT;font-size:22px;}
    QLabel#sectionCaption {color:MUTED;font-size:12px;}
    QPushButton:focus,QToolButton:focus {border:2px solid FOCUS;}
    QListWidget::item:selected {background:SELECTED;color:TEXT;}
    QMenu::section {color:MUTED;padding:8px 12px;}
    QFrame#navigationSurface {background:SURFACE;border:1px solid BORDER;border-radius:12px;}
    QFrame#navigationSurface QPushButton {background:transparent;border:0;text-align:left;padding:10px 12px;border-radius:8px;}
    QFrame#navigationSurface QPushButton:checked {background:SELECTED;color:TEXT;border-left:3px solid FOCUS;}
    QFrame#navigationSurface QPushButton:hover {background:RAISED;}

    QAbstractItemView::item:selected {background:SELECTED;color:TEXT;}
    QCheckBox::indicator {background:SURFACE;border:1px solid MUTED;}
    QCheckBox::indicator:checked {background:SELECTED;border:3px solid FOCUS;}
    QSlider::groove:horizontal {height:4px;background:BORDER;border-radius:2px;}
    QSlider::handle:horizontal {background:FOCUS;border:1px solid BORDER;width:12px;margin:-5px 0;border-radius:6px;}
    QTabBar::tab:selected {font-weight:700;}
    QScrollBar:vertical,QScrollBar:horizontal {background:BG;}
    QScrollBar::handle:vertical,QScrollBar::handle:horizontal {background:BORDER;}
    """
    for token,key in [('RAISED','raised'),('BORDER','border'),('SURFACE','surface'),('SELECTED','selected'),('MUTED','muted'),('FOCUS','focus'),('TEXT','text'),('BG','bg')]:style=style.replace(token,c[key])
    return style


def _apply_colors(scheme=None):
    app = QApplication.instance()
    mode = app.property('orbit_theme_mode') or 'system'
    resolved = mode if mode!='system' else ('dark' if (scheme or app.styleHints().colorScheme())==Qt.ColorScheme.Dark else 'light')
    app.setProperty('orbit_effective_theme', resolved)
    style=app.style()
    if hasattr(style,'icons'):style.icons.clear()
    c = colors();palette=QPalette()
    roles={'Window':'bg','WindowText':'text','Base':'surface','AlternateBase':'raised','Text':'text','Button':'raised','ButtonText':'text','Highlight':'selected','HighlightedText':'text','ToolTipBase':'surface','ToolTipText':'text','Link':'accent','PlaceholderText':'muted'}
    for role,key in roles.items():palette.setColor(getattr(QPalette.ColorRole,role),QColor(c[key]))
    app.setPalette(palette);app.setStyleSheet(themed_stylesheet())
    # 위젯별 원본 스타일은 누적 변환하지 않고 매번 원문에서 다시 계산합니다.
    for widget in app.allWidgets():
        original=widget.property('orbit_style_source')
        if original is not None:set_ui_style(widget,original)
        widget.update()


def _system_changed(scheme):
    if QApplication.instance().property('orbit_theme_mode')=='system':_apply_colors(scheme)


def apply_theme(mode=None):
    app=QApplication.instance()
    selected=normalize_theme_mode(mode if mode is not None else app.property('orbit_theme_mode'))
    resolved=selected if selected!='system' else ('dark' if app.styleHints().colorScheme()==Qt.ColorScheme.Dark else 'light')
    if app.property('orbit_monochrome') and app.property('orbit_theme_mode')==selected and effective_theme()==resolved:return
    if not app.property('orbit_monochrome'):
        app.setStyle(MonochromeStyle())
        translator=KoreanDialogs(app);app.installTranslator(translator);app.orbit_translator=translator
        layout=DialogLayout(app);app.installEventFilter(layout);app.orbit_dialog_layout=layout
        app.styleHints().colorSchemeChanged.connect(_system_changed)
        app.setProperty('orbit_monochrome',True)
    from typography import app_font
    app.setFont(app_font())
    selected=normalize_theme_mode(mode if mode is not None else app.property('orbit_theme_mode'))
    app.setProperty('orbit_theme_mode',selected)
    app.styleHints().setColorScheme({'light':Qt.ColorScheme.Light,'dark':Qt.ColorScheme.Dark,'system':Qt.ColorScheme.Unknown}[selected])
    _apply_colors()
