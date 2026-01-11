from database import get_connection


VALID_ODD_EVEN = ("odd", "even")


def _ensure_unit_and_owner_exist(conn, unit_id, owner_id):
    cur = conn.cursor()
    cur.execute("SELECT id FROM units WHERE id = ?", (unit_id,))
    if not cur.fetchone():
        raise ValueError(f"Unit {unit_id} not found")
    cur.execute("SELECT id FROM owners WHERE id = ?", (owner_id,))
    if not cur.fetchone():
        raise ValueError(f"Owner {owner_id} not found")


def _get_totals_for_unit(conn, unit_id, exclude_id=None):
    cur = conn.cursor()
    params = (unit_id,)
    cur.execute("SELECT share_percent, alternate, odd_even FROM ownerships WHERE unit_id = ?" + (" AND id != ?" if exclude_id else ""), params + ((exclude_id,) if exclude_id else ()))
    rows = cur.fetchall()

    non_alt = 0.0
    odd = 0.0
    even = 0.0
    for r in rows:
        sp = float(r[0])
        if r[1] == 0:
            non_alt += sp
        else:
            if r[2] == 'odd':
                odd += sp
            elif r[2] == 'even':
                even += sp
    odd_total = non_alt + odd
    even_total = non_alt + even
    return non_alt, odd, even, odd_total, even_total


def _validate_totals(non_alt, odd, even, odd_total, even_total):
    # Each period must have >0 and <=100
    if odd_total <= 0:
        raise ValueError("Odd-month ownership total must be greater than 0%")
    if even_total <= 0:
        raise ValueError("Even-month ownership total must be greater than 0%")
    if odd_total > 100:
        raise ValueError("Odd-month ownership total cannot exceed 100%")
    if even_total > 100:
        raise ValueError("Even-month ownership total cannot exceed 100%")


def create_ownership(unit_id, owner_id, share_percent, alternate=0, odd_even=None):
    if share_percent <= 0 or share_percent > 100:
        raise ValueError("share_percent must be > 0 and <= 100")
    if alternate not in (0, 1):
        raise ValueError("alternate must be 0 or 1")
    if alternate == 1 and odd_even not in VALID_ODD_EVEN:
        raise ValueError("When alternate=1, odd_even must be 'odd' or 'even'")
    if alternate == 0 and odd_even is not None:
        raise ValueError("When alternate=0, odd_even must be None")

    conn = get_connection()
    try:
        _ensure_unit_and_owner_exist(conn, unit_id, owner_id)
        non_alt, odd, even, odd_total, even_total = _get_totals_for_unit(conn, unit_id)

        # compute prospective totals
        if alternate == 0:
            non_alt += float(share_percent)
        else:
            if odd_even == 'odd':
                odd += float(share_percent)
            else:
                even += float(share_percent)
        odd_total = non_alt + odd
        even_total = non_alt + even

        _validate_totals(non_alt, odd, even, odd_total, even_total)

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ownerships (unit_id, owner_id, share_percent, alternate, odd_even) VALUES (?, ?, ?, ?, ?)",
            (unit_id, owner_id, share_percent, alternate, odd_even),
        )
        conn.commit()
    finally:
        conn.close()


def list_ownerships(unit_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if unit_id:
        cur.execute("SELECT * FROM ownerships WHERE unit_id = ? ORDER BY id", (unit_id,))
    else:
        cur.execute("SELECT * FROM ownerships ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows


def list_ownerships_with_names(unit_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if unit_id:
        cur.execute(
            """
            SELECT o.id, o.unit_id, u.reference AS unit_reference, o.owner_id, ow.name AS owner_name,
                   o.share_percent, o.alternate, o.odd_even
            FROM ownerships o
            JOIN units u ON o.unit_id = u.id
            JOIN owners ow ON o.owner_id = ow.id
            WHERE o.unit_id = ?
            ORDER BY o.id
            """,
            (unit_id,),
        )
    else:
        cur.execute(
            """
            SELECT o.id, o.unit_id, u.reference AS unit_reference, o.owner_id, ow.name AS owner_name,
                   o.share_percent, o.alternate, o.odd_even
            FROM ownerships o
            JOIN units u ON o.unit_id = u.id
            JOIN owners ow ON o.owner_id = ow.id
            ORDER BY o.id
            """
        )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_ownership(ownership_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ownerships WHERE id = ?", (ownership_id,))
    r = cur.fetchone()
    conn.close()
    return r


def update_ownership(ownership_id, share_percent=None, alternate=None, odd_even=None):
    if share_percent is not None and (share_percent <= 0 or share_percent > 100):
        raise ValueError("share_percent must be > 0 and <= 100")
    if alternate is not None and alternate not in (0, 1):
        raise ValueError("alternate must be 0 or 1")
    if alternate == 1 and odd_even not in VALID_ODD_EVEN:
        raise ValueError("When alternate=1, odd_even must be 'odd' or 'even'")
    if alternate == 0 and odd_even is not None:
        raise ValueError("When alternate=0, odd_even must be None")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM ownerships WHERE id = ?", (ownership_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Ownership {ownership_id} not found")

        unit_id = row["unit_id"]
        new_share = float(share_percent) if share_percent is not None else float(row["share_percent"])
        new_alt = alternate if alternate is not None else row["alternate"]
        new_odd_even = odd_even if odd_even is not None else row["odd_even"]

        non_alt, odd, even, odd_total, even_total = _get_totals_for_unit(conn, unit_id, exclude_id=ownership_id)

        if new_alt == 0:
            non_alt += new_share
        else:
            if new_odd_even == 'odd':
                odd += new_share
            else:
                even += new_share

        odd_total = non_alt + odd
        even_total = non_alt + even

        _validate_totals(non_alt, odd, even, odd_total, even_total)

        fields = []
        params = []
        if share_percent is not None:
            fields.append("share_percent = ?")
            params.append(share_percent)
        if alternate is not None:
            fields.append("alternate = ?")
            params.append(alternate)
        if odd_even is not None or (alternate == 0 and odd_even is None):
            # explicit set of odd_even (or clearing it when alternate=0)
            fields.append("odd_even = ?")
            params.append(odd_even)

        if not fields:
            return

        params.append(ownership_id)
        cur.execute(f"UPDATE ownerships SET {', '.join(fields)} WHERE id = ?", tuple(params))
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"Ownership {ownership_id} not found")
    finally:
        conn.close()


def delete_ownership(ownership_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM ownerships WHERE id = ?", (ownership_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Ownership {ownership_id} not found")

        unit_id = row["unit_id"]
        # Compute totals excluding this ownership
        non_alt, odd, even, odd_total, even_total = _get_totals_for_unit(conn, unit_id, exclude_id=ownership_id)

        # After deletion totals must still satisfy >0 and <=100 OR no ownerships at all?
        # If there will be no remaining ownerships at all, that's allowed (vacancy).
        cur.execute("SELECT COUNT(*) FROM ownerships WHERE unit_id = ?", (unit_id,))
        remaining = cur.fetchone()[0]
        if remaining <= 1:
            # deleting the last or only ownership is allowed
            pass
        else:
            _validate_totals(non_alt, odd, even, odd_total, even_total)

        cur.execute("DELETE FROM ownerships WHERE id = ?", (ownership_id,))
        conn.commit()
    finally:
        conn.close()