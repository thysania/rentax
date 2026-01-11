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


def test_receipt_splitting_basic(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # Setup unit, owners, client, assignment
    cur.execute("INSERT INTO units (reference) VALUES ('U-SPL')")
    cur.execute("INSERT INTO owners (name) VALUES ('O1')")
    cur.execute("INSERT INTO owners (name) VALUES ('O2')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C1','PP')")
    conn.commit()

    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    o1 = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    o2 = cur.execute("SELECT id FROM owners LIMIT 2 OFFSET 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, o1, 60))
    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, o2, 40))
    cur.execute("INSERT INTO assignments (unit_id, client_id, start_date, rent_amount, ras_ir) VALUES (?, ?, '2026-01-01', 100, 0)", (unit_id, client_id))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]

    receipt_id = rsvc.create_receipt(aid, '2026-01-01', '2026-01-05', 1000)
    cur.execute("SELECT amount FROM receipt_log WHERE receipt_id = ? ORDER BY owner_id", (receipt_id,))
    rows = [r[0] for r in cur.fetchall()]
    conn.close()

    assert len(rows) == 2
    assert rows[0] == 600.0
    assert rows[1] == 400.0


def test_receipt_alternating(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # Setup unit, owners, client, assignment
    cur.execute("INSERT INTO units (reference) VALUES ('U-ALT')")
    cur.execute("INSERT INTO owners (name) VALUES ('OddOwner')")
    cur.execute("INSERT INTO owners (name) VALUES ('EvenOwner')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C2','PM')")
    conn.commit()

    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    o_odd = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    o_even = cur.execute("SELECT id FROM owners LIMIT 2 OFFSET 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate, odd_even) VALUES (?, ?, ?, 1, 'odd')", (unit_id, o_odd, 100))
    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate, odd_even) VALUES (?, ?, ?, 1, 'even')", (unit_id, o_even, 100))
    cur.execute("INSERT INTO assignments (unit_id, client_id, start_date, rent_amount, ras_ir) VALUES (?, ?, '2026-01-01', 200, 0)", (unit_id, client_id))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]

    # For January (odd month) odd owner gets the full amount
    receipt_id = rsvc.create_receipt(aid, '2026-01-01', '2026-01-05', 500)
    cur.execute("SELECT owner_id, amount FROM receipt_log WHERE receipt_id = ? ORDER BY owner_id", (receipt_id,))
    rows = cur.fetchall()
    conn.close()

    assert len(rows) == 1
    assert rows[0][1] == 500.0


def test_receipt_incrementing_number_and_rounding(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO units (reference) VALUES ('U-ROUND')")
    cur.execute("INSERT INTO owners (name) VALUES ('O1')")
    cur.execute("INSERT INTO owners (name) VALUES ('O2')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C3','PP')")
    conn.commit()

    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    o1 = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    o2 = cur.execute("SELECT id FROM owners LIMIT 2 OFFSET 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    # 33% and 67% shares
    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, o1, 33))
    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, o2, 67))
    cur.execute("INSERT INTO assignments (unit_id, client_id, start_date, rent_amount, ras_ir) VALUES (?, ?, '2026-01-01', 100, 0)", (unit_id, client_id))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]

    r1 = rsvc.create_receipt(aid, '2026-01-01', '2026-01-05', 100)
    r2 = rsvc.create_receipt(aid, '2026-02-01', '2026-02-05', 100)

    cur.execute("SELECT receipt_no FROM receipt_log WHERE receipt_id = ? ORDER BY uid", (r1,))
    nums1 = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT receipt_no FROM receipt_log WHERE receipt_id = ? ORDER BY uid", (r2,))
    nums2 = [r[0] for r in cur.fetchall()]

    # For r1 all rows have receipt_no = 1, r2 -> 2
    assert all(n == 1 for n in nums1)
    assert all(n == 2 for n in nums2)

    # Check rounding sums to 100
    cur.execute("SELECT SUM(amount) FROM receipt_log WHERE receipt_id = ?", (r1,))
    total = cur.fetchone()[0]
    assert round(total, 2) == 100.0

    conn.close()
