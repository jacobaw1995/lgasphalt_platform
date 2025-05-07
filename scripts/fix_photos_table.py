import sqlite3

def fix_photos_table():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Check if photos table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photos';")
    if cursor.fetchone():
        # Rename existing photos table
        cursor.execute('ALTER TABLE photos RENAME TO photos_old')

        # Create new photos table with correct schema
        cursor.execute('''
            CREATE TABLE photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                filename TEXT NOT NULL,
                description TEXT,
                upload_date TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # Migrate data from old table to new table
        cursor.execute('''
            INSERT INTO photos (id, project_id, filename, description, upload_date)
            SELECT id, project_id, filename, description, upload_date
            FROM photos_old
            WHERE filename IS NOT NULL
        ''')

        # Drop old table
        cursor.execute('DROP TABLE photos_old')

        print("Photos table schema fixed and data migrated.")
    else:
        print("Photos table does not exist. Creating it...")
        cursor.execute('''
            CREATE TABLE photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                filename TEXT NOT NULL,
                description TEXT,
                upload_date TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

    conn.commit()
    conn.close()
    print("Photos table schema updated successfully.")

if __name__ == '__main__':
    fix_photos_table()