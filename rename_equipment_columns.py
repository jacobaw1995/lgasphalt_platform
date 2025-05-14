import sqlite3

def rename_equipment_columns():
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()

    try:
        # Step 1: Create a new table with the updated schema
        cursor.execute('''
            CREATE TABLE equipment_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                equipment_type TEXT NOT NULL,
                maintenance_schedule_days INTEGER,
                status TEXT NOT NULL,
                last_maintenance_date TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # Step 2: Copy data from the old table to the new table, mapping old column names to new ones
        cursor.execute('''
            INSERT INTO equipment_new (id, project_id, name, equipment_type, maintenance_schedule_days, status, last_maintenance_date)
            SELECT id, project_id, name, type, maintenance_schedule, status, last_used
            FROM equipment
        ''')

        # Step 3: Drop the old table
        cursor.execute('DROP TABLE equipment')

        # Step 4: Rename the new table to the original name
        cursor.execute('ALTER TABLE equipment_new RENAME TO equipment')

        # Step 5: Ensure maintenance_schedule_days is an integer (convert if necessary)
        cursor.execute('UPDATE equipment SET maintenance_schedule_days = CAST(maintenance_schedule_days AS INTEGER) WHERE maintenance_schedule_days IS NOT NULL')

        conn.commit()
        print("Updated equipment table schema with new column names successfully.")
    except Exception as e:
        print(f"Error updating equipment table: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    rename_equipment_columns()