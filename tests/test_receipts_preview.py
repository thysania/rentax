from pathlib import Path
import sqlite3
from database import initialize_database


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


def test_compute_receipt_split_rounding(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name, family_count) VALUES ('OP1', 0)")
    cur.execute("INSERT INTO units (reference) VALUES ('U-PRE')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('CPRE','PP')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 33.33))
    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 66.67))
    cur.execute("INSERT INTO assignments (unit_id, client_id, start_date, rent_amount, ras_ir) VALUES (?, ?, '2026-01-01', 1000, 0)", (unit_id, client_id))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]

    import services.receipt_service as rsvc
    split = rsvc.compute_receipt_split(aid, '2026-01-01', 100.00)

    # two entries, amounts should sum to 100.00
    assert len(split) == 2
    ssum = sum(s['amount'] for s in split)
    assert round(ssum, 2) == 100.00

    conn.close()


def test_receipt_preview_cancel(tmp_path, monkeypatch, capsys):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # setup minimal scenario
    cur.execute("INSERT INTO owners (name, family_count) VALUES ('OPC', 0)")
    cur.execute("INSERT INTO units (reference) VALUES ('U-C')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C-C','PP')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 100))
    cur.execute("INSERT INTO assignments (unit_id, client_id, start_date, rent_amount, ras_ir) VALUES (?, ?, '2026-01-01', 1000, 0)", (unit_id, client_id))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]
    conn.close()

    # run CLI and cancel at confirm
    inputs = iter([
        '1',
        str(aid),
        '2026-01-01',
        '2026-01-05',
        '1000',
        'n',  # cancel
        '0',
    ])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    from cli.receipts_menu import receipts_menu
    receipts_menu()

    # verify no receipt_log entries
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM receipt_log WHERE assignment_id = ?", (aid,))
    cnt = cur.fetchone()[0]
    assert cnt == 0
    conn.close()


def test_receipt_preview_confirm_creates(tmp_path, monkeypatch, capsys):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name, family_count) VALUES ('OPC2', 0)")
    cur.execute("INSERT INTO units (reference) VALUES ('U-C2')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C-C2','PP')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 100))
    cur.execute("INSERT INTO assignments (unit_id, client_id, start_date, rent_amount, ras_ir) VALUES (?, ?, '2026-01-01', 1000, 0)", (unit_id, client_id))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]
    conn.close()

    inputs = iter([
        '1',
        str(aid),
        '2026-01-01',
        '2026-01-05',
        '1000',
        'y',  # confirm
        '0',
    ])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    from cli.receipts_menu import receipts_menu
    receipts_menu()

    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM receipt_log WHERE assignment_id = ?", (aid,))
    cnt = cur.fetchone()[0]
    assert cnt == 1
    # verify amount matches total
    cur.execute("SELECT amount FROM receipt_log WHERE assignment_id = ?", (aid,))
    amt = cur.fetchone()[0]
    assert round(amt, 2) == 1000.00
    conn.close()
