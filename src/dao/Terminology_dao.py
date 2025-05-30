
import sqlite3
import os
import csv
import re

DB_FILE = os.path.join(os.path.dirname(__file__), "../data/database.db")

def get_connection():
    return sqlite3.connect(DB_FILE)


def sanitize_table_name(name):
    # 只保留字母、数字和下划线，其他替换为下划线
    return re.sub(r'\W+', '_', name)


def create_user_terminology_table(table_name):
    """
    创建 terminology 表，包含必要字段
    """
    table_name = sanitize_table_name(table_name)
    sql =f'''
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        term_id INTEGER PRIMARY KEY AUTOINCREMENT,    -- 术语条目ID
    term TEXT NOT NULL,                            -- 术语原文
    translation TEXT NOT NULL,                     -- 对应译文
    definition TEXT,                               -- 术语定义
    domain TEXT,                                   -- 术语领域
    project_id INTEGER,                            -- 所属项目（可为空，表示通用术语）
    FOREIGN KEY (project_id) REFERENCES projects(id) 
    )
    '''
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()
        print("terminology 表创建成功")
        return True
    except sqlite3.Error as e:
        print(f"创建 terminology 表失败: {e}")
        return False

def rename_table(old_name, new_name):
    '''
    更新表名
    '''
    import sqlite3
    old_name = sanitize_table_name(old_name)
    new_name = sanitize_table_name(new_name)
    sql = f'ALTER TABLE "{old_name}" RENAME TO "{new_name}"'
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()
        print(f"表重命名成功：{old_name} -> {new_name}")
        return True
    except sqlite3.Error as e:
        print(f"表重命名失败: {e}")
        return False

def delete_terminology_table(table_name):
    """
    删除 terminology 表
    """
    table_name = sanitize_table_name(table_name)
    sql = f'DROP TABLE IF EXISTS "{table_name}"'
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()
        print("terminology 表删除成功")
        return True
    except sqlite3.Error as e:
        print(f"删除 terminology 表失败: {e}")
        return False

#插入新条目
def add_terminology(term, translation,table_name ,definition=None, domain=None, project_id=None ):
    """新增术语条目"""
    table_name = sanitize_table_name(table_name)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO {table_name} (term, translation, definition, domain, project_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (term, translation, definition, domain, project_id))
    conn.commit()
    term_id = cursor.lastrowid
    conn.close()
    return term_id

def export_terminology(csv_path ,table_name):
    """
    导出术语库到CSV文件
    """
    table_name = sanitize_table_name(table_name)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT term, translation, definition, domain, project_id FROM {table_name}")
    rows = cur.fetchall()
    conn.close()

    with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # 写入表头
        writer.writerow(['term', 'translation', 'definition', 'domain', 'project_id'])
        # 写入数据行
        writer.writerows(rows)
    print(f"成功导出 {len(rows)} 条术语到 {csv_path}")

def import_terminology(csv_path ,table_name):
    """
    从CSV文件导入术语库，支持批量导入
    """
    table_name = sanitize_table_name(table_name)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"文件不存在: {csv_path}")

    conn = get_connection()
    cur = conn.cursor()

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            # 读取每一行数据，插入数据库
            cur.execute(f'''
                INSERT INTO {table_name} (term, translation, definition, domain, project_id)
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

def get_terminology_by_id(term_id ,table_name):
    """根据 term_id 查询术语条目"""
    table_name = sanitize_table_name(table_name)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT term_id, term, translation, definition, domain, project_id
        FROM {table_name}
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

def update_terminology(term_id, table_name, term=None, translation=None, definition=None, domain=None, project_id=None):
    """更新术语条目，传入None的字段不更新"""
    table_name = sanitize_table_name(table_name)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 先查询当前数据
    cursor.execute(f'SELECT term, translation, definition, domain, project_id FROM {table_name} WHERE term_id=?', (term_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False  # 不存在该条目

    new_term = term if term is not None else row[0]
    new_translation = translation if translation is not None else row[1]
    new_definition = definition if definition is not None else row[2]
    new_domain = domain if domain is not None else row[3]
    new_project_id = project_id if project_id is not None else row[4]

    cursor.execute(f'''
        UPDATE {table_name} 
        SET term = ?, translation = ?, definition = ?, domain = ?, project_id = ?
        WHERE term_id = ?
    ''', (new_term, new_translation, new_definition, new_domain, new_project_id, term_id))
    conn.commit()
    conn.close()
    return True

#删除条目
def delete_terminology(term_id ,table_name):
    """删除术语条目"""
    table_name = sanitize_table_name(table_name)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM {table_name} WHERE term_id = ?', (term_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def list_terminologies(table_name,project_id=None, domain=None):
    """查询术语列表，可根据项目ID和领域过滤"""
    table_name = sanitize_table_name(table_name)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    sql = f'SELECT term_id, term, translation, definition, domain, project_id FROM {table_name} WHERE 1=1'
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


