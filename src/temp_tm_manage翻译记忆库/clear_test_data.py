import sqlite3
import test_TM_data
db_path = test_TM_data.DB_PATH

def clear_database(db_path):
    """
    清空指定 SQLite 数据库文件中的所有表数据，但保留表结构。

    参数:
        db_path (str): 数据库文件路径
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查询所有用户表名（排除系统表）
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()

    target_tables = ['translation_memory']

    for (table_name,) in tables:
        if table_name in target_tables:
            cursor.execute(f"DELETE FROM {table_name};")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")

    conn.commit()
    conn.close()
    print(f"数据库 {db_path} 中所有表的数据已清空。")

if __name__ == "__main__":
    try:
        clear_database(db_path)
    except Exception as e:
        print(e)