from pathlib import Path
import sqlite3
from database import initialize_database
import services.taxes_service as tsvc


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


def test_generate_minimal_csv(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name, family_count, legal_id) VALUES ('O1', 0, 'LID1')")
    cur.execute("INSERT INTO units (reference, city) VALUES ('U1','City')")
    cur.execute("INSERT INTO clients (name, client_type, legal_id) VALUES ('C1','PP','CLID1')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 100))
    cur.execute("INSERT INTO assignments (unit_id, client_id, start_date, rent_amount, ras_ir) VALUES (?, ?, '2026-01-01', 1000, 0)", (unit_id, client_id))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]
    # create a receipt via receipts/service to get proper receipt_log & uid
    import services.receipt_service as rsvc
    r1 = rsvc.create_receipt(aid, '2026-01-01', '2026-01-05', 10000)
    cur.execute("SELECT uid FROM receipt_log WHERE receipt_id = ?", (r1,))
    uid = cur.fetchone()[0]
    # full payment
    import services.payments_service as psvc
    psvc.create_payment(uid, 10000, '2026-01-05')

    headers, rows = tsvc.generate_taxes_report(2026, csv_format='minimal')

    assert headers == ['owner_id', 'owner_name', 'year', 'gross_revenue', 'rounded_tax']
    assert len(rows) == 1
    r = rows[0]
    assert r['owner_name'] == 'O1'
    assert float(r['gross_revenue']) == 10000.0

    conn.close()


def test_generate_by_assignment_csv(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name, family_count, legal_id) VALUES ('O2', 1, 'LID2')")
    cur.execute("INSERT INTO units (reference, city) VALUES ('U2','City2')")
    cur.execute("INSERT INTO clients (name, client_type, legal_id) VALUES ('C2','PP','CLID2')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 100))
    cur.execute("INSERT INTO assignments (unit_id, client_id, start_date, rent_amount, ras_ir) VALUES (?, ?, '2026-01-01', 1000, 0)", (unit_id, client_id))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]
    import services.receipt_service as rsvc
    # create two receipts for same owner/assignment
    rsvc.create_receipt(aid, '2026-01-01', '2026-01-05', 1000)
    rsvc.create_receipt(aid, '2026-02-01', '2026-02-05', 2000)

    headers, rows = tsvc.generate_taxes_report(2026, csv_format='by-assignment')
    # Expect at least the two assignment lines + separator row + owner summary (so len >=3)
    assert 'unit_reference' in headers
    # find assignment rows
    assignment_rows = [r for r in rows if r.get('assignment_id')]
    assert len(assignment_rows) == 2
    summary_rows = [r for r in rows if r.get('rounded_tax')]
    assert len(summary_rows) == 1

    conn.close()