"""
Email Management Routes
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.email_management import bp
from app.models import User, WorkOrder, EmailConfig
from app.email_service import send_email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@bp.route('/')
@login_required
def dashboard():
    """Email management dashboard"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to access email management.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get email statistics
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'pending_notifications': 0,  # Implement based on your notification system
        'email_templates': 5  # Hardcoded for now, implement based on your templates
    }
    
    return render_template('email_management/dashboard.html', 
                         title='Email Management', stats=stats)

@bp.route('/templates')
@login_required
def email_templates():
    """Manage email templates"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to access email templates.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Email template types
    templates = [
        {
            'id': 1,
            'name': 'Work Order Assignment',
            'subject': 'New Work Order Assigned - {work_order_number}',
            'description': 'Sent when a work order is assigned to a user',
            'active': True
        },
        {
            'id': 2,
            'name': 'Work Order Completion',
            'subject': 'Work Order Completed - {work_order_number}',
            'description': 'Sent when a work order is marked as completed',
            'active': True
        },
        {
            'id': 3,
            'name': 'Welcome Email',
            'subject': 'Welcome to CUBE - PRO',
            'description': 'Sent to new users when they are created',
            'active': True
        },
        {
            'id': 4,
            'name': 'Password Reset',
            'subject': 'Password Reset Request',
            'description': 'Sent when user requests password reset',
            'active': True
        },
        {
            'id': 5,
            'name': 'Work Order Overdue',
            'subject': 'URGENT: Overdue Work Order - {work_order_number}',
            'description': 'Sent when a work order becomes overdue',
            'active': False
        }
    ]
    
    return render_template('email_management/templates.html', 
                         title='Email Templates', templates=templates)

@bp.route('/settings')
@login_required
def email_settings():
    """Email configuration settings"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to access email settings.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get current email configuration (implement based on your config system)
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'use_tls': True,
        'sender_email': 'noreply@cubeproapp.com',
        'sender_name': 'CUBE - PRO System'
    }
    
    return render_template('email_management/settings.html', 
                         title='Email Settings', config=email_config)

@bp.route('/send-test', methods=['POST'])
@login_required
def send_test_email():
    """Send a test email"""
    if not current_user.has_role('admin'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    test_email = request.form.get('test_email')
    
    if not test_email:
        return jsonify({'success': False, 'message': 'Email address required'}), 400
    
    try:
        # Send test email
        subject = 'CUBE - PRO Test Email'
        body = f"""
        Hello,
        
        This is a test email from the CUBE - PRO system.
        
        If you received this email, your email configuration is working correctly.
        
        Best regards,
        CUBE - PRO System
        """
        
        # Implement actual email sending here
        # send_email(test_email, subject, body)
        
        return jsonify({'success': True, 'message': 'Test email sent successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to send email: {str(e)}'}), 500

@bp.route('/notifications')
@login_required
def email_notifications():
    """Manage email notifications"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to access email notifications.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Notification settings
    notifications = [
        {
            'id': 1,
            'name': 'Work Order Assignment',
            'description': 'Notify users when assigned to a work order',
            'enabled': True,
            'recipients': 'Assigned User'
        },
        {
            'id': 2,
            'name': 'Work Order Status Change',
            'description': 'Notify when work order status changes',
            'enabled': True,
            'recipients': 'Creator & Assigned User'
        },
        {
            'id': 3,
            'name': 'Work Order Overdue',
            'description': 'Send alerts for overdue work orders',
            'enabled': False,
            'recipients': 'Managers & Assigned User'
        },
        {
            'id': 4,
            'name': 'Daily Summary',
            'description': 'Daily email summary of work orders',
            'enabled': False,
            'recipients': 'All Managers'
        }
    ]
    
    return render_template('email_management/notifications.html', 
                         title='Email Notifications', notifications=notifications)

@bp.route('/logs')
@login_required
def email_logs():
    """View email sending logs"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to access email logs.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Sample email logs (implement actual logging)
    logs = [
        {
            'id': 1,
            'timestamp': '2025-01-15 10:30:00',
            'recipient': 'user@example.com',
            'subject': 'Work Order WO-00001 Assigned',
            'status': 'Sent',
            'type': 'Assignment'
        },
        {
            'id': 2,
            'timestamp': '2025-01-15 09:15:00',
            'recipient': 'manager@example.com',
            'subject': 'Work Order WO-00002 Completed',
            'status': 'Sent',
            'type': 'Completion'
        },
        {
            'id': 3,
            'timestamp': '2025-01-15 08:45:00',
            'recipient': 'test@example.com',
            'subject': 'CUBE - PRO Test Email',
            'status': 'Failed',
            'type': 'Test'
        }
    ]
    
    return render_template('email_management/logs.html', 
                         title='Email Logs', logs=logs)
