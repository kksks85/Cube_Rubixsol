#!/usr/bin/env python3
"""
Update existing service incidents to use new workflow status
"""

import sqlite3
from datetime import datetime

# Database connection
DB_PATH = 'instance/workorder.db'

def update_existing_incidents():
    """Update existing incidents to have workflow_status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get incidents without workflow_status or with empty workflow_status
    cursor.execute("""
        SELECT id, incident_number, created_at 
        FROM service_incidents 
        WHERE workflow_status IS NULL OR workflow_status = ''
    """)
    incidents = cursor.fetchall()
    
    print(f"Found {len(incidents)} incidents to update")
    
    # Update each incident
    for incident_id, incident_number, created_at in incidents:
        cursor.execute("""
            UPDATE service_incidents 
            SET workflow_status = 'INCIDENT_RAISED',
                received_date = COALESCE(received_date, created_at, datetime('now'))
            WHERE id = ?
        """, (incident_id,))
        print(f"✅ Updated incident {incident_number} to INCIDENT_RAISED")
    
    conn.commit()
    
    # Verify updates
    cursor.execute("SELECT COUNT(*) FROM service_incidents WHERE workflow_status = 'INCIDENT_RAISED'")
    count = cursor.fetchone()[0]
    print(f"✅ Total incidents with INCIDENT_RAISED status: {count}")
    
    conn.close()
    return len(incidents)

if __name__ == "__main__":
    print("🔧 Updating existing service incidents...")
    print("=" * 50)
    
    try:
        updated_count = update_existing_incidents()
        print(f"\n✅ Successfully updated {updated_count} incidents")
        print("\n🎉 All incidents now have proper workflow status!")
        
    except Exception as e:
        print(f"❌ Update failed: {e}")
        import traceback
        traceback.print_exc()
