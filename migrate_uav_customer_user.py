#!/usr/bin/env python3
"""
Database Migration: Add customer_user_id to UAV Service Incidents
This script adds the customer_user_id field to link incidents to registered users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import UAVServiceIncident, User
from datetime import datetime

def run_migration():
    """Add customer_user_id column to uav_service_incidents table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = inspector.get_columns('uav_service_incidents')
            column_names = [col['name'] for col in columns]
            
            if 'customer_user_id' in column_names:
                print("✅ customer_user_id column already exists!")
                return True
            
            print("🔄 Adding customer_user_id column to uav_service_incidents table...")
            
            # Add the column using newer SQLAlchemy syntax
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE uav_service_incidents 
                    ADD COLUMN customer_user_id INTEGER
                """))
                conn.commit()
            
            # Add foreign key constraint (if supported)
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text("""
                        ALTER TABLE uav_service_incidents 
                        ADD CONSTRAINT fk_uav_incidents_customer_user 
                        FOREIGN KEY (customer_user_id) REFERENCES users (id)
                    """))
                    conn.commit()
                print("✅ Foreign key constraint added successfully!")
            except Exception as e:
                print(f"⚠️  Foreign key constraint could not be added: {str(e)}")
                print("   This is normal for SQLite databases")
            
            # Create index for better performance
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text("""
                        CREATE INDEX idx_uav_incidents_customer_user 
                        ON uav_service_incidents(customer_user_id)
                    """))
                    conn.commit()
                print("✅ Index created successfully!")
            except Exception as e:
                print(f"⚠️  Index could not be created: {str(e)}")
            
            print("✅ Migration completed successfully!")
            print("📋 Summary:")
            print("   - Added customer_user_id column to uav_service_incidents table")
            print("   - Column allows linking incidents to registered users")
            print("   - Foreign key constraint and index added (if supported)")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            return False

if __name__ == '__main__':
    print("🚀 Starting UAV Service Incident Customer User Migration...")
    print("=" * 60)
    
    success = run_migration()
    
    print("=" * 60)
    if success:
        print("✅ Migration completed successfully!")
        print("🎉 UAV Service incidents can now be linked to registered users!")
    else:
        print("❌ Migration failed!")
        print("Please check the error messages above.")
    
    sys.exit(0 if success else 1)
