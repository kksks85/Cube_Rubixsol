"""
Service Management Forms
"""

from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SelectField, FloatField, 
                    DateTimeLocalField, DateField, IntegerField, BooleanField, SubmitField,
                    HiddenField, FieldList, FormField)
from wtforms.validators import DataRequired, Length, Email, Optional, NumberRange
from wtforms.widgets import TextArea
from app.models import ServiceCategory, Product, User, InventoryItem


class ServiceCategoryForm(FlaskForm):
    """Form for creating/editing service categories"""
    name = StringField('Category Name', validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('Description', validators=[Length(0, 500)])
    category_type = SelectField('Category Type', 
                               choices=[
                                   ('HARDWARE', 'Hardware Issues'),
                                   ('SOFTWARE', 'Software Issues'),
                                   ('FIRMWARE', 'Firmware Issues'),
                                   ('MAINTENANCE', 'Preventive Maintenance'),
                                   ('INSPECTION', 'Safety Inspection')
                               ],
                               validators=[DataRequired()])
    severity_level = SelectField('Default Severity Level',
                                choices=[
                                    ('LOW', 'Low'),
                                    ('MEDIUM', 'Medium'),
                                    ('HIGH', 'High'),
                                    ('CRITICAL', 'Critical')
                                ],
                                default='MEDIUM',
                                validators=[DataRequired()])
    estimated_service_time = IntegerField('Estimated Service Time (hours)', 
                                        validators=[Optional(), NumberRange(min=1, max=200)])
    requires_parts = BooleanField('Typically Requires Parts')
    requires_software_update = BooleanField('May Require Software Update')
    requires_firmware_update = BooleanField('May Require Firmware Update')
    submit = SubmitField('Save Category')


class ServiceIncidentForm(FlaskForm):
    """Form for creating/editing service incidents"""
    # Basic Information
    title = StringField('Service Title', validators=[DataRequired(), Length(1, 200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(1, 1000)],
                               widget=TextArea())
    symptoms = TextAreaField('Reported Symptoms', validators=[Length(0, 500)])
    
    # Service Details
    incident_type = SelectField('Incident Type',
                               choices=[
                                   ('WARRANTY', 'Warranty Claim'),
                                   ('REPAIR', 'Repair Service'),
                                   ('MAINTENANCE', 'Preventive Maintenance'),
                                   ('INSPECTION', 'Safety Inspection'),
                                   ('UPGRADE', 'Software/Hardware Upgrade')
                               ],
                               validators=[DataRequired()])
    priority = SelectField('Priority',
                          choices=[
                              ('LOW', 'Low'),
                              ('MEDIUM', 'Medium'),
                              ('HIGH', 'High'),
                              ('URGENT', 'Urgent')
                          ],
                          default='MEDIUM',
                          validators=[DataRequired()])
    
    # Product and Category
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    category_id = SelectField('Service Category', coerce=int, validators=[Optional()])
    technician_id = SelectField('Assigned Technician', coerce=int, validators=[Optional()])
    
    # Customer Information
    customer_name = StringField('Customer Name', validators=[DataRequired(), Length(1, 200)])
    customer_email = StringField('Customer Email', validators=[Optional(), Email()])
    customer_phone = StringField('Customer Phone', validators=[Optional(), Length(0, 20)])
    customer_address = TextAreaField('Customer Address', validators=[Optional(), Length(0, 300)])
    
    # Service Timeline
    estimated_completion_date = DateField('Estimated Completion Date', validators=[Optional()])
    estimated_cost = FloatField('Estimated Cost', validators=[Optional(), NumberRange(min=0, max=50000)])
    
    # Technical Information
    software_version_before = StringField('Current Software Version', validators=[Optional(), Length(0, 50)])
    firmware_version_before = StringField('Current Firmware Version', validators=[Optional(), Length(0, 50)])
    
    # Notes
    internal_notes = TextAreaField('Internal Notes', validators=[Optional(), Length(0, 1000)])
    customer_notes = TextAreaField('Customer Visible Notes', validators=[Optional(), Length(0, 1000)])
    
    submit = SubmitField('Create Service Incident')


class ServiceIncidentUpdateForm(FlaskForm):
    """Form for updating service incident status and details"""
    status = SelectField('Status',
                        choices=[
                            ('RECEIVED', 'Received'),
                            ('DIAGNOSED', 'Diagnosed'),
                            ('IN_PROGRESS', 'In Progress'),
                            ('WAITING_PARTS', 'Waiting for Parts'),
                            ('COMPLETED', 'Completed'),
                            ('CLOSED', 'Closed')
                        ],
                        validators=[DataRequired()])
    diagnosis = TextAreaField('Technical Diagnosis', validators=[Optional(), Length(0, 1000)])
    estimated_completion_date = DateField('Estimated Completion Date', validators=[Optional()])
    actual_cost = FloatField('Actual Cost', validators=[Optional(), NumberRange(min=0, max=50000)])
    parts_cost = FloatField('Parts Cost', validators=[Optional(), NumberRange(min=0, max=50000)])
    labor_cost = FloatField('Labor Cost', validators=[Optional(), NumberRange(min=0, max=50000)])
    
    # Software/Firmware Updates
    software_version_after = StringField('Updated Software Version', validators=[Optional(), Length(0, 50)])
    firmware_version_after = StringField('Updated Firmware Version', validators=[Optional(), Length(0, 50)])
    
    # Resolution
    resolution_summary = TextAreaField('Resolution Summary', validators=[Optional(), Length(0, 1000)])
    internal_notes = TextAreaField('Internal Notes', validators=[Optional(), Length(0, 1000)])
    customer_notes = TextAreaField('Customer Visible Notes', validators=[Optional(), Length(0, 1000)])
    
    submit = SubmitField('Update Incident')


class ServicePartForm(FlaskForm):
    """Form for adding parts to service incidents"""
    inventory_item_id = SelectField('Inventory Item', coerce=int, validators=[DataRequired()])
    quantity_used = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1, max=100)])
    unit_cost = FloatField('Unit Cost', validators=[Optional(), NumberRange(min=0, max=10000)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(0, 200)])
    submit = SubmitField('Add Part')


class ServiceActivityForm(FlaskForm):
    """Form for adding activities to service incidents"""
    activity_type = SelectField('Activity Type',
                               choices=[
                                   ('received', 'Item Received'),
                                   ('diagnosed', 'Diagnosis Completed'),
                                   ('parts_ordered', 'Parts Ordered'),
                                   ('repair_started', 'Repair Started'),
                                   ('software_updated', 'Software Updated'),
                                   ('firmware_updated', 'Firmware Updated'),
                                   ('testing', 'Testing in Progress'),
                                   ('completed', 'Service Completed'),
                                   ('customer_contacted', 'Customer Contacted'),
                                   ('other', 'Other')
                               ],
                               validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(1, 500)])
    is_customer_visible = BooleanField('Visible to Customer', default=True)
    submit = SubmitField('Add Activity')


class ServiceSoftwareUpdateForm(FlaskForm):
    """Form for tracking software/firmware updates"""
    update_type = SelectField('Update Type',
                             choices=[
                                 ('SOFTWARE', 'Software'),
                                 ('FIRMWARE', 'Firmware'),
                                 ('DRIVER', 'Driver'),
                                 ('CONFIG', 'Configuration')
                             ],
                             validators=[DataRequired()])
    component_name = StringField('Component Name', validators=[DataRequired(), Length(1, 100)])
    version_before = StringField('Version Before', validators=[Optional(), Length(0, 50)])
    version_after = StringField('Version After', validators=[DataRequired(), Length(1, 50)])
    update_method = SelectField('Update Method',
                               choices=[
                                   ('OTA', 'Over-the-Air (OTA)'),
                                   ('USB', 'USB Connection'),
                                   ('SD_CARD', 'SD Card'),
                                   ('MANUAL', 'Manual Installation')
                               ],
                               validators=[DataRequired()])
    update_notes = TextAreaField('Update Notes', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('Record Update')


class ServiceTemplateForm(FlaskForm):
    """Form for creating service templates"""
    name = StringField('Template Name', validators=[DataRequired(), Length(1, 200)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 500)])
    template_type = SelectField('Template Type',
                               choices=[
                                   ('REPAIR', 'Repair Procedure'),
                                   ('MAINTENANCE', 'Maintenance Procedure'),
                                   ('INSPECTION', 'Inspection Checklist'),
                                   ('UPGRADE', 'Upgrade Procedure')
                               ],
                               validators=[DataRequired()])
    category_id = SelectField('Service Category', coerce=int, validators=[Optional()])
    estimated_time = IntegerField('Estimated Time (hours)', 
                                validators=[Optional(), NumberRange(min=1, max=100)])
    procedure_steps = TextAreaField('Procedure Steps', validators=[Optional(), Length(0, 2000)],
                                   widget=TextArea())
    required_tools = TextAreaField('Required Tools', validators=[Optional(), Length(0, 500)])
    safety_notes = TextAreaField('Safety Notes', validators=[Optional(), Length(0, 500)])
    applicable_models = TextAreaField('Applicable Models', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('Save Template')


class ServiceSearchForm(FlaskForm):
    """Form for searching and filtering service incidents"""
    search_term = StringField('Search', validators=[Optional(), Length(0, 100)])
    status = SelectField('Status',
                        choices=[
                            ('', 'All Statuses'),
                            ('RECEIVED', 'Received'),
                            ('DIAGNOSED', 'Diagnosed'),
                            ('IN_PROGRESS', 'In Progress'),
                            ('WAITING_PARTS', 'Waiting for Parts'),
                            ('COMPLETED', 'Completed'),
                            ('CLOSED', 'Closed')
                        ],
                        validators=[Optional()])
    incident_type = SelectField('Incident Type',
                               choices=[
                                   ('', 'All Types'),
                                   ('WARRANTY', 'Warranty'),
                                   ('REPAIR', 'Repair'),
                                   ('MAINTENANCE', 'Maintenance'),
                                   ('INSPECTION', 'Inspection'),
                                   ('UPGRADE', 'Upgrade')
                               ],
                               validators=[Optional()])
    priority = SelectField('Priority',
                          choices=[
                              ('', 'All Priorities'),
                              ('LOW', 'Low'),
                              ('MEDIUM', 'Medium'),
                              ('HIGH', 'High'),
                              ('URGENT', 'Urgent')
                          ],
                          validators=[Optional()])
    technician_id = SelectField('Technician', coerce=int, validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    submit = SubmitField('Search')


class ServiceStatusUpdateForm(FlaskForm):
    """Form for updating service incident status in step-by-step workflow"""
    status_step = SelectField('Status Step',
                             choices=[
                                 (1, 'Step 1: Received - Item received and logged'),
                                 (2, 'Step 2: Inspection - Initial inspection and assessment'),
                                 (3, 'Step 3: Diagnosis - Problem diagnosis completed'),
                                 (4, 'Step 4: Approval - Awaiting customer approval'),
                                 (5, 'Step 5: Parts - Parts ordered/procured'),
                                 (6, 'Step 6: Repair - Repair work in progress'),
                                 (7, 'Step 7: Testing - Testing and quality control'),
                                 (8, 'Step 8: Complete - Ready for pickup/delivery')
                             ],
                             coerce=int,
                             validators=[DataRequired()])
    
    # Additional fields based on status
    diagnosis = TextAreaField('Technical Diagnosis', validators=[Optional(), Length(0, 1000)])
    parts_needed = TextAreaField('Parts Needed', validators=[Optional(), Length(0, 500)])
    estimated_cost = FloatField('Estimated Cost', validators=[Optional(), NumberRange(min=0, max=50000)])
    customer_approval_notes = TextAreaField('Customer Approval Notes', validators=[Optional(), Length(0, 500)])
    repair_notes = TextAreaField('Repair Work Notes', validators=[Optional(), Length(0, 1000)])
    testing_results = TextAreaField('Testing Results', validators=[Optional(), Length(0, 500)])
    completion_notes = TextAreaField('Completion Notes', validators=[Optional(), Length(0, 500)])
    
    # Status change notes
    status_notes = TextAreaField('Status Update Notes', validators=[Optional(), Length(0, 500)])
    
    # Quick action buttons
    advance_status = SubmitField('Advance to Next Step')
    set_specific_status = SubmitField('Set Specific Status')
    add_notes_only = SubmitField('Add Notes Only')
