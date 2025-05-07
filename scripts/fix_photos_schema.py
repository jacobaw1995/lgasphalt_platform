import sqlite3

def fix_photos_table():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    # Check if photos table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photos';")
    if not cursor.fetchone():
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
    else:
        # Check if filename column exists
        cursor.execute("PRAGMA table_info(photos);")
        columns = [col[1] for col in cursor.fetchall()]
        if 'filename' not in columns:
            print("Adding filename column to photos table...")
            cursor.execute('ALTER TABLE photos ADD COLUMN filename TEXT NOT NULL DEFAULT ""')
        if 'description' not in columns:
            print("Adding description column to photos table...")
            cursor.execute('ALTER TABLE photos ADD COLUMN description TEXT')
        if 'upload_date' not in columns:
            print("Adding upload_date column to photos table...")
            cursor.execute('ALTER TABLE photos ADD COLUMN upload_date TEXT')

    conn.commit()
    conn.close()
    print("Photos table schema updated successfully.")

if __name__ == '__main__':
    fix_photos_table()