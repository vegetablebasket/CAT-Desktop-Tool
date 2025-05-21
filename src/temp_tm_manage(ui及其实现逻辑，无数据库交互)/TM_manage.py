import sys
from PyQt5 import QtCore, QtGui, QtWidgets ,uic


import temp_TM_item_show

class CreateTMShowDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("Create_TM_show.ui", self)

        self.Create_TM_sure.clicked.connect(self.accept)
        self.Create_TM_Cancle.clicked.connect(self.reject)

    def get_data(self):
        #获取用户输入的数据，以字典的形式返回
        return {
            "TM_name": self.lineEdit_TM_name.text().strip(),
            "source_language": self.lineEdit_TM_source_language.text().strip(),
            "target_language": self.lineEdit_TM_targetlanguage.text().strip(),
            "description": self.textEdit_TM_descripte.toPlainText().strip()
        }



class Widget_TM(QtWidgets.QWidget):
    def __init__(self):
        super(Widget_TM, self).__init__()
        uic.loadUi("TM_manage_show.ui", self)
        self.resize(800, 600)
        self.setWindowTitle("翻译记忆库管理")

        self.pushButton.clicked.connect(self.close_window)
        self.pushButton_createTM.clicked.connect(self.createTM)
        self.pushButton_deleteTM.clicked.connect(self.deleteTM)
        self.groupBox_TMdescripte.hide()


        #设置实例模型
        self.entries = ["记忆库_1" , "记忆库_2"]
        self.model = QtCore.QStringListModel(self.entries)
        self.listView_TMlist.setModel(self.model)
        self.listView_TMlist.doubleClicked.connect(self.on_item_double_clicked)
        self.listView_TMlist.clicked.connect(self.on_item_clicked)

    def close_window(self):
        self.close()

    #使组件只读
    def set_lineedit_read(self, read: bool):
        lineedits = [
            self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMname"),
            self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMlanguage"),
            self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMnumber"),
            self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_owner"),
            self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMcreatetime")
        ]
        for le in lineedits:
            le.setReadOnly(read)

    def createTM(self):
        print("打开新建对话框")
        self.Create_TM_show = CreateTMShowDialog()
        result = self.Create_TM_show.exec_()
        print("对话框返回结果:", result)

        if result == QtWidgets.QDialog.Accepted:
            data = self.Create_TM_show.get_data() #CreateTMShowDialog类中的方法，不是Widget_TM中的
            print("用户输入的数据：", data)
            # 构造显示字符串，比如显示记忆库名称和语言对
            entry_str = f"{data['TM_name']} ({data['source_language']} -> {data['target_language']})"

            # 添加到条目列表
            self.entries.append(entry_str)

            # 更新模型，刷新listView显示
            self.model.setStringList(self.entries)

            QtWidgets.QMessageBox.information(self, "收到数据", f"记忆库名称：{data['TM_name']}\n"
                                                                f"源语言：{data['source_language']}\n"
                                                                f"目标语言：{data['target_language']}\n"
                                                                f"描述：{data['description']}")
        else:
            print("用户取消输入")
            QtWidgets.QMessageBox.information(self, "取消", "你取消了输入")

    #删除记忆库
    def deleteTM(self):
        # 获取选中的索引列表
        selected_indexes = self.listView_TMlist.selectionModel().selectedIndexes()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "提示", "请先选择要删除的记忆库条目")
            return

        # 逆序删除，避免索引变化导致删除错误
        rows = sorted(set(index.row() for index in selected_indexes), reverse=True)
        rows_str = ", ".join(str(r + 1) for r in rows)
        QtWidgets.QMessageBox.warning(self, "提示", f"删除的记忆库条目为：{rows_str }")
        for row in rows:
            # 从 entries 列表中删除对应条目
            del self.entries[row]
        self.delete_data(rows)
        # 更新模型，刷新显示
        self.model.setStringList(self.entries)

   #双击跳转界面temp_TM_item_show
    def on_item_double_clicked(self, index:QtCore.QModelIndex):
        try:
            item_text = self.model.data(index, QtCore.Qt.DisplayRole)
            self.TM_item_show = temp_TM_item_show.TM_items_show(name=item_text)
            self.TM_item_show.exec()
        except Exception as e:
            print("双击出错" , e)
    #单击跳出预览界面
    def on_item_clicked(self, index: QtCore.QModelIndex):
        try:
            item_text = self.model.data(index, QtCore.Qt.DisplayRole)
            self.groupBox_TMdescripte.show()
            data = self.get_data(item_text)
            self.set_lineedit_read(True)
            print("1")
            # 使用 findChild 方法获取控件
            lineEdit_TMname = self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMname")
            lineEdit_TMlanguage = self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMlanguage")
            lineEdit_TMnumber = self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMnumber")
            lineEdit_owner = self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_owner")
            lineEdit_TMcreatetime = self.groupBox_TMdescripte.findChild(QtWidgets.QLineEdit, "lineEdit_TMcreatetime")
            print("2")
            # 确保控件存在后再设置文本
            if lineEdit_TMname:
                lineEdit_TMname.setText(data.get('TM_name', ''))
            if lineEdit_TMlanguage:
                lineEdit_TMlanguage.setText(data.get('language', ''))
            if lineEdit_TMnumber:
                lineEdit_TMnumber.setText(str(data.get('num', '')))
            if lineEdit_owner:
                lineEdit_owner.setText(data.get('owner', ''))
            if lineEdit_TMcreatetime:
                lineEdit_TMcreatetime.setText(data.get('create_time', ''))
            print("3")
            #设置名字
            name_text = lineEdit_TMname.text()
            self.groupBox_TMdescripte.setTitle(f"{name_text} 预览")
            print("4")
        except Exception as e:
            print(f"单击条目时发生错误: {e}")

    #从数据库得到数据 ,item_text相当于选中的条目文本，相当于'库名（源语言 -> 目标语言）'
    #或许可以改为其他关键字，
    def get_data(self , item_text):
        data = {'TM_name' : '库名' ,'language': '' , 'num': 0 , 'owner' : 'owner' , 'create_time' : 'time'}
        '''
        从数据库得到数据

        '''

        return data

    #删除数据库相应的数据，rows是listview中的行号列表
    def delete_data(self, rows):
        """
            根据行号删除数据库中对应的记忆库条目
            :param rows: List[int]，要删除条目的索引列表（逆序）
        """
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Widget_TM()
    window.show()

    sys.exit(app.exec_())
