import sys
import sqlite3
import os
import csv
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets ,uic
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem
from . import Tool

# 获取 src 目录的绝对路径
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 现在可以导入 dao 下的模块
from dao import TM_dao
from dao import table_description_dao
class EditableTextEdit(QtWidgets.QTextEdit):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setReadOnly(True)  # 初始只读


    def focusOutEvent(self, event):
        # 失去焦点时切回只读
        self.setReadOnly(True)
        super().focusOutEvent(event)
        self.setMouseTracking(True)  # 开启鼠标追踪





class NewTMEntryDialog(QtWidgets.QDialog):
    def __init__(self, current_user_id, parent=None):
        super().__init__(parent)
        self.current_user_id = current_user_id
        self.setWindowTitle("新建翻译记忆条目")
        self.resize(400, 300)

        self.source_text_edit = QtWidgets.QTextEdit()
        self.target_text_edit = QtWidgets.QTextEdit()

        # 改为 QLabel 显示语言，禁止编辑
        self.source_lang_label = QtWidgets.QLabel()
        self.target_lang_label = QtWidgets.QLabel()

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("源文本:", self.source_text_edit)
        form_layout.addRow("目标文本:", self.target_text_edit)
        form_layout.addRow("源语言:", self.source_lang_label)
        form_layout.addRow("目标语言:", self.target_lang_label)

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

        self.source_text_edit.textChanged.connect(self.detect_source_language)
        self.target_text_edit.textChanged.connect(self.detect_target_language)

        # 打开对话框时主动检测
        self.detect_source_language()
        self.detect_target_language()

    def detect_source_language(self):
        text = self.source_text_edit.toPlainText().strip()

        if text:
            try:
                mapper = Tool.LanguageMapper()
                lang = mapper.detect_language(text)
                self.source_lang_label.setText(lang)
            except Exception as e:
                print(e)
                self.source_lang_label.setText("")
        else:
            print("3")
            self.source_lang_label.setText("")

    def detect_target_language(self):
        text = self.target_text_edit.toPlainText().strip()
        if text:
            try:
                mapper = Tool.LanguageMapper()
                lang = mapper.detect_language(text)
                self.target_lang_label.setText(lang)
            except Exception as e:
                print(e)
                self.target_lang_label.setText("")
        else:
            self.target_lang_label.setText("")

    def get_data(self):
        return {
            "source_text": self.source_text_edit.toPlainText().strip(),
            "target_text": self.target_text_edit.toPlainText().strip(),
            "source_lang": self.source_lang_label.text().strip(),
            "target_lang": self.target_lang_label.text().strip(),
            "created_by": self.current_user_id
        }

'''
TM_items_show中的提示可以考虑提示其他关键词，行号索引会动态变化，不直观
editTMitems 的QtWidgets.QMessageBox.warning(self, "提示", "可以编辑" + str(row + 1))
saveTMitems(self):  QtWidgets.QMessageBox.warning(self, "提示", "已经保存" + str(row + 1))
deleteTMitems(self): QtWidgets.QMessageBox.warning(self, "提示", "已删除行" + str(row + 1))
on_selection_changed(self): QtWidgets.QMessageBox.warning(self, "提示", "已经保存" + str(row + 1))
'''


class TM_items_show(QtWidgets.QDialog):
    # 列索引常量
    COL_ID = 0
    COL_SOURCE_TEXT = 1
    COL_TARGET_TEXT = 2
    COL_SOURCE_LANG = 3
    COL_TARGET_LANG = 4
    COL_CREATED_BY = 5
    COL_CREATED_AT = 6

    def __init__(self, name="记忆库详情"):
        super().__init__()
        self.name = name
        self.TM_name = TM_dao.sanitize_identifier(name)
        self.row_edit_status = {}  # 记录行编辑状态
        self.prev_selected_items = set()
        self.ignore_selection_change = False
        self.is_create_now = False

        self._load_ui()
        self._init_ui()
        self._connect_signals()
        self.load_tm_data()

    def _load_ui(self):
        """加载UI文件"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "TM_items_show.ui")
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"UI文件未找到: {ui_path}")
        uic.loadUi(ui_path, self)
        self.setWindowTitle(self.name)
        self.resize(600, 500)
        self.table_type = "tm"
    def _init_ui(self):
        """初始化表格和控件状态"""
        header = self.tableWidget_item.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget_item.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget_item.setSelectionBehavior(QAbstractItemView.SelectRows)

    def _connect_signals(self):
        """连接信号槽"""
        self.tableWidget_item.itemSelectionChanged.connect(self.on_selection_changed)
        self.pushButton_createTMitems.clicked.connect(self.create_tm_items)
        self.pushButton_save.clicked.connect(self.save_tm_items)
        self.pushButton_edit.clicked.connect(self.edit_tm_items)
        self.pushButton_delete.clicked.connect(self.delete_tm_items)
        self.pushButton_export.clicked.connect(self.export_tm_items)
        self.pushButton_import.clicked.connect(self.import_tm_items)

    def closeEvent(self, event):
        """关闭事件，更新描述信息"""
        try:
            count = table_description_dao.get_record_count(self.TM_name)
            table_description_dao.update_table_description(self.TM_name, count , None, None,self.table_type)
            print("更新成功")
        except Exception as e:
            print(f"关闭时更新描述失败: {e}")
        super().closeEvent(event)

    def create_tm_items(self):
        """创建新条目"""
        try:
            current_user_id = 1  # TODO: 动态获取用户ID
            dialog = NewTMEntryDialog(current_user_id, self)
            if dialog.exec_() != QtWidgets.QDialog.Accepted:
                return
            data = dialog.get_data()
            if not data["source_text"] or not data["target_text"]:
                QMessageBox.warning(self, "提示", "请填写所有字段")
                return

            tm_id, created_at = TM_dao.insert_tm_entry(
                self.TM_name,
                data["source_text"], data["target_text"],
                data["source_lang"], data["target_lang"],
                data["created_by"]
            )
            self._insert_row(tm_id, data, created_at)
            self.is_create_now = True
            self.save_tm_items()
            self.is_create_now = False
            QMessageBox.information(self, "成功", f"新条目已创建，ID: {tm_id}")
        except Exception as e:
            print(f"创建条目失败: {e}")

    def _insert_row(self, tm_id, data, created_at):
        """向表格插入一行数据"""
        row = self.tableWidget_item.rowCount()
        self.tableWidget_item.insertRow(row)

        # ID列
        self.tableWidget_item.setItem(row, self.COL_ID, QTableWidgetItem(str(tm_id)))

        # 源文本和目标文本使用EditableTextEdit控件
        source_edit = EditableTextEdit()
        source_edit.setPlainText(data["source_text"])
        source_edit.setReadOnly(True)
        self.tableWidget_item.setCellWidget(row, self.COL_SOURCE_TEXT, source_edit)

        target_edit = EditableTextEdit()
        target_edit.setPlainText(data["target_text"])
        target_edit.setReadOnly(True)
        self.tableWidget_item.setCellWidget(row, self.COL_TARGET_TEXT, target_edit)

        # 其他列
        def create_item(text):
            item = QTableWidgetItem(str(text))
            item.setToolTip(str(text))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            return item

        self.tableWidget_item.setItem(row, self.COL_SOURCE_LANG, create_item(data["source_lang"]))
        self.tableWidget_item.setItem(row, self.COL_TARGET_LANG, create_item(data["target_lang"]))
        self.tableWidget_item.setItem(row, self.COL_CREATED_BY, create_item(data["created_by"]))
        self.tableWidget_item.setItem(row, self.COL_CREATED_AT, create_item(created_at))

        self.row_edit_status[row] = False
        self.tableWidget_item.selectRow(row)

    def edit_tm_items(self):
        """编辑选中行"""
        row = self._get_selected_row()
        if row is None:
            QMessageBox.warning(self, "提示", "请先选择一行进行编辑")
            return
        self.set_table_cells_read(row, False)
        self.row_edit_status[row] = True
        QMessageBox.information(self, "提示", f"可以编辑第 {row + 1} 行")

    def save_tm_items(self):
        """保存选中行"""
        row = self._get_selected_row()
        if row is None:
            QMessageBox.warning(self, "提示", "请先选择一行进行保存")
            return
        self.set_table_cells_read(row, True)
        self.push_item_data(row, False)
        self.row_edit_status[row] = False
        if not self.is_create_now:
            QMessageBox.information(self, "提示", f"已保存第 {row + 1} 行")
        self.tableWidget_item.clearSelection()

    def delete_tm_items(self):
        """删除选中行"""
        row = self._get_selected_row()
        if row is None:
            QMessageBox.warning(self, "提示", "请先选择一行进行删除")
            return
        try:
            self.ignore_selection_change = True  # 禁止选中变化信号处理
            self.push_item_data(row, True)
            self.tableWidget_item.removeRow(row)
            # 调整 row_edit_status 字典，删除对应行的状态
            self.row_edit_status.pop(row, None)
            # 重新整理 row_edit_status 键，避免行号错乱
            new_status = {}
            for r, status in self.row_edit_status.items():
                if r > row:
                    new_status[r - 1] = status
                elif r < row:
                    new_status[r] = status
            self.row_edit_status = new_status
            QMessageBox.information(self, "提示", f"已删除第 {row + 1} 行")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"删除失败: {e}")
        finally:
            self.ignore_selection_change = False

    def export_tm_items(self):
        """导出为CSV"""
        file_path, _ = QFileDialog.getSaveFileName(self, "导出翻译记忆库", "", "CSV文件 (*.csv)")
        if not file_path:
            return
        try:
            rows = TM_dao.batch_export(self.TM_name)
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', '源文本', '目标文本', '源语言', '目标语言', '创建者', '创建时间'])
                writer.writerows(rows)
            QMessageBox.information(self, "导出成功", f"已成功导出到 {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "导出失败", f"导出过程中出错: {e}")

    def import_tm_items(self):
        """从CSV导入"""
        file_path, _ = QFileDialog.getOpenFileName(self, "导入翻译记忆库", "", "CSV文件 (*.csv)")
        if not file_path:
            return
        try:
            rows_to_insert = []
            with open(file_path, encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not row.get('源文本') or not row.get('目标文本') or not row.get('源语言') or not row.get('目标语言'):
                        continue
                    created_by = int(row.get('创建者', '1')) if row.get('创建者', '1').isdigit() else 1
                    rows_to_insert.append((
                        row['源文本'], row['目标文本'], row['源语言'], row['目标语言'], created_by
                    ))
            if not rows_to_insert:
                QMessageBox.warning(self, "导入失败", "没有有效数据可导入")
                return
            success = TM_dao.batch_insert(self.TM_name, rows_to_insert)
            if success:
                self.load_tm_data()
                QMessageBox.information(self, "导入成功", f"成功导入 {len(rows_to_insert)} 条记录")
            else:
                QMessageBox.warning(self, "导入失败", "批量插入数据库时出错")
        except Exception as e:
            QMessageBox.warning(self, "导入失败", f"导入过程中出错: {e}")

    def on_selection_changed(self):
        """选中行变化时自动保存未保存编辑"""
        if self.ignore_selection_change:
            return
        try:
            current_selected_rows = set(item.row() for item in self.tableWidget_item.selectedItems())
            deselected_rows = self.prev_selected_items - current_selected_rows
            for row in deselected_rows:
                if self.row_edit_status.get(row, False):
                    self.set_table_cells_read(row, True)
                    self.push_item_data(row, False)
                    self.row_edit_status[row] = False
                    QMessageBox.information(self, "提示", f"第 {row + 1} 行已自动保存")
            self.prev_selected_items = current_selected_rows
        except Exception as e:
            print(f"选中变化处理异常: {e}")

    def set_table_cells_read(self, row, read: bool):
        """设置指定行的单元格是否可编辑"""
        source_text = self.tableWidget_item.cellWidget(row, self.COL_SOURCE_TEXT)
        target_text = self.tableWidget_item.cellWidget(row, self.COL_TARGET_TEXT)
        if source_text:
            source_text.setReadOnly(read)
        if target_text:
            target_text.setReadOnly(read)

        for col in range(self.tableWidget_item.columnCount()):
            if col in (self.COL_CREATED_AT, self.COL_ID, self.COL_CREATED_BY):
                item = self.tableWidget_item.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            elif col not in (self.COL_SOURCE_TEXT, self.COL_TARGET_TEXT):
                item = self.tableWidget_item.item(row, col)
                if item:
                    if read:
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                    else:
                        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.tableWidget_item.viewport().update()

    def load_tm_data(self):
        """加载数据库数据到表格"""
        try:
            rows = TM_dao.batch_export(self.TM_name)
            self.tableWidget_item.clear()
            self.tableWidget_item.setRowCount(len(rows) if rows else 0)
            self.tableWidget_item.setColumnCount(7)
            self.tableWidget_item.setHorizontalHeaderLabels(
                ['ID', '源文本', '目标文本', '源语言', '目标语言', '创建者', '创建时间']
            )
            if not rows:
                return
            for row_idx, row_data in enumerate(rows):
                for col_idx, value in enumerate(row_data):
                    if col_idx in (self.COL_SOURCE_TEXT, self.COL_TARGET_TEXT):
                        text_edit = EditableTextEdit()
                        text_edit.setPlainText(str(value) if value else "")
                        text_edit.setReadOnly(True)
                        self.tableWidget_item.setCellWidget(row_idx, col_idx, text_edit)
                    else:
                        item = QTableWidgetItem(str(value) if value else "")
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                        self.tableWidget_item.setItem(row_idx, col_idx, item)
        except Exception as e:
            print("加载数据库数据错误", e)

    def push_item_data(self, row, is_delete):
        """更新或删除数据库中的数据"""
        tm_id_item = self.tableWidget_item.item(row, self.COL_ID)
        if tm_id_item is None:
            print("该行无有效ID，无法操作")
            return
        try:
            tm_id = int(tm_id_item.text())
        except ValueError:
            print("tm_id格式错误，无法操作")
            return

        if is_delete:
            TM_dao.delete_tm_entry(self.TM_name, tm_id)
            print(f"已删除 tm_id={tm_id} 的记录")
            return

        source_text_widget = self.tableWidget_item.cellWidget(row, self.COL_SOURCE_TEXT)
        target_text_widget = self.tableWidget_item.cellWidget(row, self.COL_TARGET_TEXT)
        source_text = source_text_widget.toPlainText() if source_text_widget else ""
        target_text = target_text_widget.toPlainText() if target_text_widget else ""
        source_lang = self.tableWidget_item.item(row, self.COL_SOURCE_LANG).text()
        target_lang = self.tableWidget_item.item(row, self.COL_TARGET_LANG).text()

        TM_dao.update_tm_entry(
            self.TM_name, tm_id,
            source_text=source_text,
            target_text=target_text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        print(f"已更新 tm_id={tm_id} 的记录")

    def _get_selected_row(self):
        """获取当前选中行，若无选中返回None"""
        selected_ranges = self.tableWidget_item.selectedRanges()
        if not selected_ranges:
            return None
        return selected_ranges[0].topRow()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TM_items_show()
    window.show()

    sys.exit(app.exec_())