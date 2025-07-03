import sqlite3
from datetime import datetime
import bcrypt
import re

def init_db():
    """Initialize SQLite database with users, updates, and edit permissions tables."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  password_hash TEXT, 
                  role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS updates 
                 (update_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER, 
                  week INTEGER, 
                  content TEXT, 
                  timestamp TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS edit_permissions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  allow_edits INTEGER DEFAULT 0)''')
    c.execute("INSERT OR IGNORE INTO edit_permissions (allow_edits) VALUES (0)")
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def add_user(username, password, role):
    """Add a new user to the database with validation."""
    if role == "Student" and not (re.match(r'^AIE230(0[1-9]|[1-9][0-9]|1[0-5][0-7])$', username) and len(password) >= 8):
        return False
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  (username, hash_password(password), role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    """Retrieve user details by username."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("SELECT user_id, username, password_hash, role FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_all_users():
    """Retrieve all users with their details."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("SELECT user_id, username, role FROM users ORDER BY username")
    users = c.fetchall()
    conn.close()
    return users

def update_user(username, new_username, new_password):
    """Update username and/or password for a user."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    password_hash = hash_password(new_password) if new_password else get_user(username)[2]
    c.execute("UPDATE users SET username = ?, password_hash = ? WHERE username = ?",
              (new_username, password_hash, username))
    conn.commit()
    conn.close()

def reset_password(username, new_password):
    """Reset a user's password."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hash_password(new_password), username))
    conn.commit()
    conn.close()

def delete_user(username):
    """Delete a user and their updates from the database."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    user_id = get_user_id(username)
    if user_id:
        c.execute("DELETE FROM updates WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
    conn.close()

def get_user_id(username):
    """Retrieve user_id by username."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    user_id = c.fetchone()
    conn.close()
    return user_id[0] if user_id else None

def add_update(user_id, week, content):
    """Add a new update for a user."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO updates (user_id, week, content, timestamp) VALUES (?, ?, ?, ?)",
              (user_id, week, content, timestamp))
    conn.commit()
    conn.close()

def get_user_updates(user_id):
    """Retrieve all updates for a specific user with week locking."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("SELECT week, content, timestamp FROM updates WHERE user_id = ? ORDER BY week", (user_id,))
    updates = c.fetchall()
    conn.close()
    return updates

def get_all_updates():
    """Retrieve all updates joined with usernames."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("SELECT u.username, up.week, up.content, up.timestamp FROM updates up JOIN users u ON up.user_id = u.user_id ORDER BY u.username, up.week")
    updates = c.fetchall()
    conn.close()
    return updates

def get_all_usernames():
    """Retrieve all usernames from the users table."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE role = 'Student' ORDER BY username")
    usernames = [row[0] for row in c.fetchall()]
    conn.close()
    return usernames

def get_edit_permission():
    """Retrieve the current edit permission status."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("SELECT allow_edits FROM edit_permissions LIMIT 1")
    allow_edits = c.fetchone()[0]
    conn.close()
    return allow_edits

def set_edit_permission(allow_edits):
    """Set the edit permission status."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("UPDATE edit_permissions SET allow_edits = ?", (allow_edits,))
    conn.commit()
    conn.close()

def clear_week_data_for_user(user_id, week):
    """Clear updates for a specific week for a user."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("DELETE FROM updates WHERE user_id = ? AND week = ?", (user_id, week))
    conn.commit()
    conn.close()

def clear_user_data(user_id):
    """Clear all updates for a specific user."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("DELETE FROM updates WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def clear_all_data():
    """Clear all updates for all users."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("DELETE FROM updates")
    conn.commit()
    conn.close()

def clear_week_data_for_all(week):
    """Clear updates for a specific week across all users."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    c.execute("DELETE FROM updates WHERE week = ?", (week,))
    conn.commit()
    conn.close()

def update_update(user_id, week, new_content):
    """Update an existing update for a user."""
    conn = sqlite3.connect('progress_portal.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE updates SET content = ?, timestamp = ? WHERE user_id = ? AND week = ?",
              (new_content, timestamp, user_id, week))
    conn.commit()
    conn.close()