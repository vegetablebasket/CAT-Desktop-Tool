# src/pages/document_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QMessageBox, QFileDialog
)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dao import document_dao

class DocumentPage(QWidget):
    def __init__(self, project_id=1,main_window=None):
        """
        :param project_id: 当前显示的项目ID（测试可以写死为1，后续页面跳转会自动传入）
        """
        super().__init__()
        self.project_id = project_id
        self.main_window = main_window # 主窗口引用，用于页面跳转
        self.setWindowTitle("文档管理页面")
        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel(f"📄 文档管理页面 - 项目ID: {self.project_id}"))

        # 导入文档按钮
        btn_import = QPushButton("导入文档")
        btn_import.clicked.connect(self.on_import_document)
        self.layout.addWidget(btn_import)

        # 文档表格
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        self.refresh_table()

    def refresh_table(self):
        """
        刷新文档表格
        """
        docs = document_dao.get_documents_by_project(self.project_id)
        self.table.setRowCount(len(docs))
        self.table.setColumnCount(7)  # 多一列用于操作
        self.table.setHorizontalHeaderLabels(["文档ID", "文档名", "格式", "状态", "创建时间", "操作","进入翻译"])
        for row, doc in enumerate(docs):
            for col, value in enumerate(doc):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
            # 删除按钮
            btn_delete = QPushButton("删除")
            btn_delete.clicked.connect(lambda _, doc_id=doc[0]: self.delete_document(doc_id))
            self.table.setCellWidget(row, 5, btn_delete)
            # 新增“进入翻译”按钮
            btn_edit = QPushButton("进入翻译")
            btn_edit.clicked.connect(lambda _, doc_id=doc[0]: self.enter_translation_page(doc_id))
            self.table.setCellWidget(row, 6, btn_edit)
        self.table.resizeColumnsToContents()

    def on_import_document(self):
        """
        选择文件并导入为文档（暂时只支持txt），同时按段落自动写入 translation_fragments
        """
        from dao import translation_fragment_dao  # 导入你刚写的DAO
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文档", "", "文本文件 (*.txt);;所有文件 (*)")
        if not file_path:
            return
        file_name = os.path.basename(file_path)
        file_format = "txt"

        # 1. 数据库添加文档（获得文档id）
        from dao import document_dao
        document_dao.add_document(self.project_id, file_name, file_format)
        # 2. 获取新导入文档的id
        docs = document_dao.get_documents_by_project(self.project_id)
        # 按 id 最大值/最新顺序获取最新一个
        new_doc_id = docs[0][0]  # [(id, name, ...), ...]，id在第一个元素

        # 3. 读取文件内容并分段
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 按“空行”分段，strip()移除首尾空格，splitlines()保证兼容性
        raw_paragraphs = content.strip().split("\n\n")  # 两个换行符=空行
        paragraphs = [p.strip().replace('\n', ' ') for p in raw_paragraphs if p.strip()]

        # 4. 写入 translation_fragments 表
        translation_fragment_dao.create_table()  # 保证表已存在
        for idx, para in enumerate(paragraphs, 1):
            translation_fragment_dao.add_fragment(new_doc_id, idx, para)
        QMessageBox.information(self, "提示", f"文档导入并分段成功！共{len(paragraphs)}段。")
        self.refresh_table()

    def delete_document(self, doc_id):
        """
        删除文档，二次确认
        """
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除该文档吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            document_dao.delete_document(doc_id)
            QMessageBox.information(self, "提示", "文档已删除。")
            self.refresh_table()

    def enter_translation_page(self, document_id):
        """
        跳转到翻译编辑页面，传递文档ID
        """
        if self.main_window:
            self.main_window.show_translation_page(document_id)