"""
Product Management Routes
"""

from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc, or_, and_
from app import db
from app.products import bp
from app.products.forms import ProductForm, CompanyForm, ProductCategoryForm, ProductSearchForm, ProductSpecificationForm
from app.models import Product, Company, ProductCategory, ProductSpecification, ProductImage


# AJAX endpoint to get owner_name for a given product
@bp.route('/get_owner/<int:product_id>')
def get_owner(product_id):
    """Return owner company name for a given product (AJAX)"""
    product = Product.query.get(product_id)
    owner_name = ""
    if product and product.owner_company:
        owner_name = product.owner_company.name
    return jsonify({'owner_name': owner_name})
"""
Product Management Routes
"""

from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc, or_, and_
from app import db
from app.products import bp
from app.products.forms import ProductForm, CompanyForm, ProductCategoryForm, ProductSearchForm, ProductSpecificationForm
from app.models import Product, Company, ProductCategory, ProductSpecification, ProductImage


@bp.route('/')
@login_required
def list_products():
    """List all products with search and filter capabilities"""
    form = ProductSearchForm()
    
    # Base query
    query = Product.query
    
    # Apply filters
    if request.args.get('search_term'):
        search_term = f"%{request.args.get('search_term')}%"
        query = query.filter(
            or_(
                Product.product_name.ilike(search_term),
                Product.product_code.ilike(search_term),
                Product.description.ilike(search_term),
                Product.manufacturer.ilike(search_term)
            )
        )
        form.search_term.data = request.args.get('search_term')
    
    if request.args.get('category_id') and int(request.args.get('category_id')) > 0:
        query = query.filter(Product.category_id == int(request.args.get('category_id')))
        form.category_id.data = int(request.args.get('category_id'))
    
    if request.args.get('company_id') and int(request.args.get('company_id')) > 0:
        query = query.filter(Product.owner_company_id == int(request.args.get('company_id')))
        form.company_id.data = int(request.args.get('company_id'))
    
    if request.args.get('availability_status'):
        query = query.filter(Product.availability_status == request.args.get('availability_status'))
        form.availability_status.data = request.args.get('availability_status')
    
    if request.args.get('skill_level'):
        query = query.filter(Product.skill_level_required == request.args.get('skill_level'))
        form.skill_level.data = request.args.get('skill_level')
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    products = query.order_by(desc(Product.created_at)).paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Statistics
    stats = {
        'total_products': Product.query.count(),
        'active_products': Product.query.filter_by(is_active=True).count(),
        'available_products': Product.query.filter_by(availability_status='Available').count(),
        'total_companies': Company.query.count()
    }
    
    return render_template('products/list.html', 
                         products=products, 
                         form=form, 
                         stats=stats)


@bp.route('/<int:id>')
@login_required
def view_product(id):
    """View product details"""
    product = Product.query.get_or_404(id)
    specifications = product.specifications.all()
    images = product.images.all()
    
    return render_template('products/view.html', 
                         product=product, 
                         specifications=specifications, 
                         images=images)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_product():
    """Create new product"""
    if not current_user.has_role('admin') and not current_user.has_role('manager'):
        abort(403)
    
    form = ProductForm()
    
    if form.validate_on_submit():
        product = Product(
            product_code=form.product_code.data,
            product_name=form.product_name.data,
            description=form.description.data,
            category_id=form.category_id.data if form.category_id.data > 0 else None,
            owner_company_id=form.owner_company_id.data,
            created_by_id=current_user.id,
            
            # Flight Performance
            max_flight_time=form.max_flight_time.data,
            max_range=form.max_range.data,
            max_altitude=form.max_altitude.data,
            max_speed=form.max_speed.data,
            
            # Physical Specifications
            weight=form.weight.data,
            dimensions_length=form.dimensions_length.data,
            dimensions_width=form.dimensions_width.data,
            dimensions_height=form.dimensions_height.data,
            
            # Camera & Payload
            camera_resolution=form.camera_resolution.data,
            payload_capacity=form.payload_capacity.data,
            
            # Battery & Power
            battery_type=form.battery_type.data,
            battery_capacity=form.battery_capacity.data,
            charging_time=form.charging_time.data,
            
            # Navigation & Control
            gps_enabled=form.gps_enabled.data,
            autopilot_features=form.autopilot_features.data,
            control_range=form.control_range.data,
            
            # Connectivity
            wifi_enabled=form.wifi_enabled.data,
            bluetooth_enabled=form.bluetooth_enabled.data,
            cellular_enabled=form.cellular_enabled.data,
            
            # Environmental
            operating_temperature_min=form.operating_temperature_min.data,
            operating_temperature_max=form.operating_temperature_max.data,
            wind_resistance=form.wind_resistance.data,
            water_resistance_rating=form.water_resistance_rating.data,
            
            # Regulatory & Compliance
            certification_level=form.certification_level.data,
            flight_zone_restrictions=form.flight_zone_restrictions.data,
            requires_license=form.requires_license.data,
            
            # Commercial Details
            manufacturer=form.manufacturer.data,
            model_year=form.model_year.data,
            warranty_period=form.warranty_period.data,
            price=form.price.data,
            
            # Operational Use
            intended_use=form.intended_use.data,
            skill_level_required=form.skill_level_required.data,
            
            # Servicing History
            last_serviced=form.last_serviced.data,
            
            # Status
            availability_status=form.availability_status.data,
            is_active=form.is_active.data
        )
        
        # Calculate next service due date automatically
        product.update_next_service_due()
        
        db.session.add(product)
        db.session.commit()
        
        flash(f'Product "{product.product_name}" has been created successfully!', 'success')
        return redirect(url_for('products.view_product', id=product.id))
    
    return render_template('products/create.html', form=form)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    """Edit product"""
    if not current_user.has_role('admin') and not current_user.has_role('manager'):
        abort(403)
    
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        # Update all form fields
        form.populate_obj(product)
        
        # Handle category selection
        if form.category_id.data == 0:
            product.category_id = None
        
        # Calculate next service due date automatically if last_serviced changed
        product.update_next_service_due()
        
        db.session.commit()
        
        flash(f'Product "{product.product_name}" has been updated successfully!', 'success')
        return redirect(url_for('products.view_product', id=product.id))
    
    return render_template('products/edit.html', form=form, product=product)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_product(id):
    """Delete product"""
    if not current_user.has_role('admin'):
        abort(403)
    
    product = Product.query.get_or_404(id)
    product_name = product.product_name
    
    db.session.delete(product)
    db.session.commit()
    
    flash(f'Product "{product_name}" has been deleted successfully!', 'success')
    return redirect(url_for('products.list_products'))


@bp.route('/<int:id>/specifications')
@login_required
def view_specifications(id):
    """View product specifications"""
    product = Product.query.get_or_404(id)
    specifications = product.specifications.all()
    
    return render_template('products/specifications.html', 
                         product=product, 
                         specifications=specifications)


@bp.route('/<int:id>/add-specification', methods=['GET', 'POST'])
@login_required
def add_specification(id):
    """Add custom specification to product"""
    if not current_user.has_role('admin') and not current_user.has_role('manager'):
        abort(403)
    
    product = Product.query.get_or_404(id)
    form = ProductSpecificationForm()
    
    if form.validate_on_submit():
        specification = ProductSpecification(
            product_id=product.id,
            key=form.key.data,
            value=form.value.data,
            unit=form.unit.data
        )
        
        db.session.add(specification)
        db.session.commit()
        
        flash(f'Specification "{specification.key}" has been added successfully!', 'success')
        return redirect(url_for('products.view_specifications', id=product.id))
    
    return render_template('products/add_specification.html', form=form, product=product)


# Company Management Routes
@bp.route('/companies')
@login_required
def list_companies():
    """List all companies"""
    page = request.args.get('page', 1, type=int)
    companies = Company.query.order_by(Company.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('products/companies.html', companies=companies)


@bp.route('/companies/<int:id>')
@login_required
def view_company(id):
    """View company details"""
    company = Company.query.get_or_404(id)
    products = company.products.filter_by(is_active=True).all()
    
    return render_template('products/company_detail.html', company=company, products=products)


@bp.route('/companies/create', methods=['GET', 'POST'])
@login_required
def create_company():
    """Create new company"""
    if not current_user.has_role('admin') and not current_user.has_role('manager'):
        abort(403)
    
    form = CompanyForm()
    
    if form.validate_on_submit():
        company = Company()
        form.populate_obj(company)
        
        db.session.add(company)
        db.session.commit()
        
        flash(f'Company "{company.name}" has been created successfully!', 'success')
        return redirect(url_for('products.view_company', id=company.id))
    
    return render_template('products/create_company.html', form=form)


@bp.route('/companies/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_company(id):
    """Edit company"""
    if not current_user.has_role('admin') and not current_user.has_role('manager'):
        abort(403)
    
    company = Company.query.get_or_404(id)
    form = CompanyForm(obj=company)
    
    if form.validate_on_submit():
        form.populate_obj(company)
        db.session.commit()
        
        flash(f'Company "{company.name}" has been updated successfully!', 'success')
        return redirect(url_for('products.view_company', id=company.id))
    
    return render_template('products/edit_company.html', form=form, company=company)


@bp.route('/companies/<int:id>/delete', methods=['POST'])
@login_required
def delete_company(id):
    """Delete company (admin only)"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to delete companies.', 'error')
        return redirect(url_for('products.view_company', id=id))
    
    company = Company.query.get_or_404(id)
    
    # Check if company has associated products
    if company.products.count() > 0:
        flash('Cannot delete company with associated products. Please remove or transfer products first.', 'error')
        return redirect(url_for('products.view_company', id=id))
    
    company_name = company.name
    db.session.delete(company)
    db.session.commit()
    
    flash(f'Company "{company_name}" has been deleted successfully.', 'success')
    return redirect(url_for('products.list_companies'))


# Category Management Routes
@bp.route('/categories')
@login_required
def list_categories():
    """List all product categories"""
    categories = ProductCategory.query.order_by(ProductCategory.name).all()
    return render_template('products/categories.html', categories=categories)


@bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create new product category"""
    if not current_user.has_role('admin') and not current_user.has_role('manager'):
        abort(403)
    
    form = ProductCategoryForm()
    
    if form.validate_on_submit():
        category = ProductCategory()
        form.populate_obj(category)
        
        db.session.add(category)
        db.session.commit()
        
        flash(f'Category "{category.name}" has been created successfully!', 'success')
        return redirect(url_for('products.list_categories'))
    
    return render_template('products/create_category.html', form=form)


# API Endpoints
@bp.route('/api/products')
@login_required
def api_products():
    """API endpoint for product data"""
    products = Product.query.filter_by(is_active=True).all()
    
    data = [{
        'id': p.id,
        'code': p.product_code,
        'name': p.product_name,
        'manufacturer': p.manufacturer,
        'price': float(p.price) if p.price else 0,
        'company': p.owner_company.name,
        'category': p.product_category.name if p.product_category else 'Uncategorized'
    } for p in products]
    
    return jsonify(data)


@bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for product statistics"""
    stats = {
        'total_products': Product.query.count(),
        'active_products': Product.query.filter_by(is_active=True).count(),
        'companies': Company.query.count(),
        'categories': ProductCategory.query.count(),
        'by_category': []
    }
    
    # Products by category
    categories = ProductCategory.query.all()
    for category in categories:
        stats['by_category'].append({
            'name': category.name,
            'count': category.products.filter_by(is_active=True).count()
        })
    
    return jsonify(stats)
