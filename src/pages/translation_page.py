from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QTextEdit, QPushButton, QMessageBox
from dao import document_dao


class TranslationPage(QWidget):
    def __init__(self, document_id=None):
        super().__init__()
        self.current_document_id = document_id if document_id else 1  # 默认文档 ID 为 1

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 段落列表显示
        self.paragraph_list = QListWidget()
        self.paragraph_list.itemClicked.connect(self.on_paragraph_click)  # 选中段落时显示内容
        layout.addWidget(self.paragraph_list)

        # 翻译框
        self.translation_input = QTextEdit()
        self.translation_input.setPlaceholderText("请输入翻译...")
        layout.addWidget(self.translation_input)

        # 保存翻译按钮
        self.save_button = QPushButton("保存翻译")
        self.save_button.clicked.connect(self.save_translation)
        layout.addWidget(self.save_button)

        self.load_paragraphs()

    def load_paragraphs(self):
        """加载并显示所有段落"""
        self.paragraph_list.clear()  # 清空列表
        fragments = document_dao.get_translation_fragments_by_document(self.current_document_id)
        for fragment in fragments:
            self.paragraph_list.addItem(fragment[1])  # 显示段落内容

    def on_paragraph_click(self, item):
        """段落点击时显示段落内容在翻译框"""
        selected_paragraph = item.text()
        self.translation_input.setText(selected_paragraph)

    def save_translation(self):
        """保存翻译内容"""
        selected_item = self.paragraph_list.currentItem()
        if selected_item:
            original_text = selected_item.text()  # 原始段落
            translated_text = self.translation_input.toPlainText()  # 翻译后的内容

            if not translated_text.strip():
                QMessageBox.warning(self, "警告", "翻译内容不能为空！")
                return

            # 查找段落在数据库中的 ID
            fragments = document_dao.get_translation_fragments_by_document(self.current_document_id)
            fragment_id = next((f[0] for f in fragments if f[1] == original_text), None)

            if fragment_id:
                # 保存翻译结果
                document_dao.save_translation(fragment_id, translated_text)
                QMessageBox.information(self, "成功", "翻译已保存！")
                self.load_paragraphs()  # 刷新段落列表
            else:
                QMessageBox.warning(self, "错误", "无法找到对应的段落！")
        else:
            QMessageBox.warning(self, "错误", "请先选择一个段落进行翻译。")