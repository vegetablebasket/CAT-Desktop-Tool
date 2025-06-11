"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QDialog, QDialogButtonBox, QHBoxLayout, QGroupBox
)
from PyQt5.QtCore import Qt

from Translation import Fuzzy_match
from dao import table_description_dao


class DualMultiSelectDialog(QDialog):
    def __init__(self, terms, memories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("多选术语库和翻译记忆库")
        self.resize(600, 400)

        self.terms_list = QListWidget()
        self.terms_list.setSelectionMode(QListWidget.MultiSelection)
        for term in terms:
            item = QListWidgetItem(term['tm_name'])
            item.setData(Qt.UserRole, term['id'])
            self.terms_list.addItem(item)

        self.memories_list = QListWidget()
        self.memories_list.setSelectionMode(QListWidget.MultiSelection)
        for mem in memories:
            item = QListWidgetItem(mem['tm_name'])
            item.setData(Qt.UserRole, mem['id'])
            self.memories_list.addItem(item)

        terms_group = QGroupBox("术语库")
        terms_layout = QVBoxLayout()
        terms_layout.addWidget(self.terms_list)
        terms_group.setLayout(terms_layout)

        memories_group = QGroupBox("翻译记忆库")
        memories_layout = QVBoxLayout()
        memories_layout.addWidget(self.memories_list)
        memories_group.setLayout(memories_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        lists_layout = QHBoxLayout()
        lists_layout.addWidget(terms_group)
        lists_layout.addWidget(memories_group)
        main_layout.addLayout(lists_layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

    def selected_terms(self):
        return [(item.text(), item.data(Qt.UserRole)) for item in self.terms_list.selectedItems()]

    def selected_memories(self):
        return [(item.text(), item.data(Qt.UserRole)) for item in self.memories_list.selectedItems()]


class test_demo_show_fuzzy_match(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("测试匹配结果界面")
        self.resize(600, 400)

        self.label = QLabel("匹配结果将在这里显示")
        self.label.setWordWrap(True)

        self.button = QPushButton("查询")
        self.button.clicked.connect(self.on_query_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 预加载数据
        self.terms = self.load_table_names_from_db('terminology')
        self.memories = self.load_table_names_from_db('tm')

    def load_table_names_from_db(self, type_):
        try:
            all_descriptions = table_description_dao.list_table_descriptions_by_type(type_)
            filtered = [desc for desc in all_descriptions if 'id' in desc and 'tm_name' in desc]
            return filtered
        except Exception as e:
            print(f"加载记忆库名称失败: {e}")
            return []

    def on_query_clicked(self):
        dialog = DualMultiSelectDialog(self.terms, self.memories, self)
        if dialog.exec_() == QDialog.Accepted:
            #selected_terms = dialog.selected_terms()
            selected_memories = dialog.selected_memories()

            try:
                match = Fuzzy_match.Fuzzy_match(None, selected_memories)
                text = match.fuzzy_match_table_terms(0.3)

                if not text:  # 结果为空
                    self.label.setText("匹配失败")
                else:
                    text_str = "\n".join(
                        [f"库名：{name}，ID：{tm_term_id}，文本：{txt}，译文：{tar_txt},相似度：{float(score):.2f}" for name, tm_term_id, txt, tar_txt, score in
                         text])
                    self.label.setText(text_str)
            except Exception as e:
                self.label.setText(f"模糊匹配出错: {e}")
                print("on_query_clicked wrong :" , e)
        else:
            self.label.setText("取消查询")
"""
import sys

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QHBoxLayout, QGroupBox, QLineEdit, QMessageBox, QApplication, QTextEdit
)
from PyQt5.QtCore import Qt

from Translation import Fuzzy_match
from dao import table_description_dao
from dao.Terminology_dao import list_terminologies


class test_demo_show_fuzzy_match(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("测试匹配结果界面")
        self.resize(800, 600)

        # 将输入控件改为 QTextEdit
        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("请输入查询目标文本")
        self.input_edit.setMinimumHeight(100)  # 设置输入框最小高度，方便多行输入

        # 术语库列表
        self.terms_list = QListWidget()
        self.terms_list.setSelectionMode(QListWidget.MultiSelection)


        # 记忆库列表
        self.memories_list = QListWidget()
        self.memories_list.setSelectionMode(QListWidget.MultiSelection)


        # 加载数据
        self.terms = self.load_table_names_from_db('terminology')
        self.memories = self.load_table_names_from_db('tm')

        for term in self.terms:
            item = QListWidgetItem(term['tm_name'])
            item.setData(Qt.UserRole, term['id'])
            self.terms_list.addItem(item)

        for mem in self.memories:
            item = QListWidgetItem(mem['tm_name'])
            item.setData(Qt.UserRole, mem['id'])
            self.memories_list.addItem(item)

        # 术语库分组框
        terms_group = QGroupBox("术语库")
        terms_layout = QVBoxLayout()
        terms_layout.addWidget(self.terms_list)
        terms_group.setLayout(terms_layout)

        # 记忆库分组框
        memories_group = QGroupBox("翻译记忆库")
        memories_layout = QVBoxLayout()
        memories_layout.addWidget(self.memories_list)
        memories_group.setLayout(memories_layout)

        # 查询按钮
        self.button = QPushButton("查询")
        self.button.clicked.connect(self.on_query_clicked)

        # 结果显示标签
        self.label = QLabel("匹配结果将在这里显示")
        self.label.setWordWrap(True)
        self.label.setMinimumHeight(100)  # 给结果显示区域留出一定高度

        # 布局组合
        lists_layout = QHBoxLayout()
        lists_layout.addWidget(terms_group)
        lists_layout.addWidget(memories_group)

        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("查询目标："))
        main_layout.addWidget(self.input_edit)
        main_layout.addLayout(lists_layout)
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.button)


        self.setLayout(main_layout)

    def load_table_names_from_db(self, type_):
        try:
            all_descriptions = table_description_dao.list_table_descriptions_by_type(type_)
            filtered = [desc for desc in all_descriptions if 'id' in desc and 'tm_name' in desc]
            return filtered
        except Exception as e:
            print(f"加载记忆库名称失败: {e}")
            return []

    def exact_match_terms_in_text(self,input_text, table_name):
        """
        在输入文本中查找术语库中所有术语（term），做精确子串匹配
        返回匹配的术语条目列表
        """
        matched_terms = []
        # 先获取该术语库所有条目
        terms = list_terminologies(table_name)
        for term_entry in terms:
            term_text = term_entry['term']
            if term_text and term_text in input_text:
                matched_terms.append(term_entry)
        return matched_terms


    def on_query_clicked(self):
        query_text = self.input_edit.toPlainText().strip()
        if not query_text:
            QMessageBox.warning(self, "输入错误", "请输入查询目标文本！")
            return

        selected_terms = [(item.text(), item.data(Qt.UserRole)) for item in self.terms_list.selectedItems()]
        selected_memories = [(item.text(), item.data(Qt.UserRole)) for item in self.memories_list.selectedItems()]

        # 只能选择术语库或翻译记忆库其中一个，不能同时选择
        if selected_terms and selected_memories:
            QMessageBox.warning(self, "选择错误", "术语库和翻译记忆库只能选择其中一个！")
            return

        if not selected_terms and not selected_memories:
            QMessageBox.warning(self, "选择错误", "请至少选择术语库或翻译记忆库中的一项！")
            return

        try:
            if selected_memories:
                # 只选了翻译记忆库，执行模糊匹配
                match = Fuzzy_match.Fuzzy_match(query_text, selected_memories)
                text = match.fuzzy_match_table_terms(0.3)

                if not text:
                    self.label.setText("模糊匹配失败，无匹配的句段")
                else:
                    text_str = "\n".join(
                        [f"库名：{name}，ID：{tm_term_id}，文本：{txt}，译文：{tar_txt}, 相似度：{float(score):.2f}"
                         for name, tm_term_id, txt, tar_txt, score in text])
                    self.label.setText(text_str)

            elif selected_terms:
                # 只选了术语库，执行精确匹配
                matched_terms_all = []
                for name, _ in selected_terms:
                    matched_terms = self.exact_match_terms_in_text(query_text, name)
                    matched_terms_all.extend(matched_terms)

                if not matched_terms_all:
                    self.label.setText("精确匹配失败，无匹配的术语")
                else:
                    display_text = ""
                    for term in matched_terms_all:
                        display_text += f"术语：{term['term']}，译文：{term['translation']}，定义：{term.get('definition', '')}\n"
                    self.label.setText(display_text)

        except Exception as e:
            self.label.setText(f"匹配出错: {e}")
            print("on_query_clicked wrong:", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = test_demo_show_fuzzy_match()
    main_win.show()
    sys.exit(app.exec_())
