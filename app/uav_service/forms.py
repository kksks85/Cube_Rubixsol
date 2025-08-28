from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, BooleanField, DecimalField, DateTimeField, DateField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Optional, NumberRange
from wtforms.widgets import TextArea


def coerce_int_or_none(value):
    """Coerce to int or None if empty"""
    if value == '' or value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


class UAVServiceIncidentForm(FlaskForm):
    # Basic Information
    title = StringField('Incident Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=1000)], 
                               widget=TextArea())
    
    # Customer Information - Updated to use User lookup
    customer_user_id = HiddenField('Customer User ID')
    customer_name = StringField('Customer Name', validators=[DataRequired(), Length(max=200)],
                               render_kw={"placeholder": "Start typing to search for registered users..."})
    customer_email = StringField('Customer Email', validators=[Optional(), Email(), Length(max=120)],
                                render_kw={"readonly": True})
    customer_phone = StringField('Customer Phone', validators=[Optional(), Length(max=20)],
                                render_kw={"readonly": True})
    customer_address = TextAreaField('Customer Address', validators=[Optional()], widget=TextArea())
    
    # UAV Equipment Details
    serial_number = StringField('Serial Number', validators=[DataRequired(), Length(max=40)], 
                               render_kw={"placeholder": "Enter UAV serial number"})
    product_name = StringField('Product Name', validators=[DataRequired(), Length(max=100)],
                              render_kw={"placeholder": "Enter product/model name", "readonly": True})
    owner_company = StringField('Owner Company', validators=[DataRequired(), Length(max=100)],
                               render_kw={"placeholder": "Enter company name", "readonly": True})
    last_service_date = DateField('Last Service Date', validators=[Optional()],
                                 render_kw={"placeholder": "YYYY-MM-DD", "readonly": True})
    
    # Incident Details
    incident_category = SelectField('Incident Category', choices=[
        ('BATTERY', 'Battery Issue'),
        ('CAMERA', 'Camera Issue'),
        ('CRASH_REPAIR', 'Crash Repair'),
        ('ROUTINE_MAINTENANCE', 'Routine Maintenance'),
        ('SOFTWARE', 'Software Issue'),
        ('HARDWARE', 'Hardware Issue'),
        ('OTHER', 'Other')
    ], validators=[DataRequired()])
    
    priority = SelectField('Priority', choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent')
    ], default='MEDIUM', validators=[DataRequired()])
    
    # SLA
    sla_category = SelectField('SLA Category', choices=[
        ('EXPRESS', 'Express (24h)'),
        ('STANDARD', 'Standard (72h)'),
        ('ECONOMY', 'Economy (168h)')
    ], default='STANDARD', validators=[DataRequired()])
    
    # Warranty
    is_warranty_service = BooleanField('Warranty Service', default=True)


class DiagnosisForm(FlaskForm):
    diagnostic_findings = TextAreaField('Diagnostic Findings', validators=[DataRequired()], widget=TextArea())
    work_order_type = SelectField('Work Order Type', choices=[
        ('REPAIR', 'Repair'),
        ('REPLACE', 'Replace'),
        ('MAINTENANCE', 'Maintenance'),
        ('INSPECTION', 'Inspection Only')
    ], validators=[DataRequired()])
    
    # Assignment fields
    assignment_group_id = SelectField('Assignment Group', validators=[Optional()], coerce=coerce_int_or_none)
    assigned_to_id = SelectField('Assigned User', validators=[Optional()], coerce=coerce_int_or_none)
    
    estimated_cost = DecimalField('Estimated Cost', validators=[Optional(), NumberRange(min=0)], places=2)
    parts_requested = BooleanField('Parts Required', default=False)
    technician_notes = TextAreaField('Technician Notes', validators=[Optional()], widget=TextArea())
    
    # Parts Request Section (initially hidden)
    part_number = StringField('Part Number', validators=[Optional(), Length(max=50)],
                             render_kw={"placeholder": "Search for part number..."})
    part_name = StringField('Part Name', validators=[Optional(), Length(max=100)],
                           render_kw={"readonly": True, "placeholder": "Auto-populated from part selection"})
    part_category = StringField('Category', validators=[Optional(), Length(max=50)],
                               render_kw={"readonly": True, "placeholder": "Auto-populated from part selection"})
    part_in_stock = IntegerField('In Stock', validators=[Optional(), NumberRange(min=0)],
                                render_kw={"readonly": True})
    quantity_needed = IntegerField('Quantity Needed', validators=[Optional(), NumberRange(min=1)],
                                  render_kw={"placeholder": "Enter quantity needed"})


class RepairMaintenanceForm(FlaskForm):
    technician_hours = DecimalField('Hours Worked', validators=[DataRequired(), NumberRange(min=0)], places=2)
    technician_notes = TextAreaField('Work Performed', validators=[DataRequired()], widget=TextArea())
    parts_received = BooleanField('Parts Received', default=False)
    service_status = SelectField('Service Status', choices=[
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('PENDING_PARTS', 'Pending Parts'),
        ('ON_HOLD', 'On Hold')
    ], validators=[DataRequired()])
    
    actual_cost = DecimalField('Actual Cost', validators=[Optional(), NumberRange(min=0)], places=2)


class QualityCheckForm(FlaskForm):
    qa_verified = BooleanField('QA Verification Passed', default=False)
    airworthiness_certified = BooleanField('Airworthiness Certified', default=False)
    qa_notes = TextAreaField('QA Notes', validators=[Optional()], widget=TextArea())
    
    # Invoice details for non-warranty services
    invoice_number = StringField('Invoice Number', validators=[Optional(), Length(max=50)])
    final_cost = DecimalField('Final Cost', validators=[Optional(), NumberRange(min=0)], places=2)


class PreventiveMaintenanceForm(FlaskForm):
    maintenance_type = SelectField('Maintenance Type', choices=[
        ('SCHEDULED', 'Scheduled Maintenance'),
        ('FLIGHT_HOURS', 'Flight Hours Based'),
        ('TIME_BASED', 'Time Based'),
        ('BOTH', 'Both Flight Hours and Time')
    ], validators=[DataRequired()])
    
    flight_hours_interval = IntegerField('Flight Hours Interval', validators=[Optional(), NumberRange(min=1)])
    time_interval_days = IntegerField('Time Interval (Days)', validators=[Optional(), NumberRange(min=1)])


class MaintenanceScheduleForm(FlaskForm):
    uav_model = StringField('UAV Model', validators=[DataRequired(), Length(max=100)])
    uav_serial_number = StringField('UAV Serial Number', validators=[DataRequired(), Length(max=100)])
    
    maintenance_type = SelectField('Maintenance Type', choices=[
        ('FLIGHT_HOURS', 'Flight Hours Based'),
        ('TIME_BASED', 'Time Based'),
        ('BOTH', 'Both')
    ], validators=[DataRequired()])
    
    flight_hours_interval = IntegerField('Flight Hours Interval', validators=[Optional(), NumberRange(min=1)])
    time_interval_days = IntegerField('Time Interval (Days)', validators=[Optional(), NumberRange(min=1)])
    current_flight_hours = IntegerField('Current Flight Hours', validators=[Optional(), NumberRange(min=0)], default=0)
