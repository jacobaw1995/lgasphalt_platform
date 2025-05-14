import sqlite3

def update_equipment_table():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    try:
        # Step 1: Create a new table with the desired schema
        cursor.execute('''
            CREATE TABLE equipment_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                maintenance_schedule TEXT,
                status TEXT NOT NULL,
                last_used TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # Step 2: Copy data from the old table to the new table
        cursor.execute('''
            INSERT INTO equipment_new (id, name, type, maintenance_schedule, status)
            SELECT id, name, type, maintenance_schedule, status
            FROM equipment
        ''')

        # Step 3: Drop the old table
        cursor.execute('DROP TABLE equipment')

        # Step 4: Rename the new table to the original name
        cursor.execute('ALTER TABLE equipment_new RENAME TO equipment')

        # Step 5: Update any NULL values for type and status to meet NOT NULL constraints
        cursor.execute("UPDATE equipment SET type = 'Unknown' WHERE type IS NULL")
        cursor.execute("UPDATE equipment SET status = 'Unknown' WHERE status IS NULL")

        conn.commit()
        print("Updated equipment table schema successfully.")
    except Exception as e:
        print(f"Error updating equipment table: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    update_equipment_table()