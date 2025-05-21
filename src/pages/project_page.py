# src/pages/project_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dao import project_dao

class ProjectPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.setWindowTitle("项目管理页面")
        self.layout = QVBoxLayout()
        self.main_window = main_window  # 主窗口引用，用于页面跳转

        self.layout.addWidget(QLabel("📁 项目管理页面"))

        btn_new = QPushButton("新建项目")
        btn_new.clicked.connect(self.on_add_project)
        self.layout.addWidget(btn_new)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.refresh_table()

    def refresh_table(self):
        projects = project_dao.get_all_projects()
        self.table.setRowCount(len(projects))
        self.table.setColumnCount(7)  # 新增一列：进入文档
        self.table.setHorizontalHeaderLabels(["项目ID", "项目名称", "源语言", "目标语言", "创建时间", "操作", "进入文档"])
        for row, proj in enumerate(projects):
            for col, value in enumerate(proj):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
            btn_delete = QPushButton("删除")
            btn_delete.clicked.connect(lambda _, pid=proj[0]: self.delete_project(pid))
            self.table.setCellWidget(row, 5, btn_delete)
            # 新增“进入文档”按钮
            btn_enter = QPushButton("进入文档")
            btn_enter.clicked.connect(lambda _, pid=proj[0]: self.enter_document_page(pid))
            self.table.setCellWidget(row, 6, btn_enter)
        self.table.resizeColumnsToContents()

    def enter_document_page(self, project_id):
        """
        跳转到文档管理页面，传递当前项目ID
        """
        if self.main_window:
            self.main_window.show_document_page(project_id)

    def on_add_project(self):
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "新建项目", "请输入项目名称：")
        if not ok or not name.strip():
            return
        src_lang, ok = QInputDialog.getText(self, "新建项目", "请输入源语言（如zh）：")
        if not ok or not src_lang.strip():
            return
        tgt_lang, ok = QInputDialog.getText(self, "新建项目", "请输入目标语言（如en）：")
        if not ok or not tgt_lang.strip():
            return
        project_dao.add_project(name.strip(), src_lang.strip(), tgt_lang.strip())
        QMessageBox.information(self, "提示", "项目创建成功！")
        self.refresh_table()

    def delete_project(self, pid):
        reply = QMessageBox.question(
            self, '确认删除', '确定要删除该项目吗？此操作不可恢复。',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            project_dao.delete_project(pid)
            QMessageBox.information(self, "提示", "项目已删除。")
            self.refresh_table()

