# src/pages/document_page.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class DocumentPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📄 文档管理页面"))
        self.setLayout(layout)