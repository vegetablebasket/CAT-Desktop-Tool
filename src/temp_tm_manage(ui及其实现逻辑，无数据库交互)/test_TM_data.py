import sqlite3
import os
import TM_dao

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/database.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH)

def create_tables(conn):

    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # 创建 users 表
    cur.execute('''
       CREATE TABLE IF NOT EXISTS users (
           user_id INTEGER PRIMARY KEY AUTOINCREMENT,
           username TEXT NOT NULL UNIQUE,
           email TEXT,
           created_at DATETIME DEFAULT (datetime('now', 'localtime'))
       )
    ''')

    # 创建 translation_memory 表，created_by 外键关联 users.user_id
    cur.execute('''
       CREATE TABLE IF NOT EXISTS translation_memory (
           tm_id INTEGER PRIMARY KEY AUTOINCREMENT,
           source_text TEXT NOT NULL,
           target_text TEXT NOT NULL,
           source_lang TEXT NOT NULL,
           target_lang TEXT NOT NULL,
           created_by INTEGER NOT NULL,
           created_at DATETIME DEFAULT (datetime('now', 'localtime')),
           FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE
       )
    ''')

    conn.commit()

def insert_default_user(conn):
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM users WHERE user_id = 1')
    if cur.fetchone() is None:
        cur.execute('INSERT INTO users (username, email) VALUES (?, ?)', ("admin", "admin@example.com"))
        conn.commit()
        print("默认用户 admin 已插入。")
    else:
        print("默认用户 admin 已存在。")


if __name__ == "__main__":
    try:
        conn = sqlite3.connect(DB_PATH)
        create_tables(conn)
        insert_default_user(conn)

        # 插入测试数据
        TM_dao.insert_tm_entry("Hello", "你好", "en", "zh", 1)
        TM_dao.insert_tm_entry("Goodbye", "再见", "en", "zh", 1)


    except Exception as e:
        print("数据库操作异常：", e)
