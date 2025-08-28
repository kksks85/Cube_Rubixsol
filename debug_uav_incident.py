#!/usr/bin/env python3
"""
Debug UAV Service Incident workflow issues
"""

from app import create_app
from app.models import UAVServiceIncident, UAVServiceActivity
from datetime import datetime

def debug_incident_1():
    """Debug why incident 1 is stuck at diagnosis step"""
    app = create_app()
    
    with app.app_context():
        # Get incident 1
        incident = UAVServiceIncident.query.get(1)
        
        if not incident:
            print("❌ Incident 1 not found!")
            return
            
        print("=== UAV SERVICE INCIDENT DEBUG ===")
        print(f"Incident ID: {incident.id}")
        print(f"Incident Number: {incident.incident_number}")
        print(f"Title: {incident.title}")
        print(f"Current Workflow Status: {incident.workflow_status}")
        print(f"Workflow Step: {incident.workflow_step_info['step']}/5 - {incident.workflow_step_info['name']}")
        print(f"Progress: {incident.workflow_progress_percentage}%")
        print()
        
        # Check diagnostic completion status
        print("=== DIAGNOSIS STATUS ===")
        print(f"Diagnostic Checklist Completed: {getattr(incident, 'diagnostic_checklist_completed', 'Field missing')}")
        print(f"Diagnostic Findings: {getattr(incident, 'diagnostic_findings', 'Not set')}")
        print(f"Work Order Type: {getattr(incident, 'work_order_type', 'Not set')}")
        print(f"Estimated Cost: {getattr(incident, 'estimated_cost', 'Not set')}")
        print(f"Parts Requested: {getattr(incident, 'parts_requested', 'Not set')}")
        print(f"Technician Notes: {getattr(incident, 'technician_notes', 'Not set')}")
        print(f"Technician ID: {getattr(incident, 'technician_id', 'Not set')}")
        print()
        
        # Check timestamps
        print("=== WORKFLOW TIMESTAMPS ===")
        print(f"Incident Raised At: {incident.incident_raised_at}")
        print(f"Technician Assigned At: {getattr(incident, 'technician_assigned_at', 'Not set')}")
        print(f"Diagnosis Completed At: {getattr(incident, 'diagnosis_completed_at', 'Not set')}")
        print(f"Work Order Created At: {getattr(incident, 'work_order_created_at', 'Not set')}")
        print(f"Repair Started At: {getattr(incident, 'repair_started_at', 'Not set')}")
        print()
        
        # Check related work order
        print("=== WORK ORDER STATUS ===")
        print(f"Related Work Order ID: {getattr(incident, 'related_work_order_id', 'Not set')}")
        if hasattr(incident, 'related_work_order') and incident.related_work_order:
            wo = incident.related_work_order
            print(f"Work Order Title: {wo.title}")
            print(f"Work Order Status ID: {getattr(wo, 'status_id', 'No status_id')}")
        print()
        
        # Check repair/maintenance status
        print("=== REPAIR/MAINTENANCE STATUS ===")
        print(f"Service Status: {getattr(incident, 'service_status', 'Not set')}")
        print(f"Technician Hours: {getattr(incident, 'technician_hours', 'Not set')}")
        print(f"Parts Received: {getattr(incident, 'parts_received', 'Not set')}")
        print(f"Actual Cost: {getattr(incident, 'actual_cost', 'Not set')}")
        print()
        
        # Check activities
        print("=== RECENT ACTIVITIES ===")
        activities = UAVServiceActivity.query.filter_by(
            uav_service_incident_id=incident.id
        ).order_by(UAVServiceActivity.timestamp.desc()).limit(5).all()
        
        if activities:
            for activity in activities:
                print(f"- {activity.timestamp}: {activity.activity_type} - {activity.description}")
        else:
            print("No activities found")
        print()
        
        # Analyze the problem
        print("=== PROBLEM ANALYSIS ===")
        
        if incident.workflow_status == 'DIAGNOSIS_WO':
            if not getattr(incident, 'diagnostic_checklist_completed', False):
                print("🔴 ISSUE: Diagnostic checklist not completed")
                print("   Solution: Complete the diagnosis form properly")
            elif not getattr(incident, 'diagnostic_findings', None):
                print("🔴 ISSUE: Diagnostic findings missing")
                print("   Solution: Fill in diagnostic findings")
            elif not getattr(incident, 'work_order_type', None):
                print("🔴 ISSUE: Work order type not set")
                print("   Solution: Select work order type in diagnosis form")
            else:
                print("🟡 All diagnosis fields seem complete, but workflow not advanced")
                print("   Possible causes:")
                print("   1. Form validation failed")
                print("   2. advance_workflow() method not called")
                print("   3. Database transaction not committed")
        elif incident.workflow_status == 'REPAIR_MAINTENANCE':
            print("✅ Incident is in repair/maintenance step")
            if getattr(incident, 'service_status', None) != 'COMPLETED':
                print("🔴 ISSUE: Service status not set to COMPLETED")
                print("   Solution: Set service status to 'COMPLETED' in repair form")
        else:
            print(f"🔴 ISSUE: Unexpected workflow status: {incident.workflow_status}")
            
        # Suggest fix
        print("\n=== SUGGESTED FIX ===")
        if incident.workflow_status == 'DIAGNOSIS_WO':
            print("1. Go to diagnosis form: /uav-service/incidents/1/diagnosis")
            print("2. Fill all required fields completely")
            print("3. Make sure to submit the form properly")
            print("4. Check for any validation errors")
        elif incident.workflow_status == 'REPAIR_MAINTENANCE':
            print("1. Go to repair form: /uav-service/incidents/1/repair")
            print("2. Set Service Status to 'COMPLETED'")
            print("3. Fill technician hours and work performed")
            print("4. Submit the form")

if __name__ == '__main__':
    debug_incident_1()
