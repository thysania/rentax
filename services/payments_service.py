from database import get_connection
from datetime import datetime


def create_payment(receipt_log_uid, amount_received, received_at=None, note=None):
    if received_at is None:
        received_at = datetime.utcnow().strftime("%Y-%m-%d")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payments (receipt_log_uid, amount_received, received_at, note) VALUES (?, ?, ?, ?)",
        (receipt_log_uid, amount_received, received_at, note),
    )
    conn.commit()
    conn.close()


def get_payments_for_owner_year(owner_id, year):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.* FROM payments p
        JOIN receipt_log rl ON p.receipt_log_uid = rl.uid
        WHERE rl.owner_id = ? AND substr(rl.period,1,4) = ?
        """,
        (owner_id, str(year)),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def sum_received_for_owner_year(owner_id, year):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COALESCE(SUM(p.amount_received), 0.0) FROM payments p
        JOIN receipt_log rl ON p.receipt_log_uid = rl.uid
        WHERE rl.owner_id = ? AND substr(rl.period,1,4) = ?
        """,
        (owner_id, str(year)),
    )
    s = cur.fetchone()[0] or 0.0
    conn.close()
    return float(s)
