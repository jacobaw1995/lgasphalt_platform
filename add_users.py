import sqlite3
from flask_bcrypt import Bcrypt

# Initialize Bcrypt
bcrypt = Bcrypt()

def add_admin_users():
    # Connect to crm.db
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Define three admin users
    users = [
        ('admin1', 'password1', 'admin'),
        ('admin2', 'password2', 'admin'),
        ('admin3', 'password3', 'admin')
    ]

    # Insert users with hashed passwords
    for username, password, role in users:
        # Check if username already exists
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            print(f"User {username} already exists, skipping.")
            continue
        
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Insert user with hashed password
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', (username, hashed_password, role))
        print(f"Added user {username}.")

    # Commit and close
    conn.commit()
    conn.close()
    print("All admin users added successfully.")

if __name__ == '__main__':
    add_admin_users()