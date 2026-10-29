"""앱이 소유하는 모든 화면과 대화상자의 공통 무채색 테마입니다."""
from PySide6.QtCore import QEvent, QObject, QTimer, QTranslator, Qt
from PySide6.QtGui import QColor, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QFileDialog, QHeaderView, QProxyStyle, QStyleFactory, QTreeView


STYLE = '''
QWidget {background:#141414;color:#ededed;font-weight:700;}
QDialog {background:#141414;}
QLabel {background:transparent;border:none;}
QFrame#eventCard {background:#1c1c1c;border:1px solid #404040;border-radius:12px;}
QLineEdit,QPlainTextEdit,QListWidget,QTreeView,QComboBox {background:#191919;border:1px solid #4a4a4a;border-radius:6px;padding:8px;selection-background-color:#565656;selection-color:#ffffff;}
QLineEdit,QComboBox {min-height:18px;}
QLineEdit:focus,QPlainTextEdit:focus,QComboBox:focus {border:1px solid #c0c0c0;}
QTreeView::item {min-height:24px;padding:3px;}
QListWidget::item {padding:12px 6px;border-bottom:1px solid #333333;}
QListWidget::item:selected {background:#3d3d3d;color:#ffffff;}
QPushButton,QToolButton {background:#303030;color:#f0f0f0;border:1px solid #626262;border-radius:6px;padding:8px 12px;min-height:18px;}
QPushButton:hover,QToolButton:hover {background:#454545;border-color:#d5d5d5;}
QPushButton:pressed,QToolButton:pressed {background:#565656;}
QPushButton:disabled {color:#858585;background:#202020;border-color:#383838;}
QTabWidget::pane {border:1px solid #3b3b3b;border-radius:6px;}
QTabBar::tab {padding:10px 15px;background:#202020;color:#aaaaaa;}
QTabBar::tab:selected {color:#ffffff;background:#303030;border-bottom:2px solid #eeeeee;}
QSplitter::handle {background:#414141;}
QCheckBox {spacing:9px;background:transparent;padding:4px;}
QCheckBox::indicator {width:17px;height:17px;border:1px solid #858585;border-radius:4px;background:#202020;}
QCheckBox::indicator:checked {background:#ededed;border:4px solid #555555;}
QProgressBar {border:1px solid #555555;border-radius:4px;text-align:center;background:#191919;color:#ffffff;}
QProgressBar::chunk {background:#626262;}
QScrollBar:vertical {background:#202020;width:10px;margin:0;}
QScrollBar::handle:vertical {background:#656565;min-height:24px;border-radius:5px;}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {height:0;}
QScrollBar:horizontal {background:#202020;height:10px;}
QScrollBar::handle:horizontal {background:#656565;min-width:24px;border-radius:5px;}
QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal {width:0;}
QMenu {background:#202020;border:1px solid #696969;padding:6px;}
QMenu::item {padding:9px 24px;border-radius:4px;}
QMenu::item:selected {background:#484848;color:#ffffff;}
QMenu::separator {height:1px;background:#555555;margin:5px;}
QToolTip {background:#202020;color:#ffffff;border:1px solid #999999;padding:7px;}
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
                    source.setPixelColor(x, y, QColor(level, level, level, color.alpha()))
            result.addPixmap(QPixmap.fromImage(source), QIcon.Mode.Normal, QIcon.State.Off)
        self.icons[standard_icon] = result
        return result


class KoreanDialogs(QTranslator):
    """별도 Qt 번역 패키지가 없는 배포에서도 기본 파일 선택 문구를 번역합니다."""
    labels = {'Look in:': '위치:', 'File name:': '파일 이름:', 'Files of type:': '파일 형식:',
              'Open': '열기', '&Open': '열기', 'Save': '저장', '&Save': '저장', 'Cancel': '취소',
              '&Cancel': '취소', 'OK': '확인', '&OK': '확인', 'Yes': '예', '&Yes': '예',
              'No': '아니요', '&No': '아니요', 'Name': '이름', 'Size': '크기', 'Type': '종류',
              'Date Modified': '수정 시각', 'File Folder': '파일 폴더', 'Folder': '폴더',
              'Directory:': '폴더:', 'Choose': '선택', 'Directories': '폴더',
              'My Computer': '내 컴퓨터', 'Computer': '컴퓨터', 'Back': '뒤로', 'Forward': '앞으로',
              'Parent Directory': '상위 폴더', 'Create New Folder': '새 폴더 만들기',
              'List View': '목록 보기', 'Detail View': '자세히 보기', 'Show ': '표시 '}

    def translate(self, context, source_text, disambiguation=None, n=-1):
        return self.labels.get(source_text.replace('&', ''), source_text)


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
            dialog.setLabelText(label, text)
        dialog.setLabelText(QFileDialog.DialogLabel.Accept,
                            '선택' if dialog.fileMode() == QFileDialog.FileMode.Directory else
                            '저장' if dialog.acceptMode() == QFileDialog.AcceptMode.AcceptSave else '열기')
        for tree in dialog.findChildren(QTreeView):
            if tree.model() and tree.model().columnCount() >= 4:
                tree.header().setMinimumSectionSize(60)
                tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
                for column, width in enumerate((260, 70, 100, 180)):
                    tree.header().resizeSection(column, width)


def apply_theme():
    app = QApplication.instance()
    if app.property('orbit_monochrome'):
        return
    app.setStyle(MonochromeStyle())
    app.styleHints().setColorScheme(Qt.ColorScheme.Dark)
    translator = KoreanDialogs(app)
    app.installTranslator(translator)
    app.orbit_translator = translator
    dialog_layout = DialogLayout(app)
    app.installEventFilter(dialog_layout)
    app.orbit_dialog_layout = dialog_layout
    palette = QPalette()
    for role, value in ((QPalette.ColorRole.Window, 20), (QPalette.ColorRole.WindowText, 237),
                        (QPalette.ColorRole.Base, 25), (QPalette.ColorRole.AlternateBase, 35),
                        (QPalette.ColorRole.Text, 237), (QPalette.ColorRole.Button, 48),
                        (QPalette.ColorRole.ButtonText, 240), (QPalette.ColorRole.Highlight, 80),
                        (QPalette.ColorRole.HighlightedText, 255), (QPalette.ColorRole.ToolTipBase, 32),
                        (QPalette.ColorRole.ToolTipText, 255), (QPalette.ColorRole.Link, 220)):
        palette.setColor(role, QColor(value, value, value))
    app.setPalette(palette)
    app.setStyleSheet(STYLE)
    app.setProperty('orbit_monochrome', True)
