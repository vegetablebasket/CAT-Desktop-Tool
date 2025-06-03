import sqlite3
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "../data/database.db")
'''
table_type 的对应
tm 翻译记忆库表
terminology 术语库表
'''
# 表类型映射字典
TABLE_TYPE_MAP = {
    "tm": "翻译记忆库表",
    "terminology": "术语库表"
}

def validate_table_type(table_type):
    if table_type is None or table_type == "":
        return True
    if table_type not in TABLE_TYPE_MAP:
        print(f"警告：table_type '{table_type}' 不在允许范围内")
        return False
    return True

def get_table_type_description(table_type_key):
    """
    根据英文标识获取中文描述
    """
    return TABLE_TYPE_MAP.get(table_type_key, "未知类型")

def create_table_description():
    """
    创建 table_description 表，存储记忆库描述信息，包含表类型字段
    """
    sql = '''
    CREATE TABLE IF NOT EXISTS table_description(
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增ID
        tm_name VARCHAR(255)  UNIQUE,       -- 表名
        item_number INTEGER,                 -- 相应表中的条目数量
        description TEXT,                   -- 描述文本
        owner INTEGER,                     -- 创建者
        create_time DATETIME,              -- 创建时间
        table_type VARCHAR(50)             -- 表类型，例如“术语库表”、“翻译记忆库表”
    )
    '''
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(sql)
        conn.commit()

def insert_table_description(tm_name, item_number, description, owner, create_time=None, table_type=None):
    """
    插入一条记忆库描述记录
    """
    if not validate_table_type(table_type):
        print("table_type = '", table_type, "' 不存在")
        return

    if create_time is None:
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = '''
    INSERT INTO table_description (tm_name, item_number, description, owner, create_time, table_type)
    VALUES (?, ?, ?, ?, ?, ?)
    '''
    with sqlite3.connect(DB_FILE) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (tm_name, item_number, description, owner, create_time, table_type))
            conn.commit()
            print(f"插入成功，tm_name: {tm_name}")
        except sqlite3.IntegrityError:
            print(f"插入失败，tm_name {tm_name} 已存在")
        except Exception as e:
            print(f"插入失败，错误: {e}")

def get_record_count(tm_name):
    """
    查询指定翻译记忆库表的记录总数
    返回整数，失败返回None
    """
    try:
        sql = f"SELECT COUNT(*) FROM {tm_name}"
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.execute(sql)
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        print(f"查询{tm_name}记录数失败: {e}")
        return None

def update_table_description(tm_name, item_number=None, description=None, owner=None, table_type=None):
    """
    更新指定记忆库描述信息，支持部分字段更新
    """
    if not validate_table_type(table_type):
        print("table_type = '", table_type, "' 不存在")
        return

    fields = []
    values = []
    if item_number is not None:
        fields.append("item_number = ?")
        values.append(item_number)
    if description is not None:
        fields.append("description = ?")
        values.append(description)
    if owner is not None:
        fields.append("owner = ?")
        values.append(owner)
    if table_type is not None:
        fields.append("table_type = ?")
        values.append(table_type)

    if not fields:
        print("没有需要更新的字段")
        return

    values.append(tm_name)
    sql = f"UPDATE table_description SET {', '.join(fields)} WHERE tm_name = ?"

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        print(f"更新成功，影响行数: {cursor.rowcount}")

def delete_table_description(tm_name,table_type=None):
    """
    删除指定记忆库描述记录
    如果传入 table_type，则同时根据 tm_name 和 table_type删除。
    """

    if not validate_table_type(table_type):
        print(f"table_type = '{table_type}' 不存在")
        return

    sql = "DELETE FROM table_description WHERE tm_name = ?"
    params = [tm_name]
    if table_type is not None:
        sql += " AND table_type = ?"
        params.append(table_type)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        print(f"删除成功，影响行数: {cursor.rowcount}")

def get_table_description(tm_name, table_type=None):
    """
    查询指定记忆库描述信息，返回字典或None。
    如果传入 table_type，则同时根据 tm_name 和 table_type 查询。
    """
    sql = "SELECT * FROM table_description WHERE tm_name = ?"
    params = [tm_name]

    if not validate_table_type(table_type):
        print(f"table_type = '{table_type}' 不存在")
        return []

    if table_type is not None:
        sql += " AND table_type = ?"
        params.append(table_type)

    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def list_table_descriptions_by_type(table_type=None):
    """
    根据 table_type 查询记忆库描述信息，返回列表。
    如果 table_type 为 None 或空字符串，则查询所有记录。
    """
    if not validate_table_type(table_type):
        print(f"table_type = '{table_type}' 不存在")
        return []

    sql = "SELECT * FROM table_description"
    params = ()

    if table_type:  # 有指定类型，添加 WHERE 条件
        sql += " WHERE table_type = ?"
        params = (table_type,)

    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def update_item_by_id(item_id, new_name = None, new_description = None):
    try:
        fields = []
        values = []

        if new_description is not None:
            fields.append("description = ?")
            values.append(new_description)
        if new_name is not None:
            fields.append("tm_name = ?")
            values.append(new_name)
        values.append(item_id)
        sql = f"UPDATE table_description SET {', '.join(fields)} WHERE id = ?"

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()
            return cursor.rowcount  # 返回受影响的行数，1表示成功更新
    except Exception as e:
        print(f"update_item_by_id 出错: {e}")
        return None

def get_item_id(tm_name , table_type):
    """
       根据 tm_name 和 table_type 查询 table_description 表中的 id。

       参数:
           tm_name (str): 记忆库表名
           table_type (str): 表类型标识，例如 "tm" 或 "terminology"

       返回:
           int 或 None: 对应记录的 id，未找到返回 None
       """
    if not validate_table_type(table_type):
        print(f"table_type = '{table_type}' 不存在")
        return None
    sql = "SELECT id FROM table_description WHERE tm_name = ? AND table_type = ?"
    params = [tm_name, table_type]
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row:
                return row[0]
            return None
    except Exception as e:
        print(f"查询 id 失败: {e}")
        return None

if __name__ == "__main__":
    create_table_description()
    print(list_table_descriptions_by_type())
