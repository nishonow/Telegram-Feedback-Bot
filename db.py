import sqlite3

conn = sqlite3.connect("messages.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_messages (
    message_id INTEGER PRIMARY KEY,
    user_id INTEGER
)
""")
conn.commit()


def save_user_message(message_id, user_id):
    cursor.execute("INSERT OR IGNORE INTO user_messages (message_id, user_id) VALUES (?, ?)", (message_id, user_id))
    conn.commit()


def get_user_id(message_id):
    cursor.execute("SELECT user_id FROM user_messages WHERE message_id = ?", (message_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def clear_user_messages():
    cursor.execute("DELETE FROM user_messages")
    conn.commit()


def close_db():
    conn.close()
