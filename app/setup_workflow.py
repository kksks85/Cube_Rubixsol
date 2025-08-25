"""
Complete workflow setup script
"""

import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from app.models import WorkOrderStatus, WorkOrderStatusTransition, WorkOrder
from sqlalchemy import text

def setup_workflow():
    """Complete workflow setup"""
    app = create_app()
    
    with app.app_context():
        print("Setting up workflow system...")
        
        # Step 1: Create tables if they don't exist
        try:
            db.create_all()
            print("✓ Database tables created/verified")
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
        
        # Step 2: Add workflow columns to existing workorders table
        try:
            result = db.session.execute(text("PRAGMA table_info(workorders)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'workflow_stage' not in columns:
                db.session.execute(text("ALTER TABLE workorders ADD COLUMN workflow_stage VARCHAR(50) DEFAULT 'draft'"))
                print("✓ Added workflow_stage column")
            
            if 'approval_status' not in columns:
                db.session.execute(text("ALTER TABLE workorders ADD COLUMN approval_status VARCHAR(20) DEFAULT 'not_required'"))
                print("✓ Added approval_status column")
                
            if 'submitted_at' not in columns:
                db.session.execute(text("ALTER TABLE workorders ADD COLUMN submitted_at DATETIME"))
                print("✓ Added submitted_at column")
                
            if 'approved_at' not in columns:
                db.session.execute(text("ALTER TABLE workorders ADD COLUMN approved_at DATETIME"))
                print("✓ Added approved_at column")
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error adding columns: {e}")
            db.session.rollback()
        
        # Step 3: Create default statuses
        statuses_data = [
            {'name': 'Draft', 'description': 'Work order is being created', 'order_index': 1, 'is_initial': True, 'color': '#6c757d', 'icon': 'fas fa-edit'},
            {'name': 'Pending Approval', 'description': 'Waiting for admin approval', 'order_index': 2, 'requires_approval': True, 'color': '#ffc107', 'icon': 'fas fa-clock'},
            {'name': 'Approved', 'description': 'Approved and ready to start', 'order_index': 3, 'color': '#28a745', 'icon': 'fas fa-check'},
            {'name': 'In Progress', 'description': 'Work is currently being performed', 'order_index': 4, 'color': '#007bff', 'icon': 'fas fa-cog'},
            {'name': 'On Hold', 'description': 'Work is temporarily paused', 'order_index': 5, 'color': '#fd7e14', 'icon': 'fas fa-pause'},
            {'name': 'Completed', 'description': 'Work has been completed', 'order_index': 6, 'is_final': True, 'color': '#28a745', 'icon': 'fas fa-check-circle'},
            {'name': 'Cancelled', 'description': 'Work order has been cancelled', 'order_index': 7, 'is_final': True, 'color': '#dc3545', 'icon': 'fas fa-times-circle'}
        ]
        
        created_statuses = {}
        
        for status_data in statuses_data:
            status = WorkOrderStatus.query.filter_by(name=status_data['name']).first()
            if not status:
                status = WorkOrderStatus(**status_data)
                db.session.add(status)
                db.session.flush()
                print(f"✓ Created status: {status_data['name']}")
            created_statuses[status_data['name']] = status.id
        
        db.session.commit()
        
        # Step 4: Create status transitions
        transitions = [
            ('Draft', 'Pending Approval', None),
            ('Draft', 'Cancelled', 'Admin'),
            ('Pending Approval', 'Approved', 'Admin'),
            ('Pending Approval', 'Draft', 'Admin'),
            ('Pending Approval', 'Cancelled', 'Admin'),
            ('Approved', 'In Progress', None),
            ('Approved', 'Cancelled', 'Admin'),
            ('In Progress', 'On Hold', None),
            ('In Progress', 'Completed', None),
            ('In Progress', 'Cancelled', 'Admin'),
            ('On Hold', 'In Progress', None),
            ('On Hold', 'Cancelled', 'Admin'),
            ('Completed', 'In Progress', 'Admin'),
        ]
        
        for from_status, to_status, required_role in transitions:
            existing = WorkOrderStatusTransition.query.filter_by(
                from_status_id=created_statuses[from_status],
                to_status_id=created_statuses[to_status]
            ).first()
            
            if not existing:
                transition = WorkOrderStatusTransition(
                    from_status_id=created_statuses[from_status],
                    to_status_id=created_statuses[to_status],
                    requires_role=required_role
                )
                db.session.add(transition)
        
        db.session.commit()
        print("✓ Status transitions created")
        
        # Step 5: Update existing work orders to have a status
        try:
            draft_status = WorkOrderStatus.query.filter_by(name='Draft').first()
            if draft_status:
                # Update work orders that don't have a status
                workorders_without_status = WorkOrder.query.filter_by(status_id=None).all()
                for wo in workorders_without_status:
                    wo.status_id = draft_status.id
                    wo.workflow_stage = 'draft'
                    wo.approval_status = 'not_required'
                
                db.session.commit()
                print(f"✓ Updated {len(workorders_without_status)} work orders with default status")
        
        except Exception as e:
            print(f"Error updating existing work orders: {e}")
        
        print("\n🎉 Workflow setup completed successfully!")
        
        # Step 6: Verify setup
        statuses = WorkOrderStatus.query.all()
        print(f"\nCreated {len(statuses)} statuses:")
        for status in statuses:
            print(f"  - {status.name} (ID: {status.id})")
        
        return True

if __name__ == '__main__':
    setup_workflow()
