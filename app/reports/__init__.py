"""
Reports and Analytics Blueprint
"""

from flask import Blueprint

bp = Blueprint('reports', __name__)

from app.reports import routes

# Import routes to register them with the blueprint
from app.reports import routes
