import sys
import os

# 将项目根目录加入sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from src.temp_tm_manage翻译记忆库 import temp_TM_item_show


class TMPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        # 创建 temp_TM_item_show 的 UI 窗口作为子控件
        self.temp_ui =  temp_TM_item_show.TM_items_show()
        layout.addWidget(self.temp_ui)
        self.setLayout(layout)

        self.setWindowTitle("TM Page")
        self.resize(800, 600)


