import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def fix_customers_table():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Add password column (nullable initially)
    cursor.execute('ALTER TABLE customers ADD COLUMN password TEXT')

    # Set default password for existing customers
    default_password = bcrypt.generate_password_hash('default123').decode('utf-8')
    cursor.execute('UPDATE customers SET password = ? WHERE password IS NULL', (default_password,))

    conn.commit()
    conn.close()
    print("Database schema updated: password column added to customers table.")

if __name__ == '__main__':
    fix_customers_table()