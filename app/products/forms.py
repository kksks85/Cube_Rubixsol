"""
Product Management Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField, DecimalField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email, URL
from wtforms.widgets import TextArea
from app.models import ProductCategory, Company, User


class CompanyForm(FlaskForm):
    """Form for creating/editing companies"""
    name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=200)])
    registration_number = StringField('Registration Number', validators=[Optional(), Length(max=100)])
    website = StringField('Website', validators=[Optional(), URL(), Length(max=255)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    
    # Address fields
    address_line1 = StringField('Address Line 1', validators=[Optional(), Length(max=255)])
    address_line2 = StringField('Address Line 2', validators=[Optional(), Length(max=255)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    state = StringField('State/Province', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    country = StringField('Country', validators=[Optional(), Length(max=100)])


class ProductCategoryForm(FlaskForm):
    """Form for creating/editing product categories"""
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=100)])
    code = StringField('Category Code', validators=[Optional(), Length(max=10)])
    description = TextAreaField('Description', validators=[Optional()], widget=TextArea())


class ProductForm(FlaskForm):
    """Comprehensive form for UAV product management"""
    
    # Basic Information
    product_code = StringField('Product Code', validators=[DataRequired(), Length(min=2, max=50)])
    product_name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description', validators=[Optional()], widget=TextArea())
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    owner_company_id = SelectField('Owner Company', coerce=int, validators=[DataRequired()])
    
    # Flight Performance
    max_flight_time = FloatField('Max Flight Time (minutes)', validators=[Optional(), NumberRange(min=0)])
    max_range = FloatField('Max Range (km)', validators=[Optional(), NumberRange(min=0)])
    max_altitude = FloatField('Max Altitude (meters)', validators=[Optional(), NumberRange(min=0)])
    max_speed = FloatField('Max Speed (km/h)', validators=[Optional(), NumberRange(min=0)])
    
    # Physical Specifications
    weight = FloatField('Weight (grams)', validators=[Optional(), NumberRange(min=0)])
    dimensions_length = FloatField('Length (cm)', validators=[Optional(), NumberRange(min=0)])
    dimensions_width = FloatField('Width (cm)', validators=[Optional(), NumberRange(min=0)])
    dimensions_height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=0)])
    
    # Camera & Payload
    camera_resolution = StringField('Camera Resolution', validators=[Optional(), Length(max=50)])
    payload_capacity = FloatField('Payload Capacity (grams)', validators=[Optional(), NumberRange(min=0)])
    
    # Battery & Power
    battery_type = StringField('Battery Type', validators=[Optional(), Length(max=100)])
    battery_capacity = IntegerField('Battery Capacity (mAh)', validators=[Optional(), NumberRange(min=0)])
    charging_time = FloatField('Charging Time (minutes)', validators=[Optional(), NumberRange(min=0)])
    
    # Navigation & Control
    gps_enabled = BooleanField('GPS Enabled')
    autopilot_features = TextAreaField('Autopilot Features', validators=[Optional()], widget=TextArea())
    control_range = FloatField('Control Range (meters)', validators=[Optional(), NumberRange(min=0)])
    
    # Connectivity
    wifi_enabled = BooleanField('WiFi Enabled')
    bluetooth_enabled = BooleanField('Bluetooth Enabled')
    cellular_enabled = BooleanField('Cellular Enabled')
    
    # Environmental
    operating_temperature_min = FloatField('Min Operating Temperature (°C)', validators=[Optional()])
    operating_temperature_max = FloatField('Max Operating Temperature (°C)', validators=[Optional()])
    wind_resistance = FloatField('Wind Resistance (m/s)', validators=[Optional(), NumberRange(min=0)])
    water_resistance_rating = StringField('Water Resistance Rating', validators=[Optional(), Length(max=10)])
    
    # Regulatory & Compliance
    certification_level = StringField('Certification Level', validators=[Optional(), Length(max=50)])
    flight_zone_restrictions = TextAreaField('Flight Zone Restrictions', validators=[Optional()], widget=TextArea())
    requires_license = BooleanField('Requires License')
    
    # Commercial Details
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=200)])
    model_year = IntegerField('Model Year', validators=[Optional(), NumberRange(min=1900, max=2100)])
    warranty_period = IntegerField('Warranty Period (months)', validators=[Optional(), NumberRange(min=0)])
    price = DecimalField('Price', validators=[Optional(), NumberRange(min=0)], places=2)
    
    # Operational Use
    intended_use = StringField('Intended Use', validators=[Optional(), Length(max=200)])
    skill_level_required = SelectField('Skill Level Required', 
                                     choices=[('', 'Select Skill Level'),
                                            ('Beginner', 'Beginner'),
                                            ('Intermediate', 'Intermediate'), 
                                            ('Professional', 'Professional')],
                                     validators=[Optional()])
    
    # Servicing History
    last_serviced = DateField('Last Serviced', validators=[Optional()], format='%Y-%m-%d')
    next_service_due = DateField('Next Service Due', validators=[Optional()], format='%Y-%m-%d', 
                                render_kw={'readonly': True, 'class': 'form-control-plaintext'})
    
    # Status
    availability_status = SelectField('Availability Status',
                                    choices=[('Available', 'Available'),
                                           ('Discontinued', 'Discontinued'),
                                           ('Pre-order', 'Pre-order'),
                                           ('Out of Stock', 'Out of Stock')],
                                    default='Available',
                                    validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        
        # Populate category choices
        self.category_id.choices = [(0, 'Select Category')] + [
            (cat.id, cat.name) for cat in ProductCategory.query.order_by(ProductCategory.name).all()
        ]
        
        # Populate company choices
        self.owner_company_id.choices = [
            (company.id, company.name) for company in Company.query.order_by(Company.name).all()
        ]


class ProductSpecificationForm(FlaskForm):
    """Form for adding custom specifications"""
    key = StringField('Specification Name', validators=[DataRequired(), Length(min=1, max=100)])
    value = TextAreaField('Value', validators=[DataRequired()], widget=TextArea())
    unit = StringField('Unit', validators=[Optional(), Length(max=50)])


class ProductSearchForm(FlaskForm):
    """Form for searching products"""
    search_term = StringField('Search Products', validators=[Optional(), Length(max=200)])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    company_id = SelectField('Company', coerce=int, validators=[Optional()])
    availability_status = SelectField('Availability', validators=[Optional()])
    skill_level = SelectField('Skill Level', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(ProductSearchForm, self).__init__(*args, **kwargs)
        
        # Populate category choices
        self.category_id.choices = [(0, 'All Categories')] + [
            (cat.id, cat.name) for cat in ProductCategory.query.order_by(ProductCategory.name).all()
        ]
        
        # Populate company choices
        self.company_id.choices = [(0, 'All Companies')] + [
            (company.id, company.name) for company in Company.query.order_by(Company.name).all()
        ]
        
        # Availability status choices
        self.availability_status.choices = [
            ('', 'All Status'),
            ('Available', 'Available'),
            ('Discontinued', 'Discontinued'),
            ('Pre-order', 'Pre-order'),
            ('Out of Stock', 'Out of Stock')
        ]
        
        # Skill level choices
        self.skill_level.choices = [
            ('', 'All Skill Levels'),
            ('Beginner', 'Beginner'),
            ('Intermediate', 'Intermediate'),
            ('Professional', 'Professional')
        ]
