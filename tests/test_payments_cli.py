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


def test_record_payment_via_cli(tmp_path, monkeypatch, capsys):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # setup a simple receipt_log row
    cur.execute("INSERT INTO owners (name, family_count, legal_id) VALUES ('OP', 0, 'LID')")
    cur.execute("INSERT INTO units (reference, city) VALUES ('U-PY','C')")
    cur.execute("INSERT INTO clients (name, client_type, legal_id) VALUES ('CP','PP','CLID')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 100))
    cur.execute("""
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (unit_id, owner_id, client_id, 100, 'none', None, None, '01/01/2026', None, 1000, 0))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]
    # create a receipt
    import services.receipt_service as rsvc
    r1 = rsvc.create_receipt(aid, '2026-01-01', '2026-01-05', 1000)

    # find uid
    cur.execute("SELECT uid FROM receipt_log WHERE receipt_id = ?", (r1,))
    uid = cur.fetchone()[0]

    conn.close()

    # simulate CLI interaction: choose '3' and provide uid and amount
    inputs = iter([
        '3',
        str(uid),
        '900',
        '2026-01-06',
        'partial payment',
    ] + ['0']*50)
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))

    from cli.receipts_menu import receipts_menu
    receipts_menu()

    # verify payment recorded
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT amount_received, received_at, note FROM payments WHERE receipt_log_uid = ?", (uid,))
    row = cur.fetchone()
    assert row is not None
    assert abs(row[0] - 900.0) < 1e-6
    assert row[1] == '2026-01-06'
    assert row[2] == 'partial payment'

    conn.close()


def test_payments_affect_taxes(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name, family_count, legal_id) VALUES ('OT', 0, 'LID-T')")
    cur.execute("INSERT INTO units (reference, city) VALUES ('U-T','CT')")
    cur.execute("INSERT INTO clients (name, client_type, legal_id) VALUES ('CT','PP','CLID-T')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 100))
    cur.execute("""
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (unit_id, owner_id, client_id, 100, 'none', None, None, '01/01/2026', None, 1000, 0))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]
    import services.receipt_service as rsvc
    r1 = rsvc.create_receipt(aid, '2026-01-01', '2026-01-05', 10000)
    cur.execute("SELECT uid FROM receipt_log WHERE receipt_id = ?", (r1,))
    uid = cur.fetchone()[0]

    # record partial payment: owner receives 9000, ras_withheld should be 1000
    import services.payments_service as psvc
    psvc.create_payment(uid, 9000, '2026-01-05')

    conn.commit()

    import services.taxes_service as tsvc
    res = tsvc.compute_owner_taxes_for_year(owner_id, 2026)

    assert round(res['ras_withheld'], 2) == 1000.00

    conn.close()