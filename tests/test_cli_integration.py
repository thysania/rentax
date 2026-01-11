import re
from pathlib import Path
import sqlite3
import pytest

from database import initialize_database
import services.ownership_service as osvc

from cli.ownerships_menu import ownerships_menu
from cli.assignments_menu import assignments_menu


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


def test_ownerships_cli_add_list_delete(tmp_path, monkeypatch, capsys):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("INSERT INTO units (reference) VALUES ('U-CLI')")
    cur.execute("INSERT INTO owners (name) VALUES ('Owner-CLI')")
    conn.commit()
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    owner_id = cur.execute("SELECT id FROM owners LIMIT 1").fetchone()[0]
    conn.close()

    # Run ownerships_menu to add and list
    inputs = iter([
        '1',  # Add ownership
        str(unit_id),
        str(owner_id),
        '50',  # share
        'n',   # alternate
        '2',   # List
        '',    # Unit ID filter (blank = all)
        '',    # Press Enter to continue...
        '0',   # Exit
    ])

    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    ownerships_menu()
    out = capsys.readouterr().out

    assert 'U-CLI' in out
    assert 'Owner-CLI' in out
    assert '50' in out

    # Parse ownership id from listing
    m = re.search(r"^(\d+)\s*\|\s*U-CLI", out, re.M)
    assert m, "Ownership listing line not found"
    oid = m.group(1)

    # Run again to delete and verify absence
    inputs2 = iter([
        '4',
        oid,
        'y',
        '2',
        '',
        '0',
    ])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs2))
    ownerships_menu()
    out2 = capsys.readouterr().out

    # After deletion listing should show no ownerships or not show Owner-CLI
    assert 'Owner-CLI' not in out2


def test_assignments_cli_add_and_list(tmp_path, monkeypatch, capsys):
    db = _setup_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("INSERT INTO units (reference) VALUES ('U-ASS')")
    cur.execute("INSERT INTO clients (name, client_type) VALUES ('Client-ASS','PP')")
    conn.commit()
    unit_id = cur.execute("SELECT id FROM units LIMIT 1").fetchone()[0]
    client_id = cur.execute("SELECT id FROM clients LIMIT 1").fetchone()[0]
    conn.close()

    inputs = iter([
        '1',  # Add assignment
        str(unit_id),
        str(client_id),
        '2026-01-01',
        '',      # end date blank
        '750',   # rent
        '0',     # ras_ir
        '2',     # List
        '',      # press enter
        '0',
    ])

    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    assignments_menu()
    out = capsys.readouterr().out

    assert 'U-ASS' in out
    assert 'Client-ASS' in out
    assert '750' in out
