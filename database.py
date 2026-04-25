import sqlite3

def init_db():
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT,
        sender TEXT,
        receiver TEXT,
        time TEXT,
        encrypted TEXT,
        priority TEXT,
        mode TEXT,
        signal TEXT,
        emergency INTEGER
    )
    """)

    conn.commit()
    conn.close()

def save_message(msg):
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        msg["id"],
        msg["sender"],
        msg["receiver"],
        msg["time"],
        msg["encrypted"],
        msg["priority"],
        msg["mode"],
        msg["signal"],
        int(msg["emergency"])
    ))

    conn.commit()
    conn.close()

def get_messages_for_device(device):
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()

    c.execute("""
    SELECT * FROM messages
    WHERE receiver = ? OR sender = ? OR receiver = 'ALL'
    ORDER BY time ASC
    """, (device, device))

    rows = c.fetchall()
    conn.close()

    return [{
        "id": r[0],
        "sender": r[1],
        "receiver": r[2],
        "time": r[3],
        "encrypted": r[4],
        "priority": r[5],
        "mode": r[6],
        "signal": r[7],
        "emergency": bool(r[8])
    } for r in rows]