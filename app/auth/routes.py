"""
Authentication Routes
"""

from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.models import User, Role

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact an administrator.', 'error')
            return redirect(url_for('auth.login'))
        
        # Update last login time
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        flash(f'Welcome back, {user.first_name}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """User registration (admin only)"""
    if not current_user.has_role('admin'):
        flash('You do not have permission to register new users.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    form.role.choices = [(r.id, r.name.title()) for r in Role.query.all()]
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role_id=form.role.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.username} has been registered successfully.', 'success')
        return redirect(url_for('users.list_users'))
    
    return render_template('auth/register.html', title='Register User', form=form)

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('auth.change_password'))
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('Your password has been changed successfully.', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('auth/change_password.html', title='Change Password', form=form)

# Helper function for URL parsing
try:
    from urllib.parse import urlparse as url_parse
except ImportError:
    # This shouldn't happen in Python 3, but keeping for compatibility
    def url_parse(url):
        return type('ParseResult', (), {'netloc': ''})()  # Mock object
