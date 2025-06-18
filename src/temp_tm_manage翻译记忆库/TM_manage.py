import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets ,uic
from PyQt5.QtWidgets import QMessageBox

# 获取 src 目录的绝对路径
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 现在可以导入 dao 下的模块
from dao import TM_dao , table_description_dao

from temp_tm_manage翻译记忆库 import temp_TM_item_show

class CreateTMShowDialog(QtWidgets.QDialog):
    def __init__(self , text =None):
        super().__init__()
        self.original_data = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "Create_TM_show.ui")
        uic.loadUi(ui_path, self)

        self.Create_TM_sure.clicked.connect(self.accept)
        self.Create_TM_Cancle.clicked.connect(self.reject)

        self.push_data(text)
    def get_data(self):
        #获取用户输入的数据，以字典的形式返回
        return {
            "TM_name": self.lineEdit_TM_name.text().strip(),
            "description": self.textEdit_TM_descripte.toPlainText().strip()
        }
    def push_data(self, data):
        if data is None:
            print("push_data : data is None")
            return
        self.original_data = data.copy()  # 备份原始数据
        self.lineEdit_TM_name.setText(data["TM_name"])
        self.textEdit_TM_descripte.setText(data["description"])

    def get_edited_data(self):
        current_name = self.lineEdit_TM_name.text()
        current_description = self.textEdit_TM_descripte.toPlainText()

        if self.original_data is None:
            return None  # 没有原始数据，无法判断

        # 比较是否有修改
        if (current_name != self.original_data["TM_name"] or
                current_description != self.original_data["description"]):
            # 返回修改后的结果
            return {
                "TM_name": current_name,
                "description": current_description
            }
        else:
            # 没有修改，返回空
            return None


class Widget_TM(QtWidgets.QWidget):
    def __init__(self):
        super(Widget_TM, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "TM_manage_show.ui")
        uic.loadUi(ui_path, self)

        self.resize(800, 600)
        self.setWindowTitle("翻译记忆库管理")

        self.pushButton.clicked.connect(self.close_window)
        self.pushButton_createTM.clicked.connect(self.createTM)
        self.pushButton_edit.clicked.connect(self.editTM)
        self.pushButton_deleteTM.clicked.connect(self.deleteTM)
        self.groupBox_TMdescripte.hide()

        self.current_TM_name = None
        self.table_type = 'tm'

        # 从数据库加载记忆库名称列表
        self.entries = self.load_tm_names_from_db()
        self.model = QtCore.QStringListModel(self.entries)
        self.listView_TMlist.setModel(self.model)
        self.listView_TMlist.doubleClicked.connect(self.on_item_double_clicked)
        self.listView_TMlist.clicked.connect(self.on_item_clicked)
        self.listView_TMlist.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listView_TMlist.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    def close_window(self):
        self.close()

    def set_lineedit_read(self, read: bool):
        lineedits = [
            self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMname"),
            self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMnumber"),
            self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_owner"),
            self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMcreatetime"),

        ]
        for le in lineedits:
            le.setReadOnly(read)
        textEdit_description = self.groupBox_TMdescripte.findChild(QtWidgets.QTextEdit, "textEdit_description")
        if textEdit_description:
            textEdit_description.setReadOnly(read)
    def load_tm_names_from_db(self):
        """
               从数据库的 table_description 表中获取所有记忆库名称列表
               :return: list[str]
        """
        try:
            # 假设 table_description_dao 有方法 list_table_descriptions_by_type 返回所有记录列表
            all_descriptions = table_description_dao.list_table_descriptions_by_type(self.table_type)
            # all_descriptions 应该是列表，每个元素是 dict，包含 'tm_name' 字段
            tm_names = [desc['tm_name'] for desc in all_descriptions if 'tm_name' in desc]
            return tm_names
        except Exception as e:
            print(f"加载记忆库名称失败: {e}")
            return []

    def createTM(self):
        try :
            print("打开新建对话框")
            self.Create_TM_show = CreateTMShowDialog()
            result = self.Create_TM_show.exec_()
            print("对话框返回结果:", result)

            if result == QtWidgets.QDialog.Accepted:
                data = self.Create_TM_show.get_data()
                tm_name = data["TM_name"]

                # 检查名称是否为空
                if not tm_name:
                    QtWidgets.QMessageBox.warning(self, "输入错误", "记忆库名称不能为空！")
                    return

                # 检查名称是否重复
                if tm_name in self.entries:
                    QtWidgets.QMessageBox.warning(self, "重复错误", f"记忆库名称 '{tm_name}' 已存在，请使用其他名称。")
                    return

                #更新数据库
                self.current_TM_name = TM_dao.sanitize_identifier(data['TM_name'])
                TM_dao.create_user_tm_table(self.current_TM_name )
                table_description_dao.insert_table_description(
                    tm_name=self.current_TM_name,
                    item_number='0',
                    description=data['description'],
                    owner='owner',  # 你需要传入owner，或者默认值
                    table_type=self.table_type
                )

                print("用户输入的数据：", data)

                # 构造显示字符串，比如显示记忆库名称和语言对
                entry_str = self.current_TM_name

                # 添加到条目列表
                self.entries.append(entry_str)

                # 更新模型，刷新listView显示
                self.model.setStringList(self.entries)

                QtWidgets.QMessageBox.information(self, "收到数据", f"记忆库名称：{data['TM_name']}\n"
                                                                    f"描述：{data['description']}")
            else:
                print("用户取消输入")
                QtWidgets.QMessageBox.information(self, "取消", "你取消了输入")
        except Exception as e:
            print(f"创建出错: {e}")
    #编辑记忆库
    def editTM(self):
        """启用选中行编辑"""
        try:
            selected_indexes = self.listView_TMlist.selectedIndexes()
            if selected_indexes:
                index = selected_indexes[0]
                item_text = self.model.data(index, QtCore.Qt.DisplayRole)
                self.current_TM_name = item_text
                print("当前选中条目文本：", item_text)

                text_all = table_description_dao.get_table_description(item_text, self.table_type)
                table_id = table_description_dao.get_item_id(text_all['tm_name'], text_all['table_type'])
                text = {'TM_name': text_all['tm_name'], 'description': text_all['description']}
                self.Create_TM_show = CreateTMShowDialog(text)
                result = self.Create_TM_show.exec_()
                print("对话框返回结果:", result)

                if result == QtWidgets.QDialog.Accepted:
                    data = self.Create_TM_show.get_edited_data()
                    table_description_dao.update_item_by_id(table_id, data['TM_name'], data['description'])
                    TM_dao.rename_table(item_text, data['TM_name'])
                    self.listView_TMlist.model().setData(index, data['TM_name'], QtCore.Qt.EditRole)
                    self.groupBox_TMdescripte.hide()
            else:
                print("没有选中任何条目")
                QMessageBox.warning(self, "提示", "请先选择一行进行编辑！")
                return
        except Exception as e:
            print("编辑出错", e)

    #删除翻译记忆库
    def deleteTM(self):
        tm_name = self.current_TM_name
        if not tm_name:
            QtWidgets.QMessageBox.warning(self, "错误", "请选择一个记忆库再删除")
            return

        reply = QtWidgets.QMessageBox.question(self, "确认删除", f"确定要删除记忆库 {tm_name} 吗？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            try:

                TM_dao.delete_tm_table(TM_dao.sanitize_identifier(tm_name))
                table_description_dao.delete_table_description(tm_name, self.table_type)
                # 从列表中移除对应条目（entries中存的是带语言的字符串，需要匹配）
                self.entries = [e for e in self.entries if tm_name not in e]

                self.model.setStringList(self.entries)
                QtWidgets.QMessageBox.information(self, "成功", f"记忆库 {tm_name} 删除成功")
                self.groupBox_TMdescripte.hide()
                self.current_TM_name = None
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "错误", f"删除失败: {e}")
                print("删除数据库错误",e)

    def on_item_double_clicked(self, index:QtCore.QModelIndex):
        try:
            item_text = self.model.data(index, QtCore.Qt.DisplayRole)
            self.TM_item_show = temp_TM_item_show.TM_items_show(name=item_text)
            self.TM_item_show.exec()
        except Exception as e:
            print(f"双击出错: {e}")


    def on_item_clicked(self, index: QtCore.QModelIndex):
        try:
            item_text = self.model.data(index, QtCore.Qt.DisplayRole)

            self.current_TM_name =TM_dao.sanitize_identifier(item_text )  # 更新当前选中记忆库名

            self.groupBox_TMdescripte.show()
            data = self.get_data(self.current_TM_name)
            self.set_lineedit_read(True)

            # 使用 findChild 方法获取控件
            lineEdit_TMname = self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMname")
            lineEdit_TMnumber = self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMnumber")
            lineEdit_owner = self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_owner")
            lineEdit_TMcreatetime = self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMcreatetime")
            textEdit_description =  self.groupBox_TMdescripte.findChild(QtWidgets.QTextEdit, "textEdit_description")

            # 确保控件存在后再设置文本
            if lineEdit_TMname:
                lineEdit_TMname.setText(data.get('tm_name', ''))
            if textEdit_description:
                textEdit_description.setText(data.get('description', ''))
            if lineEdit_TMnumber:
                lineEdit_TMnumber.setText(str(data.get('item_number', '')))
            if lineEdit_owner:
                lineEdit_owner.setText(str(data.get('owner', '')))
            if lineEdit_TMcreatetime:
                lineEdit_TMcreatetime.setText(str(data.get('create_time', '')))

        except Exception as e:
            print(f"单击条目时发生错误: {e}")

    def get_data(self , item_text):
        """
            从数据库得到数据
            :param item_text: tm_name，记忆库名称
            :return: dict，包含库信息，如果没找到返回默认值
        """
        data = table_description_dao.get_table_description(item_text,self.table_type)
        if data is None:
            # 如果数据库没有对应记录，返回默认值
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
    window = Widget_TM()
    window.show()

    sys.exit(app.exec_())
