#!/usr/bin/env python3
"""
Add status workflow fields to ServiceIncident model
"""

from app import create_app, db
from app.models import ServiceIncident
from datetime import datetime, timezone

def add_status_workflow_fields():
    """Add new status workflow fields to ServiceIncident table"""
    
    app = create_app()
    
    with app.app_context():
        print("Adding status workflow fields to ServiceIncident table...")
        
        # Check if the new columns already exist
        inspector = db.inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('service_incidents')]
        
        # Add new columns if they don't exist
        new_columns = [
            'status_step',
            'status_details',
            'step1_received_at',
            'step2_initial_inspection_at',
            'step3_diagnosis_at',
            'step4_approval_at',
            'step5_parts_ordered_at',
            'step6_repair_started_at',
            'step7_testing_at',
            'step8_completed_at'
        ]
        
        for column in new_columns:
            if column not in columns:
                print(f"Adding column: {column}")
                try:
                    if column == 'status_step':
                        db.engine.execute(f'ALTER TABLE service_incidents ADD COLUMN {column} INTEGER DEFAULT 1')
                    elif column == 'status_details':
                        db.engine.execute(f'ALTER TABLE service_incidents ADD COLUMN {column} VARCHAR(50) DEFAULT "INTAKE_RECEIVED"')
                    else:
                        db.engine.execute(f'ALTER TABLE service_incidents ADD COLUMN {column} DATETIME')
                except Exception as e:
                    print(f"Warning: Could not add column {column}: {e}")
        
        # Update existing incidents to initialize workflow
        print("Initializing workflow for existing incidents...")
        
        incidents = ServiceIncident.query.all()
        for incident in incidents:
            if not hasattr(incident, 'status_step') or incident.status_step is None:
                incident.status_step = 1
            if not hasattr(incident, 'status_details') or incident.status_details is None:
                incident.status_details = 'INTAKE_RECEIVED'
            if not hasattr(incident, 'step1_received_at') or incident.step1_received_at is None:
                incident.step1_received_at = incident.received_date or incident.created_at
            
            # Set status steps based on current status
            if incident.status == 'COMPLETED':
                incident.status_step = 8
                incident.status_details = 'READY_FOR_PICKUP'
                incident.step8_completed_at = incident.actual_completion_date or incident.updated_at
            elif incident.status == 'IN_PROGRESS':
                incident.status_step = 6
                incident.status_details = 'REPAIR_IN_PROGRESS'
                incident.step6_repair_started_at = incident.updated_at
            elif incident.status == 'DIAGNOSED':
                incident.status_step = 3
                incident.status_details = 'DIAGNOSIS_COMPLETE'
                incident.step3_diagnosis_at = incident.diagnosis_date or incident.updated_at
            elif incident.status == 'WAITING_PARTS':
                incident.status_step = 5
                incident.status_details = 'PARTS_PROCUREMENT'
                incident.step5_parts_ordered_at = incident.updated_at
            else:  # RECEIVED or other
                incident.status_step = 1
                incident.status_details = 'INTAKE_RECEIVED'
        
        try:
            db.session.commit()
            print(f"Updated {len(incidents)} existing incidents with workflow status")
        except Exception as e:
            print(f"Error updating incidents: {e}")
            db.session.rollback()
        
        print("Status workflow fields added successfully!")

if __name__ == '__main__':
    add_status_workflow_fields()
