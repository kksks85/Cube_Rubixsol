from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import joinedload
import json

from app.uav_service import bp
from app.uav_service.forms import (UAVServiceIncidentForm, DiagnosisForm, RepairMaintenanceForm,
                                  QualityCheckForm, PreventiveMaintenanceForm, MaintenanceScheduleForm)
from app.models import (UAVServiceIncident, UAVServiceActivity, UAVMaintenanceSchedule, 
                       User, Product, WorkOrder, InventoryItem, InventoryTransaction, 
                       WorkOrderPart, AssignmentGroup, AssignmentRule, AssignmentGroupMember, 
                       WorkOrderApproval, db)


def apply_assignment_rules(incident):
    """Apply assignment rules to determine assignment group and user"""
    # Get active assignment rules ordered by priority
    rules = AssignmentRule.query.filter_by(is_active=True).order_by(AssignmentRule.priority).all()
    
    for rule in rules:
        if not rule.conditions:
            continue
            
        # Check if rule conditions match the incident
        conditions_match = True
        
        # Check incident category
        if rule.conditions.get('incident_category'):
            if incident.incident_category != rule.conditions['incident_category']:
                conditions_match = False
                
        # Check priority
        if rule.conditions.get('priority'):
            if incident.priority != rule.conditions['priority']:
                conditions_match = False
                
        # Check service department  
        if rule.conditions.get('department'):
            # This would need to be added to incident model or derived from other fields
            conditions_match = True  # For now, always match department
            
        if conditions_match and rule.actions:
            # Update rule statistics
            rule.times_triggered += 1
            rule.last_triggered_at = datetime.now(timezone.utc)
            
            # Apply assignment action
            assignment_type = rule.actions.get('assignment_type')
            
            if assignment_type == 'assignment_group':
                group_id = rule.actions.get('target_group_id')
                if group_id:
                    group = AssignmentGroup.query.get(group_id)
                    if group and group.is_active:
                        return {'assignment_group_id': group_id, 'assigned_to_id': None}
                        
            elif assignment_type == 'specific_user':
                user_id = rule.actions.get('target_user_id')
                if user_id:
                    user = User.query.get(user_id)
                    if user and user.is_active:
                        return {'assignment_group_id': None, 'assigned_to_id': user_id}
                        
            elif assignment_type == 'round_robin':
                group_id = rule.actions.get('target_group_id')
                if group_id:
                    # Get users from the group and assign to least recently assigned
                    members = AssignmentGroupMember.query.filter_by(
                        group_id=group_id, is_active=True
                    ).join(User).filter(User.is_active == True).all()
                    
                    if members:
                        # For now, just assign to first available user
                        return {'assignment_group_id': group_id, 'assigned_to_id': members[0].user_id}
            
            # If rule matched but couldn't assign, continue to next rule
    
    return {'assignment_group_id': None, 'assigned_to_id': None}


@bp.route('/api/user-lookup')
@login_required
def api_user_lookup():
    """API endpoint to lookup users for customer selection"""
    try:
        search_term = request.args.get('q', '').strip()
        if len(search_term) < 2:
            return jsonify({'users': []})
        
        # Search users by name, username, or email
        users = User.query.filter(
            db.or_(
                User.first_name.ilike(f'%{search_term}%'),
                User.last_name.ilike(f'%{search_term}%'),
                User.username.ilike(f'%{search_term}%'),
                User.email.ilike(f'%{search_term}%')
            ),
            User.is_active == True
        ).limit(10).all()
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'name': user.full_name,
                'username': user.username,
                'email': user.email,
                'phone': user.phone or '',
                'display_name': f"{user.full_name} ({user.username}) - {user.email}"
            })
        
        return jsonify({'users': user_list})
        
    except Exception as e:
        current_app.logger.error(f"Error in user lookup: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@bp.route('/api/assignment-group-users/<int:group_id>')
@login_required
def get_assignment_group_users(group_id):
    """API endpoint to get users in an assignment group"""
    try:
        group = AssignmentGroup.query.get_or_404(group_id)
        
        # Get active members of the group
        members = AssignmentGroupMember.query.filter_by(
            group_id=group_id, is_active=True
        ).join(User).filter(User.is_active == True).all()
        
        users_data = []
        for member in members:
            users_data.append({
                'id': member.user.id,
                'full_name': member.user.full_name,
                'username': member.user.username,
                'is_leader': member.is_leader
            })
        
        return jsonify({
            'group_name': group.name,
            'users': users_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching assignment group users: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@bp.route('/api/product-lookup/<serial_number>')
@login_required
def api_product_lookup(serial_number):
    """API endpoint to lookup product details by serial number"""
    try:
        # Search for product by serial number with eager loading
        product = Product.query.options(joinedload(Product.owner_company)).filter_by(serial_number=serial_number).first()
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get owner company name safely
        owner_company_name = 'Unknown'
        try:
            if product.owner_company:
                owner_company_name = product.owner_company.name
        except Exception as e:
            current_app.logger.warning(f"Error accessing owner_company: {str(e)}")
        
        # Get the last service date from the product's last_serviced field
        last_service_date = None
        try:
            if product.last_serviced:
                last_service_date = product.last_serviced.strftime('%Y-%m-%d')
            else:
                # Fallback: Check UAV service incidents for this serial number
                last_incident = UAVServiceIncident.query.filter_by(
                    serial_number=serial_number
                ).order_by(UAVServiceIncident.created_at.desc()).first()
                
                if last_incident and hasattr(last_incident, 'last_service_date') and last_incident.last_service_date:
                    last_service_date = last_incident.last_service_date.strftime('%Y-%m-%d')
                elif last_incident and hasattr(last_incident, 'created_at') and last_incident.created_at:
                    # Use incident creation date as fallback
                    last_service_date = last_incident.created_at.strftime('%Y-%m-%d')
        except Exception as e:
            current_app.logger.warning(f"Error getting last service date: {str(e)}")
        
        # Get category name safely
        category_name = 'Unknown'
        try:
            if hasattr(product, 'product_category') and product.product_category:
                category_name = product.product_category.name
        except Exception as e:
            current_app.logger.warning(f"Error accessing product_category: {str(e)}")
        
        return jsonify({
            'success': True,
            'product_name': product.product_name or 'Unknown Product',
            'owner_company': owner_company_name,
            'last_service_date': last_service_date,
            'product_code': product.product_code or '',
            'category': category_name
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in product lookup for serial {serial_number}: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@bp.route('/incidents')
@login_required
def incident_list():
    """List all UAV service incidents"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    
    query = UAVServiceIncident.query
    
    if status_filter != 'all':
        query = query.filter_by(workflow_status=status_filter)
    
    if category_filter != 'all':
        query = query.filter_by(incident_category=category_filter)
    
    incidents = query.order_by(UAVServiceIncident.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('uav_service/incident_list.html', incidents=incidents,
                         status_filter=status_filter, category_filter=category_filter)


@bp.route('/incidents/create', methods=['GET', 'POST'])
@login_required
def create_incident():
    """Create new UAV service incident - Only registered users can create incidents"""
    # Ensure only active users can create incidents
    if not current_user.is_active:
        flash('Only active users can create service incidents.', 'error')
        return redirect(url_for('uav_service.dashboard'))
    
    form = UAVServiceIncidentForm()
    
    if form.validate_on_submit():
        # Validate that customer_user_id is provided and valid
        customer_user_id = form.customer_user_id.data
        if not customer_user_id:
            flash('Please select a valid registered user as customer.', 'error')
            return render_template('uav_service/create_incident.html', form=form)
        
        # Verify the customer user exists and is active
        customer_user = User.query.filter_by(id=customer_user_id, is_active=True).first()
        if not customer_user:
            flash('Selected customer user is not valid or inactive.', 'error')
            return render_template('uav_service/create_incident.html', form=form)
        
        # Set SLA hours based on category
        sla_hours = {
            'EXPRESS': {'response': 4, 'resolution': 24},
            'STANDARD': {'response': 24, 'resolution': 72},
            'ECONOMY': {'response': 48, 'resolution': 168}
        }
        
        sla_config = sla_hours.get(form.sla_category.data, sla_hours['STANDARD'])
        
        incident = UAVServiceIncident(
            incident_number=UAVServiceIncident.generate_incident_number(),
            title=form.title.data,
            description=form.description.data,
            incident_category=form.incident_category.data,
            priority=form.priority.data,
            # Use customer user information
            customer_name=customer_user.full_name,
            customer_email=customer_user.email,
            customer_phone=customer_user.phone or '',
            customer_address=form.customer_address.data,
            customer_user_id=customer_user.id,  # Store customer user reference
            # UAV Equipment Details
            serial_number=form.serial_number.data,
            product_name=form.product_name.data,
            owner_company=form.owner_company.data,
            last_service_date=form.last_service_date.data,
            # Legacy fields for backward compatibility
            uav_model=form.product_name.data or 'Unknown',
            uav_serial_number=form.serial_number.data,
            sla_category=form.sla_category.data,
            sla_response_hours=sla_config['response'],
            sla_resolution_hours=sla_config['resolution'],
            is_warranty_service=form.is_warranty_service.data,
            created_by_id=current_user.id
        )
        
        db.session.add(incident)
        db.session.commit()
        
        # Create initial activity log
        activity = UAVServiceActivity(
            uav_service_incident_id=incident.id,
            user_id=current_user.id,
            activity_type='incident_created',
            description=f'UAV service incident created: {incident.incident_category} - {incident.title}'
        )
        db.session.add(activity)
        db.session.commit()
        
        flash(f'UAV service incident {incident.incident_number} created successfully!', 'success')
        return redirect(url_for('uav_service.view_incident', id=incident.id))
    
    return render_template('uav_service/create_incident.html', form=form)


@bp.route('/incidents/<int:id>')
@login_required
def view_incident(id):
    """View UAV service incident details"""
    incident = UAVServiceIncident.query.get_or_404(id)
    activities = UAVServiceActivity.query.filter_by(uav_service_incident_id=id).order_by(UAVServiceActivity.timestamp.desc()).all()
    
    # Get available inventory for the product
    inventory_items = []
    if incident.product_name or incident.uav_model:
        from app.models import InventoryItem
        product_name = incident.product_name or incident.uav_model
        
        # Search for inventory items compatible with this UAV model
        inventory_items = InventoryItem.query.filter(
            db.and_(
                InventoryItem.is_active == True,
                db.or_(
                    InventoryItem.compatible_uav_models.like(f'%{product_name}%'),
                    InventoryItem.compatible_uav_models.like('%ALL%'),
                    InventoryItem.compatible_uav_models.is_(None)  # Generic parts
                )
            )
        ).order_by(InventoryItem.name).all()
    
    return render_template('uav_service/view_incident.html', 
                         incident=incident, 
                         activities=activities,
                         inventory_items=inventory_items)


@bp.route('/api/parts-lookup')
@login_required
def api_parts_lookup():
    """API endpoint to lookup parts filtered by UAV/product compatibility"""
    try:
        search_term = request.args.get('q', '').strip()
        product_name = request.args.get('product_name', '').strip()
        
        if len(search_term) < 2:
            return jsonify({'parts': []})
        
        # Import here to avoid circular imports
        from app.models import InventoryItem, InventoryCategory
        
        # Base query for active parts
        query = InventoryItem.query.filter(InventoryItem.is_active == True)
        
        # Filter by search term (part number or name)
        query = query.filter(
            db.or_(
                InventoryItem.part_number.ilike(f'%{search_term}%'),
                InventoryItem.name.ilike(f'%{search_term}%')
            )
        )
        
        # Filter by UAV/product compatibility if product name provided
        if product_name:
            # Filter parts compatible with the UAV model/product
            query = query.filter(
                db.or_(
                    InventoryItem.compatible_uav_models.ilike(f'%{product_name}%'),
                    InventoryItem.compatible_uav_models.is_(None),  # Universal parts
                    InventoryItem.compatible_uav_models == ''  # Universal parts
                )
            )
        
        # Get results with category information
        parts = query.join(InventoryCategory, isouter=True).limit(15).all()
        
        parts_list = []
        for part in parts:
            parts_list.append({
                'id': part.id,
                'part_number': part.part_number,
                'name': part.name,
                'category': part.category.name if part.category else 'Uncategorized',
                'in_stock': part.quantity_in_stock,
                'unit_cost': float(part.unit_cost) if part.unit_cost else 0.0,
                'display_name': f"{part.part_number} - {part.name} (Stock: {part.quantity_in_stock})"
            })
        
        return jsonify({
            'success': True,
            'parts': parts_list
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in parts lookup: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@bp.route('/api/compatible-parts')
@login_required
def api_compatible_parts():
    """API endpoint to get parts compatible with a specific UAV model"""
    try:
        uav_model = request.args.get('uav_model', '').strip()
        
        if not uav_model:
            return jsonify({'success': False, 'error': 'UAV model is required'})
        
        # Import here to avoid circular imports
        from app.models import InventoryItem, InventoryCategory
        
        # Query for active parts compatible with the UAV model
        query = InventoryItem.query.filter(InventoryItem.is_active == True)
        
        # Filter by UAV compatibility
        query = query.filter(
            db.or_(
                InventoryItem.compatible_uav_models.ilike(f'%{uav_model}%'),
                InventoryItem.compatible_uav_models.is_(None),  # Universal parts
                InventoryItem.compatible_uav_models == ''  # Universal parts
            )
        )
        
        # Get results with category information, ordered by category then part number
        parts = query.join(InventoryCategory, isouter=True)\
                    .order_by(InventoryCategory.name, InventoryItem.part_number)\
                    .all()
        
        parts_list = []
        for part in parts:
            parts_list.append({
                'id': part.id,
                'part_number': part.part_number,
                'name': part.name,
                'category_name': part.category.name if part.category else 'Uncategorized',
                'quantity_in_stock': part.quantity_in_stock,
                'manufacturer': part.manufacturer,
                'unit_cost': float(part.unit_cost) if part.unit_cost else 0.0,
                'minimum_stock_level': part.minimum_stock_level,
                'is_low_stock': part.quantity_in_stock <= part.minimum_stock_level,
                'compatible_models': part.compatible_uav_models
            })
        
        return jsonify({
            'success': True,
            'parts': parts_list,
            'count': len(parts_list),
            'uav_model': uav_model
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching compatible parts: {str(e)}")
        return jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500


@bp.route('/incidents/<int:id>/diagnosis', methods=['GET', 'POST'])
@login_required
def diagnosis_workflow(id):
    """Handle diagnosis and work order creation"""
    print(f"DEBUG: Request method: {request.method}")
    if request.method == 'POST':
        print(f"DEBUG: POST request received for incident {id}")
        print(f"DEBUG: Form data keys: {list(request.form.keys())}")
        print(f"DEBUG: Form data: {dict(request.form)}")
    
    incident = UAVServiceIncident.query.get_or_404(id)
    form = DiagnosisForm()
    
    # Check if this is accessed via stage navigation to preserve data
    preserve_data = request.args.get('preserve_data', 'false') == 'true'
    
    # Populate assignment group choices
    assignment_groups = AssignmentGroup.query.filter_by(is_active=True).order_by(AssignmentGroup.name).all()
    form.assignment_group_id.choices = [('', '-- Select Assignment Group --')] + [
        (str(group.id), f"{group.name} ({group.code})") for group in assignment_groups
    ]
    
    # Initially populate with all active users
    users = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()
    form.assigned_to_id.choices = [('', '-- Select User --')] + [
        (str(user.id), f"{user.full_name} ({user.username})") for user in users
    ]
    
    # Pre-populate form with existing data when accessed via stage navigation or on GET
    if request.method == 'GET':
        # Always preserve existing incident data when loading the form
        if incident.diagnostic_findings:
            form.diagnostic_findings.data = incident.diagnostic_findings
        if incident.work_order_type:
            form.work_order_type.data = incident.work_order_type
        if incident.estimated_cost:
            form.estimated_cost.data = incident.estimated_cost
        if incident.technician_notes:
            form.technician_notes.data = incident.technician_notes
        if incident.parts_requested is not None:
            form.parts_requested.data = incident.parts_requested
            
        # Find existing work order for this incident to populate assignment fields
        existing_workorder = WorkOrder.query.filter_by(
            uav_service_incident_id=incident.id
        ).first()
        
        if existing_workorder:
            # Pre-populate assignment fields from existing work order
            if existing_workorder.assignment_group_id:
                form.assignment_group_id.data = str(existing_workorder.assignment_group_id)
            if existing_workorder.assigned_to_id:
                form.assigned_to_id.data = str(existing_workorder.assigned_to_id)
        else:
            # Apply assignment rules only if no existing work order
            assignment_suggestion = apply_assignment_rules(incident)
            if assignment_suggestion['assignment_group_id']:
                form.assignment_group_id.data = str(assignment_suggestion['assignment_group_id'])
            if assignment_suggestion['assigned_to_id']:
                form.assigned_to_id.data = str(assignment_suggestion['assigned_to_id'])
        
        # Show preservation message if accessed via stage navigation
        if preserve_data:
            flash('Editing diagnosis stage. All existing data has been preserved and pre-populated in the form.', 'info')
    
    if form.validate_on_submit():
        print(f"DEBUG: Form validation passed for incident {incident.id}")
        print(f"DEBUG: Form data - diagnostic_findings: {form.diagnostic_findings.data}")
        print(f"DEBUG: Form data - work_order_type: {form.work_order_type.data}")
        print(f"DEBUG: Form data - assignment_group_id: {form.assignment_group_id.data}")
        print(f"DEBUG: Form data - assigned_to_id: {form.assigned_to_id.data}")
        
        incident.diagnostic_checklist_completed = True
        incident.diagnostic_findings = form.diagnostic_findings.data
        incident.work_order_type = form.work_order_type.data
        incident.estimated_cost = form.estimated_cost.data
        incident.parts_requested = form.parts_requested.data
        incident.technician_notes = form.technician_notes.data
        incident.technician_id = current_user.id
        
        # Handle multiple parts request from the new system
        requested_parts_data = request.form.get('requested_parts_data', '')
        multiple_parts_processed = False
        
        if requested_parts_data:
            try:
                requested_parts = json.loads(requested_parts_data)
                if requested_parts and len(requested_parts) > 0:
                    multiple_parts_processed = True
                    
                    for part_data in requested_parts:
                        part = InventoryItem.query.get(int(part_data['id']))
                        if part:
                            quantity_needed = int(part_data['quantity'])
                            
                            # Check if sufficient stock is available
                            if part.quantity_in_stock >= quantity_needed:
                                # Reduce inventory quantity
                                part.quantity_in_stock -= quantity_needed
                                
                                # Create inventory transaction record
                                transaction = InventoryTransaction(
                                    transaction_type='OUT',
                                    quantity=quantity_needed,
                                    unit_cost=part.unit_cost,
                                    total_cost=part.unit_cost * quantity_needed,
                                    reference_type='UAV_SERVICE',
                                    reference_id=str(incident.id),
                                    notes=f'Parts used for UAV Service Incident #{incident.incident_number_formatted}' + 
                                          (f' - {part_data.get("notes", "")}' if part_data.get("notes") else ''),
                                    item_id=part.id,
                                    created_by_id=current_user.id
                                )
                                db.session.add(transaction)
                                
                                flash(f'Parts allocated: {quantity_needed} units of {part.name} (Part #{part.part_number})', 'success')
                            else:
                                flash(f'Insufficient stock for {part.name}. Available: {part.quantity_in_stock}, Needed: {quantity_needed}', 'warning')
                        else:
                            flash(f'Part with ID {part_data["id"]} not found', 'error')
                            
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                flash(f'Error processing parts data: {str(e)}', 'error')
        
        # Handle multiple parts from enhanced form
        if not multiple_parts_processed:
            # Check if parts are required
            parts_required = request.form.get('parts_required') == '1'
            
            if parts_required:
                # Handle JSON data for multiple parts
                parts_data = request.form.get('parts_data', '')
                if parts_data:
                    try:
                        parts_list = json.loads(parts_data)
                        parts_processed_count = 0
                        
                        for part_info in parts_list:
                            part_id = part_info.get('part_id')
                            quantity_needed = int(part_info.get('quantity', 0))
                            part_notes = part_info.get('notes', '')
                            
                            if part_id and quantity_needed > 0:
                                part = InventoryItem.query.get(part_id)
                                
                                if part:
                                    # Check if sufficient stock is available
                                    if part.quantity_in_stock >= quantity_needed:
                                        # Reduce inventory quantity
                                        part.quantity_in_stock -= quantity_needed
                                        
                                        # Create inventory transaction record
                                        transaction = InventoryTransaction(
                                            transaction_type='OUT',
                                            quantity=quantity_needed,
                                            unit_cost=part.unit_cost,
                                            total_cost=part.unit_cost * quantity_needed,
                                            reference_type='UAV_SERVICE',
                                            reference_id=str(incident.id),
                                            notes=f'Parts used for UAV Service Incident #{incident.incident_number_formatted}' +
                                                  (f' - {part_notes}' if part_notes else ''),
                                            item_id=part.id,
                                            created_by_id=current_user.id
                                        )
                                        db.session.add(transaction)
                                        
                                        flash(f'Parts allocated: {quantity_needed} units of {part.name} (Part #{part.part_number})', 'success')
                                        parts_processed_count += 1
                                    else:
                                        flash(f'Insufficient stock for {part.name}. Available: {part.quantity_in_stock}, Needed: {quantity_needed}', 'warning')
                                else:
                                    flash(f'Part with ID {part_id} not found', 'error')
                        
                        if parts_processed_count > 0:
                            multiple_parts_processed = True
                            
                    except (json.JSONDecodeError, ValueError) as e:
                        flash(f'Error processing parts data: {str(e)}', 'error')
                
                # Fallback to single part handling
                if not multiple_parts_processed:
                    # Get part details from simple form
                    part_number = request.form.get('part_number', '').strip()
                    part_quantity = request.form.get('part_quantity', '').strip()
                    part_notes = request.form.get('part_notes', '').strip()
                    
                    if part_number and part_quantity:
                        try:
                            quantity_needed = int(part_quantity)
                            part = InventoryItem.query.filter_by(part_number=part_number).first()
                            
                            if part:
                                # Check if sufficient stock is available
                                if part.quantity_in_stock >= quantity_needed:
                                    # Reduce inventory quantity
                                    part.quantity_in_stock -= quantity_needed
                                    
                                    # Create inventory transaction record
                                    transaction = InventoryTransaction(
                                        transaction_type='OUT',
                                        quantity=quantity_needed,
                                        unit_cost=part.unit_cost,
                                        total_cost=part.unit_cost * quantity_needed,
                                        reference_type='UAV_SERVICE',
                                        reference_id=str(incident.id),
                                        notes=f'Parts used for UAV Service Incident #{incident.incident_number_formatted}' +
                                              (f' - {part_notes}' if part_notes else ''),
                                        item_id=part.id,
                                        created_by_id=current_user.id
                                    )
                                    db.session.add(transaction)
                                    
                                    flash(f'Parts allocated: {quantity_needed} units of {part.name} (Part #{part.part_number})', 'success')
                                    multiple_parts_processed = True
                                else:
                                    flash(f'Insufficient stock for {part.name}. Available: {part.quantity_in_stock}, Needed: {quantity_needed}', 'warning')
                            else:
                                flash(f'Part number {part_number} not found in inventory', 'warning')
                        except ValueError:
                            flash(f'Invalid quantity for part {part_number}', 'error')
                    elif parts_required:
                        flash('Please add at least one part when parts are required', 'warning')
            
            # Fallback - check older field names for backwards compatibility
            if not multiple_parts_processed:
                # First check the simple single part form (legacy)
                simple_part_number = request.form.get('simple_part_number', '').strip()
                simple_part_quantity = request.form.get('simple_part_quantity', '').strip()
                simple_parts_notes = request.form.get('simple_parts_notes', '').strip()
                
                if simple_part_number and simple_part_quantity:
                    try:
                        quantity_needed = int(simple_part_quantity)
                        part = InventoryItem.query.filter_by(part_number=simple_part_number).first()
                        
                        if part:
                            # Check if sufficient stock is available
                            if part.quantity_in_stock >= quantity_needed:
                                # Reduce inventory quantity
                                part.quantity_in_stock -= quantity_needed
                                
                                # Create inventory transaction record
                                transaction = InventoryTransaction(
                                    transaction_type='OUT',
                                    quantity=quantity_needed,
                                    unit_cost=part.unit_cost,
                                    total_cost=part.unit_cost * quantity_needed,
                                    reference_type='UAV_SERVICE',
                                    reference_id=str(incident.id),
                                    notes=f'Parts used for UAV Service Incident #{incident.incident_number_formatted}' +
                                          (f' - {simple_parts_notes}' if simple_parts_notes else ''),
                                    item_id=part.id,
                                    created_by_id=current_user.id
                                )
                                db.session.add(transaction)
                                
                                flash(f'Parts allocated: {quantity_needed} units of {part.name} (Part #{part.part_number})', 'success')
                                multiple_parts_processed = True
                            else:
                                flash(f'Insufficient stock for {part.name}. Available: {part.quantity_in_stock}, Needed: {quantity_needed}', 'warning')
                        else:
                            flash(f'Part number {simple_part_number} not found in inventory', 'warning')
                    except ValueError:
                        flash(f'Invalid quantity for part {simple_part_number}', 'error')
            
            # If no simple part, try the multi-part format (fallback)
            if not multiple_parts_processed:
                parts_processed = 0
                for i in range(1, 4):  # Handle up to 3 parts
                    part_number_field = f'part_number_{i}'
                    part_name_field = f'part_name_{i}'
                    quantity_field = f'quantity_{i}'
                    
                    part_number = request.form.get(part_number_field, '').strip()
                    part_name = request.form.get(part_name_field, '').strip()
                    quantity_str = request.form.get(quantity_field, '').strip()
                    
                    if part_number and quantity_str:
                        try:
                            quantity_needed = int(quantity_str)
                            part = InventoryItem.query.filter_by(part_number=part_number).first()
                            
                            if part:
                                # Check if sufficient stock is available
                                if part.quantity_in_stock >= quantity_needed:
                                    # Reduce inventory quantity
                                    part.quantity_in_stock -= quantity_needed
                                    
                                    # Create inventory transaction record
                                    transaction = InventoryTransaction(
                                        transaction_type='OUT',
                                        quantity=quantity_needed,
                                        unit_cost=part.unit_cost,
                                        total_cost=part.unit_cost * quantity_needed,
                                        reference_type='UAV_SERVICE',
                                        reference_id=str(incident.id),
                                        notes=f'Parts used for UAV Service Incident #{incident.incident_number_formatted}',
                                        item_id=part.id,
                                        created_by_id=current_user.id
                                    )
                                    db.session.add(transaction)
                                    
                                    flash(f'Parts allocated: {quantity_needed} units of {part.name} (Part #{part.part_number})', 'success')
                                    parts_processed += 1
                                else:
                                    flash(f'Insufficient stock for {part.name}. Available: {part.quantity_in_stock}, Needed: {quantity_needed}', 'warning')
                            else:
                                flash(f'Part number {part_number} not found in inventory', 'warning')
                        except ValueError:
                            flash(f'Invalid quantity for part {part_number}', 'error')
                
                if parts_processed > 0:
                    multiple_parts_processed = True
        
        # Handle legacy single part request (fallback for existing functionality)
        if not multiple_parts_processed and form.part_number.data and form.quantity_needed.data:
            part = InventoryItem.query.filter_by(part_number=form.part_number.data).first()
            if part:
                quantity_needed = int(form.quantity_needed.data)
                
                # Check if sufficient stock is available
                if part.quantity_in_stock >= quantity_needed:
                    # Reduce inventory quantity
                    part.quantity_in_stock -= quantity_needed
                    
                    # Create inventory transaction record
                    transaction = InventoryTransaction(
                        transaction_type='OUT',
                        quantity=quantity_needed,
                        unit_cost=part.unit_cost,
                        total_cost=part.unit_cost * quantity_needed,
                        reference_type='UAV_SERVICE',
                        reference_id=str(incident.id),
                        notes=f'Parts used for UAV Service Incident #{incident.incident_number_formatted}',
                        item_id=part.id,
                        created_by_id=current_user.id
                    )
                    db.session.add(transaction)
                    
                    flash(f'Parts allocated: {quantity_needed} units of {part.name} (Part #{part.part_number})', 'success')
                else:
                    flash(f'Insufficient stock for {part.name}. Available: {part.quantity_in_stock}, Needed: {quantity_needed}', 'warning')

        # Advance workflow to WO_AUTHORIZATION and create approval request
        incident.advance_workflow(current_user, f'Diagnosis completed: {form.diagnostic_findings.data}')
        
        # Find Kapil Kushwaha as the approver
        kapil_user = User.query.filter(
            db.or_(
                User.username == 'kapil',
                User.username == 'kapil.kushwaha',
                User.email.like('%kapil%')
            )
        ).first()
        
        if not kapil_user:
            # Fallback to first admin user if Kapil not found
            kapil_user = User.query.filter_by(role='admin').first()
        
        if kapil_user:
            # Create approval request
            approval = WorkOrderApproval(
                incident_id=incident.id,
                approval_type='WORK_ORDER',
                requested_by_id=current_user.id,
                approver_id=kapil_user.id,
                request_details=f'Work Order Type: {form.work_order_type.data}\nDiagnostic Findings: {form.diagnostic_findings.data}',
                estimated_cost=form.estimated_cost.data,
                estimated_hours=8  # Default estimate
            )
            
            # Generate approval token for email links
            approval.generate_approval_token()
            
            db.session.add(approval)
            db.session.flush()  # Get the approval ID
            
            # Send approval email
            from app.email_service import send_approval_email
            try:
                if send_approval_email(approval):
                    flash(f'Diagnosis completed! Approval request sent to {kapil_user.full_name} for authorization.', 'success')
                else:
                    flash('Diagnosis completed! Approval request created (email sending failed - please check manually).', 'warning')
            except Exception as e:
                flash('Diagnosis completed! Approval request created (email sending failed - please check manually).', 'warning')
        else:
            flash('Diagnosis completed! No approver found - please contact administrator.', 'warning')
        
        # Create work order if needed
        if form.work_order_type.data in ['REPAIR', 'REPLACE', 'MAINTENANCE']:
            work_order = WorkOrder(
                title=f"UAV Service: {incident.title}",
                description=f"UAV Service Incident #{incident.incident_number_formatted}\n\n{incident.description}\n\nDiagnosis: {form.diagnostic_findings.data}",
                product_name=f"{incident.product_name or 'UAV'} (SN: {incident.serial_number or 'N/A'})",
                owner_name=incident.customer_name,
                estimated_hours=8,  # Default
                cost_estimate=form.estimated_cost.data,
                created_by_id=current_user.id,
                assigned_to_id=int(form.assigned_to_id.data) if form.assigned_to_id.data and form.assigned_to_id.data != '' else None,
                assignment_group_id=int(form.assignment_group_id.data) if form.assignment_group_id.data and form.assignment_group_id.data != '' else None,
                priority_id=2,  # Default medium priority
                category_id=1,  # Default category
                status_id=1,  # Draft
                uav_service_incident_id=incident.id
            )
            db.session.add(work_order)
            db.session.flush()
            
            incident.related_work_order_id = work_order.id
            
            # Add multiple parts to the work order if they were processed
            if multiple_parts_processed and requested_parts_data:
                try:
                    requested_parts = json.loads(requested_parts_data)
                    for part_data in requested_parts:
                        part = InventoryItem.query.get(int(part_data['id']))
                        if part:
                            work_order_part = WorkOrderPart(
                                work_order_id=work_order.id,
                                inventory_item_id=part.id,
                                quantity_requested=int(part_data['quantity']),
                                quantity_used=int(part_data['quantity']),
                                unit_cost=part.unit_cost,
                                total_cost=part.unit_cost * int(part_data['quantity']),
                                notes=part_data.get('notes', '')
                            )
                            db.session.add(work_order_part)
                except (json.JSONDecodeError, ValueError, KeyError):
                    pass  # Error already handled above
            
            # Legacy single part handling (fallback)
            elif not multiple_parts_processed and form.part_number.data and form.quantity_needed.data:
                part = InventoryItem.query.filter_by(part_number=form.part_number.data).first()
                if part:
                    work_order_part = WorkOrderPart(
                        work_order_id=work_order.id,
                        inventory_item_id=part.id,
                        quantity_requested=int(form.quantity_needed.data),
                        quantity_used=int(form.quantity_needed.data),
                        unit_cost=part.unit_cost,
                        total_cost=part.unit_cost * int(form.quantity_needed.data)
                    )
                    db.session.add(work_order_part)
        
        db.session.commit()
        
        flash('Diagnosis completed and work order created successfully!', 'success')
        return redirect(url_for('uav_service.view_incident', id=incident.id))
    else:
        if request.method == 'POST':
            print(f"DEBUG: Form validation failed for incident {incident.id}")
            print(f"DEBUG: Form errors: {form.errors}")
            print(f"DEBUG: Posted form data keys: {list(request.form.keys())}")
            flash('Please check the form for errors and try again.', 'error')
    
    return render_template('uav_service/diagnosis_workflow_enhanced.html', incident=incident, form=form)


@bp.route('/incidents/<int:id>/authorization')
@login_required
def wo_authorization_workflow(id):
    """Handle work order authorization workflow"""
    incident = UAVServiceIncident.query.get_or_404(id)
    
    # Get pending approval for this incident
    approval = WorkOrderApproval.query.filter_by(
        incident_id=incident.id,
        status='PENDING'
    ).first()
    
    return render_template('uav_service/wo_authorization_workflow.html', 
                         incident=incident, approval=approval)


@bp.route('/incidents/<int:id>/initiate-repair', methods=['POST'])
@login_required
def initiate_repair(id):
    """Initiate repair stage after work order approval"""
    incident = UAVServiceIncident.query.get_or_404(id)
    
    # Verify that the incident is in the correct state
    if incident.workflow_status != 'WO_APPROVED':
        flash('Cannot initiate repair. Work order must be approved first.', 'error')
        return redirect(url_for('uav_service.view_incident', id=id))
    
    try:
        # Move to repair stage
        incident.workflow_status = 'REPAIR_MAINTENANCE'
        
        # Create activity log
        activity = UAVServiceActivity(
            uav_service_incident_id=incident.id,
            user_id=current_user.id,
            activity_type='repair_initiated',
            description=f'Repair stage initiated by {current_user.full_name}'
        )
        db.session.add(activity)
        db.session.commit()
        
        flash(f'Repair stage has been initiated for incident {incident.incident_number_formatted}', 'success')
        return redirect(url_for('uav_service.repair_maintenance_workflow', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash('Error initiating repair stage. Please try again.', 'error')
        return redirect(url_for('uav_service.view_incident', id=id))


@bp.route('/incidents/<int:id>/repair', methods=['GET', 'POST'])
@login_required
def repair_maintenance_workflow(id):
    """Handle repair and maintenance workflow"""
    incident = UAVServiceIncident.query.get_or_404(id)
    form = RepairMaintenanceForm()
    
    # Check if this is accessed via stage navigation to preserve data
    preserve_data = request.args.get('preserve_data', 'false') == 'true'
    
    # Get work order parts if there's a related work order
    work_order_parts = []
    
    if incident.related_work_order_id:
        from app.models import WorkOrderPart
        work_order_parts = WorkOrderPart.query.filter_by(work_order_id=incident.related_work_order_id).all()
    
    # Pre-populate form with existing data on GET request
    if request.method == 'GET':
        # Always preserve existing incident data when loading the form
        if incident.technician_notes:
            form.technician_notes.data = incident.technician_notes
        if incident.parts_received is not None:
            form.parts_received.data = incident.parts_received
        if incident.service_status:
            form.service_status.data = incident.service_status
        if incident.actual_cost:
            form.actual_cost.data = incident.actual_cost
        # Note: technician_hours is cumulative, don't pre-populate to avoid double-counting
        
        # Show preservation message if accessed via stage navigation
        if preserve_data:
            flash('Editing repair/maintenance stage. All existing data has been preserved and pre-populated in the form.', 'info')
    
    if form.validate_on_submit():
        # Update cumulative hours (add new hours to existing)
        if form.technician_hours.data:
            incident.technician_hours = (incident.technician_hours or 0) + form.technician_hours.data
        
        # Update other fields only if they have values (preserve existing data)
        if form.technician_notes.data:
            incident.technician_notes = form.technician_notes.data
        if form.parts_received.data is not None:
            incident.parts_received = form.parts_received.data
        if form.service_status.data:
            incident.service_status = form.service_status.data
        if form.actual_cost.data:
            incident.actual_cost = form.actual_cost.data
        
        if form.service_status.data == 'COMPLETED':
            incident.advance_workflow(current_user, f'Repair/maintenance completed. Hours: {form.technician_hours.data or 0}')
        
        db.session.commit()
        
        flash('Repair/maintenance progress updated successfully!', 'success')
        return redirect(url_for('uav_service.view_incident', id=incident.id))
    
    # Pre-populate current values
    form.technician_hours.data = 0
    form.service_status.data = incident.service_status
    form.actual_cost.data = incident.actual_cost
    
    return render_template('uav_service/repair_maintenance_workflow.html', 
                         incident=incident, form=form, work_order_parts=work_order_parts)


@bp.route('/incidents/<int:id>/quality-check', methods=['GET', 'POST'])
@login_required
def quality_check_workflow(id):
    """Handle quality check and handover workflow"""
    incident = UAVServiceIncident.query.get_or_404(id)
    form = QualityCheckForm()
    
    # Check if this is accessed via stage navigation to preserve data
    preserve_data = request.args.get('preserve_data', 'false') == 'true'
    
    # Pre-populate form with existing data on GET request
    if request.method == 'GET':
        # Always preserve existing incident data when loading the form
        if incident.qa_verified is not None:
            form.qa_verified.data = incident.qa_verified
        if incident.airworthiness_certified is not None:
            form.airworthiness_certified.data = incident.airworthiness_certified
        if incident.qa_notes:
            form.qa_notes.data = incident.qa_notes
        if incident.invoice_number:
            form.invoice_number.data = incident.invoice_number
        if incident.actual_cost:
            form.final_cost.data = incident.actual_cost
            
        # Show preservation message if accessed via stage navigation
        if preserve_data:
            flash('Editing quality check stage. All existing data has been preserved and pre-populated in the form.', 'info')
    
    if form.validate_on_submit():
        # Update fields only if they have values (preserve existing data)
        if form.qa_verified.data is not None:
            incident.qa_verified = form.qa_verified.data
        if form.airworthiness_certified.data is not None:
            incident.airworthiness_certified = form.airworthiness_certified.data
        if form.qa_notes.data:
            incident.qa_notes = form.qa_notes.data
        if current_user.id:
            incident.qa_technician_id = current_user.id
        
        # Handle billing for non-warranty services
        if not incident.is_warranty_service:
            if form.invoice_number.data:
                incident.invoice_number = form.invoice_number.data
            if form.final_cost.data:
                incident.actual_cost = form.final_cost.data
                incident.invoice_generated = True
        
        if form.qa_verified.data and form.airworthiness_certified.data:
            incident.advance_workflow(current_user, 'QA verification and airworthiness certification completed')
        
        db.session.commit()
        
        flash('Quality check completed successfully!', 'success')
        return redirect(url_for('uav_service.view_incident', id=incident.id))
    
    return render_template('uav_service/quality_check_workflow.html', incident=incident, form=form)


@bp.route('/incidents/<int:id>/preventive-maintenance', methods=['GET', 'POST'])
@login_required
def preventive_maintenance_workflow(id):
    """Setup preventive maintenance schedule"""
    incident = UAVServiceIncident.query.get_or_404(id)
    form = PreventiveMaintenanceForm()
    
    # Check if this is accessed via stage navigation to preserve data
    preserve_data = request.args.get('preserve_data', 'false') == 'true'
    
    # Check for existing maintenance schedule to preserve data
    existing_schedule = UAVMaintenanceSchedule.query.filter_by(
        uav_serial_number=incident.serial_number
    ).first()
    
    # Pre-populate form with existing data on GET request
    if request.method == 'GET':
        if existing_schedule:
            # Preserve existing maintenance schedule data
            if existing_schedule.maintenance_type:
                form.maintenance_type.data = existing_schedule.maintenance_type
            if existing_schedule.flight_hours_interval:
                form.flight_hours_interval.data = existing_schedule.flight_hours_interval
            if existing_schedule.time_interval_days:
                form.time_interval_days.data = existing_schedule.time_interval_days
                
        # Show preservation message if accessed via stage navigation
        if preserve_data:
            flash('Editing preventive maintenance stage. All existing data has been preserved and pre-populated in the form.', 'info')
    
    if form.validate_on_submit():
        # Create or update maintenance schedule
        schedule = existing_schedule or UAVMaintenanceSchedule(
            uav_model=incident.product_name,
            uav_serial_number=incident.serial_number,
            customer_id=incident.created_by_id,
            product_id=incident.product_id
        )
        
        # Update fields only if they have values (preserve existing data)
        if form.maintenance_type.data:
            schedule.maintenance_type = form.maintenance_type.data
        if form.flight_hours_interval.data:
            schedule.flight_hours_interval = form.flight_hours_interval.data
        if form.time_interval_days.data:
            schedule.time_interval_days = form.time_interval_days.data
            
        # Set defaults for required fields if not already set
        if not schedule.current_flight_hours:
            schedule.current_flight_hours = 0
        if not schedule.last_maintenance_date:
            schedule.last_maintenance_date = datetime.now(timezone.utc)
        
        # Calculate next maintenance due
        schedule.calculate_next_maintenance()
        
        db.session.add(schedule)
        
        # Mark incident as having preventive maintenance setup
        incident.is_preventive_maintenance = True
        incident.next_maintenance_due = schedule.next_maintenance_due
        
        # IMPORTANT: Advance workflow to complete the incident
        incident.advance_workflow(current_user, f'Preventive maintenance schedule created: {form.maintenance_type.data}')
        
        db.session.commit()
        
        flash('Preventive maintenance schedule created and incident completed successfully!', 'success')
        return redirect(url_for('uav_service.view_incident', id=incident.id))
    
    return render_template('uav_service/preventive_maintenance_workflow.html', incident=incident, form=form)


@bp.route('/incidents/<int:id>/close', methods=['GET', 'POST'])
@login_required
def close_incident_workflow(id):
    """Close the service incident and update related work order"""
    incident = UAVServiceIncident.query.get_or_404(id)
    
    # Check if this is accessed via stage navigation to preserve data
    preserve_data = request.args.get('preserve_data', 'false') == 'true'
    
    # Show preservation message if accessed via stage navigation
    if request.method == 'GET' and preserve_data:
        flash('Editing incident closure stage. All existing data has been preserved. You can review the incident details before final closure.', 'info')
    
    if request.method == 'POST':
        # Get the closing notes from the form (preserve existing if empty)
        closing_notes = request.form.get('closing_notes', '')
        if not closing_notes:
            closing_notes = 'Service incident closed successfully.'
        
        # Only advance workflow if not already closed (preserve status)
        if incident.workflow_status != 'CLOSED':
            incident.advance_workflow(current_user, closing_notes)
            flash('Service incident has been closed successfully! Related work order has been marked as completed.', 'success')
        else:
            # Just update notes if already closed
            activity = UAVServiceActivity(
                uav_service_incident_id=incident.id,
                user_id=current_user.id,
                activity_type='closure_update',
                description=f'Closure notes updated: {closing_notes}'
            )
            db.session.add(activity)
            db.session.commit()
            flash('Incident closure information has been updated.', 'success')
        
        return redirect(url_for('uav_service.view_incident', id=incident.id))
    
    return render_template('uav_service/close_incident_workflow.html', incident=incident)


@bp.route('/maintenance/schedules')
@login_required
def maintenance_schedules():
    """View all maintenance schedules"""
    page = request.args.get('page', 1, type=int)
    schedules = UAVMaintenanceSchedule.query.order_by(UAVMaintenanceSchedule.next_maintenance_due.asc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Pass current datetime to template for calculations
    from datetime import datetime, timezone
    current_datetime = datetime.now(timezone.utc)
    
    return render_template('uav_service/maintenance_schedules.html', 
                         schedules=schedules, 
                         current_datetime=current_datetime)


@bp.route('/maintenance/schedules/create', methods=['GET', 'POST'])
@login_required
def create_maintenance_schedule():
    """Create new maintenance schedule"""
    form = MaintenanceScheduleForm()
    
    if form.validate_on_submit():
        schedule = UAVMaintenanceSchedule(
            uav_model=form.uav_model.data,
            uav_serial_number=form.uav_serial_number.data,
            maintenance_type=form.maintenance_type.data,
            flight_hours_interval=form.flight_hours_interval.data,
            time_interval_days=form.time_interval_days.data,
            current_flight_hours=form.current_flight_hours.data,
            customer_id=current_user.id
        )
        
        schedule.calculate_next_maintenance()
        
        db.session.add(schedule)
        db.session.commit()
        
        flash('Maintenance schedule created successfully!', 'success')
        return redirect(url_for('uav_service.maintenance_schedules'))
    
    return render_template('uav_service/create_maintenance_schedule.html', form=form)


@bp.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """API endpoint for UAV service dashboard statistics"""
    from datetime import datetime, timezone, timedelta
    
    # Total incidents
    total_incidents = UAVServiceIncident.query.count()
    
    # Open incidents (not closed)
    open_incidents = UAVServiceIncident.query.filter(
        UAVServiceIncident.workflow_status.in_(['INCIDENT_RAISED', 'DIAGNOSIS_WO', 'REPAIR_MAINTENANCE', 'QUALITY_CHECK', 'PREVENTIVE_MAINTENANCE'])
    ).count()
    
    # SLA breached incidents - need to calculate based on property logic
    all_incidents = UAVServiceIncident.query.filter(
        UAVServiceIncident.workflow_status != 'CLOSED'
    ).all()
    
    sla_breached = 0
    for incident in all_incidents:
        if incident.sla_status == 'BREACHED':
            sla_breached += 1
    
    # Maintenance due - check if UAVMaintenanceSchedule exists and has data
    try:
        maintenance_due = UAVMaintenanceSchedule.query.filter(
            UAVMaintenanceSchedule.next_maintenance_due <= datetime.now(timezone.utc) + timedelta(days=7)
        ).count()
    except Exception:
        # If UAVMaintenanceSchedule doesn't exist or has issues, count incidents needing preventive maintenance
        maintenance_due = UAVServiceIncident.query.filter_by(
            workflow_status='PREVENTIVE_MAINTENANCE'
        ).count()
    
    stats = {
        'total_incidents': total_incidents,
        'open_incidents': open_incidents,
        'sla_breached': sla_breached,
        'maintenance_due': maintenance_due
    }
    
    return jsonify(stats)


@bp.route('/api/product-by-serial/<serial_number>')
@login_required
def api_product_by_serial(serial_number):
    """API endpoint to fetch product details by serial number"""
    try:
        # Find product by serial number
        product = Product.query.filter_by(serial_number=serial_number).first()
        
        if not product:
            return jsonify({
                'success': False,
                'message': 'No product found with this serial number'
            }), 404
        
        # Get last service date from previous incidents
        last_incident = UAVServiceIncident.query.filter_by(
            serial_number=serial_number
        ).order_by(UAVServiceIncident.created_at.desc()).first()
        
        last_service_date = None
        if last_incident and last_incident.handed_over_at:
            last_service_date = last_incident.handed_over_at.strftime('%Y-%m-%d')
        elif last_incident and last_incident.last_service_date:
            last_service_date = last_incident.last_service_date.strftime('%Y-%m-%d')
        
        # Prepare response data
        response_data = {
            'success': True,
            'product': {
                'id': product.id,
                'product_name': product.product_name,
                'product_code': product.product_code,
                'serial_number': product.serial_number,
                'owner_company': product.owner_company.name if product.owner_company else 'Unknown',
                'owner_company_id': product.owner_company.id if product.owner_company else None,
                'category': product.category.name if product.category else 'Unknown',
                'description': product.description,
                'last_service_date': last_service_date
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching product by serial number {serial_number}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while fetching product details'
        }), 500


@bp.route('/incidents/<int:id>/edit-stages', methods=['GET', 'POST'])
@login_required
def edit_stages(id):
    """Navigate to and edit any stage of the incident workflow"""
    incident = UAVServiceIncident.query.get_or_404(id)
    
    # Check permission
    if not incident.can_edit_stages(current_user):
        flash('You do not have permission to edit incident stages.', 'error')
        return redirect(url_for('uav_service.view_incident', id=id))
    
    if request.method == 'POST':
        selected_stage = request.form.get('selected_stage')
        
        # Define stage mappings with data preservation flags
        stage_mappings = {
            'INCIDENT_RAISED': {
                'workflow_status': 'INCIDENT_RAISED',
                'route': 'uav_service.view_incident',
                'preserve_data': True
            },
            'DIAGNOSIS_WO': {
                'workflow_status': 'DIAGNOSIS_WO', 
                'route': 'uav_service.diagnosis_workflow',
                'preserve_data': True
            },
            'WO_AUTHORIZATION': {
                'workflow_status': 'WO_AUTHORIZATION',
                'route': 'uav_service.wo_authorization_workflow',
                'preserve_data': True
            },
            'REPAIR_MAINTENANCE': {
                'workflow_status': 'REPAIR_MAINTENANCE',
                'route': 'uav_service.repair_maintenance_workflow',
                'preserve_data': True
            },
            'QUALITY_CHECK': {
                'workflow_status': 'QUALITY_CHECK',
                'route': 'uav_service.quality_check_workflow',
                'preserve_data': True
            },
            'PREVENTIVE_MAINTENANCE': {
                'workflow_status': 'PREVENTIVE_MAINTENANCE',
                'route': 'uav_service.preventive_maintenance_workflow',
                'preserve_data': True
            },
            'CLOSED': {
                'workflow_status': 'CLOSED',
                'route': 'uav_service.close_incident_workflow',
                'preserve_data': True
            }
        }
        
        if selected_stage in stage_mappings:
            stage_info = stage_mappings[selected_stage]
            
            # Update incident workflow status if different (preserving all existing data)
            if incident.workflow_status != stage_info['workflow_status']:
                old_status = incident.workflow_status
                incident.workflow_status = stage_info['workflow_status']
                
                # Log the manual stage change with data preservation note
                activity = UAVServiceActivity(
                    uav_service_incident_id=incident.id,
                    user_id=current_user.id,
                    activity_type='stage_navigation',
                    description=f'Manual stage navigation: {old_status} → {stage_info["workflow_status"]} (Data preserved)'
                )
                db.session.add(activity)
                db.session.commit()
                
                flash(f'Successfully navigated to {selected_stage.replace("_", " ").title()} stage. All existing data has been preserved.', 'success')
            else:
                flash(f'Opening {selected_stage.replace("_", " ").title()} stage for editing. All existing data will be preserved.', 'info')
            
            # Add URL parameter to indicate data preservation
            redirect_url = url_for(stage_info['route'], id=incident.id, preserve_data='true')
            return redirect(redirect_url)
        else:
            flash('Invalid stage selected.', 'error')
    
    # Define workflow stages with their descriptions
    workflow_stages = [
        {
            'key': 'INCIDENT_RAISED',
            'name': 'Incident/Service Request',
            'description': 'Customer reports issue',
            'step': 1,
            'icon': 'fas fa-inbox'
        },
        {
            'key': 'DIAGNOSIS_WO',
            'name': 'Diagnosis & Work Order',
            'description': 'Technician diagnosis',
            'step': 2,
            'icon': 'fas fa-stethoscope'
        },
        {
            'key': 'REPAIR_MAINTENANCE',
            'name': 'Repair/Maintenance',
            'description': 'Parts & technician work',
            'step': 3,
            'icon': 'fas fa-tools'
        },
        {
            'key': 'QUALITY_CHECK',
            'name': 'Quality Check & Handover',
            'description': 'QA & compliance',
            'step': 4,
            'icon': 'fas fa-check-circle'
        },
        {
            'key': 'PREVENTIVE_MAINTENANCE',
            'name': 'Preventive Maintenance',
            'description': 'Schedule future maintenance',
            'step': 5,
            'icon': 'fas fa-calendar-alt'
        },
        {
            'key': 'CLOSED',
            'name': 'Closed',
            'description': 'Service completed',
            'step': 6,
            'icon': 'fas fa-flag-checkered'
        }
    ]
    
    return render_template('uav_service/edit_stages.html', 
                         incident=incident, 
                         workflow_stages=workflow_stages)


@bp.route('/dashboard')
@login_required
def dashboard():
    """UAV Service dashboard"""
    # Recent incidents
    recent_incidents = UAVServiceIncident.query.order_by(
        UAVServiceIncident.created_at.desc()
    ).limit(10).all()
    
    # SLA critical incidents
    sla_critical = UAVServiceIncident.query.filter_by(sla_status='CRITICAL').all()
    
    # Maintenance due
    maintenance_due = UAVMaintenanceSchedule.query.filter(
        UAVMaintenanceSchedule.next_maintenance_due <= datetime.now(timezone.utc) + timedelta(days=7)
    ).limit(5).all()
    
    return render_template('uav_service/dashboard.html', 
                         recent_incidents=recent_incidents,
                         sla_critical=sla_critical,
                         maintenance_due=maintenance_due)
