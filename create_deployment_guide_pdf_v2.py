#!/usr/bin/env python3
"""
CUBE On-Premise Deployment Guide PDF Generator
Creates a professional PDF document from the deployment guide
"""

import os
import sys
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

class CubePDFGenerator:
    def __init__(self):
        self.doc = None
        self.story = []
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50')
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.HexColor('#2980B9')
        )
        
        # Subsection header style
        self.subsection_style = ParagraphStyle(
            'CustomSubsection',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=15,
            textColor=colors.HexColor('#27AE60')
        )
        
        # Code block style
        self.code_style = ParagraphStyle(
            'CodeBlock',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Courier',
            textColor=colors.HexColor('#2C3E50'),
            backColor=colors.HexColor('#F8F9FA'),
            spaceAfter=12,
            leftIndent=20,
            rightIndent=20
        )
        
        # Bullet style
        self.bullet_style = ParagraphStyle(
            'BulletList',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20,
            bulletIndent=10
        )

    def create_cover_page(self):
        """Create the cover page"""
        # Title
        self.story.append(Spacer(1, 2*inch))
        self.story.append(Paragraph("CUBE PRO", self.title_style))
        self.story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#34495E')
        )
        self.story.append(Paragraph("On-Premise Deployment &amp; Release Management Guide", subtitle_style))
        self.story.append(Spacer(1, 1*inch))
        
        # Version info
        version_info = f"""
        <b>Version:</b> 1.0<br/>
        <b>Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
        <b>Document Type:</b> Implementation Guide<br/>
        <b>Target Audience:</b> System Administrators, DevOps Engineers
        """
        version_style = ParagraphStyle(
            'VersionInfo',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        self.story.append(Paragraph(version_info, version_style))
        self.story.append(PageBreak())

    def create_table_of_contents(self):
        """Create table of contents"""
        self.story.append(Paragraph("Table of Contents", self.section_style))
        self.story.append(Spacer(1, 20))
        
        toc_items = [
            "1. Implementation Overview",
            "2. System Requirements", 
            "3. Installation Steps",
            "4. Environment Setup",
            "5. Database Configuration",
            "6. Deployment Strategy",
            "7. Backup and Recovery",
            "8. Security Implementation",
            "9. Monitoring Setup",
            "10. Troubleshooting Guide",
            "11. Maintenance Procedures",
            "12. Best Practices"
        ]
        
        for item in toc_items:
            self.story.append(Paragraph(item, self.styles['Normal']))
            self.story.append(Spacer(1, 6))
        
        self.story.append(PageBreak())

    def add_content_section(self, title, paragraphs):
        """Add a content section with multiple paragraphs"""
        self.story.append(Paragraph(title, self.section_style))
        self.story.append(Spacer(1, 12))
        
        for para in paragraphs:
            if para.startswith('####'):
                # Subsection
                self.story.append(Paragraph(para[4:].strip(), self.subsection_style))
            elif para.startswith('```'):
                # Skip code block markers
                continue
            elif para.startswith('•') or para.startswith('-'):
                # Bullet point
                bullet_text = para[1:].strip()
                self.story.append(Paragraph(f"• {bullet_text}", self.bullet_style))
            elif para.strip() and not para.startswith('#'):
                # Regular paragraph
                self.story.append(Paragraph(para, self.styles['Normal']))
                self.story.append(Spacer(1, 6))

    def generate_content(self):
        """Generate all content sections"""
        
        # 1. Implementation Overview
        overview = [
            "This comprehensive guide provides step-by-step instructions for implementing the CUBE PRO work order management system on an on-premise server infrastructure.",
            "",
            "#### Key Benefits",
            "• Enterprise-grade reliability for mission-critical operations",
            "• Scalable architecture supporting growth from small teams to enterprises", 
            "• Security-first approach with comprehensive protection measures",
            "• Zero data loss through robust backup and recovery procedures",
            "• Minimal downtime using blue-green deployment strategies",
            "",
            "#### Scope of Implementation",
            "• Complete server setup and configuration procedures",
            "• Multi-environment deployment (Development, Staging, Production)",
            "• Automated backup and recovery systems",
            "• Security hardening and best practices",
            "• Monitoring and maintenance protocols"
        ]
        self.add_content_section("1. Implementation Overview", overview)
        
        # 2. System Requirements
        requirements = [
            "#### Minimum Hardware Requirements",
            "• CPU: 4 cores (Intel Xeon or AMD EPYC recommended)",
            "• RAM: 8GB minimum, 16GB recommended for production",
            "• Storage: 500GB SSD for OS, application, and database",
            "• Network: Gigabit Ethernet connection",
            "• Backup Storage: Additional 1TB for backup retention",
            "",
            "#### Recommended Production Hardware",
            "• CPU: 8+ cores for optimal performance",
            "• RAM: 32GB or higher for heavy workloads",
            "• Storage: 1TB+ NVMe SSD for fast I/O operations",
            "• Network: Redundant Gigabit connections for high availability",
            "• Backup: Network-attached storage (NAS) or dedicated backup server",
            "",
            "#### Software Requirements", 
            "• Operating System: Ubuntu Server 22.04 LTS (Primary) or CentOS/RHEL 8/9",
            "• Database: PostgreSQL 14+ for data persistence",
            "• Web Server: Nginx for reverse proxy and static file serving",
            "• Application Server: Gunicorn for Python WSGI applications",
            "• Cache: Redis for session management and caching",
            "• Version Control: Git for source code management"
        ]
        self.add_content_section("2. System Requirements", requirements)
        
        # 3. Installation Steps
        installation = [
            "#### Step 1: Operating System Preparation",
            "Update the system and install essential packages for the CUBE environment.",
            "",
            "#### Step 2: User Account Setup", 
            "Create a dedicated application user with appropriate permissions for security isolation.",
            "",
            "#### Step 3: Directory Structure Creation",
            "Establish organized directory structure for different environments and operational needs.",
            "",
            "#### Step 4: Database Server Installation",
            "Install and configure PostgreSQL database server with security hardening.",
            "",
            "#### Step 5: Web Server Configuration",
            "Set up Nginx as reverse proxy with SSL/TLS termination and static file serving.",
            "",
            "#### Step 6: Application Dependencies",
            "Install Python runtime, virtual environments, and required application dependencies."
        ]
        self.add_content_section("3. Installation Steps", installation)
        
        # 4. Environment Setup
        environment = [
            "#### Development Environment",
            "Isolated environment for feature development and initial testing with relaxed security for debugging.",
            "",
            "#### Staging Environment", 
            "Production-like environment for integration testing with production data copies and realistic load testing.",
            "",
            "#### Production Environment",
            "Live environment serving end users with maximum security, monitoring, and performance optimization.",
            "",
            "#### Environment Isolation",
            "• Separate databases for each environment",
            "• Independent configuration files and secrets",
            "• Isolated network access and firewall rules",
            "• Environment-specific logging and monitoring",
            "• Separate backup and recovery procedures"
        ]
        self.add_content_section("4. Environment Setup", environment)
        
        # 5. Database Configuration
        database = [
            "#### PostgreSQL Installation and Setup",
            "Install PostgreSQL database server with optimized configuration for CUBE workloads.",
            "",
            "#### Database Security Configuration",
            "• Encrypted connections using SSL/TLS",
            "• Role-based access control with principle of least privilege", 
            "• Regular security updates and vulnerability patching",
            "• Audit logging for compliance and security monitoring",
            "• Backup encryption for data protection at rest",
            "",
            "#### Performance Optimization",
            "• Memory allocation tuning for optimal query performance",
            "• Index optimization for frequently accessed data",
            "• Connection pooling to manage database connections efficiently",
            "• Query performance monitoring and optimization",
            "• Regular database maintenance and statistics updates"
        ]
        self.add_content_section("5. Database Configuration", database)
        
        # 6. Deployment Strategy
        deployment = [
            "#### Blue-Green Deployment Model",
            "Zero-downtime deployment strategy ensuring business continuity during updates.",
            "",
            "#### Deployment Process",
            "• Blue Environment: Current production serving live traffic",
            "• Green Environment: New version preparation and testing", 
            "• Health Validation: Comprehensive testing before traffic switch",
            "• Traffic Switch: Instantaneous routing from blue to green",
            "• Monitoring: Real-time validation of successful deployment",
            "• Rollback: Immediate reversion capability if issues detected",
            "",
            "#### Release Management",
            "• Feature development in dedicated branches",
            "• Integration testing in staging environment",
            "• Automated testing and quality assurance",
            "• Staged rollout with monitoring and validation",
            "• Documentation and change management"
        ]
        self.add_content_section("6. Deployment Strategy", deployment)
        
        # 7. Backup and Recovery
        backup = [
            "#### Automated Backup System",
            "Comprehensive backup strategy ensuring data protection and business continuity.",
            "",
            "#### Backup Schedule",
            "• Daily: Database backups at 2 AM with 30-day retention",
            "• Weekly: Full application backups every Sunday with 12-week retention",
            "• Monthly: Complete system snapshots with long-term archival",
            "",
            "#### Recovery Procedures", 
            "• Recovery Time Objective (RTO): 4 hours maximum downtime",
            "• Recovery Point Objective (RPO): 24 hours maximum data loss",
            "• Automated backup verification and integrity testing",
            "• Documented recovery procedures with regular testing",
            "• Disaster recovery site preparation and maintenance"
        ]
        self.add_content_section("7. Backup and Recovery", backup)
        
        # 8. Security Implementation
        security = [
            "#### Server Security Hardening",
            "• Firewall configuration with minimal open ports",
            "• SSL/TLS encryption for all communications",
            "• SSH key-based authentication with disabled password login",
            "• Regular security updates and vulnerability management",
            "• Intrusion detection and prevention systems",
            "",
            "#### Application Security",
            "• Environment variable encryption for sensitive data",
            "• Database connection security with encrypted credentials",
            "• Session management with secure token handling",
            "• Input validation and sanitization against injection attacks",
            "• Cross-Site Request Forgery (CSRF) protection",
            "",
            "#### Access Control",
            "• Role-based access control (RBAC) implementation",
            "• Strong password policies and complexity requirements",
            "• Multi-factor authentication (MFA) for administrative access",
            "• Comprehensive audit logging and monitoring",
            "• Regular access reviews and permission audits"
        ]
        self.add_content_section("8. Security Implementation", security)

    def generate_pdf(self, filename="CUBE_OnPremise_Deployment_Guide.pdf"):
        """Generate the complete PDF document"""
        print(f"Generating PDF: {filename}")
        
        # Create document
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=50
        )
        
        # Build content
        self.create_cover_page()
        self.create_table_of_contents()
        self.generate_content()
        
        # Add footer with page numbers
        def add_page_number(canvas, doc):
            """Add page number and header to each page"""
            page_num = canvas.getPageNumber()
            if page_num > 1:  # Skip cover page
                # Page number
                canvas.drawRightString(A4[0] - 72, 30, f"Page {page_num}")
                # Header
                canvas.drawString(72, A4[1] - 50, "CUBE PRO - On-Premise Deployment Guide")
                canvas.line(72, A4[1] - 55, A4[0] - 72, A4[1] - 55)
        
        # Build PDF
        try:
            self.doc.build(self.story, onFirstPage=add_page_number, onLaterPages=add_page_number)
            print(f"✅ PDF generated successfully: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error building PDF: {e}")
            raise

def main():
    """Main function to generate the PDF"""
    try:
        generator = CubePDFGenerator()
        pdf_file = generator.generate_pdf()
        
        print(f"\n🎉 PDF Generation Complete!")
        print(f"📄 File: {pdf_file}")
        print(f"📍 Location: {os.path.abspath(pdf_file)}")
        print(f"📊 Size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
        
        return pdf_file
    
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Install with: pip install reportlab")
        return None
    
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
