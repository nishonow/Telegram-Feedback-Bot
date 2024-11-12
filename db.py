import sqlite3

conn = sqlite3.connect("messages.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_messages (
    message_id INTEGER PRIMARY KEY,
    user_id INTEGER
)
""")

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT NOT NULL,
    name TEXT NOT NULL,
    username TEXT
)
''')

conn.commit()


def add_user(telegram_id, name, username=None):
    cursor.execute('INSERT INTO users (telegram_id, name, username) VALUES (?, ?, ?)',
                   (telegram_id, name, username))
    conn.commit()

def user_exists(telegram_id):
    cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
    return cursor.fetchone() is not None

def count_users():
    cursor.execute("SELECT COUNT(*) FROM users")
    result = cursor.fetchone()
    return result[0] if result else 0

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
