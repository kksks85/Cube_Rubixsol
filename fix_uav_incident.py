#!/usr/bin/env python3
"""
Fix UAV Service Incident 1 workflow progression
"""

from app import create_app
from app.models import db, UAVServiceIncident, UAVServiceActivity, User
from datetime import datetime, timezone

def fix_incident_1():
    """Fix incident 1 workflow progression"""
    app = create_app()
    
    with app.app_context():
        # Get incident 1
        incident = UAVServiceIncident.query.get(1)
        admin_user = User.query.get(1)  # Assuming user 1 is admin
        
        if not incident:
            print("❌ Incident 1 not found!")
            return
            
        if not admin_user:
            print("❌ Admin user not found!")
            return
            
        print("=== FIXING UAV SERVICE INCIDENT 1 ===")
        print(f"Current Status: {incident.workflow_status}")
        print(f"Current Step: {incident.workflow_step_info['step']}/5")
        
        # Check if we need to advance from DIAGNOSIS_WO to REPAIR_MAINTENANCE
        if incident.workflow_status == 'DIAGNOSIS_WO':
            print("\n🔧 Advancing workflow from DIAGNOSIS_WO to REPAIR_MAINTENANCE...")
            
            # Set the missing timestamps
            now = datetime.now(timezone.utc)
            incident.diagnosis_completed_at = now
            incident.work_order_created_at = now
            incident.repair_started_at = now
            
            # Fix the diagnostic findings (remove the error message)
            incident.diagnostic_findings = "Camera gimbal malfunction - requires replacement and calibration"
            
            # Advance the workflow
            incident.workflow_status = 'REPAIR_MAINTENANCE'
            
            # Add activity log
            activity = UAVServiceActivity(
                uav_service_incident_id=incident.id,
                user_id=admin_user.id,
                activity_type='workflow_advance',
                description='Workflow manually advanced to REPAIR_MAINTENANCE. Fixed diagnostic findings and timestamps.'
            )
            db.session.add(activity)
            
            print(f"✅ Workflow advanced to: {incident.workflow_status}")
            print(f"✅ New step: {incident.workflow_step_info['step']}/5")
            print(f"✅ Progress: {incident.workflow_progress_percentage}%")
            
        elif incident.workflow_status == 'REPAIR_MAINTENANCE':
            print("\n🔧 Incident is already in REPAIR_MAINTENANCE step")
            
            # Check if repair is marked as completed
            if getattr(incident, 'service_status', None) == 'COMPLETED':
                print("🔧 Advancing workflow from REPAIR_MAINTENANCE to QUALITY_CHECK...")
                
                # Advance to quality check
                now = datetime.now(timezone.utc)
                incident.repair_completed_at = now
                incident.quality_check_at = now
                incident.workflow_status = 'QUALITY_CHECK'
                
                # Add activity log
                activity = UAVServiceActivity(
                    uav_service_incident_id=incident.id,
                    user_id=admin_user.id,
                    activity_type='workflow_advance',
                    description='Workflow manually advanced to QUALITY_CHECK after repair completion.'
                )
                db.session.add(activity)
                
                print(f"✅ Workflow advanced to: {incident.workflow_status}")
                print(f"✅ New step: {incident.workflow_step_info['step']}/5")
                print(f"✅ Progress: {incident.workflow_progress_percentage}%")
            else:
                print(f"⏳ Service status is '{getattr(incident, 'service_status', 'Not set')}' - set to 'COMPLETED' to advance")
        
        # Commit changes
        db.session.commit()
        print("\n✅ Changes saved to database!")
        
        # Show final status
        print(f"\n=== FINAL STATUS ===")
        print(f"Workflow Status: {incident.workflow_status}")
        print(f"Step: {incident.workflow_step_info['step']}/5 - {incident.workflow_step_info['name']}")
        print(f"Progress: {incident.workflow_progress_percentage}%")
        print(f"Diagnostic Findings: {incident.diagnostic_findings}")

if __name__ == '__main__':
    fix_incident_1()
