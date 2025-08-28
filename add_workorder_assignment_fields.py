#!/usr/bin/env python3
"""
Add assignment fields to WorkOrder table
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def add_assignment_fields_to_workorders():
    """Add assignment_group_id and uav_service_incident_id to workorders table"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('workorders')]
            
            # Add assignment_group_id if it doesn't exist
            if 'assignment_group_id' not in columns:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE workorders ADD COLUMN assignment_group_id INTEGER"))
                    conn.commit()
                print("✅ Added assignment_group_id column to workorders table")
            else:
                print("✅ assignment_group_id column already exists")

            # Add uav_service_incident_id if it doesn't exist
            if 'uav_service_incident_id' not in columns:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE workorders ADD COLUMN uav_service_incident_id INTEGER"))
                    conn.commit()
                print("✅ Added uav_service_incident_id column to workorders table")
            else:
                print("✅ uav_service_incident_id column already exists")
                
            # Check final table structure
            columns = inspector.get_columns('workorders')
            print(f"✅ WorkOrders table now has {len(columns)} columns:")
            for col in columns:
                print(f"   - {col['name']} ({col['type']})")
                
        except Exception as e:
            print(f"❌ Error adding assignment fields to workorders: {str(e)}")
            raise

if __name__ == '__main__':
    add_assignment_fields_to_workorders()
