#!/usr/bin/env python3
"""
Database Migration Script - Add Serial Number to Products
Adds serial_number column to products table
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import Product
from sqlalchemy import text

def add_serial_number_column():
    """Add serial_number column to products table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM PRAGMA_TABLE_INFO('products') 
                WHERE name = 'serial_number'
            """)).fetchone()
            
            if result.count == 0:
                print("Adding serial_number column to products table...")
                
                # Add the column without UNIQUE constraint (SQLite limitation)
                db.session.execute(text("""
                    ALTER TABLE products 
                    ADD COLUMN serial_number VARCHAR(40)
                """))
                
                # Create unique index for the new column
                db.session.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS ix_products_serial_number_unique 
                    ON products(serial_number) WHERE serial_number IS NOT NULL
                """))
                
                db.session.commit()
                print("✓ Successfully added serial_number column to products table")
                print("✓ Created unique index on serial_number column")
                
                # Verify the column was added
                products_count = Product.query.count()
                print(f"✓ Verified: {products_count} products in database")
                
            else:
                print("✓ serial_number column already exists in products table")
                
        except Exception as e:
            print(f"❌ Error adding serial_number column: {str(e)}")
            db.session.rollback()
            return False
            
        return True

if __name__ == '__main__':
    print("🔄 Running migration: Add serial_number column to products table")
    success = add_serial_number_column()
    
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)
