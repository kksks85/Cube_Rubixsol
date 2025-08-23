"""
Reporting Engine Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SelectMultipleField, DateField, FloatField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import TextArea, Select, CheckboxInput, DateInput

class ReportBuilderForm(FlaskForm):
    """Main report builder form"""
    report_name = StringField('Report Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    
    # Table Selection
    primary_table = SelectField('Primary Table', validators=[DataRequired()], coerce=str)
    
    # Column Selection
    columns = SelectMultipleField('Select Columns', validators=[DataRequired()], coerce=str)
    
    # Join Configuration
    join_tables = SelectMultipleField('Join Tables', validators=[Optional()], coerce=str)
    
    # Group By
    group_by_columns = SelectMultipleField('Group By', validators=[Optional()], coerce=str)
    
    # Order By
    order_by_column = SelectField('Order By', validators=[Optional()], coerce=str)
    order_direction = SelectField('Order Direction', 
                                choices=[('ASC', 'Ascending'), ('DESC', 'Descending')],
                                default='ASC', validators=[Optional()])
    
    # Limit
    limit_results = IntegerField('Limit Results', validators=[Optional()])
    
    submit = SubmitField('Generate Report')

class ReportFilterForm(FlaskForm):
    """Dynamic filter form for reports"""
    column = SelectField('Column', validators=[DataRequired()], coerce=str)
    operator = SelectField('Operator', validators=[DataRequired()], 
                         choices=[
                             ('eq', 'Equals'),
                             ('ne', 'Not Equals'),
                             ('gt', 'Greater Than'),
                             ('ge', 'Greater Than or Equal'),
                             ('lt', 'Less Than'),
                             ('le', 'Less Than or Equal'),
                             ('like', 'Contains'),
                             ('ilike', 'Contains (Case Insensitive)'),
                             ('in', 'In List'),
                             ('not_in', 'Not In List'),
                             ('between', 'Between'),
                             ('is_null', 'Is Null'),
                             ('is_not_null', 'Is Not Null'),
                             ('starts_with', 'Starts With'),
                             ('ends_with', 'Ends With')
                         ])
    value = StringField('Value', validators=[Optional()])
    value2 = StringField('Value 2 (for between)', validators=[Optional()])
    
class SavedReportForm(FlaskForm):
    """Form for managing saved reports"""
    name = StringField('Report Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    is_public = BooleanField('Make Public', default=False)
    tags = StringField('Tags (comma separated)', validators=[Optional()])
    submit = SubmitField('Save Report')

class ReportScheduleForm(FlaskForm):
    """Form for scheduling automatic reports"""
    name = StringField('Schedule Name', validators=[DataRequired()])
    frequency = SelectField('Frequency', validators=[DataRequired()],
                          choices=[
                              ('daily', 'Daily'),
                              ('weekly', 'Weekly'),
                              ('monthly', 'Monthly'),
                              ('quarterly', 'Quarterly')
                          ])
    email_recipients = TextAreaField('Email Recipients (one per line)', validators=[Optional()])
    format = SelectField('Export Format', validators=[DataRequired()],
                       choices=[
                           ('csv', 'CSV'),
                           ('excel', 'Excel'),
                           ('pdf', 'PDF')
                       ])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Schedule Report')
