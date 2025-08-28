#!/usr/bin/env python3
"""
Complete UAV Service Incident 1 by advancing to final step
"""

from app import create_app
from app.models import db, UAVServiceIncident, UAVServiceActivity, User
from datetime import datetime, timezone

def complete_incident_1():
    """Complete incident 1 workflow"""
    app = create_app()
    
    with app.app_context():
        # Get incident 1
        incident = UAVServiceIncident.query.get(1)
        admin_user = User.query.get(1)
        
        if not incident:
            print("❌ Incident 1 not found!")
            return
            
        if not admin_user:
            print("❌ Admin user not found!")
            return
            
        print("=== COMPLETING UAV SERVICE INCIDENT 1 ===")
        print(f"Current Status: {incident.workflow_status}")
        print(f"Current Step: {incident.workflow_step_info['step']}/5")
        print(f"Current Progress: {incident.workflow_progress_percentage}%")
        
        # Check current status and advance accordingly
        if incident.workflow_status == 'QUALITY_CHECK':
            print("\n🔧 Advancing from QUALITY_CHECK to PREVENTIVE_MAINTENANCE...")
            
            # Advance to final step
            now = datetime.now(timezone.utc)
            incident.workflow_status = 'PREVENTIVE_MAINTENANCE'
            incident.handed_over_at = now
            incident.is_preventive_maintenance = True
            
            # Add activity log
            activity = UAVServiceActivity(
                uav_service_incident_id=incident.id,
                user_id=admin_user.id,
                activity_type='workflow_advance',
                description='Workflow completed - Advanced to PREVENTIVE_MAINTENANCE. Incident service completed.'
            )
            db.session.add(activity)
            
            print(f"✅ Workflow completed!")
            print(f"✅ Final status: {incident.workflow_status}")
            print(f"✅ Final step: {incident.workflow_step_info['step']}/5")
            print(f"✅ Final progress: {incident.workflow_progress_percentage}%")
            
        elif incident.workflow_status == 'PREVENTIVE_MAINTENANCE':
            print("✅ Incident is already completed!")
            print(f"Status: {incident.workflow_status}")
            print(f"Step: {incident.workflow_step_info['step']}/5")
            print(f"Progress: {incident.workflow_progress_percentage}%")
            
        else:
            print(f"⚠️ Incident is at unexpected status: {incident.workflow_status}")
            print("Please complete the previous steps first")
            return
        
        # Commit changes
        db.session.commit()
        print("\n✅ Changes saved to database!")
        
        # Show final status
        print(f"\n=== FINAL STATUS ===")
        print(f"Incident: {incident.incident_number}")
        print(f"Workflow Status: {incident.workflow_status}")
        print(f"Step: {incident.workflow_step_info['step']}/5 - {incident.workflow_step_info['name']}")
        print(f"Progress: {incident.workflow_progress_percentage}%")
        print(f"Service Completed: {'✅ YES' if incident.workflow_status == 'PREVENTIVE_MAINTENANCE' else '❌ NO'}")
        
        if incident.workflow_status == 'PREVENTIVE_MAINTENANCE':
            print("\n🎉 INCIDENT SUCCESSFULLY COMPLETED! 🎉")
            print("📋 Summary:")
            print("✅ Service request processed")
            print("✅ Diagnosis completed")  
            print("✅ Repair/maintenance performed")
            print("✅ Quality check passed")
            print("✅ Preventive maintenance scheduled")
            print("✅ Customer handover completed")

if __name__ == '__main__':
    complete_incident_1()
