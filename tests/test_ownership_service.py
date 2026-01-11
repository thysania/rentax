import sqlite3
from pathlib import Path
import pytest

from database import initialize_database
import services.ownership_service as osvc


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


def test_create_invalid_share_percent_and_odd_even(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("INSERT INTO units (reference) VALUES ('U1')")
    cur.execute("INSERT INTO owners (name) VALUES ('O1')")
    conn.commit()

    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]

    with pytest.raises(ValueError):
        osvc.create_ownership(unit_id, owner_id, 0)

    with pytest.raises(ValueError):
        osvc.create_ownership(unit_id, owner_id, 150)

    # alternate=1 must have odd_even
    with pytest.raises(ValueError):
        osvc.create_ownership(unit_id, owner_id, 10, alternate=1)

    conn.close()


def test_totals_and_mixed_validity(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("INSERT INTO units (reference) VALUES ('U2')")
    cur.execute("INSERT INTO owners (name) VALUES ('O1')")
    cur.execute("INSERT INTO owners (name) VALUES ('O2')")
    cur.execute("INSERT INTO owners (name) VALUES ('O3')")
    conn.commit()

    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    o1 = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    o2 = cur.execute("SELECT id FROM owners LIMIT 2 OFFSET 1").fetchone()[0]
    o3 = cur.execute("SELECT id FROM owners LIMIT 3 OFFSET 2").fetchone()[0]

    # Add a non-alternating owner with 30%
    osvc.create_ownership(unit_id, o1, 30, alternate=0)

    # Add odd alternating 20% (odd_total=50, even_total=30) - valid
    osvc.create_ownership(unit_id, o2, 20, alternate=1, odd_even='odd')

    # Add even alternating 10% (odd_total=50, even_total=40) - valid
    osvc.create_ownership(unit_id, o3, 10, alternate=1, odd_even='even')

    # Now adding odd alternating 60% would make odd_total 110% -> invalid
    with pytest.raises(ValueError):
        osvc.create_ownership(unit_id, o3, 60, alternate=1, odd_even='odd')

    conn.close()


def test_each_period_must_have_owner(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("INSERT INTO units (reference) VALUES ('U3')")
    cur.execute("INSERT INTO owners (name) VALUES ('O1')")
    conn.commit()

    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    o1 = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]

    # Adding only odd alternating owner should fail because even_total would be 0
    with pytest.raises(ValueError):
        osvc.create_ownership(unit_id, o1, 50, alternate=1, odd_even='odd')

    # But adding non-alternating owner covers both periods
    osvc.create_ownership(unit_id, o1, 50, alternate=0)

    conn.close()


def test_update_and_delete_behaviors(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("INSERT INTO units (reference) VALUES ('U4')")
    cur.execute("INSERT INTO owners (name) VALUES ('O1')")
    cur.execute("INSERT INTO owners (name) VALUES ('O2')")
    conn.commit()

    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    o1 = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    o2 = cur.execute("SELECT id FROM owners LIMIT 2 OFFSET 1").fetchone()[0]

    # create two non-alternating owners splitting 60 and 40
    osvc.create_ownership(unit_id, o1, 60, alternate=0)
    osvc.create_ownership(unit_id, o2, 40, alternate=0)

    rows = osvc.list_ownerships(unit_id)
    assert len(rows) == 2

    # updating o2 to 50 would make total 110 -> invalid
    oid = rows[1]['id']
    with pytest.raises(ValueError):
        osvc.update_ownership(oid, share_percent=50)

    # deleting one owner leaving only one is allowed
    osvc.delete_ownership(oid)
    rows2 = osvc.list_ownerships(unit_id)
    assert len(rows2) == 1

    # deleting last one (only ownership remaining) is allowed
    osvc.delete_ownership(rows2[0]['id'])
    rows3 = osvc.list_ownerships(unit_id)
    assert len(rows3) == 0

    conn.close()


def test_list_ownerships_with_names(tmp_path, monkeypatch):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("INSERT INTO units (reference) VALUES ('U-A')")
    cur.execute("INSERT INTO owners (name) VALUES ('OwnerA')")
    conn.commit()

    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]

    osvc.create_ownership(unit_id, owner_id, 50, alternate=0)
    rows = osvc.list_ownerships_with_names(unit_id)
    assert len(rows) == 1
    r = rows[0]
    assert r['unit_reference'] == 'U-A'
    assert r['owner_name'] == 'OwnerA'

    conn.close()
