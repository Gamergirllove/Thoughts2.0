import sqlite3
from contextlib import contextmanager

DB_PATH = "podcast.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS shows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            author TEXT,
            image_url TEXT,
            intro_path TEXT,
            outro_path TEXT,
            sponsor_path TEXT,
            base_url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            show_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            raw_path TEXT,
            final_path TEXT,
            duration_seconds REAL,
            file_size INTEGER,
            published INTEGER DEFAULT 0,
            pub_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (show_id) REFERENCES shows(id)
        )
        """)
