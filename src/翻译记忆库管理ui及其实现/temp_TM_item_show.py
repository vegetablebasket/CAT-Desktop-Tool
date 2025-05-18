import sys
from PyQt5 import QtCore, QtGui, QtWidgets ,uic
from PyQt5.QtWidgets import QAbstractItemView
from enum import Enum

class ItemStatus(Enum):
    EDIT = 'edit'
    SAVE = 'save'
    CREATE = 'create'
    DEFAULT = 'default'

class EditableTextEdit(QtWidgets.QTextEdit):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setReadOnly(True)  # 初始只读

    def focusOutEvent(self, event):
        # 失去焦点时切回只读
        self.setReadOnly(True)
        super().focusOutEvent(event)

class TM_items_show(QtWidgets.QDialog):
    col_source_text = 1
    col_target_text = 2

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
        #按钮功能
        self.pushButton_createTMitems.clicked.connect(self.createTMitems)
        self.pushButton_save.clicked.connect(self.saveTMitems)
        self.pushButton_edit.clicked.connect(self.editTMitems)
        #初始化prev_selected_item
        self.prev_selected_items = set()
        self.ignore_selection_change = True


    def createTMitems(self):
        print("点击了新建按钮")
        try:
            print("点击了新建按钮1")
            data = self.get_item_data()
            item_count = self.tableWidget_item.rowCount()
            self.tableWidget_item.insertRow(item_count)
            print("点击了新建按钮2")
            source_text = EditableTextEdit()
            target_text = EditableTextEdit()
            source_text.setReadOnly(True)
            target_text.setReadOnly(True)
            print("点击了新建按钮3")
            for col in range(self.tableWidget_item.columnCount()):
                print("点击了新建按钮3" + str(col))
                if col == self.col_source_text:
                    self.tableWidget_item.setCellWidget(item_count , col , source_text)
                elif col == self.col_target_text:
                    self.tableWidget_item.setCellWidget(item_count , col , target_text)
                else :
                    text = data.get(col, "")
                    self.tableWidget_item.setItem(item_count ,col ,QtWidgets.QTableWidgetItem(str(text)))
                # 新增行后，选中该行
            self.set_table_cells_read(item_count,True)
            print("点击了新建按钮4")
            self.ignore_selection_change = False
            self.tableWidget_item.selectRow(item_count)
            self.ignore_selection_change = True
            print("点击了新建按钮5")
        except Exception as ex:
            print("创建出错" , ex)

    def editTMitems(self):
        try:
            selected_ranges = self.tableWidget_item.selectedRanges()
            if not selected_ranges:
                QtWidgets.QMessageBox.warning(self, "提示", "请先选择一行进行编辑")
                return
            row = selected_ranges[0].topRow()

            self.selected_row = row
            self.set_table_cells_read(row , False)#将选中行的编辑状态改为可编辑
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

            self.push_item_data(row)
            QtWidgets.QMessageBox.warning(self, "提示", "已经保存" + str(row + 1))
            #保存后取消选中
            self.ignore_selection_change = False
            self.tableWidget_item.clearSelection()
            self.ignore_selection_change = True
        except Exception as ex:
            print("save wrong" , ex)

    #在条目取消选中时自动保存并进行提示

    def on_selection_changed(self):
        try:
            if not self.ignore_selection_change:
                return

                # 获取当前选中行号集合
            current_selected_rows = set()
            for item in self.tableWidget_item.selectedItems():
                current_selected_rows.add(item.row())

            # 计算取消选中的行号
            deselected_rows = self.prev_selected_items - current_selected_rows

            rows_to_save = set()
            for row in deselected_rows:
                rows_to_save.add(row)
                print(f"条目退出选中: 行 {row}")

            for row in rows_to_save:
                self.set_table_cells_read(row, True)
                self.push_item_data(row)
                QtWidgets.QMessageBox.warning(self, "提示", "已经保存" + str(row + 1))

            # 更新 prev_selected_items 为当前选中行号集合
            self.prev_selected_items = current_selected_rows
        except Exception as ex:
            print("on_selection wrong" , ex)
    def get_item_data(self):#得到数据
        '''

        从数据库中得到数据
        '''
        # 返回字典，key是列号，value是内容
        data = {
            0: "id",
            1: "源文本",
            2: "目标文本",
            3: "对应翻译",
            4: "创建者",
            5: "创建时间"
        }
        return data
    #将某一行的数据传回
    def push_item_data(self , row):
        '''
        在执行将数据传到数据库的行为
        '''

    def set_table_cells_read(self , count , read:bool):
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
                    else :
                        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)  # 设置为可编辑

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TM_items_show()
    window.show()

    sys.exit(app.exec_())