from PyQt6.QtWidgets import (QLineEdit, QFileDialog, QTextEdit, QComboBox, QListWidget,
                            QApplication,QLabel,QVBoxLayout, QHBoxLayout, QDialog, QPushButton)
from PyQt6.QtGui import QFont
import sys
from PyQt6.QtCore import Qt
class Createproject(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("创建新项目")
        self.setFixedSize(500, 400)
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout()


        self.project_name_input=QLineEdit()
        self.project_name_input.setPlaceholderText("请输入项目名")

        create_button=QPushButton("创建项目")
        create_button.clicked.connect(self.create_project)

        self.project_name_input.setFont(QFont("Arial", 18))  # 设置字体和大小
        create_button.setFont(QFont("Arial", 18))  # 设置按钮的字体

        create_button.setStyleSheet("background-color: #55555; color: white; min-width: 150px;")  # 设置按钮背景和文字颜色

        layout.addWidget(QLabel("项目名称："), alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.project_name_input)
        layout.addWidget(create_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def create_project(self):
        project_name = self.project_name_input.text()
        if project_name:
            print(f"创建新项目：{project_name}")
            self.accept()  # 关闭对话框
        else:
            print("项目名称不能为空！")


if __name__ == "__main__":
    app = QApplication([])
    window = Createproject()
    window.show()
    app.exec()