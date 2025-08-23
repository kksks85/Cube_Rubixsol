"""
Work Order Management System
A comprehensive tool for managing work orders with user management, 
reporting, and dashboard capabilities.

Author: Python Expert (20+ years experience)
Date: August 23, 2025
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///workorder.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register template filters
    @app.template_filter('days_since')
    def days_since_filter(date):
        if date:
            delta = datetime.now().date() - date
            return delta.days
        return 0
    
    @app.template_filter('days_until')
    def days_until_filter(date):
        if date:
            delta = date - datetime.now().date()
            return delta.days
        return 0
    
    # Import and register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.workorders import bp as workorders_bp
    app.register_blueprint(workorders_bp, url_prefix='/workorders')
    
    from app.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/users')
    
    from app.products import bp as products_bp
    app.register_blueprint(products_bp, url_prefix='/products')
    
    from app.reporting import bp as reporting_bp
    app.register_blueprint(reporting_bp, url_prefix='/reporting')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        from app.models import User, Role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
            
        manager_role = Role.query.filter_by(name='manager').first()
        if not manager_role:
            manager_role = Role(name='manager', description='Manager')
            db.session.add(manager_role)
            
        technician_role = Role.query.filter_by(name='technician').first()
        if not technician_role:
            technician_role = Role(name='technician', description='Technician')
            db.session.add(technician_role)
            
        db.session.commit()
        
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@workorder.com',
                first_name='System',
                last_name='Administrator',
                role_id=admin_role.id
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
