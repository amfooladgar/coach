# tools/storage.py
import sqlite3
import datetime
from data.schemas import Task, CalendarEvent

def init_db(db_path="data/store.sqlite"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS tasks
        (id TEXT, title TEXT, why TEXT, priority TEXT,
         pillar TEXT, due TEXT, status TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS calendar_events
        (event_id TEXT PRIMARY KEY, 
         task_id TEXT,
         title TEXT,
         start_time TEXT,
         end_time TEXT,
         duration_min INTEGER,
         block_type TEXT,
         created_at TEXT,
         date TEXT)""")
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

def save_calendar_events(events: list[CalendarEvent], db_path="data/store.sqlite"):
    """Save scheduled calendar events to the database."""
    if not events:
        return
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    for event in events:
        # Extract date for easier querying
        event_date = event.start_time.date().isoformat()
        cur.execute(
            """INSERT INTO calendar_events 
               (event_id, task_id, title, start_time, end_time, 
                duration_min, block_type, created_at, date)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                event.event_id,
                event.task_id,
                event.title,
                event.start_time.isoformat(),
                event.end_time.isoformat(),
                event.duration_min,
                event.block_type,
                event.created_at.isoformat(),
                event_date
            )
        )
    conn.commit()
    conn.close()

def get_todays_schedule(db_path="data/store.sqlite") -> list[CalendarEvent]:
    """Retrieve today's scheduled events from the database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    today = datetime.date.today().isoformat()
    cur.execute(
        """SELECT event_id, task_id, title, start_time, end_time, 
                  duration_min, block_type, created_at
           FROM calendar_events
           WHERE date = ?
           ORDER BY start_time""",
        (today,)
    )
    
    rows = cur.fetchall()
    conn.close()
    
    events = []
    for row in rows:
        events.append(CalendarEvent(
            event_id=row[0],
            task_id=row[1],
            title=row[2],
            start_time=datetime.datetime.fromisoformat(row[3]),
            end_time=datetime.datetime.fromisoformat(row[4]),
            duration_min=row[5],
            block_type=row[6],
            created_at=datetime.datetime.fromisoformat(row[7])
        ))
    
    return events
