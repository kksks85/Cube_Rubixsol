"""
Reporting Module
Advanced reporting system for dashboard and report management
"""

from flask import Blueprint

bp = Blueprint('reporting', __name__)

from app.reporting import routes, models