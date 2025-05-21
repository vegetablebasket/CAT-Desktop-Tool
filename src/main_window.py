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
        self.resize(1200, 900)  # 建议宽1200像素，高900像素

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 先加载所有主页面
        self.project_page = ProjectPage(self)
        self.translation_page = TranslationPage()
        self.term_page = TermPage()
        self.tm_page = TMPage()
        self.pages = {
            "项目管理": self.project_page,
            "翻译编辑": self.translation_page,
            "术语库管理": self.term_page,
            "记忆库管理": self.tm_page
        }

        for page in self.pages.values():
            self.stack.addWidget(page)

        # 菜单栏
        menu = self.menuBar().addMenu("功能导航")
        for idx, (name, page) in enumerate(self.pages.items()):
            action = QAction(name, self)
            action.triggered.connect(lambda _, i=idx: self.stack.setCurrentIndex(i))
            menu.addAction(action)

    def show_document_page(self, project_id):
        """
        切换到文档管理页面，并传递project_id
        """
        # 每次都新建一个文档页面（保证刷新内容），并切换到它
        doc_page = DocumentPage(project_id, main_window=self)
        self.stack.addWidget(doc_page)
        self.stack.setCurrentWidget(doc_page)

    def show_translation_page(self, document_id):
        """
        切换到翻译编辑页面，并传递文档ID
        """
        page = TranslationPage(document_id)
        self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
