"""
Work Order Management System
Main application entry point
"""

import os
from app import create_app, db
from app.models import User, Role, WorkOrder, Priority, Status, Category

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make database models available in shell context"""
    return {
        'db': db, 
        'User': User, 
        'Role': Role, 
        'WorkOrder': WorkOrder,
        'Priority': Priority,
        'Status': Status,
        'Category': Category
    }

def create_default_data():
    """Create default data on first run"""
    with app.app_context():
        # Create default priorities
        priorities = [
            {'name': 'Low', 'level': 1, 'color': '#28a745'},
            {'name': 'Medium', 'level': 2, 'color': '#ffc107'},
            {'name': 'High', 'level': 3, 'color': '#fd7e14'},
            {'name': 'Critical', 'level': 4, 'color': '#dc3545'}
        ]
        
        for priority_data in priorities:
            priority = Priority.query.filter_by(name=priority_data['name']).first()
            if not priority:
                priority = Priority(**priority_data)
                db.session.add(priority)
        
        # Create default statuses
        statuses = [
            {'name': 'Open', 'description': 'Work order is open and awaiting assignment', 'is_closed': False, 'color': '#007bff'},
            {'name': 'In Progress', 'description': 'Work is currently being performed', 'is_closed': False, 'color': '#fd7e14'},
            {'name': 'On Hold', 'description': 'Work is temporarily suspended', 'is_closed': False, 'color': '#6c757d'},
            {'name': 'Completed', 'description': 'Work has been completed successfully', 'is_closed': True, 'color': '#28a745'},
            {'name': 'Cancelled', 'description': 'Work order has been cancelled', 'is_closed': True, 'color': '#dc3545'}
        ]
        
        for status_data in statuses:
            status = Status.query.filter_by(name=status_data['name']).first()
            if not status:
                status = Status(**status_data)
                db.session.add(status)
        
        # Create default categories
        categories = [
            {'name': 'Maintenance', 'description': 'Routine maintenance tasks'},
            {'name': 'Repair', 'description': 'Equipment and facility repairs'},
            {'name': 'Installation', 'description': 'New equipment or system installation'},
            {'name': 'Inspection', 'description': 'Safety and compliance inspections'},
            {'name': 'Emergency', 'description': 'Emergency response work orders'}
        ]
        
        for category_data in categories:
            category = Category.query.filter_by(name=category_data['name']).first()
            if not category:
                category = Category(**category_data)
                db.session.add(category)
        
        db.session.commit()

if __name__ == '__main__':
    # Create default data on startup
    create_default_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
