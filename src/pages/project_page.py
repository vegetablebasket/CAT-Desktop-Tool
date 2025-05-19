# pages/project_page.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class ProjectPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📁 这是项目管理页面"))
        self.setLayout(layout)