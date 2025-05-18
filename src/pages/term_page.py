from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class TermPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📚 术语库页面"))
        self.setLayout(layout)