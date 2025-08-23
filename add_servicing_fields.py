#!/usr/bin/env python3
"""
Database Migration Script: Add Servicing History Fields
=========================================================

This script adds the new servicing history fields to existing Product tables.
Run this script to update your database with the new last_serviced and 
next_service_due columns.

Author: Python Expert
Date: 2025
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Product
from sqlalchemy import text

def add_servicing_fields():
    """Add servicing fields to the Product table if they don't exist."""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if the columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('product')]
            
            print("Current Product table columns:")
            for col in columns:
                print(f"  - {col}")
            
            # Add last_serviced column if it doesn't exist
            if 'last_serviced' not in columns:
                print("\nAdding 'last_serviced' column...")
                db.session.execute(text('ALTER TABLE product ADD COLUMN last_serviced DATE'))
                print("✓ Added 'last_serviced' column successfully")
            else:
                print("\n'last_serviced' column already exists")
            
            # Add next_service_due column if it doesn't exist
            if 'next_service_due' not in columns:
                print("Adding 'next_service_due' column...")
                db.session.execute(text('ALTER TABLE product ADD COLUMN next_service_due DATE'))
                print("✓ Added 'next_service_due' column successfully")
            else:
                print("'next_service_due' column already exists")
            
            # Commit the changes
            db.session.commit()
            print("\n✓ Database migration completed successfully!")
            
            # Show updated column list
            inspector = db.inspect(db.engine)
            updated_columns = [col['name'] for col in inspector.get_columns('product')]
            print(f"\nUpdated Product table now has {len(updated_columns)} columns:")
            for col in updated_columns:
                print(f"  - {col}")
            
            # Show current product count
            product_count = Product.query.count()
            print(f"\nCurrent database contains {product_count} products")
            
            if product_count > 0:
                print("\nNote: Existing products will have NULL values for servicing fields.")
                print("You can update these through the web interface by editing each product.")
                
        except Exception as e:
            print(f"\n❌ Error during migration: {str(e)}")
            db.session.rollback()
            return False
            
    return True

def verify_migration():
    """Verify that the migration was successful."""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Try to query the new fields
            test_product = Product.query.first()
            if test_product:
                # Access the new fields to ensure they exist
                last_serviced = test_product.last_serviced
                next_service_due = test_product.next_service_due
                print("✓ Migration verification successful - new fields are accessible")
                return True
            else:
                print("✓ Migration successful (no products to test with)")
                return True
                
        except Exception as e:
            print(f"❌ Migration verification failed: {str(e)}")
            return False

if __name__ == '__main__':
    print("CUBE - PRO: Database Migration for Servicing History")
    print("=" * 55)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Perform the migration
    if add_servicing_fields():
        print()
        print("Verifying migration...")
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("\nThe following features are now available:")
            print("  • Track last serviced date for each UAV")
            print("  • Automatic calculation of next service due date (90 days)")
            print("  • Service status indicators in the UI")
            print("  • Visual alerts for overdue maintenance")
            print("\nYou can now start using the servicing history features!")
        else:
            print("\n⚠️  Migration completed but verification failed.")
            print("Please check the database manually.")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
