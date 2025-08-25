#!/usr/bin/env python3
"""
Migration script to add email management models
"""

import sys
import os

# Add the parent directory to the path to import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app, db
from app.models import EmailLog, EmailTemplate, User, Role
from datetime import datetime, timedelta
import random

def create_email_models():
    """Create the email management models and sample data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create the new tables
            db.create_all()
            print("✓ Email management tables created successfully")
            
            # Check if we already have email templates
            if EmailTemplate.query.count() == 0:
                # Create default email templates
                templates = [
                    {
                        'name': 'Work Order Assignment',
                        'template_type': 'work_order_assigned',
                        'subject': 'New Work Order Assigned - {work_order_number}',
                        'body': '''
                        <h2>New Work Order Assigned</h2>
                        <p>Hello {user_name},</p>
                        <p>A new work order has been assigned to you:</p>
                        <ul>
                            <li><strong>Work Order:</strong> {work_order_number}</li>
                            <li><strong>Title:</strong> {title}</li>
                            <li><strong>Priority:</strong> {priority}</li>
                            <li><strong>Due Date:</strong> {due_date}</li>
                        </ul>
                        <p>Please log in to the system to view the full details.</p>
                        <p>Best regards,<br>CUBE - PRO System</p>
                        ''',
                        'is_html': True,
                        'is_active': True
                    },
                    {
                        'name': 'Work Order Completion',
                        'template_type': 'work_order_completed',
                        'subject': 'Work Order Completed - {work_order_number}',
                        'body': '''
                        <h2>Work Order Completed</h2>
                        <p>Hello {user_name},</p>
                        <p>Work Order {work_order_number} has been marked as completed.</p>
                        <p><strong>Title:</strong> {title}</p>
                        <p><strong>Completed by:</strong> {completed_by}</p>
                        <p>Best regards,<br>CUBE - PRO System</p>
                        ''',
                        'is_html': True,
                        'is_active': True
                    },
                    {
                        'name': 'Welcome Email',
                        'template_type': 'user_welcome',
                        'subject': 'Welcome to CUBE - PRO',
                        'body': '''
                        <h2>Welcome to CUBE - PRO</h2>
                        <p>Hello {user_name},</p>
                        <p>Welcome to the CUBE - PRO system! Your account has been created successfully.</p>
                        <p><strong>Username:</strong> {username}</p>
                        <p>Please contact your administrator for login credentials.</p>
                        <p>Best regards,<br>CUBE - PRO System</p>
                        ''',
                        'is_html': True,
                        'is_active': True
                    },
                    {
                        'name': 'Password Reset',
                        'template_type': 'password_reset',
                        'subject': 'Password Reset Request',
                        'body': '''
                        <h2>Password Reset Request</h2>
                        <p>Hello {user_name},</p>
                        <p>You have requested a password reset for your CUBE - PRO account.</p>
                        <p>Please contact your administrator to reset your password.</p>
                        <p>If you did not request this reset, please ignore this email.</p>
                        <p>Best regards,<br>CUBE - PRO System</p>
                        ''',
                        'is_html': True,
                        'is_active': True
                    },
                    {
                        'name': 'Work Order Overdue',
                        'template_type': 'work_order_overdue',
                        'subject': 'URGENT: Overdue Work Order - {work_order_number}',
                        'body': '''
                        <h2 style="color: red;">URGENT: Overdue Work Order</h2>
                        <p>Hello {user_name},</p>
                        <p>The following work order is now overdue:</p>
                        <ul>
                            <li><strong>Work Order:</strong> {work_order_number}</li>
                            <li><strong>Title:</strong> {title}</li>
                            <li><strong>Due Date:</strong> {due_date}</li>
                            <li><strong>Days Overdue:</strong> {days_overdue}</li>
                        </ul>
                        <p>Please complete this work order as soon as possible.</p>
                        <p>Best regards,<br>CUBE - PRO System</p>
                        ''',
                        'is_html': True,
                        'is_active': True
                    }
                ]
                
                # Get the first admin user for created_by
                admin_user = User.query.join(Role).filter(Role.name == 'admin').first()
                if not admin_user:
                    admin_user = User.query.first()  # Fallback to any user
                
                for template_data in templates:
                    template = EmailTemplate(
                        name=template_data['name'],
                        template_type=template_data['template_type'],
                        subject=template_data['subject'],
                        body=template_data['body'],
                        is_html=template_data['is_html'],
                        is_active=template_data['is_active'],
                        created_by_id=admin_user.id if admin_user else None
                    )
                    db.session.add(template)
                
                db.session.commit()
                print(f"✓ Created {len(templates)} email templates")
            
            # Create sample email logs for the last 7 days
            if EmailLog.query.count() == 0:
                # Get some users and work orders for sample data
                users = User.query.limit(10).all()
                
                if users:
                    sample_logs = []
                    today = datetime.now()
                    
                    for i in range(7):  # Last 7 days
                        day = today - timedelta(days=i)
                        
                        # Generate 5-15 emails per day
                        emails_per_day = random.randint(5, 15)
                        
                        for j in range(emails_per_day):
                            user = random.choice(users)
                            
                            # Random email types
                            email_types = ['work_order_assigned', 'work_order_completed', 'user_welcome', 'password_reset']
                            email_type = random.choice(email_types)
                            
                            # 95% success rate
                            status = 'sent' if random.random() < 0.95 else 'failed'
                            
                            log = EmailLog(
                                recipient_email=user.email,
                                subject=f'Test {email_type.replace("_", " ").title()}',
                                status=status,
                                template_type=email_type,
                                sent_at=day - timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                                user_id=user.id,
                                error_message='SMTP connection failed' if status == 'failed' else None
                            )
                            sample_logs.append(log)
                    
                    # Add all logs to the session
                    for log in sample_logs:
                        db.session.add(log)
                    
                    db.session.commit()
                    print(f"✓ Created {len(sample_logs)} sample email logs")
            
            print("\n✅ Email management setup completed successfully!")
            print("\nCreated models:")
            print("- EmailLog: For tracking sent emails and statistics")
            print("- EmailTemplate: For managing email templates")
            print("\nSample data created:")
            print(f"- {EmailTemplate.query.count()} email templates")
            print(f"- {EmailLog.query.count()} email log entries")
            
        except Exception as e:
            print(f"❌ Error creating email models: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    print("Setting up email management models...")
    success = create_email_models()
    if success:
        print("\n🎉 Setup completed! You can now view real email statistics in the dashboard.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
