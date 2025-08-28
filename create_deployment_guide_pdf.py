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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#34495E')
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.HexColor('#2980B9'),
            borderWidth=1,
            borderColor=colors.HexColor('#2980B9'),
            borderPadding=(5, 5, 5, 5),
            backColor=colors.HexColor('#EBF3FD')
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
            borderWidth=1,
            borderColor=colors.HexColor('#DEE2E6'),
            borderPadding=(8, 8, 8, 8),
            spaceAfter=12
        )
        
        # Important note style
        self.note_style = ParagraphStyle(
            'ImportantNote',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#856404'),
            backColor=colors.HexColor('#FFF3CD'),
            borderWidth=1,
            borderColor=colors.HexColor('#FFEAA7'),
            borderPadding=(10, 10, 10, 10),
            spaceAfter=12
        )
        
        # Warning style
        self.warning_style = ParagraphStyle(
            'Warning',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#721C24'),
            backColor=colors.HexColor('#F8D7DA'),
            borderWidth=1,
            borderColor=colors.HexColor('#F5C6CB'),
            borderPadding=(10, 10, 10, 10),
            spaceAfter=12
        )

    def create_cover_page(self):
        """Create the cover page"""
        # Title
        self.story.append(Spacer(1, 2*inch))
        self.story.append(Paragraph("CUBE PRO", self.title_style))
        self.story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        self.story.append(Paragraph("On-Premise Deployment & Release Management Guide", self.subtitle_style))
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
        self.story.append(Spacer(1, 1*inch))
        
        # Company info
        company_info = """
        <b>CUBE PRO - Enterprise Work Order Management System</b><br/>
        Professional On-Premise Deployment Solutions
        """
        company_style = ParagraphStyle(
            'CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50')
        )
        self.story.append(Paragraph(company_info, company_style))
        
        self.story.append(PageBreak())

    def create_table_of_contents(self):
        """Create table of contents"""
        self.story.append(Paragraph("Table of Contents", self.section_style))
        self.story.append(Spacer(1, 20))
        
        toc_data = [
            ['Section', 'Page'],
            ['1. On-Premise Server Implementation', '3'],
            ['2. Environment Setup', '5'],
            ['3. Database Management', '8'],
            ['4. Development and Production Release Strategy', '12'],
            ['5. Data Protection and Backup Strategy', '16'],
            ['6. Zero-Downtime Deployment', '20'],
            ['7. Monitoring and Maintenance', '24'],
            ['8. Security Best Practices', '27'],
            ['9. Troubleshooting', '30'],
            ['10. Deployment Checklist', '33'],
            ['11. Support and Maintenance', '35']
        ]
        
        toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980B9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6'))
        ]))
        
        self.story.append(toc_table)
        self.story.append(PageBreak())

    def add_section(self, title, content):
        """Add a section with title and content"""
        self.story.append(Paragraph(title, self.section_style))
        self.story.append(Spacer(1, 12))
        
        # Process content
        lines = content.strip().split('\n')
        current_paragraph = []
        in_code_block = False
        code_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines at start
            if not line and not current_paragraph and not in_code_block:
                continue
                
            # Handle code blocks
            if line.startswith('```'):
                if in_code_block:
                    # End code block
                    if code_lines:
                        code_text = '\n'.join(code_lines)
                        self.story.append(Paragraph(f"<pre>{code_text}</pre>", self.code_style))
                        code_lines = []
                    in_code_block = False
                else:
                    # Start code block
                    if current_paragraph:
                        para_text = ' '.join(current_paragraph)
                        self.story.append(Paragraph(para_text, self.styles['Normal']))
                        current_paragraph = []
                    in_code_block = True
                continue
            
            if in_code_block:
                code_lines.append(line)
                continue
            
            # Handle headers
            if line.startswith('#### '):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    self.story.append(Paragraph(para_text, self.styles['Normal']))
                    current_paragraph = []
                header_text = line[5:]
                self.story.append(Paragraph(header_text, self.subsection_style))
                continue
            
            # Handle special formatting
            if line.startswith('**') and line.endswith('**'):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    self.story.append(Paragraph(para_text, self.styles['Normal']))
                    current_paragraph = []
                important_text = line[2:-2]
                self.story.append(Paragraph(f"<b>{important_text}</b>", self.note_style))
                continue
            
            # Regular content
            if line:
                # Convert markdown formatting
                line = line.replace('**', '<b>').replace('**', '</b>')
                line = line.replace('`', '<font name="Courier">')
                line = line.replace('`', '</font>')
                current_paragraph.append(line)
            else:
                # Empty line - end current paragraph
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    self.story.append(Paragraph(para_text, self.styles['Normal']))
                    self.story.append(Spacer(1, 6))
                    current_paragraph = []
        
        # Add remaining paragraph
        if current_paragraph:
            para_text = ' '.join(current_paragraph)
            self.story.append(Paragraph(para_text, self.styles['Normal']))

    def add_implementation_overview(self):
        """Add implementation overview section"""
        overview_content = """
        This comprehensive guide provides step-by-step instructions for implementing the CUBE PRO 
        work order management system on an on-premise server infrastructure. The guide covers:

        • Complete server setup and configuration
        • Multi-environment deployment (Development, Staging, Production)
        • Zero-downtime deployment strategies
        • Data protection and backup procedures
        • Security best practices
        • Monitoring and maintenance protocols

        #### Key Benefits

        **Enterprise-Grade Reliability**: Designed for mission-critical business operations
        **Scalable Architecture**: Supports growth from small teams to enterprise organizations
        **Security-First Approach**: Comprehensive security measures and best practices
        **Zero Data Loss**: Robust backup and recovery procedures
        **Minimal Downtime**: Blue-green deployment ensures business continuity
        """
        self.add_section("1. Implementation Overview", overview_content)

    def add_system_requirements(self):
        """Add system requirements section"""
        requirements_content = """
        #### Minimum Hardware Requirements

        • CPU: 4 cores (Intel Xeon or AMD EPYC recommended)
        • RAM: 8GB minimum, 16GB recommended
        • Storage: 500GB SSD (for OS, application, and database)
        • Network: Gigabit Ethernet connection
        • Backup Storage: Additional 1TB for backups

        #### Recommended Production Hardware

        • CPU: 8+ cores
        • RAM: 32GB or higher
        • Storage: 1TB+ NVMe SSD
        • Network: Redundant Gigabit connections
        • Backup: Network-attached storage (NAS) or dedicated backup server

        #### Software Requirements

        • Operating System: Ubuntu Server 22.04 LTS (Recommended) or CentOS/RHEL 8/9
        • Database: PostgreSQL 14+
        • Web Server: Nginx
        • Application Server: Gunicorn
        • Cache: Redis
        • Version Control: Git
        """
        self.add_section("2. System Requirements", requirements_content)

    def add_installation_steps(self):
        """Add installation steps section"""
        installation_content = """
        #### Step 1: Operating System Setup

        Update the system and install essential packages:

        ```bash
        sudo apt update && sudo apt upgrade -y
        sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server git curl wget htop
        ```

        #### Step 2: Create Application User

        ```bash
        sudo useradd -m -s /bin/bash cubeapp
        sudo usermod -aG sudo cubeapp
        sudo su - cubeapp
        ```

        #### Step 3: Directory Structure

        ```bash
        mkdir -p /home/cubeapp/{cube-prod,cube-dev,cube-staging,backups,logs,scripts}
        ```

        #### Step 4: Database Configuration

        ```bash
        sudo -u postgres psql << EOF
        CREATE DATABASE cube_prod;
        CREATE DATABASE cube_dev;
        CREATE DATABASE cube_staging;
        CREATE USER cubeapp WITH PASSWORD 'your_secure_password';
        GRANT ALL PRIVILEGES ON DATABASE cube_prod TO cubeapp;
        GRANT ALL PRIVILEGES ON DATABASE cube_dev TO cubeapp;
        GRANT ALL PRIVILEGES ON DATABASE cube_staging TO cubeapp;
        \q
        EOF
        ```
        """
        self.add_section("3. Installation Steps", installation_content)

    def add_deployment_strategy(self):
        """Add deployment strategy section"""
        deployment_content = """
        #### Blue-Green Deployment

        The recommended deployment strategy uses blue-green deployment to ensure zero downtime:

        **Blue Environment**: Current production environment serving live traffic
        **Green Environment**: New version being prepared and tested
        **Switch**: Traffic is routed from blue to green after successful testing

        #### Environment Structure

        • **Development**: Feature development and initial testing
        • **Staging**: Pre-production testing with production-like data
        • **Production**: Live environment serving end users

        #### Release Process

        1. Develop features in development environment
        2. Test in staging environment with production data copy
        3. Deploy to green production environment
        4. Perform health checks and validation
        5. Switch traffic from blue to green
        6. Monitor and verify successful deployment
        7. Decommission old blue environment

        #### Rollback Strategy

        In case of issues, traffic can be immediately switched back to the blue environment,
        providing instant rollback capability with zero data loss.
        """
        self.add_section("4. Deployment Strategy", deployment_content)

    def add_backup_strategy(self):
        """Add backup strategy section"""
        backup_content = """
        #### Automated Backup System

        **Daily Backups**: Database backups at 2 AM daily
        **Weekly Backups**: Full application backups every Sunday at 3 AM
        **Retention Policy**: 30 days for daily, 12 weeks for weekly backups

        #### Backup Components

        • Database dumps (PostgreSQL)
        • Application code and configuration
        • User uploads and static files
        • System logs and monitoring data

        #### Disaster Recovery

        **Recovery Time Objective (RTO)**: 4 hours maximum
        **Recovery Point Objective (RPO)**: 24 hours maximum
        **Backup Testing**: Monthly verification of backup integrity

        #### Backup Verification

        Regular automated testing ensures backup files are valid and can be restored successfully.
        Test restores are performed monthly in isolated environments.
        """
        self.add_section("5. Backup Strategy", backup_content)

    def add_security_measures(self):
        """Add security measures section"""
        security_content = """
        #### Server Security

        • Firewall configuration (UFW/iptables)
        • SSL/TLS encryption with Let's Encrypt
        • SSH key-based authentication
        • Regular security updates
        • Intrusion detection system

        #### Application Security

        • Environment variable encryption
        • Database connection security
        • Session management
        • Input validation and sanitization
        • CSRF protection

        #### Access Control

        • Role-based access control (RBAC)
        • Strong password policies
        • Multi-factor authentication (MFA)
        • Audit logging
        • Regular access reviews

        #### Data Protection

        • Database encryption at rest
        • Encrypted backup storage
        • Secure data transmission
        • GDPR compliance measures
        • Data retention policies
        """
        self.add_section("6. Security Measures", security_content)

    def add_monitoring_maintenance(self):
        """Add monitoring and maintenance section"""
        monitoring_content = """
        #### System Monitoring

        • CPU, memory, and disk usage monitoring
        • Application performance monitoring (APM)
        • Database performance monitoring
        • Network connectivity monitoring
        • Log aggregation and analysis

        #### Health Checks

        • Application endpoint monitoring
        • Database connectivity checks
        • Service availability monitoring
        • Response time monitoring
        • Error rate tracking

        #### Maintenance Schedule

        **Daily**: Automated backups, log rotation, health checks
        **Weekly**: System updates, performance review, capacity planning
        **Monthly**: Security updates, disaster recovery testing, backup verification
        **Quarterly**: Full system audit, performance optimization, documentation updates

        #### Alerting

        • Email notifications for critical issues
        • SMS alerts for urgent problems
        • Integration with monitoring platforms
        • Escalation procedures
        • On-call rotation management
        """
        self.add_section("7. Monitoring and Maintenance", monitoring_content)

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
            bottomMargin=18
        )
        
        # Build content
        self.create_cover_page()
        self.create_table_of_contents()
        self.add_implementation_overview()
        self.add_system_requirements()
        self.add_installation_steps()
        self.add_deployment_strategy()
        self.add_backup_strategy()
        self.add_security_measures()
        self.add_monitoring_maintenance()
        
        # Add footer with page numbers
        def add_page_number(canvas, doc):
            """Add page number to each page"""
            page_num = canvas.getPageNumber()
            text = f"Page {page_num}"
            canvas.drawRightString(A4[0] - 72, 30, text)
            
            # Add header
            canvas.drawString(72, A4[1] - 50, "CUBE PRO - On-Premise Deployment Guide")
            canvas.line(72, A4[1] - 55, A4[0] - 72, A4[1] - 55)
        
        # Build PDF
        self.doc.build(self.story, onFirstPage=add_page_number, onLaterPages=add_page_number)
        print(f"PDF generated successfully: {filename}")
        return filename

def main():
    """Main function to generate the PDF"""
    try:
        generator = CubePDFGenerator()
        pdf_file = generator.generate_pdf()
        
        print(f"\n✅ PDF Generated Successfully!")
        print(f"📄 File: {pdf_file}")
        print(f"📍 Location: {os.path.abspath(pdf_file)}")
        print(f"📊 Size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
        
        return pdf_file
    
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Install required packages with: pip install reportlab")
        return None
    
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return None

if __name__ == "__main__":
    main()
