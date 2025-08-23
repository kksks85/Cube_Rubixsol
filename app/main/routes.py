"""
Main Application Routes
Handles dashboard, profile, and general navigation
"""

from datetime import datetime, timezone, timedelta
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from app import db
from app.main import bp
from app.models import WorkOrder, User, Priority, Status, Category, Product

@bp.route('/')
@bp.route('/index')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with overview statistics"""
    
    # Get current date for filtering
    today = datetime.now(timezone.utc)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Basic statistics
    stats = {}
    
    if current_user.has_role('admin') or current_user.has_role('manager'):
        # Admin/Manager can see all work orders
        stats['total_workorders'] = WorkOrder.query.count()
        stats['open_workorders'] = WorkOrder.query.join(Status).filter(~Status.is_closed).count()
        stats['overdue_workorders'] = WorkOrder.query.join(Status).filter(
            ~Status.is_closed,
            WorkOrder.due_date < today
        ).count()
        stats['completed_this_week'] = WorkOrder.query.join(Status).filter(
            Status.is_closed,
            WorkOrder.completed_date >= week_ago
        ).count()
        
        # Recent work orders
        recent_workorders = WorkOrder.query.order_by(desc(WorkOrder.created_at)).limit(5).all()
        
        # UAV Service Statistics
        one_month_from_now = today + timedelta(days=30)
        
        # UAVs with service due within one month
        uavs_service_due_soon = Product.query.filter(
            Product.next_service_due.isnot(None),
            Product.next_service_due <= one_month_from_now,
            Product.next_service_due >= today.date()
        ).all()
        
        # UAVs with overdue service
        uavs_service_overdue = Product.query.filter(
            Product.next_service_due.isnot(None),
            Product.next_service_due < today.date()
        ).all()
        
        stats['uavs_service_due_soon'] = len(uavs_service_due_soon)
        stats['uavs_service_overdue'] = len(uavs_service_overdue)
        
        # Priority distribution
        priority_stats = db.session.query(
            Priority.name,
            Priority.color,
            func.count(WorkOrder.id).label('count')
        ).join(WorkOrder).group_by(Priority.id, Priority.name, Priority.color).all()
        
        # Status distribution
        status_stats = db.session.query(
            Status.name,
            Status.color,
            func.count(WorkOrder.id).label('count')
        ).join(WorkOrder).group_by(Status.id, Status.name, Status.color).all()
        
    else:
        # Technicians can only see their assigned work orders
        stats['total_workorders'] = WorkOrder.query.filter_by(assigned_to_id=current_user.id).count()
        stats['open_workorders'] = WorkOrder.query.join(Status).filter(
            ~Status.is_closed,
            WorkOrder.assigned_to_id == current_user.id
        ).count()
        stats['overdue_workorders'] = WorkOrder.query.join(Status).filter(
            ~Status.is_closed,
            WorkOrder.assigned_to_id == current_user.id,
            WorkOrder.due_date < today
        ).count()
        stats['completed_this_week'] = WorkOrder.query.join(Status).filter(
            Status.is_closed,
            WorkOrder.assigned_to_id == current_user.id,
            WorkOrder.completed_date >= week_ago
        ).count()
        
        # Recent assigned work orders
        recent_workorders = WorkOrder.query.filter_by(
            assigned_to_id=current_user.id
        ).order_by(desc(WorkOrder.created_at)).limit(5).all()
        
        # UAV Service Statistics (same for all users)
        one_month_from_now = today + timedelta(days=30)
        
        # UAVs with service due within one month
        uavs_service_due_soon = Product.query.filter(
            Product.next_service_due.isnot(None),
            Product.next_service_due <= one_month_from_now,
            Product.next_service_due >= today.date()
        ).all()
        
        # UAVs with overdue service
        uavs_service_overdue = Product.query.filter(
            Product.next_service_due.isnot(None),
            Product.next_service_due < today.date()
        ).all()
        
        stats['uavs_service_due_soon'] = len(uavs_service_due_soon)
        stats['uavs_service_overdue'] = len(uavs_service_overdue)
        
        # Priority distribution for assigned work orders
        priority_stats = db.session.query(
            Priority.name,
            Priority.color,
            func.count(WorkOrder.id).label('count')
        ).join(WorkOrder).filter(
            WorkOrder.assigned_to_id == current_user.id
        ).group_by(Priority.id, Priority.name, Priority.color).all()
        
        # Status distribution for assigned work orders
        status_stats = db.session.query(
            Status.name,
            Status.color,
            func.count(WorkOrder.id).label('count')
        ).join(WorkOrder).filter(
            WorkOrder.assigned_to_id == current_user.id
        ).group_by(Status.id, Status.name, Status.color).all()
    
    # Active users count (admin/manager only)
    if current_user.has_role('admin') or current_user.has_role('manager'):
        stats['active_users'] = User.query.filter_by(is_active=True).count()
    else:
        stats['active_users'] = 0
    
    return render_template('main/dashboard.html',
                         title='Dashboard',
                         stats=stats,
                         recent_workorders=recent_workorders,
                         priority_stats=priority_stats,
                         status_stats=status_stats,
                         uavs_service_due_soon=uavs_service_due_soon,
                         uavs_service_overdue=uavs_service_overdue)

@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Calculate work order statistics for the current user
    total_assigned = current_user.assigned_workorders.count()
    
    # Get open work orders (not closed status)
    open_assigned = db.session.query(WorkOrder).join(Status).filter(
        WorkOrder.assigned_to_id == current_user.id,
        ~Status.is_closed
    ).count()
    
    workorder_stats = {
        'total_assigned': total_assigned,
        'open_assigned': open_assigned
    }
    
    return render_template('main/profile.html', 
                         title='My Profile',
                         workorder_stats=workorder_stats)

@bp.route('/help')
@login_required
def help():
    """Help and documentation page"""
    return render_template('main/help.html', title='Help & Documentation')

@bp.route('/search')
@login_required
def search():
    """Global search functionality"""
    query = request.args.get('q', '')
    
    if not query:
        flash('Please enter a search term.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    # Search work orders
    workorder_query = WorkOrder.query.filter(
        db.or_(
            WorkOrder.title.contains(query),
            WorkOrder.description.contains(query),
            WorkOrder.location.contains(query)
        )
    )
    
    # Apply access control
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        workorder_query = workorder_query.filter_by(assigned_to_id=current_user.id)
    
    workorders = workorder_query.order_by(desc(WorkOrder.created_at)).limit(20).all()
    
    # Search users (admin/manager only)
    users = []
    if current_user.has_role('admin') or current_user.has_role('manager'):
        users = User.query.filter(
            db.or_(
                User.username.contains(query),
                User.first_name.contains(query),
                User.last_name.contains(query),
                User.email.contains(query)
            )
        ).limit(10).all()
    
    return render_template('main/search_results.html',
                         title=f'Search Results for "{query}"',
                         query=query,
                         workorders=workorders,
                         users=users)
