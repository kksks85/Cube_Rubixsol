#!/usr/bin/env python3
"""
Fix assignment_rules table schema
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def fix_assignment_rules_table():
    """Drop and recreate assignment_rules table with correct schema"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Drop the existing table
            from sqlalchemy import text
            with db.engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS assignment_rules"))
                conn.commit()
            print("✅ Dropped existing assignment_rules table")
            
            # Import the model after dropping the table
            from app.models import AssignmentRule
            
            # Create the table with correct schema
            db.create_all()
            print("✅ Assignment rules table recreated successfully!")
            
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
            print(f"❌ Error fixing assignment rules table: {str(e)}")
            raise

if __name__ == '__main__':
    fix_assignment_rules_table()
