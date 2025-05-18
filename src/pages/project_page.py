# pages/project_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QDialog, QLabel, QLineEdit, QDialogButtonBox, QMessageBox
)
from dao import project_dao

class ProjectPage(QWidget):
    def __init__(self):
        super().__init__()
        project_dao.init_db()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 按钮栏
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("新建项目")
        self.btn_delete = QPushButton("删除项目")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        self.layout.addLayout(btn_layout)

        # 表格展示
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "项目名称", "创建时间"])
        self.layout.addWidget(self.table)

        # 事件绑定
        self.btn_add.clicked.connect(self.show_add_dialog)
        self.btn_delete.clicked.connect(self.delete_selected_project)

        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(0)
        projects = project_dao.get_all_projects()
        for row, (pid, name, created_at) in enumerate(projects):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(pid)))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(created_at))

    def show_add_dialog(self):
        dialog = CreateProjectDialog()
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.name_input.text()
            if name:
                project_dao.add_project(name)
                self.refresh_table()

    def delete_selected_project(self):
        selected = self.table.currentRow()
        if selected >= 0:
            pid_item = self.table.item(selected, 0)
            if pid_item:
                pid = int(pid_item.text())
                confirm = QMessageBox.question(self, "确认", "确定删除该项目？",
                                               QMessageBox.Yes | QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    project_dao.delete_project(pid)
                    self.refresh_table()

class CreateProjectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("新建项目")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("请输入项目名称："))
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)