# dao/project_dao.py

import sqlite3
import os
from datetime import datetime

# 绝对路径，确保可用
DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
DB_PATH = os.path.join(DB_DIR, 'database.db')

# 自动创建 data 文件夹
os.makedirs(DB_DIR, exist_ok=True)

def init_db():
    print("📁 正在连接数据库:", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_all_projects():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, created_at FROM projects")
    results = cursor.fetchall()
    conn.close()
    return results

def add_project(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (name, created_at) VALUES (?, ?)",
                   (name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def delete_project(project_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()