# migrate.py
import sqlite3

db_path = "data/store.sqlite"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Rename old table
cur.execute("ALTER TABLE journal RENAME TO journal_old;")

# 2. Create new schema with id as PK and mood/gratitude columns
cur.execute(
    """CREATE TABLE journal
       (
           id         INTEGER PRIMARY KEY AUTOINCREMENT,
           date       TEXT,
           summary    TEXT,
           insights   TEXT,
           actions    TEXT,
           mood       TEXT,
           gratitude  TEXT,
           created_at TEXT
       )"""
)

# 3. Copy over old data (fill mood & gratitude with NULL)
cur.execute(
    """INSERT INTO journal (date, summary, insights, actions, created_at)
       SELECT date, summary, insights, actions, created_at
       FROM journal_old"""
)

# 4. Drop old table
cur.execute("DROP TABLE journal_old;")

conn.commit()
conn.close()

print("✅ Migration complete. Schema updated with id PK, mood, and gratitude.")
