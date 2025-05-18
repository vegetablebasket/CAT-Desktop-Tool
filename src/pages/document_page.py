# src/pages/document_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QTextEdit, QListWidget
)
from dao import document_dao
from PyQt5.QtCore import Qt
import os
from docx import Document
import pdfminer
from pdfminer.high_level import extract_text

class DocumentPage(QWidget):
    def __init__(self):
        super().__init__()
        document_dao.init_doc_table()

        self.current_project_id = 1  # 临时固定值，后期动态获取

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 按钮栏
        btn_layout = QHBoxLayout()
        self.import_btn = QPushButton("导入文档")
        self.delete_btn = QPushButton("删除选中文档")
        btn_layout.addWidget(self.import_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        # 文档列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "文档名称", "导入时间"])
        layout.addWidget(self.table)

        # 预览区域
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview)

        # 段落列表区域
        self.paragraph_list = QListWidget()
        layout.addWidget(self.paragraph_list)

        # 绑定按钮
        self.import_btn.clicked.connect(self.import_file)
        self.delete_btn.clicked.connect(self.delete_selected_document)

        self.refresh_table()

    def refresh_table(self):
        """刷新表格，显示当前项目下的文档列表"""
        self.table.setRowCount(0)
        documents = document_dao.get_documents_by_project(self.current_project_id)
        for row, (doc_id, name, created_at) in enumerate(documents):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(doc_id)))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(created_at))

    def import_file(self):
        """导入文件，支持 .txt、.docx、.pdf 格式"""
        path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "Text Files (*.txt);;Word Files (*.docx);;PDF Files (*.pdf);;All Files (*)")
        if path:
            file_extension = os.path.splitext(path)[1].lower()
            try:
                if file_extension == '.txt':
                    content = self.read_txt(path)
                elif file_extension == '.docx':
                    content = self.read_docx(path)
                elif file_extension == '.pdf':
                    content = self.read_pdf(path)
                else:
                    raise ValueError("不支持的文件格式")

                name = os.path.basename(path)
                document_dao.add_document(name, content, self.current_project_id)

                # 提取段落并保存
                paragraphs = content.splitlines()
                for para in paragraphs:
                    document_dao.add_translation_fragment(self.current_project_id, para)

                self.refresh_table()

            except Exception as e:
                QMessageBox.critical(self, "导入失败", str(e))

    def read_txt(self, file_path):
        """读取 .txt 文件，将每一行当作一个段落"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().splitlines()  # 按行分割为段落
        except UnicodeDecodeError:
            # 如果 utf-8 解码失败，尝试使用 gbk 编码
            with open(file_path, "r", encoding="gbk") as f:
                content = f.read().splitlines()
        return '\n'.join(content)

    def read_docx(self, file_path):
        """读取 .docx 文件，返回所有段落"""
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip() != ""]
        return '\n'.join(paragraphs)

    def read_pdf(self, file_path):
        """读取 .pdf 文件，返回提取的文本"""
        return extract_text(file_path)

    def delete_selected_document(self):
        """删除选中文档"""
        selected = self.table.currentRow()
        if selected >= 0:
            doc_id = int(self.table.item(selected, 0).text())
            confirm = QMessageBox.question(self, "确认删除", "确定要删除此文档？", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                document_dao.delete_document(doc_id)
                self.refresh_table()

    def display_preview(self, doc_id):
        """显示文档内容预览"""
        # 这里可以增加显示文档内容的功能
        pass
