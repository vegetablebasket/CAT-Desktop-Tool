import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets ,uic
from PyQt5.QtWidgets import QMessageBox

from dao import Terminology_dao, table_description_dao
from 术语库 import Terminology_show  # 你已有的显示模块



class CreateTerminologyShowDialog(QtWidgets.QDialog ):
    def __init__(self , text = None):
        super().__init__()
        self.original_data = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "Create_Terminology.ui")
        uic.loadUi(ui_path, self)

        self.Create_Terminology_sure.clicked.connect(self.accept)
        self.Create_Terminology_Cancle.clicked.connect(self.reject)

        self.push_data(text)
    def get_data(self):
        #获取用户输入的数据，以字典的形式返回
        return {
            "Terminology_name": self.lineEdit_Terminology_name.text().strip(),
            "description": self.textEdit_Terminology_descripte.toPlainText().strip()
        }

    def push_data(self, data):
        if data is None:
            return
        self.original_data = data.copy()  # 备份原始数据
        self.lineEdit_Terminology_name.setText(data["Terminology_name"])
        self.textEdit_Terminology_descripte.setText(data["description"])

    def get_edited_data(self):
        current_name = self.lineEdit_Terminology_name.text()
        current_description = self.textEdit_Terminology_descripte.toPlainText()

        if self.original_data is None:
            return None  # 没有原始数据，无法判断

        # 比较是否有修改
        if (current_name != self.original_data["Terminology_name"] or
                current_description != self.original_data["description"]):
            # 返回修改后的结果
            return {
                "Terminology_name": current_name,
                "description": current_description
            }
        else:
            # 没有修改，返回空
            return None

class Widget_Terminology(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "Terminology_manage_show.ui")
        uic.loadUi(ui_path, self)

        self.resize(800, 600)
        self.setWindowTitle("术语库管理")

        self.pushButton_createTerminology.clicked.connect(self.createTerminology)
        self.pushButton_deleteTerminology.clicked.connect(self.deleteTerminology)
        self.pushButton_edit.clicked.connect(self.editTerminology)
        self.listView_Terminologylist.doubleClicked.connect(self.on_item_double_clicked)
        self.listView_Terminologylist.clicked.connect(self.on_item_clicked)

        self.groupBox_Terminologydescripte.hide()

        self.current_terminology_name = None
        self.table_type = 'terminology'

        #设置listView的条目模式，并且设置为双击不可编辑,且只能选中一项
        self.entries = self.load_terminology_names_from_db()
        self.model = QtCore.QStringListModel(self.entries)
        self.listView_Terminologylist.setModel(self.model)
        self.listView_Terminologylist.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listView_Terminologylist.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
    def load_terminology_names_from_db(self):
        try:
            all_descriptions = table_description_dao.list_table_descriptions_by_type(self.table_type)
            terminology_names = [desc['tm_name'] for desc in all_descriptions if 'tm_name' in desc]
            return terminology_names
        except Exception as e:
            print(f"加载术语库名称失败: {e}")
            return []

    def createTerminology(self):
        try:
            print("打开新建对话框")
            self.Create_Terminology_show = CreateTerminologyShowDialog()
            result = self.Create_Terminology_show.exec_()
            print("对话框返回结果:", result)

            if result == QtWidgets.QDialog.Accepted:
                data = self.Create_Terminology_show.get_data()
                terminology_name = data["Terminology_name"]

                if not terminology_name:
                    QtWidgets.QMessageBox.warning(self, "输入错误", "术语库名称不能为空！")
                    return

                if terminology_name in self.entries:
                    QtWidgets.QMessageBox.warning(self, "重复错误",
                                                  f"术语库名称 '{terminology_name}' 已存在，请使用其他名称。")
                    return

                self.current_terminology_name = terminology_name
                Terminology_dao.create_user_terminology_table(self.current_terminology_name)
                table_description_dao.insert_table_description(
                    tm_name = Terminology_dao.sanitize_table_name(self.current_terminology_name) ,
                    item_number='0',
                    description=data['description'],
                    owner='owner',
                    table_type=self.table_type
                )

                print("用户输入的数据：", data)

                entry_str = self.current_terminology_name
                self.entries.append(entry_str)
                self.model.setStringList(self.entries)

                QtWidgets.QMessageBox.information(self, "收到数据",
                                                  f"术语库名称：{data['Terminology_name']}\n描述：{data['description']}")
            else:
                print("用户取消输入")
                QtWidgets.QMessageBox.information(self, "取消", "你取消了输入")
        except Exception as e:
            print(f"创建出错: {e}")

    def deleteTerminology(self):
        terminology_name = self.current_terminology_name
        if not terminology_name:
            QtWidgets.QMessageBox.warning(self, "错误", "请选择一个术语库再删除")
            return

        reply = QtWidgets.QMessageBox.question(self, "确认删除", f"确定要删除术语库 {terminology_name} 吗？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                Terminology_dao.delete_terminology_table(terminology_name)
                table_description_dao.delete_table_description(terminology_name, self.table_type)

                self.entries = [e for e in self.entries if e != terminology_name]
                self.model.setStringList(self.entries)
                QtWidgets.QMessageBox.information(self, "成功", f"术语库 {terminology_name} 删除成功")
                self.groupBox_Terminologydescripte.hide()
                self.current_terminology_name = None
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "错误", f"删除失败: {e}")
                print("删除数据库错误", e)

    def editTerminology(self):
        """启用选中行编辑"""
        try:
            selected_indexes = self.listView_Terminologylist.selectedIndexes()
            if selected_indexes:
                index = selected_indexes[0]
                item_text = self.model.data(index, QtCore.Qt.DisplayRole)
                print("当前选中条目文本：", item_text)

                text_all = table_description_dao.get_table_description(item_text, self.table_type)
                table_id = table_description_dao.get_item_id(text_all['tm_name'],text_all['table_type'])
                text = {'Terminology_name': text_all['tm_name'],'description': text_all['description']}
                self.Create_Terminology_show = CreateTerminologyShowDialog(text)
                result = self.Create_Terminology_show.exec_()
                print("对话框返回结果:", result)

                if result == QtWidgets.QDialog.Accepted:
                    data = self.Create_Terminology_show.get_edited_data()
                    table_description_dao.update_item_by_id(table_id, data['Terminology_name'], data['description'])
                    Terminology_dao.rename_table(item_text, data['Terminology_name'])
                    self.listView_Terminologylist.model().setData(index, data['Terminology_name'], QtCore.Qt.EditRole)
                    self.groupBox_Terminologydescripte.hide()
            else:
                print("没有选中任何条目")
                QMessageBox.warning(self, "提示", "请先选择一行进行编辑！")
                return
        except Exception as e:
            print("编辑出错" ,e)

    def on_item_double_clicked(self, index: QtCore.QModelIndex):
        try:
            item_text = self.model.data(index, QtCore.Qt.DisplayRole)
            self.Terminology_show = Terminology_show.TerminologyItemsShow(name=item_text)
            result = self.Terminology_show.exec()

            self.groupBox_Terminologydescripte.hide()

        except Exception as e:
            print(f"双击术语库出错: {e}")

    def on_item_clicked(self, index: QtCore.QModelIndex):
        try:
            item_text = self.model.data(index, QtCore.Qt.DisplayRole)
            self.current_terminology_name = str(item_text)
            self.groupBox_Terminologydescripte.show()
            self.current_terminology_name = Terminology_dao.sanitize_table_name(self.current_terminology_name)
            data = self.get_data(self.current_terminology_name)
            # 设置界面控件显示数据，类似 Widget_TM.on_item_clicked
            self.set_lineedit_read(True)

            # 使用 findChild 方法获取控件
            lineEdit_Terminologyname = self.groupBox_Terminologydescripte.findChild(QtWidgets.QLineEdit, "lineEdit_Terminologyname")
            lineEdit_Terminologynumber = self.groupBox_Terminologydescripte.findChild(QtWidgets.QLineEdit, "lineEdit_Terminologynumber")
            lineEdit_owner = self.groupBox_Terminologydescripte.findChild(QtWidgets.QLineEdit, "lineEdit_owner")
            lineEdit_Terminologycreatetime = self.groupBox_Terminologydescripte.findChild(QtWidgets.QLineEdit, "lineEdit_Terminologycreatetime")
            textEdit_description = self.groupBox_Terminologydescripte.findChild(QtWidgets.QTextEdit, "textEdit_description")

            # 确保控件存在后再设置文本
            if lineEdit_Terminologyname:
                lineEdit_Terminologyname.setText(data.get('tm_name', ''))
            if textEdit_description:
                textEdit_description.setText(data.get('description', ''))
            if lineEdit_Terminologynumber:
                lineEdit_Terminologynumber.setText(str(data.get('item_number', '')))
            if lineEdit_owner:
                lineEdit_owner.setText(str(data.get('owner', '')))
            if lineEdit_Terminologycreatetime:
                lineEdit_Terminologycreatetime.setText(str(data.get('create_time', '')))

        except Exception as e:
            print(f"单击术语库条目时发生错误: {e}")

    def set_lineedit_read(self, read: bool):
        lineedits = [
            self.groupBox_Terminologydescripte.findChild(QtWidgets.QLineEdit, "lineEdit_Terminologyname"),
            self.groupBox_Terminologydescripte.findChild(QtWidgets.QLineEdit, "lineEdit_Terminologynumber"),
            self.groupBox_Terminologydescripte.findChild(QtWidgets.QLineEdit, "lineEdit_owner"),
            self.groupBox_Terminologydescripte.findChild(QtWidgets.QLineEdit, "lineEdit_Terminologycreatetime"),

        ]
        for le in lineedits:
            le.setReadOnly(read)
        textEdit_description = self.groupBox_Terminologydescripte.findChild(QtWidgets.QTextEdit, "textEdit_description")
        if textEdit_description:
            textEdit_description.setReadOnly(read)

    def get_data(self, item_text):
        data = table_description_dao.get_table_description(item_text, self.table_type)
        print(data)
        if data is None:
            data = {
                'tm_name': item_text,
                'item_number': '0',
                'description': '',
                'owner': None,
                'create_time': None
            }
        return data



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Widget_Terminology()
    window.show()

    sys.exit(app.exec_())
