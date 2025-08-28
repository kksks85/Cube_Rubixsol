#!/usr/bin/env python3
"""
CUBE On-Premise Deployment Guide PDF Generator (Final Version)
Creates a professional PDF with properly formatted content
"""

import os
import re
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def clean_text(text):
    """Clean text to avoid parsing issues"""
    # Remove problematic characters and fix markdown
    text = text.replace('`', "'")
    text = text.replace('**', '')
    text = text.replace('*', '')
    text = re.sub(r'[^\w\s\-\.\,\:\;\(\)\/\\\@\#\$\%\&\+\=\|\[\]\{\}\<\>\!]', ' ', text)
    return text.strip()

class FinalPDFGenerator:
    def __init__(self):
        self.doc = None
        self.story = []
        self.styles = getSampleStyleSheet()
        self.setup_styles()
        
    def setup_styles(self):
        """Setup custom styles"""
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Title'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1B4F72'),
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        
        self.section_style = ParagraphStyle(
            'Section',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=25,
            textColor=colors.HexColor('#2980B9'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#2980B9'),
            borderPadding=8,
            backColor=colors.HexColor('#EBF3FD')
        )
        
        self.subsection_style = ParagraphStyle(
            'Subsection',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.HexColor('#27AE60'),
            fontName='Helvetica-Bold'
        )
        
        self.bullet_style = ParagraphStyle(
            'Bullet',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=4,
            leftIndent=20,
            bulletIndent=10
        )
        
        self.code_style = ParagraphStyle(
            'Code',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Courier',
            textColor=colors.HexColor('#2C3E50'),
            backColor=colors.HexColor('#F8F9FA'),
            borderWidth=1,
            borderColor=colors.HexColor('#DEE2E6'),
            borderPadding=8,
            spaceAfter=12,
            leftIndent=15,
            rightIndent=15
        )

    def create_cover_page(self):
        """Create an attractive cover page"""
        self.story.append(Spacer(1, 1.5*inch))
        
        # Main title
        self.story.append(Paragraph("CUBE PRO", self.title_style))
        self.story.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        self.story.append(Paragraph("On-Premise Deployment Guide", self.subtitle_style))
        self.story.append(Spacer(1, 0.5*inch))
        
        # Version box
        version_text = f"""
        Version 2.0 - Comprehensive Implementation Guide<br/>
        Generated: {datetime.now().strftime('%B %d, %Y')}<br/>
        Target: System Administrators and DevOps Engineers
        """
        
        version_style = ParagraphStyle(
            'Version',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            borderWidth=2,
            borderColor=colors.HexColor('#3498DB'),
            borderPadding=15,
            backColor=colors.HexColor('#F0F8FF'),
            spaceAfter=30
        )
        self.story.append(Paragraph(version_text, version_style))
        
        # Features highlight
        features_text = """
        Complete Enterprise Deployment Solution featuring:<br/>
        • Zero-downtime blue-green deployment strategy<br/>
        • Comprehensive backup and disaster recovery procedures<br/>
        • Multi-environment setup (Development, Staging, Production)<br/>
        • Advanced security hardening and monitoring<br/>
        • Automated maintenance and health monitoring<br/>
        • Scalable architecture for enterprise growth
        """
        
        features_style = ParagraphStyle(
            'Features',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_LEFT,
            borderWidth=1,
            borderColor=colors.HexColor('#27AE60'),
            borderPadding=12,
            backColor=colors.HexColor('#F0FFF0'),
            spaceAfter=20
        )
        self.story.append(Paragraph(features_text, features_style))
        
        self.story.append(PageBreak())

    def add_main_content(self):
        """Add the main content sections"""
        
        # Table of Contents
        self.story.append(Paragraph("Table of Contents", self.section_style))
        self.story.append(Spacer(1, 15))
        
        toc_items = [
            "1. System Requirements and Prerequisites",
            "2. Server Setup and OS Configuration", 
            "3. Database Installation and Configuration",
            "4. Application Deployment Process",
            "5. Environment Management (Dev/Staging/Prod)",
            "6. Blue-Green Deployment Strategy",
            "7. Backup and Disaster Recovery",
            "8. Security Implementation",
            "9. Monitoring and Maintenance",
            "10. Troubleshooting and Support",
            "11. Performance Optimization",
            "12. Scaling and Growth Planning"
        ]
        
        for item in toc_items:
            self.story.append(Paragraph(item, self.styles['Normal']))
            self.story.append(Spacer(1, 4))
        
        self.story.append(PageBreak())
        
        # Section 1: System Requirements
        self.story.append(Paragraph("1. System Requirements and Prerequisites", self.section_style))
        
        self.story.append(Paragraph("Hardware Requirements", self.subsection_style))
        hw_requirements = [
            "CPU: Minimum 4 cores, recommended 8+ cores for production workloads",
            "RAM: Minimum 8GB, recommended 16GB for development, 32GB+ for production",
            "Storage: Minimum 500GB SSD, recommended 1TB+ NVMe SSD for optimal performance",
            "Network: Gigabit Ethernet, redundant connections recommended for production",
            "Backup Storage: Additional 1TB minimum for backup retention and disaster recovery"
        ]
        
        for req in hw_requirements:
            self.story.append(Paragraph(f"• {clean_text(req)}", self.bullet_style))
        
        self.story.append(Spacer(1, 15))
        self.story.append(Paragraph("Software Requirements", self.subsection_style))
        sw_requirements = [
            "Operating System: Ubuntu Server 22.04 LTS (primary) or CentOS/RHEL 8/9",
            "Database: PostgreSQL 14 or later with SSL support",
            "Web Server: Nginx with SSL/TLS capabilities",
            "Application Runtime: Python 3.9+ with virtual environment support",
            "Cache Server: Redis 6+ for session management and application caching",
            "Version Control: Git 2.30+ for source code management",
            "Process Manager: Systemd for service management",
            "Backup Tools: PostgreSQL utilities, rsync, and compression tools"
        ]
        
        for req in sw_requirements:
            self.story.append(Paragraph(f"• {clean_text(req)}", self.bullet_style))
        
        # Section 2: Installation Process
        self.story.append(Spacer(1, 25))
        self.story.append(Paragraph("2. Server Setup and Installation Process", self.section_style))
        
        self.story.append(Paragraph("Step 1: Operating System Preparation", self.subsection_style))
        self.story.append(Paragraph("Update the system and install essential packages:", self.styles['Normal']))
        
        os_commands = """# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql \\
postgresql-contrib redis-server git curl wget htop unzip

# Install security tools
sudo apt install -y ufw fail2ban"""
        
        self.story.append(Preformatted(clean_text(os_commands), self.code_style))
        
        self.story.append(Paragraph("Step 2: User Account and Directory Setup", self.subsection_style))
        
        user_commands = """# Create dedicated application user
sudo useradd -m -s /bin/bash cubeapp
sudo usermod -aG sudo cubeapp

# Create directory structure
sudo mkdir -p /home/cubeapp/{cube-prod,cube-dev,cube-staging,backups,logs,scripts}
sudo chown -R cubeapp:cubeapp /home/cubeapp/"""
        
        self.story.append(Preformatted(clean_text(user_commands), self.code_style))
        
        # Section 3: Database Configuration
        self.story.append(Spacer(1, 25))
        self.story.append(Paragraph("3. Database Installation and Configuration", self.section_style))
        
        self.story.append(Paragraph("PostgreSQL Setup", self.subsection_style))
        self.story.append(Paragraph("Configure PostgreSQL for optimal performance and security:", self.styles['Normal']))
        
        db_commands = """# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create databases and user
sudo -u postgres psql <<EOF
CREATE DATABASE cube_prod;
CREATE DATABASE cube_dev; 
CREATE DATABASE cube_staging;
CREATE USER cubeapp WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE cube_prod TO cubeapp;
GRANT ALL PRIVILEGES ON DATABASE cube_dev TO cubeapp;
GRANT ALL PRIVILEGES ON DATABASE cube_staging TO cubeapp;
EOF"""
        
        self.story.append(Preformatted(clean_text(db_commands), self.code_style))
        
        # Section 4: Security Configuration
        self.story.append(Spacer(1, 25))
        self.story.append(Paragraph("4. Security Implementation", self.section_style))
        
        security_measures = [
            "Firewall Configuration: Configure UFW to allow only necessary ports (22, 80, 443)",
            "SSL/TLS Setup: Install Let's Encrypt certificates for secure communications",
            "Database Security: Enable SSL connections and configure authentication",
            "Application Security: Use environment variables for secrets and credentials",
            "System Hardening: Disable unused services and apply security updates",
            "Access Control: Implement role-based permissions and strong passwords",
            "Monitoring: Set up intrusion detection and log monitoring systems"
        ]
        
        for measure in security_measures:
            self.story.append(Paragraph(f"• {clean_text(measure)}", self.bullet_style))
        
        # Section 5: Deployment Strategy
        self.story.append(Spacer(1, 25))
        self.story.append(Paragraph("5. Blue-Green Deployment Strategy", self.section_style))
        
        self.story.append(Paragraph("Overview", self.subsection_style))
        deployment_overview = """
        The blue-green deployment strategy ensures zero-downtime updates by maintaining two identical 
        production environments. During deployment, traffic is switched from the current environment 
        (blue) to the updated environment (green) after successful testing and validation.
        """
        self.story.append(Paragraph(clean_text(deployment_overview), self.styles['Normal']))
        
        self.story.append(Paragraph("Deployment Process", self.subsection_style))
        deployment_steps = [
            "Prepare green environment with new application version",
            "Run comprehensive tests including database migrations",
            "Perform health checks and validation procedures", 
            "Switch load balancer traffic from blue to green environment",
            "Monitor application performance and error rates",
            "Maintain blue environment for immediate rollback if needed",
            "Decommission blue environment after successful validation period"
        ]
        
        for step in deployment_steps:
            self.story.append(Paragraph(f"• {clean_text(step)}", self.bullet_style))
        
        # Section 6: Backup and Recovery
        self.story.append(Spacer(1, 25))
        self.story.append(Paragraph("6. Backup and Disaster Recovery", self.section_style))
        
        self.story.append(Paragraph("Backup Strategy", self.subsection_style))
        backup_strategy = [
            "Daily automated database backups at 2 AM with 30-day retention",
            "Weekly full application backups every Sunday with 12-week retention",
            "Monthly system snapshots for long-term disaster recovery",
            "Real-time database replication for high-availability configurations",
            "Automated backup verification and integrity testing procedures",
            "Offsite backup storage for geographic disaster protection"
        ]
        
        for strategy in backup_strategy:
            self.story.append(Paragraph(f"• {clean_text(strategy)}", self.bullet_style))
        
        self.story.append(Paragraph("Recovery Objectives", self.subsection_style))
        rto_rpo = """
        Recovery Time Objective (RTO): Maximum 4 hours for full system restoration
        Recovery Point Objective (RPO): Maximum 24 hours of data loss in worst-case scenarios
        High Availability Target: 99.9% uptime for production systems
        """
        self.story.append(Paragraph(clean_text(rto_rpo), self.styles['Normal']))

    def generate_pdf(self, filename="CUBE_OnPremise_Deployment_Guide_Final.pdf"):
        """Generate the final PDF document"""
        print(f"Generating final PDF: {filename}")
        
        # Create document
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=60,
            leftMargin=60,
            topMargin=60,
            bottomMargin=60
        )
        
        # Build content
        self.create_cover_page()
        self.add_main_content()
        
        # Page numbering function
        def add_page_elements(canvas, doc):
            page_num = canvas.getPageNumber()
            if page_num > 1:
                # Header
                canvas.setFont('Helvetica', 9)
                canvas.drawString(60, A4[1] - 40, "CUBE PRO - On-Premise Deployment Guide")
                canvas.line(60, A4[1] - 45, A4[0] - 60, A4[1] - 45)
                
                # Footer
                canvas.drawRightString(A4[0] - 60, 30, f"Page {page_num}")
                canvas.drawString(60, 30, f"Version 2.0 - {datetime.now().strftime('%Y-%m-%d')}")
        
        # Build PDF
        try:
            self.doc.build(self.story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
            
            file_size = os.path.getsize(filename)
            print(f"✅ PDF generated successfully!")
            print(f"📄 File: {filename}")
            print(f"📂 Location: {os.path.abspath(filename)}")
            print(f"📊 Size: {file_size / 1024:.1f} KB")
            
            return filename
            
        except Exception as e:
            print(f"❌ Error: {e}")
            raise

def main():
    """Main execution function"""
    try:
        generator = FinalPDFGenerator()
        pdf_file = generator.generate_pdf()
        
        print(f"\n🎉 Success! Your deployment guide PDF is ready.")
        print(f"📖 This comprehensive guide contains all the information needed")
        print(f"   for enterprise on-premise deployment of CUBE PRO.")
        
        return pdf_file
        
    except Exception as e:
        print(f"❌ Failed to generate PDF: {e}")
        return None

if __name__ == "__main__":
    main()
