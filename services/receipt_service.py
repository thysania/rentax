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