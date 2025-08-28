"""
Reporting Models
Database models for the reporting system
"""

from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Text
import json


class Report(db.Model):
    """Report model for storing report configurations"""
    
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # active, draft, archived
    
    # Data configuration
    data_source = db.Column(db.String(100))  # Table name
    columns = db.Column(db.Text)  # JSON string of selected columns
    filters = db.Column(db.Text)  # JSON string of filter conditions
    visualizations = db.Column(db.Text)  # JSON string of chart configurations
    
    # Metadata
    tags = db.Column(db.String(200))
    template_type = db.Column(db.String(50), default='blank')
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_execution = db.Column(db.DateTime)
    execution_count = db.Column(db.Integer, default=0)
    
    # Relationships
    creator = db.relationship('User', backref='reports')
    executions = db.relationship('ReportExecution', backref='report', cascade='all, delete-orphan')
    schedules = db.relationship('ReportSchedule', backref='report', cascade='all, delete-orphan')
    shares = db.relationship('ReportShare', backref='report', cascade='all, delete-orphan')
    
    @property
    def columns_list(self):
        """Get columns as a list"""
        if self.columns:
            try:
                return json.loads(self.columns)
            except:
                return ['*']
        return ['*']
    
    @columns_list.setter
    def columns_list(self, value):
        """Set columns from a list"""
        self.columns = json.dumps(value) if value else None
    
    @property
    def filters_list(self):
        """Get filters as a list"""
        if self.filters:
            try:
                return json.loads(self.filters)
            except:
                return []
        return []
    
    @filters_list.setter
    def filters_list(self, value):
        """Set filters from a list"""
        self.filters = json.dumps(value) if value else None
    
    @property
    def visualizations_dict(self):
        """Get visualizations as a dictionary"""
        if self.visualizations:
            try:
                return json.loads(self.visualizations)
            except:
                return {}
        return {}
    
    @visualizations_dict.setter
    def visualizations_dict(self, value):
        """Set visualizations from a dictionary"""
        self.visualizations = json.dumps(value) if value else None
    
    @property
    def is_scheduled(self):
        """Check if report has active schedules"""
        return any(schedule.is_active for schedule in self.schedules)
    
    def __repr__(self):
        return f'<Report {self.name}>'


class ReportExecution(db.Model):
    """Model for tracking report executions"""
    
    __tablename__ = 'report_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    executed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Execution details
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)  # completed, failed, running
    execution_time = db.Column(db.Float)  # Execution time in seconds
    row_count = db.Column(db.Integer)
    error_message = db.Column(db.Text)
    
    # Configuration snapshot
    config_snapshot = db.Column(db.Text)  # JSON snapshot of report config at execution time
    
    # Relationships
    executor = db.relationship('User')
    
    def __repr__(self):
        return f'<ReportExecution {self.id}: {self.status}>'


class ReportSchedule(db.Model):
    """Model for scheduled report executions"""
    
    __tablename__ = 'report_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    
    # Schedule configuration
    frequency = db.Column(db.String(20), nullable=False)  # once, daily, weekly, monthly, quarterly
    day_of_week = db.Column(db.String(10))  # For weekly schedules
    day_of_month = db.Column(db.Integer)  # For monthly schedules
    hour = db.Column(db.Integer, default=9)  # Hour of day (0-23)
    minute = db.Column(db.Integer, default=0)  # Minute of hour (0-59)
    
    # Output configuration
    export_format = db.Column(db.String(10), default='csv')  # csv, excel, pdf
    email_recipients = db.Column(db.Text)  # JSON array of email addresses
    include_data = db.Column(db.String(20), default='full')  # summary, full, filtered
    
    # Tracking
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    run_count = db.Column(db.Integer, default=0)
    
    @property
    def email_recipients_list(self):
        """Get email recipients as a list"""
        if self.email_recipients:
            try:
                return json.loads(self.email_recipients)
            except:
                return []
        return []
    
    @email_recipients_list.setter
    def email_recipients_list(self, value):
        """Set email recipients from a list"""
        self.email_recipients = json.dumps(value) if value else None
    
    def __repr__(self):
        return f'<ReportSchedule {self.id}: {self.frequency}>'


class ReportShare(db.Model):
    """Model for shared reports"""
    
    __tablename__ = 'report_shares'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    shared_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Share configuration
    share_type = db.Column(db.String(20), nullable=False)  # link, email, internal
    share_token = db.Column(db.String(100), unique=True)  # Unique token for public links
    permissions = db.Column(db.String(20), default='view')  # view, execute, edit
    
    # Recipients and message
    recipients = db.Column(db.Text)  # JSON array or text list
    message = db.Column(db.Text)
    
    # Access tracking
    is_active = db.Column(db.Boolean, default=True)
    access_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime)
    
    # Expiration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    sharer = db.relationship('User')
    
    @property
    def is_expired(self):
        """Check if the share has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    @property
    def recipients_list(self):
        """Get recipients as a list"""
        if self.recipients:
            try:
                return json.loads(self.recipients)
            except:
                return self.recipients.split(',') if self.recipients else []
        return []
    
    @recipients_list.setter
    def recipients_list(self, value):
        """Set recipients from a list"""
        self.recipients = json.dumps(value) if isinstance(value, list) else value
    
    def __repr__(self):
        return f'<ReportShare {self.id}: {self.share_type}>'