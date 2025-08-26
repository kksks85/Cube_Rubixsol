"""
Inventory Management Routes
"""

from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, desc
from app import db
from app.inventory import bp
from app.inventory.forms import (InventoryCategoryForm, InventoryItemForm, 
                               InventoryTransactionForm, WorkOrderPartRequestForm, StockSearchForm)
from app.models import (InventoryCategory, InventoryItem, InventoryTransaction, 
                       WorkOrderPart, WorkOrder, User)

@bp.route('/')
@login_required
def dashboard():
    """Inventory dashboard with key metrics"""
    # Get inventory statistics
    total_items = InventoryItem.query.filter_by(is_active=True).count()
    low_stock_items = InventoryItem.query.filter(
        InventoryItem.quantity_in_stock <= InventoryItem.minimum_stock_level,
        InventoryItem.is_active == True
    ).count()
    out_of_stock_items = InventoryItem.query.filter(
        InventoryItem.quantity_in_stock == 0,
        InventoryItem.is_active == True
    ).count()
    
    # Recent transactions
    recent_transactions = InventoryTransaction.query.order_by(
        desc(InventoryTransaction.created_at)
    ).limit(10).all()
    
    # Low stock alerts
    low_stock_alerts = InventoryItem.query.filter(
        InventoryItem.quantity_in_stock <= InventoryItem.minimum_stock_level,
        InventoryItem.is_active == True
    ).order_by(InventoryItem.quantity_in_stock).limit(10).all()
    
    # Categories with item counts
    categories = db.session.query(
        InventoryCategory,
        db.func.count(InventoryItem.id).label('item_count')
    ).outerjoin(InventoryItem).group_by(InventoryCategory.id).all()
    
    return render_template('inventory/dashboard.html',
                         total_items=total_items,
                         low_stock_items=low_stock_items,
                         out_of_stock_items=out_of_stock_items,
                         recent_transactions=recent_transactions,
                         low_stock_alerts=low_stock_alerts,
                         categories=categories)

@bp.route('/items')
@login_required
def items():
    """List all inventory items with search and filter"""
    form = StockSearchForm()
    
    # Populate category choices
    categories = InventoryCategory.query.all()
    form.category_id.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in categories]
    
    # Build query
    query = InventoryItem.query.filter_by(is_active=True)
    
    # Check for URL parameters (from category view items button)
    category_param = request.args.get('category', type=int)
    search_param = request.args.get('search', '')
    stock_status_param = request.args.get('stock_status', '')
    
    # Apply filters from URL parameters or form submission
    if request.method == 'POST' and form.validate_on_submit():
        # Form submission takes priority
        if form.search_term.data:
            search = f"%{form.search_term.data}%"
            query = query.filter(or_(
                InventoryItem.name.ilike(search),
                InventoryItem.part_number.ilike(search),
                InventoryItem.manufacturer.ilike(search)
            ))
        
        if form.category_id.data and form.category_id.data != 0:
            query = query.filter_by(category_id=form.category_id.data)
        
        if form.stock_status.data:
            if form.stock_status.data == 'out_of_stock':
                query = query.filter(InventoryItem.quantity_in_stock == 0)
            elif form.stock_status.data == 'low_stock':
                query = query.filter(
                    InventoryItem.quantity_in_stock <= InventoryItem.minimum_stock_level,
                    InventoryItem.quantity_in_stock > 0
                )
            elif form.stock_status.data == 'in_stock':
                query = query.filter(InventoryItem.quantity_in_stock > InventoryItem.minimum_stock_level)
    else:
        # Apply URL parameters
        if category_param:
            query = query.filter_by(category_id=category_param)
            # Set form default for display
            form.category_id.data = category_param
        
        if search_param:
            search = f"%{search_param}%"
            query = query.filter(or_(
                InventoryItem.name.ilike(search),
                InventoryItem.part_number.ilike(search),
                InventoryItem.manufacturer.ilike(search)
            ))
            form.search_term.data = search_param
        
        if stock_status_param:
            if stock_status_param == 'out_of_stock':
                query = query.filter(InventoryItem.quantity_in_stock == 0)
            elif stock_status_param == 'low_stock':
                query = query.filter(
                    InventoryItem.quantity_in_stock <= InventoryItem.minimum_stock_level,
                    InventoryItem.quantity_in_stock > 0
                )
            elif stock_status_param == 'in_stock':
                query = query.filter(InventoryItem.quantity_in_stock > InventoryItem.minimum_stock_level)
            form.stock_status.data = stock_status_param
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    items = query.order_by(InventoryItem.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get selected category name for display
    selected_category = None
    if category_param:
        selected_category = InventoryCategory.query.get(category_param)
    
    return render_template('inventory/items.html', items=items, form=form, selected_category=selected_category)

@bp.route('/items/create', methods=['GET', 'POST'])
@login_required
def create_item():
    """Create new inventory item"""
    form = InventoryItemForm()
    
    # Populate category choices
    categories = InventoryCategory.query.order_by(InventoryCategory.name).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        # Check for duplicate part number
        existing_item = InventoryItem.query.filter_by(part_number=form.part_number.data).first()
        if existing_item:
            flash('Part number already exists. Please use a different part number.', 'error')
            return render_template('inventory/create_item.html', form=form)
        
        item = InventoryItem(
            part_number=form.part_number.data,
            name=form.name.data,
            description=form.description.data,
            manufacturer=form.manufacturer.data,
            model=form.model.data,
            quantity_in_stock=form.quantity_in_stock.data,
            minimum_stock_level=form.minimum_stock_level.data,
            maximum_stock_level=form.maximum_stock_level.data,
            unit_cost=form.unit_cost.data,
            weight=form.weight.data,
            dimensions=form.dimensions.data,
            compatible_uav_models=form.compatible_uav_models.data,
            category_id=form.category_id.data,
            is_active=form.is_active.data
        )
        
        db.session.add(item)
        db.session.flush()  # Get the item ID
        
        # Create initial stock transaction if quantity > 0
        if form.quantity_in_stock.data > 0:
            transaction = InventoryTransaction(
                item_id=item.id,
                transaction_type='IN',
                quantity=form.quantity_in_stock.data,
                unit_cost=form.unit_cost.data,
                total_cost=(form.unit_cost.data or 0) * form.quantity_in_stock.data,
                reference_type='ADJUSTMENT',
                notes='Initial stock entry',
                created_by_id=current_user.id
            )
            db.session.add(transaction)
        
        db.session.commit()
        flash(f'Inventory item "{item.name}" created successfully.', 'success')
        return redirect(url_for('inventory.view_item', id=item.id))
    
    return render_template('inventory/create_item.html', form=form)

@bp.route('/items/<int:id>')
@login_required
def view_item(id):
    """View inventory item details"""
    item = InventoryItem.query.get_or_404(id)
    
    # Get recent transactions for this item
    transactions = InventoryTransaction.query.filter_by(item_id=id).order_by(
        desc(InventoryTransaction.created_at)
    ).limit(20).all()
    
    # Get work orders using this part
    work_order_parts = WorkOrderPart.query.filter_by(inventory_item_id=id).order_by(
        desc(WorkOrderPart.requested_at)
    ).limit(10).all()
    
    return render_template('inventory/view_item.html', 
                         item=item, 
                         transactions=transactions,
                         work_order_parts=work_order_parts)

@bp.route('/items/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    """Edit inventory item"""
    item = InventoryItem.query.get_or_404(id)
    form = InventoryItemForm(obj=item)
    
    # Populate category choices
    categories = InventoryCategory.query.order_by(InventoryCategory.name).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        # Check for duplicate part number (excluding current item)
        existing_item = InventoryItem.query.filter(
            InventoryItem.part_number == form.part_number.data,
            InventoryItem.id != id
        ).first()
        if existing_item:
            flash('Part number already exists. Please use a different part number.', 'error')
            return render_template('inventory/edit_item.html', form=form, item=item)
        
        # Update item
        item.part_number = form.part_number.data
        item.name = form.name.data
        item.description = form.description.data
        item.manufacturer = form.manufacturer.data
        item.model = form.model.data
        item.minimum_stock_level = form.minimum_stock_level.data
        item.maximum_stock_level = form.maximum_stock_level.data
        item.unit_cost = form.unit_cost.data
        item.weight = form.weight.data
        item.dimensions = form.dimensions.data
        item.compatible_uav_models = form.compatible_uav_models.data
        item.category_id = form.category_id.data
        item.is_active = form.is_active.data
        
        db.session.commit()
        flash(f'Inventory item "{item.name}" updated successfully.', 'success')
        return redirect(url_for('inventory.view_item', id=item.id))
    
    return render_template('inventory/edit_item.html', form=form, item=item)

@bp.route('/items/<int:id>/transaction', methods=['GET', 'POST'])
@login_required
def add_transaction(id):
    """Add inventory transaction (stock in/out/adjustment)"""
    item = InventoryItem.query.get_or_404(id)
    form = InventoryTransactionForm()
    
    if form.validate_on_submit():
        # Validate transaction
        if form.transaction_type.data == 'OUT' and form.quantity.data > item.quantity_in_stock:
            flash(f'Cannot remove {form.quantity.data} units. Only {item.quantity_in_stock} units available.', 'error')
            return render_template('inventory/add_transaction.html', form=form, item=item)
        
        # Calculate new quantity
        if form.transaction_type.data == 'IN':
            new_quantity = item.quantity_in_stock + form.quantity.data
        elif form.transaction_type.data == 'OUT':
            new_quantity = item.quantity_in_stock - form.quantity.data
        else:  # ADJUSTMENT
            new_quantity = form.quantity.data
        
        # Create transaction
        transaction = InventoryTransaction(
            item_id=item.id,
            transaction_type=form.transaction_type.data,
            quantity=form.quantity.data if form.transaction_type.data != 'ADJUSTMENT' else (form.quantity.data - item.quantity_in_stock),
            unit_cost=form.unit_cost.data,
            total_cost=(form.unit_cost.data or 0) * abs(form.quantity.data if form.transaction_type.data != 'ADJUSTMENT' else (form.quantity.data - item.quantity_in_stock)),
            reference_type=form.reference_type.data,
            reference_id=form.reference_id.data,
            notes=form.notes.data,
            created_by_id=current_user.id
        )
        
        # Update item quantity
        item.quantity_in_stock = new_quantity
        if form.transaction_type.data == 'IN':
            item.last_restocked = datetime.now(timezone.utc)
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Transaction recorded successfully. New stock level: {item.quantity_in_stock}', 'success')
        return redirect(url_for('inventory.view_item', id=item.id))
    
    return render_template('inventory/add_transaction.html', form=form, item=item)

@bp.route('/categories')
@login_required
def categories():
    """List inventory categories with calculated statistics"""
    # Get view mode from URL parameter (default to 'tiles')
    view_mode = request.args.get('view', 'tiles')
    
    # Get categories with calculated statistics
    categories_list = []
    categories = InventoryCategory.query.order_by(InventoryCategory.name).all()
    
    for category in categories:
        # Get active items for this category
        active_items = InventoryItem.query.filter_by(
            category_id=category.id, 
            is_active=True
        ).all()
        
        # Calculate statistics
        total_items = len(active_items)
        total_value = sum(item.quantity_in_stock * (item.unit_cost or 0) for item in active_items)
        low_stock_items = sum(1 for item in active_items 
                             if item.quantity_in_stock <= item.minimum_stock_level and item.quantity_in_stock > 0)
        out_of_stock_items = sum(1 for item in active_items 
                                if item.quantity_in_stock == 0)
        total_quantity = sum(item.quantity_in_stock for item in active_items)
        
        # Create category data object
        category_data = {
            'category': category,
            'total_items': total_items,
            'total_value': total_value,
            'total_quantity': total_quantity,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'has_alerts': low_stock_items > 0 or out_of_stock_items > 0
        }
        categories_list.append(category_data)
    
    return render_template('inventory/categories.html', 
                         categories_data=categories_list, 
                         view_mode=view_mode)

@bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create new inventory category"""
    form = InventoryCategoryForm()
    
    if form.validate_on_submit():
        category = InventoryCategory(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash(f'Category "{category.name}" created successfully.', 'success')
        return redirect(url_for('inventory.categories'))
    
    # Get existing categories for the sidebar
    existing_categories = InventoryCategory.query.order_by(InventoryCategory.name).all()
    return render_template('inventory/create_category.html', form=form, existing_categories=existing_categories)

@bp.route('/work-orders/<int:work_order_id>/parts')
@login_required
def work_order_parts(work_order_id):
    """List parts for a work order"""
    work_order = WorkOrder.query.get_or_404(work_order_id)
    parts = WorkOrderPart.query.filter_by(work_order_id=work_order_id).order_by(
        desc(WorkOrderPart.requested_at)
    ).all()
    
    return render_template('inventory/work_order_parts.html', 
                         work_order=work_order, parts=parts)

@bp.route('/work-orders/<int:work_order_id>/request-part', methods=['GET', 'POST'])
@login_required
def request_part(work_order_id):
    """Request part for work order"""
    work_order = WorkOrder.query.get_or_404(work_order_id)
    form = WorkOrderPartRequestForm()
    
    # Populate inventory item choices (only active items with stock)
    items = InventoryItem.query.filter(
        InventoryItem.is_active == True,
        InventoryItem.quantity_in_stock > 0
    ).order_by(InventoryItem.name).all()
    form.inventory_item_id.choices = [(item.id, f"{item.part_number} - {item.name} (Stock: {item.quantity_in_stock})") for item in items]
    
    if form.validate_on_submit():
        item = InventoryItem.query.get(form.inventory_item_id.data)
        
        # Check if enough stock available
        if form.quantity_requested.data > item.quantity_in_stock:
            flash(f'Cannot request {form.quantity_requested.data} units. Only {item.quantity_in_stock} units available.', 'error')
            return render_template('inventory/request_part.html', form=form, work_order=work_order)
        
        # Create part request
        part_request = WorkOrderPart(
            work_order_id=work_order_id,
            inventory_item_id=form.inventory_item_id.data,
            quantity_requested=form.quantity_requested.data,
            unit_cost=item.unit_cost,
            total_cost=(item.unit_cost or 0) * form.quantity_requested.data,
            notes=form.notes.data,
            requested_by_id=current_user.id,
            status='REQUESTED'
        )
        
        db.session.add(part_request)
        db.session.commit()
        
        flash(f'Part request submitted successfully for {item.name}.', 'success')
        return redirect(url_for('inventory.work_order_parts', work_order_id=work_order_id))
    
    return render_template('inventory/request_part.html', form=form, work_order=work_order)

@bp.route('/parts/<int:part_id>/allocate')
@login_required
def allocate_part(part_id):
    """Allocate requested part (reduce inventory)"""
    part = WorkOrderPart.query.get_or_404(part_id)
    
    if part.status != 'REQUESTED':
        flash('Part can only be allocated if it is in REQUESTED status.', 'error')
        return redirect(url_for('inventory.work_order_parts', work_order_id=part.work_order_id))
    
    item = part.inventory_item
    
    # Check stock availability
    if part.quantity_requested > item.quantity_in_stock:
        flash(f'Cannot allocate {part.quantity_requested} units. Only {item.quantity_in_stock} units available.', 'error')
        return redirect(url_for('inventory.work_order_parts', work_order_id=part.work_order_id))
    
    # Update inventory
    item.quantity_in_stock -= part.quantity_requested
    
    # Create inventory transaction
    transaction = InventoryTransaction(
        item_id=item.id,
        transaction_type='OUT',
        quantity=part.quantity_requested,
        unit_cost=item.unit_cost,
        total_cost=(item.unit_cost or 0) * part.quantity_requested,
        reference_type='WORKORDER',
        reference_id=part.work_order.work_order_number,
        notes=f'Allocated for Work Order {part.work_order.work_order_number}',
        created_by_id=current_user.id
    )
    
    # Update part status
    part.status = 'ALLOCATED'
    part.allocated_at = datetime.now(timezone.utc)
    part.allocated_by_id = current_user.id
    
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'Part {item.name} allocated successfully to Work Order {part.work_order.work_order_number}.', 'success')
    return redirect(url_for('inventory.work_order_parts', work_order_id=part.work_order_id))

@bp.route('/api/items/<int:item_id>/stock')
@login_required
def get_item_stock(item_id):
    """API endpoint to get current stock for an item"""
    item = InventoryItem.query.get_or_404(item_id)
    return jsonify({
        'stock': item.quantity_in_stock,
        'status': item.stock_status,
        'is_low_stock': item.is_low_stock
    })

@bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """Edit inventory category"""
    category = InventoryCategory.query.get_or_404(id)
    form = InventoryCategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash(f'Category "{category.name}" updated successfully.', 'success')
        return redirect(url_for('inventory.categories'))
    
    # Get existing categories for the sidebar
    existing_categories = InventoryCategory.query.order_by(InventoryCategory.name).all()
    return render_template('inventory/create_category.html', form=form, category=category, existing_categories=existing_categories)

@bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    """Delete inventory category"""
    category = InventoryCategory.query.get_or_404(id)
    
    # Check if category has items
    if category.items.count() > 0:
        flash(f'Cannot delete category "{category.name}" - it contains {category.items.count()} items.', 'error')
        return redirect(url_for('inventory.categories'))
    
    name = category.name
    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{name}" deleted successfully.', 'success')
    return redirect(url_for('inventory.categories'))
