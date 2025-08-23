import sqlite3

DB_PATH = 'instance/workorder.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE workorders ADD COLUMN address VARCHAR(200);")
    print("Column 'address' added successfully.")
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e) or 'already exists' in str(e):
        print("Column 'address' already exists.")
    else:
        print(f"Error: {e}")
finally:
    conn.commit()
    conn.close()
