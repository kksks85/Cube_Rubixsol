"""
Data Import Module
Comprehensive data import system for bulk loading data into application tables
"""

from flask import Blueprint

bp = Blueprint('data_import', __name__)

from app.data_import import routes
