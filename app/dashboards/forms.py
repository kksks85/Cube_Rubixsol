from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class DashboardForm(FlaskForm):
    name = StringField('Dashboard Name', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    is_public = BooleanField('Make Public')
    
    
class DashboardWidgetForm(FlaskForm):
    widget_type = SelectField('Widget Type', choices=[
        ('report', 'Report'),
        ('chart', 'Chart'),
        ('kpi', 'KPI'),
        ('quick_action', 'Quick Action')
    ], validators=[DataRequired()])
    title = StringField('Widget Title', validators=[DataRequired(), Length(min=1, max=100)])
    position_x = IntegerField('Position X', validators=[NumberRange(min=0, max=11)], default=0)
    position_y = IntegerField('Position Y', validators=[NumberRange(min=0)], default=0)
    width = IntegerField('Width', validators=[NumberRange(min=1, max=12)], default=4)
    height = IntegerField('Height', validators=[NumberRange(min=1)], default=3)
    report_id = SelectField('Report', coerce=int, validators=[Optional()])
    
    
class DashboardLayoutForm(FlaskForm):
    """Form for saving dashboard layout"""
    layout_data = HiddenField('Layout Data')


class ReportForm(FlaskForm):
    name = StringField('Report Name', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    report_type = SelectField('Report Type', choices=[
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('kpi', 'KPI'),
        ('summary', 'Summary')
    ], validators=[DataRequired()])
    is_public = BooleanField('Make Public')
    refresh_interval = IntegerField('Refresh Interval (seconds)', 
                                  validators=[NumberRange(min=30, max=3600)], default=300)
