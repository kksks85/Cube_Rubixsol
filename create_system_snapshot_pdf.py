"""
CUBE-PRO System Snapshot PDF Generator
Creates a comprehensive PDF documentation of the system architecture and tech stack
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as ReportLabImage
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_system_snapshot_pdf():
    """Create a comprehensive PDF documentation of the CUBE-PRO system"""
    
    filename = f"CUBE_PRO_System_Snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=HexColor('#0176d3'),
        alignment=TA_CENTER
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        spaceBefore=20,
        textColor=HexColor('#0176d3')
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=12,
        textColor=HexColor('#014486')
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=6,
        spaceBefore=8,
        textColor=HexColor('#5a6c7d')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
        leftIndent=20,
        bulletIndent=10
    )
    
    # Title Page
    story.append(Paragraph("CUBE-PRO", title_style))
    story.append(Paragraph("Enterprise UAV Service Management System", heading2_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("System Architecture & Technology Stack Snapshot", heading1_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Document metadata
    metadata_data = [
        ['Generated:', datetime.now().strftime('%B %d, %Y at %H:%M:%S')],
        ['Document Type:', 'Technical Architecture Documentation'],
        ['System Version:', 'CUBE-PRO v2.0'],
        ['Framework:', 'Python Flask with SQLAlchemy ORM'],
        ['Owner:', 'Rubix Solutions']
    ]
    
    metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f4f6f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#d8dde6')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(metadata_table)
    story.append(PageBreak())
    
    # Table of Contents
    story.append(Paragraph("Table of Contents", heading1_style))
    
    toc_data = [
        ['1. Architecture Overview', '3'],
        ['2. Technology Stack', '4'],
        ['3. Database Architecture', '6'],
        ['4. Application Modules', '8'],
        ['5. Frontend Architecture', '10'],
        ['6. Advanced Features', '12'],
        ['7. Data & Analytics', '14'],
        ['8. Deployment & Configuration', '15'],
        ['9. Security & Performance', '16'],
        ['10. Enterprise Features', '17']
    ]
    
    toc_table = Table(toc_data, colWidths=[5*inch, 1*inch])
    toc_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, HexColor('#e5e9ef')),
    ]))
    
    story.append(toc_table)
    story.append(PageBreak())
    
    # 1. Architecture Overview
    story.append(Paragraph("1. Architecture Overview", heading1_style))
    
    story.append(Paragraph("Core Technology Stack", heading2_style))
    overview_text = """
    CUBE-PRO is a comprehensive enterprise-grade UAV service management system built on modern web technologies. 
    The system employs a Model-View-Controller (MVC) architecture pattern using Python Flask as the primary framework, 
    providing scalable and maintainable code structure through Blueprint-based modular design.
    """
    story.append(Paragraph(overview_text, body_style))
    
    # Technology stack table
    tech_stack_data = [
        ['Component', 'Technology', 'Version', 'Purpose'],
        ['Backend Framework', 'Python Flask', '2.3.3', 'Web application framework'],
        ['Database ORM', 'SQLAlchemy', '3.0.5', 'Object-relational mapping'],
        ['Authentication', 'Flask-Login', '0.6.3', 'User session management'],
        ['Forms', 'WTForms + Flask-WTF', '3.0.1 + 1.1.1', 'Form handling and validation'],
        ['Database', 'SQLite/PostgreSQL', 'Latest', 'Data persistence'],
        ['Frontend Framework', 'Bootstrap', '5.3.2', 'Responsive UI components'],
        ['JavaScript', 'Vanilla ES6+', 'Native', 'Client-side interactions'],
        ['Charts', 'Chart.js', 'Latest', 'Data visualization'],
        ['Icons', 'Font Awesome', '6.x', 'Icon library'],
        ['Analytics', 'Plotly + Pandas', '5.17.0 + 2.1.1', 'Advanced reporting']
    ]
    
    tech_table = Table(tech_stack_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 2.5*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0176d3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#d8dde6')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#fafbfc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#fafbfc'), white]),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(tech_table)
    story.append(PageBreak())
    
    # 2. Database Architecture
    story.append(Paragraph("2. Database Architecture", heading1_style))
    
    story.append(Paragraph("Core Models (22 Total)", heading2_style))
    
    models_text = """
    The system employs a comprehensive database schema with 22 interconnected models, providing complete 
    coverage for enterprise UAV service management operations.
    """
    story.append(Paragraph(models_text, body_style))
    
    # Database models table
    models_data = [
        ['Category', 'Models', 'Purpose'],
        ['User Management', 'User, Role', 'Authentication and authorization'],
        ['Work Orders', 'WorkOrder, WorkOrderActivity, WorkOrderPart', 'Service ticket management'],
        ['Products', 'Product, ProductCategory, ProductSpecification, ProductImage, Company', 'UAV catalog management'],
        ['Inventory', 'InventoryCategory, InventoryItem, InventoryTransaction', 'Parts and stock management'],
        ['Service Management', 'ServiceCategory, ServiceIncident, ServicePart, ServiceActivity, ServiceSoftwareUpdate, ServiceTemplate', 'Comprehensive service workflow'],
        ['Reporting', 'SavedReport, ReportSchedule, ReportExecutionLog', 'Analytics and reporting'],
        ['Support Tables', 'Priority, Status, Category', 'Reference data']
    ]
    
    models_table = Table(models_data, colWidths=[1.5*inch, 3*inch, 2*inch])
    models_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#014486')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#d8dde6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f4f6f9')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(models_table)
    
    story.append(Paragraph("Key Relationships", heading3_style))
    relationships_text = """
    • <b>One-to-Many:</b> Users → Work Orders, Categories → Products, Companies → Products<br/>
    • <b>Many-to-Many:</b> Work Orders ↔ Inventory Parts through WorkOrderPart junction table<br/>
    • <b>Complex Workflows:</b> Service Incidents with 8-step workflow tracking and status management<br/>
    • <b>Audit Trails:</b> Activity logging for all critical operations with timestamp tracking
    """
    story.append(Paragraph(relationships_text, body_style))
    
    story.append(PageBreak())
    
    # 3. Application Modules
    story.append(Paragraph("3. Application Modules", heading1_style))
    
    story.append(Paragraph("8 Primary Modules", heading2_style))
    
    modules_data = [
        ['Module', 'Route Prefix', 'Primary Functions', 'Key Features'],
        ['Authentication', '/auth', 'Login, logout, password management', 'Session handling, role-based access'],
        ['Main Dashboard', '/', 'Overview, statistics, navigation', 'Real-time updates, analytics widgets'],
        ['Work Orders', '/workorders', 'CRUD operations, status tracking', 'Activity logging, assignment management'],
        ['Inventory', '/inventory', 'Parts management, stock tracking', 'UAV-specific categories, cost tracking'],
        ['Service Management', '/service', 'UAV service incidents, workflow', '8-step process, template management'],
        ['Products', '/products', 'UAV catalog, specifications', 'Company management, technical specs'],
        ['User Management', '/users', 'Admin, role management', 'Bulk operations, user analytics'],
        ['Reporting', '/reporting', 'Custom reports, analytics', 'Scheduled reports, multiple formats']
    ]
    
    modules_table = Table(modules_data, colWidths=[1.2*inch, 1*inch, 2.3*inch, 2*inch])
    modules_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#5a6c7d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#d8dde6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#fafbfc')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(modules_table)
    
    story.append(Paragraph("Additional Modules", heading3_style))
    additional_text = """
    • <b>Email Management (/email-management):</b> SMTP configuration, template management, notification system<br/>
    • <b>API Endpoints:</b> Real-time dashboard updates, data synchronization, mobile app support
    """
    story.append(Paragraph(additional_text, body_style))
    
    story.append(PageBreak())
    
    # 4. Frontend Architecture
    story.append(Paragraph("4. Frontend Architecture", heading1_style))
    
    story.append(Paragraph("Responsive Design", heading2_style))
    frontend_text = """
    The frontend architecture is built on modern web standards with a mobile-first approach, 
    ensuring optimal user experience across all device types and screen sizes.
    """
    story.append(Paragraph(frontend_text, body_style))
    
    frontend_features_data = [
        ['Component', 'Technology/Approach', 'Implementation Details'],
        ['Responsive Framework', 'Bootstrap 5.3.2', 'Mobile-first grid system, utility classes'],
        ['Theme System', 'CSS Variables + JavaScript', 'Light/Dark mode toggle with localStorage persistence'],
        ['Color Scheme', 'Enterprise Blue/Grey Palette', 'Professional corporate identity with accessibility compliance'],
        ['Typography', 'Inter Font Family', 'Modern, readable typeface with multiple weights'],
        ['JavaScript Architecture', 'Vanilla ES6+ Modules', 'No framework dependencies, modern browser APIs'],
        ['Real-time Updates', 'AJAX + Fetch API', '30-second dashboard refresh, live statistics'],
        ['Interactive Elements', 'Bootstrap Components', 'Form validation, modals, tooltips, progress bars'],
        ['Chart Integration', 'Chart.js', 'Dynamic data visualization with responsive design'],
        ['Icon System', 'Font Awesome 6.x', 'Comprehensive icon library with consistent styling'],
        ['Loading States', 'Custom CSS + JavaScript', 'Professional UX feedback with spinners and animations']
    ]
    
    frontend_table = Table(frontend_features_data, colWidths=[1.5*inch, 2*inch, 3*inch])
    frontend_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#04844b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#d8dde6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f4f6f9'), white]),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(frontend_table)
    
    story.append(Paragraph("Template Structure", heading3_style))
    template_text = """
    • <b>Base Templates:</b> base.html and base_new.html providing consistent layout and styling<br/>
    • <b>Modular Components:</b> Reusable blocks for forms, tables, navigation, and data display<br/>
    • <b>Jinja2 Features:</b> Custom filters, macros, template inheritance for maintainable code
    """
    story.append(Paragraph(template_text, body_style))
    
    story.append(PageBreak())
    
    # 5. Advanced Features
    story.append(Paragraph("5. Advanced Features", heading1_style))
    
    story.append(Paragraph("Service Management System", heading2_style))
    service_features_text = """
    The service management system provides a comprehensive 8-step workflow for UAV maintenance and repair operations, 
    with built-in quality control and progress tracking at each stage.
    """
    story.append(Paragraph(service_features_text, body_style))
    
    workflow_data = [
        ['Step', 'Status', 'Activities', 'Integration Points'],
        ['1', 'Received', 'Initial intake, documentation', 'Work order creation, customer notification'],
        ['2', 'Inspection', 'Visual and technical assessment', 'Photo documentation, preliminary diagnosis'],
        ['3', 'Diagnosis', 'Detailed analysis and testing', 'Parts requirement identification'],
        ['4', 'Approval', 'Customer approval for repairs', 'Cost estimation, timeline communication'],
        ['5', 'Parts', 'Parts ordering and allocation', 'Inventory integration, supplier management'],
        ['6', 'Repair', 'Actual repair work', 'Technician assignment, time tracking'],
        ['7', 'Testing', 'Quality assurance testing', 'Flight testing, functionality validation'],
        ['8', 'Complete', 'Final delivery preparation', 'Customer notification, invoicing']
    ]
    
    workflow_table = Table(workflow_data, colWidths=[0.5*inch, 1*inch, 2.5*inch, 2.5*inch])
    workflow_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#fe9339')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#d8dde6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#fff7ed'), white]),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(workflow_table)
    
    story.append(Paragraph("Real-time Dashboard Features", heading3_style))
    dashboard_text = """
    • <b>Live Statistics:</b> Auto-refreshing work order counts with 30-second update intervals<br/>
    • <b>Cache Management:</b> Intelligent cache-busting to prevent stale data display<br/>
    • <b>API Integration:</b> RESTful endpoints for real-time data synchronization<br/>
    • <b>Session Handling:</b> Automatic database session management for data consistency
    """
    story.append(Paragraph(dashboard_text, body_style))
    
    story.append(Paragraph("Inventory Management", heading3_style))
    inventory_text = """
    • <b>UAV-Specific Categories:</b> Pre-configured for drone components (Motors, Flight Controllers, Sensors, etc.)<br/>
    • <b>Smart Stock Tracking:</b> Minimum/maximum level alerts with automatic reorder suggestions<br/>
    • <b>Cost Management:</b> Comprehensive cost tracking with unit and total calculations<br/>
    • <b>Transaction History:</b> Complete audit trail for all inventory movements and adjustments
    """
    story.append(Paragraph(inventory_text, body_style))
    
    story.append(PageBreak())
    
    # 6. Data & Analytics
    story.append(Paragraph("6. Data & Analytics", heading1_style))
    
    story.append(Paragraph("Reporting Engine", heading2_style))
    reporting_text = """
    The integrated reporting engine provides comprehensive analytics capabilities with custom report building, 
    automated scheduling, and multiple export formats for business intelligence and operational insights.
    """
    story.append(Paragraph(reporting_text, body_style))
    
    analytics_data = [
        ['Feature', 'Capability', 'Business Value'],
        ['Custom Report Builder', 'Drag-and-drop query interface', 'Self-service analytics for non-technical users'],
        ['Scheduled Reports', 'Automated generation and delivery', 'Regular business intelligence updates'],
        ['Export Formats', 'CSV, Excel, PDF with custom formatting', 'Flexible data sharing and presentation'],
        ['Report Templates', 'Saved configurations and parameters', 'Standardized reporting across organization'],
        ['Dashboard Analytics', 'Real-time KPI monitoring', 'Immediate operational visibility'],
        ['Work Order Metrics', 'Status distribution, completion rates', 'Performance measurement and optimization'],
        ['Inventory Analytics', 'Stock levels, cost analysis, trends', 'Supply chain optimization'],
        ['Service Metrics', 'Workflow tracking, performance KPIs', 'Service quality and efficiency monitoring'],
        ['User Activity', 'Login tracking, role-based usage', 'System utilization and security monitoring']
    ]
    
    analytics_table = Table(analytics_data, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
    analytics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0070d2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#d8dde6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f0f8ff'), white]),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(analytics_table)
    
    story.append(PageBreak())
    
    # 7. Security & Performance
    story.append(Paragraph("7. Security & Performance", heading1_style))
    
    story.append(Paragraph("Security Features", heading2_style))
    
    security_data = [
        ['Security Layer', 'Implementation', 'Protection Level'],
        ['Authentication', 'Flask-Login session management', 'User identity verification'],
        ['Password Security', 'Werkzeug hashing with salt', 'Strong password protection'],
        ['CSRF Protection', 'Flask-WTF token validation', 'Form submission security'],
        ['Role-Based Access', 'Admin, Manager, Technician roles', 'Granular permission control'],
        ['Session Management', 'Secure cookie handling', 'Session hijacking prevention'],
        ['Input Validation', 'WTForms server-side validation', 'Data integrity and XSS prevention'],
        ['SQL Injection Prevention', 'SQLAlchemy ORM parameterized queries', 'Database security'],
        ['Audit Logging', 'Comprehensive activity tracking', 'Security monitoring and compliance']
    ]
    
    security_table = Table(security_data, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
    security_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ea001e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#d8dde6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#fef2f2'), white]),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(security_table)
    
    story.append(Paragraph("Performance Optimizations", heading3_style))
    performance_text = """
    • <b>Database Indexing:</b> Strategic indexes on frequently queried fields for optimal performance<br/>
    • <b>Lazy Loading:</b> SQLAlchemy relationship optimization to minimize database queries<br/>
    • <b>Cache Headers:</b> Browser cache management for static assets and dynamic content<br/>
    • <b>AJAX Updates:</b> Reduced page reloads with targeted content updates<br/>
    • <b>Efficient Queries:</b> Optimized database queries with proper joins and filtering
    """
    story.append(Paragraph(performance_text, body_style))
    
    story.append(PageBreak())
    
    # 8. Enterprise Features
    story.append(Paragraph("8. Enterprise Features", heading1_style))
    
    story.append(Paragraph("Professional UI/UX Design", heading2_style))
    enterprise_text = """
    The system features a professional enterprise-grade user interface designed for productivity and ease of use 
    in demanding business environments.
    """
    story.append(Paragraph(enterprise_text, body_style))
    
    ui_features_text = """
    • <b>Enterprise Color Scheme:</b> Professional blue and grey palette for corporate environments<br/>
    • <b>Consistent Typography:</b> Inter font family for modern, readable text across all interfaces<br/>
    • <b>Responsive Tables:</b> Mobile-optimized data display with sorting and filtering capabilities<br/>
    • <b>Loading Indicators:</b> Professional feedback mechanisms for all user interactions<br/>
    • <b>Accessibility Compliance:</b> WCAG guidelines adherence for inclusive design
    """
    story.append(Paragraph(ui_features_text, body_style))
    
    story.append(Paragraph("Business Logic & Operations", heading3_style))
    business_text = """
    • <b>Workflow Management:</b> 8-step service processes with automated progression and validation<br/>
    • <b>Cost Tracking:</b> Detailed financial management with labor, parts, and overhead calculations<br/>
    • <b>Audit Trails:</b> Complete activity logging for compliance and quality assurance<br/>
    • <b>Multi-tenant Support:</b> Company-based organization for service bureau operations<br/>
    • <b>Integration Ready:</b> API endpoints for third-party system integration
    """
    story.append(Paragraph(business_text, body_style))
    
    story.append(Paragraph("Deployment Architecture", heading3_style))
    deployment_text = """
    • <b>Environment Configuration:</b> Python virtual environments with dependency management<br/>
    • <b>Database Migrations:</b> Flask-Migrate support for schema evolution<br/>
    • <b>Production Ready:</b> Gunicorn WSGI server configuration for scalable deployment<br/>
    • <b>Configuration Management:</b> Environment variables and secure configuration handling<br/>
    • <b>Monitoring Ready:</b> Structured logging and health check endpoints
    """
    story.append(Paragraph(deployment_text, body_style))
    
    # File Structure
    story.append(Paragraph("File Structure Overview", heading3_style))
    structure_text = """
    <font name="Courier" size="8">
    CUBE/<br/>
    ├── app/                    # Main application package<br/>
    │   ├── auth/              # Authentication module<br/>
    │   ├── main/              # Dashboard and core functionality<br/>
    │   ├── workorders/        # Work order management<br/>
    │   ├── inventory/         # Inventory and parts system<br/>
    │   ├── service/           # Service management workflow<br/>
    │   ├── products/          # Product catalog management<br/>
    │   ├── users/             # User administration<br/>
    │   ├── reporting/         # Analytics and reporting engine<br/>
    │   ├── email_management/  # Email system and templates<br/>
    │   ├── static/           # CSS, JavaScript, and assets<br/>
    │   └── templates/        # Jinja2 HTML templates<br/>
    ├── instance/             # Database and instance files<br/>
    ├── requirements.txt      # Python dependencies<br/>
    └── run.py               # Application entry point
    </font>
    """
    story.append(Paragraph(structure_text, body_style))
    
    story.append(PageBreak())
    
    # Summary
    story.append(Paragraph("System Summary", heading1_style))
    
    summary_text = """
    CUBE-PRO represents a comprehensive, enterprise-grade work order management system specifically designed for UAV service operations. 
    Built on modern web technologies with Flask and SQLAlchemy, the system provides a robust foundation for managing complex service workflows, 
    inventory operations, and business analytics.
    
    The 8-step service workflow, real-time dashboard updates, and comprehensive reporting capabilities make this system suitable for 
    professional UAV service centers, corporate fleet management, and multi-tenant service bureau operations.
    
    With its modular architecture, security features, and professional user interface, CUBE-PRO provides the scalability and 
    reliability required for mission-critical UAV service management operations.
    """
    story.append(Paragraph(summary_text, body_style))
    
    # Footer information
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("© 2025 Rubix Solutions - CUBE-PRO Enterprise UAV Service Management System", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=HexColor('#5a6c7d'), alignment=TA_CENTER)))
    
    # Build PDF
    doc.build(story)
    print(f"✓ System snapshot PDF created: {filename}")
    return filename

if __name__ == "__main__":
    try:
        # Install required package if not available
        try:
            import reportlab
        except ImportError:
            print("Installing reportlab package...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
            import reportlab
        
        filename = create_system_snapshot_pdf()
        print(f"PDF documentation generated successfully: {filename}")
        
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
        print("Please ensure reportlab is installed: pip install reportlab")
