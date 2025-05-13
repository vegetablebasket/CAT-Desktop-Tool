import sys
from langdetect import detect
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QListWidget, QPushButton, QLabel, QTextEdit, QSplitter, QStatusBar
)
from PyQt6.QtCore import Qt


class TranslateWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAT-Desktop-Tool")
        self.setMinimumSize(800, 500)
        self.setup_ui()

    def setup_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)

        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(30)
        main_layout.addWidget(self.status_bar)

        # 分割器布局
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧布局
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.project_input_label = QLabel("原文")
        self.project_input_text = QTextEdit()
        self.project_input_text.setPlaceholderText("请输入原文...")
        self.project_input_text.textChanged.connect(self.detect_language)  # 实时检测语言

        # 左侧按钮
        button_layout = QHBoxLayout()
        self.screenshot_button = QPushButton("截图")
        self.extract_button = QPushButton("取词")
        self.highlight_button = QPushButton("划词")
        button_layout.addWidget(self.screenshot_button)
        button_layout.addWidget(self.extract_button)
        button_layout.addWidget(self.highlight_button)

        left_layout.addWidget(self.project_input_label)
        left_layout.addWidget(self.project_input_text)
        left_layout.addLayout(button_layout)

        # 右侧布局
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.project_output_label = QLabel("译文")
        self.project_output_text = QTextEdit()
        self.project_output_text.setPlaceholderText("翻译结果将在这里显示...")
        self.project_output_text.setReadOnly(True)

        # 右侧按钮
        right_button_layout = QHBoxLayout()
        self.translate_button = QPushButton("翻译")
        self.clear_button = QPushButton("清空")
        self.translate_button.clicked.connect(self.translate_text)  # 翻译功能
        self.clear_button.clicked.connect(self.clear_text)  # 清空功能
        right_button_layout.addWidget(self.translate_button)
        right_button_layout.addWidget(self.clear_button)

        right_layout.addWidget(self.project_output_label)
        right_layout.addWidget(self.project_output_text)
        right_layout.addLayout(right_button_layout)

        # 添加左右布局到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])  # 设置初始比例

        # 添加分割器到主布局
        main_layout.addWidget(splitter)

    def detect_language(self):
        """
        实时检测输入文本的语言
        """
        text = self.project_input_text.toPlainText()
        if text.strip():
            try:
                lang = detect(text)
                self.status_bar.showMessage(f"检测到语言: {lang}")
            except Exception as e:
                self.status_bar.showMessage("无法检测语言")
        else:
            self.status_bar.clearMessage()

    def translate_text(self):
        input_text = self.project_input_text.toPlainText()
        if not input_text.strip():
            self.status_bar.showMessage("请输入原文后再翻译")
            return

        try:
            # 调用 Microsoft Translator API
            translated_text = self.translate_text_with_microsoft(input_text, target_language="zh")
            self.project_output_text.setText(translated_text)
            self.status_bar.showMessage("翻译完成")
        except Exception as e:
            self.status_bar.showMessage(f"翻译失败: {str(e)}")
    def clear_text(self):
        """
        清空输入和输出框
        """
        self.project_input_text.clear()
        self.project_output_text.clear()
        self.status_bar.clearMessage()

    def translate_text_with_microsoft(input_text, target_language="en"):
        """
        使用 Microsoft Translator API 翻译文本
        """
        # 替换为你的订阅密钥和终结点
        subscription_key = "YOUR_MICROSOFT_TRANSLATOR_KEY"
        endpoint = "https://api.cognitive.microsofttranslator.com/translate"

        # 请求头
        headers = {
            "Ocp-Apim-Subscription-Key": subscription_key,
            "Ocp-Apim-Subscription-Region": "YOUR_REGION",  # 替换为你的区域
            "Content-Type": "application/json"
        }

        # 请求参数
        params = {
            "api-version": "3.0",
            "to": target_language
        }

        # 请求体
        body = [{"text": input_text}]

        # 发送 POST 请求
        response = requests.post(endpoint, headers=headers, params=params, json=body)
        response.raise_for_status()

        # 返回翻译结果
        return response.json()[0]["translations"][0]["text"]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslateWindow()
    window.show()
    sys.exit(app.exec())