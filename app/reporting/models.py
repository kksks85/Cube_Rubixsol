"""
Reporting Engine Models
"""

from datetime import datetime, timezone
from app import db
import json

class SavedReport(db.Model):
    """Model for saving custom reports"""
    __tablename__ = 'saved_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Report Configuration (stored as JSON)
    config = db.Column(db.Text, nullable=False)  # JSON string of report configuration
    
    # Metadata
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(500))  # Comma-separated tags
    
    # Usage Statistics
    view_count = db.Column(db.Integer, default=0)
    last_executed = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    creator = db.relationship('User', backref='created_reports')
    schedules = db.relationship('ReportSchedule', backref='report', cascade='all, delete-orphan')
    
    def get_config(self):
        """Parse and return the JSON configuration"""
        return json.loads(self.config) if self.config else {}
    
    def set_config(self, config_dict):
        """Set the configuration from a dictionary"""
        self.config = json.dumps(config_dict)
    
    def increment_view_count(self):
        """Increment view count and update last executed time"""
        self.view_count += 1
        self.last_executed = datetime.now(timezone.utc)
        db.session.commit()
    
    def get_tags_list(self):
        """Get tags as a list"""
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []
    
    def __repr__(self):
        return f'<SavedReport {self.name}>'

class ReportSchedule(db.Model):
    """Model for scheduling automatic report generation"""
    __tablename__ = 'report_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('saved_reports.id'), nullable=False)
    
    # Schedule Configuration
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, quarterly
    email_recipients = db.Column(db.Text)  # JSON array of email addresses
    export_format = db.Column(db.String(20), default='csv')  # csv, excel, pdf
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    run_count = db.Column(db.Integer, default=0)
    
    # Metadata
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    creator = db.relationship('User', backref='report_schedules')
    
    def get_recipients_list(self):
        """Get email recipients as a list"""
        return json.loads(self.email_recipients) if self.email_recipients else []
    
    def set_recipients_list(self, recipients):
        """Set email recipients from a list"""
        self.email_recipients = json.dumps(recipients)
    
    def calculate_next_run(self):
        """Calculate the next run time based on frequency"""
        from dateutil.relativedelta import relativedelta
        
        if not self.last_run:
            base_time = datetime.now(timezone.utc)
        else:
            base_time = self.last_run
        
        if self.frequency == 'daily':
            self.next_run = base_time + relativedelta(days=1)
        elif self.frequency == 'weekly':
            self.next_run = base_time + relativedelta(weeks=1)
        elif self.frequency == 'monthly':
            self.next_run = base_time + relativedelta(months=1)
        elif self.frequency == 'quarterly':
            self.next_run = base_time + relativedelta(months=3)
    
    def __repr__(self):
        return f'<ReportSchedule {self.name}>'

class ReportExecutionLog(db.Model):
    """Model for logging report executions"""
    __tablename__ = 'report_execution_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('saved_reports.id'))
    schedule_id = db.Column(db.Integer, db.ForeignKey('report_schedules.id'), nullable=True)
    
    # Execution Details
    executed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    execution_time = db.Column(db.Float)  # Time taken in seconds
    row_count = db.Column(db.Integer)
    export_format = db.Column(db.String(20))
    file_size = db.Column(db.Integer)  # File size in bytes
    
    # Status
    status = db.Column(db.String(20), default='success')  # success, error, timeout
    error_message = db.Column(db.Text)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    executed_by = db.relationship('User', backref='report_executions')
    report = db.relationship('SavedReport', backref='execution_logs')
    schedule = db.relationship('ReportSchedule', backref='execution_logs')
    
    def __repr__(self):
        return f'<ReportExecutionLog {self.id}>'
