import sqlite3
from pathlib import Path
import pytest

from database import initialize_database
import services.client_service as cs


def _setup_db(tmp_path, monkeypatch):
    # Copy project's schema.sql into the temp schema file
    project_root = Path(__file__).resolve().parents[1]
    orig_schema = project_root / "sql" / "schema.sql"
    schema_file = tmp_path / "schema.sql"
    schema_file.write_text(orig_schema.read_text())

    monkeypatch.setattr(__import__("database"), 'SCHEMA_PATH', schema_file)
    db_path = Path(tmp_path / "database.db")
    monkeypatch.setattr(__import__("database"), 'DB_PATH', db_path)

    initialize_database()
    return db_path


def test_create_and_list_client(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path, monkeypatch)

    cs.create_client('Alice', 'PP', phone='123', legal_id='L1')

    clients = cs.list_clients()
    assert len(clients) == 1
    c = clients[0]
    assert c['name'] == 'Alice'
    assert c['client_type'] == 'PP'


def test_get_update_delete_client(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path, monkeypatch)

    cs.create_client('Bob', 'PM', phone='555', legal_id='L2')
    clients = cs.list_clients()
    client_id = clients[0]['id']

    c = cs.get_client(client_id)
    assert c['name'] == 'Bob'

    cs.update_client(client_id, name='Bobby')
    c2 = cs.get_client(client_id)
    assert c2['name'] == 'Bobby'

    cs.delete_client(client_id)
    assert cs.get_client(client_id) is None


def test_invalid_client_type(tmp_path, monkeypatch):
    db_path = _setup_db(tmp_path, monkeypatch)

    with pytest.raises(ValueError):
        cs.create_client('X', 'XX')
