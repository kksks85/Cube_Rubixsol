"""
CUBE-PRO Application Architecture Diagram Generator

This script creates a comprehensive architecture diagram for the CUBE-PRO
Enterprise Work Order Management System and saves it as a PDF.

Author: GitHub Copilot
Date: August 25, 2025
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, ConnectionPatch
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

def create_architecture_diagram():
    """Create comprehensive architecture diagram for CUBE-PRO application"""
    
    # Create figure with custom size for detailed diagram
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle('CUBE-PRO Enterprise Work Order Management System\nApplication Architecture', 
                 fontsize=24, fontweight='bold', y=0.98)
    
    # Create main axis
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Color scheme - Blue, Grey, White theme
    colors = {
        'primary': '#2563eb',
        'secondary': '#6b7280',
        'light_blue': '#dbeafe',
        'light_grey': '#f3f4f6',
        'white': '#ffffff',
        'text': '#374151',
        'border': '#d1d5db'
    }
    
    # === PRESENTATION LAYER ===
    # Header for Presentation Layer
    ax.text(50, 95, 'PRESENTATION LAYER', ha='center', va='center', 
            fontsize=16, fontweight='bold', color=colors['primary'])
    
    # Frontend Components
    frontend_boxes = [
        {'name': 'Templates & UI', 'pos': (15, 87), 'size': (12, 6)},
        {'name': 'Bootstrap 5 CSS', 'pos': (30, 87), 'size': (12, 6)},
        {'name': 'JavaScript/AJAX', 'pos': (45, 87), 'size': (12, 6)},
        {'name': 'Responsive Design', 'pos': (60, 87), 'size': (12, 6)},
        {'name': 'Charts & Analytics', 'pos': (75, 87), 'size': (12, 6)}
    ]
    
    for box in frontend_boxes:
        rect = FancyBboxPatch(
            (box['pos'][0] - box['size'][0]/2, box['pos'][1] - box['size'][1]/2),
            box['size'][0], box['size'][1],
            boxstyle="round,pad=0.3",
            facecolor=colors['light_blue'],
            edgecolor=colors['primary'],
            linewidth=1.5
        )
        ax.add_patch(rect)
        ax.text(box['pos'][0], box['pos'][1], box['name'], 
                ha='center', va='center', fontsize=10, fontweight='bold')
    
    # === APPLICATION LAYER ===
    # Header for Application Layer
    ax.text(50, 78, 'APPLICATION LAYER - FLASK FRAMEWORK', ha='center', va='center', 
            fontsize=16, fontweight='bold', color=colors['primary'])
    
    # Main Flask App Core
    flask_core = FancyBboxPatch(
        (45, 70), 10, 5,
        boxstyle="round,pad=0.3",
        facecolor=colors['primary'],
        edgecolor=colors['text'],
        linewidth=2
    )
    ax.add_patch(flask_core)
    ax.text(50, 72.5, 'Flask Application\nCore (__init__.py)', 
            ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    # Blueprint Modules
    blueprints = [
        {'name': 'Authentication\n(auth)', 'pos': (15, 60), 'routes': ['login', 'logout', 'register', 'change_password']},
        {'name': 'Main Dashboard\n(main)', 'pos': (30, 60), 'routes': ['dashboard', 'profile', 'search']},
        {'name': 'Work Orders\n(workorders)', 'pos': (45, 60), 'routes': ['list', 'create', 'edit', 'view']},
        {'name': 'User Management\n(users)', 'pos': (60, 60), 'routes': ['list_users', 'create_user', 'edit_user']},
        {'name': 'Products\n(products)', 'pos': (75, 60), 'routes': ['list_products', 'create_product', 'companies']},
        {'name': 'Email Management\n(email_management)', 'pos': (20, 45), 'routes': ['dashboard', 'templates', 'settings']},
        {'name': 'Reporting Engine\n(reporting)', 'pos': (50, 45), 'routes': ['builder', 'execute', 'schedules']},
        {'name': 'Analytics\n(analytics)', 'pos': (80, 45), 'routes': ['stats', 'charts', 'exports']}
    ]
    
    for bp in blueprints:
        # Blueprint box
        rect = FancyBboxPatch(
            (bp['pos'][0] - 6, bp['pos'][1] - 4),
            12, 8,
            boxstyle="round,pad=0.3",
            facecolor=colors['light_grey'],
            edgecolor=colors['secondary'],
            linewidth=1.5
        )
        ax.add_patch(rect)
        ax.text(bp['pos'][0], bp['pos'][1] + 1, bp['name'], 
                ha='center', va='center', fontsize=9, fontweight='bold')
        
        # Routes
        routes_text = '\n'.join([f'• {route}' for route in bp['routes'][:3]])
        if len(bp['routes']) > 3:
            routes_text += '\n• ...'
        ax.text(bp['pos'][0], bp['pos'][1] - 2, routes_text, 
                ha='center', va='center', fontsize=7)
        
        # Connection to Flask core
        if bp['pos'][1] >= 55:  # Upper blueprints
            conn = ConnectionPatch((bp['pos'][0], bp['pos'][1] - 4), (50, 70),
                                 "data", "data", alpha=0.3, color=colors['secondary'])
            ax.add_artist(conn)
    
    # === BUSINESS LOGIC LAYER ===
    ax.text(50, 36, 'BUSINESS LOGIC LAYER', ha='center', va='center', 
            fontsize=16, fontweight='bold', color=colors['primary'])
    
    # Forms and Services
    business_components = [
        {'name': 'Forms\n(WTForms)', 'pos': (20, 28), 'details': ['Validation', 'CSRF Protection', 'Field Types']},
        {'name': 'Email Service', 'pos': (40, 28), 'details': ['SMTP Config', 'Templates', 'Notifications']},
        {'name': 'Report Engine', 'pos': (60, 28), 'details': ['Query Builder', 'Export', 'Scheduling']},
        {'name': 'Authentication', 'pos': (80, 28), 'details': ['Flask-Login', 'Password Hash', 'Sessions']}
    ]
    
    for comp in business_components:
        rect = FancyBboxPatch(
            (comp['pos'][0] - 8, comp['pos'][1] - 4),
            16, 8,
            boxstyle="round,pad=0.3",
            facecolor=colors['white'],
            edgecolor=colors['border'],
            linewidth=1.5
        )
        ax.add_patch(rect)
        ax.text(comp['pos'][0], comp['pos'][1] + 1.5, comp['name'], 
                ha='center', va='center', fontsize=10, fontweight='bold')
        
        details_text = '\n'.join([f'• {detail}' for detail in comp['details']])
        ax.text(comp['pos'][0], comp['pos'][1] - 1.5, details_text, 
                ha='center', va='center', fontsize=8)
    
    # === DATA LAYER ===
    ax.text(50, 19, 'DATA LAYER', ha='center', va='center', 
            fontsize=16, fontweight='bold', color=colors['primary'])
    
    # Database Models
    db_models = [
        {'name': 'User', 'pos': (15, 10), 'fields': ['id', 'username', 'email', 'role_id']},
        {'name': 'WorkOrder', 'pos': (30, 10), 'fields': ['id', 'title', 'status', 'priority']},
        {'name': 'Product', 'pos': (45, 10), 'fields': ['id', 'name', 'category', 'specs']},
        {'name': 'Company', 'pos': (60, 10), 'fields': ['id', 'name', 'contact', 'products']},
        {'name': 'Role', 'pos': (75, 10), 'fields': ['id', 'name', 'permissions']},
        {'name': 'EmailConfig', 'pos': (87, 10), 'fields': ['smtp_host', 'port', 'user']}
    ]
    
    for model in db_models:
        rect = FancyBboxPatch(
            (model['pos'][0] - 5, model['pos'][1] - 4),
            10, 8,
            boxstyle="round,pad=0.3",
            facecolor=colors['light_blue'],
            edgecolor=colors['primary'],
            linewidth=1.5
        )
        ax.add_patch(rect)
        ax.text(model['pos'][0], model['pos'][1] + 2, model['name'], 
                ha='center', va='center', fontsize=9, fontweight='bold')
        
        fields_text = '\n'.join([f'• {field}' for field in model['fields'][:3]])
        if len(model['fields']) > 3:
            fields_text += '\n• ...'
        ax.text(model['pos'][0], model['pos'][1] - 1, fields_text, 
                ha='center', va='center', fontsize=7)
    
    # SQLAlchemy ORM
    orm_rect = FancyBboxPatch(
        (35, 0.5), 30, 4,
        boxstyle="round,pad=0.3",
        facecolor=colors['secondary'],
        edgecolor=colors['text'],
        linewidth=2
    )
    ax.add_patch(orm_rect)
    ax.text(50, 2.5, 'SQLAlchemy ORM + SQLite Database', 
            ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    
    # Technology Stack Legend
    legend_elements = [
        mpatches.Patch(color=colors['primary'], label='Core Framework (Flask)'),
        mpatches.Patch(color=colors['light_blue'], label='Frontend/Data Models'),
        mpatches.Patch(color=colors['light_grey'], label='Blueprint Modules'),
        mpatches.Patch(color=colors['white'], label='Business Services'),
        mpatches.Patch(color=colors['secondary'], label='Database Layer')
    ]
    
    ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(0.98, 0.02))
    
    # Add architecture flow arrows
    # Frontend to Flask Core
    ax.annotate('', xy=(50, 70), xytext=(50, 80),
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['primary']))
    
    # Flask Core to Business Logic
    ax.annotate('', xy=(50, 32), xytext=(50, 65),
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['primary']))
    
    # Business Logic to Data Layer
    ax.annotate('', xy=(50, 15), xytext=(50, 24),
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['primary']))
    
    # Data Layer to Database
    ax.annotate('', xy=(50, 4.5), xytext=(50, 6),
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['primary']))
    
    plt.tight_layout()
    return fig

def create_detailed_components_diagram():
    """Create detailed component interaction diagram"""
    
    fig = plt.figure(figsize=(18, 14))
    fig.suptitle('CUBE-PRO Detailed Component Interactions & Data Flow', 
                 fontsize=20, fontweight='bold', y=0.98)
    
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    colors = {
        'primary': '#2563eb',
        'secondary': '#6b7280',
        'success': '#059669',
        'warning': '#d97706',
        'light_blue': '#dbeafe',
        'light_grey': '#f3f4f6',
        'white': '#ffffff'
    }
    
    # Key Features & Capabilities
    features = [
        {'name': 'User Authentication\n& Authorization', 'pos': (20, 85), 'color': colors['primary']},
        {'name': 'Work Order\nManagement', 'pos': (50, 85), 'color': colors['success']},
        {'name': 'Product & Company\nCatalog', 'pos': (80, 85), 'color': colors['warning']},
        
        {'name': 'Advanced Reporting\n& Analytics', 'pos': (20, 65), 'color': colors['primary']},
        {'name': 'Email Notifications\n& Templates', 'pos': (50, 65), 'color': colors['success']},
        {'name': 'Responsive UI\n& Dashboard', 'pos': (80, 65), 'color': colors['warning']},
        
        {'name': 'User Management\n& Roles', 'pos': (20, 45), 'color': colors['primary']},
        {'name': 'Multi-tier\nArchitecture', 'pos': (50, 45), 'color': colors['success']},
        {'name': 'RESTful API\nEndpoints', 'pos': (80, 45), 'color': colors['warning']}
    ]
    
    for feature in features:
        circle = Circle(feature['pos'], 8, 
                       facecolor=feature['color'], 
                       edgecolor='white', 
                       linewidth=2, 
                       alpha=0.8)
        ax.add_patch(circle)
        ax.text(feature['pos'][0], feature['pos'][1], feature['name'], 
                ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # Data Flow Diagram
    ax.text(50, 30, 'DATA FLOW & SECURITY MODEL', ha='center', va='center', 
            fontsize=16, fontweight='bold', color=colors['primary'])
    
    # Security layers
    security_layers = [
        "1. CSRF Protection (WTForms)",
        "2. Password Hashing (Werkzeug)",
        "3. Session Management (Flask-Login)",
        "4. Role-Based Access Control",
        "5. SQL Injection Prevention (SQLAlchemy ORM)",
        "6. Input Validation & Sanitization"
    ]
    
    ax.text(25, 20, 'Security Features:', ha='left', va='top', 
            fontsize=12, fontweight='bold', color=colors['primary'])
    
    for i, layer in enumerate(security_layers):
        ax.text(25, 17 - i*2, layer, ha='left', va='center', fontsize=10)
    
    # Technology Stack
    tech_stack = [
        "• Backend: Python Flask Framework",
        "• Database: SQLite with SQLAlchemy ORM",
        "• Frontend: HTML5, Bootstrap 5, JavaScript",
        "• Authentication: Flask-Login",
        "• Forms: WTForms with CSRF protection",
        "• Email: SMTP integration",
        "• Charts: Chart.js for analytics",
        "• PDF Generation: ReportLab"
    ]
    
    ax.text(60, 20, 'Technology Stack:', ha='left', va='top', 
            fontsize=12, fontweight='bold', color=colors['primary'])
    
    for i, tech in enumerate(tech_stack):
        ax.text(60, 17 - i*1.5, tech, ha='left', va='center', fontsize=10)
    
    plt.tight_layout()
    return fig

def create_deployment_diagram():
    """Create deployment and infrastructure diagram"""
    
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('CUBE-PRO Deployment Architecture & Infrastructure', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    colors = {
        'primary': '#2563eb',
        'secondary': '#6b7280',
        'success': '#059669',
        'light_blue': '#dbeafe',
        'white': '#ffffff'
    }
    
    # Development Environment
    dev_rect = FancyBboxPatch(
        (10, 75), 35, 20,
        boxstyle="round,pad=1",
        facecolor=colors['light_blue'],
        edgecolor=colors['primary'],
        linewidth=2
    )
    ax.add_patch(dev_rect)
    ax.text(27.5, 90, 'DEVELOPMENT ENVIRONMENT', 
            ha='center', va='center', fontsize=12, fontweight='bold')
    
    dev_components = [
        "• Python Virtual Environment (.venv)",
        "• Flask Development Server",
        "• SQLite Database (workorder.db)",
        "• Debug Mode: ON",
        "• Hot Reload: Enabled",
        "• Port: 5000 (localhost)"
    ]
    
    for i, comp in enumerate(dev_components):
        ax.text(12, 87 - i*2, comp, ha='left', va='center', fontsize=9)
    
    # Production Environment
    prod_rect = FancyBboxPatch(
        (55, 75), 35, 20,
        boxstyle="round,pad=1",
        facecolor=colors['success'],
        edgecolor=colors['secondary'],
        linewidth=2,
        alpha=0.3
    )
    ax.add_patch(prod_rect)
    ax.text(72.5, 90, 'PRODUCTION ENVIRONMENT', 
            ha='center', va='center', fontsize=12, fontweight='bold')
    
    prod_components = [
        "• WSGI Server (Gunicorn/uWSGI)",
        "• Reverse Proxy (Nginx)",
        "• PostgreSQL/MySQL Database",
        "• SSL/TLS Encryption",
        "• Load Balancing",
        "• Monitoring & Logging"
    ]
    
    for i, comp in enumerate(prod_components):
        ax.text(57, 87 - i*2, comp, ha='left', va='center', fontsize=9)
    
    # File Structure
    ax.text(50, 65, 'PROJECT STRUCTURE', ha='center', va='center', 
            fontsize=16, fontweight='bold', color=colors['primary'])
    
    file_structure = [
        "CUBE/",
        "├── app/",
        "│   ├── __init__.py (Flask app factory)",
        "│   ├── models.py (Database models)",
        "│   ├── auth/ (Authentication blueprint)",
        "│   ├── main/ (Dashboard blueprint)",
        "│   ├── workorders/ (Work order management)",
        "│   ├── users/ (User management)",
        "│   ├── products/ (Product catalog)",
        "│   ├── email_management/ (Email system)",
        "│   ├── reporting/ (Analytics engine)",
        "│   ├── templates/ (Jinja2 templates)",
        "│   └── static/ (CSS, JS, images)",
        "├── instance/ (Database files)",
        "├── requirements.txt (Dependencies)",
        "├── run.py (Application entry point)",
        "└── Documentation (PDFs, guides)"
    ]
    
    ax.text(20, 55, '\n'.join(file_structure), ha='left', va='top', 
            fontsize=9, fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['white'], 
                     edgecolor=colors['secondary']))
    
    # Scalability Notes
    scalability_notes = [
        "SCALABILITY CONSIDERATIONS:",
        "",
        "• Modular Blueprint Architecture",
        "• Database Migration Support (Flask-Migrate)",
        "• RESTful API Design",
        "• Stateless Session Management",
        "• Caching Strategy Ready",
        "• Horizontal Scaling Capable",
        "• Microservices Migration Path",
        "• Container Deployment Ready (Docker)"
    ]
    
    ax.text(60, 55, '\n'.join(scalability_notes), ha='left', va='top', 
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.5", facecolor=colors['light_blue'], 
                     edgecolor=colors['primary']))
    
    plt.tight_layout()
    return fig

def save_architecture_pdf():
    """Save all architecture diagrams to a comprehensive PDF"""
    
    filename = 'CUBE_PRO_Architecture_Diagram.pdf'
    
    with PdfPages(filename) as pdf:
        # Page 1: Main Architecture Diagram
        fig1 = create_architecture_diagram()
        pdf.savefig(fig1, bbox_inches='tight', dpi=300)
        plt.close(fig1)
        
        # Page 2: Detailed Components
        fig2 = create_detailed_components_diagram()
        pdf.savefig(fig2, bbox_inches='tight', dpi=300)
        plt.close(fig2)
        
        # Page 3: Deployment Architecture
        fig3 = create_deployment_diagram()
        pdf.savefig(fig3, bbox_inches='tight', dpi=300)
        plt.close(fig3)
        
        # Set PDF metadata
        d = pdf.infodict()
        d['Title'] = 'CUBE-PRO Enterprise Work Order Management System - Architecture Diagram'
        d['Author'] = 'CUBE-PRO Development Team'
        d['Subject'] = 'Application Architecture and System Design'
        d['Keywords'] = 'Flask, Python, Work Order Management, Enterprise, Architecture'
        d['Creator'] = 'CUBE-PRO Architecture Generator'
        d['Producer'] = 'Matplotlib PDF Backend'
    
    print(f"✅ Architecture diagram saved as: {filename}")
    print(f"📄 Contains 3 comprehensive pages:")
    print(f"   1. Main Application Architecture")
    print(f"   2. Detailed Component Interactions")
    print(f"   3. Deployment & Infrastructure")
    
    return filename

if __name__ == "__main__":
    print("🎨 Generating CUBE-PRO Architecture Diagram...")
    print("=" * 50)
    
    try:
        filename = save_architecture_pdf()
        print("=" * 50)
        print(f"🎉 Successfully created comprehensive architecture diagram!")
        print(f"📁 File location: {filename}")
        print("💡 The diagram includes:")
        print("   • Multi-layer application architecture")
        print("   • Flask blueprint structure") 
        print("   • Database model relationships")
        print("   • Component interactions")
        print("   • Technology stack details")
        print("   • Security implementation")
        print("   • Deployment considerations")
        
    except Exception as e:
        print(f"❌ Error generating diagram: {e}")
        print("💡 Make sure matplotlib is installed: pip install matplotlib")
