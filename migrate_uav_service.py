#!/usr/bin/env python3
"""
UAV Service Database Migration
Creates the UAV service management tables
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models import (UAVServiceIncident, UAVServiceActivity, UAVMaintenanceSchedule)

def create_uav_service_tables():
    """Create UAV service management tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ UAV service tables created successfully!")
            
            # Print table information
            print("\n📋 Created tables:")
            print("   - uav_service_incidents")
            print("   - uav_service_activities") 
            print("   - uav_maintenance_schedules")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
            
    return True

if __name__ == '__main__':
    print("🚁 Creating UAV Service Management Tables...")
    print("=" * 50)
    
    success = create_uav_service_tables()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🚁 UAV Service Management System is ready to use!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
