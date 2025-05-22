
import sqlite3
import os
import csv

DB_FILE = os.path.join(os.path.dirname(__file__), "../data/database.db")

def get_connection():
    return sqlite3.connect(DB_FILE)
#插入新条目
def add_terminology(term, translation, definition=None, domain=None, project_id=None):
    """新增术语条目"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO terminology (term, translation, definition, domain, project_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (term, translation, definition, domain, project_id))
    conn.commit()
    term_id = cursor.lastrowid
    conn.close()
    return term_id

def export_terminology(csv_path):
    """
    导出术语库到CSV文件
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT term, translation, definition, domain, project_id FROM terminology")
    rows = cur.fetchall()
    conn.close()

    with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(['term', 'translation', 'definition', 'domain', 'project_id'])
        # 写入数据行
        writer.writerows(rows)
    print(f"成功导出 {len(rows)} 条术语到 {csv_path}")

def import_terminology(csv_path):
    """
    从CSV文件导入术语库，支持批量导入
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"文件不存在: {csv_path}")

    conn = get_connection()
    cur = conn.cursor()

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            # 读取每一行数据，插入数据库
            cur.execute('''
                INSERT INTO terminology (term, translation, definition, domain, project_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['term'],
                row['translation'],
                row.get('definition', None),
                row.get('domain', None),
                int(row['project_id']) if row.get('project_id') else None
            ))
            count += 1

    conn.commit()
    conn.close()
    print(f"成功导入 {count} 条术语从 {csv_path}")

def get_terminology_by_id(term_id):
    """根据 term_id 查询术语条目"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT term_id, term, translation, definition, domain, project_id
        FROM terminology
        WHERE term_id = ?
    ''', (term_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "term_id": row[0],
            "term": row[1],
            "translation": row[2],
            "definition": row[3],
            "domain": row[4],
            "project_id": row[5]
        }
    else:
        return None

def update_terminology(term_id, term=None, translation=None, definition=None, domain=None, project_id=None):
    """更新术语条目，传入None的字段不更新"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 先查询当前数据
    cursor.execute('SELECT term, translation, definition, domain, project_id FROM terminology WHERE term_id=?', (term_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False  # 不存在该条目

    new_term = term if term is not None else row[0]
    new_translation = translation if translation is not None else row[1]
    new_definition = definition if definition is not None else row[2]
    new_domain = domain if domain is not None else row[3]
    new_project_id = project_id if project_id is not None else row[4]

    cursor.execute('''
        UPDATE terminology
        SET term = ?, translation = ?, definition = ?, domain = ?, project_id = ?
        WHERE term_id = ?
    ''', (new_term, new_translation, new_definition, new_domain, new_project_id, term_id))
    conn.commit()
    conn.close()
    return True

#删除条目
def delete_terminology(term_id):
    """删除术语条目"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM terminology WHERE term_id = ?', (term_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def list_terminologies(project_id=None, domain=None):
    """查询术语列表，可根据项目ID和领域过滤"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    sql = 'SELECT term_id, term, translation, definition, domain, project_id FROM terminology WHERE 1=1'
    params = []
    if project_id is not None:
        sql += ' AND project_id = ?'
        params.append(project_id)
    if domain is not None:
        sql += ' AND domain = ?'
        params.append(domain)
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            "term_id": row[0],
            "term": row[1],
            "translation": row[2],
            "definition": row[3],
            "domain": row[4],
            "project_id": row[5]
        })
    return result