from database import get_connection
from datetime import datetime


def list_receipt_logs_with_names():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT rl.uid, rl.receipt_id, rl.assignment_id, u.reference AS unit_reference,
               rl.owner_id, ow.name AS owner_name, rl.client_id, c.name AS client_name,
               rl.receipt_no, rl.period, rl.issue_date, rl.amount
        FROM receipt_log rl
        JOIN assignments a ON rl.assignment_id = a.id
        JOIN units u ON a.unit_id = u.id
        JOIN owners ow ON rl.owner_id = ow.id
        JOIN clients c ON rl.client_id = c.id
        ORDER BY rl.uid
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def _month_parity(period):
    try:
        dt = datetime.strptime(period, "%Y-%m-%d")
    except Exception:
        raise ValueError("period must be YYYY-MM-DD date string")
    return "odd" if dt.month % 2 == 1 else "even"


def compute_receipt_split(assignment_id, period, total_amount):
    """Compute per-owner split for a potential receipt without writing to DB.

    Returns list of entries: {owner_id, owner_name, share_percent, amount}
    """
    if total_amount is None:
        raise ValueError("total_amount is required")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, unit_id, client_id FROM assignments WHERE id = ?", (assignment_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Assignment {assignment_id} not found")
        unit_id = row["unit_id"]

        cur.execute("SELECT * FROM ownerships WHERE unit_id = ?", (unit_id,))
        ownerships = cur.fetchall()
        if not ownerships:
            raise ValueError("No ownerships defined for unit; cannot split receipt")

        parity = _month_parity(period)
        applicable = []
        for o in ownerships:
            if o["alternate"] == 0:
                applicable.append(o)
            else:
                if o["odd_even"] == parity:
                    applicable.append(o)

        if not applicable:
            raise ValueError("No ownership applies for the given period")

        entries = []
        total_assigned = 0.0
        for o in applicable:
            amount = float(total_amount) * float(o["share_percent"]) / 100.0
            amount = round(amount, 2)
            total_assigned += amount
            entries.append({
                'owner_id': o['owner_id'],
                'share_percent': float(o['share_percent']),
                'amount': amount,
            })

        remainder = round(float(total_amount) - total_assigned, 2)
        if remainder != 0 and entries:
            entries[0]['amount'] = round(entries[0]['amount'] + remainder, 2)

        # fetch owner names
        owner_ids = tuple({e['owner_id'] for e in entries})
        if owner_ids:
            placeholders = ','.join('?' for _ in owner_ids)
            cur.execute(f"SELECT id, name FROM owners WHERE id IN ({placeholders})", owner_ids)
            names = {r[0]: r[1] for r in cur.fetchall()}
            for e in entries:
                e['owner_name'] = names.get(e['owner_id'], '')

        return entries
    finally:
        conn.close()


def create_receipt(assignment_id, period, issue_date, total_amount, base_label=None):
    if total_amount is None:
        raise ValueError("total_amount is required")

    conn = get_connection()
    try:
        cur = conn.cursor()
        # Validate assignment and fetch unit_id, client_id
        cur.execute("SELECT id, unit_id, client_id FROM assignments WHERE id = ?", (assignment_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Assignment {assignment_id} not found")
        unit_id = row["unit_id"]
        client_id = row["client_id"]

        # Determine receipt_no (per assignment)
        cur.execute("SELECT MAX(receipt_no) as mx FROM receipt_log WHERE assignment_id = ?", (assignment_id,))
        mx = cur.fetchone()[0]
        next_no = (mx or 0) + 1

        # Create receipts entry
        cur.execute("INSERT INTO receipts (assignment_id, base_label) VALUES (?, ?)", (assignment_id, base_label))
        receipt_id = cur.lastrowid

        # Fetch ownerships for the unit
        cur.execute("SELECT * FROM ownerships WHERE unit_id = ?", (unit_id,))
        ownerships = cur.fetchall()
        if not ownerships:
            raise ValueError("No ownerships defined for unit; cannot split receipt")

        parity = _month_parity(period)
        applicable = []
        for o in ownerships:
            if o["alternate"] == 0:
                applicable.append(o)
            else:
                if o["odd_even"] == parity:
                    applicable.append(o)

        if not applicable:
            raise ValueError("No ownership applies for the given period")

        # Create receipt_log entries per owner
        total_assigned = 0.0
        entries = []
        for o in applicable:
            amount = float(total_amount) * float(o["share_percent"]) / 100.0
            amount = round(amount, 2)
            total_assigned += amount
            entries.append((receipt_id, assignment_id, o["owner_id"], client_id, next_no, period, issue_date, amount))

        # Adjust for rounding difference by adding remainder to the first owner
        remainder = round(float(total_amount) - total_assigned, 2)
        if remainder != 0 and entries:
            e = list(entries[0])
            e[-1] = round(e[-1] + remainder, 2)
            entries[0] = tuple(e)

        # Insert all entries
        for ent in entries:
            cur.execute(
                "INSERT INTO receipt_log (receipt_id, assignment_id, owner_id, client_id, receipt_no, period, issue_date, amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ent,
            )

        conn.commit()
        return receipt_id
    finally:
        conn.close()


# CSV/Report generation for receipts/payments
from services.taxes_service import write_csv_file


def generate_receipts_report(year, csv_format='detailed', owner_id=None):
    """Generate receipts/payments report for a year.

    csv_format: 'detailed' (one line per receipt_log with payments),
                'by-owner' (aggregation per owner),
                'minimal' (owner,total_received)
    owner_id: optional owner filter

    Returns: (headers, rows)
    """
    conn = get_connection()
    cur = conn.cursor()

    if csv_format == 'detailed':
        headers = [
            'uid', 'receipt_id', 'assignment_id', 'unit_reference', 'owner_id', 'owner_name',
            'client_id', 'client_name', 'receipt_no', 'period', 'issue_date', 'amount', 'amount_received', 'balance'
        ]
        q = """
        SELECT rl.uid, rl.receipt_id, rl.assignment_id, u.reference AS unit_reference,
               rl.owner_id, ow.name AS owner_name, rl.client_id, c.name AS client_name,
               rl.receipt_no, rl.period, rl.issue_date, rl.amount, COALESCE(SUM(p.amount_received), 0.0) as amount_received
        FROM receipt_log rl
        JOIN assignments a ON rl.assignment_id = a.id
        JOIN units u ON a.unit_id = u.id
        JOIN owners ow ON rl.owner_id = ow.id
        JOIN clients c ON rl.client_id = c.id
        LEFT JOIN payments p ON p.receipt_log_uid = rl.uid
        WHERE substr(rl.period,1,4) = ?
        """
        params = [str(year)]
        if owner_id is not None:
            q += " AND rl.owner_id = ?"
            params.append(owner_id)
        q += " GROUP BY rl.uid ORDER BY rl.uid"
        cur.execute(q, tuple(params))
        rows = []
        for uid, receipt_id, aid, ref, oid, oname, cid, cname, rno, period, issue_date, amount, amt_recv in cur.fetchall():
            balance = round(amount - amt_recv, 2)
            rows.append({
                'uid': uid,
                'receipt_id': receipt_id,
                'assignment_id': aid,
                'unit_reference': ref,
                'owner_id': oid,
                'owner_name': oname,
                'client_id': cid,
                'client_name': cname,
                'receipt_no': rno,
                'period': period,
                'issue_date': issue_date,
                'amount': f"{amount:.2f}",
                'amount_received': f"{amt_recv:.2f}",
                'balance': f"{balance:.2f}",
            })
        conn.close()
        return headers, rows

    if csv_format == 'by-owner' or csv_format == 'minimal':
        # aggregate per owner
        headers = ['owner_id', 'owner_name', 'total_nominal', 'total_received', 'outstanding'] if csv_format == 'by-owner' else ['owner_id', 'owner_name', 'total_received']
        q = """
        SELECT rl.owner_id, ow.name as owner_name, COALESCE(SUM(rl.amount),0.0) as total_nominal, COALESCE(SUM(p.amount_received),0.0) as total_received
        FROM receipt_log rl
        JOIN owners ow ON rl.owner_id = ow.id
        LEFT JOIN payments p ON p.receipt_log_uid = rl.uid
        WHERE substr(rl.period,1,4) = ?
        GROUP BY rl.owner_id
        """
        params = [str(year)]
        if owner_id is not None:
            q = q.replace("GROUP BY rl.owner_id", "AND rl.owner_id = ? GROUP BY rl.owner_id")
            params.append(owner_id)
        cur.execute(q, tuple(params))
        rows = []
        for oid, oname, total_nom, total_recv in cur.fetchall():
            if csv_format == 'by-owner':
                outst = round(total_nom - total_recv, 2)
                rows.append({
                    'owner_id': oid,
                    'owner_name': oname,
                    'total_nominal': f"{total_nom:.2f}",
                    'total_received': f"{total_recv:.2f}",
                    'outstanding': f"{outst:.2f}",
                })
            else:
                rows.append({
                    'owner_id': oid,
                    'owner_name': oname,
                    'total_received': f"{total_recv:.2f}",
                })
        conn.close()
        return headers, rows

    conn.close()
    raise ValueError("Unknown csv_format")