"""
Data Import Forms
Forms for the data import module
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import TextArea

class UploadForm(FlaskForm):
    """Form for uploading data files"""
    batch_name = StringField('Batch Name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    target_table = SelectField('Target Table', validators=[DataRequired()], choices=[
        ('users', 'Users'),
        ('products', 'Products'),
        ('companies', 'Companies'),
        ('inventory_items', 'Inventory Items'),
        ('inventory_categories', 'Inventory Categories'),
        ('workorders', 'Work Orders'),
        ('product_categories', 'Product Categories'),
        ('uav_service_incidents', 'UAV Service Incidents'),
        ('assignment_groups', 'Assignment Groups'),
    ])
    file = FileField('Excel File', validators=[
        FileRequired(),
        FileAllowed(['xlsx', 'xls'], 'Only Excel files (.xlsx, .xls) are allowed!')
    ])
    submit = SubmitField('Upload and Analyze')

class MappingForm(FlaskForm):
    """Form for mapping Excel columns to database fields"""
    batch_id = HiddenField()
    mapping_config = HiddenField()  # JSON string of column mappings
    submit_mapping = SubmitField('Apply Mapping and Validate')

class ApprovalForm(FlaskForm):
    """Form for approving/rejecting import batches"""
    batch_id = HiddenField()
    action = HiddenField()  # 'approve' or 'reject'
    approval_notes = TextAreaField('Approval Notes', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Submit Decision')

class ProcessForm(FlaskForm):
    """Form for processing approved import batches"""
    batch_id = HiddenField()
    confirm = BooleanField('I confirm that I want to import this data', validators=[DataRequired()])
    submit = SubmitField('Import Data')

class TemplateForm(FlaskForm):
    """Form for creating import templates"""
    name = StringField('Template Name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    target_table = SelectField('Target Table', validators=[DataRequired()], choices=[
        ('users', 'Users'),
        ('products', 'Products'),
        ('companies', 'Companies'),
        ('inventory_items', 'Inventory Items'),
        ('inventory_categories', 'Inventory Categories'),
        ('workorders', 'Work Orders'),
        ('product_categories', 'Product Categories'),
        ('uav_service_incidents', 'UAV Service Incidents'),
        ('assignment_groups', 'Assignment Groups'),
    ])
    column_mapping = TextAreaField('Column Mapping (JSON)', 
                                 widget=TextArea(),
                                 validators=[Optional()],
                                 render_kw={"rows": 10, "class": "form-control font-monospace"})
    validation_rules = TextAreaField('Validation Rules (JSON)', 
                                   widget=TextArea(),
                                   validators=[Optional()],
                                   render_kw={"rows": 10, "class": "form-control font-monospace"})
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Template')
