# create_project_gui.py
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt
from project import Project

class Createproject(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("创建新项目")
        self.setFixedSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # 项目名称
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("项目名称")

        # 项目描述
        self.project_desc_input = QLineEdit()
        self.project_desc_input.setPlaceholderText("项目描述")

        # 源语言
        self.source_lang_tree = QTreeWidget()
        self.source_lang_tree.setHeaderLabels(["源语言"])
        self.source_lang_tree.setMaximumHeight(120)
        self.source_checkboxes = []
        self._add_languages(self.source_lang_tree, self.source_checkboxes, single_select=True)

        # 目标语言
        self.target_lang_tree = QTreeWidget()
        self.target_lang_tree.setHeaderLabels(["目标语言"])
        self.target_lang_tree.setMaximumHeight(120)
        self.target_checkboxes = []
        self._add_languages(self.target_lang_tree, self.target_checkboxes, single_select=False)

        # 上传文件
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("请选择文件")
        upload_btn = QPushButton("上传")
        upload_btn.clicked.connect(self.upload_file)


        # 使用记忆库
        self.use_memory_checkbox = QCheckBox("使用记忆库")
        self.use_memory_checkbox.stateChanged.connect(self.toggle_memory_inputs)

        self.memory_path_input = QLineEdit()
        self.memory_path_input.setPlaceholderText("请选择或新建记忆库文件")
        self.memory_path_input.setVisible(False)
        memory_upload_btn = QPushButton("上传")
        memory_upload_btn.clicked.connect(self.upload_memory_file)
        memory_upload_btn.setVisible(False)
        self.memory_upload_btn = memory_upload_btn  # 保存引用便于切换可见性

        memory_create_btn = QPushButton("新建")
        memory_create_btn.clicked.connect(self.create_memory_file)
        memory_create_btn.setVisible(False)
        self.memory_create_btn = memory_create_btn

        # 使用术语库
        self.use_termbase_checkbox = QCheckBox("使用术语库")
        self.use_termbase_checkbox.stateChanged.connect(self.toggle_termbase_inputs)

        self.termbase_path_input = QLineEdit()
        self.termbase_path_input.setPlaceholderText("请选择术语库文件")
        self.termbase_path_input.setVisible(False)
        termbase_upload_btn = QPushButton("上传")
        termbase_upload_btn.clicked.connect(self.upload_termbase_file)
        termbase_upload_btn.setVisible(False)
        self.termbase_upload_btn = termbase_upload_btn
        termbase_create_btn = QPushButton("新建")
        termbase_create_btn.clicked.connect(self.create_termbase_file)
        termbase_create_btn.setVisible(False)
        self.termbase_create_btn = termbase_create_btn


        # 创建按钮
        create_btn = QPushButton("创建项目")
        create_btn.clicked.connect(self.define)

        # 布局填充
        main_layout.addWidget(QLabel("项目名称:"))
        main_layout.addWidget(self.project_name_input)

        main_layout.addWidget(QLabel("项目描述:"))
        main_layout.addWidget(self.project_desc_input)

        main_layout.addWidget(QLabel("源语言:"))
        main_layout.addWidget(self.source_lang_tree)

        main_layout.addWidget(QLabel("目标语言:"))
        main_layout.addWidget(self.target_lang_tree)

        main_layout.addWidget(QLabel("上传文件:"))
        h_file_layout = QHBoxLayout()
        h_file_layout.addWidget(self.file_path_input)
        h_file_layout.addWidget(upload_btn)
        main_layout.addLayout(h_file_layout)

        # 添加到布局中
        main_layout.addWidget(self.use_memory_checkbox)
        h_memory_layout = QHBoxLayout()
        h_memory_layout.addWidget(self.memory_path_input)
        h_memory_layout.addWidget(self.memory_upload_btn)
        h_memory_layout.addWidget(self.memory_create_btn)
        main_layout.addLayout(h_memory_layout)

        main_layout.addWidget(self.use_termbase_checkbox)
        h_termbase_layout = QHBoxLayout()
        h_termbase_layout.addWidget(self.termbase_path_input,stretch=4)
        h_termbase_layout.addWidget(self.termbase_upload_btn,stretch=1)
        h_termbase_layout.addWidget(self.termbase_create_btn,stretch=1)
        main_layout.addLayout(h_termbase_layout)


        main_layout.addWidget(create_btn)

        self.setLayout(main_layout)

    def _add_languages(self, tree_widget, checkbox_list, single_select=False):
        parent = QTreeWidgetItem(tree_widget)
        parent.setText(0, "语言选项")

        for lang in ["中文", "English", "日文", "韩文"]:
            child = QTreeWidgetItem(parent)
            checkbox = QCheckBox(lang)
            checkbox_list.append(checkbox)
            tree_widget.setItemWidget(child, 0, checkbox)

        if single_select:
            # 实现互斥逻辑
            def make_exclusive(checkbox):
                def handler(state):
                    if state == Qt.CheckState.Checked.value:
                        for cb in checkbox_list:
                            if cb != checkbox:
                                cb.setChecked(False)
                return handler

            for cb in checkbox_list:
                cb.stateChanged.connect(make_exclusive(cb))

    def toggle_memory_inputs(self, state):
        visible = state == Qt.CheckState.Checked.value
        self.memory_path_input.setVisible(visible)
        self.memory_upload_btn.setVisible(visible)
        self.memory_create_btn.setVisible(visible)

    def toggle_termbase_inputs(self, state):
        visible = state == Qt.CheckState.Checked.value
        self.termbase_path_input.setVisible(visible)
        self.termbase_upload_btn.setVisible(visible)
        self.termbase_create_btn.setVisible(visible)

    def upload_memory_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择记忆库文件", "", "All Files (*)")
        if path:
            self.memory_path_input.setText(path)

    def upload_termbase_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择术语库文件", "", "All Files (*)")
        if path:
            self.termbase_path_input.setText(path)

    def upload_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if path:
            self.file_path_input.setText(path)

    def create_memory_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "新建记忆库文件", "", "TM Files (*.tmx);;All Files (*)")
        if path:
            self.memory_path_input.setText(path)
            # 可选：创建一个空文件或写入初始结构
            with open(path, 'w', encoding='utf-8') as f:
                f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?><tmx version=\"1.4\"></tmx>")
    def create_termbase_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "新建术语库文件", "", "TM Files (*.tmx);;All Files (*)")
        if path:
            self.termbase_path_input.setText(path)
            # 可选：创建一个空文件或写入初始结构
            with open(path, 'w', encoding='utf-8') as f:
                f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?><tmx version=\"1.4\"></tmx>")
    def define(self):
        # 获取表单数据
        name = self.project_name_input.text()
        description = self.project_desc_input.text()
        file_path = self.file_path_input.text()
        use_memory = self.use_memory_checkbox.isChecked()
        use_termbase = self.use_termbase_checkbox.isChecked()

        # 源语言

        for cb in self.source_checkboxes:
            if cb.isChecked():
                source_language = cb.text()
                break

        # 目标语言
        target_languages = [cb.text() for cb in self.target_checkboxes if cb.isChecked()]

        # 验证必填字段
        if not name or not source_language or not target_languages or not file_path:
            print("请填写所有必填字段")
            return

        memory_path = self.memory_path_input.text() if use_memory else None
        termbase_path = self.termbase_path_input.text() if use_termbase else None

        project = Project(
            name=name,
            description=description,
            source_language=source_language,
            target_languages=target_languages,
            file_path=file_path,
            use_memory=use_memory,
            memory_path=memory_path,
            use_termbase=use_termbase,
            termbase_path=termbase_path
        )

        # 创建项目文件
        if project.create():
            print("项目创建成功")
            self.accept()
        else:
            print("项目创建失败")
if __name__ == "__main__":
    app = QApplication([])
    win = Createproject()
    win.show()
    app.exec()
