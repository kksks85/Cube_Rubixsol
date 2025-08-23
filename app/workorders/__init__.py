"""
Work Orders Blueprint
Handles work order CRUD operations
"""

from flask import Blueprint

bp = Blueprint('workorders', __name__)

from app.workorders import routes

# Import routes to register them with the blueprint
from app.workorders import routes
