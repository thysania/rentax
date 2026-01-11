from pathlib import Path
import sqlite3
import pytest

from database import initialize_database
import services.receipt_service as rsvc


def _setup_db(tmp_path, monkeypatch):
    project_root = Path(__file__).resolve().parents[1]
    orig_schema = project_root / "sql" / "schema.sql"
    schema_file = tmp_path / "schema.sql"
    schema_file.write_text(orig_schema.read_text())

    monkeypatch.setattr(__import__("database"), 'SCHEMA_PATH', schema_file)
    db_path = Path(tmp_path / "database.db")
    monkeypatch.setattr(__import__("database"), 'DB_PATH', db_path)

    initialize_database()
    return db_path


def test_list_receipt_logs_with_names(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # setup minimal data: unit, owner, client, assignment, receipt, receipt_log
    cur.execute("INSERT INTO units (reference) VALUES ('U-R')")
    cur.execute("INSERT INTO owners (name) VALUES ('O-R')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C-R','PP')")
    conn.commit()

    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO assignments (unit_id, client_id, start_date, rent_amount, ras_ir) VALUES (?, ?, '2026-01-01', 200, 0)", (unit_id, client_id))
    conn.commit()
    assignment_id = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO receipts (assignment_id, base_label) VALUES (?, 'base')", (assignment_id,))
    conn.commit()
    receipt_id = cur.execute("SELECT id FROM receipts LIMIT 1").fetchone()[0]

    cur.execute(
        "INSERT INTO receipt_log (receipt_id, assignment_id, owner_id, client_id, receipt_no, period, issue_date, amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (receipt_id, assignment_id, owner_id, client_id, 1, '2026-01-01', '2026-01-05', 200),
    )
    conn.commit()

    rows = rsvc.list_receipt_logs_with_names()
    assert len(rows) == 1
    r = rows[0]
    assert r['unit_reference'] == 'U-R'
    assert r['owner_name'] == 'O-R'
    assert r['client_name'] == 'C-R'

    conn.close()
