from pathlib import Path
import sqlite3
import pytest

from database import initialize_database
import services.taxes_service as tsvc
import services.receipt_service as rsvc
import services.payments_service as psvc


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


def test_tax_zero_for_low_income(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # owner receives 10k gross in the year
    cur.execute("INSERT INTO owners (name, family_count) VALUES ('T1', 0)")
    cur.execute("INSERT INTO units (reference) VALUES ('UT1')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C1','PP')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    # Create ownership and assignment and one receipt split
    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 100))
    cur.execute("""
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (unit_id, owner_id, client_id, 100, 'none', None, None, '01/01/2026', None, 1000, 0))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]
    r1 = rsvc.create_receipt(aid, '2026-01-01', '2026-01-05', 10000)

    # Record payment as full (no RAS withheld)
    cur.execute("SELECT uid FROM receipt_log WHERE receipt_id = ?", (r1,))
    uid = cur.fetchone()[0]
    psvc.create_payment(uid, 10000, '2026-01-05')

    conn.commit()

    res = tsvc.compute_owner_taxes_for_year(owner_id, 2026)

    assert res['gross_revenue'] == 10000.0
    # final_tax is an integer (rounded up) and should be zero in this case
    assert res['final_tax'] == 0

    conn.close()


def test_tax_calculation_with_family_and_ras(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # owner receives 100k gross, family_count 2, but client withholds 10% (10k)
    cur.execute("INSERT INTO owners (name, family_count) VALUES ('T2', 2)")
    cur.execute("INSERT INTO units (reference) VALUES ('UT2')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C2','PP')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    # ownership + assignment
    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 100))
    cur.execute("""
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (unit_id, owner_id, client_id, 100, 'none', None, None, '01/01/2026', None, 10000, 0))
    conn.commit()

    aid = cur.execute("SELECT id FROM assignments LIMIT 1").fetchone()[0]

    # create receipts totaling 100k
    for m in range(1, 11):
        month = f"2026-{m:02d}-01"
        rsvc.create_receipt(aid, month, month, 10000)

    # Now mark payments as client withholding 10%: owner receives 90000 total
    cur.execute("SELECT uid FROM receipt_log WHERE owner_id = ? ORDER BY uid", (owner_id,))
    uids = [r[0] for r in cur.fetchall()]
    for uid in uids:
        # each nominal 10000, owner receives 9000
        psvc.create_payment(uid, 9000, '2026-06-01')

    conn.commit()

    res = tsvc.compute_owner_taxes_for_year(owner_id, 2026)

    # manual calculation
    gross = 100000.0
    taxable = round(gross * 0.6, 2)  # 60000
    # bracket for 60000 is 40001-60000 -> 10% and deduction 4000
    initial_tax = taxable * 0.10 - 4000  # 2000
    fam_ded = min(2 * 500, 3000)  # 1000
    after_family = initial_tax - fam_ded  # 1000
    ras_withheld = gross - 90000.0  # 10000
    final = max(0, __import__('math').ceil(after_family - ras_withheld))  # 0

    assert res['gross_revenue'] == gross
    assert res['taxable_amount'] == taxable
    # Allow small float differences on initial_tax
    assert round(res['initial_tax'], 2) == round(initial_tax, 2)
    assert res['family_deduction'] == fam_ded
    assert round(res['ras_withheld'], 2) == round(ras_withheld, 2)
    assert res['final_tax'] == final

    conn.close()


def test_final_tax_rounds_up(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # Make gross such that taxable*rate - deduction is small fractional > 0
    # Choose taxable = 40001.5 -> gross = taxable / 0.6
    taxable = 40001.5
    gross = taxable / 0.6  # = 66669.166666...

    cur.execute("INSERT INTO owners (name, family_count) VALUES ('T3', 0)")
    cur.execute("INSERT INTO units (reference) VALUES ('UT3')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C3','PP')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    # create ownership and assignment
    cur.execute("INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate) VALUES (?, ?, ?, 0)", (unit_id, owner_id, 100))
    # create a receipt_log record directly for the owner with amount = gross
    cur.execute("INSERT INTO receipts (assignment_id, base_label) VALUES (?, 'base')", (1,))
    conn.commit()

    # Insert a receipt_log row directly for the owner with amount = gross
    cur.execute("INSERT INTO receipt_log (receipt_id, assignment_id, owner_id, client_id, receipt_no, period, issue_date, amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (1, 1, owner_id, client_id, 1, '2026-01-01', '2026-01-05', gross))
    conn.commit()

    # Record full payment so ras_withheld is zero and the small fractional tax remains
    cur.execute("SELECT uid FROM receipt_log WHERE owner_id = ? LIMIT 1", (owner_id,))
    uid = cur.fetchone()[0]
    psvc.create_payment(uid, gross, '2026-01-05')
    conn.commit()

    res = tsvc.compute_owner_taxes_for_year(owner_id, 2026)

    # initial tax = taxable * 0.10 - 4000 = 4000.15 - 4000 = 0.15 -> final should ceil to 1
    assert res['final_tax'] == 1

    conn.close()
