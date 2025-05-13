import os
import json
from pathlib import Path

def detect_file_type(file_path):
    ext = Path(file_path).suffix.lower()
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
def parse_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return [{'type': 'paragraph', 'content': content}]
from docx import Document

def parse_word(file_path):
    doc = Document(file_path)
    sections = []
    for para in doc.paragraphs:
        if para.text.strip():
            sections.append({
                'type': 'paragraph',
                'content': para.text,
                'style': para.style.name
            })
    return sections
from PyPDF2 import PdfReader

def parse_pdf(file_path):
    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        text.append(page.extract_text())
    return [{
        'type': 'page',
        'content': '\n'.join(text),
        'total_pages': len(reader.pages)
    }]
import pandas as pd

def parse_excel(file_path):
    df = pd.read_excel(file_path)
    # 转换为字典列表（按行）
    return df.to_dict('records')
from bs4 import BeautifulSoup

def parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    # 提取所有段落
    paragraphs = [p.get_text() for p in soup.find_all('p')]
    return [{'type': 'paragraph', 'content': p} for p in paragraphs]

    def parse_source_file(self):
        file_path = self.file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError("源文件不存在")

        file_type = detect_file_type(file_path)

        try:
            if file_type == 'text':
                self.parsed_content = parse_text(file_path)
            elif file_type == 'word':
                self.parsed_content = parse_word(file_path)
            elif file_type == 'pdf':
                self.parsed_content = parse_pdf(file_path)
            elif file_type == 'excel':
                self.parsed_content = parse_excel(file_path)
            elif file_type == 'html':
                self.parsed_content = parse_html(file_path)

            # 保存解析结果到项目目录
            parsed_file = os.path.join(self.project_dir, 'parsed_content.json')
            with open(parsed_file, 'w', encoding='utf-8') as f:
                json.dump(self.parsed_content, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"解析失败: {str(e)}")
            self.parsed_content = None