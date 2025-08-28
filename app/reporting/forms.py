"""
Reporting Forms
WTForms for the reporting module
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from app.reporting.engine import ReportEngine


class NewReportForm(FlaskForm):
    """Form for creating new reports"""
    
    name = StringField('Report Name', validators=[
        DataRequired(message='Report name is required'),
        Length(min=3, max=100, message='Report name must be between 3 and 100 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500, message='Description must not exceed 500 characters')
    ])
    
    category = SelectField('Category', choices=[
        ('', 'Select Category'),
        ('financial', 'Financial'),
        ('operational', 'Operational'),
        ('analytics', 'Analytics'),
        ('custom', 'Custom')
    ], validators=[Optional()])
    
    data_source = SelectField('Data Source', validators=[
        DataRequired(message='Please select a data source')
    ])
    
    tags = StringField('Tags', validators=[
        Optional(),
        Length(max=200, message='Tags must not exceed 200 characters')
    ])
    
    template = HiddenField('Template', default='blank')
    
    submit = SubmitField('Create Report')
    
    def __init__(self, *args, **kwargs):
        super(NewReportForm, self).__init__(*args, **kwargs)
        
        # Populate data source choices
        try:
            engine = ReportEngine()
            tables = engine.get_available_tables()
            self.data_source.choices = [('', 'Select Table')] + [
                (table_name, table_info.get('display_name', table_name))
                for table_name, table_info in tables.items()
            ]
        except Exception as e:
            self.data_source.choices = [('', 'No tables available')]
    
    def validate_name(self, field):
        """Custom validation for report name"""
        # Check for reserved words or special characters
        reserved_words = ['admin', 'system', 'root', 'test']
        if field.data.lower() in reserved_words:
            raise ValidationError('This name is reserved. Please choose a different name.')


class ReportFilterForm(FlaskForm):
    """Form for report filtering and search"""
    
    search = StringField('Search Reports', validators=[Optional()])
    
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('financial', 'Financial'),
        ('operational', 'Operational'),
        ('analytics', 'Analytics'),
        ('custom', 'Custom')
    ], validators=[Optional()])
    
    status = SelectField('Status', choices=[
        ('', 'All Status'),
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('archived', 'Archived')
    ], validators=[Optional()])
    
    data_source = SelectField('Data Source', choices=[('', 'All Sources')], validators=[Optional()])
    
    submit = SubmitField('Filter')


class ShareReportForm(FlaskForm):
    """Form for sharing reports"""
    
    share_type = SelectField('Share Type', choices=[
        ('link', 'Public Link'),
        ('email', 'Email Share'),
        ('internal', 'Internal Users')
    ], validators=[DataRequired()])
    
    recipients = TextAreaField('Recipients', validators=[
        Optional(),
        Length(max=1000, message='Recipients list is too long')
    ])
    
    message = TextAreaField('Message', validators=[
        Optional(),
        Length(max=500, message='Message is too long')
    ])
    
    permissions = SelectField('Permissions', choices=[
        ('view', 'View Only'),
        ('execute', 'View & Execute'),
        ('edit', 'View, Execute & Edit')
    ], default='view', validators=[DataRequired()])
    
    expires_in = SelectField('Link Expires', choices=[
        ('', 'Never'),
        ('1', '1 Day'),
        ('7', '1 Week'),
        ('30', '1 Month'),
        ('90', '3 Months')
    ], validators=[Optional()])
    
    submit = SubmitField('Share Report')


class ScheduleReportForm(FlaskForm):
    """Form for scheduling reports"""
    
    frequency = SelectField('Frequency', choices=[
        ('once', 'Run Once'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly')
    ], validators=[DataRequired()])
    
    day_of_week = SelectField('Day of Week', choices=[
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], validators=[Optional()])
    
    day_of_month = SelectField('Day of Month', choices=[
        (str(i), str(i)) for i in range(1, 32)
    ], validators=[Optional()])
    
    hour = SelectField('Hour', choices=[
        (str(i), f"{i:02d}:00") for i in range(24)
    ], default='9', validators=[DataRequired()])
    
    format = SelectField('Export Format', choices=[
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF')
    ], default='csv', validators=[DataRequired()])
    
    email_recipients = TextAreaField('Email Recipients', validators=[
        Optional(),
        Length(max=1000, message='Recipients list is too long')
    ])
    
    include_data = SelectField('Include Data', choices=[
        ('summary', 'Summary Only'),
        ('full', 'Full Dataset'),
        ('filtered', 'Filtered Data')
    ], default='full', validators=[DataRequired()])
    
    submit = SubmitField('Schedule Report')


class QuickReportForm(FlaskForm):
    """Form for quick report generation"""
    
    table = SelectField('Table', validators=[DataRequired()])
    columns = StringField('Columns (comma-separated)', validators=[Optional()])
    limit = SelectField('Limit Results', choices=[
        ('', 'No Limit'),
        ('10', '10 rows'),
        ('50', '50 rows'),
        ('100', '100 rows'),
        ('500', '500 rows'),
        ('1000', '1000 rows')
    ], validators=[Optional()])
    
    submit = SubmitField('Generate Report')
    
    def __init__(self, *args, **kwargs):
        super(QuickReportForm, self).__init__(*args, **kwargs)
        
        # Populate table choices
        try:
            engine = ReportEngine()
            tables = engine.get_available_tables()
            self.table.choices = [
                (table_name, table_info.get('display_name', table_name))
                for table_name, table_info in tables.items()
            ]
        except Exception as e:
            self.table.choices = [('', 'No tables available')]
