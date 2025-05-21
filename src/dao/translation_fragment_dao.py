# src/dao/translation_fragment_dao.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/cat.db")

def create_table():
    """
    创建翻译段落表，只需运行一次
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS translation_fragments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,         -- 所属文档ID
        seq INTEGER,                 -- 段落序号，从1开始
        source_text TEXT,            -- 原文内容
        translated_text TEXT,        -- 译文内容
        status TEXT                  -- 状态（未翻译/已翻译/需审校等）
    )
    ''')
    conn.commit()
    conn.close()

# 新增一个段落
def add_fragment(document_id, seq, source_text, status="未翻译"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO translation_fragments (document_id, seq, source_text, status)
        VALUES (?, ?, ?, ?)
    ''', (document_id, seq, source_text, status))
    conn.commit()
    conn.close()

# 获取某文档下所有段落
def get_fragments(document_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        SELECT id, seq, source_text, translated_text, status
        FROM translation_fragments
        WHERE document_id=?
        ORDER BY seq
    ''', (document_id,))
    data = cur.fetchall()
    conn.close()
    return data

# 更新段落译文和状态
def update_fragment(fragment_id, translated_text, status):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        UPDATE translation_fragments
        SET translated_text=?, status=?
        WHERE id=?
    ''', (translated_text, status, fragment_id))
    conn.commit()
    conn.close()
