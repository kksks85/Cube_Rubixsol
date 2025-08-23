#!/usr/bin/env python3
"""
Simple Database Migration for Servicing Fields
"""

import os
import sys
import sqlite3
from datetime import datetime

def migrate_database():
    """Add servicing fields to the product table."""
    
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'workorder.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current table schema
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print("Current products table columns:")
        for col in columns:
            print(f"  - {col}")
        
        # Add last_serviced column if it doesn't exist
        if 'last_serviced' not in columns:
            print("\nAdding 'last_serviced' column...")
            cursor.execute("ALTER TABLE products ADD COLUMN last_serviced DATE")
            print("✓ Added 'last_serviced' column successfully")
        else:
            print("\n'last_serviced' column already exists")
        
        # Add next_service_due column if it doesn't exist  
        if 'next_service_due' not in columns:
            print("Adding 'next_service_due' column...")
            cursor.execute("ALTER TABLE products ADD COLUMN next_service_due DATE")
            print("✓ Added 'next_service_due' column successfully")
        else:
            print("'next_service_due' column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(products)")
        updated_columns = [row[1] for row in cursor.fetchall()]
        
        print(f"\nUpdated products table now has {len(updated_columns)} columns:")
        for col in updated_columns:
            print(f"  - {col}")
        
        # Count products
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"\nCurrent database contains {product_count} products")
        
        conn.close()
        
        print("\n✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == '__main__':
    print("CUBE - PRO: Database Migration for Servicing History")
    print("=" * 55)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if migrate_database():
        print("\n🎉 Migration completed successfully!")
        print("\nThe following features are now available:")
        print("  • Track last serviced date for each UAV")
        print("  • Automatic calculation of next service due date (90 days)")
        print("  • Service status indicators in the UI")
        print("  • Visual alerts for overdue maintenance")
        print("\nYou can now restart your Flask app and use the servicing features!")
    else:
        print("\n❌ Migration failed.")
        sys.exit(1)
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
