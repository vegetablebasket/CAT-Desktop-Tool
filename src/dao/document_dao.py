# src/dao/document_dao.py
# 用于操作“文档表”（documents）的数据库操作

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/cat.db")

def add_document(project_id, name, file_format, status="未翻译"):
    """
    向数据库插入一个新文档
    :param project_id: 项目ID（int）
    :param name: 文档名（str）
    :param file_format: 文件格式（str），如txt、docx
    :param status: 文档状态（str），默认“未翻译”
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO documents (project_id, name, file_format, status, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (project_id, name, file_format, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_documents_by_project(project_id):
    """
    查询某项目下的所有文档
    :param project_id: 项目ID（int）
    :return: [(id, name, file_format, status, created_at), ...]
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        SELECT id, name, file_format, status, created_at
        FROM documents
        WHERE project_id = ?
        ORDER BY id DESC
    ''', (project_id,))
    data = cur.fetchall()
    conn.close()
    return data

def delete_document(doc_id):
    """
    删除指定文档
    :param doc_id: 文档ID（int）
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('DELETE FROM documents WHERE id=?', (doc_id,))
    conn.commit()
    conn.close()
