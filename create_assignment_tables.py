#!/usr/bin/env python3
"""
Migration script to add assignment groups functionality
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import AssignmentGroup, AssignmentGroupMember

def create_assignment_tables():
    """Create assignment group tables"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating assignment group tables...")
            
            # Create the tables
            db.create_all()
            
            print("✅ Assignment group tables created successfully!")
            print("Tables created:")
            print("  - assignment_groups")
            print("  - assignment_group_members")
            
        except Exception as e:
            print(f"❌ Error creating tables: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    create_assignment_tables()
