# src/pages/translation_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QComboBox

import sys
import os

import api_ui
from Translation.ui_select_tmAndterminology import  test_demo_show_fuzzy_match
from api_ui import api_ui_

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dao import translation_fragment_dao

class TranslationPage(QWidget):
    def __init__(self, document_id=None):
        """
        :param document_id: 要编辑的文档ID
        """
        super().__init__()
        self.setWindowTitle("翻译编辑页面")
        self.document_id = document_id
        self.fragments = []  # 当前文档所有段落
        self.current_index = 0  # 当前段落下标

        self.init_ui()
        if document_id is not None:
            self.load_fragments(document_id)

    def init_ui(self):
        # 创建主水平布局，左右分栏
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # 左边：翻译编辑区，放到一个单独的 QWidget 里
        self.left_widget = QWidget()
        left_layout = QVBoxLayout()
        self.left_widget.setLayout(left_layout)

        # 段落进度标签
        self.progress_label = QLabel("段落进度：0/0")
        left_layout.addWidget(self.progress_label)

        # 原文显示标签
        self.source_label = QLabel("原文内容：")
        self.source_label.setWordWrap(True)
        left_layout.addWidget(self.source_label)

        # 译文输入区
        left_layout.addWidget(QLabel("请输入译文："))
        self.text_edit = QTextEdit()
        left_layout.addWidget(self.text_edit)

        # 状态显示标签
        self.status_label = QLabel("当前状态：")
        left_layout.addWidget(self.status_label)

        # 翻译进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("翻译进度：%p%")
        left_layout.addWidget(self.progress_bar)

        # 状态过滤下拉框
        self.filter_box = QComboBox()
        self.filter_box.addItems(["全部", "未翻译", "已翻译", "需审校"])
        self.filter_box.currentIndexChanged.connect(self.on_filter_changed)
        left_layout.addWidget(self.filter_box)

        # 按钮区
        btn_layout = QHBoxLayout()
        self.btn_prev = QPushButton("上一段")
        self.btn_prev.clicked.connect(self.prev_fragment)
        btn_layout.addWidget(self.btn_prev)
        self.btn_save = QPushButton("保存译文")
        self.btn_save.clicked.connect(self.save_translation)
        btn_layout.addWidget(self.btn_save)
        self.btn_next = QPushButton("下一段")
        self.btn_next.clicked.connect(self.next_fragment)
        btn_layout.addWidget(self.btn_next)
        self.btn_copy_source = QPushButton("复制原文")
        self.btn_copy_source.clicked.connect(self.copy_source_text)
        btn_layout.addWidget(self.btn_copy_source)
        self.btn_lookup = QPushButton("机器翻译")
        self.btn_lookup.clicked.connect(self.lookup_word)
        btn_layout.addWidget(self.btn_lookup)

        left_layout.addLayout(btn_layout)

        # 把左边控件添加到主布局
        main_layout.addWidget(self.left_widget, stretch=3)  # stretch参数控制宽度比例

        # 右边：模糊匹配显示区
        self.fuzzy_match_widget = test_demo_show_fuzzy_match()
        main_layout.addWidget(self.fuzzy_match_widget, stretch=2)

    def on_filter_changed(self):
        """
        状态过滤切换，刷新段落列表
        """
        self.current_index = 0  # 重新回到第1段
        self.load_fragments(self.document_id)

    def load_fragments(self, document_id):
        """
        读取指定文档的所有段落，支持按状态筛选
        """
        all_frags = translation_fragment_dao.get_fragments(document_id)
        filter_status = self.filter_box.currentText()
        if filter_status == "全部":
            self.fragments = all_frags
        else:
            self.fragments = [frag for frag in all_frags if frag[4] == filter_status]

        if not self.fragments:
            QMessageBox.warning(self, "无内容", "该文档暂无分段或筛选结果为空。")
            self.current_index = 0
            self.show_fragment()
            return

        self.current_index = 0
        self.show_fragment()
        self.refresh_progress()


    def show_fragment(self):
        """
        显示当前段落（原文+译文+状态+进度）
        """
        total = len(self.fragments)
        idx = self.current_index
        self.progress_label.setText(f"段落进度：{idx+1}/{total}")
        if total == 0:
            self.source_label.setText("原文内容：无")
            self.text_edit.setText("")
            self.status_label.setText("当前状态：无")
            return
        frag = self.fragments[idx]
        frag_id, seq, source_text, translated_text, status = frag
        self.source_label.setText(f"原文内容（第{seq}段）：{source_text}")
        self.text_edit.setText(translated_text if translated_text else "")
        self.status_label.setText(f"当前状态：{status if status else '未翻译'}")
        # 按钮可用性
        self.btn_prev.setEnabled(idx > 0)
        self.btn_next.setEnabled(idx < total - 1)
        self.refresh_progress()

    def refresh_progress(self):
        """
        统计已翻译/总段数，刷新进度条
        """
        all_count = len(self.fragments)
        if all_count == 0:
            self.progress_bar.setValue(0)
            return
        done_count = sum(1 for f in self.fragments if f[4] == "已翻译")
        percent = int(done_count / all_count * 100)
        self.progress_bar.setValue(percent)

    def save_translation(self):
        """
        保存当前译文及状态到数据库
        """
        if not self.fragments:
            return
        frag = self.fragments[self.current_index]
        frag_id = frag[0]
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "保存失败", "请输入译文后再保存！")
            return
        status = "已翻译" if text else "未翻译"
        translation_fragment_dao.update_fragment(frag_id, text, status)
        # 更新本地缓存
        lst = list(self.fragments[self.current_index])
        lst[3] = text
        lst[4] = status
        self.fragments[self.current_index] = tuple(lst)
        QMessageBox.information(self, "保存成功", "译文已保存。")
        self.show_fragment()

    def prev_fragment(self):
        """
        切换到上一段
        """
        if self.current_index > 0:
            self.current_index -= 1
            self.show_fragment()

    def next_fragment(self):
        """
        切换到下一段
        """
        if self.current_index < len(self.fragments) - 1:
            self.current_index += 1
            self.show_fragment()

    def copy_source_text(self):
        """
        将当前段落原文复制到剪贴板，并弹窗提示
        """
        text = self.source_label.text()
        # 去除前缀（如“原文内容（第x段）：”）只保留原文
        if "：" in text:
            text = text.split("：", 1)[1]
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "提示", "原文已复制到剪贴板！")

    def lookup_word(self):
        """
        机器翻译按钮，点击后跳转到机器翻译界面
        """
        try:
            self.translation_app = api_ui.api_ui_. TranslatorApp()
            self.translation_app.show()
        except Exception as e:
            print(e)

