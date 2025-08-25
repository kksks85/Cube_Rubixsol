#!/usr/bin/env python3
"""
CUBE - PRO Troubleshooting Guide Generator
Creates a comprehensive PDF troubleshooting guide for common system issues
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os

class TroubleshootingGuideGenerator:
    def __init__(self):
        self.filename = "CUBE_PRO_Troubleshooting_Guide.pdf"
        self.doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#34495e')
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.HexColor('#7f8c8d')
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        self.code_style = ParagraphStyle(
            'CodeStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Courier',
            backColor=colors.HexColor('#f8f9fa'),
            borderColor=colors.HexColor('#e9ecef'),
            borderWidth=1,
            borderPadding=8,
            spaceAfter=12
        )

    def add_title_page(self):
        """Add title page"""
        # Title
        title = Paragraph("CUBE - PRO", self.title_style)
        subtitle = Paragraph("Troubleshooting Guide", 
                            ParagraphStyle('Subtitle', parent=self.styles['Heading2'], 
                                         fontSize=18, alignment=TA_CENTER, 
                                         textColor=colors.HexColor('#7f8c8d')))
        
        # Version and date
        version_info = Paragraph(f"Version 1.0<br/>Generated: {datetime.now().strftime('%B %d, %Y')}", 
                               ParagraphStyle('VersionInfo', parent=self.styles['Normal'], 
                                            fontSize=12, alignment=TA_CENTER))
        
        # Company info
        company_info = Paragraph(
            "Enterprise Work Order Management System<br/>Technical Documentation",
            ParagraphStyle('CompanyInfo', parent=self.styles['Normal'], 
                         fontSize=11, alignment=TA_CENTER, textColor=colors.HexColor('#95a5a6'))
        )
        
        self.story.extend([
            Spacer(1, 2*inch),
            title,
            subtitle,
            Spacer(1, 1*inch),
            version_info,
            Spacer(1, 0.5*inch),
            company_info,
            PageBreak()
        ])

    def add_table_of_contents(self):
        """Add table of contents"""
        toc_title = Paragraph("Table of Contents", self.heading_style)
        self.story.append(toc_title)
        
        toc_items = [
            "1. System Overview",
            "2. Authentication Issues",
            "3. Database Connection Problems",
            "4. Work Order Management Issues",
            "5. Product Management Issues",
            "6. Email Management Issues",
            "7. User Management Issues",
            "8. Performance Issues",
            "9. Security Issues",
            "10. Deployment Issues",
            "11. Browser Compatibility Issues",
            "12. Emergency Procedures",
            "13. Appendix: Error Codes",
            "14. Contact Information"
        ]
        
        for item in toc_items:
            toc_item = Paragraph(item, self.body_style)
            self.story.append(toc_item)
        
        self.story.append(PageBreak())

    def add_system_overview(self):
        """Add system overview section"""
        self.story.append(Paragraph("1. System Overview", self.heading_style))
        
        overview_text = """
        CUBE - PRO is a Flask-based enterprise work order management system built with Python, SQLAlchemy, 
        and Bootstrap. This troubleshooting guide covers common issues, their root causes, and step-by-step 
        solutions for system administrators and technical support teams.
        """
        self.story.append(Paragraph(overview_text, self.body_style))
        
        # System Architecture
        self.story.append(Paragraph("System Architecture", self.subheading_style))
        arch_text = """
        • Frontend: HTML5, CSS3, JavaScript, Bootstrap 5<br/>
        • Backend: Python Flask Framework<br/>
        • Database: SQLite (Development), PostgreSQL/MySQL (Production)<br/>
        • Authentication: Flask-Login with role-based access<br/>
        • Email: SMTP integration for notifications<br/>
        • Deployment: WSGI-compatible servers (Gunicorn, uWSGI)
        """
        self.story.append(Paragraph(arch_text, self.body_style))
        self.story.append(Spacer(1, 12))

    def add_authentication_issues(self):
        """Add authentication troubleshooting section"""
        self.story.append(Paragraph("2. Authentication Issues", self.heading_style))
        
        # Login failures
        self.story.append(Paragraph("2.1 Login Failures", self.subheading_style))
        
        auth_table_data = [
            ['Issue', 'Root Cause', 'Solution'],
            ['Invalid credentials error', 'Wrong username/password', '1. Verify credentials\n2. Check caps lock\n3. Reset password if needed'],
            ['User account locked', 'Multiple failed login attempts', '1. Check user.is_active status\n2. Reset account via admin panel\n3. Clear failed login attempts'],
            ['Session expires immediately', 'Flask session configuration', '1. Check SECRET_KEY configuration\n2. Verify session timeout settings\n3. Check browser cookies'],
            ['Role permissions denied', 'Incorrect user role assignment', '1. Verify user role in database\n2. Check role permissions\n3. Update user role if needed'],
            ['Login page not loading', 'Template or route issues', '1. Check Flask routes\n2. Verify template files\n3. Check static file serving']
        ]
        
        auth_table = Table(auth_table_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
        auth_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        self.story.append(auth_table)
        self.story.append(Spacer(1, 12))

    def add_database_issues(self):
        """Add database troubleshooting section"""
        self.story.append(Paragraph("3. Database Connection Problems", self.heading_style))
        
        # Database connection issues
        self.story.append(Paragraph("3.1 Connection Issues", self.subheading_style))
        
        db_issues = [
            {
                'problem': 'Database file not found (SQLite)',
                'cause': 'Missing database file or incorrect path',
                'solution': '1. Check SQLALCHEMY_DATABASE_URI in config\n2. Run database initialization: python -c "from app import db; db.create_all()"\n3. Verify file permissions'
            },
            {
                'problem': 'OperationalError: no such table',
                'cause': 'Database tables not created',
                'solution': '1. Run migrations: flask db upgrade\n2. Initialize database: python init_db.py\n3. Check model definitions'
            },
            {
                'problem': 'Connection timeout',
                'cause': 'Database server unavailable or network issues',
                'solution': '1. Check database server status\n2. Verify network connectivity\n3. Check connection pool settings\n4. Review firewall rules'
            },
            {
                'problem': 'Permission denied errors',
                'cause': 'Insufficient database user privileges',
                'solution': '1. Check database user permissions\n2. Grant necessary privileges\n3. Verify database user exists\n4. Check connection string credentials'
            }
        ]
        
        for issue in db_issues:
            self.story.append(Paragraph(f"<b>Problem:</b> {issue['problem']}", self.body_style))
            self.story.append(Paragraph(f"<b>Root Cause:</b> {issue['cause']}", self.body_style))
            self.story.append(Paragraph(f"<b>Solution:</b>", self.body_style))
            self.story.append(Paragraph(issue['solution'], self.code_style))
            self.story.append(Spacer(1, 8))

    def add_workorder_issues(self):
        """Add work order management troubleshooting section"""
        self.story.append(Paragraph("4. Work Order Management Issues", self.heading_style))
        
        # Work order creation issues
        self.story.append(Paragraph("4.1 Work Order Creation Problems", self.subheading_style))
        
        wo_issues = [
            {
                'problem': 'Work order creation fails',
                'cause': 'Form validation errors or database constraints',
                'solution': '1. Check required fields are filled\n2. Verify data types and lengths\n3. Check foreign key constraints\n4. Review form validation logic'
            },
            {
                'problem': 'Work order number not generating',
                'cause': 'Auto-increment or sequence issues',
                'solution': '1. Check work_order_number generation logic\n2. Verify database sequence\n3. Check for duplicate numbers\n4. Reset sequence if needed'
            },
            {
                'problem': 'Status transitions not working',
                'cause': 'Workflow validation or permission issues',
                'solution': '1. Check status transition rules\n2. Verify user permissions\n3. Review workflow logic\n4. Check WorkOrderStatus table'
            },
            {
                'problem': 'Assignment notifications not sent',
                'cause': 'Email configuration or template issues',
                'solution': '1. Check SMTP settings\n2. Verify email templates\n3. Check notification triggers\n4. Review email logs'
            }
        ]
        
        for issue in wo_issues:
            self.story.append(Paragraph(f"<b>{issue['problem']}</b>", 
                            ParagraphStyle('IssueName', parent=self.body_style, 
                                         textColor=colors.HexColor('#e74c3c'))))
            self.story.append(Paragraph(f"<i>Cause:</i> {issue['cause']}", self.body_style))
            self.story.append(Paragraph(f"<i>Solution:</i> {issue['solution']}", self.body_style))
            self.story.append(Spacer(1, 8))

    def add_product_issues(self):
        """Add product management troubleshooting section"""
        self.story.append(Paragraph("5. Product Management Issues", self.heading_style))
        
        product_issues = [
            {
                'problem': 'Product creation fails with duplicate error',
                'cause': 'Unique constraint violation on product code',
                'solution': '1. Check for existing product codes\n2. Use different product code\n3. Review unique constraints\n4. Check data import process'
            },
            {
                'problem': 'Company-product relationship broken',
                'cause': 'Foreign key constraint or orphaned records',
                'solution': '1. Verify company exists\n2. Check foreign key relationships\n3. Clean up orphaned records\n4. Re-establish relationships'
            },
            {
                'problem': 'Product images not displaying',
                'cause': 'File path issues or missing static files',
                'solution': '1. Check static file configuration\n2. Verify image file paths\n3. Check file permissions\n4. Review upload directory settings'
            }
        ]
        
        for issue in product_issues:
            self.story.append(Paragraph(f"<b>{issue['problem']}</b>", self.subheading_style))
            self.story.append(Paragraph(issue['cause'], self.body_style))
            self.story.append(Paragraph(issue['solution'], self.code_style))
            self.story.append(Spacer(1, 10))

    def add_email_issues(self):
        """Add email management troubleshooting section"""
        self.story.append(Paragraph("6. Email Management Issues", self.heading_style))
        
        email_table_data = [
            ['Issue', 'Diagnostic Steps', 'Solution'],
            ['SMTP connection failed', '1. Test SMTP settings\n2. Check firewall\n3. Verify credentials', '1. Update SMTP configuration\n2. Use app passwords for Gmail\n3. Check port settings (587/465)'],
            ['Emails not sending', '1. Check email logs\n2. Verify templates\n3. Test connectivity', '1. Fix SMTP configuration\n2. Update email templates\n3. Check email queue'],
            ['Template rendering errors', '1. Check template syntax\n2. Verify variables\n3. Test rendering', '1. Fix Jinja2 syntax\n2. Add missing variables\n3. Update template logic'],
            ['High bounce rate', '1. Check email addresses\n2. Review content\n3. Check reputation', '1. Clean email list\n2. Improve content\n3. Use proper sender domain']
        ]
        
        email_table = Table(email_table_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
        email_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fff8')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        self.story.append(email_table)
        self.story.append(Spacer(1, 12))

    def add_performance_issues(self):
        """Add performance troubleshooting section"""
        self.story.append(Paragraph("8. Performance Issues", self.heading_style))
        
        perf_text = """
        Performance issues can significantly impact user experience. Here are common performance problems and solutions:
        """
        self.story.append(Paragraph(perf_text, self.body_style))
        
        # Performance optimization table
        perf_data = [
            ['Symptom', 'Likely Cause', 'Optimization'],
            ['Slow page loading', 'Large database queries\nUnoptimized templates', '1. Add database indexes\n2. Optimize queries\n3. Use pagination\n4. Enable caching'],
            ['High memory usage', 'Memory leaks\nLarge datasets in memory', '1. Check for memory leaks\n2. Use lazy loading\n3. Implement pagination\n4. Optimize data structures'],
            ['Database timeouts', 'Long-running queries\nLocking issues', '1. Optimize slow queries\n2. Add proper indexes\n3. Use connection pooling\n4. Analyze query plans'],
            ['High CPU usage', 'Inefficient algorithms\nToo many requests', '1. Profile code performance\n2. Optimize algorithms\n3. Implement rate limiting\n4. Use caching'],
        ]
        
        perf_table = Table(perf_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fefdf4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        self.story.append(perf_table)
        self.story.append(Spacer(1, 12))

    def add_emergency_procedures(self):
        """Add emergency procedures section"""
        self.story.append(Paragraph("12. Emergency Procedures", self.heading_style))
        
        emergency_text = """
        In case of critical system failures, follow these emergency procedures:
        """
        self.story.append(Paragraph(emergency_text, self.body_style))
        
        # Emergency procedures
        self.story.append(Paragraph("12.1 System Down", self.subheading_style))
        emergency_steps = """
        1. Check server status and logs
        2. Verify database connectivity
        3. Restart application services
        4. Check system resources (CPU, memory, disk)
        5. Review recent changes or deployments
        6. Contact system administrator if issue persists
        """
        self.story.append(Paragraph(emergency_steps, self.code_style))
        
        self.story.append(Paragraph("12.2 Data Corruption", self.subheading_style))
        data_steps = """
        1. STOP all write operations immediately
        2. Backup current state
        3. Identify scope of corruption
        4. Restore from latest known good backup
        5. Verify data integrity
        6. Document incident for analysis
        """
        self.story.append(Paragraph(data_steps, self.code_style))
        
        self.story.append(Paragraph("12.3 Security Breach", self.subheading_style))
        security_steps = """
        1. Isolate affected systems
        2. Change all admin passwords
        3. Review access logs
        4. Check for unauthorized changes
        5. Update security patches
        6. Notify relevant stakeholders
        7. Document and report incident
        """
        self.story.append(Paragraph(security_steps, self.code_style))

    def add_error_codes_appendix(self):
        """Add error codes appendix"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("13. Appendix: Common Error Codes", self.heading_style))
        
        error_codes = [
            ['Error Code', 'Description', 'Action Required'],
            ['ERR_DB_001', 'Database connection failed', 'Check database server and connection string'],
            ['ERR_AUTH_002', 'Authentication failure', 'Verify user credentials and account status'],
            ['ERR_PERM_003', 'Permission denied', 'Check user role and permissions'],
            ['ERR_VAL_004', 'Form validation error', 'Review form input data and constraints'],
            ['ERR_FILE_005', 'File upload failed', 'Check file size, type, and storage permissions'],
            ['ERR_EMAIL_006', 'Email sending failed', 'Verify SMTP configuration and connectivity'],
            ['ERR_WO_007', 'Work order creation failed', 'Check required fields and business rules'],
            ['ERR_PROD_008', 'Product operation failed', 'Verify product data and relationships'],
            ['ERR_SYS_009', 'System configuration error', 'Review system settings and configuration'],
            ['ERR_NET_010', 'Network connectivity issue', 'Check network connection and firewall settings']
        ]
        
        error_table = Table(error_codes, colWidths=[1.5*inch, 3*inch, 2.5*inch])
        error_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fdeeee')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        self.story.append(error_table)

    def add_contact_information(self):
        """Add contact information section"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("14. Contact Information", self.heading_style))
        
        contact_text = """
        For additional technical support or to report issues not covered in this guide, 
        please contact the appropriate support team:
        """
        self.story.append(Paragraph(contact_text, self.body_style))
        
        contact_info = [
            ['Support Level', 'Contact Method', 'Response Time'],
            ['Level 1 - General Support', 'help@cubeproapp.com\nPhone: +1-800-CUBE-PRO', '24 hours'],
            ['Level 2 - Technical Issues', 'tech-support@cubeproapp.com\nPhone: +1-800-CUBE-TEC', '8 hours'],
            ['Level 3 - Critical Issues', 'emergency@cubeproapp.com\nPhone: +1-800-CUBE-911', '2 hours'],
            ['Development Team', 'dev-team@cubeproapp.com', '48 hours'],
            ['Security Issues', 'security@cubeproapp.com\nPGP Key Available', 'Immediate']
        ]
        
        contact_table = Table(contact_info, colWidths=[2*inch, 3*inch, 2*inch])
        contact_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        self.story.append(contact_table)
        
        # Footer note
        footer_text = """
        <br/><br/>
        <b>Note:</b> Keep this troubleshooting guide accessible to all technical staff. 
        Regular updates will be provided as new issues are identified and resolved.
        <br/><br/>
        <i>Document Version: 1.0 | Last Updated: {}</i>
        """.format(datetime.now().strftime('%B %d, %Y'))
        
        self.story.append(Paragraph(footer_text, 
                         ParagraphStyle('Footer', parent=self.body_style, 
                                      fontSize=9, textColor=colors.HexColor('#7f8c8d'))))

    def generate_pdf(self):
        """Generate the complete PDF document"""
        print("🔧 Generating CUBE - PRO Troubleshooting Guide...")
        
        # Build the document
        self.add_title_page()
        self.add_table_of_contents()
        self.add_system_overview()
        self.add_authentication_issues()
        self.add_database_issues()
        self.add_workorder_issues()
        self.add_product_issues()
        self.add_email_issues()
        self.add_performance_issues()
        self.add_emergency_procedures()
        self.add_error_codes_appendix()
        self.add_contact_information()
        
        # Build PDF
        self.doc.build(self.story)
        
        return self.filename

def main():
    """Main function to generate the troubleshooting guide"""
    try:
        generator = TroubleshootingGuideGenerator()
        filename = generator.generate_pdf()
        
        print(f"✅ Troubleshooting guide generated successfully!")
        print(f"📄 File: {filename}")
        print(f"📍 Location: {os.path.abspath(filename)}")
        print(f"📊 Size: {os.path.getsize(filename)} bytes")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Install with: pip install reportlab")
        return False
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return False

if __name__ == "__main__":
    main()
