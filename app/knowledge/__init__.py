"""
Knowledge Management Module
KEDB-compliant knowledge base system
"""

from flask import Blueprint

# Import models to register them
from app.knowledge.models import *
from app.knowledge.routes import knowledge

def init_app(app):
    """Initialize knowledge management module"""
    app.register_blueprint(knowledge)
    
    # Register CLI commands
    from app.knowledge.cli import init_knowledge_cli
    init_knowledge_cli(app)
