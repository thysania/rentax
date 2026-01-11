import sqlite3
from pathlib import Path

DB_PATH = Path("database.db")
SCHEMA_PATH = Path("sql/schema.sql")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH.resolve()}")

    conn = get_connection()
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    except sqlite3.DatabaseError as e:
        conn.rollback()
        # Re-raise with a clearer message while preserving the original exception context
        raise sqlite3.DatabaseError(f"Failed to execute schema.sql: {e}") from e
    finally:
        conn.close()


def list_tables():
    conn = get_connection()
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    conn.close()
    return [r["name"] for r in rows]


if __name__ == "__main__":
    import sys
    import traceback

    try:
        initialize_database()
        print("Database ready.")
        print("Tables:", list_tables())
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure 'sql/schema.sql' exists and contains the schema.")
        sys.exit(1)
    except sqlite3.DatabaseError as e:
        print(f"Database error while initializing: {e}")
        print("Check 'sql/schema.sql' for syntax issues or invalid statements.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
