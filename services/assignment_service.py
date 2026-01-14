from database import get_connection
from datetime import datetime


DATE_MAX = "9999-12-31"


def _parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except Exception:
        raise ValueError("Dates must be in dd/mm/yyyy format")


def _ensure_unit_and_client_exist(conn, unit_id, client_id):
    cur = conn.cursor()
    cur.execute("SELECT id FROM units WHERE id = ?", (unit_id,))
    if not cur.fetchone():
        raise ValueError(f"Unit {unit_id} not found")
    cur.execute("SELECT id FROM clients WHERE id = ?", (client_id,))
    if not cur.fetchone():
        raise ValueError(f"Client {client_id} not found")


def _check_overlap(conn, unit_id, start_date, end_date, exclude_assignment_id=None):
    # start_date and end_date are strings in YYYY-MM-DD
    new_start = start_date
    new_end = end_date if end_date is not None else DATE_MAX

    cur = conn.cursor()
    if exclude_assignment_id is not None:
        cur.execute(
            """
            SELECT id FROM assignments
            WHERE unit_id = ?
              AND id != ?
              AND NOT (COALESCE(end_date, ?) < ? OR start_date > ?)
            """,
            (unit_id, exclude_assignment_id, DATE_MAX, new_start, new_end),
        )
    else:
        cur.execute(
            """
            SELECT id FROM assignments
            WHERE unit_id = ?
              AND NOT (COALESCE(end_date, ?) < ? OR start_date > ?)
            """,
            (unit_id, DATE_MAX, new_start, new_end),
        )

    return cur.fetchone() is not None



def create_assignment(unit_id, owner_id, client_id, share_percent, alternation_type='none', cycle_length=None, cycle_position=None, start_date=None, end_date=None, rent_amount=None, ras_ir=0):
    if rent_amount is None:
        raise ValueError("rent_amount is required")
    if share_percent is None:
        raise ValueError("share_percent is required")
    if owner_id is None:
        raise ValueError("owner_id is required")
    if alternation_type not in ('none', 'odd_even', 'cycle'):
        raise ValueError("alternation_type must be one of 'none', 'odd_even', 'cycle'")
    try:
        start = _parse_date(start_date)
    except Exception:
        raise ValueError("start_date must be in dd/mm/yyyy format")
    if end_date is not None:
        try:
            end = _parse_date(end_date)
        except Exception:
            raise ValueError("end_date must be in dd/mm/yyyy format")
        if end < start:
            raise ValueError("end_date cannot be before start_date")
    if ras_ir not in (0, 1):
        raise ValueError("ras_ir must be 0 or 1")

    conn = get_connection()
    try:
        # Check FKs
        cur = conn.cursor()
        cur.execute("SELECT id FROM units WHERE id = ?", (unit_id,))
        if not cur.fetchone():
            raise ValueError(f"Unit {unit_id} not found")
        cur.execute("SELECT id FROM owners WHERE id = ?", (owner_id,))
        if not cur.fetchone():
            raise ValueError(f"Owner {owner_id} not found")
        cur.execute("SELECT id FROM clients WHERE id = ?", (client_id,))
        if not cur.fetchone():
            raise ValueError(f"Client {client_id} not found")

        # Check overlap (per unit, per period)
        if _check_overlap(conn, unit_id, start_date, end_date):
            raise ValueError("Assignment overlaps with an existing assignment for this unit")

        cur.execute(
            """
            INSERT INTO assignments (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (unit_id, owner_id, client_id, share_percent, alternation_type, cycle_length, cycle_position, start_date, end_date, rent_amount, ras_ir),
        )
        conn.commit()
    finally:
        conn.close()


def list_assignments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM assignments ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def list_assignments_with_names():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT a.id, a.unit_id, u.reference AS unit_reference, a.client_id, c.name AS client_name,
               a.start_date, a.end_date, a.rent_amount, a.ras_ir
        FROM assignments a
        JOIN units u ON a.unit_id = u.id
        JOIN clients c ON a.client_id = c.id
        ORDER BY a.id
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_assignment(assignment_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,))
    r = cur.fetchone()
    conn.close()
    return r


def update_assignment(assignment_id, start_date=None, end_date=None, rent_amount=None, ras_ir=None):
    if start_date is not None:
        _parse_date(start_date)
    if end_date is not None:
        _parse_date(end_date)
    if ras_ir is not None and ras_ir not in (0, 1):
        raise ValueError("ras_ir must be 0 or 1")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Assignment {assignment_id} not found")

        unit_id = row["unit_id"]
        new_start = start_date if start_date is not None else row["start_date"]
        new_end = end_date if end_date is not None else row["end_date"]

        # Validate dates order
        if new_end is not None:
            if _parse_date(new_end) < _parse_date(new_start):
                raise ValueError("end_date cannot be before start_date")

        # Check overlap excluding current assignment
        if _check_overlap(conn, unit_id, new_start, new_end, exclude_assignment_id=assignment_id):
            raise ValueError("Updated assignment would overlap with another assignment for this unit")

        fields = []
        params = []
        if start_date is not None:
            fields.append("start_date = ?")
            params.append(start_date)
        if end_date is not None:
            fields.append("end_date = ?")
            params.append(end_date)
        if rent_amount is not None:
            fields.append("rent_amount = ?")
            params.append(rent_amount)
        if ras_ir is not None:
            fields.append("ras_ir = ?")
            params.append(ras_ir)

        if not fields:
            return

        params.append(assignment_id)
        cur.execute(f"UPDATE assignments SET {', '.join(fields)} WHERE id = ?", tuple(params))
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"Assignment {assignment_id} not found")
    finally:
        conn.close()


def delete_assignment(assignment_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        raise ValueError(f"Assignment {assignment_id} not found")
    conn.close()
