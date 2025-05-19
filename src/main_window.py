# main_window.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QAction
from pages.project_page import ProjectPage
from pages.document_page import DocumentPage
from pages.translation_page import TranslationPage
from pages.term_page import TermPage
from pages.tm_page import TMPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAT 翻译工具")
        self.setGeometry(100, 100, 1000, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.pages = {
            "项目管理": ProjectPage(),
            "文档管理": DocumentPage(),
            "翻译编辑": TranslationPage(),
            "术语库管理": TermPage(),
            "记忆库管理": TMPage()
        }

        for page in self.pages.values():
            self.stack.addWidget(page)

        # 菜单栏构建
        menu = self.menuBar().addMenu("功能导航")
        for idx, (name, _) in enumerate(self.pages.items()):
            action = QAction(name, self)
            action.triggered.connect(lambda _, i=idx: self.stack.setCurrentIndex(i))
            menu.addAction(action)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())