"""
Email Service Module
Handles sending emails for the CUBE - PRO system
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_email(to_email, subject, body, is_html=False):
    """
    Send email using configured SMTP settings
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body content
        is_html (bool): Whether body is HTML content
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Email configuration (should be moved to config/environment variables)
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = 'noreply@cubeproapp.com'
        sender_password = 'your_app_password'  # Use app password for Gmail
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"CUBE - PRO System <{sender_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach body to email
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security
        
        # Uncomment when you have valid SMTP credentials
        # server.login(sender_email, sender_password)
        # text = msg.as_string()
        # server.sendmail(sender_email, to_email, text)
        # server.quit()
        
        # For now, just log the email (in production, actually send it)
        current_app.logger.info(f"Email would be sent to {to_email}: {subject}")
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def send_work_order_notification(user, work_order, notification_type):
    """
    Send work order related notifications
    
    Args:
        user: User object to send notification to
        work_order: WorkOrder object
        notification_type: Type of notification (assigned, completed, etc.)
    """
    subject_map = {
        'assigned': f'Work Order Assigned - {work_order.work_order_number}',
        'completed': f'Work Order Completed - {work_order.work_order_number}',
        'updated': f'Work Order Updated - {work_order.work_order_number}',
        'overdue': f'URGENT: Overdue Work Order - {work_order.work_order_number}'
    }
    
    body_map = {
        'assigned': f"""
        Hello {user.first_name},
        
        A new work order has been assigned to you:
        
        Work Order: {work_order.work_order_number}
        Title: {work_order.title}
        Priority: {work_order.priority.name if work_order.priority else 'Normal'}
        Due Date: {work_order.due_date.strftime('%Y-%m-%d') if work_order.due_date else 'Not set'}
        
        Please log in to the system to view the full details.
        
        Best regards,
        CUBE - PRO System
        """,
        'completed': f"""
        Hello {user.first_name},
        
        Work Order {work_order.work_order_number} has been marked as completed.
        
        Title: {work_order.title}
        Completed by: {work_order.assigned_to.full_name if work_order.assigned_to else 'Unknown'}
        
        Best regards,
        CUBE - PRO System
        """,
        'updated': f"""
        Hello {user.first_name},
        
        Work Order {work_order.work_order_number} has been updated.
        
        Title: {work_order.title}
        Current Status: {work_order.status_detail.name if work_order.status_detail else 'Unknown'}
        
        Please check the system for the latest updates.
        
        Best regards,
        CUBE - PRO System
        """,
        'overdue': f"""
        URGENT NOTIFICATION
        
        Hello {user.first_name},
        
        Work Order {work_order.work_order_number} is now overdue!
        
        Title: {work_order.title}
        Due Date: {work_order.due_date.strftime('%Y-%m-%d') if work_order.due_date else 'Unknown'}
        Days Overdue: {abs(work_order.days_until_due) if work_order.days_until_due else 'Unknown'}
        
        Please take immediate action to complete this work order.
        
        Best regards,
        CUBE - PRO System
        """
    }
    
    subject = subject_map.get(notification_type, f'Work Order Notification - {work_order.work_order_number}')
    body = body_map.get(notification_type, f'Work Order {work_order.work_order_number} notification.')
    
    return send_email(user.email, subject, body)

def send_welcome_email(user, temporary_password=None):
    """
    Send welcome email to new users
    
    Args:
        user: User object
        temporary_password: Temporary password if provided
    """
    subject = "Welcome to CUBE - PRO"
    
    body = f"""
    Hello {user.first_name},
    
    Welcome to the CUBE - PRO Work Order Management System!
    
    Your account has been created with the following details:
    Username: {user.username}
    Email: {user.email}
    Role: {user.role.name.title() if user.role else 'User'}
    
    """
    
    if temporary_password:
        body += f"""
    Temporary Password: {temporary_password}
    
    Please log in and change your password immediately for security reasons.
    """
    
    body += """
    
    You can access the system at: [Your System URL]
    
    If you have any questions, please contact your system administrator.
    
    Best regards,
    CUBE - PRO Administration Team
    """
    
    return send_email(user.email, subject, body)
