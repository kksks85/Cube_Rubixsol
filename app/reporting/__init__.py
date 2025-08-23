"""
Reporting Engine Blueprint
Provides advanced custom reporting functionality
"""

from flask import Blueprint

bp = Blueprint('reporting', __name__)

from app.reporting import routes
