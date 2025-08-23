import sqlite3

# Path to your SQLite database
DB_PATH = 'instance/workorder.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE workorders ADD COLUMN owner_name VARCHAR(200);")
    print("Column 'owner_name' added successfully.")
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e) or 'already exists' in str(e):
        print("Column 'owner_name' already exists.")
    else:
        print(f"Error: {e}")
finally:
    conn.commit()
    conn.close()
