"""
Service Management Routes
"""

from datetime import datetime, timezone, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, and_, func
from app import db
from app.service import bp
from app.service.forms import (ServiceCategoryForm, ServiceIncidentForm, ServiceIncidentUpdateForm,
                             ServicePartForm, ServiceActivityForm, ServiceSoftwareUpdateForm,
                             ServiceTemplateForm, ServiceSearchForm, ServiceStatusUpdateForm)
from app.models import (ServiceCategory, ServiceIncident, ServicePart, ServiceActivity,
                       ServiceSoftwareUpdate, ServiceTemplate, Product, User, InventoryItem,
                       WorkOrder, InventoryTransaction)


@bp.route('/')
@login_required
def dashboard():
    """Service management dashboard"""
    # Service statistics
    total_incidents = ServiceIncident.query.count()
    open_incidents = ServiceIncident.query.filter(
        ServiceIncident.status.notin_(['COMPLETED', 'CLOSED'])
    ).count()
    overdue_incidents = ServiceIncident.query.filter(
        and_(
            ServiceIncident.estimated_completion_date < datetime.now(timezone.utc),
            ServiceIncident.status.notin_(['COMPLETED', 'CLOSED'])
        )
    ).count()
    completed_this_month = ServiceIncident.query.filter(
        and_(
            ServiceIncident.status == 'COMPLETED',
            ServiceIncident.actual_completion_date >= datetime.now().replace(day=1)
        )
    ).count()
    
    # Recent incidents
    recent_incidents = ServiceIncident.query.order_by(
        desc(ServiceIncident.created_at)
    ).limit(10).all()
    
    # Priority distribution
    priority_stats = db.session.query(
        ServiceIncident.priority,
        func.count(ServiceIncident.id).label('count')
    ).filter(
        ServiceIncident.status.notin_(['COMPLETED', 'CLOSED'])
    ).group_by(ServiceIncident.priority).all()
    
    # Technician workload
    technician_workload = db.session.query(
        User.first_name, User.last_name,
        func.count(ServiceIncident.id).label('active_incidents')
    ).outerjoin(ServiceIncident, and_(
        ServiceIncident.technician_id == User.id,
        ServiceIncident.status.notin_(['COMPLETED', 'CLOSED'])
    )).group_by(User.id, User.first_name, User.last_name).all()
    
    # Service categories with incident counts
    category_stats = db.session.query(
        ServiceCategory.name,
        func.count(ServiceIncident.id).label('incident_count')
    ).outerjoin(ServiceIncident).group_by(ServiceCategory.id, ServiceCategory.name).all()
    
    return render_template('service/dashboard.html',
                         total_incidents=total_incidents,
                         open_incidents=open_incidents,
                         overdue_incidents=overdue_incidents,
                         completed_this_month=completed_this_month,
                         recent_incidents=recent_incidents,
                         priority_stats=priority_stats,
                         technician_workload=technician_workload,
                         category_stats=category_stats)


@bp.route('/incidents')
@login_required
def incidents():
    """List all service incidents with filtering"""
    form = ServiceSearchForm()
    
    # Populate form choices
    form.technician_id.choices = [(0, 'All Technicians')] + [
        (u.id, f"{u.first_name} {u.last_name}") 
        for u in User.query.order_by(User.first_name).all()
    ]
    form.category_id.choices = [(0, 'All Categories')] + [
        (c.id, c.name) 
        for c in ServiceCategory.query.order_by(ServiceCategory.name).all()
    ]
    
    # Build query
    query = ServiceIncident.query
    
    # Apply filters
    if form.validate_on_submit():
        if form.search_term.data:
            search = f"%{form.search_term.data}%"
            query = query.filter(or_(
                ServiceIncident.title.ilike(search),
                ServiceIncident.incident_number.ilike(search),
                ServiceIncident.customer_name.ilike(search),
                ServiceIncident.description.ilike(search)
            ))
        
        if form.status.data:
            query = query.filter(ServiceIncident.status == form.status.data)
        
        if form.incident_type.data:
            query = query.filter(ServiceIncident.incident_type == form.incident_type.data)
        
        if form.priority.data:
            query = query.filter(ServiceIncident.priority == form.priority.data)
        
        if form.technician_id.data and form.technician_id.data != 0:
            query = query.filter(ServiceIncident.technician_id == form.technician_id.data)
        
        if form.category_id.data and form.category_id.data != 0:
            query = query.filter(ServiceIncident.category_id == form.category_id.data)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    incidents = query.order_by(desc(ServiceIncident.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('service/incidents.html', incidents=incidents, form=form)


@bp.route('/incidents/create', methods=['GET', 'POST'])
@login_required
def create_incident():
    """Create new service incident"""
    form = ServiceIncidentForm()
    
    # Populate form choices
    form.product_id.choices = [(p.id, f"{p.product_name} ({p.product_code})") 
                              for p in Product.query.filter_by(is_active=True).order_by(Product.product_name).all()]
    form.category_id.choices = [(0, 'Select Category')] + [(c.id, c.name) 
                                                          for c in ServiceCategory.query.order_by(ServiceCategory.name).all()]
    form.technician_id.choices = [(0, 'Unassigned')] + [(u.id, f"{u.first_name} {u.last_name}") 
                                                        for u in User.query.order_by(User.first_name).all()]
    
    if form.validate_on_submit():
        # Generate incident number
        incident_number = f"SVC-{datetime.now().strftime('%Y%m%d')}-{ServiceIncident.query.count() + 1:04d}"
        
        incident = ServiceIncident(
            incident_number=incident_number,
            title=form.title.data,
            description=form.description.data,
            symptoms=form.symptoms.data,
            incident_type=form.incident_type.data,
            priority=form.priority.data,
            product_id=form.product_id.data,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            technician_id=form.technician_id.data if form.technician_id.data != 0 else None,
            customer_name=form.customer_name.data,
            customer_email=form.customer_email.data,
            customer_phone=form.customer_phone.data,
            customer_address=form.customer_address.data,
            estimated_completion_date=form.estimated_completion_date.data,
            estimated_cost=form.estimated_cost.data,
            software_version_before=form.software_version_before.data,
            firmware_version_before=form.firmware_version_before.data,
            internal_notes=form.internal_notes.data,
            customer_notes=form.customer_notes.data,
            created_by_id=current_user.id
        )
        
        # Initialize workflow
        incident.initialize_workflow()
        
        db.session.add(incident)
        db.session.flush()  # Get the incident ID
        
        # Add initial activity
        incident.add_activity(
            user=current_user,
            activity_type='received',
            description=f'Service incident created: {incident.title}'
        )
        
        # Auto-generate work order if category requires it
        if incident.service_category and (incident.service_category.requires_parts or 
                                        incident.service_category.requires_software_update or
                                        incident.service_category.requires_firmware_update):
            work_order = incident.generate_work_order()
            if work_order:
                incident.add_activity(
                    user=current_user,
                    activity_type='workorder_created',
                    description=f'Work order {work_order.work_order_number} created automatically'
                )
        
        db.session.commit()
        flash(f'Service incident {incident.incident_number_formatted} created successfully.', 'success')
        return redirect(url_for('service.view_incident', id=incident.id))
    
    return render_template('service/create_incident.html', form=form)


@bp.route('/incidents/<int:id>')
@login_required
def view_incident(id):
    """View service incident details"""
    incident = ServiceIncident.query.get_or_404(id)
    
    # Get related data
    activities = incident.service_activities.order_by(desc(ServiceActivity.timestamp)).all()
    parts = incident.service_parts.all()
    software_updates = incident.software_updates.all()
    
    return render_template('service/view_incident.html', 
                         incident=incident, 
                         activities=activities,
                         parts=parts,
                         software_updates=software_updates)


@bp.route('/incidents/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_incident(id):
    """Edit service incident"""
    incident = ServiceIncident.query.get_or_404(id)
    form = ServiceIncidentUpdateForm(obj=incident)
    
    if form.validate_on_submit():
        old_status = incident.status
        
        # Update incident
        form.populate_obj(incident)
        incident.updated_at = datetime.now(timezone.utc)
        
        # Add activity if status changed
        if old_status != incident.status:
            incident.add_activity(
                user=current_user,
                activity_type='status_changed',
                description=f'Status changed from {old_status} to {incident.status}'
            )
        
        # Set completion date if status is completed
        if incident.status == 'COMPLETED' and not incident.actual_completion_date:
            incident.actual_completion_date = datetime.now(timezone.utc)
            incident.add_activity(
                user=current_user,
                activity_type='completed',
                description='Service incident marked as completed'
            )
        
        db.session.commit()
        flash('Service incident updated successfully.', 'success')
        return redirect(url_for('service.view_incident', id=incident.id))
    
    return render_template('service/edit_incident.html', form=form, incident=incident)


@bp.route('/incidents/<int:id>/status', methods=['GET', 'POST'])
@login_required
def update_status(id):
    """Update incident status with step-by-step workflow"""
    incident = ServiceIncident.query.get_or_404(id)
    form = ServiceStatusUpdateForm()
    
    # Set current status step as default
    if not form.status_step.data:
        form.status_step.data = incident.status_step
    
    if form.validate_on_submit():
        if 'advance_status' in request.form:
            # Advance to next step
            if incident.advance_status(current_user, form.status_notes.data):
                flash('Status advanced to next step successfully.', 'success')
            else:
                flash('Cannot advance status further.', 'warning')
                
        elif 'set_specific_status' in request.form:
            # Set specific status step
            if incident.set_status_step(form.status_step.data, current_user, form.status_notes.data):
                flash('Status updated successfully.', 'success')
            else:
                flash('Invalid status step.', 'error')
                
        elif 'add_notes_only' in request.form:
            # Add notes without changing status
            if form.status_notes.data:
                incident.add_activity(
                    user=current_user,
                    activity_type='notes_added',
                    description=form.status_notes.data
                )
                flash('Notes added successfully.', 'success')
        
        # Update additional fields based on current step
        if form.diagnosis.data and incident.status_step >= 3:
            incident.diagnosis = form.diagnosis.data
        if form.estimated_cost.data and incident.status_step >= 4:
            incident.estimated_cost = form.estimated_cost.data
        if form.testing_results.data and incident.status_step >= 7:
            if not incident.internal_notes:
                incident.internal_notes = ""
            incident.internal_notes += f"\n\nTesting Results: {form.testing_results.data}"
        if form.completion_notes.data and incident.status_step >= 8:
            incident.resolution_summary = form.completion_notes.data
        
        db.session.commit()
        return redirect(url_for('service.view_incident', id=incident.id))
    
    return render_template('service/update_status.html', form=form, incident=incident)


@bp.route('/incidents/<int:id>/status/advance', methods=['POST'])
@login_required
def advance_status(id):
    """Quick advance status to next step (AJAX endpoint)"""
    incident = ServiceIncident.query.get_or_404(id)
    
    if incident.advance_status(current_user):
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Status advanced successfully',
            'current_step': incident.status_step,
            'status_label': incident.current_status_info['label'],
            'progress_percentage': incident.progress_percentage
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Cannot advance status further'
        }), 400


@bp.route('/incidents/<int:id>/add_part', methods=['GET', 'POST'])
@login_required
def add_part(id):
    """Add part to service incident"""
    incident = ServiceIncident.query.get_or_404(id)
    form = ServicePartForm()
    
    # Populate inventory items
    form.inventory_item_id.choices = [(i.id, f"{i.name} ({i.part_number}) - Stock: {i.quantity_in_stock}") 
                                     for i in InventoryItem.query.filter_by(is_active=True).order_by(InventoryItem.name).all()]
    
    if form.validate_on_submit():
        inventory_item = InventoryItem.query.get(form.inventory_item_id.data)
        
        # Check if enough stock
        if inventory_item.quantity_in_stock < form.quantity_used.data:
            flash(f'Insufficient stock. Available: {inventory_item.quantity_in_stock}', 'error')
            return render_template('service/add_part.html', form=form, incident=incident)
        
        service_part = ServicePart(
            service_incident_id=incident.id,
            inventory_item_id=form.inventory_item_id.data,
            quantity_used=form.quantity_used.data,
            unit_cost=form.unit_cost.data or inventory_item.unit_cost,
            total_cost=(form.unit_cost.data or inventory_item.unit_cost) * form.quantity_used.data,
            notes=form.notes.data,
            status='REQUIRED'
        )
        
        db.session.add(service_part)
        
        # Add activity
        incident.add_activity(
            user=current_user,
            activity_type='parts_added',
            description=f'Added {form.quantity_used.data}x {inventory_item.name} to service'
        )
        
        db.session.commit()
        flash('Part added to service incident successfully.', 'success')
        return redirect(url_for('service.view_incident', id=incident.id))
    
    return render_template('service/add_part.html', form=form, incident=incident)


@bp.route('/incidents/<int:id>/install_part/<int:part_id>')
@login_required
def install_part(id, part_id):
    """Mark part as installed"""
    incident = ServiceIncident.query.get_or_404(id)
    service_part = ServicePart.query.get_or_404(part_id)
    
    if service_part.service_incident_id != incident.id:
        flash('Invalid part for this incident.', 'error')
        return redirect(url_for('service.view_incident', id=incident.id))
    
    # Install the part (this updates inventory)
    service_part.install_part(current_user)
    
    # Add activity
    incident.add_activity(
        user=current_user,
        activity_type='part_installed',
        description=f'Installed {service_part.quantity_used}x {service_part.inventory_item.name}'
    )
    
    db.session.commit()
    flash('Part marked as installed and inventory updated.', 'success')
    return redirect(url_for('service.view_incident', id=incident.id))


@bp.route('/incidents/<int:id>/add_activity', methods=['GET', 'POST'])
@login_required
def add_activity(id):
    """Add activity to service incident"""
    incident = ServiceIncident.query.get_or_404(id)
    form = ServiceActivityForm()
    
    if form.validate_on_submit():
        incident.add_activity(
            user=current_user,
            activity_type=form.activity_type.data,
            description=form.description.data
        )
        
        # Set is_customer_visible from form
        activity = incident.service_activities.order_by(desc(ServiceActivity.timestamp)).first()
        activity.is_customer_visible = form.is_customer_visible.data
        
        db.session.commit()
        flash('Activity added successfully.', 'success')
        return redirect(url_for('service.view_incident', id=incident.id))
    
    return render_template('service/add_activity.html', form=form, incident=incident)


@bp.route('/incidents/<int:id>/add_software_update', methods=['GET', 'POST'])
@login_required
def add_software_update(id):
    """Add software/firmware update to service incident"""
    incident = ServiceIncident.query.get_or_404(id)
    form = ServiceSoftwareUpdateForm()
    
    if form.validate_on_submit():
        software_update = ServiceSoftwareUpdate(
            service_incident_id=incident.id,
            update_type=form.update_type.data,
            component_name=form.component_name.data,
            version_before=form.version_before.data,
            version_after=form.version_after.data,
            update_method=form.update_method.data,
            update_notes=form.update_notes.data,
            performed_by_id=current_user.id,
            status='PENDING'
        )
        
        db.session.add(software_update)
        
        # Add activity
        incident.add_activity(
            user=current_user,
            activity_type='software_update_planned',
            description=f'Planned {form.update_type.data.lower()} update for {form.component_name.data} to version {form.version_after.data}'
        )
        
        db.session.commit()
        flash('Software update recorded successfully.', 'success')
        return redirect(url_for('service.view_incident', id=incident.id))
    
    return render_template('service/add_software_update.html', form=form, incident=incident)


@bp.route('/incidents/<int:id>/generate_workorder')
@login_required
def generate_workorder(id):
    """Generate work order for service incident"""
    incident = ServiceIncident.query.get_or_404(id)
    
    if incident.related_workorder_id:
        flash('Work order already exists for this incident.', 'info')
        return redirect(url_for('workorders.view_workorder', id=incident.related_workorder_id))
    
    work_order = incident.generate_work_order()
    db.session.commit()
    
    flash(f'Work order {work_order.work_order_number} created successfully.', 'success')
    return redirect(url_for('workorders.view_workorder', id=work_order.id))


@bp.route('/categories')
@login_required
def categories():
    """List service categories"""
    categories = ServiceCategory.query.order_by(ServiceCategory.name).all()
    return render_template('service/categories.html', categories=categories)


@bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create new service category"""
    form = ServiceCategoryForm()
    
    if form.validate_on_submit():
        category = ServiceCategory(
            name=form.name.data,
            description=form.description.data,
            category_type=form.category_type.data,
            severity_level=form.severity_level.data,
            estimated_service_time=form.estimated_service_time.data,
            requires_parts=form.requires_parts.data,
            requires_software_update=form.requires_software_update.data,
            requires_firmware_update=form.requires_firmware_update.data
        )
        
        db.session.add(category)
        db.session.commit()
        flash(f'Service category "{category.name}" created successfully.', 'success')
        return redirect(url_for('service.categories'))
    
    return render_template('service/create_category.html', form=form)


@bp.route('/templates')
@login_required
def templates():
    """List service templates"""
    templates = ServiceTemplate.query.order_by(ServiceTemplate.name).all()
    return render_template('service/templates.html', templates=templates)


@bp.route('/templates/create', methods=['GET', 'POST'])
@login_required
def create_template():
    """Create new service template"""
    form = ServiceTemplateForm()
    
    # Populate categories
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) 
                                                      for c in ServiceCategory.query.order_by(ServiceCategory.name).all()]
    
    if form.validate_on_submit():
        template = ServiceTemplate(
            name=form.name.data,
            description=form.description.data,
            template_type=form.template_type.data,
            category_id=form.category_id.data if form.category_id.data != 0 else None,
            estimated_time=form.estimated_time.data,
            procedure_steps=form.procedure_steps.data,
            required_tools=form.required_tools.data,
            safety_notes=form.safety_notes.data,
            applicable_models=form.applicable_models.data,
            created_by_id=current_user.id
        )
        
        db.session.add(template)
        db.session.commit()
        flash(f'Service template "{template.name}" created successfully.', 'success')
        return redirect(url_for('service.templates'))
    
    return render_template('service/create_template.html', form=form)


@bp.route('/templates/<int:id>')
@login_required
def view_template(id):
    """View service template details"""
    template = ServiceTemplate.query.get_or_404(id)
    return render_template('service/view_template.html', template=template)


@bp.route('/templates/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_template(id):
    """Edit service template"""
    template = ServiceTemplate.query.get_or_404(id)
    form = ServiceTemplateForm(obj=template)
    
    # Populate categories
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) 
                                                      for c in ServiceCategory.query.order_by(ServiceCategory.name).all()]
    
    if form.validate_on_submit():
        template.name = form.name.data
        template.description = form.description.data
        template.template_type = form.template_type.data
        template.category_id = form.category_id.data if form.category_id.data != 0 else None
        template.estimated_time = form.estimated_time.data
        template.procedure_steps = form.procedure_steps.data
        template.required_tools = form.required_tools.data
        template.safety_notes = form.safety_notes.data
        template.applicable_models = form.applicable_models.data
        template.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        flash(f'Service template "{template.name}" updated successfully.', 'success')
        return redirect(url_for('service.view_template', id=template.id))
    
    return render_template('service/edit_template.html', form=form, template=template)


@bp.route('/templates/<int:id>/delete', methods=['POST'])
@login_required
def delete_template(id):
    """Delete service template"""
    template = ServiceTemplate.query.get_or_404(id)
    
    try:
        db.session.delete(template)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Template deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/incidents/<int:id>/status', methods=['POST'])
@login_required
def update_incident_status(id):
    """API endpoint to update incident status"""
    incident = ServiceIncident.query.get_or_404(id)
    new_status = request.json.get('status')
    
    if new_status not in ['RECEIVED', 'DIAGNOSED', 'IN_PROGRESS', 'WAITING_PARTS', 'COMPLETED', 'CLOSED']:
        return jsonify({'error': 'Invalid status'}), 400
    
    old_status = incident.status
    incident.status = new_status
    incident.updated_at = datetime.now(timezone.utc)
    
    # Add activity
    incident.add_activity(
        user=current_user,
        activity_type='status_changed',
        description=f'Status changed from {old_status} to {new_status}'
    )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'new_status': new_status,
        'incident_number': incident.incident_number_formatted
    })


@bp.route('/reports')
@login_required
def reports():
    """Service reports and analytics"""
    # Service metrics for the last 30 days
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    # Incident trends
    daily_incidents = db.session.query(
        func.date(ServiceIncident.created_at).label('date'),
        func.count(ServiceIncident.id).label('count')
    ).filter(
        ServiceIncident.created_at >= thirty_days_ago
    ).group_by(func.date(ServiceIncident.created_at)).all()
    
    # Service time analysis
    completed_incidents = ServiceIncident.query.filter(
        and_(
            ServiceIncident.status == 'COMPLETED',
            ServiceIncident.actual_completion_date.isnot(None),
            ServiceIncident.created_at >= thirty_days_ago
        )
    ).all()
    
    avg_service_time = 0
    if completed_incidents:
        total_days = sum(incident.service_duration_days for incident in completed_incidents)
        avg_service_time = total_days / len(completed_incidents)
    
    # Category performance
    category_performance = db.session.query(
        ServiceCategory.name,
        func.count(ServiceIncident.id).label('total_incidents'),
        func.avg(
            func.julianday(ServiceIncident.actual_completion_date) - 
            func.julianday(ServiceIncident.received_date)
        ).label('avg_days')
    ).join(ServiceIncident).filter(
        ServiceIncident.status == 'COMPLETED'
    ).group_by(ServiceCategory.id, ServiceCategory.name).all()
    
    return render_template('service/reports.html',
                         daily_incidents=daily_incidents,
                         avg_service_time=avg_service_time,
                         category_performance=category_performance,
                         completed_incidents=len(completed_incidents))
