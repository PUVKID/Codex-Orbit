"""앱이 소유하는 화면과 대화상자의 부드러운 청록 테마입니다."""
from PySide6.QtCore import QEvent, QObject, QTimer, QTranslator, Qt
from PySide6.QtGui import QColor, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QFileDialog, QHeaderView, QProxyStyle, QStyleFactory, QTreeView


STYLE = '''
QWidget {background:#172d36;color:#edf4f4;font-weight:700;font-size:13px;}
QDialog {background:#142a33;}
QLabel {background:transparent;border:none;}
QFrame#eventCard {background:#1e3540;border:1px solid #344e5a;border-radius:16px;}
QLineEdit,QPlainTextEdit,QTreeView,QComboBox {background:#203842;border:1px solid #3a5662;border-radius:10px;padding:10px;selection-background-color:#436976;selection-color:#ffffff;}
QLineEdit,QComboBox {min-height:22px;}
QLineEdit:focus,QPlainTextEdit:focus,QComboBox:focus {border:1px solid #9bdbc9;}
QTreeView::item {min-height:24px;padding:3px;}
QListWidget {background:#1b333e;border:1px solid #324b56;border-radius:14px;padding:10px;outline:0;}
QListWidget::item {padding:17px 12px;border-bottom:1px solid #304a55;border-radius:10px;color:#b9cbd3;}
QListWidget::item:selected {background:#2d4955;color:#ffffff;border-left:3px solid #9adfc9;}
QListWidget::item:hover {background:#263f4a;}
QPushButton,QToolButton {background:#2b4551;color:#edf5f7;border:1px solid #46616d;border-radius:10px;padding:8px 12px;min-height:18px;}
QPushButton:hover,QToolButton:hover {background:#375763;border-color:#88b9bd;}
QPushButton:pressed,QToolButton:pressed {background:#436573;}
QPushButton:disabled {color:#8199a4;background:#203640;border-color:#344c58;}
QPushButton#disclosure {background:#203943;border:1px solid #3a5560;text-align:left;padding:14px 12px;}
QTabWidget::pane {border:0;border-top:1px solid #35505a;}
QTabBar::tab {padding:16px 17px;background:transparent;color:#a8beca;border-bottom:2px solid transparent;font-size:15px;}
QTabBar::tab:selected {background:#263f4b;color:#ffffff;border-bottom:2px solid #98dfd5;border-top-left-radius:10px;border-top-right-radius:10px;}
QTabBar::tab:hover {color:#d5f5ee;}
QSplitter::handle {background:transparent;width:1px;}
QScrollArea {border:0;background:transparent;}
QCheckBox {spacing:10px;background:transparent;padding:7px;}
QCheckBox::indicator {width:18px;height:18px;border:1px solid #829da7;border-radius:5px;background:#243d48;}
QCheckBox::indicator:checked {background:#a3dfcd;border:4px solid #426d69;}
QProgressBar {border:0;border-radius:6px;text-align:center;background:#304b57;color:#f4f8f9;}
QProgressBar::chunk {background:#78bdb3;border-radius:6px;}
QScrollBar:vertical {background:#19313b;width:8px;margin:0;}
QScrollBar::handle:vertical {background:#4c6a77;min-height:28px;border-radius:4px;}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical {height:0;}
QScrollBar:horizontal {background:#213b47;height:8px;}
QScrollBar::handle:horizontal {background:#65818c;min-width:24px;border-radius:4px;}
QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal {width:0;}
QMenu {background:#203a45;border:1px solid #526c77;padding:7px;}
QMenu::item {padding:10px 26px;border-radius:7px;}
QMenu::item:selected {background:#395967;color:#ffffff;}
QMenu::separator {height:1px;background:#3b5662;margin:5px;}
QToolTip {background:#294550;color:#f0f6f7;border:1px solid #627f8c;padding:8px;}
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
    for role, value in ((QPalette.ColorRole.Window, '#142a33'), (QPalette.ColorRole.Base, '#203842'),
                        (QPalette.ColorRole.Button, '#2b4551'), (QPalette.ColorRole.Highlight, '#436976'),
                        (QPalette.ColorRole.Link, '#a2e2d2')):
        palette.setColor(role, QColor(value))
    app.setPalette(palette)
    app.setStyleSheet(STYLE)
    app.setProperty('orbit_monochrome', True)
