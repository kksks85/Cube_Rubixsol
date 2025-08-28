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


class AssignmentGroup(db.Model):
    """Assignment groups for organizing users and work order distribution"""
    __tablename__ = 'assignment_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    department = db.Column(db.String(64))
    priority_level = db.Column(db.String(20), default='standard')  # standard, high, critical
    
    # Configuration settings
    auto_assign = db.Column(db.Boolean, default=False)
    round_robin = db.Column(db.Boolean, default=False)
    notification_enabled = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Assignment criteria (stored as JSON strings)
    work_order_types = db.Column(db.Text)  # JSON array of work order types
    priority_filter = db.Column(db.Text)   # JSON array of priority filters
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    members = db.relationship('AssignmentGroupMember', backref='group', lazy='dynamic', 
                             cascade='all, delete-orphan')
    
    @property
    def member_count(self):
        """Get number of members in the group"""
        return self.members.filter_by(is_active=True).count()
    
    @property
    def work_order_types_list(self):
        """Get work order types as a list"""
        if self.work_order_types:
            import json
            try:
                return json.loads(self.work_order_types)
            except:
                return []
        return []
    
    @property
    def priority_filter_list(self):
        """Get priority filters as a list"""
        if self.priority_filter:
            import json
            try:
                return json.loads(self.priority_filter)
            except:
                return []
        return []
    
    def set_work_order_types(self, types_list):
        """Set work order types from a list"""
        import json
        self.work_order_types = json.dumps(types_list) if types_list else None
    
    def set_priority_filter(self, priority_list):
        """Set priority filters from a list"""
        import json
        self.priority_filter = json.dumps(priority_list) if priority_list else None
    
    def __repr__(self):
        return f'<AssignmentGroup {self.name} ({self.code})>'


class AssignmentGroupMember(db.Model):
    """Members of assignment groups"""
    __tablename__ = 'assignment_group_members'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('assignment_groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_leader = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Unique constraint to prevent duplicate memberships
    __table_args__ = (db.UniqueConstraint('group_id', 'user_id', name='_group_user_uc'),)
    
    # Relationships
    user = db.relationship('User', backref='group_memberships')
    
    def __repr__(self):
        return f'<AssignmentGroupMember {self.user.username} in {self.group.name}>'


class AssignmentRule(db.Model):
    """Assignment rules for automatic incident assignment"""
    __tablename__ = 'assignment_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Integer, nullable=False, default=5)  # 1=highest, 5=lowest
    is_active = db.Column(db.Boolean, default=True)
    
    # Rule conditions (JSON field)
    conditions = db.Column(db.JSON)  # Store conditions as JSON
    
    # Assignment actions (JSON field)
    actions = db.Column(db.JSON)  # Store assignment actions as JSON
    
    # Rule settings (JSON field)
    settings = db.Column(db.JSON)  # Store settings as JSON
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Statistics
    times_triggered = db.Column(db.Integer, default=0)
    last_triggered_at = db.Column(db.DateTime)
    
    # Relationships
    creator = db.relationship('User', backref='created_assignment_rules')
    
    def __repr__(self):
        return f'<AssignmentRule {self.name} (Priority: {self.priority})>'
    
    @property
    def condition_summary(self):
        """Get a human-readable summary of conditions"""
        if not self.conditions:
            return "No specific conditions"
        
        conditions = []
        if self.conditions.get('incident_category'):
            conditions.append(f"Category: {self.conditions['incident_category']}")
        if self.conditions.get('priority'):
            conditions.append(f"Priority: {self.conditions['priority']}")
        if self.conditions.get('department'):
            conditions.append(f"Department: {self.conditions['department']}")
        
        return "; ".join(conditions) if conditions else "No specific conditions"
    
    @property
    def action_summary(self):
        """Get a human-readable summary of actions"""
        if not self.actions:
            return "No actions defined"
        
        assignment_type = self.actions.get('assignment_type', 'unknown')
        if assignment_type == 'specific_user':
            user_id = self.actions.get('target_user_id')
            if user_id:
                user = User.query.get(user_id)
                return f"Assign to user: {user.full_name if user else 'Unknown User'}"
        elif assignment_type == 'assignment_group':
            group_id = self.actions.get('target_group_id')
            if group_id:
                group = AssignmentGroup.query.get(group_id)
                return f"Assign to group: {group.name if group else 'Unknown Group'}"
        elif assignment_type == 'round_robin':
            return "Round robin assignment"
        elif assignment_type == 'load_balancing':
            return "Load balancing assignment"
        elif assignment_type == 'skill_based':
            return "Skill-based assignment"
        
        return f"Assignment type: {assignment_type}"


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
    """Status options for work orders - DEPRECATED, use WorkOrderStatus instead"""
    __tablename__ = 'statuses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(255))
    is_closed = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(7), default='#6c757d')
    
    # Relationships - COMMENTED OUT to avoid conflicts with WorkOrderStatus
    # workorders = db.relationship('WorkOrder', backref='status', lazy='dynamic')
    
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
    address = db.Column(db.String(200))
    product_name = db.Column(db.String(200))
    owner_name = db.Column(db.String(200))
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
    assignment_group_id = db.Column(db.Integer, db.ForeignKey('assignment_groups.id'))  # New field
    priority_id = db.Column(db.Integer, db.ForeignKey('priorities.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('workorder_statuses.id'), nullable=True)  # Updated to use workorder_statuses
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    uav_service_incident_id = db.Column(db.Integer, db.ForeignKey('uav_service_incidents.id'))  # Link to incident
    
    # Relationships
    activities = db.relationship('WorkOrderActivity', backref='workorder', 
                               lazy='dynamic', cascade='all, delete-orphan')
    parts = db.relationship('WorkOrderPart', backref='workorder', 
                          lazy='dynamic', cascade='all, delete-orphan')
    assignment_group = db.relationship('AssignmentGroup', backref='assigned_workorders')
    
    @property
    def is_overdue(self):
        """Check if work order is overdue"""
        if self.due_date and self.status_detail and not self.status_detail.is_final:
            return datetime.now(timezone.utc) > self.due_date.replace(tzinfo=timezone.utc)
        return False
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.due_date and self.status_detail and not self.status_detail.is_final:
            delta = self.due_date.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)
            return delta.days
        return None
    
    @property
    def work_order_number(self):
        """Return formatted work order number"""
        return f"WO-{self.id:05d}"
    
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
        return f'<WorkOrder {self.work_order_number}: {self.title}>'

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
    serial_number = db.Column(db.String(40), nullable=True, index=True)
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


class WorkOrderStatus(db.Model):
    """Enhanced work order status with workflow support"""
    __tablename__ = 'workorder_statuses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    order_index = db.Column(db.Integer, default=0)  # For stage ordering
    is_initial = db.Column(db.Boolean, default=False)  # Initial status
    is_final = db.Column(db.Boolean, default=False)   # Final status
    requires_approval = db.Column(db.Boolean, default=False)  # Needs admin approval
    color = db.Column(db.String(7), default='#6c757d')  # Status color
    icon = db.Column(db.String(50), default='fas fa-circle')  # Status icon
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    workorders = db.relationship('WorkOrder', backref='status_detail', lazy='dynamic')
    transitions_from = db.relationship('WorkOrderStatusTransition', 
                                     foreign_keys='WorkOrderStatusTransition.from_status_id',
                                     backref='from_status', lazy='dynamic')
    transitions_to = db.relationship('WorkOrderStatusTransition',
                                   foreign_keys='WorkOrderStatusTransition.to_status_id', 
                                   backref='to_status', lazy='dynamic')

    def __repr__(self):
        return f'<WorkOrderStatus {self.name}>'


class WorkOrderStatusTransition(db.Model):
    """Define allowed status transitions"""
    __tablename__ = 'workorder_status_transitions'
    
    id = db.Column(db.Integer, primary_key=True)
    from_status_id = db.Column(db.Integer, db.ForeignKey('workorder_statuses.id'), nullable=False)
    to_status_id = db.Column(db.Integer, db.ForeignKey('workorder_statuses.id'), nullable=False)
    requires_role = db.Column(db.String(50))  # Role required for this transition
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<WorkOrderStatusTransition {self.from_status.name} -> {self.to_status.name}>'


class WorkOrderApproval(db.Model):
    """Track approval workflow for work orders"""
    __tablename__ = 'workorder_approvals'
    
    id = db.Column(db.Integer, primary_key=True)
    workorder_id = db.Column(db.Integer, db.ForeignKey('workorders.id'), nullable=False)
    requested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    comments = db.Column(db.Text)
    requested_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    approved_at = db.Column(db.DateTime)
    
    # Relationships
    workorder = db.relationship('WorkOrder', backref='approvals')
    requested_by = db.relationship('User', foreign_keys=[requested_by_id], backref='approval_requests')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='approval_decisions')

    def __repr__(self):
        return f'<WorkOrderApproval WO#{self.workorder_id} - {self.status}>'


class EmailConfig(db.Model):
    """Email configuration settings"""
    __tablename__ = 'email_config'
    
    id = db.Column(db.Integer, primary_key=True)
    smtp_server = db.Column(db.String(255), default='smtp.gmail.com')
    smtp_port = db.Column(db.Integer, default=587)
    use_tls = db.Column(db.Boolean, default=True)
    sender_email = db.Column(db.String(255))
    sender_name = db.Column(db.String(255), default='CUBE - PRO System')
    smtp_username = db.Column(db.String(255))
    smtp_password = db.Column(db.String(255))  # Should be encrypted in production
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<EmailConfig {self.sender_email}>'


class EmailLog(db.Model):
    """Email sending log for tracking statistics"""
    __tablename__ = 'email_log'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500))
    status = db.Column(db.String(50), default='sent')  # sent, failed, pending
    error_message = db.Column(db.Text)
    template_type = db.Column(db.String(100))  # work_order, user_welcome, password_reset, etc.
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    work_order_id = db.Column(db.Integer, db.ForeignKey('workorders.id'))
    
    # Relationships
    user = db.relationship('User', backref='email_logs')
    work_order = db.relationship('WorkOrder', backref='email_logs')
    
    def __repr__(self):
        return f'<EmailLog {self.recipient_email} - {self.status}>'


class EmailTemplate(db.Model):
    """Email templates for different types of notifications"""
    __tablename__ = 'email_template'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    template_type = db.Column(db.String(100), nullable=False)  # work_order_assigned, user_welcome, etc.
    subject = db.Column(db.String(500), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_html = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    created_by = db.relationship('User', backref='created_email_templates')
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'

# Inventory Management Models

class InventoryCategory(db.Model):
    """Categories for inventory items (e.g., UAV Parts, Sensors, Batteries)"""
    __tablename__ = 'inventory_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    items = db.relationship('InventoryItem', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<InventoryCategory {self.name}>'

class InventoryItem(db.Model):
    """Individual inventory items/parts"""
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    
    # Stock Information
    quantity_in_stock = db.Column(db.Integer, default=0, nullable=False)
    minimum_stock_level = db.Column(db.Integer, default=0)
    maximum_stock_level = db.Column(db.Integer, default=100)
    condition = db.Column(db.String(20), default='new', nullable=False)  # 'new' or 'faulty'
    unit_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Item Details
    weight = db.Column(db.Numeric(8, 3))  # in kg
    dimensions = db.Column(db.String(100))  # e.g., "10x5x2 cm"
    compatible_uav_models = db.Column(db.Text)  # JSON or comma-separated
    
    # Status and Tracking
    is_active = db.Column(db.Boolean, default=True)
    last_restocked = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_categories.id'))
    
    # Relationships
    transactions = db.relationship('InventoryTransaction', backref='item', lazy='dynamic')
    work_order_parts = db.relationship('WorkOrderPart', backref='inventory_item', lazy='dynamic')
    
    @property
    def is_low_stock(self):
        """Check if item is below minimum stock level"""
        return self.quantity_in_stock <= self.minimum_stock_level
    
    @property
    def stock_status(self):
        """Get stock status as string"""
        if self.quantity_in_stock == 0:
            return "Out of Stock"
        elif self.is_low_stock:
            return "Low Stock"
        elif self.quantity_in_stock >= self.maximum_stock_level:
            return "Overstock"
        else:
            return "In Stock"
    
    def __repr__(self):
        return f'<InventoryItem {self.part_number}: {self.name}>'

class InventoryTransaction(db.Model):
    """Track all inventory movements (in/out/adjustments)"""
    __tablename__ = 'inventory_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'IN', 'OUT', 'ADJUSTMENT'
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2))
    total_cost = db.Column(db.Numeric(10, 2))
    
    # Reference Information
    reference_type = db.Column(db.String(50))  # 'PURCHASE', 'WORKORDER', 'ADJUSTMENT', 'RETURN'
    reference_id = db.Column(db.String(50))  # ID of related record
    notes = db.Column(db.Text)
    
    # Tracking
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    created_by = db.relationship('User', backref='inventory_transactions')
    
    def __repr__(self):
        return f'<InventoryTransaction {self.transaction_type}: {self.quantity} units>'

class WorkOrderPart(db.Model):
    """Parts requested/used in work orders"""
    __tablename__ = 'work_order_parts'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity_requested = db.Column(db.Integer, nullable=False)
    quantity_used = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='REQUESTED')  # 'REQUESTED', 'ALLOCATED', 'USED', 'RETURNED'
    
    # Cost tracking
    unit_cost = db.Column(db.Numeric(10, 2))
    total_cost = db.Column(db.Numeric(10, 2))
    
    # Notes and tracking
    notes = db.Column(db.Text)
    requested_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    allocated_at = db.Column(db.DateTime)
    used_at = db.Column(db.DateTime)
    
    # Foreign Keys
    work_order_id = db.Column(db.Integer, db.ForeignKey('workorders.id'), nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    requested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    allocated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    requested_by = db.relationship('User', foreign_keys=[requested_by_id], backref='requested_parts')
    allocated_by = db.relationship('User', foreign_keys=[allocated_by_id], backref='allocated_parts')
    
    @property
    def status_badge_class(self):
        """Get Bootstrap badge class for status"""
        status_classes = {
            'REQUESTED': 'bg-warning',
            'ALLOCATED': 'bg-info',
            'USED': 'bg-success',
            'RETURNED': 'bg-secondary'
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    def __repr__(self):
        return f'<WorkOrderPart WO-{self.work_order_id}: {self.quantity_requested} units>'


# UAV Service Management Models
class UAVServiceIncident(db.Model):
    """UAV Service Incident Management System"""
    __tablename__ = 'uav_service_incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Incident Details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    incident_category = db.Column(db.String(50), nullable=False)  # 'BATTERY', 'CAMERA', 'CRASH_REPAIR', 'ROUTINE_MAINTENANCE', 'OTHER'
    priority = db.Column(db.String(20), default='MEDIUM')  # 'LOW', 'MEDIUM', 'HIGH', 'URGENT'
    
    # 6-Step Workflow Status (updated)
    workflow_status = db.Column(db.String(50), default='INCIDENT_RAISED')
    # Workflow stages: INCIDENT_RAISED, DIAGNOSIS_WO, REPAIR_MAINTENANCE, QUALITY_CHECK, PREVENTIVE_MAINTENANCE, CLOSED
    
    # Customer Information
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(120))
    customer_phone = db.Column(db.String(20))
    customer_address = db.Column(db.Text)
    customer_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # Reference to User table
    
    # UAV Equipment Details (New format)
    serial_number = db.Column(db.String(40), index=True)
    product_name = db.Column(db.String(100))
    owner_company = db.Column(db.String(100))
    last_service_date = db.Column(db.Date)
    
    # UAV Information (Legacy fields - kept for backward compatibility)
    uav_model = db.Column(db.String(100))  # Made nullable for transition
    uav_serial_number = db.Column(db.String(100))
    flight_hours = db.Column(db.Integer, default=0)
    last_maintenance_date = db.Column(db.DateTime)
    
    # SLA and Service Tracking
    sla_category = db.Column(db.String(30), default='STANDARD')  # 'EXPRESS', 'STANDARD', 'ECONOMY'
    sla_response_hours = db.Column(db.Integer, default=24)
    sla_resolution_hours = db.Column(db.Integer, default=72)
    
    # Workflow Timestamps
    incident_raised_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    technician_assigned_at = db.Column(db.DateTime)
    diagnosis_completed_at = db.Column(db.DateTime)
    work_order_created_at = db.Column(db.DateTime)
    repair_started_at = db.Column(db.DateTime)
    repair_completed_at = db.Column(db.DateTime)
    quality_check_at = db.Column(db.DateTime)
    handed_over_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)  # New timestamp for closed status
    
    # Diagnosis and Work Order
    diagnostic_checklist_completed = db.Column(db.Boolean, default=False)
    diagnostic_findings = db.Column(db.Text)
    work_order_type = db.Column(db.String(30))  # 'REPAIR', 'REPLACE', 'MAINTENANCE'
    
    # Repair/Maintenance Details
    parts_requested = db.Column(db.Boolean, default=False)
    parts_received = db.Column(db.Boolean, default=False)
    technician_hours = db.Column(db.Numeric(5, 2), default=0.00)
    technician_notes = db.Column(db.Text)
    service_status = db.Column(db.String(30), default='PENDING')  # 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'PENDING_PARTS'
    
    # Quality Check
    qa_verified = db.Column(db.Boolean, default=False)
    airworthiness_certified = db.Column(db.Boolean, default=False)
    qa_notes = db.Column(db.Text)
    
    # Billing and Warranty
    is_warranty_service = db.Column(db.Boolean, default=True)
    estimated_cost = db.Column(db.Numeric(10, 2))
    actual_cost = db.Column(db.Numeric(10, 2))
    invoice_generated = db.Column(db.Boolean, default=False)
    invoice_number = db.Column(db.String(50))
    
    # Preventive Maintenance
    is_preventive_maintenance = db.Column(db.Boolean, default=False)
    next_maintenance_due = db.Column(db.DateTime)
    maintenance_type = db.Column(db.String(50))  # 'SCHEDULED', 'FLIGHT_HOURS', 'TIME_BASED'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    qa_technician_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    related_work_order_id = db.Column(db.Integer, db.ForeignKey('workorders.id'))
    
    # Relationships
    product = db.relationship('Product', backref='uav_service_incidents')
    technician = db.relationship('User', foreign_keys=[technician_id], backref='assigned_uav_services')
    qa_technician = db.relationship('User', foreign_keys=[qa_technician_id], backref='qa_uav_services')
    creator = db.relationship('User', foreign_keys=[created_by_id], backref='created_uav_services')
    customer_user = db.relationship('User', foreign_keys=[customer_user_id], backref='customer_uav_services')
    related_work_order = db.relationship('WorkOrder', foreign_keys='UAVServiceIncident.related_work_order_id', backref='uav_service_incident')
    
    @property
    def incident_number_formatted(self):
        """Return formatted incident number"""
        return f"UAV-{self.id:06d}"
    
    @property
    def workflow_step_info(self):
        """Get current workflow step information"""
        workflow_steps = {
            'INCIDENT_RAISED': {'step': 1, 'name': 'Incident/Service Request', 'description': 'Customer reported issue, categorized and logged'},
            'DIAGNOSIS_WO': {'step': 2, 'name': 'Diagnosis & Work Order', 'description': 'Technician assigned, diagnosis completed, work order created'},
            'REPAIR_MAINTENANCE': {'step': 3, 'name': 'Repair/Maintenance', 'description': 'Parts requested, technician performing work'},
            'QUALITY_CHECK': {'step': 4, 'name': 'Quality Check & Handover', 'description': 'QA verification, compliance check, customer handover'},
            'PREVENTIVE_MAINTENANCE': {'step': 5, 'name': 'Preventive Maintenance', 'description': 'Scheduled maintenance triggered automatically'},
            'CLOSED': {'step': 6, 'name': 'Closed', 'description': 'Service completed and incident closed'}
        }
        return workflow_steps.get(self.workflow_status, workflow_steps['INCIDENT_RAISED'])
    
    @property
    def workflow_progress_percentage(self):
        """Calculate workflow progress percentage"""
        step = self.workflow_step_info['step']
        return (step / 6) * 100
    
    @property
    def is_sla_breached(self):
        """Check if SLA is breached"""
        if self.workflow_status in ['QUALITY_CHECK', 'PREVENTIVE_MAINTENANCE', 'CLOSED']:
            return False  # Service completed
        
        hours_elapsed = (datetime.now(timezone.utc) - self.incident_raised_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600
        return hours_elapsed > self.sla_resolution_hours
    
    @property
    def sla_status(self):
        """Get SLA status"""
        if self.is_sla_breached:
            return 'BREACHED'
        
        hours_elapsed = (datetime.now(timezone.utc) - self.incident_raised_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600
        remaining_hours = self.sla_resolution_hours - hours_elapsed
        
        if remaining_hours <= 4:
            return 'CRITICAL'
        elif remaining_hours <= 12:
            return 'WARNING'
        else:
            return 'ON_TRACK'
    
    def advance_workflow(self, user, notes=None):
        """Advance to next workflow step"""
        current_step = self.workflow_step_info['step']
        
        if current_step == 1 and self.workflow_status == 'INCIDENT_RAISED':
            self.workflow_status = 'DIAGNOSIS_WO'
            self.technician_assigned_at = datetime.now(timezone.utc)
        elif current_step == 2 and self.workflow_status == 'DIAGNOSIS_WO':
            self.workflow_status = 'REPAIR_MAINTENANCE'
            self.work_order_created_at = datetime.now(timezone.utc)
            self.repair_started_at = datetime.now(timezone.utc)
        elif current_step == 3 and self.workflow_status == 'REPAIR_MAINTENANCE':
            self.workflow_status = 'QUALITY_CHECK'
            self.repair_completed_at = datetime.now(timezone.utc)
            self.quality_check_at = datetime.now(timezone.utc)
        elif current_step == 4 and self.workflow_status == 'QUALITY_CHECK':
            self.workflow_status = 'PREVENTIVE_MAINTENANCE'
            self.handed_over_at = datetime.now(timezone.utc)
        elif current_step == 5 and self.workflow_status == 'PREVENTIVE_MAINTENANCE':
            self.workflow_status = 'CLOSED'
            self.closed_at = datetime.now(timezone.utc)
            
            # Update related work order status to completed
            if self.related_work_order_id:
                from app.models import WorkOrder
                work_order = WorkOrder.query.get(self.related_work_order_id)
                if work_order:
                    work_order.status = 'COMPLETED'
                    work_order.completed_at = datetime.now(timezone.utc)
                    
                    # Add activity log for work order completion
                    from app.models import WorkOrderActivity
                    wo_activity = WorkOrderActivity(
                        workorder_id=work_order.id,
                        user_id=user.id,
                        activity_type='status_update',
                        description=f'Work order automatically completed due to service incident closure.'
                    )
                    db.session.add(wo_activity)
        
        # Log activity
        if notes:
            activity = UAVServiceActivity(
                uav_service_incident_id=self.id,
                user_id=user.id,
                activity_type='workflow_advance',
                description=f'Workflow advanced to {self.workflow_status}. Notes: {notes}'
            )
            db.session.add(activity)
        
        db.session.commit()
    
    @staticmethod
    def generate_incident_number():
        """Generate unique incident number"""
        import random
        import string
        
        # Get current year
        year = datetime.now().year
        
        # Try up to 100 times to find a unique number
        for _ in range(100):
            # Generate format: UAV-YYYY-NNNN (e.g., UAV-2024-0001)
            sequence = random.randint(1, 9999)
            incident_number = f"UAV-{year}-{sequence:04d}"
            
            # Check if this number already exists
            existing = UAVServiceIncident.query.filter_by(incident_number=incident_number).first()
            if not existing:
                return incident_number
        
        # Fallback: use timestamp-based number
        timestamp = int(datetime.now().timestamp())
        return f"UAV-{year}-{timestamp % 10000:04d}"
    
    def __repr__(self):
        return f'<UAVServiceIncident {self.incident_number}: {self.title}>'


class UAVServiceActivity(db.Model):
    """Activity log for UAV service incidents"""
    __tablename__ = 'uav_service_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_customer_visible = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    uav_service_incident_id = db.Column(db.Integer, db.ForeignKey('uav_service_incidents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='uav_service_activities')
    uav_service_incident = db.relationship('UAVServiceIncident', backref='activities')
    
    def __repr__(self):
        return f'<UAVServiceActivity {self.id}: {self.activity_type}>'


class UAVMaintenanceSchedule(db.Model):
    """Preventive maintenance scheduling for UAVs"""
    __tablename__ = 'uav_maintenance_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    uav_model = db.Column(db.String(100), nullable=False)
    uav_serial_number = db.Column(db.String(100))
    
    # Maintenance Rules
    maintenance_type = db.Column(db.String(50), nullable=False)  # 'FLIGHT_HOURS', 'TIME_BASED', 'BOTH'
    flight_hours_interval = db.Column(db.Integer)  # Every X flight hours
    time_interval_days = db.Column(db.Integer)  # Every X days
    
    # Current Status
    current_flight_hours = db.Column(db.Integer, default=0)
    last_maintenance_date = db.Column(db.DateTime)
    next_maintenance_due = db.Column(db.DateTime)
    
    # Notifications
    notification_sent = db.Column(db.Boolean, default=False)
    customer_notified = db.Column(db.Boolean, default=False)
    service_center_notified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    # Relationships
    customer = db.relationship('User', backref='uav_maintenance_schedules')
    product = db.relationship('Product', backref='maintenance_schedules')
    
    @property
    def is_maintenance_due(self):
        """Check if maintenance is due"""
        if self.maintenance_type in ['TIME_BASED', 'BOTH']:
            if self.next_maintenance_due and datetime.now(timezone.utc) >= self.next_maintenance_due.replace(tzinfo=timezone.utc):
                return True
        
        if self.maintenance_type in ['FLIGHT_HOURS', 'BOTH']:
            if self.flight_hours_interval and self.current_flight_hours >= self.flight_hours_interval:
                return True
        
        return False
    
    def calculate_next_maintenance(self):
        """Calculate next maintenance due date"""
        if self.maintenance_type in ['TIME_BASED', 'BOTH'] and self.time_interval_days:
            if self.last_maintenance_date:
                from datetime import timedelta
                self.next_maintenance_due = self.last_maintenance_date + timedelta(days=self.time_interval_days)
            else:
                from datetime import timedelta
                self.next_maintenance_due = datetime.now(timezone.utc) + timedelta(days=self.time_interval_days)
    
    def __repr__(self):
        return f'<UAVMaintenanceSchedule {self.uav_model}: {self.uav_serial_number}>'


# Data Import Models

class ImportBatch(db.Model):
    """Import batch to track data import operations"""
    __tablename__ = 'import_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_name = db.Column(db.String(255), nullable=False)
    target_table = db.Column(db.String(100), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, validating, validated, importing, completed, failed
    total_rows = db.Column(db.Integer, default=0)
    valid_rows = db.Column(db.Integer, default=0)
    invalid_rows = db.Column(db.Integer, default=0)
    imported_rows = db.Column(db.Integer, default=0)
    failed_rows = db.Column(db.Integer, default=0)
    validation_summary = db.Column(db.Text)
    import_summary = db.Column(db.Text)
    error_log = db.Column(db.Text)
    preview_data = db.Column(db.Text)  # JSON string of first few rows for preview
    column_mapping = db.Column(db.Text)  # JSON string of column mappings
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    validation_started_at = db.Column(db.DateTime)
    validation_completed_at = db.Column(db.DateTime)
    import_started_at = db.Column(db.DateTime)
    import_completed_at = db.Column(db.DateTime)
    
    # Foreign Keys
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('import_templates.id'))
    
    # Relationships
    created_by = db.relationship('User', backref='import_batches')
    template = db.relationship('ImportTemplate', backref='import_batches')
    rows = db.relationship('ImportBatchRow', backref='import_batch', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def duration(self):
        """Calculate total duration of the import process"""
        if self.import_completed_at and self.created_at:
            return self.import_completed_at - self.created_at
        elif self.import_started_at and self.created_at:
            return datetime.now(timezone.utc) - self.created_at
        return None
    
    @property
    def validation_duration(self):
        """Calculate validation duration"""
        if self.validation_completed_at and self.validation_started_at:
            return self.validation_completed_at - self.validation_started_at
        return None
    
    @property
    def import_duration(self):
        """Calculate import duration"""
        if self.import_completed_at and self.import_started_at:
            return self.import_completed_at - self.import_started_at
        return None
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_rows > 0:
            return round((self.imported_rows / self.total_rows) * 100, 2)
        return 0
    
    def __repr__(self):
        return f'<ImportBatch {self.batch_name}: {self.status}>'


class ImportBatchRow(db.Model):
    """Individual row data and validation results for import batches"""
    __tablename__ = 'import_batch_rows'
    
    id = db.Column(db.Integer, primary_key=True)
    row_number = db.Column(db.Integer, nullable=False)
    raw_data = db.Column(db.Text, nullable=False)  # JSON string of original row data
    processed_data = db.Column(db.Text)  # JSON string of processed/transformed data
    validation_status = db.Column(db.String(50), default='pending')  # pending, valid, invalid
    validation_errors = db.Column(db.Text)  # JSON string of validation errors
    import_status = db.Column(db.String(50), default='pending')  # pending, imported, failed, skipped
    import_errors = db.Column(db.Text)  # JSON string of import errors
    target_record_id = db.Column(db.Integer)  # ID of the created/updated record
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    validated_at = db.Column(db.DateTime)
    imported_at = db.Column(db.DateTime)
    
    # Foreign Keys
    batch_id = db.Column(db.Integer, db.ForeignKey('import_batches.id'), nullable=False)
    
    @property
    def has_validation_errors(self):
        """Check if row has validation errors"""
        return self.validation_status == 'invalid'
    
    @property
    def has_import_errors(self):
        """Check if row has import errors"""
        return self.import_status == 'failed'
    
    @property
    def is_importable(self):
        """Check if row can be imported"""
        return self.validation_status == 'valid' and self.import_status == 'pending'
    
    def __repr__(self):
        return f'<ImportBatchRow {self.batch_id}:{self.row_number} - {self.validation_status}>'


class ImportTemplate(db.Model):
    """Templates for data import with predefined mappings and validation rules"""
    __tablename__ = 'import_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    target_table = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    column_mapping = db.Column(db.Text, nullable=False)  # JSON string of Excel column to DB column mapping
    validation_rules = db.Column(db.Text)  # JSON string of validation rules
    sample_data = db.Column(db.Text)  # JSON string of sample data for template generation
    is_active = db.Column(db.Boolean, default=True)
    version = db.Column(db.String(20), default='1.0')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    created_by = db.relationship('User', backref='import_templates')
    
    @property
    def usage_count(self):
        """Count how many times this template has been used"""
        return ImportBatch.query.filter_by(template_id=self.id).count()
    
    def __repr__(self):
        return f'<ImportTemplate {self.name} -> {self.target_table}>'


# Import Status Enum
class ImportStatus:
    """Status constants for import operations"""
    PENDING = 'pending'
    UPLOADING = 'uploading'
    UPLOADED = 'uploaded'
    VALIDATING = 'validating'
    VALIDATED = 'validated'
    APPROVED = 'approved'
    IMPORTING = 'importing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    
    @classmethod
    def get_all_statuses(cls):
        """Get all available statuses"""
        return [
            cls.PENDING, cls.UPLOADING, cls.UPLOADED,
            cls.VALIDATING, cls.VALIDATED, cls.APPROVED,
            cls.IMPORTING, cls.COMPLETED, cls.FAILED, cls.CANCELLED
        ]
    
    @classmethod
    def get_active_statuses(cls):
        """Get statuses that indicate active/in-progress operations"""
        return [cls.UPLOADING, cls.VALIDATING, cls.IMPORTING]
    
    @classmethod
    def get_completed_statuses(cls):
        """Get statuses that indicate completed operations"""
        return [cls.COMPLETED, cls.FAILED, cls.CANCELLED]


# Knowledge Management Models (KEDB Integration)
