"""
User Management Routes
"""

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import desc
from app import db
from app.users import bp
from app.models import User, Role, WorkOrder, Status

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
    completed_workorders = user.assigned_workorders.join(Status).filter(Status.is_closed).count()
    open_workorders = user.assigned_workorders.join(Status).filter(~Status.is_closed).count()
    
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
