"""
Work Order Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, DateField, FloatField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from wtforms.widgets import DateInput, DateTimeLocalInput
from datetime import datetime

class WorkOrderForm(FlaskForm):
    """Work order creation/edit form"""
    title = StringField('Title', validators=[DataRequired()])
    product_name = SelectField('Product name', coerce=int, validators=[Optional()])
    owner_name = StringField('Owner Name', validators=[Optional()])
    description = TextAreaField('Description', validators=[DataRequired()])
    address = StringField('Address', validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    priority_id = SelectField('Priority', coerce=int, validators=[DataRequired()])
    status_id = SelectField('Status', coerce=int, validators=[DataRequired()])  # Added status field
    assigned_to_id = SelectField('Assigned To', coerce=int, validators=[Optional()])
    estimated_hours = FloatField('Estimated Hours', validators=[Optional(), NumberRange(min=0)])
    cost_estimate = DecimalField('Cost Estimate', validators=[Optional(), NumberRange(min=0)], places=2)
    due_date = DateField('Due Date', validators=[Optional()], widget=DateInput())
    notes = TextAreaField('Notes')
    submit = SubmitField('Save Work Order')

class WorkOrderUpdateForm(FlaskForm):
    """Work order update form (for technicians)"""
    status_id = SelectField('Status', coerce=int, validators=[DataRequired()])
    actual_hours = FloatField('Actual Hours', validators=[Optional(), NumberRange(min=0)])
    actual_cost = DecimalField('Actual Cost', validators=[Optional(), NumberRange(min=0)], places=2)
    notes = TextAreaField('Update Notes')
    submit = SubmitField('Update Work Order')

class WorkOrderFilterForm(FlaskForm):
    """Work order filtering form"""
    status_id = SelectField('Status', coerce=int, validators=[Optional()])
    priority_id = SelectField('Priority', coerce=int, validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    assigned_to_id = SelectField('Assigned To', coerce=int, validators=[Optional()])
    date_from = DateField('From Date', validators=[Optional()], widget=DateInput())
    date_to = DateField('To Date', validators=[Optional()], widget=DateInput())
    submit = SubmitField('Apply Filters')
