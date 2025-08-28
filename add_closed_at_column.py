#!/usr/bin/env python3
"""
Migration script to add closed_at column to uav_service_incidents table
"""

import sqlite3
import os
from datetime import datetime

def add_closed_at_column():
    """Add closed_at column to uav_service_incidents table"""
    
    # Database path
    db_path = os.path.join('instance', 'workorder.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(uav_service_incidents)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'closed_at' in columns:
            print("Column 'closed_at' already exists in uav_service_incidents table")
            conn.close()
            return True
        
        # Add the closed_at column
        print("Adding 'closed_at' column to uav_service_incidents table...")
        cursor.execute("""
            ALTER TABLE uav_service_incidents 
            ADD COLUMN closed_at DATETIME NULL
        """)
        
        # Commit the changes
        conn.commit()
        print("Successfully added 'closed_at' column to uav_service_incidents table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(uav_service_incidents)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'closed_at' in columns:
            print("✓ Column 'closed_at' verified in table structure")
        else:
            print("✗ Failed to verify 'closed_at' column")
            return False
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.close()
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("UAV Service Incidents Database Migration")
    print("=" * 45)
    print(f"Migration started at: {datetime.now()}")
    print()
    
    success = add_closed_at_column()
    
    print()
    if success:
        print("✓ Migration completed successfully!")
        print("The application should now work with the new closed_at column.")
    else:
        print("✗ Migration failed!")
        print("Please check the error messages above and try again.")
    
    print(f"Migration ended at: {datetime.now()}")
