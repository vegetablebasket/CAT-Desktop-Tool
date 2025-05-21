# src/dao/init_db.py
# 用于创建（初始化）数据库和表结构，只需要运行一次

import sqlite3
import os

# 数据库文件名，可以根据自己需要修改
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/cat.db")

# 建立连接，若文件不存在会自动创建
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 创建项目表（projects），存储项目基本信息
cur.execute('''
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 项目唯一编号
    name TEXT NOT NULL,                    -- 项目名称
    source_lang TEXT,                      -- 源语言
    target_lang TEXT,                      -- 目标语言
    created_at TEXT                        -- 创建时间
)
''')

# 创建文档表（documents），存储每个文档
cur.execute('''
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 文档唯一编号
    project_id INTEGER,                    -- 所属项目编号
    name TEXT NOT NULL,                    -- 文档名称
    file_format TEXT,                      -- 文档格式（txt/docx等）
    status TEXT,                           -- 文档当前状态
    created_at TEXT,                       -- 上传时间
    FOREIGN KEY (project_id) REFERENCES projects(id)  -- 外键关联项目
)
''')

conn.commit()
conn.close()

print("数据库表结构创建完成！你只需要运行本脚本一次。")
