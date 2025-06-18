import hashlib
import random
import sys

import requests
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QTextEdit, QPushButton, QFileDialog, QComboBox
)

# 替换为你自己的百度翻译 API 凭据
APP_ID = '20250520002361934'
SECRET_KEY = 'TUDvE1a3cX7vIzrpSlzj'


def baidu_translate(q, from_lang='auto', to_lang='en'):
    salt = str(random.randint(32768, 65536))
    sign_str = APP_ID + q + salt + SECRET_KEY
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    params = {
        'q': q,
        'from': from_lang,
        'to': to_lang,
        'appid': APP_ID,
        'salt': salt,
        'sign': sign
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        if 'trans_result' in data:
            return '\n'.join([item['dst'] for item in data['trans_result']])
        else:
            return f"错误：{data.get('error_msg', '未知错误')}"
    except Exception as e:
        return f"异常：{str(e)}"


class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("百度翻译 · 支持多语言")
        self.setGeometry(200, 100, 1000, 700)

        font = QFont("Microsoft YaHei", 14)
        self.lang_code_map = {
            '自动检测': 'auto',
            '中文': 'zh',
            '英文': 'en',
            '日文': 'jp',
            '韩文': 'kor',
            '法文': 'fra',
            '德文': 'de',
            '俄文': 'ru',
            '西班牙文': 'spa',
            '葡萄牙文': 'pt'
        }

        # 布局设置
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # --- 左侧区域 ---
        lang_layout = QHBoxLayout()
        self.from_lang = QComboBox()
        self.to_lang = QComboBox()
        for name in self.lang_code_map:
            self.from_lang.addItem(name)
            self.to_lang.addItem(name)
        self.from_lang.setCurrentText("自动检测")
        self.to_lang.setCurrentText("英文")

        lang_layout.addWidget(QLabel("源语言："))
        lang_layout.addWidget(self.from_lang)
        lang_layout.addWidget(QLabel("目标语言："))
        lang_layout.addWidget(self.to_lang)

        input_label = QLabel("输入内容：")
        input_label.setFont(font)

        self.input_text = QTextEdit()
        self.input_text.setFont(font)
        self.input_text.textChanged.connect(self.translate_text)

        left_layout.addLayout(lang_layout)
        left_layout.addWidget(input_label)
        left_layout.addWidget(self.input_text)

        # --- 右侧区域 ---
        output_label = QLabel("翻译结果：")
        output_label.setFont(font)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(font)
        self.output_text.setStyleSheet("background-color: #f9f9f9;")

        button_layout = QHBoxLayout()
        copy_button = QPushButton("复制翻译")
        export_button = QPushButton("导出为 TXT")
        copy_button.clicked.connect(self.copy_translation)
        export_button.clicked.connect(self.export_translation)

        button_layout.addWidget(copy_button)
        button_layout.addWidget(export_button)

        right_layout.addWidget(output_label)
        right_layout.addWidget(self.output_text)
        right_layout.addLayout(button_layout)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)

        self.setLayout(main_layout)

    def translate_text(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            self.output_text.setPlainText("")
            return

        self.output_text.setPlainText("正在翻译...")
        QApplication.processEvents()

        try:
            from_lang = self.lang_code_map[self.from_lang.currentText()]
            to_lang = self.lang_code_map[self.to_lang.currentText()]
            if from_lang == to_lang:
                self.output_text.setPlainText("源语言和目标语言不能相同")
                return

            result = baidu_translate(text, from_lang=from_lang, to_lang=to_lang)
            self.output_text.setPlainText(result)
        except Exception as e:
            self.output_text.setPlainText(f"翻译失败：{e}")

    def copy_translation(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())
        self.setWindowTitle("翻译结果已复制")

    def export_translation(self):
        text = self.output_text.toPlainText()
        if not text:
            return
        path, _ = QFileDialog.getSaveFileName(self, "保存翻译结果", "translation.txt", "Text Files (*.txt)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.setWindowTitle(f"已保存：{path}")
            except Exception as e:
                self.setWindowTitle(f"保存失败：{e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = TranslatorApp()
    translator.show()
    sys.exit(app.exec())
