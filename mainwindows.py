import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem, QPushButton, QLabel
)
from PyQt6.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAT-Desktop-Tool")
        self.setMinimumSize(800, 500)
        self.setup_ui()

    def setup_ui(self):
        # 创建主水平布局
        main_layout = QHBoxLayout(self)

        # 左侧面板：用于显示最近项目列表
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setStyleSheet("background-color: #2D2D2D;")

        # 搜索栏：输入搜索文本
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("打开最近的项目")
        search_edit.setStyleSheet("background-color: #404040; color: white; border: none; padding: 8px;")
        left_layout.addWidget(search_edit)

        # 最近项目列表
        recent_list = QListWidget()
        recent_list.setStyleSheet("background-color: #2D2D2D; color: white; border: none;")
        # 示例项目项（可替换为实际项目）
        for project_name in ["项目A", "项目B", "项目C"]:
            item = QListWidgetItem(project_name)
            recent_list.addItem(item)
        left_layout.addWidget(recent_list)

        # 右侧面板：用于功能按钮
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_panel.setStyleSheet("background-color: #333; padding: 20px;")

        # 通用按钮样式
        button_style = """
        QPushButton {
            background-color: #333;
            color: white;
            border: none;
            padding: 10px;
            margin: 5px 0;
            text-align: left;
            font-size: 14px;
            min-width: 200px;
        }
        QPushButton:hover {
            background-color: #666;
        }
        """

        # 添加功能按钮
        buttons = [
            ("打开项目", self.open_project),
            ("创建新项目", self.create_project),
            ("记忆库管理", self.manage_memory),
            ("术语库管理", self.manage_terminology),
            ("系统设置", self.system_settings)
        ]

        for label, slot in buttons:
            btn = QPushButton(label)
            btn.setStyleSheet(button_style)
            btn.clicked.connect(slot)  # 预设空槽函数供后续实现
            right_layout.addWidget(btn)

        # 添加左右面板到主布局
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)

        # 设置窗口整体背景
        self.setStyleSheet("background-color: #2D2D2D;")

    # 以下为功能按钮的占位方法（后续可扩展）
    def open_project(self):
        print("打开项目")

    def create_project(self):
        print("创建新项目")

    def manage_memory(self):
        print("记忆库管理")

    def manage_terminology(self):
        print("术语库管理")

    def system_settings(self):
        print("系统设置")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
