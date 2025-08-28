#!/usr/bin/env python3
"""
Update UAV Service Incident Model Fields
Replaces old UAV fields with new equipment details fields
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db

def update_uav_incident_fields():
    """Update UAV Service Incident table fields"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Updating UAV Service Incident table fields...")
            
            # Check if we can modify the table structure
            connection = db.engine.connect()
            
            # For SQLite, we need to create a new table and migrate data
            print("📋 Checking current table structure...")
            
            # Add new columns first (this is safe)
            print("➕ Adding new columns...")
            
            try:
                # Add new columns for UAV Equipment Details
                connection.execute(db.text("""
                    ALTER TABLE uav_service_incidents 
                    ADD COLUMN serial_number VARCHAR(40)
                """))
                print("✓ Added serial_number column")
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"⚠️  Error adding serial_number: {e}")
            
            try:
                connection.execute(db.text("""
                    ALTER TABLE uav_service_incidents 
                    ADD COLUMN product_name VARCHAR(100)
                """))
                print("✓ Added product_name column")
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"⚠️  Error adding product_name: {e}")
            
            try:
                connection.execute(db.text("""
                    ALTER TABLE uav_service_incidents 
                    ADD COLUMN owner_company VARCHAR(100)
                """))
                print("✓ Added owner_company column")
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"⚠️  Error adding owner_company: {e}")
            
            try:
                connection.execute(db.text("""
                    ALTER TABLE uav_service_incidents 
                    ADD COLUMN last_service_date DATE
                """))
                print("✓ Added last_service_date column")
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"⚠️  Error adding last_service_date: {e}")
            
            # Migrate existing data
            print("📦 Migrating existing data...")
            
            # Copy uav_serial_number to serial_number
            connection.execute(db.text("""
                UPDATE uav_service_incidents 
                SET serial_number = uav_serial_number 
                WHERE uav_serial_number IS NOT NULL AND serial_number IS NULL
            """))
            
            # Copy uav_model to product_name
            connection.execute(db.text("""
                UPDATE uav_service_incidents 
                SET product_name = uav_model 
                WHERE uav_model IS NOT NULL AND product_name IS NULL
            """))
            
            # Set default owner_company for existing records
            connection.execute(db.text("""
                UPDATE uav_service_incidents 
                SET owner_company = 'Unknown' 
                WHERE owner_company IS NULL
            """))
            
            connection.commit()
            connection.close()
            
            print("✅ Successfully updated UAV Service Incident table!")
            print("\n📊 Migration Summary:")
            print("   - Added: serial_number (VARCHAR(40))")
            print("   - Added: product_name (VARCHAR(100))")  
            print("   - Added: owner_company (VARCHAR(100))")
            print("   - Added: last_service_date (DATE)")
            print("   - Migrated existing uav_serial_number → serial_number")
            print("   - Migrated existing uav_model → product_name")
            print("   - Set default 'Unknown' for owner_company")
            print("\n⚠️  Note: Old fields (uav_model, uav_serial_number, flight_hours) still exist")
            print("   They can be removed manually if needed after testing.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating table: {str(e)}")
            return False

def list_table_structure():
    """List current table structure"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n📋 Current UAV Service Incident Table Structure:")
            print("=" * 60)
            
            connection = db.engine.connect()
            result = connection.execute(db.text("PRAGMA table_info(uav_service_incidents)"))
            
            for row in result:
                col_id, name, col_type, not_null, default_val, pk = row
                nullable = "NOT NULL" if not_null else "NULL"
                primary = " (PRIMARY KEY)" if pk else ""
                default = f" DEFAULT {default_val}" if default_val else ""
                print(f"{name:<25} | {col_type:<15} | {nullable:<10}{default}{primary}")
            
            connection.close()
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error listing table structure: {str(e)}")

if __name__ == '__main__':
    print("🔧 UAV Service Incident Table Field Update")
    print("=" * 50)
    
    # Show current structure
    list_table_structure()
    
    # Update fields
    success = update_uav_incident_fields()
    
    if success:
        # Show updated structure
        list_table_structure()
        print("✅ Field update completed successfully!")
    else:
        print("❌ Field update failed!")
        sys.exit(1)
