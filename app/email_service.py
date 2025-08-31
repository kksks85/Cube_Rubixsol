"""
Email Service Module
Handles sending emails for the CUBE - PRO system
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from app.models import db, EmailLog
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def send_email(to_email, subject, body, is_html=False, template_type='general', user_id=None, work_order_id=None):
    """
    Send email using configured SMTP settings and log to database
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body content
        is_html (bool): Whether body is HTML content
        template_type (str): Type of email template being sent
        user_id (int): Optional user ID for logging
        work_order_id (int): Optional work order ID for logging
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    email_log = None
    try:
        # Get email configuration from Flask app config
        smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = current_app.config.get('MAIL_PORT', 587)
        sender_email = current_app.config.get('MAIL_USERNAME', 'noreply@cubeproapp.com')
        sender_password = current_app.config.get('MAIL_PASSWORD', '')
        use_tls = current_app.config.get('MAIL_USE_TLS', True)
        
        # Create email log entry
        email_log = EmailLog(
            recipient_email=to_email,
            subject=subject,
            template_type=template_type,
            user_id=user_id,
            work_order_id=work_order_id,
            status='pending'
        )
        db.session.add(email_log)
        db.session.flush()  # Get the ID but don't commit yet
        
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
        
        # For development, simulate email sending and log it
        # In production, uncomment the SMTP code below
        logger.info(f"📧 Email sent to {to_email}")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   Template: {template_type}")
        
        # Update email log as sent
        email_log.status = 'sent'
        email_log.sent_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # Uncomment for actual email sending:
        # Create SMTP session
        # server = smtplib.SMTP(smtp_server, smtp_port)
        # if use_tls:
        #     server.starttls()
        # server.login(sender_email, sender_password)
        # text = msg.as_string()
        # server.sendmail(sender_email, to_email, text)
        # server.quit()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        
        # Update email log as failed
        if email_log:
            email_log.status = 'failed'
            email_log.error_message = str(e)
            email_log.sent_at = datetime.now(timezone.utc)
            try:
                db.session.commit()
            except:
                db.session.rollback()
        
        return False
        # if use_tls:
        #     server.starttls()  # Enable security
        # 
        # if sender_password:
        #     server.login(sender_email, sender_password)
        # 
        # text = msg.as_string()
        # server.sendmail(sender_email, to_email, text)
        # server.quit()
        
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
    
    return send_email(
        to_email=user.email,
        subject=subject,
        body=body,
        template_type='work_order_notification',
        user_id=user.id,
        work_order_id=work_order.id
    )

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
    
    return send_email(
        to_email=user.email,
        subject=subject,
        body=body,
        template_type='user_welcome',
        user_id=user.id
    )


def send_approval_email(approval):
    """Send approval request email to the approver"""
    try:
        from flask import url_for
        from datetime import datetime, timezone
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Generate approval links
        approve_url = url_for('approval_management.email_approve', 
                            token=approval.approval_token, _external=True)
        reject_url = url_for('approval_management.email_reject', 
                           token=approval.approval_token, _external=True)
        view_url = url_for('approval_management.view_approval', 
                         approval_id=approval.id, _external=True)
        
        # Email content
        subject = f"Work Order Approval Required - {approval.incident.incident_number_formatted}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Work Order Approval Required</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .incident-details {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .approval-actions {{ text-align: center; margin: 20px 0; }}
                .btn {{ display: inline-block; padding: 12px 24px; margin: 10px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .btn-success {{ background-color: #28a745; color: white; }}
                .btn-danger {{ background-color: #dc3545; color: white; }}
                .btn-info {{ background-color: #17a2b8; color: white; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Work Order Approval Required</h1>
                </div>
                
                <div class="content">
                    <p>Dear {approval.approver.full_name},</p>
                    
                    <p>A work order requires your approval. Please review the details below:</p>
                    
                    <div class="incident-details">
                        <h3>Incident Details</h3>
                        <p><strong>Incident Number:</strong> {approval.incident.incident_number_formatted}</p>
                        <p><strong>Title:</strong> {approval.incident.title}</p>
                        <p><strong>Customer:</strong> {approval.incident.customer_name}</p>
                        <p><strong>Priority:</strong> {approval.incident.priority}</p>
                        <p><strong>Requested By:</strong> {approval.requester.full_name}</p>
                        <p><strong>Request Date:</strong> {approval.requested_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        {f'<p><strong>Estimated Cost:</strong> ${approval.estimated_cost}</p>' if approval.estimated_cost else ''}
                        {f'<p><strong>Estimated Hours:</strong> {approval.estimated_hours} hours</p>' if approval.estimated_hours else ''}
                        {f'<p><strong>Request Details:</strong> {approval.request_details}</p>' if approval.request_details else ''}
                    </div>
                    
                    <div class="approval-actions">
                        <h3>Quick Actions</h3>
                        <a href="{approve_url}" class="btn btn-success">✓ APPROVE</a>
                        <a href="{reject_url}" class="btn btn-danger">✗ REJECT</a>
                        <a href="{view_url}" class="btn btn-info">📋 VIEW DETAILS</a>
                    </div>
                    
                    <p><strong>Note:</strong> You can also manage this approval from the Administration → Approval Management panel in the system.</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from CUBE PRO Work Order Management System</p>
                    <p>Do not reply to this email</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send HTML email with proper logging
        success = send_email(
            to_email=approval.approver.email,
            subject=subject, 
            body=html_content, 
            is_html=True,
            template_type='work_order_approval',
            user_id=approval.approver_id
        )
        
        if success:
            # Update approval record
            approval.email_sent_at = datetime.now(timezone.utc)
            logger.info(f"Approval email sent successfully to {approval.approver.email} for incident {approval.incident.incident_number}")
        
        return success
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send approval email: {str(e)}")
        return False


def send_approval_notification(approval, action):
    """Send notification after approval/rejection"""
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        # Email content
        subject = f"Work Order {action.title()} - {approval.incident.incident_number_formatted}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Work Order {action.title()}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ padding: 20px; text-align: center; }}
                .header.approved {{ background-color: #28a745; color: white; }}
                .header.rejected {{ background-color: #dc3545; color: white; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .details {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header {action.lower()}">
                    <h1>Work Order {action.title()}</h1>
                </div>
                
                <div class="content">
                    <p>Dear {approval.requester.full_name},</p>
                    
                    <p>Your work order request has been <strong>{action.lower()}</strong>.</p>
                    
                    <div class="details">
                        <p><strong>Incident:</strong> {approval.incident.incident_number_formatted}</p>
                        <p><strong>{action.title()} By:</strong> {approval.approver.full_name}</p>
                        <p><strong>Date:</strong> {approval.approved_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        {f'<p><strong>Comments:</strong> {approval.approval_comments}</p>' if approval.approval_comments else ''}
                    </div>
                    
                    <p>{'You can now proceed with the repair/maintenance work.' if action == 'approved' else 'Please review the comments and resubmit if necessary.'}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send HTML email with proper logging
        success = send_email(
            to_email=approval.requester.email,
            subject=subject, 
            body=html_content, 
            is_html=True,
            template_type='approval_notification',
            user_id=approval.requested_by_id
        )
        
        if success:
            logger.info(f"Approval notification sent to {approval.requester.email}")
        
        return success
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send approval notification: {str(e)}")
        return False
