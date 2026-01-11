import os
import sqlite3
import tempfile
import shutil
from pathlib import Path

import pytest

from database import initialize_database, DB_PATH, SCHEMA_PATH


def test_initialize_database_missing_schema(tmp_path, monkeypatch, capsys):
    # Point schema path to a non-existing file
    monkeypatch.setattr(__import__('database'), 'SCHEMA_PATH', Path(tmp_path / 'schema.sql'))
    # Ensure DB path is under tmp_path
    monkeypatch.setattr(__import__('database'), 'DB_PATH', Path(tmp_path / 'database.db'))

    with pytest.raises(FileNotFoundError):
        initialize_database()


def test_initialize_database_corrupt_schema(tmp_path, monkeypatch):
    # Create a corrupt schema file
    schema_file = tmp_path / 'schema.sql'
    schema_file.write_text('CREATE TABLE IF NOT EXISTS bad_table (id INTEGER PRIMARY KEY AUTOINCREMENT, );')

    monkeypatch.setattr(__import__('database'), 'SCHEMA_PATH', schema_file)
    monkeypatch.setattr(__import__('database'), 'DB_PATH', Path(tmp_path / 'database.db'))

    with pytest.raises(sqlite3.DatabaseError):
        initialize_database()


def test_initialize_database_success(tmp_path, monkeypatch):
    # Create a minimal valid schema
    schema_file = tmp_path / 'schema.sql'
    schema_file.write_text('CREATE TABLE IF NOT EXISTS foo (id INTEGER PRIMARY KEY AUTOINCREMENT);')

    monkeypatch.setattr(__import__('database'), 'SCHEMA_PATH', schema_file)
    db_path = Path(tmp_path / 'database.db')
    monkeypatch.setattr(__import__('database'), 'DB_PATH', db_path)

    # Should not raise
    initialize_database()
    # Verify file exists and table created
    assert db_path.exists()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='foo';")
    rows = cur.fetchall()
    conn.close()
    assert len(rows) == 1
