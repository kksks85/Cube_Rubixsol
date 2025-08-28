#!/usr/bin/env python3
"""
Add new workflow fields to ServiceIncident model
Based on the new flowchart workflow design
"""

import sqlite3
from datetime import datetime

# Database connection
DB_PATH = 'instance/workorder.db'

def add_workflow_fields():
    """Add new workflow fields to service_incidents table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # List of new fields to add
    new_fields = [
        # New workflow status
        ("workflow_status", "VARCHAR(50) DEFAULT 'INCIDENT_RAISED'"),
        
        # Decision points
        ("requires_part_replacement", "BOOLEAN DEFAULT FALSE"),
        ("faulty_parts_collected", "BOOLEAN DEFAULT FALSE"),
        
        # Workflow timestamps
        ("technician_assigned_at", "DATETIME"),
        ("inspection_started_at", "DATETIME"),
        ("inspection_completed_at", "DATETIME"),
        ("parts_required_determined_at", "DATETIME"),
        ("work_order_raised_at", "DATETIME"),
        ("parts_collected_at", "DATETIME"),
        ("service_completed_at", "DATETIME"),
        ("faulty_parts_collected_at", "DATETIME"),
        ("inventory_updated_at", "DATETIME"),
        ("incident_closed_at", "DATETIME"),
        
        # Integration fields
        ("related_work_order_id", "INTEGER"),
        ("required_parts_list", "TEXT"),
        ("collected_parts_list", "TEXT"),
        ("faulty_parts_list", "TEXT"),
        
        # Inspection report fields
        ("inspection_report", "TEXT"),
        ("inspection_findings", "TEXT"),
        ("parts_required_details", "TEXT")
    ]
    
    # Check which fields already exist
    cursor.execute("PRAGMA table_info(service_incidents)")
    existing_fields = [field[1] for field in cursor.fetchall()]
    
    # Add new fields that don't exist
    added_fields = []
    for field_name, field_definition in new_fields:
        if field_name not in existing_fields:
            try:
                cursor.execute(f"ALTER TABLE service_incidents ADD COLUMN {field_name} {field_definition}")
                added_fields.append(field_name)
                print(f"✅ Added field: {field_name}")
            except sqlite3.Error as e:
                print(f"❌ Error adding field {field_name}: {e}")
        else:
            print(f"⚪ Field already exists: {field_name}")
    
    # Set initial workflow_status for existing incidents
    try:
        cursor.execute("""
            UPDATE service_incidents 
            SET workflow_status = 'INCIDENT_RAISED' 
            WHERE workflow_status IS NULL OR workflow_status = ''
        """)
        updated_count = cursor.rowcount
        print(f"✅ Updated workflow_status for {updated_count} existing incidents")
    except sqlite3.Error as e:
        print(f"❌ Error updating workflow_status: {e}")
    
    conn.commit()
    conn.close()
    
    return added_fields

def verify_migration():
    """Verify that all fields were added correctly"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(service_incidents)")
    fields = cursor.fetchall()
    
    print("\n📋 Current service_incidents table structure:")
    print("-" * 50)
    for field in fields:
        print(f"{field[1]:<30} {field[2]:<20} {'NOT NULL' if field[3] else 'NULL':<10} {field[4] if field[4] else ''}")
    
    conn.close()

if __name__ == "__main__":
    print("🔧 Adding workflow fields to ServiceIncident model...")
    print("=" * 60)
    
    try:
        added_fields = add_workflow_fields()
        print(f"\n✅ Successfully added {len(added_fields)} new fields")
        
        verify_migration()
        
        print("\n🎉 Migration completed successfully!")
        print("\nNew workflow features:")
        print("- Enhanced workflow status tracking")
        print("- Technician assignment management")
        print("- Inspection process workflow")
        print("- Parts requirement decision points")
        print("- Work order integration")
        print("- Inventory update tracking")
        print("- Faulty parts collection")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
