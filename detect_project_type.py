import os
import json
from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup
import pandas as pd

class Fileparser:
    def __init__(self, file_path, project_dir):
        self.file_path = file_path  # 源文件路径
        self.project_dir = project_dir  # 项目目录
        self.parsed_content = None  # 解析结果


    def detect_file_type(self):
        ext = Path(self.file_path).suffix.lower()
        if ext == '.txt':
            return 'text'
        elif ext == '.docx':
            return 'word'
        elif ext == '.pdf':
            return 'pdf'
        elif ext in ('.xlsx', '.xls'):
            return 'excel'
        elif ext in ('.html', '.htm'):
            return 'html'
        else:
            raise ValueError(f"不支持的格式: {ext}")
    def parse_text(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return [{'type': 'paragraph', 'content': content}]


    def parse_word(self):
        doc = Document(self.file_path)
        sections = []
        for para in doc.paragraphs:
            if para.text.strip():
                sections.append({
                    'type': 'paragraph',
                    'content': para.text,
                    'style': para.style.name
                })
        return sections


    def parse_pdf(self):
        reader = PdfReader(self.file_path)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return [{
            'type': 'page',
            'content': '\n'.join(text),
            'total_pages': len(reader.pages)
        }]


    def parse_excel(self):
        df = pd.read_excel(self.file_path)
        # 转换为字典列表（按行）
        return df.to_dict('records')


    def parse_html(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    # 提取所有段落
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        return [{'type': 'paragraph', 'content': p} for p in paragraphs]

    def parse_source_file(self):
        file_path = self.file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError("源文件不存在")

        file_type = self.detect_file_type()

        try:
            if file_type == 'text':
                self.parsed_content = self.parse_text()
            elif file_type == 'word':
                self.parsed_content = self.parse_word()
            elif file_type == 'pdf':
                self.parsed_content = self.parse_pdf()
            elif file_type == 'excel':
                self.parsed_content = self.parse_excel()
            elif file_type == 'html':
                self.parsed_content = self.parse_html()

            # 保存解析结果到项目目录
            parsed_file = os.path.join(self.project_dir, 'parsed_content.json')
            with open(parsed_file, 'w', encoding='utf-8') as f:
                json.dump(self.parsed_content, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"解析失败: {str(e)}")
            self.parsed_content = None