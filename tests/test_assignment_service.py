from pathlib import Path
import sqlite3
import pytest

from database import initialize_database
import services.assignment_service as asv


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


def test_create_assignment_and_ras_ir(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name) VALUES ('O1')")
    cur.execute("INSERT INTO units (reference) VALUES ('U1')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C1','PP')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    # New assignment schema: owner_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir
    cur.execute("""
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (unit_id, owner_id, client_id, 100, 'none', None, None, '01/01/2026', '31/01/2026', 500, 1))

    rows = asv.list_assignments()
    assert len(rows) == 1
    r = rows[0]
    assert r['ras_ir'] == 1
    assert r['rent_amount'] == 500

    # name-aware listing
    rows2 = asv.list_assignments_with_names()
    assert len(rows2) == 1
    r2 = rows2[0]
    assert r2['unit_reference'] == 'U1'
    assert r2['client_name'] == 'C1'

    conn.close()


def test_create_assignment_requires_unit_and_client(tmp_path, monkeypatch):
    _ = _setup_db(tmp_path, monkeypatch)

    with pytest.raises(ValueError):
        asv.create_assignment(9999, 1, '01/01/2026', None, 100)

    with pytest.raises(ValueError):
        asv.create_assignment(1, 9999, '01/01/2026', None, 100)


def test_overlapping_assignments_rejected(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name) VALUES ('O2')")
    cur.execute("INSERT INTO units (reference) VALUES ('U2')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C2','PP')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("""
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (unit_id, owner_id, client_id, 100, 'none', None, None, '01/01/2026', '30/06/2026', 400, 0))

    # Overlap
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("""
            INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (unit_id, owner_id, client_id, 100, 'none', None, None, '01/05/2026', '01/08/2026', 400, 0))

    # Non-overlap afterwards
    cur.execute("""
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (unit_id, owner_id, client_id, 100, 'none', None, None, '01/07/2026', '31/12/2026', 400, 0))

    conn.close()


def test_update_assignment_overlap_detection(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name) VALUES ('O3')")
    cur.execute("INSERT INTO units (reference) VALUES ('U3')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C3','PM')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    cur.execute("""
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (unit_id, owner_id, client_id, 100, 'none', None, None, '01/01/2026', '31/03/2026', 300, 0))
    cur.execute("""
        INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (unit_id, owner_id, client_id, 100, 'none', None, None, '01/04/2026', '30/06/2026', 300, 0))

    rows = asv.list_assignments()
    a1 = rows[0]['id']
    a2 = rows[1]['id']

    # Try to expand a2 to overlap a1
    with pytest.raises(ValueError):
        asv.update_assignment(a2, start_date='2026-03-15')

    conn.close()


def test_rent_amount_required(tmp_path, monkeypatch):
    _ = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(_)
    cur = conn.cursor()

    cur.execute("INSERT INTO owners (name) VALUES ('O4')")
    cur.execute("INSERT INTO units (reference) VALUES ('U4')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('C4','PP')")
    conn.commit()

    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]

    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("""
            INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (unit_id, owner_id, client_id, 100, 'none', None, None, '01/01/2026', None, None, 0))

    conn.close()
