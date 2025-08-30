"""
Third-Party Integration Module
Provides centralized integration management for external systems
"""

from flask import Blueprint

bp = Blueprint('integrations', __name__)

from app.integrations import routes, models, forms
