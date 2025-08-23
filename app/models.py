"""
Database Models for Work Order Management System
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Role(db.Model):
    """User roles for access control"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    """User model with authentication and profile information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Foreign Keys
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    # Relationships
    created_workorders = db.relationship('WorkOrder', foreign_keys='WorkOrder.created_by_id', 
                                       backref='creator', lazy='dynamic')
    assigned_workorders = db.relationship('WorkOrder', foreign_keys='WorkOrder.assigned_to_id', 
                                        backref='assignee', lazy='dynamic')
    activities = db.relationship('WorkOrderActivity', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
    
    def has_role(self, role_name):
        """Check if user has specific role"""
        return self.role and self.role.name == role_name
    
    def can_edit_workorder(self, workorder):
        """Check if user can edit a work order"""
        if self.has_role('admin'):
            return True
        if self.has_role('manager'):
            return True
        if workorder.assigned_to_id == self.id:
            return True
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'

class Priority(db.Model):
    """Priority levels for work orders"""
    __tablename__ = 'priorities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 1=Low, 2=Medium, 3=High, 4=Critical
    color = db.Column(db.String(7), default='#6c757d')  # Hex color code
    
    # Relationships
    workorders = db.relationship('WorkOrder', backref='priority', lazy='dynamic')
    
    def __repr__(self):
        return f'<Priority {self.name}>'

class Status(db.Model):
    """Status options for work orders"""
    __tablename__ = 'statuses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(255))
    is_closed = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(7), default='#6c757d')
    
    # Relationships
    workorders = db.relationship('WorkOrder', backref='status', lazy='dynamic')
    
    def __repr__(self):
        return f'<Status {self.name}>'

class Category(db.Model):
    """Categories for work orders"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    workorders = db.relationship('WorkOrder', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class WorkOrder(db.Model):
    """Main work order model"""
    __tablename__ = 'workorders'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    product_name = db.Column(db.String(200))
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float, default=0.0)
    cost_estimate = db.Column(db.Numeric(10, 2))
    actual_cost = db.Column(db.Numeric(10, 2), default=0.0)
    due_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    priority_id = db.Column(db.Integer, db.ForeignKey('priorities.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # Relationships
    activities = db.relationship('WorkOrderActivity', backref='workorder', 
                               lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def is_overdue(self):
        """Check if work order is overdue"""
        if self.due_date and not self.status.is_closed:
            return datetime.now(timezone.utc) > self.due_date.replace(tzinfo=timezone.utc)
        return False
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.due_date and not self.status.is_closed:
            delta = self.due_date.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)
            return delta.days
        return None
    
    def add_activity(self, user, activity_type, description):
        """Add activity log entry"""
        activity = WorkOrderActivity(
            workorder_id=self.id,
            user_id=user.id,
            activity_type=activity_type,
            description=description
        )
        db.session.add(activity)
        return activity
    
    def __repr__(self):
        return f'<WorkOrder {self.id}: {self.title}>'

class WorkOrderActivity(db.Model):
    """Activity log for work orders"""
    __tablename__ = 'workorder_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(32), nullable=False)  # created, updated, assigned, completed, etc.
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    workorder_id = db.Column(db.Integer, db.ForeignKey('workorders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.activity_type}>'


class Company(db.Model):
    """Company information for product ownership"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    registration_number = db.Column(db.String(100), unique=True)
    website = db.Column(db.String(255))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    
    # Address Details
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    products = db.relationship('Product', backref='owner_company', lazy='dynamic')
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [self.address_line1, self.address_line2, self.city, self.state, self.postal_code, self.country]
        return ', '.join(filter(None, parts))
    
    def __repr__(self):
        return f'<Company {self.name}>'


class ProductCategory(db.Model):
    """Categories for UAV products"""
    __tablename__ = 'product_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.String(10), unique=True)
    
    # Relationships
    products = db.relationship('Product', backref='product_category', lazy='dynamic')
    
    def __repr__(self):
        return f'<ProductCategory {self.name}>'


class Product(db.Model):
    """UAV Product Master with comprehensive attributes"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    product_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    product_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Top 10 UAV Attributes
    # 1. Flight Performance
    max_flight_time = db.Column(db.Float)  # in minutes
    max_range = db.Column(db.Float)  # in kilometers
    max_altitude = db.Column(db.Float)  # in meters
    max_speed = db.Column(db.Float)  # in km/h
    
    # 2. Physical Specifications
    weight = db.Column(db.Float)  # in grams
    dimensions_length = db.Column(db.Float)  # in cm
    dimensions_width = db.Column(db.Float)  # in cm
    dimensions_height = db.Column(db.Float)  # in cm
    
    # 3. Camera & Payload
    camera_resolution = db.Column(db.String(50))  # e.g., "4K", "1080p"
    payload_capacity = db.Column(db.Float)  # in grams
    
    # 4. Battery & Power
    battery_type = db.Column(db.String(100))
    battery_capacity = db.Column(db.Integer)  # in mAh
    charging_time = db.Column(db.Float)  # in minutes
    
    # 5. Navigation & Control
    gps_enabled = db.Column(db.Boolean, default=True)
    autopilot_features = db.Column(db.Text)  # JSON or comma-separated features
    control_range = db.Column(db.Float)  # in meters
    
    # 6. Connectivity
    wifi_enabled = db.Column(db.Boolean, default=False)
    bluetooth_enabled = db.Column(db.Boolean, default=False)
    cellular_enabled = db.Column(db.Boolean, default=False)
    
    # 7. Environmental
    operating_temperature_min = db.Column(db.Float)  # in Celsius
    operating_temperature_max = db.Column(db.Float)  # in Celsius
    wind_resistance = db.Column(db.Float)  # in m/s
    water_resistance_rating = db.Column(db.String(10))  # IP rating
    
    # 8. Regulatory & Compliance
    certification_level = db.Column(db.String(50))  # CE, FCC, etc.
    flight_zone_restrictions = db.Column(db.Text)
    requires_license = db.Column(db.Boolean, default=False)
    
    # 9. Commercial Details
    manufacturer = db.Column(db.String(200))
    model_year = db.Column(db.Integer)
    warranty_period = db.Column(db.Integer)  # in months
    price = db.Column(db.Numeric(10, 2))
    
    # 10. Operational Use
    intended_use = db.Column(db.String(200))  # Agricultural, Surveillance, Photography, etc.
    skill_level_required = db.Column(db.String(50))  # Beginner, Intermediate, Professional
    
    # Servicing History
    last_serviced = db.Column(db.Date)  # Last service date
    next_service_due = db.Column(db.Date)  # Automatically calculated field (last_serviced + 90 days)
    
    # Status and Availability
    is_active = db.Column(db.Boolean, default=True)
    availability_status = db.Column(db.String(50), default='Available')  # Available, Discontinued, Pre-order
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    owner_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    specifications = db.relationship('ProductSpecification', backref='product', lazy='dynamic', 
                                   cascade='all, delete-orphan')
    images = db.relationship('ProductImage', backref='product', lazy='dynamic', 
                           cascade='all, delete-orphan')
    
    @property
    def dimensions_formatted(self):
        """Return formatted dimensions"""
        if self.dimensions_length and self.dimensions_width and self.dimensions_height:
            return f"{self.dimensions_length} x {self.dimensions_width} x {self.dimensions_height} cm"
        return "Not specified"
    
    @property
    def temperature_range(self):
        """Return formatted temperature range"""
        if self.operating_temperature_min is not None and self.operating_temperature_max is not None:
            return f"{self.operating_temperature_min}°C to {self.operating_temperature_max}°C"
        return "Not specified"
    
    @property
    def connectivity_features(self):
        """Return list of connectivity features"""
        features = []
        if self.wifi_enabled:
            features.append("WiFi")
        if self.bluetooth_enabled:
            features.append("Bluetooth")
        if self.cellular_enabled:
            features.append("Cellular")
        if self.gps_enabled:
            features.append("GPS")
        return features
    
    def get_specification(self, key):
        """Get specific specification value"""
        spec = self.specifications.filter_by(key=key).first()
        return spec.value if spec else None
    
    def set_specification(self, key, value, unit=None):
        """Set or update specification"""
        spec = self.specifications.filter_by(key=key).first()
        if spec:
            spec.value = value
            spec.unit = unit
        else:
            spec = ProductSpecification(product_id=self.id, key=key, value=value, unit=unit)
            db.session.add(spec)
        return spec
    
    def update_next_service_due(self):
        """Automatically calculate next service due date (90 days from last serviced)"""
        if self.last_serviced:
            from datetime import timedelta
            self.next_service_due = self.last_serviced + timedelta(days=90)
        else:
            self.next_service_due = None
    
    @property
    def service_status(self):
        """Return service status based on next service due date"""
        if not self.next_service_due:
            return "No service history"
        
        from datetime import date
        today = date.today()
        days_until_service = (self.next_service_due - today).days
        
        if days_until_service < 0:
            return f"Overdue by {abs(days_until_service)} days"
        elif days_until_service <= 7:
            return f"Due in {days_until_service} days"
        elif days_until_service <= 30:
            return f"Due in {days_until_service} days"
        else:
            return f"Due in {days_until_service} days"
    
    @property
    def service_status_class(self):
        """Return CSS class for service status"""
        if not self.next_service_due:
            return "text-muted"
        
        from datetime import date
        today = date.today()
        days_until_service = (self.next_service_due - today).days
        
        if days_until_service < 0:
            return "text-danger"  # Overdue
        elif days_until_service <= 7:
            return "text-warning"  # Due soon
        elif days_until_service <= 30:
            return "text-info"  # Due this month
        else:
            return "text-success"  # Not due yet
    
    def __repr__(self):
        return f'<Product {self.product_code}: {self.product_name}>'


class ProductSpecification(db.Model):
    """Additional specifications for products"""
    __tablename__ = 'product_specifications'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(50))
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    def __repr__(self):
        return f'<ProductSpec {self.key}: {self.value}>'


class ProductImage(db.Model):
    """Product images and documentation"""
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    image_type = db.Column(db.String(50))  # main, gallery, specification, manual
    description = db.Column(db.Text)
    is_primary = db.Column(db.Boolean, default=False)
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<ProductImage {self.filename}>'
