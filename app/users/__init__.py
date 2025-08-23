"""
Users Management Blueprint
"""

from flask import Blueprint

bp = Blueprint('users', __name__)

from app.users import routes

# Import routes to register them with the blueprint
from app.users import routes
