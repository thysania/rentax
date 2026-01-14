import sqlite3
from pathlib import Path
import pytest

from database import initialize_database, DB_PATH, SCHEMA_PATH


def _setup_db(tmp_path, monkeypatch):
    # Copy project's schema.sql into the temp schema file
    project_root = Path(__file__).resolve().parents[1]
    orig_schema = project_root / "sql" / "schema.sql"
    schema_file = tmp_path / "schema.sql"
    schema_file.write_text(orig_schema.read_text())

    monkeypatch.setattr(__import__("database"), 'SCHEMA_PATH', schema_file)
    db_path = Path(tmp_path / "database.db")
    monkeypatch.setattr(__import__("database"), 'DB_PATH', db_path)

    initialize_database()
    return db_path


def test_ownership_invalid_odd_even(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path, monkeypatch)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Create required owner and unit
    cur.execute("INSERT INTO owners (name) VALUES ('Alice')")
    cur.execute("INSERT INTO units (reference) VALUES ('U1')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]

    with pytest.raises(sqlite3.IntegrityError):
        cur.execute(
            "INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate, odd_even) VALUES (?, ?, ?, ?, ?)",
            (unit_id, owner_id, 50, 1, 'weird'),
        )
    conn.close()


def test_ownership_share_percent_bounds(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path, monkeypatch)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name) VALUES ('Bob')")
    cur.execute("INSERT INTO units (reference) VALUES ('U2')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]

    # share_percent must be > 0
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute(
            "INSERT INTO ownerships (unit_id, owner_id, share_percent) VALUES (?, ?, ?)",
            (unit_id, owner_id, 0),
        )

    # share_percent must be <= 100
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute(
            "INSERT INTO ownerships (unit_id, owner_id, share_percent) VALUES (?, ?, ?)",
            (unit_id, owner_id, 150),
        )

    conn.close()


def test_receipt_log_foreign_keys(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path, monkeypatch)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Create minimal related records: assignment, receipt
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C1','PP')")
    cur.execute("INSERT INTO owners (name) VALUES ('O1')")
    cur.execute("INSERT INTO units (reference) VALUES ('UR')")
    conn.commit()

    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]
    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]

    # Create assignment and receipt
    cur.execute(
        """
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (unit_id, owner_id, client_id, 100, 'none', None, None, '01/01/2026', None, 500, 0),
    )
    conn.commit()

    assignment_id = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]
    cur.execute("INSERT INTO receipts (assignment_id, base_label) VALUES (?, 'base')", (assignment_id,))
    conn.commit()

    receipt_id = cur.execute("SELECT id FROM receipts LIMIT 1").fetchone()[0]

    # Attempt to insert receipt_log with non-existing owner_id should fail
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute(
            "INSERT INTO receipt_log (receipt_id, assignment_id, owner_id, client_id, receipt_no, period, issue_date, amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (receipt_id, assignment_id, 9999, client_id, 1, '2026-01-01', '2026-01-01', 500),
        )

    conn.close()


def test_assignment_rent_amount_not_null(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path, monkeypatch)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Need unit and client
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C2','PP')")
    cur.execute("INSERT INTO units (reference) VALUES ('U3')")
    conn.commit()

    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]

    # rent_amount is NOT NULL; inserting NULL should raise
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute(
            "INSERT INTO assignments (unit_id, client_id, start_date, rent_amount) VALUES (?, ?, '2026-01-01', NULL)",
            (unit_id, client_id),
        )

    conn.close()
