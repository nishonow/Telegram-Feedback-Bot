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

cursor.execute('''
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT NOT NULL
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

def count_admins():
    cursor.execute("SELECT COUNT(*) FROM admins")
    result = cursor.fetchone()
    return result[0] if result else 0

def add_admin(telegram_id):
    cursor.execute('INSERT INTO admins (telegram_id) VALUES (?)',
                   (telegram_id,))
    conn.commit()

def admin_exists(telegram_id):
    cursor.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,))
    return cursor.fetchone() is not None

def delete_admin(telegram_id):
    cursor.execute("DELETE FROM admins WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    return cursor.rowcount > 0  # Returns True if an admin was deleted, False otherwise


def clear_admins():
    cursor.execute("DELETE FROM admins WHERE id != 1")
    conn.commit()

def get_all_admins():
    cursor.execute("SELECT telegram_id FROM admins")
    admin_ids = cursor.fetchall()
    return [int(admin_id[0]) for admin_id in admin_ids]  # Ensure all IDs are integers

def get_all_user_ids():
    cursor.execute("SELECT telegram_id FROM users")  # Query to select all telegram_ids
    user_ids = cursor.fetchall()  # Fetch all results
    return [user_id[0] for user_id in user_ids]



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
