"""
Authentication decorators for route protection
"""

from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    """
    Decorator to require admin role for access to route.
    Must be used after @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # Unauthorized
        
        if not current_user.role or current_user.role.name != 'admin':
            abort(403)  # Forbidden
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(role_name):
    """
    Decorator to require specific role for access to route.
    Must be used after @login_required.
    
    Args:
        role_name (str): The required role name
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            
            if not current_user.role or current_user.role.name != role_name:
                abort(403)  # Forbidden
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def roles_required(*role_names):
    """
    Decorator to require one of multiple roles for access to route.
    Must be used after @login_required.
    
    Args:
        *role_names: Variable number of allowed role names
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            
            if not current_user.role or current_user.role.name not in role_names:
                abort(403)  # Forbidden
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
