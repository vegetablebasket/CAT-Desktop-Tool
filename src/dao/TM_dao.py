import sqlite3
import os
import re
import threading
from datetime import datetime
_lock = threading.Lock()

DB_FILE = os.path.join(os.path.dirname(__file__), "../data/database.db")

def sanitize_identifier(name):
    """
    过滤表名或字段名中的非法字符，只保留字母、数字和下划线
    """
    if not isinstance(name, str):
        name = ''
    # 替换所有非字母数字下划线字符为下划线
    return re.sub(r'\W', '_', name)

def create_user_tm_table(db_name ):
    """
    根据用户输入的库名动态创建翻译记忆表，表名格式：translation_memory_{db_name}
    """
    table_name = sanitize_identifier(db_name)

    sql = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        tm_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_text TEXT NOT NULL,
        target_text TEXT NOT NULL,
        source_lang TEXT,
        target_lang TEXT,
        created_by INTEGER,
        created_at DATETIME DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    )
    '''


    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()

    return table_name
def delete_tm_table(table_name):
    """
        删除指定表
        SQL中表名不能以数字开头
        没有给表名加引号时，如果表名是数字开头或者包含特殊字符，SQL会报错
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}";')
        conn.commit()
        print(f"删除成功，数据库名: {table_name}")
def rename_table(old_name, new_name):
    '''
    更新表名
    '''
    import sqlite3
    old_name = sanitize_identifier(old_name)
    new_name = sanitize_identifier(new_name)
    sql = f'ALTER TABLE "{old_name}" RENAME TO "{new_name}"'
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()
        print(f"表重命名成功：{old_name} -> {new_name}")
        return True
    except sqlite3.Error as e:
        print(f"表重命名失败: {e}")
        return False

def insert_tm_entry(table_name, source_text, target_text, source_lang=None, target_lang=None, created_by=None):
    """
    向指定表插入一条翻译记忆条目，返回插入ID和创建时间
    """
    table_name = sanitize_identifier(table_name)
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    sql = f'''
        INSERT INTO {table_name} (source_text, target_text, source_lang, target_lang, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    '''

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (source_text, target_text, source_lang, target_lang, created_by, created_at))
        conn.commit()
        tm_id = cursor.lastrowid
        print(f"插入成功，条目ID: {tm_id}")
        return tm_id, created_at

def query_tm_entries(table_name, keyword=None):
    """
    查询指定表中的翻译记忆条目，支持关键字模糊搜索
    返回列表，格式为 [(tm_id, source_text, target_text, source_lang, target_lang, created_by, created_at), ...]
    """
    table_name = sanitize_identifier(table_name)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        if keyword:
            sql = f'''
                SELECT tm_id, source_text, target_text, source_lang, target_lang, created_by, created_at
                FROM {table_name}
                WHERE source_text LIKE ? OR target_text LIKE ?
            '''
            cursor.execute(sql, (f'%{keyword}%', f'%{keyword}%'))
        else:
            sql = f'''
                SELECT tm_id, source_text, target_text, source_lang, target_lang, created_by, created_at
                FROM {table_name}
            '''
            cursor.execute(sql)
        rows = cursor.fetchall()
    return rows

def update_tm_entry(table_name, tm_id, source_text=None, target_text=None, source_lang=None, target_lang=None):
    """
    更新指定表中某条翻译记忆条目，支持部分字段更新
    """
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
        return

    values.append(tm_id)
    sql = f"UPDATE {table_name} SET {', '.join(fields)} WHERE tm_id = ?"

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        print(f"更新成功，影响行数: {cursor.rowcount}")

def delete_tm_entry(table_name, tm_id):
    """
    删除指定表中某条翻译记忆条目
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        sql = f"DELETE FROM {table_name} WHERE tm_id = ?"
        cursor.execute(sql, (tm_id,))
        conn.commit()
        print(f"删除成功，影响行数: {cursor.rowcount}")


def batch_insert(table_name, rows):
    """
    批量插入数据
    rows: 可迭代对象，每个元素是包含5个字段的元组或列表
    (source_text, target_text, source_lang, target_lang, created_by)
    """
    table_name = sanitize_identifier(table_name)
    sql = f'''
        INSERT INTO "{table_name}" 
        (source_text, target_text, source_lang, target_lang, created_by)
        VALUES (?, ?, ?, ?, ?)
    '''
    try:
        with _lock:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, rows)
                conn.commit()
        print(f"成功插入 {len(rows)} 条记录")
        return True
    except sqlite3.Error as e:
        print(f"批量插入出错: {e}")
        return False

def batch_export(table_name):
    """
    导出指定翻译记忆表的全部数据到CSV文件
    :param table_name: 表名
    :return: rows是一个列表
    """
    table_name = sanitize_identifier(table_name)

    # 查询全部数据
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            sql = f'''
                SELECT tm_id, source_text, target_text, source_lang, target_lang, created_by, created_at
                FROM "{table_name}"
            '''
            cursor.execute(sql)
            rows = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"查询数据库时出错: {e}")
        return None

    if not rows:
        print("表中没有数据可导出")
        return None

    return rows

if __name__ == "__main__":
    delete_tm_table("translation_memory")
    print("删除成功")