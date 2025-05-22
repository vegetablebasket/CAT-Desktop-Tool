# src/dao/init_TM_db.py
# 用于创建（初始化）数据库和表结构，只需要运行一次

import sqlite3
import os


# 数据库文件名，可以根据自己需要修改
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/database.db")

# 建立连接，若文件不存在会自动创建
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 创建 translation_memory 表
cur.execute('''
    CREATE TABLE IF NOT EXISTS translation_memory (
    tm_id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 翻译记忆条目ID
    source_text TEXT NOT NULL,                  -- 源文本
    target_text TEXT NOT NULL,                  -- 对应翻译
    source_lang TEXT,                           --语文本语言
    target_lang TEXT,                           --对应翻译语言
    created_by INTEGER,                         -- 创建者（用户ID）
    created_at DATETIME DEFAULT (datetime('now', 'localtime')),  -- 创建时间，默认当前时间
    FOREIGN KEY (created_by) REFERENCES users(user_id)            -- 外键关联用户表（假设表名为 users，主键为 user_id）
    )
    ''')

# 创建 terminology 表
cur.execute('''
    CREATE TABLE IF NOT EXISTS terminology (
    term_id INTEGER PRIMARY KEY AUTOINCREMENT,    -- 术语条目ID
    term TEXT NOT NULL,                            -- 术语原文
    translation TEXT NOT NULL,                     -- 对应译文
    definition TEXT,                               -- 术语定义
    domain TEXT,                                   -- 术语领域
    project_id INTEGER,                            -- 所属项目（可为空，表示通用术语）
    FOREIGN KEY (project_id) REFERENCES projects(id) 
    )
    ''')

# 创建 operation_logs 表
cur.execute('''
   CREATE TABLE IF NOT EXISTS operation_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 日志ID
    user_id INTEGER,                            -- 操作用户（外键）
    action TEXT NOT NULL,                       -- 操作行为（添加术语、导入文件等）
    object_type TEXT NOT NULL,                  -- 操作对象类型（项目/文档/术语/记忆等）
    object_id INTEGER,                          -- 操作对象ID
    timestamp DATETIME DEFAULT (datetime('now', 'localtime')),  -- 操作时间，默认当前时间
    FOREIGN KEY (user_id) REFERENCES users(user_id)
   )
   ''')
conn.commit()
conn.close()

print("数据库表结构创建完成！你只需要运行本脚本一次。")
