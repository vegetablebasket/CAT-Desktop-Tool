from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class TranslationPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("✍ 翻译编辑页面"))
        self.setLayout(layout)


