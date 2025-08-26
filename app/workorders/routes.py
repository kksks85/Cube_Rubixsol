"""
Work Order Routes
"""

from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc, asc
from app import db
from app.workorders import bp
from app.workorders.forms import WorkOrderForm, WorkOrderUpdateForm, WorkOrderFilterForm
from app.models import WorkOrder, User, Priority, Category, Product, Company, WorkOrderStatus

@bp.route('/test')
def test_route():
    """Test route to verify blueprint is working"""
    return "Workorders blueprint is working!"

@bp.route('/')
@bp.route('/list')
@login_required
def list_workorders():
    """List work orders with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Initialize filter form
    filter_form = WorkOrderFilterForm()
    
    # Populate form choices
    filter_form.status_id.choices = [(0, 'All Statuses')] + [(s.id, s.name) for s in WorkOrderStatus.query.all()]
    filter_form.priority_id.choices = [(0, 'All Priorities')] + [(p.id, p.name) for p in Priority.query.all()]
    filter_form.category_id.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in Category.query.all()]
    
    if current_user.has_role('admin') or current_user.has_role('manager'):
        filter_form.assigned_to_id.choices = [(0, 'All Users')] + [
            (u.id, u.full_name) for u in User.query.filter_by(is_active=True).all()
        ]
    else:
        filter_form.assigned_to_id.choices = [(0, 'All'), (current_user.id, 'My Work Orders')]
    
    # Build query
    query = WorkOrder.query
    
    # Apply access control
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        query = query.filter_by(assigned_to_id=current_user.id)
    
    # Apply filters
    if request.args.get('status_id') and int(request.args.get('status_id')) > 0:
        query = query.filter_by(status_id=int(request.args.get('status_id')))
        filter_form.status_id.data = int(request.args.get('status_id'))
    
    if request.args.get('priority_id') and int(request.args.get('priority_id')) > 0:
        query = query.filter_by(priority_id=int(request.args.get('priority_id')))
        filter_form.priority_id.data = int(request.args.get('priority_id'))
    
    if request.args.get('category_id') and int(request.args.get('category_id')) > 0:
        query = query.filter_by(category_id=int(request.args.get('category_id')))
        filter_form.category_id.data = int(request.args.get('category_id'))
    
    if request.args.get('assigned_to_id') and int(request.args.get('assigned_to_id')) > 0:
        query = query.filter_by(assigned_to_id=int(request.args.get('assigned_to_id')))
        filter_form.assigned_to_id.data = int(request.args.get('assigned_to_id'))
    
    # Sort by priority and creation date
    query = query.join(Priority).order_by(desc(Priority.level), desc(WorkOrder.created_at))
    
    # Paginate results
    workorders = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('workorders/list.html',
                         title='Work Orders',
                         workorders=workorders,
                         filter_form=filter_form)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_workorder():
    """Create new work order"""
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to create work orders.', 'error')
        return redirect(url_for('workorders.list_workorders'))
    
    form = WorkOrderForm()
    
    # Populate form choices
    form.category_id.choices = [(0, 'Select Category')] + [(c.id, c.name) for c in Category.query.all()]
    form.priority_id.choices = [(p.id, p.name) for p in Priority.query.order_by(Priority.level).all()]
    form.assigned_to_id.choices = [(0, 'Unassigned')] + [
        (u.id, u.full_name) for u in User.query.filter_by(is_active=True).all()
    ]
    form.status_id.choices = [(s.id, s.name) for s in WorkOrderStatus.query.order_by(WorkOrderStatus.id).all()]
    from app.models import Product
    form.product_name.choices = [(0, 'Select Product')] + [
        (p.id, p.product_name) for p in Product.query.filter_by(is_active=True).all()
    ]
    
    if form.validate_on_submit():
        # Get initial status (should be "Draft")
        initial_status = WorkOrderStatus.query.filter_by(name='Draft').first()
        if not initial_status:
            initial_status = WorkOrderStatus.query.first()
        
        # Get product name from selected product ID
        selected_product = None
        if form.product_name.data and form.product_name.data > 0:
            selected_product = Product.query.get(form.product_name.data)
        workorder = WorkOrder(
            title=form.title.data,
            description=form.description.data,
            address=form.address.data,
            product_name=selected_product.product_name if selected_product else None,
            owner_name=form.owner_name.data,
            # ...existing code...
            category_id=form.category_id.data if form.category_id.data > 0 else None,
            priority_id=form.priority_id.data,
            assigned_to_id=form.assigned_to_id.data if form.assigned_to_id.data > 0 else None,
            estimated_hours=form.estimated_hours.data,
            cost_estimate=form.cost_estimate.data,
            due_date=form.due_date.data,
            notes=form.notes.data,
            created_by_id=current_user.id,
            status_id=form.status_id.data if form.status_id.data else initial_status.id
        )
        
        db.session.add(workorder)
        db.session.flush()  # Get the ID
        
        # Add creation activity
        workorder.add_activity(current_user, 'created', f'Work order created: {workorder.title}')
        
        # Add assignment activity if assigned
        if workorder.assigned_to_id:
            workorder.add_activity(
                current_user, 
                'assigned', 
                f'Work order assigned to {workorder.assignee.full_name}'
            )
        
        db.session.commit()
        
        # Ensure the session is refreshed to confirm the work order is persisted
        db.session.refresh(workorder)

        # Generate Gate Pass PDF and save to Desktop
        try:
            import os
            from app.workorders.pdf_utils import generate_gate_pass_pdf
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            pdf_filename = f"GatePass_WorkOrder_{workorder.id}.pdf"
            pdf_path = os.path.join(desktop_path, pdf_filename)
            generate_gate_pass_pdf(workorder, pdf_path)
            flash(f'Gate Pass PDF saved to your Desktop as {pdf_filename}.', 'info')
        except Exception as e:
            flash(f'Work order created, but failed to generate Gate Pass PDF: {e}', 'warning')

        flash(f'Work order #{workorder.id} has been created successfully.', 'success')
        return redirect(url_for('workorders.view_workorder', id=workorder.id))
    
    return render_template('workorders/create.html', title='Create Work Order', form=form)

@bp.route('/<int:id>')
@login_required
def view_workorder(id):
    """View work order details"""
    workorder = WorkOrder.query.get_or_404(id)
    
    # Check access permissions
    if not current_user.can_edit_workorder(workorder) and workorder.assigned_to_id != current_user.id:
        if not (current_user.has_role('admin') or current_user.has_role('manager')):
            abort(403)
    
    # Get activity history
    from app.models import WorkOrderActivity
    activities = workorder.activities.order_by(desc(WorkOrderActivity.timestamp)).all()
    
    return render_template('workorders/view.html',
                         title=f'Work Order #{workorder.id}',
                         workorder=workorder,
                         activities=activities)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workorder(id):
    """Edit work order"""
    workorder = WorkOrder.query.get_or_404(id)
    
    if not current_user.can_edit_workorder(workorder):
        flash('You do not have permission to edit this work order.', 'error')
        return redirect(url_for('workorders.view_workorder', id=id))
    
    form = WorkOrderForm()
    
    # Populate form choices
    form.category_id.choices = [(0, 'Select Category')] + [(c.id, c.name) for c in Category.query.all()]
    form.priority_id.choices = [(p.id, p.name) for p in Priority.query.order_by(Priority.level).all()]
    form.assigned_to_id.choices = [(0, 'Unassigned')] + [
        (u.id, u.full_name) for u in User.query.filter_by(is_active=True).all()
    ]
    
    if form.validate_on_submit():
        # Track changes for activity log
        changes = []
        
        if workorder.title != form.title.data:
            changes.append(f'Title changed from "{workorder.title}" to "{form.title.data}"')
            workorder.title = form.title.data
        
        if workorder.description != form.description.data:
            workorder.description = form.description.data
            changes.append('Description updated')
        
        if workorder.address != form.address.data:
            if workorder.address:
                changes.append(f'Address changed from "{workorder.address}" to "{form.address.data}"')
            else:
                changes.append(f'Address set to "{form.address.data}"')
            workorder.address = form.address.data
        
        # Update product-related fields
        if workorder.product_name != form.product_name.data:
            workorder.product_name = form.product_name.data
            changes.append('Product name updated')
        
        if workorder.owner_name != form.owner_name.data:
            workorder.owner_name = form.owner_name.data
            changes.append('Owner name updated')
        
        # Track assignment changes
        if workorder.assigned_to_id != (form.assigned_to_id.data if form.assigned_to_id.data > 0 else None):
            old_assignee = workorder.assignee.full_name if workorder.assignee else 'Unassigned'
            new_assignee_id = form.assigned_to_id.data if form.assigned_to_id.data > 0 else None
            new_assignee = User.query.get(new_assignee_id).full_name if new_assignee_id else 'Unassigned'
            
            workorder.assigned_to_id = new_assignee_id
            workorder.add_activity(current_user, 'assigned', f'Assigned changed from {old_assignee} to {new_assignee}')
        
        # Update other fields
        workorder.category_id = form.category_id.data if form.category_id.data > 0 else None
        workorder.priority_id = form.priority_id.data
        workorder.estimated_hours = form.estimated_hours.data
        workorder.cost_estimate = form.cost_estimate.data
        workorder.due_date = form.due_date.data
        workorder.notes = form.notes.data
        workorder.updated_at = datetime.now(timezone.utc)
        
        # Add activity for changes
        if changes:
            workorder.add_activity(current_user, 'updated', '; '.join(changes))
        
        db.session.commit()
        
        flash('Work order has been updated successfully.', 'success')
        return redirect(url_for('workorders.view_workorder', id=workorder.id))
    
    # Pre-populate form
    form.title.data = workorder.title
    form.description.data = workorder.description
    form.address.data = workorder.address
    form.product_name.data = workorder.product_name
    form.owner_name.data = workorder.owner_name
    form.category_id.data = workorder.category_id or 0
    form.priority_id.data = workorder.priority_id
    form.assigned_to_id.data = workorder.assigned_to_id or 0
    form.estimated_hours.data = workorder.estimated_hours
    form.cost_estimate.data = workorder.cost_estimate
    form.due_date.data = workorder.due_date
    form.notes.data = workorder.notes
    
    return render_template('workorders/edit.html',
                         title=f'Edit Work Order #{workorder.id}',
                         form=form,
                         workorder=workorder)

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_workorder(id):
    """Update work order status (for technicians)"""
    workorder = WorkOrder.query.get_or_404(id)
    
    # Check if user can update this work order
    if workorder.assigned_to_id != current_user.id and not current_user.can_edit_workorder(workorder):
        flash('You do not have permission to update this work order.', 'error')
        return redirect(url_for('workorders.view_workorder', id=id))
    
    form = WorkOrderUpdateForm()
    
    # Populate status choices
    form.status_id.choices = [(s.id, s.name) for s in WorkOrderStatus.query.all()]
    
    if form.validate_on_submit():
        # Track status change
        old_status = workorder.status_detail.name if workorder.status_detail else "None"
        new_status = WorkOrderStatus.query.get(form.status_id.data).name
        
        workorder.status_id = form.status_id.data
        
        # Update actual hours and cost if provided
        if form.actual_hours.data is not None:
            workorder.actual_hours = form.actual_hours.data
        
        if form.actual_cost.data is not None:
            workorder.actual_cost = form.actual_cost.data
        
        # Set completion date if status is closed
        new_status_obj = WorkOrderStatus.query.get(form.status_id.data)
        if new_status_obj.is_final and not workorder.completed_date:
            workorder.completed_date = datetime.now(timezone.utc)
        
        workorder.updated_at = datetime.now(timezone.utc)
        
        # Add activity
        activity_desc = f'Status changed from {old_status} to {new_status}'
        if form.notes.data:
            activity_desc += f'. Notes: {form.notes.data}'
        
        workorder.add_activity(current_user, 'status_changed', activity_desc)
        
        db.session.commit()
        
        flash('Work order has been updated successfully.', 'success')
        return redirect(url_for('workorders.view_workorder', id=workorder.id))
    
    # Pre-populate current status
    form.status_id.data = workorder.status_id
    
    return render_template('workorders/update.html',
                         title=f'Update Work Order #{workorder.id}',
                         form=form,
                         workorder=workorder)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_workorder(id):
    """Delete work order (admin only)"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to delete work orders.', 'error')
        return redirect(url_for('workorders.view_workorder', id=id))
    
    workorder = WorkOrder.query.get_or_404(id)
    
    db.session.delete(workorder)
    db.session.commit()
    
    flash(f'Work order #{id} has been deleted.', 'success')
    return redirect(url_for('workorders.list_workorders'))

# API Endpoints for autocomplete functionality

@bp.route('/<int:id>/copy', methods=['POST'])
@login_required
def copy_workorder(id):
    """Copy an existing work order and redirect to the new work order's view page"""
    original = WorkOrder.query.get_or_404(id)
    if not (current_user.has_role('admin') or current_user.has_role('manager')):
        flash('You do not have permission to copy work orders.', 'error')
        return redirect(url_for('workorders.view_workorder', id=id))

    # Create a new WorkOrder instance with copied fields
    new_workorder = WorkOrder(
        title=original.title + ' (Copy)',
        description=original.description,
        address=original.address,
        product_name=original.product_name,
        owner_name=original.owner_name,
        category_id=original.category_id,
        priority_id=original.priority_id,
        assigned_to_id=original.assigned_to_id,
        estimated_hours=original.estimated_hours,
        cost_estimate=original.cost_estimate,
        due_date=original.due_date,
        notes=original.notes,
        created_by_id=current_user.id,
        status_id=original.status_id
    )
    db.session.add(new_workorder)
    db.session.commit()
    flash(f'Work order copied successfully as #{new_workorder.id}.', 'success')
    return redirect(url_for('workorders.view_workorder', id=new_workorder.id))
@bp.route('/api/search_products')
@login_required
def search_products():
    """API endpoint to search products for autocomplete"""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    products = Product.query.filter(
        Product.product_name.ilike(f'%{query}%')
    ).limit(10).all()
    
    results = []
    for product in products:
        results.append({
            'name': product.product_name,
            'code': product.product_code,
            'company_name': product.owner_company.name if product.owner_company else '',
            'company_address': product.owner_company.full_address if product.owner_company else ''
        })
    
    return jsonify(results)

@bp.route('/api/get_product_details')
@login_required  
def get_product_details():
    """API endpoint to get product details including company info"""
    product_name = request.args.get('product_name', '')
    
    product = Product.query.filter_by(product_name=product_name).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify({
        'product_name': product.product_name,
        'product_code': product.product_code,
        'company_name': product.owner_company.name if product.owner_company else '',
        'company_address': product.owner_company.full_address if product.owner_company else ''
    })
