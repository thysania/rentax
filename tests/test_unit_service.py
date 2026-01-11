import sqlite3
from pathlib import Path
import pytest

from database import initialize_database
import services.unit_service as us


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


def test_create_list_get_update_delete_unit(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path, monkeypatch)

    us.create_unit('U-100', city='CityX', neighborhood='N1', floor=2, unit_type='apt')

    units = us.list_units()
    assert len(units) == 1
    u = units[0]
    assert u['reference'] == 'U-100'
    assert u['city'] == 'CityX'

    uid = u['id']
    fetched = us.get_unit(uid)
    assert fetched['reference'] == 'U-100'

    us.update_unit(uid, reference='U-101', city='CityY')
    updated = us.get_unit(uid)
    assert updated['reference'] == 'U-101'
    assert updated['city'] == 'CityY'

    us.delete_unit(uid)
    assert us.get_unit(uid) is None


def test_invalid_unit_type_and_reference(tmp_path, monkeypatch):
    _ = _setup_db(tmp_path, monkeypatch)

    with pytest.raises(ValueError):
        us.create_unit('', city='X')

    with pytest.raises(ValueError):
        us.create_unit('R1', unit_type='invalid')

    us.create_unit('R2')
    units = us.list_units()
    uid = units[0]['id']

    with pytest.raises(ValueError):
        us.update_unit(uid, unit_type='bad')
