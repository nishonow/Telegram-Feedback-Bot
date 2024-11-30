import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

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

cursor.execute('''
CREATE TABLE IF NOT EXISTS super_admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT NOT NULL
)
''')

conn.commit()

def add_secret(telegram_id):
    cursor.execute('INSERT INTO super_admins (telegram_id) VALUES (?)',
                   (telegram_id,))
    conn.commit()


def get_admins():
    cursor.execute('''
        SELECT a.telegram_id, u.name, u.username
        FROM admins a
        LEFT JOIN users u ON a.telegram_id = u.telegram_id
    ''')
    admins = cursor.fetchall()
    return [{"telegram_id": row[0], "name": row[1], "username": row[2]} for row in admins]

def get_super_admins():
    cursor.execute('''
        SELECT sa.telegram_id, u.name, u.username
        FROM super_admins sa
        LEFT JOIN users u ON sa.telegram_id = u.telegram_id
    ''')
    super_admins = cursor.fetchall()
    return [{"telegram_id": row[0], "name": row[1], "username": row[2]} for row in super_admins]

def add_user(telegram_id, name, username=None):
    cursor.execute('INSERT INTO users (telegram_id, name, username) VALUES (?, ?, ?)',
                   (telegram_id, name, username))
    conn.commit()

def get_user_info(telegram_id):
    cursor.execute("SELECT name, username FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    return result if result else None


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

def count_super_admins():
    cursor.execute("SELECT COUNT(*) FROM super_admins")
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

def add_super_admin(telegram_id):
    cursor.execute('INSERT INTO super_admins (telegram_id) VALUES (?)',
                   (telegram_id,))
    conn.commit()

def admin_super_exists(telegram_id):
    cursor.execute("SELECT 1 FROM super_admins WHERE telegram_id = ?", (telegram_id,))
    return cursor.fetchone() is not None

def delete_super_admin(telegram_id):
    cursor.execute("DELETE FROM super_admins WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    return cursor.rowcount > 0


def clear_admins(telegram_id):
    cursor.execute("DELETE FROM admins WHERE telegram_id != ?", (telegram_id,))
    conn.commit()

def clear_super_admins(telegram_id):
    cursor.execute("DELETE FROM super_admins WHERE telegram_id != ?", (telegram_id,))
    conn.commit()


def get_all_admins():
    cursor.execute("SELECT telegram_id FROM admins")
    admin_ids = cursor.fetchall()
    return [int(admin_id[0]) for admin_id in admin_ids]  # Ensure all IDs are integers

def get_all_super_admins():
    cursor.execute("SELECT telegram_id FROM super_admins")
    admin_ids = cursor.fetchall()
    return [int(admin_id[0]) for admin_id in admin_ids]

def get_all_user_ids():
    cursor.execute("SELECT telegram_id FROM users")  # Query to select all telegram_ids
    user_ids = cursor.fetchall()  # Fetch all results
    return [user_id[0] for user_id in user_ids]




def close_db():
    conn.close()
