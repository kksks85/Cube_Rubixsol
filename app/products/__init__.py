"""
Product Master Module
Handles UAV product management and owner details
"""

from flask import Blueprint

bp = Blueprint('products', __name__)

from app.products import routes

# Import routes to register them with the blueprint
from app.products import routes
