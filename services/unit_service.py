from database import get_connection


def create_unit(reference, city=None, neighborhood=None, floor=None, unit_type=None):
    if not reference or not reference.strip():
        raise ValueError("reference is required")
    if unit_type is not None and unit_type not in ("apt", "store", "building"):
        raise ValueError("unit_type must be one of: apt, store, building")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO units (reference, city, neighborhood, floor, unit_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (reference.strip(), city, neighborhood, floor, unit_type),
    )
    conn.commit()
    conn.close()


def list_units():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM units ORDER BY id")
    units = cur.fetchall()
    conn.close()
    return units


def get_unit(unit_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM units WHERE id = ?", (unit_id,))
    unit = cur.fetchone()
    conn.close()
    return unit


def update_unit(unit_id, reference=None, city=None, neighborhood=None, floor=None, unit_type=None):
    if unit_type is not None and unit_type not in ("apt", "store", "building"):
        raise ValueError("unit_type must be one of: apt, store, building")

    fields = []
    params = []
    if reference is not None:
        if not reference.strip():
            raise ValueError("reference cannot be empty")
        fields.append("reference = ?")
        params.append(reference.strip())
    if city is not None:
        fields.append("city = ?")
        params.append(city)
    if neighborhood is not None:
        fields.append("neighborhood = ?")
        params.append(neighborhood)
    if floor is not None:
        fields.append("floor = ?")
        params.append(floor)
    if unit_type is not None:
        fields.append("unit_type = ?")
        params.append(unit_type)

    if not fields:
        return

    params.append(unit_id)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE units SET {', '.join(fields)} WHERE id = ?", tuple(params))
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        raise ValueError(f"Unit {unit_id} not found")
    conn.close()


def delete_unit(unit_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM units WHERE id = ?", (unit_id,))
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        raise ValueError(f"Unit {unit_id} not found")
    conn.close()
