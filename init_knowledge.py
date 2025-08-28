"""
Database Migration Script for Knowledge Management
Run this to create knowledge management tables
"""

from app import create_app, db
from app.models import Role
from app.knowledge.models import *

def init_knowledge_database():
    """Initialize knowledge management database tables and roles"""
    app = create_app()
    
    with app.app_context():
        # Create all knowledge tables
        db.create_all()
        
        # Create knowledge management roles if they don't exist
        knowledge_roles = [
            ('knowledge_admin', 'Knowledge Base Administrator'),
            ('knowledge_reviewer', 'Knowledge Article Reviewer'),
            ('knowledge_author', 'Knowledge Article Author')
        ]
        
        for role_name, description in knowledge_roles:
            existing_role = Role.query.filter_by(name=role_name).first()
            if not existing_role:
                role = Role(name=role_name, description=description)
                db.session.add(role)
                print(f"Created role: {role_name}")
        
        # Create default knowledge categories
        categories = [
            {
                'name': 'Technical Solutions',
                'description': 'Technical troubleshooting and solutions',
                'icon': 'fa-wrench',
                'color': '#007bff',
                'children': [
                    'Network Issues',
                    'Software Problems', 
                    'Hardware Issues',
                    'Security Incidents'
                ]
            },
            {
                'name': 'Procedures',
                'description': 'Standard operating procedures',
                'icon': 'fa-list-ol',
                'color': '#28a745',
                'children': [
                    'Installation Guides',
                    'Configuration Steps',
                    'Maintenance Tasks'
                ]
            },
            {
                'name': 'FAQ',
                'description': 'Frequently Asked Questions',
                'icon': 'fa-question-circle',
                'color': '#ffc107',
                'children': [
                    'User Account Issues',
                    'Password Problems',
                    'General Usage'
                ]
            }
        ]
        
        for cat_data in categories:
            existing = KnowledgeCategory.query.filter_by(name=cat_data['name']).first()
            if not existing:
                parent = KnowledgeCategory(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    icon=cat_data['icon'],
                    color=cat_data['color']
                )
                db.session.add(parent)
                db.session.flush()
                
                for child_name in cat_data['children']:
                    child = KnowledgeCategory(
                        name=child_name,
                        parent_id=parent.id
                    )
                    db.session.add(child)
                
                print(f"Created category: {cat_data['name']} with {len(cat_data['children'])} subcategories")
        
        # Create default tags
        default_tags = [
            'windows', 'linux', 'network', 'database', 'security', 'backup',
            'email', 'printer', 'software', 'hardware', 'password', 'access'
        ]
        
        for tag_name in default_tags:
            existing = KnowledgeTag.query.filter_by(name=tag_name).first()
            if not existing:
                tag = KnowledgeTag(name=tag_name)
                db.session.add(tag)
        
        db.session.commit()
        print("Knowledge management database initialized successfully!")

if __name__ == '__main__':
    init_knowledge_database()
