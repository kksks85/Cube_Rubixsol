from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from app.approval_management import bp
from app.models import db, WorkOrderApproval, UAVServiceIncident, User, UAVServiceActivity
from app.email_service import send_approval_email
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Approval management dashboard"""
    if not current_user.has_role('admin') and not current_user.has_role('manager'):
        flash('Access denied. Only administrators and managers can access approval management.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get pending approvals for current user
    pending_approvals = WorkOrderApproval.query.filter_by(
        approver_id=current_user.id, 
        status='PENDING'
    ).order_by(WorkOrderApproval.requested_at.desc()).all()
    
    # Get completed approvals for current user
    completed_approvals = WorkOrderApproval.query.filter(
        WorkOrderApproval.approver_id == current_user.id,
        WorkOrderApproval.status.in_(['APPROVED', 'REJECTED'])
    ).order_by(WorkOrderApproval.approved_at.desc()).limit(20).all()
    
    # Get all pending approvals (for admins)
    all_pending = None
    if current_user.has_role('admin'):
        all_pending = WorkOrderApproval.query.filter_by(
            status='PENDING'
        ).order_by(WorkOrderApproval.requested_at.desc()).all()
    
    return render_template('approval_management/dashboard.html',
                         pending_approvals=pending_approvals,
                         completed_approvals=completed_approvals,
                         all_pending=all_pending)

@bp.route('/approve/<int:approval_id>', methods=['POST'])
@login_required
def approve_request(approval_id):
    """Approve a work order request"""
    approval = WorkOrderApproval.query.get_or_404(approval_id)
    
    # Check if user has permission to approve
    if approval.approver_id != current_user.id and not current_user.has_role('admin'):
        flash('You do not have permission to approve this request.', 'error')
        return redirect(url_for('approval_management.dashboard'))
    
    # Check if already processed
    if approval.status != 'PENDING':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('approval_management.dashboard'))
    
    comments = request.form.get('comments', '')
    
    try:
        # Approve the request
        approval.approve(current_user, comments)
        
        # Update incident workflow status to approved (waiting for repair initiation)
        incident = approval.incident
        incident.workflow_status = 'WO_APPROVED'
        
        # Create activity log
        activity = UAVServiceActivity(
            uav_service_incident_id=incident.id,
            user_id=current_user.id,
            activity_type='wo_approved',
            description=f'Work order approved by {current_user.full_name}. Ready to initiate repair. Comments: {comments}' if comments else f'Work order approved by {current_user.full_name}. Ready to initiate repair.'
        )
        db.session.add(activity)
        
        db.session.commit()
        
        flash(f'Work order for incident {incident.incident_number_formatted} has been approved successfully!', 'success')
        logger.info(f"Work order approved by {current_user.username} for incident {incident.incident_number}")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error approving work order: {str(e)}")
        flash('Error processing approval. Please try again.', 'error')
    
    return redirect(url_for('approval_management.dashboard'))

@bp.route('/reject/<int:approval_id>', methods=['POST'])
@login_required
def reject_request(approval_id):
    """Reject a work order request"""
    approval = WorkOrderApproval.query.get_or_404(approval_id)
    
    # Check if user has permission to reject
    if approval.approver_id != current_user.id and not current_user.has_role('admin'):
        flash('You do not have permission to reject this request.', 'error')
        return redirect(url_for('approval_management.dashboard'))
    
    # Check if already processed
    if approval.status != 'PENDING':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('approval_management.dashboard'))
    
    comments = request.form.get('comments', '')
    if not comments.strip():
        flash('Please provide comments for rejection.', 'error')
        return redirect(url_for('approval_management.dashboard'))
    
    try:
        # Reject the request
        approval.reject(current_user, comments)
        
        # Close the incident directly when rejected
        incident = approval.incident
        incident.workflow_status = 'CLOSED'
        incident.closed_at = datetime.now(timezone.utc)
        
        # Create activity log
        activity = UAVServiceActivity(
            uav_service_incident_id=incident.id,
            user_id=current_user.id,
            activity_type='wo_rejected',
            description=f'Work order rejected by {current_user.full_name}. Incident closed automatically. Reason: {comments}'
        )
        db.session.add(activity)
        
        db.session.commit()
        
        flash(f'Work order for incident {incident.incident_number_formatted} has been rejected and the incident is now closed.', 'warning')
        logger.info(f"Work order rejected by {current_user.username} for incident {incident.incident_number}")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rejecting work order: {str(e)}")
        flash('Error processing rejection. Please try again.', 'error')
    
    return redirect(url_for('approval_management.dashboard'))

@bp.route('/email-approve/<token>')
def email_approve(token):
    """Approve via email link"""
    approval = WorkOrderApproval.query.filter_by(approval_token=token).first()
    
    if not approval:
        flash('Invalid or expired approval link.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if approval.status != 'PENDING':
        flash('This request has already been processed.', 'info')
        return redirect(url_for('approval_management.view_approval', approval_id=approval.id))
    
    # Track email click
    if not approval.email_clicked_at:
        approval.email_clicked_at = datetime.now(timezone.utc)
        db.session.commit()
    
    return render_template('approval_management/email_approval.html', approval=approval, action='approve')

@bp.route('/email-reject/<token>')
def email_reject(token):
    """Reject via email link"""
    approval = WorkOrderApproval.query.filter_by(approval_token=token).first()
    
    if not approval:
        flash('Invalid or expired approval link.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if approval.status != 'PENDING':
        flash('This request has already been processed.', 'info')
        return redirect(url_for('approval_management.view_approval', approval_id=approval.id))
    
    # Track email click
    if not approval.email_clicked_at:
        approval.email_clicked_at = datetime.now(timezone.utc)
        db.session.commit()
    
    return render_template('approval_management/email_approval.html', approval=approval, action='reject')

@bp.route('/email-process/<token>', methods=['POST'])
def process_email_approval(token):
    """Process approval/rejection from email"""
    approval = WorkOrderApproval.query.filter_by(approval_token=token).first()
    
    if not approval:
        flash('Invalid or expired approval link.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if approval.status != 'PENDING':
        flash('This request has already been processed.', 'info')
        return redirect(url_for('approval_management.view_approval', approval_id=approval.id))
    
    action = request.form.get('action')
    comments = request.form.get('comments', '')
    
    try:
        if action == 'approve':
            approval.approve(approval.approver, comments)
            incident = approval.incident
            incident.workflow_status = 'WO_APPROVED'
            
            activity = UAVServiceActivity(
                uav_service_incident_id=incident.id,
                user_id=approval.approver_id,
                activity_type='wo_approved',
                description=f'Work order approved via email by {approval.approver.full_name}. Ready to initiate repair. Comments: {comments}' if comments else f'Work order approved via email by {approval.approver.full_name}. Ready to initiate repair.'
            )
            
            flash(f'Work order for incident {incident.incident_number_formatted} has been approved successfully! Ready to initiate repair.', 'success')
            
        elif action == 'reject':
            if not comments.strip():
                flash('Please provide comments for rejection.', 'error')
                return render_template('approval_management/email_approval.html', approval=approval, action='reject')
            
            approval.reject(approval.approver, comments)
            incident = approval.incident
            incident.workflow_status = 'CLOSED'
            incident.closed_at = datetime.now(timezone.utc)
            
            activity = UAVServiceActivity(
                uav_service_incident_id=incident.id,
                user_id=approval.approver_id,
                activity_type='wo_rejected',
                description=f'Work order rejected via email by {approval.approver.full_name}. Incident closed automatically. Reason: {comments}'
            )
            
            flash(f'Work order for incident {incident.incident_number_formatted} has been rejected and the incident is now closed.', 'warning')
        
        db.session.add(activity)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing email approval: {str(e)}")
        flash('Error processing approval. Please try again.', 'error')
    
    return redirect(url_for('approval_management.view_approval', approval_id=approval.id))

@bp.route('/view/<int:approval_id>')
@login_required
def view_approval(approval_id):
    """View approval details"""
    approval = WorkOrderApproval.query.get_or_404(approval_id)
    
    # Check if user has permission to view
    if (approval.approver_id != current_user.id and 
        approval.requested_by_id != current_user.id and 
        not current_user.has_role('admin')):
        flash('You do not have permission to view this approval.', 'error')
        return redirect(url_for('approval_management.dashboard'))
    
    return render_template('approval_management/view_approval.html', approval=approval)

@bp.route('/api/stats')
@login_required
def approval_stats():
    """Get approval statistics for dashboard"""
    if not current_user.has_role('admin') and not current_user.has_role('manager'):
        return jsonify({'error': 'Access denied'}), 403
    
    # Get stats for current user
    user_pending = WorkOrderApproval.query.filter_by(
        approver_id=current_user.id, 
        status='PENDING'
    ).count()
    
    user_approved = WorkOrderApproval.query.filter_by(
        approver_id=current_user.id, 
        status='APPROVED'
    ).count()
    
    user_rejected = WorkOrderApproval.query.filter_by(
        approver_id=current_user.id, 
        status='REJECTED'
    ).count()
    
    # Get system-wide stats (for admins)
    system_stats = None
    if current_user.has_role('admin'):
        system_pending = WorkOrderApproval.query.filter_by(status='PENDING').count()
        system_approved = WorkOrderApproval.query.filter_by(status='APPROVED').count()
        system_rejected = WorkOrderApproval.query.filter_by(status='REJECTED').count()
        
        system_stats = {
            'pending': system_pending,
            'approved': system_approved,
            'rejected': system_rejected,
            'total': system_pending + system_approved + system_rejected
        }
    
    return jsonify({
        'user_stats': {
            'pending': user_pending,
            'approved': user_approved,
            'rejected': user_rejected,
            'total': user_pending + user_approved + user_rejected
        },
        'system_stats': system_stats
    })
