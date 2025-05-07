import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def add_sample_customer():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    customer_password = bcrypt.generate_password_hash('customer123').decode('utf-8')
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO customers (name, email, phone, address, password)
            VALUES (?, ?, ?, ?, ?)
        ''', ('John Doe', 'john.doe@example.com', '123-456-7890', '123 Main St', customer_password))
        conn.commit()
        print("Sample customer added or already exists.")
    except sqlite3.IntegrityError:
        print("Customer with this email already exists.")
    
    conn.close()

if __name__ == '__main__':
    add_sample_customer()