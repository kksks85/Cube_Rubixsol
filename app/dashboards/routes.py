from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.dashboards import bp
from app.dashboards.forms import DashboardForm, DashboardWidgetForm, DashboardLayoutForm, ReportForm
from app.models import Dashboard, DashboardWidget, UserDashboardPreference, Report, User
import json
from datetime import datetime, timezone


@bp.route('/')
@login_required
def index():
    """List all dashboards accessible to user"""
    user_dashboards = Dashboard.query.filter_by(created_by_id=current_user.id).all()
    public_dashboards = Dashboard.query.filter_by(is_public=True).all()
    
    # Debug: Print dashboard info
    print(f"Debug - User ID: {current_user.id}")
    print(f"Debug - User dashboards count: {len(user_dashboards)}")
    print(f"Debug - Public dashboards count: {len(public_dashboards)}")
    print(f"Debug - All dashboards count: {Dashboard.query.count()}")
    
    # Get user's home dashboard preference
    home_preference = UserDashboardPreference.query.filter_by(
        user_id=current_user.id,
        is_home_dashboard=True
    ).first()
    
    return render_template('dashboards/index.html',
                         user_dashboards=user_dashboards,
                         public_dashboards=public_dashboards,
                         home_preference=home_preference)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new dashboard"""
    form = DashboardForm()
    
    if form.validate_on_submit():
        dashboard = Dashboard(
            name=form.name.data,
            description=form.description.data,
            is_public=form.is_public.data,
            created_by_id=current_user.id
        )
        
        db.session.add(dashboard)
        db.session.commit()
        
        flash(f'Dashboard "{dashboard.name}" created successfully!', 'success')
        return redirect(url_for('dashboards.view', id=dashboard.id))
    
    return render_template('dashboards/create.html', form=form)


@bp.route('/view/<int:id>')
@login_required
def view(id):
    """View a specific dashboard"""
    dashboard = Dashboard.query.get_or_404(id)
    
    # Check if user can view this dashboard
    if not dashboard.can_view(current_user):
        flash('You do not have permission to view this dashboard.', 'error')
        return redirect(url_for('dashboards.index'))
    
    # Get widgets ordered by position
    widgets = dashboard.widgets.filter_by(is_visible=True).order_by(
        DashboardWidget.position_y.asc(),
        DashboardWidget.position_x.asc()
    ).all()
    
    # Check if this is user's home dashboard
    is_home = UserDashboardPreference.query.filter_by(
        user_id=current_user.id,
        dashboard_id=dashboard.id,
        is_home_dashboard=True
    ).first() is not None
    
    return render_template('dashboards/view.html',
                         dashboard=dashboard,
                         widgets=widgets,
                         is_home=is_home,
                         can_edit=dashboard.can_edit(current_user))


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit dashboard details"""
    dashboard = Dashboard.query.get_or_404(id)
    
    if not dashboard.can_edit(current_user):
        flash('You do not have permission to edit this dashboard.', 'error')
        return redirect(url_for('dashboards.view', id=id))
    
    form = DashboardForm(obj=dashboard)
    
    if form.validate_on_submit():
        dashboard.name = form.name.data
        dashboard.description = form.description.data
        dashboard.is_public = form.is_public.data
        dashboard.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        flash('Dashboard updated successfully!', 'success')
        return redirect(url_for('dashboards.view', id=id))
    
    return render_template('dashboards/edit.html', form=form, dashboard=dashboard)


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a dashboard"""
    dashboard = Dashboard.query.get_or_404(id)
    
    if not dashboard.can_edit(current_user):
        flash('You do not have permission to delete this dashboard.', 'error')
        return redirect(url_for('dashboards.view', id=id))
    
    db.session.delete(dashboard)
    db.session.commit()
    
    flash(f'Dashboard "{dashboard.name}" deleted successfully!', 'success')
    return redirect(url_for('dashboards.index'))


@bp.route('/set-home/<int:id>', methods=['POST'])
@login_required
def set_home(id):
    """Set dashboard as user's home dashboard"""
    dashboard = Dashboard.query.get_or_404(id)
    
    if not dashboard.can_view(current_user):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    # Remove existing home dashboard preference
    UserDashboardPreference.query.filter_by(
        user_id=current_user.id,
        is_home_dashboard=True
    ).update({'is_home_dashboard': False})
    
    # Set new home dashboard
    preference = UserDashboardPreference.query.filter_by(
        user_id=current_user.id,
        dashboard_id=dashboard.id
    ).first()
    
    if not preference:
        preference = UserDashboardPreference(
            user_id=current_user.id,
            dashboard_id=dashboard.id
        )
        db.session.add(preference)
    
    preference.is_home_dashboard = True
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'"{dashboard.name}" set as home dashboard'})


@bp.route('/add-widget/<int:dashboard_id>', methods=['GET', 'POST'])
@login_required
def add_widget(dashboard_id):
    """Add a widget to dashboard"""
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    
    if not dashboard.can_edit(current_user):
        flash('You do not have permission to edit this dashboard.', 'error')
        return redirect(url_for('dashboards.view', id=dashboard_id))
    
    form = DashboardWidgetForm()
    
    # Populate report choices
    reports = Report.query.filter(
        (Report.is_public == True) | (Report.created_by_id == current_user.id)
    ).all()
    form.report_id.choices = [(0, 'Select a report...')] + [(r.id, r.name) for r in reports]
    
    if form.validate_on_submit():
        widget = DashboardWidget(
            dashboard_id=dashboard.id,
            widget_type=form.widget_type.data,
            title=form.title.data,
            position_x=form.position_x.data,
            position_y=form.position_y.data,
            width=form.width.data,
            height=form.height.data,
            report_id=form.report_id.data if form.report_id.data > 0 else None
        )
        
        db.session.add(widget)
        db.session.commit()
        
        flash('Widget added successfully!', 'success')
        return redirect(url_for('dashboards.view', id=dashboard_id))
    
    return render_template('dashboards/add_widget.html', form=form, dashboard=dashboard)


@bp.route('/edit-widget/<int:widget_id>', methods=['GET', 'POST'])
@login_required
def edit_widget(widget_id):
    """Edit a dashboard widget"""
    widget = DashboardWidget.query.get_or_404(widget_id)
    dashboard = widget.dashboard
    
    if not dashboard.can_edit(current_user):
        flash('You do not have permission to edit this widget.', 'error')
        return redirect(url_for('dashboards.view', id=dashboard.id))
    
    form = DashboardWidgetForm(obj=widget)
    
    # Populate report choices
    reports = Report.query.filter(
        (Report.is_public == True) | (Report.created_by_id == current_user.id)
    ).all()
    form.report_id.choices = [(0, 'Select a report...')] + [(r.id, r.name) for r in reports]
    
    if form.validate_on_submit():
        widget.widget_type = form.widget_type.data
        widget.title = form.title.data
        widget.position_x = form.position_x.data
        widget.position_y = form.position_y.data
        widget.width = form.width.data
        widget.height = form.height.data
        widget.report_id = form.report_id.data if form.report_id.data > 0 else None
        widget.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        flash('Widget updated successfully!', 'success')
        return redirect(url_for('dashboards.view', id=dashboard.id))
    
    return render_template('dashboards/edit_widget.html', form=form, widget=widget, dashboard=dashboard)


@bp.route('/delete-widget/<int:widget_id>', methods=['POST'])
@login_required
def delete_widget(widget_id):
    """Delete a dashboard widget"""
    widget = DashboardWidget.query.get_or_404(widget_id)
    dashboard = widget.dashboard
    
    if not dashboard.can_edit(current_user):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    db.session.delete(widget)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Widget deleted successfully'})


@bp.route('/save-layout/<int:dashboard_id>', methods=['POST'])
@login_required
def save_layout(dashboard_id):
    """Save dashboard layout (widget positions)"""
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    
    if not dashboard.can_edit(current_user):
        return jsonify({'success': False, 'message': 'Permission denied'})
    
    layout_data = request.get_json()
    
    if not layout_data or 'widgets' not in layout_data:
        return jsonify({'success': False, 'message': 'Invalid layout data'})
    
    try:
        # Update widget positions
        for widget_data in layout_data['widgets']:
            widget = DashboardWidget.query.get(widget_data['id'])
            if widget and widget.dashboard_id == dashboard.id:
                widget.position_x = widget_data['x']
                widget.position_y = widget_data['y']
                widget.width = widget_data['width']
                widget.height = widget_data['height']
        
        # Save layout configuration to dashboard
        dashboard.layout_config = json.dumps(layout_data)
        dashboard.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Layout saved successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error saving layout: {str(e)}'})


@bp.route('/reports')
@login_required
def reports():
    """List all reports accessible to user"""
    user_reports = Report.query.filter_by(created_by_id=current_user.id).all()
    public_reports = Report.query.filter_by(is_public=True).all()
    
    return render_template('dashboards/reports.html',
                         user_reports=user_reports,
                         public_reports=public_reports)


@bp.route('/reports/create', methods=['GET', 'POST'])
@login_required
def create_report():
    """Create a new report"""
    form = ReportForm()
    
    if form.validate_on_submit():
        report = Report(
            name=form.name.data,
            description=form.description.data,
            report_type=form.report_type.data,
            is_public=form.is_public.data,
            refresh_interval=form.refresh_interval.data,
            created_by_id=current_user.id
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash(f'Report "{report.name}" created successfully!', 'success')
        return redirect(url_for('dashboards.reports'))
    
    return render_template('dashboards/create_report.html', form=form)


@bp.route('/widget-data/<int:widget_id>')
@login_required
def widget_data(widget_id):
    """Get data for a specific widget"""
    widget = DashboardWidget.query.get_or_404(widget_id)
    dashboard = widget.dashboard
    
    if not dashboard.can_view(current_user):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Generate sample data based on widget type
    if widget.widget_type == 'kpi':
        data = {
            'value': 145,
            'label': widget.title,
            'change': '+12%',
            'trend': 'up'
        }
    elif widget.widget_type == 'chart':
        data = {
            'type': 'line',
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'datasets': [{
                'label': widget.title,
                'data': [10, 15, 13, 17, 20],
                'borderColor': '#007bff',
                'backgroundColor': 'rgba(0, 123, 255, 0.1)'
            }]
        }
    elif widget.widget_type == 'quick_action':
        data = {
            'actions': [
                {'name': 'New Work Order', 'url': url_for('workorders.create')},
                {'name': 'Add Product', 'url': url_for('products.create')},
                {'name': 'View Reports', 'url': url_for('dashboards.reports')}
            ]
        }
    else:
        data = {'message': f'Data for {widget.title}'}
    
    return jsonify(data)
