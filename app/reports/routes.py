"""
Reports and Analytics Routes
"""

from datetime import datetime, timezone, timedelta
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, desc, extract
import json
from app import db
from app.reports import bp
from app.models import WorkOrder, User, Priority, Status, Category, WorkOrderActivity

@bp.route('/')
@login_required
def dashboard():
    """Reports dashboard"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to view reports.', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('reports/dashboard.html', title='Reports & Analytics')

@bp.route('/workorder-summary')
@login_required
def workorder_summary():
    """Work order summary report"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to view reports.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Date range (default to last 30 days)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    # Custom date range from request
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').replace(tzinfo=timezone.utc)
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
    # Basic statistics
    total_workorders = WorkOrder.query.filter(
        WorkOrder.created_at.between(start_date, end_date)
    ).count()
    
    completed_workorders = WorkOrder.query.join(Status).filter(
        Status.is_closed,
        WorkOrder.created_at.between(start_date, end_date)
    ).count()
    
    overdue_workorders = WorkOrder.query.join(Status).filter(
        ~Status.is_closed,
        WorkOrder.due_date < datetime.now(timezone.utc),
        WorkOrder.created_at.between(start_date, end_date)
    ).count()
    
    # Average completion time
    avg_completion_time = db.session.query(
        func.avg(
            func.julianday(WorkOrder.completed_date) - func.julianday(WorkOrder.created_at)
        )
    ).join(Status).filter(
        Status.is_closed,
        WorkOrder.completed_date.isnot(None),
        WorkOrder.created_at.between(start_date, end_date)
    ).scalar() or 0
    
    # Priority breakdown
    priority_data = db.session.query(
        Priority.name,
        Priority.color,
        func.count(WorkOrder.id).label('count')
    ).join(WorkOrder).filter(
        WorkOrder.created_at.between(start_date, end_date)
    ).group_by(Priority.id, Priority.name, Priority.color).all()
    
    # Status breakdown
    status_data = db.session.query(
        Status.name,
        Status.color,
        func.count(WorkOrder.id).label('count')
    ).join(WorkOrder).filter(
        WorkOrder.created_at.between(start_date, end_date)
    ).group_by(Status.id, Status.name, Status.color).all()
    
    # Category breakdown
    category_data = db.session.query(
        Category.name,
        func.count(WorkOrder.id).label('count')
    ).join(WorkOrder).filter(
        WorkOrder.created_at.between(start_date, end_date)
    ).group_by(Category.id, Category.name).all()
    
    # Monthly trend (last 12 months)
    monthly_data = db.session.query(
        extract('year', WorkOrder.created_at).label('year'),
        extract('month', WorkOrder.created_at).label('month'),
        func.count(WorkOrder.id).label('created'),
        func.sum(func.case([(Status.is_closed, 1)], else_=0)).label('completed')
    ).join(Status).filter(
        WorkOrder.created_at >= (end_date - timedelta(days=365))
    ).group_by(
        extract('year', WorkOrder.created_at),
        extract('month', WorkOrder.created_at)
    ).order_by(
        extract('year', WorkOrder.created_at),
        extract('month', WorkOrder.created_at)
    ).all()
    
    stats = {
        'total': total_workorders,
        'completed': completed_workorders,
        'overdue': overdue_workorders,
        'completion_rate': round((completed_workorders / total_workorders * 100) if total_workorders > 0 else 0, 1),
        'avg_completion_days': round(avg_completion_time, 1) if avg_completion_time else 0
    }
    
    return render_template('reports/workorder_summary.html',
                         title='Work Order Summary',
                         stats=stats,
                         priority_data=priority_data,
                         status_data=status_data,
                         category_data=category_data,
                         monthly_data=monthly_data,
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'))

@bp.route('/user-performance')
@login_required
def user_performance():
    """User performance report"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to view reports.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Date range (default to last 30 days)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    # Custom date range from request
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').replace(tzinfo=timezone.utc)
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
    # User performance data
    user_stats = db.session.query(
        User.id,
        User.first_name,
        User.last_name,
        func.count(WorkOrder.id).label('total_assigned'),
        func.sum(func.case([(Status.is_closed, 1)], else_=0)).label('completed'),
        func.avg(WorkOrder.actual_hours).label('avg_hours'),
        func.sum(WorkOrder.actual_cost).label('total_cost')
    ).outerjoin(WorkOrder, User.id == WorkOrder.assigned_to_id).outerjoin(Status).filter(
        User.is_active == True,
        db.or_(
            WorkOrder.created_at.between(start_date, end_date),
            WorkOrder.id.is_(None)  # Include users with no work orders
        )
    ).group_by(User.id, User.first_name, User.last_name).all()
    
    # Calculate performance metrics
    performance_data = []
    for stat in user_stats:
        total = stat.total_assigned or 0
        completed = stat.completed or 0
        completion_rate = (completed / total * 100) if total > 0 else 0
        avg_hours = round(stat.avg_hours or 0, 1)
        total_cost = float(stat.total_cost or 0)
        
        performance_data.append({
            'user_id': stat.id,
            'name': f"{stat.first_name} {stat.last_name}",
            'total_assigned': total,
            'completed': completed,
            'completion_rate': round(completion_rate, 1),
            'avg_hours': avg_hours,
            'total_cost': total_cost
        })
    
    # Sort by completion rate
    performance_data.sort(key=lambda x: x['completion_rate'], reverse=True)
    
    return render_template('reports/user_performance.html',
                         title='User Performance',
                         performance_data=performance_data,
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'))

@bp.route('/cost-analysis')
@login_required
def cost_analysis():
    """Cost analysis report"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to view reports.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Date range (default to last 30 days)
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    # Custom date range from request
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').replace(tzinfo=timezone.utc)
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
    # Cost statistics
    total_estimated = db.session.query(
        func.sum(WorkOrder.cost_estimate)
    ).filter(
        WorkOrder.created_at.between(start_date, end_date)
    ).scalar() or 0
    
    total_actual = db.session.query(
        func.sum(WorkOrder.actual_cost)
    ).filter(
        WorkOrder.created_at.between(start_date, end_date)
    ).scalar() or 0
    
    # Cost by category
    category_costs = db.session.query(
        Category.name,
        func.sum(WorkOrder.cost_estimate).label('estimated'),
        func.sum(WorkOrder.actual_cost).label('actual'),
        func.count(WorkOrder.id).label('count')
    ).join(WorkOrder).filter(
        WorkOrder.created_at.between(start_date, end_date)
    ).group_by(Category.id, Category.name).all()
    
    # Cost by priority
    priority_costs = db.session.query(
        Priority.name,
        Priority.color,
        func.sum(WorkOrder.cost_estimate).label('estimated'),
        func.sum(WorkOrder.actual_cost).label('actual'),
        func.count(WorkOrder.id).label('count')
    ).join(WorkOrder).filter(
        WorkOrder.created_at.between(start_date, end_date)
    ).group_by(Priority.id, Priority.name, Priority.color).all()
    
    # Monthly cost trend
    monthly_costs = db.session.query(
        extract('year', WorkOrder.created_at).label('year'),
        extract('month', WorkOrder.created_at).label('month'),
        func.sum(WorkOrder.cost_estimate).label('estimated'),
        func.sum(WorkOrder.actual_cost).label('actual')
    ).filter(
        WorkOrder.created_at >= (end_date - timedelta(days=365))
    ).group_by(
        extract('year', WorkOrder.created_at),
        extract('month', WorkOrder.created_at)
    ).order_by(
        extract('year', WorkOrder.created_at),
        extract('month', WorkOrder.created_at)
    ).all()
    
    stats = {
        'total_estimated': float(total_estimated),
        'total_actual': float(total_actual),
        'variance': float(total_actual - total_estimated),
        'variance_percent': round(((total_actual - total_estimated) / total_estimated * 100) if total_estimated > 0 else 0, 1)
    }
    
    return render_template('reports/cost_analysis.html',
                         title='Cost Analysis',
                         stats=stats,
                         category_costs=category_costs,
                         priority_costs=priority_costs,
                         monthly_costs=monthly_costs,
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'))

@bp.route('/api/chart-data/<chart_type>')
@login_required
def chart_data(chart_type):
    """API endpoint for chart data"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').replace(tzinfo=timezone.utc)
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').replace(tzinfo=timezone.utc)
    
    if chart_type == 'priority_distribution':
        data = db.session.query(
            Priority.name,
            Priority.color,
            func.count(WorkOrder.id).label('count')
        ).join(WorkOrder).filter(
            WorkOrder.created_at.between(start_date, end_date)
        ).group_by(Priority.id, Priority.name, Priority.color).all()
        
        return jsonify({
            'labels': [d.name for d in data],
            'data': [d.count for d in data],
            'colors': [d.color for d in data]
        })
    
    elif chart_type == 'status_distribution':
        data = db.session.query(
            Status.name,
            Status.color,
            func.count(WorkOrder.id).label('count')
        ).join(WorkOrder).filter(
            WorkOrder.created_at.between(start_date, end_date)
        ).group_by(Status.id, Status.name, Status.color).all()
        
        return jsonify({
            'labels': [d.name for d in data],
            'data': [d.count for d in data],
            'colors': [d.color for d in data]
        })
    
    elif chart_type == 'monthly_trend':
        data = db.session.query(
            extract('year', WorkOrder.created_at).label('year'),
            extract('month', WorkOrder.created_at).label('month'),
            func.count(WorkOrder.id).label('created'),
            func.sum(func.case([(Status.is_closed, 1)], else_=0)).label('completed')
        ).join(Status).filter(
            WorkOrder.created_at >= (end_date - timedelta(days=365))
        ).group_by(
            extract('year', WorkOrder.created_at),
            extract('month', WorkOrder.created_at)
        ).order_by(
            extract('year', WorkOrder.created_at),
            extract('month', WorkOrder.created_at)
        ).all()
        
        labels = [f"{int(d.year)}-{int(d.month):02d}" for d in data]
        created = [d.created for d in data]
        completed = [d.completed for d in data]
        
        return jsonify({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Created',
                    'data': created,
                    'borderColor': '#007bff',
                    'backgroundColor': 'rgba(0, 123, 255, 0.1)'
                },
                {
                    'label': 'Completed',
                    'data': completed,
                    'borderColor': '#28a745',
                    'backgroundColor': 'rgba(40, 167, 69, 0.1)'
                }
            ]
        })
    
    return jsonify({'error': 'Invalid chart type'}), 400
