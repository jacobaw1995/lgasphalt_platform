import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def add_admin_user():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    # Insert admin user if not exists
    hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', ('admin', hashed_password, 'admin'))
        conn.commit()
        print("Admin user added or already exists: username=admin, role=admin")
    except sqlite3.Error as e:
        print(f"Error adding admin user: {str(e)}")
    
    conn.close()

if __name__ == '__main__':
    add_admin_user()