#!/usr/bin/env python3
"""
Force recreate assignment groups tables
"""

import os
import sqlite3

def force_recreate_assignment_tables():
    """Forcefully recreate assignment group tables"""
    db_path = os.path.join('instance', 'workorder.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        print(f"Working with database: {db_path}")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop existing tables
        print("Dropping existing assignment tables...")
        cursor.execute("DROP TABLE IF EXISTS assignment_group_members")
        cursor.execute("DROP TABLE IF EXISTS assignment_groups")
        
        # Create assignment_groups table with correct schema
        print("Creating assignment_groups table...")
        cursor.execute("""
        CREATE TABLE assignment_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(128) NOT NULL,
            code VARCHAR(32) NOT NULL UNIQUE,
            description TEXT,
            department VARCHAR(64),
            priority_level VARCHAR(20) DEFAULT 'standard',
            auto_assign BOOLEAN DEFAULT 0,
            round_robin BOOLEAN DEFAULT 0,
            notification_enabled BOOLEAN DEFAULT 1,
            is_active BOOLEAN DEFAULT 1,
            work_order_types TEXT,
            priority_filter TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            created_by_id INTEGER,
            FOREIGN KEY (created_by_id) REFERENCES users (id)
        )
        """)
        
        # Create assignment_group_members table
        print("Creating assignment_group_members table...")
        cursor.execute("""
        CREATE TABLE assignment_group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            is_leader BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            joined_at DATETIME,
            FOREIGN KEY (group_id) REFERENCES assignment_groups (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE (group_id, user_id)
        )
        """)
        
        # Commit changes
        conn.commit()
        
        # Verify the schema
        print("\nVerifying assignment_groups schema:")
        cursor.execute("PRAGMA table_info(assignment_groups)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        print("\nVerifying assignment_group_members schema:")
        cursor.execute("PRAGMA table_info(assignment_group_members)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
        print("\n✅ Assignment tables recreated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    force_recreate_assignment_tables()
