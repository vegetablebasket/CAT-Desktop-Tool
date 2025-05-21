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
    def __init__(self, project_id=1):
        """
        :param project_id: 当前显示的项目ID（测试可以写死为1，后续页面跳转会自动传入）
        """
        super().__init__()
        self.project_id = project_id
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
        self.table.setColumnCount(6)  # 多一列用于操作
        self.table.setHorizontalHeaderLabels(["文档ID", "文档名", "格式", "状态", "创建时间", "操作"])
        for row, doc in enumerate(docs):
            for col, value in enumerate(doc):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
            # 删除按钮
            btn_delete = QPushButton("删除")
            btn_delete.clicked.connect(lambda _, doc_id=doc[0]: self.delete_document(doc_id))
            self.table.setCellWidget(row, 5, btn_delete)
        self.table.resizeColumnsToContents()

    def on_import_document(self):
        """
        选择文件并导入为文档（只支持txt）
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文档", "", "文本文件 (*.txt);;所有文件 (*)")
        if not file_path:
            return
        file_name = os.path.basename(file_path)
        file_format = "txt"
        # 这里只保存文件信息到数据库，内容暂时不做处理
        document_dao.add_document(self.project_id, file_name, file_format)
        QMessageBox.information(self, "提示", "文档导入成功！")
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
