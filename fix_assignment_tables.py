#!/usr/bin/env python3
"""
Fix assignment groups database schema
"""

import os
import sys
import sqlite3

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import AssignmentGroup, AssignmentGroupMember

def fix_assignment_tables():
    """Drop and recreate assignment group tables with correct schema"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Fixing assignment group tables schema...")
            
            # Get the database file path
            db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            
            if not db_path:
                print("❌ Could not determine database path")
                return False
            
            print(f"Database path: {db_path}")
            
            # Connect directly to SQLite to drop tables
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Drop existing tables if they exist
            print("Dropping existing assignment tables...")
            cursor.execute("DROP TABLE IF EXISTS assignment_group_members")
            cursor.execute("DROP TABLE IF EXISTS assignment_groups")
            conn.commit()
            conn.close()
            
            print("Creating new tables with correct schema...")
            
            # Create the tables with correct schema
            db.create_all()
            
            print("✅ Assignment group tables fixed successfully!")
            print("Tables recreated:")
            print("  - assignment_groups (with all columns)")
            print("  - assignment_group_members")
            
            # Verify the schema
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(assignment_groups)")
            columns = cursor.fetchall()
            print("\nVerified columns in assignment_groups:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            conn.close()
            
        except Exception as e:
            print(f"❌ Error fixing tables: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    fix_assignment_tables()
