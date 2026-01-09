from database import get_connection


def create_owner(name, phone=None, legal_id=None, family_count=0):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO owners (name, phone, legal_id, family_count)
        VALUES (?, ?, ?, ?)
    """, (name, phone, legal_id, family_count))

    conn.commit()
    conn.close()


def list_owners():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM owners ORDER BY id")
    owners = cur.fetchall()

    conn.close()
    return owners