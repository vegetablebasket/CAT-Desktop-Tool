import sys
import os
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QMessageBox
from src.dao import Terminology_dao,table_description_dao


class EditableTextEdit(QtWidgets.QTextEdit):
    """可编辑的 QTextEdit，失去焦点后自动切回只读状态"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)

    def focusOutEvent(self, event):
        self.setReadOnly(True)
        super().focusOutEvent(event)

class NewTerminologyEntryDialog(QtWidgets.QDialog):
    """新建术语条目对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建术语条目")
        self.resize(400, 400)

        self.term_edit = QtWidgets.QLineEdit()
        self.translation_edit = QtWidgets.QLineEdit()
        self.definition_edit = QtWidgets.QTextEdit()
        self.domain_edit = QtWidgets.QLineEdit()
        self.project_id_edit = QtWidgets.QLineEdit()

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("术语原文:", self.term_edit)
        form_layout.addRow("对应译文:", self.translation_edit)
        form_layout.addRow("术语定义:", self.definition_edit)
        form_layout.addRow("术语领域:", self.domain_edit)
        form_layout.addRow("所属项目ID:", self.project_id_edit)

        self.save_button = QtWidgets.QPushButton("保存")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QtWidgets.QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)


        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def get_data(self):
        project_id_text = self.project_id_edit.text().strip()
        project_id = int(project_id_text) if project_id_text.isdigit() else None
        return {
            "term": self.term_edit.text().strip(),
            "translation": self.translation_edit.text().strip(),
            "definition": self.definition_edit.toPlainText().strip(),
            "domain": self.domain_edit.text().strip(),
            "project_id": project_id
        }

class TerminologyItemsShow(QtWidgets.QDialog):
    """
    术语条目展示与管理窗口
    列索引说明：
        0: term_id
        1: term (术语原文)
        2: translation (对应译文)
        3: definition (术语定义)
        4: domain (术语领域)
        5: project_id (所属项目)
    """
    col_term_id = 0
    col_term = 1
    col_translation = 2
    col_definition = 3
    col_domain = 4
    col_project_id = 5

    def __init__(self, name="术语库详情"):
        super().__init__()
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "Terminology_items_show.ui")
        print("UI 文件路径:", ui_path)
        print("UI 文件存在吗？", os.path.exists(ui_path))
        print("__file__ 的值:", __file__)
        print([attr for attr in dir(self) if not attr.startswith('_')])
        uic.loadUi(ui_path, self)
        self.setWindowTitle(name)
        self.resize(700, 500)

        self.name = name
        self.table_name = Terminology_dao.sanitize_table_name(self.name)
        self.table_type = 'terminology'

        # 表格设置：6列，列宽自动拉伸，单行选择
        self.tableWidget_item.setColumnCount(6)
        self.tableWidget_item.setHorizontalHeaderLabels(
            ["ID", "术语原文", "对应译文", "术语定义", "术语领域", "所属项目ID"]
        )
        header = self.tableWidget_item.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget_item.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget_item.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 连接信号
        self.tableWidget_item.itemSelectionChanged.connect(self.on_selection_changed)
        self.pushButton_createTerminologyitems.clicked.connect(self.createTerminologyitems)
        self.pushButton_save.clicked.connect(self.saveTerminologyitems)
        self.pushButton_edit.clicked.connect(self.editTerminologyitems)
        self.pushButton_delete.clicked.connect(self.deleteTerminologyitems)
        self.pushButton_export.clicked.connect(self.exportTerminology)
        self.pushButton_import.clicked.connect(self.importTerminology)
        # 记录行编辑状态，key: row，value: bool（True表示编辑中未保存）
        self.row_edit_status = {}

        # 加载数据
        self.load_terminology_data()

    def closeEvent(self, event):
        """关闭事件，更新描述信息"""
        try:
            count = table_description_dao.get_record_count(self.table_name)
            table_description_dao.update_table_description(self.table_name, count , None, None,self.table_type)
            print("更新成功")
        except Exception as e:
            print(f"关闭时更新描述失败: {e}")
        super().closeEvent(event)

    def load_terminology_data(self):
        """从数据库加载术语数据并显示"""
        self.tableWidget_item.clearContents()
        self.tableWidget_item.setRowCount(0)

        terminology_list = Terminology_dao.list_terminologies(self.table_name)

        for row_idx, item in enumerate(terminology_list):
            self.tableWidget_item.insertRow(row_idx)
            self.tableWidget_item.setItem(row_idx, self.col_term_id, QTableWidgetItem(str(item.get("term_id", ""))))
            self.tableWidget_item.setItem(row_idx, self.col_term, QTableWidgetItem(item.get("term", "")))
            self.tableWidget_item.setItem(row_idx, self.col_translation, QTableWidgetItem(item.get("translation", "")))
            self.tableWidget_item.setItem(row_idx, self.col_definition, QTableWidgetItem(item.get("definition") or ""))
            self.tableWidget_item.setItem(row_idx, self.col_domain, QTableWidgetItem(item.get("domain") or ""))
            project_id = item.get("project_id")
            self.tableWidget_item.setItem(row_idx, self.col_project_id, QTableWidgetItem(str(project_id) if project_id is not None else ""))

            # 默认所有单元格只读
            for col in range(self.tableWidget_item.columnCount()):
                item_widget = self.tableWidget_item.item(row_idx, col)
                if item_widget:
                    item_widget.setFlags(item_widget.flags() & ~QtCore.Qt.ItemIsEditable)

    def on_selection_changed(self):
        """选中行变化时触发"""
        selected_rows = self.tableWidget_item.selectionModel().selectedRows()
        if not selected_rows:
            self.pushButton_edit.setEnabled(False)
            self.pushButton_delete.setEnabled(False)
            self.pushButton_save.setEnabled(False)
        else:
            self.pushButton_edit.setEnabled(True)
            self.pushButton_delete.setEnabled(True)
            # 只有编辑状态时才启用保存按钮
            row = selected_rows[0].row()
            self.pushButton_save.setEnabled(self.row_edit_status.get(row, False))

    def createTerminologyitems(self):
        """新建术语条目"""
        dlg = NewTerminologyEntryDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = dlg.get_data()
            if not data["term"] or not data["translation"]:
                QMessageBox.warning(self, "提示", "术语原文和对应译文不能为空！")
                return
            term_id = Terminology_dao.add_terminology(
                data["term"], data["translation"],self.table_name, data["definition"], data["domain"], data["project_id"]
            )
            if term_id:
                QMessageBox.information(self, "成功", f"新增术语条目成功，ID={term_id}")
                self.load_terminology_data()
            else:
                QMessageBox.warning(self, "失败", "新增术语条目失败！")

    def editTerminologyitems(self):
        """启用选中行编辑"""
        selected_rows = self.tableWidget_item.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择一行进行编辑！")
            return
        row = selected_rows[0].row()
        # 设置该行所有单元格可编辑，除了ID列
        for col in range(1, self.tableWidget_item.columnCount()):
            item = self.tableWidget_item.item(row, col)
            if item:
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.row_edit_status[row] = True
        self.pushButton_save.setEnabled(True)

    def saveTerminologyitems(self):
        """保存编辑后的术语条目"""
        selected_rows = self.tableWidget_item.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择一行进行保存！")
            return
        row = selected_rows[0].row()
        if not self.row_edit_status.get(row, False):
            QMessageBox.information(self, "提示", "该行没有处于编辑状态，无需保存。")
            return

        try:
            term_id = int(self.tableWidget_item.item(row, self.col_term_id).text())
            term = self.tableWidget_item.item(row, self.col_term).text().strip()
            translation = self.tableWidget_item.item(row, self.col_translation).text().strip()
            definition = self.tableWidget_item.item(row, self.col_definition).text().strip()
            domain = self.tableWidget_item.item(row, self.col_domain).text().strip()
            project_id_text = self.tableWidget_item.item(row, self.col_project_id).text().strip()
            project_id = int(project_id_text) if project_id_text.isdigit() else None

            if not term or not translation:
                QMessageBox.warning(self, "提示", "术语原文和对应译文不能为空！")
                return

            success = Terminology_dao.update_terminology(term_id,self.table_name, term, translation, definition, domain, project_id)
            if success:
                QMessageBox.information(self, "成功", "术语条目保存成功！")
                # 取消编辑状态，设置单元格只读
                for col in range(self.tableWidget_item.columnCount()):
                    item = self.tableWidget_item.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.row_edit_status[row] = False
                self.pushButton_save.setEnabled(False)
            else:
                QMessageBox.warning(self, "失败", "术语条目保存失败！")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存时发生异常: {e}")

    def deleteTerminologyitems(self):
        """删除选中术语条目"""
        selected_rows = self.tableWidget_item.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择一行进行删除！")
            return
        row = selected_rows[0].row()
        term_id = self.tableWidget_item.item(row, self.col_term_id).text()
        ret = QMessageBox.question(self, "确认删除", f"确定删除ID={term_id}的术语条目吗？", QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            success = Terminology_dao.delete_terminology(int(term_id),self.table_name)
            if success:
                QMessageBox.information(self, "成功", "术语条目删除成功！")
                self.load_terminology_data()
            else:
                QMessageBox.warning(self, "失败", "术语条目删除失败！")

    def exportTerminology(self):
        """导出术语库到CSV文件"""
        from PyQt5.QtWidgets import QFileDialog

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "导出术语库", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        if file_path:
            try:
                Terminology_dao.export_terminology(file_path ,self.table_name)
                QMessageBox.information(self, "导出成功", f"术语库已成功导出到:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "导出失败", f"导出时发生错误:\n{e}")

    def importTerminology(self):
        """从CSV文件导入术语库"""
        from PyQt5.QtWidgets import QFileDialog

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "导入术语库", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        if file_path:
            try:
                Terminology_dao.import_terminology(file_path ,self.table_name)
                QMessageBox.information(self, "导入成功", f"术语库已成功从文件导入:\n{file_path}")
                self.load_terminology_data()  # 重新加载数据
            except Exception as e:
                QMessageBox.warning(self, "导入失败", f"导入时发生错误:\n{e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TerminologyItemsShow()
    window.show()

    sys.exit(app.exec_())