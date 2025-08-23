"""
Main Blueprint
Handles dashboard and core application routes
"""

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes

# Import routes to register them with the blueprint
from app.main import routes
