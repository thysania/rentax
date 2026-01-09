import sqlite3
from pathlib import Path

DB_PATH = Path("rent.db")
SCHEMA_PATH = Path("schema.sql")


def get_connection():
    first_run = not DB_PATH.exists()

    conn = sqlite3.connect(DB_PATH)

    if first_run:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()

    return conn