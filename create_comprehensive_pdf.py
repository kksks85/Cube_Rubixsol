#!/usr/bin/env python3
"""
CUBE On-Premise Deployment Guide - Comprehensive PDF Generator
Creates a detailed PDF document with all implementation details
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def read_markdown_file(filename):
    """Read the markdown file and return content"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: {filename} not found. Creating PDF with basic content.")
        return None

class ComprehensivePDFGenerator:
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
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1B4F72')
        )
        
        self.heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=20,
            textColor=colors.HexColor('#2980B9'),
            borderWidth=2,
            borderColor=colors.HexColor('#2980B9'),
            borderPadding=10,
            backColor=colors.HexColor('#EBF3FD')
        )
        
        self.heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=15,
            textColor=colors.HexColor('#27AE60')
        )
        
        self.code_style = ParagraphStyle(
            'Code',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Courier',
            textColor=colors.HexColor('#2C3E50'),
            backColor=colors.HexColor('#F8F9FA'),
            borderWidth=1,
            borderColor=colors.HexColor('#DEE2E6'),
            borderPadding=8,
            spaceAfter=12,
            leftIndent=10,
            rightIndent=10
        )
        
        self.bullet_style = ParagraphStyle(
            'Bullet',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20
        )

    def create_title_page(self):
        """Create title page"""
        self.story.append(Spacer(1, 2*inch))
        
        # Main title
        self.story.append(Paragraph("CUBE PRO", self.title_style))
        self.story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=30
        )
        self.story.append(Paragraph("On-Premise Deployment &amp; Release Management Guide", subtitle_style))
        
        # Document info
        info_text = f"""
        <b>Version:</b> 2.0 (Comprehensive Edition)<br/>
        <b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        <b>Document Type:</b> Technical Implementation Guide<br/>
        <b>Target Audience:</b> System Administrators, DevOps Engineers, IT Managers<br/>
        <b>Classification:</b> Internal Use - Technical Documentation
        """
        
        info_style = ParagraphStyle(
            'DocInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=40
        )
        self.story.append(Paragraph(info_text, info_style))
        
        # Executive summary box
        summary_text = """
        <b>Executive Summary:</b><br/>
        This comprehensive guide provides complete instructions for deploying the CUBE PRO 
        work order management system on on-premise infrastructure. The guide covers enterprise-grade 
        deployment strategies, security best practices, backup procedures, and maintenance protocols 
        to ensure reliable, scalable, and secure operations in production environments.
        """
        
        summary_style = ParagraphStyle(
            'Summary',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            borderWidth=1,
            borderColor=colors.HexColor('#3498DB'),
            borderPadding=15,
            backColor=colors.HexColor('#F0F8FF'),
            spaceAfter=20
        )
        self.story.append(Paragraph(summary_text, summary_style))
        
        self.story.append(PageBreak())

    def process_markdown_content(self, content):
        """Process markdown content and convert to PDF elements"""
        if not content:
            self.add_basic_content()
            return
            
        lines = content.split('\n')
        current_section = []
        in_code_block = False
        code_lines = []
        
        for line in lines:
            line = line.rstrip()
            
            # Handle code blocks
            if line.startswith('```'):
                if in_code_block:
                    # End code block
                    if code_lines:
                        code_text = '\n'.join(code_lines)
                        self.story.append(Preformatted(code_text, self.code_style))
                    code_lines = []
                    in_code_block = False
                else:
                    # Start code block
                    in_code_block = True
                continue
                
            if in_code_block:
                code_lines.append(line)
                continue
            
            # Handle headers
            if line.startswith('# ') and not line.startswith('## '):
                title = line[2:].strip()
                if not title.startswith('CUBE') and not title.startswith('Table'):
                    self.story.append(Paragraph(title, self.heading1_style))
                    self.story.append(Spacer(1, 12))
            elif line.startswith('## '):
                title = line[3:].strip()
                self.story.append(Paragraph(title, self.heading1_style))
                self.story.append(Spacer(1, 12))
            elif line.startswith('### '):
                title = line[4:].strip()
                self.story.append(Paragraph(title, self.heading2_style))
                self.story.append(Spacer(1, 8))
            elif line.startswith('#### '):
                title = line[5:].strip()
                subsection_style = ParagraphStyle(
                    'Subsection',
                    parent=self.styles['Normal'],
                    fontSize=12,
                    fontName='Helvetica-Bold',
                    spaceAfter=8,
                    spaceBefore=8,
                    textColor=colors.HexColor('#8B4513')
                )
                self.story.append(Paragraph(title, subsection_style))
            elif line.startswith('- ') or line.startswith('* '):
                bullet_text = line[2:].strip()
                # Clean up markdown formatting
                bullet_text = bullet_text.replace('**', '<b>').replace('**', '</b>')
                bullet_text = bullet_text.replace('`', '<font name="Courier">').replace('`', '</font>')
                self.story.append(Paragraph(f"• {bullet_text}", self.bullet_style))
            elif line.strip() and not line.startswith('---'):
                # Regular paragraph
                para_text = line.strip()
                # Clean up markdown formatting
                para_text = para_text.replace('**', '<b>').replace('**', '</b>')
                para_text = para_text.replace('`', '<font name="Courier">').replace('`', '</font>')
                
                if para_text:
                    self.story.append(Paragraph(para_text, self.styles['Normal']))
                    self.story.append(Spacer(1, 6))

    def add_basic_content(self):
        """Add basic content if markdown file is not available"""
        sections = [
            ("1. System Requirements", [
                "The CUBE PRO system requires specific hardware and software configurations for optimal performance.",
                "• CPU: 4+ cores (8+ recommended for production)",
                "• RAM: 8GB minimum (16GB+ recommended)",
                "• Storage: 500GB SSD minimum (1TB+ recommended)",
                "• OS: Ubuntu 22.04 LTS or CentOS 8/9",
                "• Database: PostgreSQL 14+",
                "• Web Server: Nginx",
                "• Python: 3.9+"
            ]),
            ("2. Installation Process", [
                "The installation process involves several key steps to ensure proper deployment.",
                "• System preparation and package installation",
                "• User account and directory structure setup",
                "• Database server installation and configuration",
                "• Application deployment and configuration",
                "• Web server setup and SSL configuration",
                "• Security hardening and firewall configuration"
            ]),
            ("3. Environment Configuration", [
                "Multiple environments ensure proper testing and deployment procedures.",
                "• Development: Feature development and initial testing",
                "• Staging: Production-like testing environment",
                "• Production: Live environment serving end users",
                "• Each environment has isolated databases and configurations",
                "• Environment-specific security and monitoring settings"
            ]),
            ("4. Backup and Recovery", [
                "Comprehensive backup strategy ensures data protection and business continuity.",
                "• Daily automated database backups with 30-day retention",
                "• Weekly full application backups with 12-week retention",
                "• Monthly system snapshots for disaster recovery",
                "• Automated backup verification and integrity testing",
                "• Documented recovery procedures with regular testing"
            ]),
            ("5. Security Implementation", [
                "Security measures protect the system and data from various threats.",
                "• Firewall configuration with minimal open ports",
                "• SSL/TLS encryption for all communications",
                "• Database encryption and secure connections",
                "• Role-based access control (RBAC)",
                "• Regular security updates and vulnerability management",
                "• Intrusion detection and monitoring systems"
            ]),
            ("6. Monitoring and Maintenance", [
                "Ongoing monitoring ensures system health and optimal performance.",
                "• Real-time system metrics monitoring (CPU, memory, disk)",
                "• Application performance monitoring and alerting",
                "• Database performance optimization and monitoring",
                "• Log aggregation and analysis for troubleshooting",
                "• Automated health checks and uptime monitoring",
                "• Regular maintenance schedules and procedures"
            ])
        ]
        
        for title, content in sections:
            self.story.append(Paragraph(title, self.heading1_style))
            self.story.append(Spacer(1, 12))
            
            for item in content:
                if item.startswith('•'):
                    self.story.append(Paragraph(item, self.bullet_style))
                else:
                    self.story.append(Paragraph(item, self.styles['Normal']))
                    self.story.append(Spacer(1, 6))
            
            self.story.append(Spacer(1, 20))

    def generate_pdf(self, filename="CUBE_OnPremise_Deployment_Guide_Comprehensive.pdf"):
        """Generate the PDF document"""
        print(f"🔄 Generating comprehensive PDF: {filename}")
        
        # Create document
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=60,
            leftMargin=60,
            topMargin=60,
            bottomMargin=60
        )
        
        # Create title page
        self.create_title_page()
        
        # Read and process markdown content
        markdown_content = read_markdown_file("ON_PREMISE_DEPLOYMENT_GUIDE.md")
        self.process_markdown_content(markdown_content)
        
        # Add page numbers and header
        def add_page_elements(canvas, doc):
            page_num = canvas.getPageNumber()
            if page_num > 1:
                # Header
                canvas.setFont('Helvetica', 9)
                canvas.drawString(60, A4[1] - 40, "CUBE PRO - On-Premise Deployment Guide")
                canvas.line(60, A4[1] - 45, A4[0] - 60, A4[1] - 45)
                
                # Footer with page number
                canvas.drawRightString(A4[0] - 60, 30, f"Page {page_num}")
                canvas.drawString(60, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Build PDF
        try:
            self.doc.build(self.story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
            
            # Get file size
            file_size = os.path.getsize(filename)
            
            print(f"✅ PDF generated successfully!")
            print(f"📄 File: {filename}")
            print(f"📂 Location: {os.path.abspath(filename)}")
            print(f"📊 Size: {file_size / 1024:.1f} KB")
            print(f"📄 Pages: Comprehensive multi-page document")
            
            return filename
            
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            raise

def main():
    """Main function"""
    try:
        generator = ComprehensivePDFGenerator()
        pdf_file = generator.generate_pdf()
        
        print(f"\n🎉 Success! Your comprehensive deployment guide is ready.")
        print(f"📖 Open the PDF to view the complete on-premise deployment instructions.")
        
        return pdf_file
        
    except Exception as e:
        print(f"❌ Failed to generate PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
