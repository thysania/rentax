from database import get_connection


def create_client(name, client_type, phone=None, legal_id=None):
    if client_type not in ("PP", "PM"):
        raise ValueError('client_type must be "PP" or "PM"')

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO clients (name, phone, legal_id, client_type)
        VALUES (?, ?, ?, ?)
        """,
        (name, phone, legal_id, client_type),
    )
    conn.commit()
    conn.close()


def list_clients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients ORDER BY id")
    clients = cur.fetchall()
    conn.close()
    return clients


def get_client(client_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cur.fetchone()
    conn.close()
    return client


def update_client(client_id, name=None, client_type=None, phone=None, legal_id=None):
    if client_type is not None and client_type not in ("PP", "PM"):
        raise ValueError('client_type must be "PP" or "PM"')

    fields = []
    params = []
    if name is not None:
        fields.append("name = ?")
        params.append(name)
    if client_type is not None:
        fields.append("client_type = ?")
        params.append(client_type)
    if phone is not None:
        fields.append("phone = ?")
        params.append(phone)
    if legal_id is not None:
        fields.append("legal_id = ?")
        params.append(legal_id)

    if not fields:
        return

    params.append(client_id)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE clients SET {', '.join(fields)} WHERE id = ?", tuple(params))
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        raise ValueError(f"Client {client_id} not found")
    conn.close()


def delete_client(client_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        raise ValueError(f"Client {client_id} not found")
    conn.close()
