# src/dao/project_dao.py
# 该模块用于操作“项目表”（projects）的所有数据库操作

import sqlite3
import os
from datetime import datetime

# 构建数据库路径（与init_db.py一致）
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/cat.db")

# 新建项目
def add_project(name, source_lang, target_lang):
    """
    添加一个新项目到数据库
    :param name: 项目名称（字符串）
    :param source_lang: 源语言（字符串）
    :param target_lang: 目标语言（字符串）
    :return: 无
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT INTO projects (name, source_lang, target_lang, created_at) VALUES (?, ?, ?, ?)',
                (name, source_lang, target_lang, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# 获取所有项目
def get_all_projects():
    """
    查询数据库中所有项目，按id降序排列
    :return: 项目列表（每项为元组）
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, name, source_lang, target_lang, created_at FROM projects ORDER BY id DESC')
    data = cur.fetchall()
    conn.close()
    return data

# 删除项目
def delete_project(pid):
    """
    根据项目id删除项目
    :param pid: 项目id（整数）
    :return: 无
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('DELETE FROM projects WHERE id=?', (pid,))
    conn.commit()
    conn.close()
