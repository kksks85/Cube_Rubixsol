"""
Service Management Blueprint
"""

from flask import Blueprint

bp = Blueprint('service', __name__, url_prefix='/service')

from app.service import routes
