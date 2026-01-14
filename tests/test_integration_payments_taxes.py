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


def test_payments_reflected_in_detailed_report_service(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name, family_count, legal_id) VALUES ('OwnerINT', 0, 'LIDINT')")
    cur.execute("INSERT INTO units (reference, city) VALUES ('U-INT','CT')")
    cur.execute("INSERT INTO clients (name, client_type, legal_id) VALUES ('CINT','PP','CLIDINT')")
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

    # owner receives 9000 (client withheld 1000)
    import services.payments_service as psvc
    psvc.create_payment(uid, 9000.0, '2026-01-05')

    conn.commit()

    import services.taxes_service as tsvc
    headers, rows = tsvc.generate_taxes_report(2026, csv_format='detailed')

    # find owner row
    owner_row = None
    for r in rows:
        if r.get('owner_name') == 'OwnerINT':
            owner_row = r
            break

    assert owner_row is not None
    assert owner_row['rounded_tax'] == '0'
    assert owner_row['ras_withheld'] == '1000.00'
    assert owner_row['due_tax'] == '-1000.00'

    conn.close()


def test_end_to_end_cli_payment_and_csv(tmp_path, monkeypatch, capsys):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name, family_count, legal_id) VALUES ('OwnerCLI', 0, 'LIDCLI')")
    cur.execute("INSERT INTO units (reference, city) VALUES ('U-CLI-2','CityCLI')")
    cur.execute("INSERT INTO clients (name, client_type, legal_id) VALUES ('ClientCLI','PP','CLID-CLI')")
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

    conn.close()

    # Record payment via CLI
    inputs = iter([
        '3',
        str(uid),
        '9000',
        '2026-01-06',
        '',
    ] + ['0']*50)
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    from cli.receipts_menu import receipts_menu
    receipts_menu()

    # Now export taxes CSV via CLI to stdout
    inputs2 = iter([
        '2026',
        '',
        'y',
        'detailed',
        '-',
    ] + ['0']*50)
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs2))
    from cli.taxes_menu import taxes_menu
    taxes_menu()

    out = capsys.readouterr().out

    # Output should contain headers and the ras_withheld and due_tax reflecting the payment
    assert 'ras_withheld' in out
    assert '1000.00' in out
    assert '-1000.00' in out
