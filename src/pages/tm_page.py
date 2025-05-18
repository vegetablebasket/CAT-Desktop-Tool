from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class TMPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🧠 记忆库页面"))
        self.setLayout(layout)