import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def init_db():
    # Connect to (or create) crm.db
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Create users table (for admin users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL  -- e.g., 'admin', 'task_editor', 'finance_manager'
        )
    ''')

    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            address TEXT
            password TEXT NOT NULL

        )
    ''')

    # Create projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            status TEXT,  -- e.g., 'planned', 'in_progress', 'completed'
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')

    # Create tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            assigned_to INTEGER,
            start_date TEXT,
            end_date TEXT,
            status TEXT,
            duration_days INTEGER,
            hours_spent REAL,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
    ''')

    # Create equipment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,  -- e.g., 'paver', 'roller'
            maintenance_schedule TEXT,
            status TEXT  -- e.g., 'available', 'in_use', 'maintenance'
        )
    ''')

    # Create photos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            upload_date TEXT,
            description TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')

    # Create forms table (for estimates, site inspections)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            type TEXT NOT NULL,  -- e.g., 'estimate', 'site_inspection'
            data TEXT,  -- JSON or text for form fields
            created_date TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')

    # Create project_finances table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_finances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            type TEXT NOT NULL,  -- e.g., 'cost', 'revenue'
            category TEXT,  -- e.g., 'materials', 'labor', 'client_payment'
            amount REAL NOT NULL,
            description TEXT,
            date TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database crm.db created successfully with all tables.")

if __name__ == '__main__':
    init_db()