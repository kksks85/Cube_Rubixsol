#!/usr/bin/env python3
"""
CUBE - PRO Quick Reference Card Generator
Creates a compact reference card for administrators
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

class QuickReferenceGenerator:
    def __init__(self):
        self.doc = None
        self.story = []
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='RefTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='RefSection',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=10,
            textColor=colors.darkgreen,
            backColor=colors.lightgreen,
            borderWidth=1,
            borderColor=colors.darkgreen,
            borderPadding=3
        ))
        
        # Compact style
        self.styles.add(ParagraphStyle(
            name='Compact',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=3,
            leading=11
        ))
    
    def generate_quick_reference(self, filename="CUBE_PRO_Quick_Reference.pdf"):
        """Generate the quick reference card"""
        # Create the PDF document
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        # Title
        self.story.append(Paragraph("CUBE - PRO Quick Reference Card", self.styles['RefTitle']))
        self.story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", self.styles['Compact']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Essential URLs and Access
        self.story.append(Paragraph("🔗 System Access", self.styles['RefSection']))
        access_data = [
            ["Login URL:", "http://your-server:5000"],
            ["Admin Username:", "admin (change after first login)"],
            ["Configuration Path:", "Main Menu → Configuration"],
            ["Reports Path:", "Main Menu → Reports"],
            ["Support Email:", "support@rubixsolutions.com"],
        ]
        
        access_table = Table(access_data, colWidths=[1.5*inch, 3.5*inch])
        access_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        self.story.append(access_table)
        self.story.append(Spacer(1, 0.1*inch))
        
        # Quick Setup Checklist
        self.story.append(Paragraph("✅ First-Time Setup Checklist", self.styles['RefSection']))
        checklist_text = """
        ☐ 1. Change default admin password
        ☐ 2. Create departments (Configuration → User Management → Departments)
        ☐ 3. Create user accounts (Configuration → User Management → Users)
        ☐ 4. Set up assignment groups (Configuration → User Management → Assignment Groups)
        ☐ 5. Configure work order categories (Configuration → Work Orders → Categories)
        ☐ 6. Set up priority levels (Configuration → Work Orders → Priorities)
        ☐ 7. Configure email settings (Configuration → Email → SMTP Settings)
        ☐ 8. Set up notification rules (Configuration → Email → Notification Rules)
        ☐ 9. Test work order creation process
        ☐ 10. Train users and provide access
        """
        self.story.append(Paragraph(checklist_text, self.styles['Compact']))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Common Tasks
        self.story.append(Paragraph("⚡ Common Administrative Tasks", self.styles['RefSection']))
        
        common_tasks_data = [
            ["Task", "Navigation Path", "Key Notes"],
            ["Add New User", "Config → User Mgmt → Users → Add", "Assign role and department"],
            ["Reset Password", "Config → User Mgmt → Users → Edit User", "Generate temporary password"],
            ["Create Department", "Config → User Mgmt → Departments → Add", "Assign manager"],
            ["Add Work Category", "Config → Work Orders → Categories", "Set SLA and assignment group"],
            ["Configure Email", "Config → Email → SMTP Settings", "Test connection before saving"],
            ["View System Logs", "Config → System → Audit Logs", "Monitor user activity"],
            ["Generate Reports", "Reports → Report Builder", "Schedule automated delivery"],
            ["Backup System", "Config → System → Backup", "Verify backup integrity"],
        ]
        
        tasks_table = Table(common_tasks_data, colWidths=[1.3*inch, 1.8*inch, 1.9*inch])
        tasks_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        self.story.append(tasks_table)
        self.story.append(Spacer(1, 0.1*inch))
        
        # User Roles Quick Reference
        self.story.append(Paragraph("👥 User Roles & Permissions", self.styles['RefSection']))
        
        roles_data = [
            ["Role", "Key Permissions", "Typical Users"],
            ["Admin", "Full system access, user management, configuration", "IT administrators, system managers"],
            ["Manager", "Approve work orders, view reports, manage team", "Department heads, supervisors"],
            ["User", "Create/update work orders, view assigned tasks", "Employees, technicians"],
            ["Viewer", "Read-only access to work orders and reports", "Executives, auditors"],
        ]
        
        roles_table = Table(roles_data, colWidths=[0.8*inch, 2.2*inch, 2*inch])
        roles_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        self.story.append(roles_table)
        self.story.append(Spacer(1, 0.1*inch))
        
        # Work Order Status Flow
        self.story.append(Paragraph("🔄 Work Order Status Flow", self.styles['RefSection']))
        status_text = """
        Draft → Submitted → Approved → In Progress → Completed → Closed
        
        Alternative flows:
        • Draft → Cancelled (if not needed)
        • Submitted → Rejected → Draft (if approval denied)
        • In Progress → On Hold → In Progress (if temporarily suspended)
        """
        self.story.append(Paragraph(status_text, self.styles['Compact']))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Emergency Procedures
        self.story.append(Paragraph("🚨 Emergency Procedures", self.styles['RefSection']))
        
        emergency_data = [
            ["Situation", "Immediate Action", "Follow-up"],
            ["System Down", "Check server status, restart if needed", "Review logs, contact support"],
            ["Database Issues", "Stop application, backup current state", "Run integrity check, restore if needed"],
            ["User Locked Out", "Reset account in User Management", "Review security logs"],
            ["Email Not Working", "Check SMTP settings and test", "Verify server connectivity"],
            ["Performance Issues", "Check server resources", "Analyze logs, optimize database"],
        ]
        
        emergency_table = Table(emergency_data, colWidths=[1.2*inch, 1.8*inch, 2*inch])
        emergency_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, -1), colors.pink),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        self.story.append(emergency_table)
        self.story.append(Spacer(1, 0.1*inch))
        
        # Key Configuration Files and Settings
        self.story.append(Paragraph("⚙️ Key Settings & Configurations", self.styles['RefSection']))
        
        config_data = [
            ["Setting", "Location", "Purpose"],
            ["Password Policy", "Config → Security → Password Rules", "Set complexity requirements"],
            ["Session Timeout", "Config → Security → Session Settings", "Auto-logout timing"],
            ["Email Templates", "Config → Email → Templates", "Customize notification content"],
            ["Report Schedules", "Reports → Scheduled Reports", "Automate report delivery"],
            ["Audit Logging", "Config → System → Audit Settings", "Track user activities"],
            ["Backup Schedule", "Config → System → Backup", "Automated data protection"],
        ]
        
        config_table = Table(config_data, colWidths=[1.3*inch, 1.7*inch, 2*inch])
        config_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, -1), colors.moccasin),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        self.story.append(config_table)
        self.story.append(Spacer(1, 0.1*inch))
        
        # Footer
        footer_text = """
        <b>💡 Pro Tips:</b>
        • Always test changes in a non-production environment first
        • Keep regular backups before making major configuration changes
        • Document all customizations and configuration changes
        • Review user access permissions quarterly
        • Monitor system performance and logs regularly
        
        <b>📞 Support:</b> For technical assistance, contact support@rubixsolutions.com
        """
        self.story.append(Paragraph(footer_text, self.styles['Compact']))
        
        # Build the PDF
        self.doc.build(self.story)
        print(f"Quick Reference Card generated successfully: {filename}")
        return filename

def main():
    """Main function to generate the quick reference"""
    generator = QuickReferenceGenerator()
    
    # Generate the quick reference
    ref_card = generator.generate_quick_reference()
    
    print(f"✅ CUBE - PRO Quick Reference Card generated successfully!")
    print(f"📄 File location: {os.path.abspath(ref_card)}")
    print(f"📋 Quick Reference includes:")
    print("   • Essential system access information")
    print("   • First-time setup checklist")
    print("   • Common administrative tasks")
    print("   • User roles and permissions")
    print("   • Emergency procedures")
    print("   • Key configuration settings")

if __name__ == "__main__":
    main()
