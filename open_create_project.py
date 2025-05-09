from PyQt6.QtWidgets import (QLineEdit, QFileDialog, QTextEdit, QComboBox, QListWidget,
                             QTreeWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QDialog, QPushButton,
                             QListWidgetItem,
                             QCheckBox, QTreeWidgetItem, QAbstractItemView)
from PyQt6.QtGui import QFont
import sys
from PyQt6.QtCore import Qt
class Createproject(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("创建新项目")
        self.setFixedSize(1000, 800)
        self.setup_ui()
    def setup_ui(self):
        #主布局与分部局
        main_layout = QHBoxLayout(self)
        #左右布局
        right_layout=QVBoxLayout()
        left_layout=QVBoxLayout()
        #右分部局及大小
        right_layout1=QVBoxLayout()
        right_layout2=QVBoxLayout()
        right_layout3=QVBoxLayout()

        right_layout1.setSpacing(3)
        right_layout1.setContentsMargins(3, 3, 3, 3)
        right_layout2.setSpacing(3)
        right_layout2.setContentsMargins(3, 3, 3, 3)
        right_layout3.setSpacing(3)
        right_layout3.setContentsMargins(3, 3, 3, 3)

        #项目名
        project_name=QLabel("新建项目名称")
        project_name_input=QLineEdit()
        project_name_input.setPlaceholderText("项目名称")

        #项目描述
        project_describe = QLabel("新建项目描述")
        project_describe_input = QLineEdit()
        project_describe_input .setPlaceholderText("项目描述")
        #目标语言选择
        list_tree = QTreeWidget()
        list_tree.setColumnCount(1)
        list_tree.setHeaderLabels(["目标语言"])
        list_tree.setMaximumHeight(130)
            # 创建父项
        parent_item = QTreeWidgetItem(list_tree)
        parent_item.setText(0, "选择目标语言")

            # 创建子项（包含 QCheckBox）
        child_item = QTreeWidgetItem(parent_item)
        child_item.setText(0, "子模板1")

        child_item1 = QTreeWidgetItem(parent_item)
        child_item1.setText(1, "子模板2")

        child_item2 = QTreeWidgetItem(parent_item)
        child_item2.setText(2, "子模板3")

        child_item3= QTreeWidgetItem(parent_item)
        child_item3.setText(3, "子模板4")

        #目标语言选项
        checkBox1 = QCheckBox("English")
        checkBox2=QCheckBox("中文")
        checkBox3=QCheckBox("日文")
        checkBox4=QCheckBox("韩文")

        #原文语言选项
        checkbox1 = QCheckBox("English")
        checkbox2 = QCheckBox("中文")
        checkbox3 = QCheckBox("日文")
        checkbox4 = QCheckBox("韩文")

        #目标语言列表填充
        list_tree.setItemWidget(child_item,0,checkBox1)
        list_tree.setItemWidget(child_item1,0,checkBox2)
        list_tree.setItemWidget(child_item2,0,checkBox3)
        list_tree.setItemWidget(child_item3,0,checkBox4)

        #源语言选择
        source_list=QTreeWidget()
        source_list.setColumnCount(1)
        source_list.setHeaderLabels(["源语言"])
        source_list.setMaximumHeight(130)

        #创建父项
        parton=QTreeWidgetItem(source_list)
        parton.setText(0, "选择源语言")

        #创建子项
        child_tem = QTreeWidgetItem(parton)
        child_tem.setText(0, "语言种类")
        child_tem1 = QTreeWidgetItem(parton)
        child_tem1.setText(1, "语言种类")
        child_tem2= QTreeWidgetItem(parton)
        child_tem2.setText(2, "语言种类")
        child_tem3 = QTreeWidgetItem(parton)
        child_tem3.setText(3, "语言种类")

        #源文件语言填充
        source_list.setItemWidget(child_tem,0,checkbox1)
        source_list.setItemWidget(child_tem1,0,checkbox2)
        source_list.setItemWidget(child_tem2,0,checkbox3)
        source_list.setItemWidget(child_tem3,0,checkbox4)

        #右布局组件填充
        right_layout1.addWidget(project_name)
        right_layout1.addWidget(project_name_input)
        right_layout2.addWidget(project_describe)
        right_layout2.addWidget(project_describe_input)

        #文件路径输入
        filabel = QLabel("请选择要翻译的文件:")
        file_path_input = QLineEdit()
        file_path_input.setPlaceholderText("文件路径将显示在这里")


        # 上传按钮
        upload_button = QPushButton("上传文件")
        upload_button.clicked.connect(self.upload_file)

        #记忆库选择
        menmery=QTreeWidget()
        menmery.setColumnCount(1)
        menmery.setHeaderLabels(["记忆库选择"])

        #父项
        memery_parent=QTreeWidgetItem(menmery)
        memery_parent.setText(0, "是否选择使用记忆库")

        #子项
        memery_child=QTreeWidgetItem(memery_parent)
        memery_child.setText(0, "选择")

        memery_child1=QTreeWidgetItem(memery_parent)
        memery_child1.setText(0, "选择")


        #选项按钮
        box = QCheckBox("是")
        box1 = QCheckBox("新建记忆库")

        #选项构建
        menmery.setItemWidget(memery_child,0,box)
        menmery.setItemWidget(memery_child1,0,box1)



        offi=QTreeWidget()
        offi.setColumnCount(1)
        offi.setHeaderLabels(["术语库"])

        offi_parent=QTreeWidgetItem(offi)
        offi_parent.setText(0, "术语库选择")

        offi_child=QTreeWidgetItem(offi_parent)
        offi_child.setText(0, "选择")
        offi_child1=QTreeWidgetItem(offi_parent)
        offi_child1.setText(1, "选择")

        offibox=QCheckBox("是")
        offibox1=QCheckBox("新建术语库")

        offi.setItemWidget(offi_child,0,offibox)
        offi.setItemWidget(offi_child1,0,offibox1)


        definedo=QPushButton("确认创建")
        definedo.clicked.connect(self.define)

        left_layout.addWidget(menmery)
        left_layout.addWidget(offi)
        left_layout.addWidget(definedo)

        right_layout3.addWidget(filabel)
        right_layout3.addWidget(file_path_input)
        right_layout3.addWidget(upload_button)

        right_layout.addLayout(right_layout1)
        right_layout.addLayout(right_layout2)
        right_layout.addWidget(source_list)
        right_layout.addWidget(list_tree)
        right_layout.addLayout(right_layout3)
        main_layout.addLayout(right_layout)
        main_layout.addLayout(left_layout)


    def upload_file(self):
        # 弹出文件对话框，选择文件
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            self.file_path_input.setText(file_path)  # 显示文件路径

    def define(self):
        print("ok")

if __name__ == "__main__":
    app = QApplication([])
    window = Createproject()
    window.show()
    app.exec()