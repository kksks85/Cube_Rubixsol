"""
Email Management Module
"""

from flask import Blueprint

bp = Blueprint('email_management', __name__, url_prefix='/email-management')

from app.email_management import routes
