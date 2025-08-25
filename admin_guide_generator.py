#!/usr/bin/env python3
"""
CUBE - PRO Application Admin Guide Generator
Generates a comprehensive PDF guide for system administrators
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

class AdminGuideGenerator:
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
        
        # Chapter heading style
        self.styles.add(ParagraphStyle(
            name='ChapterHeading',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=30,
            textColor=colors.darkblue,
            borderWidth=2,
            borderColor=colors.darkblue,
            borderPadding=10
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.darkgreen
        ))
        
        # Step style
        self.styles.add(ParagraphStyle(
            name='StepStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20,
            bulletIndent=10
        ))
        
        # Warning style
        self.styles.add(ParagraphStyle(
            name='Warning',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            textColor=colors.red,
            backColor=colors.lightgrey,
            borderWidth=1,
            borderColor=colors.red,
            borderPadding=5
        ))
        
        # Note style
        self.styles.add(ParagraphStyle(
            name='Note',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            textColor=colors.blue,
            backColor=colors.lightblue,
            borderWidth=1,
            borderColor=colors.blue,
            borderPadding=5
        ))
    
    def add_title_page(self):
        """Add title page to the document"""
        self.story.append(Spacer(1, 2*inch))
        
        # Main title
        title = Paragraph("CUBE - PRO", self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        subtitle = Paragraph("Enterprise Work Order Management System", self.styles['Title'])
        self.story.append(subtitle)
        self.story.append(Spacer(1, 0.5*inch))
        
        # Guide title
        guide_title = Paragraph("System Administrator Configuration Guide", self.styles['Heading1'])
        self.story.append(guide_title)
        self.story.append(Spacer(1, 1*inch))
        
        # Version info
        version_info = f"""
        <para align=center>
        <b>Version:</b> 1.0<br/>
        <b>Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
        <b>Powered by:</b> Rubix Solutions
        </para>
        """
        self.story.append(Paragraph(version_info, self.styles['Normal']))
        self.story.append(PageBreak())
    
    def add_table_of_contents(self):
        """Add table of contents"""
        self.story.append(Paragraph("Table of Contents", self.styles['ChapterHeading']))
        
        toc_data = [
            ["Chapter", "Page"],
            ["1. Introduction", "3"],
            ["2. Initial System Setup", "4"],
            ["3. User Management Configuration", "8"],
            ["4. Department Management", "12"],
            ["5. Assignment Groups Configuration", "15"],
            ["6. Approval Delegation Setup", "18"],
            ["7. Work Order Categories & Priorities", "21"],
            ["8. Status Configuration", "24"],
            ["9. Email Configuration", "27"],
            ["10. Notification Rules", "30"],
            ["11. Reporting Setup", "33"],
            ["12. Security & Access Control", "36"],
            ["13. System Maintenance", "39"],
            ["14. Troubleshooting", "42"],
            ["Appendix A: Common Issues", "45"],
            ["Appendix B: Best Practices", "47"]
        ]
        
        toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        self.story.append(toc_table)
        self.story.append(PageBreak())
    
    def add_introduction(self):
        """Add introduction chapter"""
        self.story.append(Paragraph("1. Introduction", self.styles['ChapterHeading']))
        
        intro_text = """
        Welcome to the CUBE - PRO Enterprise Work Order Management System Administrator Guide. 
        This comprehensive guide will walk you through the complete setup and configuration of 
        your work order management system.
        
        This guide is designed for system administrators who need to:
        • Configure the system for their organization
        • Set up users, departments, and access controls
        • Configure work order workflows and approval processes
        • Manage system settings and maintenance
        """
        
        self.story.append(Paragraph(intro_text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Prerequisites
        self.story.append(Paragraph("Prerequisites", self.styles['SectionHeading']))
        prereq_text = """
        Before beginning the configuration process, ensure you have:
        • Administrator access to the CUBE - PRO system
        • Understanding of your organization's workflow processes
        • List of departments and user roles in your organization
        • Email server configuration details (if using email notifications)
        """
        
        self.story.append(Paragraph(prereq_text, self.styles['Normal']))
        
        # Important note
        note_text = """
        <b>Important:</b> This guide assumes you have already installed and deployed the 
        CUBE - PRO system. For installation instructions, please refer to the Installation Guide.
        """
        self.story.append(Paragraph(note_text, self.styles['Note']))
        self.story.append(PageBreak())
    
    def add_initial_setup(self):
        """Add initial system setup chapter"""
        self.story.append(Paragraph("2. Initial System Setup", self.styles['ChapterHeading']))
        
        # First Login
        self.story.append(Paragraph("2.1 First Login", self.styles['SectionHeading']))
        
        first_login_steps = """
        Follow these steps for your first login to the system:
        
        1. Open your web browser and navigate to your CUBE - PRO URL
        2. You will see the login screen with the CUBE - PRO branding
        3. Use the default administrator credentials (these should have been provided during installation)
        4. Upon successful login, you will be directed to the main dashboard
        """
        
        self.story.append(Paragraph(first_login_steps, self.styles['Normal']))
        
        # Screenshot placeholder
        screenshot_note = """
        📷 Screenshot: Login screen showing the CUBE - PRO interface with username and password fields
        """
        self.story.append(Paragraph(screenshot_note, self.styles['Note']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Change Default Password
        self.story.append(Paragraph("2.2 Change Default Administrator Password", self.styles['SectionHeading']))
        
        password_steps = """
        <b>CRITICAL:</b> Immediately change the default administrator password for security.
        
        Steps to change password:
        1. Click on your username in the top navigation bar
        2. Select "Profile" from the dropdown menu
        3. Click "Change Password" button
        4. Enter your current password
        5. Enter a strong new password (minimum 8 characters, include uppercase, lowercase, numbers)
        6. Confirm the new password
        7. Click "Update Password"
        """
        
        self.story.append(Paragraph(password_steps, self.styles['StepStyle']))
        
        # Security warning
        security_warning = """
        <b>Security Warning:</b> Use a strong password and store it securely. This account has 
        full administrative access to your work order management system.
        """
        self.story.append(Paragraph(security_warning, self.styles['Warning']))
        
        self.story.append(PageBreak())
    
    def add_user_management(self):
        """Add user management configuration chapter"""
        self.story.append(Paragraph("3. User Management Configuration", self.styles['ChapterHeading']))
        
        # Overview
        self.story.append(Paragraph("3.1 User Management Overview", self.styles['SectionHeading']))
        overview_text = """
        The User Management module allows you to create and manage user accounts, assign roles, 
        and configure access permissions. This is one of the most critical configurations as it 
        determines who can access what features in your system.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Accessing User Management
        self.story.append(Paragraph("3.2 Accessing User Management", self.styles['SectionHeading']))
        access_steps = """
        To access User Management:
        1. From the main dashboard, look for the "Configuration" menu in the navigation bar
        2. Click on "Configuration" to expand the menu
        3. Under "User Management", you will see options for:
           • User Management - Main user configuration
           • Department Management - Organize users by department
           • Assignment Groups - Group users for work assignment
           • Approval Delegation - Set up approval workflows
        """
        self.story.append(Paragraph(access_steps, self.styles['StepStyle']))
        
        # Creating Users
        self.story.append(Paragraph("3.3 Creating New Users", self.styles['SectionHeading']))
        user_creation_steps = """
        To create a new user account:
        
        1. Navigate to Configuration → User Management → User Management
        2. Click the "Add New User" button (usually a "+" icon or green button)
        3. Fill in the required information:
           • <b>Username:</b> Unique identifier for login (cannot be changed later)
           • <b>Email:</b> User's email address (used for notifications)
           • <b>First Name:</b> User's first name
           • <b>Last Name:</b> User's last name
           • <b>Phone:</b> Contact phone number (optional)
           • <b>Department:</b> Select from configured departments
           • <b>Role:</b> Assign appropriate role (Admin, Manager, User, etc.)
           • <b>Manager:</b> Select the user's direct manager
           • <b>Assignment Group:</b> Select relevant assignment group
           • <b>Active Status:</b> Enable/disable the account
        
        4. Set a temporary password or use auto-generated password
        5. Click "Create User" to save
        """
        self.story.append(Paragraph(user_creation_steps, self.styles['StepStyle']))
        
        # User Roles
        self.story.append(Paragraph("3.4 Understanding User Roles", self.styles['SectionHeading']))
        roles_table_data = [
            ["Role", "Permissions", "Typical Use"],
            ["Admin", "Full system access, configuration, user management", "System administrators, IT staff"],
            ["Manager", "Approve work orders, view reports, manage team", "Department heads, supervisors"],
            ["User", "Create work orders, update assigned tasks", "Regular employees, technicians"],
            ["Viewer", "Read-only access to work orders and reports", "Executives, auditors"]
        ]
        
        roles_table = Table(roles_table_data, colWidths=[1.2*inch, 2.5*inch, 2*inch])
        roles_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(roles_table)
        self.story.append(PageBreak())
    
    def add_department_management(self):
        """Add department management chapter"""
        self.story.append(Paragraph("4. Department Management", self.styles['ChapterHeading']))
        
        # Overview
        overview_text = """
        Departments help organize users and work orders by functional areas of your organization. 
        Proper department configuration is essential for routing work orders and generating 
        meaningful reports.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Creating Departments
        self.story.append(Paragraph("4.1 Creating Departments", self.styles['SectionHeading']))
        dept_steps = """
        To create a new department:
        
        1. Navigate to Configuration → User Management → Department Management
        2. Click "Add New Department" button
        3. Fill in the department information:
           • <b>Department Name:</b> Clear, descriptive name (e.g., "IT Support", "Facilities")
           • <b>Department Code:</b> Short abbreviation (e.g., "IT", "FAC")
           • <b>Description:</b> Brief description of department function
           • <b>Manager:</b> Select department head/manager
           • <b>Budget Code:</b> For cost tracking (optional)
           • <b>Active Status:</b> Enable/disable department
        
        4. Click "Save Department"
        """
        self.story.append(Paragraph(dept_steps, self.styles['StepStyle']))
        
        # Best Practices
        self.story.append(Paragraph("4.2 Department Configuration Best Practices", self.styles['SectionHeading']))
        best_practices = """
        • <b>Consistent Naming:</b> Use clear, standardized department names
        • <b>Logical Grouping:</b> Group related functions together
        • <b>Manager Assignment:</b> Always assign a manager for approval workflows
        • <b>Regular Review:</b> Periodically review and update department structure
        • <b>Documentation:</b> Maintain documentation of department responsibilities
        """
        self.story.append(Paragraph(best_practices, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_assignment_groups(self):
        """Add assignment groups configuration chapter"""
        self.story.append(Paragraph("5. Assignment Groups Configuration", self.styles['ChapterHeading']))
        
        # Overview
        overview_text = """
        Assignment Groups allow you to create specialized teams that can be assigned work orders 
        based on skills, availability, or location. This is particularly useful for technical 
        teams or specialized service groups.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Creating Assignment Groups
        self.story.append(Paragraph("5.1 Creating Assignment Groups", self.styles['SectionHeading']))
        group_steps = """
        To create an assignment group:
        
        1. Navigate to Configuration → User Management → Assignment Groups
        2. Click "Add New Assignment Group"
        3. Configure the group:
           • <b>Group Name:</b> Descriptive name (e.g., "Network Technicians", "HVAC Team")
           • <b>Group Code:</b> Short identifier
           • <b>Description:</b> Group's purpose and responsibilities
           • <b>Group Leader:</b> Select group supervisor
           • <b>Skill Tags:</b> Add relevant skill keywords
           • <b>Active Status:</b> Enable/disable group
        
        4. Add group members:
           • Select users from available list
           • Assign roles within the group (Lead, Member, Backup)
           • Set availability schedules if needed
        
        5. Save the assignment group
        """
        self.story.append(Paragraph(group_steps, self.styles['StepStyle']))
        
        # Examples
        self.story.append(Paragraph("5.2 Assignment Group Examples", self.styles['SectionHeading']))
        examples_table_data = [
            ["Group Name", "Purpose", "Members"],
            ["IT Support Level 1", "Basic IT support and troubleshooting", "Help desk technicians"],
            ["Facilities Maintenance", "Building maintenance and repairs", "Maintenance staff, contractors"],
            ["Network Infrastructure", "Network and server maintenance", "Network administrators, engineers"],
            ["Security Team", "Physical and cyber security", "Security officers, IT security"],
        ]
        
        examples_table = Table(examples_table_data, colWidths=[1.8*inch, 2.2*inch, 2*inch])
        examples_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(examples_table)
        self.story.append(PageBreak())
    
    def add_approval_delegation(self):
        """Add approval delegation setup chapter"""
        self.story.append(Paragraph("6. Approval Delegation Setup", self.styles['ChapterHeading']))
        
        # Overview
        overview_text = """
        Approval Delegation allows you to set up automated approval workflows for work orders. 
        This ensures proper authorization and accountability for work requests while maintaining 
        efficiency in your processes.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Configuring Approval Rules
        self.story.append(Paragraph("6.1 Configuring Approval Rules", self.styles['SectionHeading']))
        approval_steps = """
        To set up approval delegation:
        
        1. Navigate to Configuration → User Management → Approval Delegation
        2. Click "Add New Approval Rule"
        3. Define the approval criteria:
           • <b>Rule Name:</b> Descriptive name for the rule
           • <b>Trigger Conditions:</b>
             - Work order value threshold (e.g., >$1000)
             - Department or category specific
             - Priority level requirements
             - Time-sensitive criteria
        
        4. Set approval hierarchy:
           • <b>Primary Approver:</b> First level approval
           • <b>Secondary Approver:</b> For higher value/priority items
           • <b>Backup Approvers:</b> When primary is unavailable
           • <b>Auto-Approval:</b> For routine, low-value requests
        
        5. Configure notification settings:
           • Email notifications to approvers
           • Escalation timelines
           • Reminder frequencies
        
        6. Test the approval workflow
        7. Activate the rule
        """
        self.story.append(Paragraph(approval_steps, self.styles['StepStyle']))
        
        # Common Approval Scenarios
        self.story.append(Paragraph("6.2 Common Approval Scenarios", self.styles['SectionHeading']))
        scenarios_text = """
        <b>Scenario 1: Cost-Based Approval</b>
        • Under $500: Auto-approve
        • $500-$2000: Department manager approval
        • Over $2000: Department manager + Finance approval
        
        <b>Scenario 2: Emergency Work Orders</b>
        • High priority: Auto-approve, notify management
        • After-hours: On-call manager approval
        • Safety-critical: Immediate approval with post-review
        
        <b>Scenario 3: Vendor/Contractor Work</b>
        • Internal staff: Standard approval
        • External vendors: Procurement + Department approval
        • Emergency contractors: Manager approval + compliance review
        """
        self.story.append(Paragraph(scenarios_text, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_work_order_categories(self):
        """Add work order categories and priorities chapter"""
        self.story.append(Paragraph("7. Work Order Categories & Priorities", self.styles['ChapterHeading']))
        
        # Categories Setup
        self.story.append(Paragraph("7.1 Setting Up Work Order Categories", self.styles['SectionHeading']))
        categories_text = """
        Categories help organize and route work orders effectively. Proper categorization enables 
        better reporting, resource allocation, and workflow management.
        
        To configure categories:
        1. Navigate to Configuration → Work Order Settings → Categories
        2. Click "Add New Category"
        3. Configure category details:
           • <b>Category Name:</b> Clear, descriptive name
           • <b>Category Code:</b> Short identifier for reporting
           • <b>Description:</b> Purpose and scope of category
           • <b>Default Assignment Group:</b> Auto-assign to relevant team
           • <b>SLA (Service Level Agreement):</b> Expected response/completion time
           • <b>Cost Center:</b> For budget tracking
           • <b>Required Fields:</b> Mandatory information for this category
        
        4. Set category-specific workflows if needed
        5. Save and activate the category
        """
        self.story.append(Paragraph(categories_text, self.styles['StepStyle']))
        
        # Sample Categories
        sample_categories_data = [
            ["Category", "Description", "Typical SLA", "Assignment Group"],
            ["IT Support", "Computer, software, network issues", "4 hours", "IT Support Team"],
            ["Facilities", "Building maintenance, utilities", "24 hours", "Facilities Team"],
            ["Equipment Repair", "Machinery, tools, equipment", "8 hours", "Maintenance Team"],
            ["Safety Issue", "Safety hazards, compliance", "2 hours", "Safety Team"],
            ["Vendor Service", "External contractor work", "Varies", "Procurement Team"],
        ]
        
        categories_table = Table(sample_categories_data, colWidths=[1.4*inch, 1.8*inch, 1.2*inch, 1.6*inch])
        categories_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.pink),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(categories_table)
        
        # Priorities Setup
        self.story.append(Paragraph("7.2 Setting Up Priority Levels", self.styles['SectionHeading']))
        priorities_text = """
        Priority levels help ensure urgent work orders receive appropriate attention and resources.
        
        Recommended priority structure:
        • <b>Critical (P1):</b> System down, safety hazard - Response within 1 hour
        • <b>High (P2):</b> Significant impact, urgent - Response within 4 hours
        • <b>Medium (P3):</b> Standard business impact - Response within 24 hours
        • <b>Low (P4):</b> Minor impact, convenience - Response within 72 hours
        • <b>Planned (P5):</b> Scheduled maintenance - Response as scheduled
        """
        self.story.append(Paragraph(priorities_text, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_status_configuration(self):
        """Add status configuration chapter"""
        self.story.append(Paragraph("8. Status Configuration", self.styles['ChapterHeading']))
        
        # Status Overview
        overview_text = """
        Work order statuses track the lifecycle of requests from creation to completion. 
        Proper status configuration ensures clear communication and effective workflow management.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Default Statuses
        self.story.append(Paragraph("8.1 Default Status Configuration", self.styles['SectionHeading']))
        
        default_statuses_data = [
            ["Status", "Description", "Color", "Next Status Options"],
            ["Draft", "Work order being created", "Gray", "Submitted, Cancelled"],
            ["Submitted", "Awaiting approval/assignment", "Blue", "Approved, Rejected"],
            ["Approved", "Approved, awaiting assignment", "Green", "In Progress, On Hold"],
            ["In Progress", "Work actively being performed", "Orange", "Completed, On Hold"],
            ["On Hold", "Work temporarily suspended", "Yellow", "In Progress, Cancelled"],
            ["Completed", "Work finished successfully", "Dark Green", "Closed"],
            ["Cancelled", "Work order cancelled", "Red", "None"],
            ["Closed", "Work order closed/archived", "Black", "None"],
        ]
        
        status_table = Table(default_statuses_data, colWidths=[1*inch, 1.8*inch, 0.8*inch, 2.4*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(status_table)
        
        # Custom Status Configuration
        self.story.append(Paragraph("8.2 Creating Custom Statuses", self.styles['SectionHeading']))
        custom_status_steps = """
        To create custom statuses for your organization:
        
        1. Navigate to Configuration → Work Order Settings → Statuses
        2. Review existing statuses
        3. Click "Add New Status"
        4. Configure status properties:
           • <b>Status Name:</b> Clear, action-oriented name
           • <b>Status Description:</b> When and how this status is used
           • <b>Color Code:</b> Visual indicator for dashboards
           • <b>Status Type:</b> Active, Closed, Cancelled
           • <b>Auto-notifications:</b> Send emails when status changes
           • <b>Required Actions:</b> What must be done in this status
           • <b>Time Limits:</b> Maximum time allowed in this status
        
        5. Set status transitions (which statuses can follow)
        6. Test the status workflow
        7. Activate for use
        """
        self.story.append(Paragraph(custom_status_steps, self.styles['StepStyle']))
        
        self.story.append(PageBreak())
    
    def add_email_configuration(self):
        """Add email configuration chapter"""
        self.story.append(Paragraph("9. Email Configuration", self.styles['ChapterHeading']))
        
        # Email Setup Overview
        overview_text = """
        Email configuration enables automated notifications for work order updates, approvals, 
        and reminders. Proper email setup is crucial for keeping stakeholders informed and 
        maintaining workflow efficiency.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # SMTP Configuration
        self.story.append(Paragraph("9.1 SMTP Server Configuration", self.styles['SectionHeading']))
        smtp_steps = """
        To configure email settings:
        
        1. Navigate to Configuration → Email Configuration → SMTP Settings
        2. Enter your email server details:
           • <b>SMTP Server:</b> Your email server hostname
           • <b>SMTP Port:</b> Usually 587 (TLS) or 465 (SSL)
           • <b>Security:</b> TLS/SSL encryption method
           • <b>Username:</b> Email account for sending notifications
           • <b>Password:</b> Email account password or app password
           • <b>From Address:</b> Address that appears as sender
           • <b>From Name:</b> Display name for emails
        
        3. Test the configuration:
           • Click "Send Test Email"
           • Enter a test recipient email
           • Verify the test email is received
        
        4. Save configuration if test successful
        """
        self.story.append(Paragraph(smtp_steps, self.styles['StepStyle']))
        
        # Common SMTP Settings
        self.story.append(Paragraph("9.2 Common SMTP Provider Settings", self.styles['SectionHeading']))
        
        smtp_providers_data = [
            ["Provider", "SMTP Server", "Port", "Security", "Notes"],
            ["Gmail", "smtp.gmail.com", "587", "TLS", "Requires app password"],
            ["Outlook/Hotmail", "smtp-mail.outlook.com", "587", "TLS", "Use account credentials"],
            ["Yahoo", "smtp.mail.yahoo.com", "587", "TLS", "Requires app password"],
            ["Office 365", "smtp.office365.com", "587", "TLS", "Use account credentials"],
            ["Custom/On-premise", "Your server", "Varies", "TLS/SSL", "Contact IT department"],
        ]
        
        smtp_table = Table(smtp_providers_data, colWidths=[1.2*inch, 1.5*inch, 0.6*inch, 0.8*inch, 1.9*inch])
        smtp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(smtp_table)
        
        # Email Templates
        self.story.append(Paragraph("9.3 Email Template Configuration", self.styles['SectionHeading']))
        template_text = """
        Customize email templates for different notification types:
        
        1. Navigate to Configuration → Email Configuration → Email Templates
        2. Select template type to customize:
           • Work order created
           • Work order assigned
           • Work order completed
           • Approval required
           • Status updates
           • Reminder notifications
        
        3. Customize template content:
           • Subject line with dynamic variables
           • Email body with HTML formatting
           • Include relevant work order details
           • Add company branding/signature
        
        4. Use available variables:
           • {{work_order_number}} - Work order ID
           • {{title}} - Work order title
           • {{status}} - Current status
           • {{assigned_to}} - Assigned user name
           • {{due_date}} - Due date
           • {{priority}} - Priority level
        
        5. Preview and test templates
        6. Save and activate
        """
        self.story.append(Paragraph(template_text, self.styles['StepStyle']))
        
        self.story.append(PageBreak())
    
    def add_notification_rules(self):
        """Add notification rules chapter"""
        self.story.append(Paragraph("10. Notification Rules", self.styles['ChapterHeading']))
        
        # Rules Overview
        overview_text = """
        Notification rules determine when and to whom email notifications are sent. Properly 
        configured rules ensure relevant stakeholders are informed without overwhelming users 
        with unnecessary emails.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Creating Notification Rules
        self.story.append(Paragraph("10.1 Creating Notification Rules", self.styles['SectionHeading']))
        rules_steps = """
        To create notification rules:
        
        1. Navigate to Configuration → Email Configuration → Notification Rules
        2. Click "Add New Rule"
        3. Define rule criteria:
           • <b>Rule Name:</b> Descriptive name for the rule
           • <b>Trigger Event:</b> What event triggers the notification
             - Work order created
             - Status changed
             - Assignment changed
             - Due date approaching
             - Priority escalated
        
        4. Set conditions:
           • <b>Category filter:</b> Specific categories only
           • <b>Priority filter:</b> Priority levels that trigger
           • <b>Department filter:</b> Specific departments
           • <b>Value threshold:</b> Cost-based triggers
        
        5. Define recipients:
           • Work order creator
           • Assigned user
           • Department manager
           • Assignment group members
           • Custom email addresses
        
        6. Set timing:
           • Immediate notification
           • Delayed notification
           • Recurring reminders
           • Business hours only
        
        7. Test and activate the rule
        """
        self.story.append(Paragraph(rules_steps, self.styles['StepStyle']))
        
        # Sample Notification Rules
        self.story.append(Paragraph("10.2 Sample Notification Rules", self.styles['SectionHeading']))
        
        sample_rules_data = [
            ["Rule Name", "Trigger", "Recipients", "Timing"],
            ["New Work Order", "Work order created", "Creator, Manager", "Immediate"],
            ["High Priority Alert", "High/Critical priority", "All relevant staff", "Immediate"],
            ["Assignment Notice", "Work order assigned", "Assigned user", "Immediate"],
            ["Due Date Reminder", "24 hours before due", "Assigned user, Manager", "Daily at 9 AM"],
            ["Completion Notice", "Work order completed", "Creator, Manager", "Immediate"],
            ["Overdue Alert", "Past due date", "Assigned user, Manager", "Every 4 hours"],
        ]
        
        rules_table = Table(sample_rules_data, colWidths=[1.4*inch, 1.4*inch, 1.6*inch, 1.6*inch])
        rules_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(rules_table)
        self.story.append(PageBreak())
    
    def add_reporting_setup(self):
        """Add reporting setup chapter"""
        self.story.append(Paragraph("11. Reporting Setup", self.styles['ChapterHeading']))
        
        # Reporting Overview
        overview_text = """
        The reporting module provides insights into work order performance, trends, and resource 
        utilization. Proper setup ensures you have the metrics needed for decision-making and 
        process improvement.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Available Reports
        self.story.append(Paragraph("11.1 Available Report Types", self.styles['SectionHeading']))
        
        report_types_data = [
            ["Report Type", "Purpose", "Key Metrics", "Frequency"],
            ["Work Order Summary", "Overall performance overview", "Total, completed, pending counts", "Daily/Weekly"],
            ["Department Performance", "Department-specific metrics", "Response times, completion rates", "Weekly/Monthly"],
            ["User Productivity", "Individual performance", "Assignments, completion times", "Weekly/Monthly"],
            ["Cost Analysis", "Financial tracking", "Costs by category, department", "Monthly/Quarterly"],
            ["SLA Compliance", "Service level adherence", "On-time completion rates", "Daily/Weekly"],
            ["Trend Analysis", "Historical patterns", "Volume trends, seasonal patterns", "Monthly/Quarterly"],
        ]
        
        reports_table = Table(report_types_data, colWidths=[1.4*inch, 1.4*inch, 1.6*inch, 1.6*inch])
        reports_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.moccasin),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(reports_table)
        
        # Report Configuration
        self.story.append(Paragraph("11.2 Configuring Automated Reports", self.styles['SectionHeading']))
        report_config_steps = """
        To set up automated reporting:
        
        1. Navigate to Reports → Report Configuration
        2. Click "Create Scheduled Report"
        3. Configure report parameters:
           • <b>Report Name:</b> Descriptive name
           • <b>Report Type:</b> Select from available templates
           • <b>Data Range:</b> Time period to include
           • <b>Filters:</b> Department, category, priority filters
           • <b>Format:</b> PDF, Excel, or CSV
        
        4. Set delivery schedule:
           • <b>Frequency:</b> Daily, weekly, monthly
           • <b>Day/Time:</b> When to generate and send
           • <b>Recipients:</b> Email addresses for delivery
           • <b>Subject line:</b> Email subject template
        
        5. Preview the report
        6. Save and activate scheduling
        """
        self.story.append(Paragraph(report_config_steps, self.styles['StepStyle']))
        
        # KPI Dashboard
        self.story.append(Paragraph("11.3 Setting Up KPI Dashboard", self.styles['SectionHeading']))
        kpi_text = """
        Configure key performance indicators for the main dashboard:
        
        <b>Essential KPIs to display:</b>
        • Open work orders count
        • Overdue work orders
        • Average response time
        • Completion rate (current period)
        • High priority work orders
        • Team workload distribution
        • Cost trend (if applicable)
        • Customer satisfaction scores
        
        <b>Dashboard customization:</b>
        • Role-based dashboard views
        • Drill-down capabilities
        • Real-time data refresh
        • Export capabilities
        • Mobile-friendly display
        """
        self.story.append(Paragraph(kpi_text, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_security_access_control(self):
        """Add security and access control chapter"""
        self.story.append(Paragraph("12. Security & Access Control", self.styles['ChapterHeading']))
        
        # Security Overview
        overview_text = """
        Proper security configuration protects your work order data and ensures users have 
        appropriate access levels. This chapter covers essential security settings and best practices.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Access Control Configuration
        self.story.append(Paragraph("12.1 Role-Based Access Control", self.styles['SectionHeading']))
        rbac_text = """
        Configure access permissions by role:
        
        1. Navigate to Configuration → Security → Role Management
        2. Review default roles and permissions
        3. Customize permissions as needed:
           • <b>Admin Role:</b> Full system access
           • <b>Manager Role:</b> Department oversight, approvals
           • <b>User Role:</b> Create and update work orders
           • <b>Viewer Role:</b> Read-only access
        
        4. Create custom roles if needed:
           • Define specific permission sets
           • Assign to specialized functions
           • Test access levels thoroughly
        
        5. Implement least privilege principle:
           • Grant minimum necessary permissions
           • Regular access reviews
           • Remove unused accounts promptly
        """
        self.story.append(Paragraph(rbac_text, self.styles['StepStyle']))
        
        # Security Settings
        self.story.append(Paragraph("12.2 System Security Settings", self.styles['SectionHeading']))
        security_checklist = """
        <b>Essential Security Configurations:</b>
        
        ✓ <b>Password Policy:</b>
          • Minimum length: 8 characters
          • Complexity requirements: uppercase, lowercase, numbers
          • Password expiration: 90 days
          • Password history: Prevent reuse of last 5 passwords
        
        ✓ <b>Session Management:</b>
          • Session timeout: 30 minutes of inactivity
          • Concurrent session limits
          • Secure session cookies
          • Logout on browser close
        
        ✓ <b>Login Security:</b>
          • Account lockout after 5 failed attempts
          • Lockout duration: 15 minutes
          • Strong captcha for repeated failures
          • Login attempt logging
        
        ✓ <b>Data Protection:</b>
          • HTTPS encryption for all traffic
          • Database encryption at rest
          • Regular security backups
          • Audit trail logging
        
        ✓ <b>Access Monitoring:</b>
          • User activity logging
          • Failed login alerts
          • Privilege escalation monitoring
          • Regular access reviews
        """
        self.story.append(Paragraph(security_checklist, self.styles['Normal']))
        
        # Backup and Recovery
        self.story.append(Paragraph("12.3 Backup and Recovery", self.styles['SectionHeading']))
        backup_text = """
        Implement robust backup and recovery procedures:
        
        <b>Backup Strategy:</b>
        • Daily automated backups
        • Weekly full system backups
        • Off-site backup storage
        • Regular recovery testing
        
        <b>What to backup:</b>
        • Database (work orders, users, configuration)
        • File attachments and documents
        • System configuration files
        • Custom templates and reports
        
        <b>Recovery procedures:</b>
        • Document step-by-step recovery process
        • Test recovery procedures quarterly
        • Maintain recovery time objectives (RTO)
        • Train staff on emergency procedures
        """
        self.story.append(Paragraph(backup_text, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_system_maintenance(self):
        """Add system maintenance chapter"""
        self.story.append(Paragraph("13. System Maintenance", self.styles['ChapterHeading']))
        
        # Maintenance Overview
        overview_text = """
        Regular system maintenance ensures optimal performance, data integrity, and system 
        reliability. This chapter outlines essential maintenance tasks and schedules.
        """
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        
        # Regular Maintenance Tasks
        self.story.append(Paragraph("13.1 Regular Maintenance Schedule", self.styles['SectionHeading']))
        
        maintenance_schedule_data = [
            ["Task", "Frequency", "Description", "Impact"],
            ["Database cleanup", "Weekly", "Remove old logs, temporary data", "Low"],
            ["System health check", "Daily", "Monitor performance metrics", "None"],
            ["User account review", "Monthly", "Deactivate unused accounts", "Medium"],
            ["Backup verification", "Weekly", "Verify backup integrity", "None"],
            ["Security updates", "As needed", "Apply critical security patches", "Medium"],
            ["Performance tuning", "Quarterly", "Optimize database and queries", "Low"],
            ["Capacity planning", "Monthly", "Monitor storage and usage", "None"],
            ["Log rotation", "Weekly", "Archive and compress log files", "Low"],
        ]
        
        maintenance_table = Table(maintenance_schedule_data, colWidths=[1.5*inch, 1*inch, 2*inch, 1.5*inch])
        maintenance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(maintenance_table)
        
        # Performance Monitoring
        self.story.append(Paragraph("13.2 Performance Monitoring", self.styles['SectionHeading']))
        monitoring_text = """
        Monitor these key performance indicators:
        
        <b>System Performance:</b>
        • Response times for page loads
        • Database query performance
        • Server resource utilization (CPU, memory, disk)
        • Network latency and throughput
        
        <b>Application Metrics:</b>
        • User session counts
        • Work order processing times
        • Email delivery success rates
        • Error rates and types
        
        <b>Monitoring Tools:</b>
        • Built-in performance dashboard
        • Server monitoring tools
        • Database performance monitors
        • Application log analysis
        
        <b>Alert Thresholds:</b>
        • Set alerts for critical metrics
        • Define escalation procedures
        • Document response procedures
        • Regular threshold reviews
        """
        self.story.append(Paragraph(monitoring_text, self.styles['Normal']))
        
        # Database Maintenance
        self.story.append(Paragraph("13.3 Database Maintenance", self.styles['SectionHeading']))
        db_maintenance_text = """
        Regular database maintenance tasks:
        
        <b>Weekly Tasks:</b>
        • Update database statistics
        • Rebuild fragmented indexes
        • Clean temporary tables
        • Verify backup integrity
        
        <b>Monthly Tasks:</b>
        • Archive old work order data
        • Analyze space usage
        • Review query performance
        • Update maintenance plans
        
        <b>Quarterly Tasks:</b>
        • Full database integrity check
        • Performance baseline review
        • Capacity planning assessment
        • Recovery procedure testing
        """
        self.story.append(Paragraph(db_maintenance_text, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_troubleshooting(self):
        """Add troubleshooting chapter"""
        self.story.append(Paragraph("14. Troubleshooting", self.styles['ChapterHeading']))
        
        # Common Issues
        self.story.append(Paragraph("14.1 Common Issues and Solutions", self.styles['SectionHeading']))
        
        # Login Issues
        self.story.append(Paragraph("Login and Authentication Issues", self.styles['SectionHeading']))
        login_issues_text = """
        <b>Problem:</b> Users cannot log in
        <b>Possible Causes and Solutions:</b>
        • Incorrect credentials - Verify username/password, reset if necessary
        • Account locked - Check account status, unlock if needed
        • Session timeout - Clear browser cache and cookies
        • Browser compatibility - Try different browser or update current one
        • Network connectivity - Verify network connection and firewall settings
        
        <b>Problem:</b> Frequent logouts
        <b>Solutions:</b>
        • Increase session timeout in system settings
        • Check for browser security settings blocking cookies
        • Verify system time synchronization
        """
        self.story.append(Paragraph(login_issues_text, self.styles['Normal']))
        
        # Email Issues
        self.story.append(Paragraph("Email Notification Issues", self.styles['SectionHeading']))
        email_issues_text = """
        <b>Problem:</b> Emails not being sent
        <b>Troubleshooting Steps:</b>
        1. Check SMTP configuration settings
        2. Test SMTP connection manually
        3. Verify email account credentials
        4. Check firewall/network restrictions
        5. Review email server logs
        6. Verify recipient email addresses
        
        <b>Problem:</b> Emails going to spam
        <b>Solutions:</b>
        • Configure SPF/DKIM records
        • Use authenticated SMTP
        • Avoid spam trigger words
        • Include unsubscribe links
        • Monitor sender reputation
        """
        self.story.append(Paragraph(email_issues_text, self.styles['Normal']))
        
        # Performance Issues
        self.story.append(Paragraph("Performance Issues", self.styles['SectionHeading']))
        performance_issues_text = """
        <b>Problem:</b> Slow page load times
        <b>Diagnostic Steps:</b>
        1. Check server resource utilization
        2. Analyze database query performance
        3. Review network latency
        4. Check for large file attachments
        5. Monitor concurrent user load
        
        <b>Solutions:</b>
        • Optimize database queries
        • Increase server resources
        • Implement caching strategies
        • Archive old data
        • Optimize file storage
        """
        self.story.append(Paragraph(performance_issues_text, self.styles['Normal']))
        
        # Data Issues
        self.story.append(Paragraph("Data and Reporting Issues", self.styles['SectionHeading']))
        data_issues_text = """
        <b>Problem:</b> Missing or incorrect data in reports
        <b>Troubleshooting:</b>
        1. Verify report filter settings
        2. Check data source integrity
        3. Review user permissions
        4. Validate date range parameters
        5. Check for data synchronization issues
        
        <b>Problem:</b> Work orders not appearing
        <b>Possible Causes:</b>
        • Permission restrictions
        • Incorrect status filters
        • Department/category filters
        • Date range limitations
        • Data corruption (rare)
        """
        self.story.append(Paragraph(data_issues_text, self.styles['Normal']))
        
        self.story.append(PageBreak())
    
    def add_appendices(self):
        """Add appendices"""
        # Appendix A: Common Issues
        self.story.append(Paragraph("Appendix A: Common Issues Quick Reference", self.styles['ChapterHeading']))
        
        quick_ref_data = [
            ["Issue", "Quick Solution", "Reference Section"],
            ["Can't log in", "Reset password, check account status", "14.1"],
            ["No email notifications", "Check SMTP settings", "9.1, 14.1"],
            ["Slow performance", "Check server resources, database", "13.2, 14.1"],
            ["Missing work orders", "Check filters and permissions", "14.1"],
            ["Reports not generating", "Verify data range and permissions", "11.2, 14.1"],
            ["Users can't create WO", "Check role permissions", "12.1"],
            ["Approval workflow stuck", "Review approval delegation rules", "6.1"],
            ["Wrong assignment group", "Check category assignment rules", "5.1, 7.1"],
        ]
        
        quick_ref_table = Table(quick_ref_data, colWidths=[2*inch, 2.5*inch, 1.5*inch])
        quick_ref_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.pink),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(quick_ref_table)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Appendix B: Best Practices
        self.story.append(Paragraph("Appendix B: Configuration Best Practices", self.styles['ChapterHeading']))
        
        best_practices_text = """
        <b>User Management Best Practices:</b>
        • Use consistent naming conventions
        • Regularly review and update user accounts
        • Implement strong password policies
        • Document role assignments and responsibilities
        • Conduct quarterly access reviews
        
        <b>Work Order Configuration Best Practices:</b>
        • Keep categories simple and intuitive
        • Set realistic SLA timeframes
        • Use consistent priority definitions
        • Regularly review and update workflows
        • Train users on proper categorization
        
        <b>Email and Notification Best Practices:</b>
        • Don't over-notify - balance information with noise
        • Use clear, actionable subject lines
        • Include relevant work order details
        • Test all notification rules thoroughly
        • Provide unsubscribe options where appropriate
        
        <b>Security Best Practices:</b>
        • Implement least privilege access
        • Regular security updates and patches
        • Monitor user activity and access patterns
        • Maintain current backups and test recovery
        • Document all security procedures
        
        <b>Maintenance Best Practices:</b>
        • Follow regular maintenance schedules
        • Monitor system performance continuously
        • Keep documentation current
        • Plan for capacity growth
        • Train multiple staff on system administration
        """
        self.story.append(Paragraph(best_practices_text, self.styles['Normal']))
        
        # Contact Information
        self.story.append(Spacer(1, 0.5*inch))
        contact_text = """
        <b>Technical Support Contact:</b>
        
        For technical support and additional assistance:
        • Email: support@rubixsolutions.com
        • Documentation: https://docs.cube-pro.com
        • System Status: https://status.cube-pro.com
        
        <b>Emergency Contact:</b>
        For critical system issues outside business hours, 
        contact your designated system administrator or IT support team.
        """
        self.story.append(Paragraph(contact_text, self.styles['Note']))
    
    def generate_pdf(self, filename="CUBE_PRO_Admin_Guide.pdf"):
        """Generate the complete PDF guide"""
        # Create the PDF document
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Add all content sections
        self.add_title_page()
        self.add_table_of_contents()
        self.add_introduction()
        self.add_initial_setup()
        self.add_user_management()
        self.add_department_management()
        self.add_assignment_groups()
        self.add_approval_delegation()
        self.add_work_order_categories()
        self.add_status_configuration()
        self.add_email_configuration()
        self.add_notification_rules()
        self.add_reporting_setup()
        self.add_security_access_control()
        self.add_system_maintenance()
        self.add_troubleshooting()
        self.add_appendices()
        
        # Build the PDF
        self.doc.build(self.story)
        print(f"Admin Guide generated successfully: {filename}")
        return filename

def main():
    """Main function to generate the admin guide"""
    generator = AdminGuideGenerator()
    
    # Generate the PDF
    pdf_file = generator.generate_pdf()
    
    print(f"✅ CUBE - PRO Admin Guide generated successfully!")
    print(f"📄 File location: {os.path.abspath(pdf_file)}")
    print(f"📊 Guide includes:")
    print("   • Complete system configuration steps")
    print("   • User and department management")
    print("   • Work order workflow setup")
    print("   • Email and notification configuration")
    print("   • Security and access control")
    print("   • Troubleshooting and maintenance")
    print("   • Best practices and quick reference")

if __name__ == "__main__":
    main()
