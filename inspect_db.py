import sqlite3
import bcrypt
from datetime import datetime

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect('progress_portal.db')

def view_users():
    """Display all users in the database."""
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT user_id, username, role FROM users")
    users = c.fetchall()
    print("\nUsers:")
    if users:
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[2]}")
    else:
        print("No users found.")
    conn.close()

def view_updates():
    """Display all updates with usernames."""
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT u.username, up.week, up.content, up.timestamp FROM updates up JOIN users u ON up.user_id = u.user_id ORDER BY u.username, up.week")
    updates = c.fetchall()
    print("\nUpdates:")
    if updates:
        for update in updates:
            print(f"Username: {update[0]}, Week: {update[1]}, Content: {update[2]}, Timestamp: {update[3]}")
    else:
        print("No updates found.")
    conn.close()

def add_admin_user(username, password):
    """Add an admin user with a hashed password."""
    conn = connect_db()
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  (username, hashed, 'Admin'))
        conn.commit()
        print(f"Admin user '{username}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"Username '{username}' already exists.")
    finally:
        conn.close()

def reset_password(username, new_password):
    """Reset a user's password."""
    conn = connect_db()
    c = conn.cursor()
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    c.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed, username))
    if c.rowcount > 0:
        print(f"Password for '{username}' reset successfully.")
    else:
        print(f"Username '{username}' not found.")
    conn.commit()
    conn.close()

def add_sample_update(user_id, week, content):
    """Add a sample update for a user."""
    conn = connect_db()
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO updates (user_id, week, content, timestamp) VALUES (?, ?, ?, ?)",
              (user_id, week, content, timestamp))
    conn.commit()
    print(f"Sample update added for user_id {user_id}.")
    conn.close()

def main():
    """Main function to interact with the database."""
    print("SQLite Database Inspector for Deep Learning Progress Portal")
    
    while True:
        print("\nOptions:")
        print("1. View all users")
        print("2. View all updates")
        print("3. Add admin user")
        print("4. Reset user password")
        print("5. Add sample update")
        print("6. Exit")
        choice = input("Enter choice (1-6): ")

        if choice == '1':
            view_users()
        elif choice == '2':
            view_updates()
        elif choice == '3':
            username = input("Enter admin username: ")
            password = input("Enter admin password: ")
            add_admin_user(username, password)
        elif choice == '4':
            username = input("Enter username to reset password: ")
            new_password = input("Enter new password: ")
            reset_password(username, new_password)
        elif choice == '5':
            user_id = input("Enter user_id for sample update: ")
            week = input("Enter week number: ")
            content = input("Enter update content: ")
            try:
                add_sample_update(int(user_id), int(week), content)
            except ValueError:
                print("Invalid user_id or week number. Please enter numeric values.")
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()