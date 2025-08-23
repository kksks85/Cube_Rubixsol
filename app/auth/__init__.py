"""
Authentication Blueprint
Handles user login, logout, and registration
"""

from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes

# Import routes to register them with the blueprint
from app.auth import routes
