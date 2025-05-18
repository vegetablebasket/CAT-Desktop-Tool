# src/dao/document_dao.py

import sqlite3
import os
from datetime import datetime

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
DB_PATH = os.path.join(DB_DIR, "database.db")

os.makedirs(DB_DIR, exist_ok=True)

# 初始化文档表
def init_doc_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT,
            created_at TEXT NOT NULL,
            project_id INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 初始化翻译片段表
def init_translation_fragments_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS translation_fragments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fragment TEXT NOT NULL,            -- 存储文档原始段落
            translated_fragment TEXT,         -- 存储翻译后的段落
            document_id INTEGER NOT NULL,     -- 文档 ID 关联到 documents 表
            FOREIGN KEY(document_id) REFERENCES documents(id)
        )
    ''')
    conn.commit()
    conn.close()


# 添加文档
def add_document(name, content, project_id):
    """将文件内容作为字符串插入数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO documents (name, content, created_at, project_id)
                      VALUES (?, ?, ?, ?)''',
                   (name, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), project_id))
    conn.commit()
    conn.close()
# 获取文档
def get_documents_by_project(project_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, created_at FROM documents WHERE project_id = ?", (project_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def reset_autoincrement():
    """重置 AUTOINCREMENT 值"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='documents'")  # 重置 documents 表的自增 ID
    conn.commit()
    conn.close()

# 删除文档
def delete_document(doc_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    reset_autoincrement() # 删除后重置AUTOINCREMENT

# 添加翻译片段
def add_translation_fragment(document_id, fragment):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO translation_fragments (fragment, document_id)
        VALUES (?, ?)
    ''', (fragment, document_id))
    conn.commit()
    conn.close()

# 获取文档的翻译片段
def get_translation_fragments_by_document(document_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, fragment FROM translation_fragments WHERE document_id = ?", (document_id,))
    result = cursor.fetchall()
    conn.close()
    return result

# 保存翻译内容
def save_translation(fragment_id, translated_text):
    """保存翻译结果"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE translation_fragments 
        SET translated_fragment = ? 
        WHERE id = ?
    ''', (translated_text, fragment_id))
    conn.commit()
    conn.close()