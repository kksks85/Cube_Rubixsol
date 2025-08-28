"""
User Management Routes
"""

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import desc
from datetime import datetime
from app import db
from app.users import bp
from app.models import User, Role, WorkOrder, WorkOrderStatus, AssignmentGroup, AssignmentGroupMember, UAVServiceIncident, AssignmentRule

@bp.route('/')
@login_required
def list_users():
    """List all users (admin/manager only)"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to view users.', 'error')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.order_by(User.username).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Calculate statistics for the comprehensive dashboard
    total_users = User.query.count()
    active_users_count = User.query.filter_by(is_active=True).count()
    admin_count = User.query.join(Role).filter(Role.name == 'admin').count()
    manager_count = User.query.join(Role).filter(Role.name == 'manager').count()
    tech_count = User.query.join(Role).filter(Role.name == 'technician').count()
    
    return render_template('users/list.html', 
                         title='User Management', 
                         users=users,
                         total_users=total_users,
                         active_users_count=active_users_count,
                         admin_count=admin_count,
                         manager_count=manager_count,
                         tech_count=tech_count)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create new user (admin only)"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to create users.', 'error')
        return redirect(url_for('users.list_users'))
    
    from app.users.forms import CreateUserForm
    form = CreateUserForm()
    form.role.choices = [(r.id, r.name.title()) for r in Role.query.all()]
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role_id=form.role.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.username} has been created successfully.', 'success')
        return redirect(url_for('users.view_user', id=user.id))
    
    return render_template('users/create.html', title='Create User', form=form)

@bp.route('/<int:id>')
@login_required
def view_user(id):
    """View user profile"""
    user = User.query.get_or_404(id)
    
    # Users can view their own profile, admin/managers can view any profile
    if user.id != current_user.id and not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to view this profile.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get user's work order statistics
    total_assigned = user.assigned_workorders.count()
    completed_workorders = user.assigned_workorders.join(WorkOrder.status_detail).filter(WorkOrderStatus.is_final == True).count()
    open_workorders = user.assigned_workorders.join(WorkOrder.status_detail).filter(WorkOrderStatus.is_final == False).count()
    
    # Recent work orders
    recent_workorders = user.assigned_workorders.order_by(desc(WorkOrder.created_at)).limit(5).all()
    
    stats = {
        'total_assigned': total_assigned,
        'completed': completed_workorders,
        'open': open_workorders,
        'completion_rate': round((completed_workorders / total_assigned * 100) if total_assigned > 0 else 0, 1)
    }
    
    return render_template('users/profile.html',
                         title=f'Profile: {user.full_name}',
                         user=user,
                         stats=stats,
                         recent_workorders=recent_workorders)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    """Edit user (admin only)"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to edit users.', 'error')
        return redirect(url_for('users.view_user', id=id))
    
    user = User.query.get_or_404(id)
    
    # Prevent admin from editing their own admin status
    if user.id == current_user.id:
        flash('You cannot edit your own profile through this interface.', 'warning')
        return redirect(url_for('users.view_user', id=id))
    
    from app.auth.forms import RegistrationForm
    form = RegistrationForm(obj=user)
    form.role.choices = [(r.id, r.name.title()) for r in Role.query.all()]
    
    # Remove password validation for editing
    del form.password
    del form.password2
    
    if form.validate_on_submit():
        # Check if username/email changed and validate uniqueness
        if user.username != form.username.data:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user and existing_user.id != user.id:
                flash('Username already exists.', 'error')
                return render_template('users/edit.html', title='Edit User', form=form, user=user)
        
        if user.email != form.email.data:
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user and existing_user.id != user.id:
                flash('Email already exists.', 'error')
                return render_template('users/edit.html', title='Edit User', form=form, user=user)
        
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone = form.phone.data
        user.role_id = form.role.data
        
        db.session.commit()
        
        flash(f'User {user.username} has been updated successfully.', 'success')
        return redirect(url_for('users.view_user', id=user.id))
    
    # Set current values
    form.role.data = user.role_id
    
    return render_template('users/edit.html', title='Edit User', form=form, user=user)

@bp.route('/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status(id):
    """Activate/deactivate user (admin only)"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to modify user status.', 'error')
        return redirect(url_for('users.list_users'))
    
    user = User.query.get_or_404(id)
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('users.list_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    
    return redirect(url_for('users.list_users'))

@bp.route('/<int:id>/reset-password', methods=['POST'])
@login_required
def reset_user_password(id):
    """Reset user password (admin only)"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to reset passwords.', 'error')
        return redirect(url_for('users.view_user', id=id))
    
    user = User.query.get_or_404(id)
    
    # Generate temporary password
    import secrets
    temp_password = secrets.token_urlsafe(12)
    user.set_password(temp_password)
    
    db.session.commit()
    
    flash(f'Password reset for {user.username}. Temporary password: {temp_password}', 'success')
    return redirect(url_for('users.view_user', id=user.id))

@bp.route('/api/user/<int:id>/toggle-status', methods=['POST'])
@login_required
def api_toggle_user_status(id):
    """API endpoint to toggle user status"""
    if not current_user.has_role('admin'):
        return {'success': False, 'message': 'Permission denied'}, 403
    
    user = User.query.get_or_404(id)
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        return {'success': False, 'message': 'Cannot deactivate your own account'}, 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    return {'success': True, 'message': f'User {user.username} has been {status}'}

@bp.route('/api/user/<int:id>/reset-password', methods=['POST'])
@login_required
def api_reset_user_password(id):
    """API endpoint to reset user password"""
    if not current_user.has_role('admin'):
        return {'success': False, 'message': 'Permission denied'}, 403
    
    user = User.query.get_or_404(id)
    
    # Generate temporary password
    import secrets
    temp_password = secrets.token_urlsafe(12)
    user.set_password(temp_password)
    
    db.session.commit()
    
    return {'success': True, 'message': f'Password reset. Temporary password: {temp_password}'}

# Assignment Groups Routes
@bp.route('/assignment-groups')
@login_required
def assignment_groups():
    """List all assignment groups"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to view assignment groups.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get all assignment groups with statistics
    groups = AssignmentGroup.query.order_by(AssignmentGroup.name).all()
    
    # Calculate statistics
    total_groups = len(groups)
    active_groups = len([g for g in groups if g.is_active])
    total_members = sum([g.member_count for g in groups])
    
    stats = {
        'total_groups': total_groups,
        'active_groups': active_groups,
        'total_members': total_members,
        'pending_assignments': 0  # This can be calculated based on work orders
    }
    
    return render_template('users/assignment_groups.html', 
                         title='Assignment Groups', 
                         groups=groups, 
                         stats=stats)

@bp.route('/assignment-groups/create', methods=['GET', 'POST'])
@login_required
def create_assignment_group():
    """Create new assignment group"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to create assignment groups.', 'error')
        return redirect(url_for('users.assignment_groups'))
    
    if request.method == 'POST':
        try:
            # Get form data
            group_name = request.form.get('group_name', '').strip()
            group_code = request.form.get('group_code', '').strip()
            description = request.form.get('description', '').strip()
            department = request.form.get('department', '').strip()
            priority_level = request.form.get('priority_level', 'standard')
            
            # Get boolean settings
            auto_assign = bool(request.form.get('auto_assign'))
            round_robin = bool(request.form.get('round_robin'))
            notification_enabled = bool(request.form.get('notification_enabled'))
            is_active = bool(request.form.get('is_active'))
            
            # Get multi-select values
            work_order_types = request.form.getlist('work_order_types')
            priority_filter = request.form.getlist('priority_filter')
            
            # Validation
            if not group_name:
                flash('Group name is required.', 'error')
                return render_template('users/create_assignment_group.html', title='Create Assignment Group')
            
            if not group_code:
                flash('Group code is required.', 'error')
                return render_template('users/create_assignment_group.html', title='Create Assignment Group')
            
            # Check if group code already exists
            existing_group = AssignmentGroup.query.filter_by(code=group_code).first()
            if existing_group:
                flash('Group code already exists. Please choose a different code.', 'error')
                return render_template('users/create_assignment_group.html', title='Create Assignment Group')
            
            # Create new assignment group
            assignment_group = AssignmentGroup(
                name=group_name,
                code=group_code,
                description=description,
                department=department,
                priority_level=priority_level,
                auto_assign=auto_assign,
                round_robin=round_robin,
                notification_enabled=notification_enabled,
                is_active=is_active,
                created_by_id=current_user.id
            )
            
            # Set work order types and priority filters
            assignment_group.set_work_order_types(work_order_types)
            assignment_group.set_priority_filter(priority_filter)
            
            # Save to database
            db.session.add(assignment_group)
            db.session.commit()
            
            flash(f'Assignment group "{group_name}" has been created successfully!', 'success')
            return redirect(url_for('users.assignment_groups'))
            
        except Exception as e:
            flash(f'Error creating assignment group: {str(e)}', 'error')
            return render_template('users/create_assignment_group.html', title='Create Assignment Group')
    
    return render_template('users/create_assignment_group.html', title='Create Assignment Group')

@bp.route('/assignment-groups/members')
@login_required
def manage_group_members():
    """Manage assignment group members"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to manage group members.', 'error')
        return redirect(url_for('users.assignment_groups'))
    
    # Get all assignment groups
    groups = AssignmentGroup.query.filter_by(is_active=True).order_by(AssignmentGroup.name).all()
    
    # Get all users who can be added to groups (excluding already assigned ones for now)
    available_users = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()
    
    return render_template('users/manage_group_members.html', 
                         title='Manage Group Members',
                         groups=groups,
                         available_users=available_users)

@bp.route('/assignment-groups/permissions')
@login_required
def group_permissions():
    """Manage group permissions"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to manage group permissions.', 'error')
        return redirect(url_for('users.assignment_groups'))
    
    return render_template('users/group_permissions.html', title='Group Permissions')

# Assignment Rules Routes
@bp.route('/assignment-rules')
@login_required
def assignment_rules():
    """List all assignment rules"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to view assignment rules.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Fetch assignment rules from database
    rules = AssignmentRule.query.order_by(AssignmentRule.priority, AssignmentRule.created_at.desc()).all()
    
    # Calculate statistics
    total_rules = len(rules)
    active_rules = len([r for r in rules if r.is_active]) if rules else 0
    rules_triggered_today = sum([1 for r in rules if r.last_triggered_at and 
                                r.last_triggered_at.date() == datetime.now().date()]) if rules else 0
    
    stats = {
        'total_rules': total_rules,
        'active_rules': active_rules,
        'rules_triggered_today': rules_triggered_today,
        'avg_response_time': 0  # Would calculate from metrics
    }
    
    return render_template('users/assignment_rules.html', 
                         title='Assignment Rules',
                         rules=rules,
                         total_rules=total_rules,
                         stats=stats)

@bp.route('/assignment-rules/create', methods=['GET', 'POST'])
@login_required
def create_assignment_rule():
    """Create new assignment rule"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to create assignment rules.', 'error')
        return redirect(url_for('users.assignment_rules'))
    
    if request.method == 'POST':
        try:
            # Get form data
            rule_name = request.form.get('rule_name', '').strip()
            rule_priority = request.form.get('rule_priority')
            description = request.form.get('description', '').strip()
            
            # Rule conditions
            incident_category = request.form.get('incident_category', '').strip()
            priority_condition = request.form.get('priority_condition', '').strip()
            department_condition = request.form.get('department_condition', '').strip()
            location_condition = request.form.get('location_condition', '').strip()
            tag_condition = request.form.get('tag_condition', '').strip()
            time_condition = request.form.get('time_condition', '').strip()
            
            # Assignment actions
            assignment_type = request.form.get('assignment_type', '').strip()
            target_user = request.form.get('target_user')
            target_group = request.form.get('target_group')
            fallback_assignment = request.form.get('fallback_assignment', '').strip()
            notification_template = request.form.get('notification_template', '').strip()
            
            # Rule settings
            is_active = bool(request.form.get('is_active'))
            auto_escalate = bool(request.form.get('auto_escalate'))
            send_notification = bool(request.form.get('send_notification'))
            log_activity = bool(request.form.get('log_activity'))
            escalation_time = request.form.get('escalation_time')
            max_assignments = request.form.get('max_assignments')
            
            # Validation
            if not rule_name:
                flash('Rule name is required.', 'error')
                return render_template('users/create_assignment_rule.html', 
                                     title='Create Assignment Rule',
                                     available_users=User.query.filter_by(is_active=True).all(),
                                     assignment_groups=AssignmentGroup.query.filter_by(is_active=True).all())
            
            if not rule_priority:
                flash('Rule priority is required.', 'error')
                return render_template('users/create_assignment_rule.html', 
                                     title='Create Assignment Rule',
                                     available_users=User.query.filter_by(is_active=True).all(),
                                     assignment_groups=AssignmentGroup.query.filter_by(is_active=True).all())
            
            if not assignment_type:
                flash('Assignment type is required.', 'error')
                return render_template('users/create_assignment_rule.html', 
                                     title='Create Assignment Rule',
                                     available_users=User.query.filter_by(is_active=True).all(),
                                     assignment_groups=AssignmentGroup.query.filter_by(is_active=True).all())
            
            # Build rule configuration (would be stored in database)
            rule_config = {
                'conditions': {
                    'incident_category': incident_category or None,
                    'priority': priority_condition or None,
                    'department': department_condition or None,
                    'location': location_condition or None,
                    'tags': tag_condition.split(',') if tag_condition else [],
                    'time': time_condition or None
                },
                'actions': {
                    'assignment_type': assignment_type,
                    'target_user_id': int(target_user) if target_user else None,
                    'target_group_id': int(target_group) if target_group else None,
                    'fallback': fallback_assignment or None,
                    'notification_template': notification_template or 'default'
                },
                'settings': {
                    'is_active': is_active,
                    'auto_escalate': auto_escalate,
                    'send_notification': send_notification,
                    'log_activity': log_activity,
                    'escalation_time': int(escalation_time) if escalation_time else 60,
                    'max_assignments': int(max_assignments) if max_assignments else 10
                }
            }
            
            # Create and save the assignment rule
            assignment_rule = AssignmentRule(
                name=rule_name,
                description=description,
                priority=int(rule_priority),
                is_active=is_active,
                conditions=rule_config['conditions'],
                actions=rule_config['actions'],
                settings=rule_config['settings'],
                created_by=current_user.id
            )
            
            db.session.add(assignment_rule)
            db.session.commit()
            
            flash(f'Assignment rule "{rule_name}" created successfully!', 'success')
            flash(f'Priority: {rule_priority}, Type: {assignment_type}', 'info')
            flash(f'Active: {is_active}, Notifications: {send_notification}', 'info')
            
            if incident_category:
                flash(f'Applies to: {incident_category} incidents', 'info')
            
            if target_user:
                user = User.query.get(target_user)
                if user:
                    flash(f'Assigns to user: {user.full_name}', 'info')
            
            if target_group:
                group = AssignmentGroup.query.get(target_group)
                if group:
                    flash(f'Assigns to group: {group.name}', 'info')
            
            return redirect(url_for('users.assignment_rules'))
            
        except Exception as e:
            flash(f'Error creating assignment rule: {str(e)}', 'error')
            return render_template('users/create_assignment_rule.html', 
                                 title='Create Assignment Rule',
                                 available_users=User.query.filter_by(is_active=True).all(),
                                 assignment_groups=AssignmentGroup.query.filter_by(is_active=True).all())
    
    # GET request - show form
    available_users = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()
    assignment_groups = AssignmentGroup.query.filter_by(is_active=True).order_by(AssignmentGroup.name).all()
    
    return render_template('users/create_assignment_rule.html', 
                         title='Create Assignment Rule',
                         available_users=available_users,
                         assignment_groups=assignment_groups)

@bp.route('/assignment-rules/templates')
@login_required
def rule_templates():
    """View assignment rule templates"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to view rule templates.', 'error')
        return redirect(url_for('users.assignment_rules'))
    
    return render_template('users/rule_templates.html', title='Assignment Rule Templates')

@bp.route('/assignment-rules/test')
@login_required
def test_assignment_rules():
    """Test assignment rules"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to test assignment rules.', 'error')
        return redirect(url_for('users.assignment_rules'))
    
    return render_template('users/test_assignment_rules.html', title='Test Assignment Rules')


# AJAX Routes for Assignment Group Member Management
@bp.route('/assignment-groups/<int:group_id>/members', methods=['GET'])
@login_required
def get_group_members(group_id):
    """Get members of a specific group (AJAX)"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        return {'error': 'Permission denied'}, 403
    
    group = AssignmentGroup.query.get_or_404(group_id)
    members = []
    
    for membership in group.members.filter_by(is_active=True).all():
        members.append({
            'id': membership.id,
            'user_id': membership.user_id,
            'user_name': membership.user.full_name,
            'username': membership.user.username,
            'email': membership.user.email,
            'role': membership.user.role.name if membership.user.role else 'N/A',
            'department': getattr(membership.user, 'department', 'N/A'),
            'is_leader': membership.is_leader,
            'joined_at': membership.joined_at.strftime('%Y-%m-%d') if membership.joined_at else 'N/A'
        })
    
    return {'members': members, 'total': len(members)}

@bp.route('/assignment-groups/<int:group_id>/members', methods=['POST'])
@login_required
def add_group_member(group_id):
    """Add member to assignment group (AJAX)"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        return {'error': 'Permission denied'}, 403
    
    try:
        group = AssignmentGroup.query.get_or_404(group_id)
        user_id = request.json.get('user_id')
        is_leader = request.json.get('is_leader', False)
        
        if not user_id:
            return {'error': 'User ID is required'}, 400
        
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        
        # Check if user is already a member
        existing_membership = AssignmentGroupMember.query.filter_by(
            group_id=group_id, user_id=user_id
        ).first()
        
        if existing_membership:
            if existing_membership.is_active:
                return {'error': 'User is already a member of this group'}, 400
            else:
                # Reactivate membership
                existing_membership.is_active = True
                existing_membership.is_leader = is_leader
        else:
            # Create new membership
            membership = AssignmentGroupMember(
                group_id=group_id,
                user_id=user_id,
                is_leader=is_leader
            )
            db.session.add(membership)
        
        db.session.commit()
        
        return {
            'success': True, 
            'message': f'{user.full_name} has been added to the group successfully!'
        }
        
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error adding member: {str(e)}'}, 500

@bp.route('/assignment-groups/<int:group_id>/members/<int:member_id>', methods=['DELETE'])
@login_required
def remove_group_member(group_id, member_id):
    """Remove member from assignment group (AJAX)"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        return {'error': 'Permission denied'}, 403
    
    try:
        membership = AssignmentGroupMember.query.filter_by(
            id=member_id, group_id=group_id
        ).first_or_404()
        
        user_name = membership.user.full_name
        
        # Soft delete - mark as inactive
        membership.is_active = False
        db.session.commit()
        
        return {
            'success': True,
            'message': f'{user_name} has been removed from the group successfully!'
        }
        
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error removing member: {str(e)}'}, 500

@bp.route('/assignment-groups/<int:group_id>/members/<int:member_id>/toggle-leader', methods=['POST'])
@login_required
def toggle_member_leader(group_id, member_id):
    """Toggle member leader status (AJAX)"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        return {'error': 'Permission denied'}, 403
    
    try:
        membership = AssignmentGroupMember.query.filter_by(
            id=member_id, group_id=group_id, is_active=True
        ).first_or_404()
        
        # Toggle leader status
        membership.is_leader = not membership.is_leader
        db.session.commit()
        
        status = 'promoted to leader' if membership.is_leader else 'removed from leadership'
        
        return {
            'success': True,
            'is_leader': membership.is_leader,
            'message': f'{membership.user.full_name} has been {status}!'
        }
        
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error updating member: {str(e)}'}, 500
