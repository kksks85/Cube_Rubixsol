"""
User Management Forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, PasswordField, TelField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class CreateUserForm(FlaskForm):
    """Form for creating new users"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters.')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address.')
    ])
    
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(max=50, message='First name cannot exceed 50 characters.')
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(max=50, message='Last name cannot exceed 50 characters.')
    ])
    
    phone = TelField('Phone Number', validators=[
        Length(max=20, message='Phone number cannot exceed 20 characters.')
    ])
    
    role = SelectField('Role', coerce=int, validators=[DataRequired()])
    
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class EditUserForm(FlaskForm):
    """Form for editing existing users"""
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(max=50, message='First name cannot exceed 50 characters.')
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(max=50, message='Last name cannot exceed 50 characters.')
    ])
    
    phone = TelField('Phone Number', validators=[
        Length(max=20, message='Phone number cannot exceed 20 characters.')
    ])
    
    role = SelectField('Role', coerce=int, validators=[DataRequired()])
