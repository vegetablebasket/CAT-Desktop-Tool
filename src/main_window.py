# main_window.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QAction
from dao import document_dao
from pages.project_page import ProjectPage
from pages.document_page import DocumentPage
from pages.translation_page import TranslationPage
from pages.term_page import TermPage
from pages.tm_page import TMPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAT - 计算机辅助翻译系统")
        self.setGeometry(100, 100, 1000, 600)

        # 使用 QStackedWidget 管理不同的页面
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 初始化数据库
        self.init_database()

        # 初始化页面组件
        self.pages = {
            "项目管理": ProjectPage(),
            "文档管理": DocumentPage(),
            "翻译编辑": TranslationPage(),
            "术语库管理": TermPage(),
            "记忆库管理": TMPage()
        }

        # 将每个页面加入堆叠
        for page in self.pages.values():
            self.stack.addWidget(page)

        # 创建菜单栏
        menubar = self.menuBar()
        nav_menu = menubar.addMenu("功能导航")

        # 菜单项及其对应的页面切换
        for index, (label, page) in enumerate(self.pages.items()):
            action = QAction(label, self)
            action.triggered.connect(lambda _, idx=index: self.stack.setCurrentIndex(idx))
            nav_menu.addAction(action)

    def init_database(self):
        """初始化数据库：创建表格"""
        # 确保数据库表已经创建
        document_dao.init_doc_table()  # 初始化文档表
        document_dao.init_translation_fragments_table()  # 初始化翻译片段表

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())