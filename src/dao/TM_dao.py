import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "../data/database.db")

#插入新条目
def insert_tm_entry(source_text, target_text, source_lang=None, target_lang=None,  created_by=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO translation_memory (source_text, target_text,source_lang, target_lang, created_by)
        VALUES (?, ?, ?, ?,?)
    ''', (source_text, target_text, source_lang, target_lang , created_by))
    conn.commit()
    print(f"插入成功，条目ID: {cursor.lastrowid}")
    conn.close()

#查询条目
#返回：[(tm_id, source_text , target_text , source_lang, target_lang , created_by , created_at ) , ...]
def query_tm_entries(keyword=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if keyword:
        cursor.execute('''
            SELECT tm_id, source_text, target_text, source_lang, target_lang, created_by, created_at
            FROM translation_memory
            WHERE source_text LIKE ? OR target_text LIKE ?
        ''', (f'%{keyword}%', f'%{keyword}%'))
    else:
        cursor.execute('''
            SELECT tm_id, source_text, target_text, source_lang, target_lang created_by, created_at
            FROM translation_memory
        ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

#更新条目
def update_tm_entry(tm_id, source_text=None, target_text=None,  source_lang=None,target_lang=None,):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 动态构造更新语句
    fields = []
    values = []
    if source_text is not None:
        fields.append("source_text = ?")
        values.append(source_text)
    if target_text is not None:
        fields.append("target_text = ?")
        values.append(target_text)
    if source_lang is not None:
        fields.append("source_lang = ?")
        values.append(source_lang)
    if target_lang is not None:
        fields.append("target_lang = ?")
        values.append(target_lang)

    if not fields:
        print("没有需要更新的字段")
        conn.close()
        return

    values.append(tm_id)
    sql = f"UPDATE translation_memory SET {', '.join(fields)} WHERE tm_id = ?"
    cursor.execute(sql, values)
    conn.commit()
    print(f"更新成功，影响行数: {cursor.rowcount}")
    conn.close()

#删除条目
def delete_tm_entry(tm_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM translation_memory WHERE tm_id = ?', (tm_id,))
    conn.commit()
    print(f"删除成功，影响行数: {cursor.rowcount}")
    conn.close()

