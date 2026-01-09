import sqlite3
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "rent.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection():
    """
    Returns a SQLite connection.
    Creates database + tables automatically on first run.
    """
    first_run = not DB_PATH.exists()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # <-- IMPORTANT FIX

    if first_run:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()

    return conn


# --------------------
# OWNERS
# --------------------

def list_owners():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, phone, cnie, family_deduction
        FROM owners
        ORDER BY name
    """)
    rows = cur.fetchall()
    conn.close()

    return rows


def add_owner(name, phone, cnie, family_deduction=0):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO owners (name, phone, cnie, family_deduction)
        VALUES (?, ?, ?, ?)
    """, (name, phone, cnie, family_deduction))

    conn.commit()
    conn.close()


# --------------------
# CLIENTS
# --------------------

def list_clients():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, phone, cnie, client_type, ras_ir
        FROM clients
        ORDER BY name
    """)
    rows = cur.fetchall()
    conn.close()

    return rows


def add_client(name, phone, cnie, client_type, ras_ir=0):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO clients (name, phone, cnie, client_type, ras_ir)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, cnie, client_type, ras_ir))

    conn.commit()
    conn.close()


# --------------------
# UNITS
# --------------------

def list_units():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, label, city, neighbourhood, floor, unit_type, is_vacant
        FROM units
        ORDER BY city, label
    """)
    rows = cur.fetchall()
    conn.close()

    return rows


def add_unit(label, city, neighbourhood, floor, unit_type, is_vacant=1):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO units (label, city, neighbourhood, floor, unit_type, is_vacant)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (label, city, neighbourhood, floor, unit_type, is_vacant))

    conn.commit()
    conn.close()


# --------------------
# ASSIGNMENTS / RECEIPTS
# --------------------

def list_assignments():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT a.id,
               o.name AS owner,
               c.name AS client,
               u.label AS unit,
               a.start_date,
               a.end_date,
               a.rent_amount,
               a.alternate,
               a.odd_even
        FROM assignments a
        JOIN owners o ON o.id = a.owner_id
        JOIN clients c ON c.id = a.client_id
        JOIN units u ON u.id = a.unit_id
        ORDER BY a.start_date DESC
    """)
    rows = cur.fetchall()
    conn.close()

    return rows


def add_assignment(
    owner_id,
    client_id,
    unit_id,
    start_date,
    rent_amount,
    end_date=None,
    alternate=0,
    odd_even=None
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO assignments (
            owner_id,
            client_id,
            unit_id,
            start_date,
            end_date,
            rent_amount,
            alternate,
            odd_even
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        owner_id,
        client_id,
        unit_id,
        start_date,
        end_date,
        rent_amount,
        alternate,
        odd_even
    ))

    conn.commit()
    conn.close()