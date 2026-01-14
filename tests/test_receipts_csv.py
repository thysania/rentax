from pathlib import Path
import sqlite3
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


def test_generate_receipts_report_formats(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # Setup minimal data: owner, unit, client, ownership, assignment, receipt
    cur.execute("INSERT INTO owners (name, family_count, legal_id) VALUES ('OR', 0, 'LIDR')")
    cur.execute("INSERT INTO units (reference, city) VALUES ('UR','CR')")
    cur.execute("INSERT INTO clients (name, client_type, legal_id) VALUES ('CR','PP','CLIDR')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 100))
    cur.execute(
        """
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (unit_id, owner_id, client_id, 100, 'none', None, None, '01/01/2026', None, 1000, 0),
    )
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]
    # create a receipt and a partial payment
    r1 = rsvc.create_receipt(aid, '2026-01-01', '2026-01-05', 1000)
    cur.execute("SELECT uid FROM receipt_log WHERE receipt_id = ?", (r1,))
    uid = cur.fetchone()[0]

    import services.payments_service as psvc
    psvc.create_payment(uid, 400, '2026-01-06')

    conn.commit()

    # detailed
    headers, rows = rsvc.generate_receipts_report(2026, csv_format='detailed')
    assert 'uid' in headers
    assert len(rows) == 1
    r = rows[0]
    assert r['amount'] == '1000.00'
    assert r['amount_received'] == '400.00'
    assert r['balance'] == '600.00'

    # by-owner
    headers2, rows2 = rsvc.generate_receipts_report(2026, csv_format='by-owner')
    assert 'total_nominal' in headers2
    assert len(rows2) == 1
    r2 = rows2[0]
    assert r2['total_nominal'] == '1000.00'
    assert r2['total_received'] == '400.00'

    # minimal
    headers3, rows3 = rsvc.generate_receipts_report(2026, csv_format='minimal')
    assert headers3 == ['owner_id', 'owner_name', 'total_received']
    assert len(rows3) == 1
    assert rows3[0]['total_received'] == '400.00'

    conn.close()


def test_cli_export_receipts_stdout(tmp_path, monkeypatch, capsys):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name, family_count, legal_id) VALUES ('OC', 0, 'LIDC')")
    cur.execute("INSERT INTO units (reference, city) VALUES ('UC','CC')")
    cur.execute("INSERT INTO clients (name, client_type, legal_id) VALUES ('CC','PP','CLIDC')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 100))
    cur.execute(
        """
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (unit_id, owner_id, client_id, 100, 'none', None, None, '01/01/2026', None, 1000, 0),
    )
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]
    import services.receipt_service as rsvc
    r1 = rsvc.create_receipt(aid, '2026-01-01', '2026-01-05', 500)

    conn.close()

    # simulate menu: choose export (4), year, owner blank, format detailed, output '-', then exit
    inputs = iter([
        '4',
        '2026',
        '',
        '1',
        '-',
    ] + ['0']*50)
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))

    from cli.receipts_menu import receipts_menu
    receipts_menu()

    captured = capsys.readouterr()
    # Should contain CSV headers for detailed format
    assert 'uid,receipt_id,assignment_id,unit_reference,owner_id,owner_name' in captured.out
    assert '500.00' in captured.out