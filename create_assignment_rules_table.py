#!/usr/bin/env python3
"""
Create assignment_rules table
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import AssignmentRule

def create_assignment_rules_table():
    """Create assignment_rules table"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create the assignment_rules table
            db.create_all()
            print("✅ Assignment rules table created successfully!")
            
            # Check if table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'assignment_rules' in tables:
                print("✅ Table 'assignment_rules' confirmed to exist")
                
                # Get column info
                columns = inspector.get_columns('assignment_rules')
                print(f"✅ Table has {len(columns)} columns:")
                for col in columns:
                    print(f"   - {col['name']} ({col['type']})")
            else:
                print("❌ Table 'assignment_rules' was not created")
                
        except Exception as e:
            print(f"❌ Error creating assignment rules table: {str(e)}")
            raise

if __name__ == '__main__':
    create_assignment_rules_table()
