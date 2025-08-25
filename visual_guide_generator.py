#!/usr/bin/env python3
"""
CUBE - PRO Screenshot Guide Generator
Creates a visual guide with placeholder screenshots and step-by-step instructions
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
from datetime import datetime
import os

class ScreenshotGuideGenerator:
    def __init__(self):
        self.doc = None
        self.story = []
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Screenshot placeholder style
        self.styles.add(ParagraphStyle(
            name='ScreenshotPlaceholder',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=colors.grey,
            backColor=colors.lightgrey,
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=10
        ))
        
        # Step instruction style
        self.styles.add(ParagraphStyle(
            name='StepInstruction',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20,
            bulletIndent=10,
            backColor=colors.lightblue,
            borderWidth=1,
            borderColor=colors.blue,
            borderPadding=5
        ))
    
    def add_screenshot_placeholder(self, description, width=6*inch, height=3*inch):
        """Add a screenshot placeholder with description"""
        # Create a drawing for the placeholder
        drawing = Drawing(width, height)
        drawing.add(Rect(0, 0, width, height, fillColor=colors.lightgrey, strokeColor=colors.grey))
        
        # Add the drawing to story
        self.story.append(drawing)
        
        # Add description
        self.story.append(Paragraph(f"📷 Screenshot: {description}", self.styles['ScreenshotPlaceholder']))
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_visual_setup_guide(self):
        """Add visual setup guide with screenshot placeholders"""
        self.story.append(Paragraph("CUBE - PRO Visual Setup Guide", self.styles['CustomTitle']))
        self.story.append(Spacer(1, 0.5*inch))
        
        # Section 1: Login Process
        self.story.append(Paragraph("1. Initial Login Process", self.styles['Heading1']))
        
        step1_text = """
        <b>Step 1:</b> Navigate to your CUBE - PRO login page
        """
        self.story.append(Paragraph(step1_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Login page showing CUBE - PRO branding, username/password fields, and login button")
        
        step2_text = """
        <b>Step 2:</b> Enter your administrator credentials and click "Login"
        """
        self.story.append(Paragraph(step2_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Login page with sample credentials filled in")
        
        step3_text = """
        <b>Step 3:</b> You will be redirected to the main dashboard
        """
        self.story.append(Paragraph(step3_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Main dashboard showing navigation menu, KPI widgets, and recent work orders")
        
        self.story.append(PageBreak())
        
        # Section 2: User Management
        self.story.append(Paragraph("2. User Management Configuration", self.styles['Heading1']))
        
        step4_text = """
        <b>Step 1:</b> Access Configuration menu from the top navigation
        """
        self.story.append(Paragraph(step4_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Top navigation bar with Configuration menu highlighted")
        
        step5_text = """
        <b>Step 2:</b> Click on User Management in the Configuration dropdown
        """
        self.story.append(Paragraph(step5_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Configuration dropdown menu expanded showing User Management options")
        
        step6_text = """
        <b>Step 3:</b> Click 'Add New User' to create a user account
        """
        self.story.append(Paragraph(step6_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("User Management page with user list and 'Add New User' button highlighted")
        
        step7_text = """
        <b>Step 4:</b> Fill in the user creation form
        """
        self.story.append(Paragraph(step7_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("User creation form showing all fields: username, email, name, department, role, etc.")
        
        self.story.append(PageBreak())
        
        # Section 3: Department Management
        self.story.append(Paragraph("3. Department Management Setup", self.styles['Heading1']))
        
        step8_text = """
        <b>Step 1:</b> Navigate to Configuration → User Management → Department Management
        """
        self.story.append(Paragraph(step8_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Department Management page showing existing departments and Add New Department button")
        
        step9_text = """
        <b>Step 2:</b> Click 'Add New Department' and fill in department details
        """
        self.story.append(Paragraph(step9_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Department creation form with fields for name, code, description, manager, etc.")
        
        self.story.append(PageBreak())
        
        # Section 4: Work Order Categories
        self.story.append(Paragraph("4. Work Order Categories Configuration", self.styles['Heading1']))
        
        step10_text = """
        <b>Step 1:</b> Access Work Order Settings from Configuration menu
        """
        self.story.append(Paragraph(step10_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Configuration menu showing Work Order Settings option")
        
        step11_text = """
        <b>Step 2:</b> Configure categories for work order classification
        """
        self.story.append(Paragraph(step11_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Categories management page with existing categories and Add New Category form")
        
        self.story.append(PageBreak())
        
        # Section 5: Email Configuration
        self.story.append(Paragraph("5. Email Configuration Setup", self.styles['Heading1']))
        
        step12_text = """
        <b>Step 1:</b> Navigate to Configuration → Email Configuration → SMTP Settings
        """
        self.story.append(Paragraph(step12_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("SMTP configuration page with server settings fields")
        
        step13_text = """
        <b>Step 2:</b> Configure email templates for notifications
        """
        self.story.append(Paragraph(step13_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Email templates page showing different template types and editor")
        
        step14_text = """
        <b>Step 3:</b> Set up notification rules for automated emails
        """
        self.story.append(Paragraph(step14_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Notification rules page with rule creation form")
        
        self.story.append(PageBreak())
        
        # Section 6: Work Order Creation Process
        self.story.append(Paragraph("6. Work Order Creation Process", self.styles['Heading1']))
        
        step15_text = """
        <b>Step 1:</b> Click 'Create Work Order' from the main navigation or dashboard
        """
        self.story.append(Paragraph(step15_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Main dashboard with 'Create Work Order' button highlighted")
        
        step16_text = """
        <b>Step 2:</b> Fill in work order details using the comprehensive form
        """
        self.story.append(Paragraph(step16_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Work order creation form showing all fields: title, description, category, priority, etc.")
        
        step17_text = """
        <b>Step 3:</b> Review and submit the work order
        """
        self.story.append(Paragraph(step17_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Work order review page with submit button and form validation")
        
        self.story.append(PageBreak())
        
        # Section 7: Dashboard Overview
        self.story.append(Paragraph("7. Dashboard and Reporting Overview", self.styles['Heading1']))
        
        step18_text = """
        <b>Dashboard Features:</b> Key performance indicators and quick access
        """
        self.story.append(Paragraph(step18_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Full dashboard view showing KPI widgets, charts, recent work orders, and navigation")
        
        step19_text = """
        <b>Reports Section:</b> Access comprehensive reporting features
        """
        self.story.append(Paragraph(step19_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Reports page showing available report types and generated reports")
        
        self.story.append(PageBreak())
        
        # Section 8: Mobile Responsive Views
        self.story.append(Paragraph("8. Mobile and Responsive Interface", self.styles['Heading1']))
        
        step20_text = """
        <b>Mobile Dashboard:</b> CUBE - PRO works seamlessly on mobile devices
        """
        self.story.append(Paragraph(step20_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Mobile view of dashboard showing responsive design", width=3*inch, height=5*inch)
        
        step21_text = """
        <b>Mobile Work Order Creation:</b> Create work orders on the go
        """
        self.story.append(Paragraph(step21_text, self.styles['StepInstruction']))
        
        self.add_screenshot_placeholder("Mobile work order creation form", width=3*inch, height=5*inch)
    
    def add_configuration_checklist(self):
        """Add configuration checklist"""
        self.story.append(Paragraph("Configuration Checklist", self.styles['Heading1']))
        
        checklist_text = """
        Use this checklist to ensure you've completed all essential configuration steps:
        
        <b>User Management Setup:</b>
        ☐ Created user accounts for all team members
        ☐ Assigned appropriate roles to each user
        ☐ Configured department structure
        ☐ Set up assignment groups
        ☐ Configured approval delegation rules
        
        <b>Work Order Configuration:</b>
        ☐ Created work order categories
        ☐ Set up priority levels
        ☐ Configured status workflow
        ☐ Set SLA timeframes
        ☐ Tested work order creation process
        
        <b>Email and Notifications:</b>
        ☐ Configured SMTP settings
        ☐ Customized email templates
        ☐ Set up notification rules
        ☐ Tested email delivery
        ☐ Configured reminder schedules
        
        <b>Security and Access:</b>
        ☐ Reviewed user permissions
        ☐ Configured password policies
        ☐ Set up session timeouts
        ☐ Enabled audit logging
        ☐ Configured backup procedures
        
        <b>Reporting and Analytics:</b>
        ☐ Set up automated reports
        ☐ Configured dashboard KPIs
        ☐ Tested report generation
        ☐ Set up report delivery schedules
        ☐ Customized dashboard views
        
        <b>Training and Documentation:</b>
        ☐ Trained administrative users
        ☐ Trained end users
        ☐ Created user documentation
        ☐ Established support procedures
        ☐ Scheduled regular system reviews
        """
        
        self.story.append(Paragraph(checklist_text, self.styles['Normal']))
    
    def generate_visual_guide(self, filename="CUBE_PRO_Visual_Setup_Guide.pdf"):
        """Generate the visual setup guide PDF"""
        # Create the PDF document
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Add content sections
        self.add_visual_setup_guide()
        self.add_configuration_checklist()
        
        # Build the PDF
        self.doc.build(self.story)
        print(f"Visual Setup Guide generated successfully: {filename}")
        return filename

def main():
    """Main function to generate both guides"""
    generator = ScreenshotGuideGenerator()
    
    # Generate the visual guide
    visual_guide = generator.generate_visual_guide()
    
    print(f"✅ CUBE - PRO Visual Setup Guide generated successfully!")
    print(f"📄 File location: {os.path.abspath(visual_guide)}")
    print(f"📊 Visual Guide includes:")
    print("   • Step-by-step screenshots (placeholders)")
    print("   • Visual workflow demonstrations")
    print("   • Configuration checklists")
    print("   • Mobile interface examples")
    print("   • Quick reference sections")
    print("\n" + "="*60)
    print("📋 DOCUMENTATION PACKAGE COMPLETE:")
    print("📄 1. CUBE_PRO_Admin_Guide.pdf - Complete technical documentation")
    print("📄 2. CUBE_PRO_Visual_Setup_Guide.pdf - Visual step-by-step guide")
    print("\n💡 Note: Replace screenshot placeholders with actual screenshots")
    print("   from your CUBE - PRO system for best results.")

if __name__ == "__main__":
    main()
