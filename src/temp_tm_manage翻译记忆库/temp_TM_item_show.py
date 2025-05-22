import sys
import sqlite3
import os
from PyQt5 import QtCore, QtGui, QtWidgets ,uic
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem

# 获取 src 目录的绝对路径
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 现在可以导入 dao 下的模块
from dao import TM_dao

class EditableTextEdit(QtWidgets.QTextEdit):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setReadOnly(True)  # 初始只读

    def focusOutEvent(self, event):
        # 失去焦点时切回只读
        self.setReadOnly(True)
        super().focusOutEvent(event)

class NewTMEntryDialog(QtWidgets.QDialog):
    def __init__(self, current_user_id, parent=None):
        super().__init__(parent)
        self.current_user_id = current_user_id
        self.setWindowTitle("新建翻译记忆条目")
        self.resize(400, 300)

        self.source_text_edit = QtWidgets.QTextEdit()
        self.target_text_edit = QtWidgets.QTextEdit()
        self.source_lang_edit = QtWidgets.QLineEdit()
        self.target_lang_edit = QtWidgets.QLineEdit()

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("源文本:", self.source_text_edit)
        form_layout.addRow("目标文本:", self.target_text_edit)
        form_layout.addRow("源语言:", self.source_lang_edit)
        form_layout.addRow("目标语言:", self.target_lang_edit)

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
        return {
            "source_text": self.source_text_edit.toPlainText().strip(),
            "target_text": self.target_text_edit.toPlainText().strip(),
            "source_lang": self.source_lang_edit.text().strip(),
            "target_lang": self.target_lang_edit.text().strip(),
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
    '''
            0: "id",
            1: "源文本",
            2: "目标文本",
            3: "源文本语言",
            4: "目标文本语言",
            5: "创建者",
            6: "创建时间"
    '''
    col_id = 0
    col_source_text = 1
    col_target_text = 2
    col_create_by = 5
    col_create_at = 6
    col_source_lang = 3
    col_target_lang = 4
    def __init__(self, name = "记忆库详情"):
        super().__init__()
        uic.loadUi("TM_items_show.ui", self)
        self.name = name
        self.setWindowTitle(self.name)
        self.resize(600, 500)

        #使所有列的宽度自动拉伸，均匀分布填满表格宽度。
        header = self.tableWidget_item.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        #一次只能选定一行
        self.tableWidget_item.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget_item.setSelectionBehavior(QAbstractItemView.SelectRows)

        #条目选中状态改变时，做出的改变
        self.tableWidget_item.itemSelectionChanged.connect(self.on_selection_changed)
        self.row_edit_status = {}  # key: row号, value: bool，True表示编辑未保存，False表示已保存或未编辑
        #按钮功能
        self.pushButton_createTMitems.clicked.connect(self.createTMitems)
        self.pushButton_save.clicked.connect(self.saveTMitems)
        self.pushButton_edit.clicked.connect(self.editTMitems)
        self.pushButton_delete.clicked.connect(self.deleteTMitems)

        #初始化prev_selected_item
        self.prev_selected_items = set()
        self.ignore_selection_change = False

        #初始化已显现数据
        self.load_tm_data()

    def createTMitems(self):
        try:
            # 假设当前登录用户ID是1，实际项目中应动态获取
            current_user_id = 1
            dialog = NewTMEntryDialog(current_user_id, self)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                data = dialog.get_data()

                # 简单校验
                if not all([data["source_text"], data["target_text"], data["source_lang"], data["target_lang"]]):
                    QtWidgets.QMessageBox.warning(self, "提示", "请填写所有字段")
                    return

                print("1")
                # 插入数据库，获取新生成的 tm_id 和 created_at
                conn = sqlite3.connect(TM_dao.DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                                           INSERT INTO translation_memory (source_text, target_text, source_lang, target_lang, created_by)
                                           VALUES (?, ?, ?, ?, ?)
                                       ''',
                               (data["source_text"], data["target_text"], data["source_lang"], data["target_lang"],
                                data["created_by"]))
                conn.commit()
                print("2")
                tm_id = cursor.lastrowid

                # 查询刚插入的 created_at
                cursor.execute("SELECT created_at FROM translation_memory WHERE tm_id=?", (tm_id,))
                created_at = cursor.fetchone()[0]

                conn.close()
                print("3")
                # 在表格中插入新行并填充数据
                row_count = self.tableWidget_item.rowCount()
                self.tableWidget_item.insertRow(row_count)

                # 填充各列
                self.tableWidget_item.setItem(row_count, self.col_id, QTableWidgetItem(str(tm_id)))

                # 源文本和目标文本用 EditableTextEdit
                source_text_edit = EditableTextEdit()
                source_text_edit.setPlainText(data["source_text"])
                source_text_edit.setReadOnly(True)
                self.tableWidget_item.setCellWidget(row_count, self.col_source_text, source_text_edit)

                target_text_edit = EditableTextEdit()
                target_text_edit.setPlainText(data["target_text"])
                target_text_edit.setReadOnly(True)
                self.tableWidget_item.setCellWidget(row_count, self.col_target_text, target_text_edit)

                self.tableWidget_item.setItem(row_count, self.col_source_lang,
                                              QTableWidgetItem(data["source_lang"]))
                self.tableWidget_item.setItem(row_count, self.col_target_lang,
                                              QTableWidgetItem(data["target_lang"]))
                self.tableWidget_item.setItem(row_count, self.col_create_by,
                                              QTableWidgetItem(str(data["created_by"])))
                self.tableWidget_item.setItem(row_count, self.col_create_at, QTableWidgetItem(str(created_at)))

                # 新增行默认未编辑状态
                self.row_edit_status[row_count] = False

                QtWidgets.QMessageBox.information(self, "成功", f"新条目已创建，ID: {tm_id}")


        except Exception as e:
            print("创建出错:", e)

    def editTMitems(self):
        try:
            selected_ranges = self.tableWidget_item.selectedRanges()
            if not selected_ranges:
                QtWidgets.QMessageBox.warning(self, "提示", "请先选择一行进行编辑")
                return
            row = selected_ranges[0].topRow()


            row = selected_ranges[0].topRow()
            self.set_table_cells_read(row , False)#将选中行的编辑状态改为可编辑
            self.row_edit_status[row] = True  # 标记为编辑未保存
            QtWidgets.QMessageBox.warning(self, "提示", "可以编辑" + str(row + 1))

        except Exception as ex:
            print("edit wrong" , ex)

    def saveTMitems(self):
        try:
            selected_range = self.tableWidget_item.selectedRanges()
            if not selected_range:
                QtWidgets.QMessageBox.warning(self, "提示", "请先选择一行进行保存")
                return

            row = selected_range[0].topRow()

            self.set_table_cells_read(row, True)  # 将选中行的编辑状态改为不可编辑

            self.push_item_data(row , False)
            self.row_edit_status[row] = False  # 标记为已保存
            QtWidgets.QMessageBox.warning(self, "提示", "已经保存" + str(row + 1))
            #保存后取消选中
            self.tableWidget_item.clearSelection()

        except Exception as ex:
            print("save wrong" , ex)

    def deleteTMitems(self):
        try:
            selected_range = self.tableWidget_item.selectedRanges()
            if not selected_range:
                QtWidgets.QMessageBox.warning(self, "提示", "请先选择一行进行删除")
                return

            row = selected_range[0].topRow()
            # 删除该行
            self.push_item_data(row, True)
            self.tableWidget_item.removeRow(row)
            # 清理状态
            if row in self.row_edit_status:
                del self.row_edit_status[row]

            QtWidgets.QMessageBox.warning(self, "提示", "已删除行" + str(row + 1))
        except Exception as ex:
            print("delete wrong" , ex)

    #在条目取消选中时自动保存并进行提示
    def on_selection_changed(self):
        try:
            if  self.ignore_selection_change:
                return

            # 获取当前选中行号集合
            current_selected_rows = set(item.row() for item in self.tableWidget_item.selectedItems())
            # 计算取消选中的行号
            deselected_rows = self.prev_selected_items - current_selected_rows

            for row in deselected_rows:
                if self.row_edit_status.get(row, False):
                    self.set_table_cells_read(row, True)
                    self.push_item_data(row, False)
                    self.row_edit_status[row] = False
                    QtWidgets.QMessageBox.information(self, "提示", f"第 {row + 1} 行已自动保存")


                # 只有编辑未保存的行才自动保存


            # 更新 prev_selected_items 为当前选中行号集合
            self.prev_selected_items = current_selected_rows

        except Exception as ex:
            print("on_selection wrong" , ex)
    # 将table_widget的选中单元格全设为只读

    def set_table_cells_read(self, count, read: bool):
        source_text = self.tableWidget_item.cellWidget(count, self.col_source_text)
        target_text = self.tableWidget_item.cellWidget(count, self.col_target_text)
        for column in range(self.tableWidget_item.columnCount()):

            if column == self.col_source_text:
                source_text.setReadOnly(read)
            elif column == self.col_target_text:
                target_text.setReadOnly(read)
            else:
                item = self.tableWidget_item.item(count, column)
                if item is not None:
                    if read:
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # 设置为不可编辑
                    else:
                        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)  # 设置为可编辑

    """
    以下属于与数据库的交互，TM_dao
    """
    #用于初始化展示翻译记忆库的内容
    def load_tm_data(self):
        # 连接数据库
        conn = sqlite3.connect(TM_dao.DB_FILE)
        cursor = conn.cursor()

        # 查询所有翻译记忆条目
        cursor.execute("SELECT tm_id, source_text, target_text,source_lang , target_lang, created_by, created_at FROM translation_memory")
        rows = cursor.fetchall()

        # 设置表格行数和列数
        self.tableWidget_item.setRowCount(len(rows))
        self.tableWidget_item.setColumnCount(7)  # 根据字段数调整

        # 可以动态设置表头
        self.tableWidget_item.setHorizontalHeaderLabels(['ID', '源文本', '目标文本', '源语言', '目标语言', '创建者', '创建时间'])

        # 填充数据
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                if col_idx in (self.col_source_text, self.col_target_text):
                    text_edit = EditableTextEdit()
                    text_edit.setPlainText(str(value) if value else "")
                    text_edit.setReadOnly(True)
                    self.tableWidget_item.setCellWidget(row_idx, col_idx, text_edit)
                else:
                    item = QTableWidgetItem(str(value) if value else "")
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  # 默认不可编辑
                    self.tableWidget_item.setItem(row_idx, col_idx, item)

        conn.close()


    #将可以自动生成的数据返回，翻译记忆对id ， 创建者 ， 创建时间 ；
    # 对于源文本与目标文本，则等待用户输入
    def get_item_data(self):#得到数据
        '''

        新增行时默认空字符串，ID留空，创建者和时间留空，语言默认可空
        '''
        # 返回字典，key是列号，value是内容
        # 插入数据库，获取新生成的 tm_id 和 created_at

        data = {
            self.col_id: "",
            self.col_source_text: "",
            self.col_target_text: "",
            self.col_source_lang: "",
            self.col_target_lang: "",
            self.col_create_by: "",
            self.col_create_at: ""
        }
        return data

    #将某一行的数据传回
    #is_delete = True ,则将对应位置数据删除 ； is_delete = False , 则更新数据库中的数据
    def push_item_data(self , row , is_delete):
        tm_id_item = self.tableWidget_item.item(row, 0)
        if tm_id_item is None:
            print("该行无有效ID，无法操作")
            return
        try:
            tm_id = int(tm_id_item.text())
        except ValueError:
            print("tm_id格式错误，无法操作")
            return

        if is_delete:
            # 调用删除函数，确保 TM_dao.delete_tm_entry 已定义
            TM_dao.delete_tm_entry(tm_id)
            print(f"已删除 tm_id={tm_id} 的记录")
            return

        # 更新操作
        source_text_widget = self.tableWidget_item.cellWidget(row, self.col_source_text)
        target_text_widget = self.tableWidget_item.cellWidget(row, self.col_target_text)

        source_text = source_text_widget.toPlainText() if source_text_widget else ""
        target_text = target_text_widget.toPlainText() if target_text_widget else ""
        source_lang = self.tableWidget_item.item(row, self.col_source_lang).text()
        target_lang = self.tableWidget_item.item(row, self.col_target_lang).text()


        TM_dao.update_tm_entry(tm_id, source_text=source_text, target_text=target_text,source_lang = source_lang , target_lang = target_lang )
        print(f"已更新 tm_id={tm_id} 的记录")



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TM_items_show()
    window.show()

    sys.exit(app.exec_())