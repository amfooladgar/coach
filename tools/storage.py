# tools/storage.py
import sqlite3
from data.schemas import Task

def init_db(db_path="data/store.sqlite"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS tasks
        (id TEXT, title TEXT, why TEXT, priority TEXT,
         pillar TEXT, due TEXT, status TEXT)""")
    conn.commit()
    conn.close()

def save_tasks(tasks: list[Task], db_path="data/store.sqlite"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for t in tasks:
        cur.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?,?)",
                    (t.task_id, t.title, t.why, t.priority,
                     t.pillar, t.due.isoformat(), t.status))
    conn.commit()
    conn.close()
