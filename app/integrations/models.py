"""
Integration Models
Database models for third-party integrations
"""

from datetime import datetime, timezone
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import json


class IntegrationProvider(db.Model):
    """Available integration providers"""
    __tablename__ = 'integration_providers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    provider_type = db.Column(db.String(50), nullable=False)  # 'REST', 'SOAP', 'LDAP', 'DATABASE'
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    is_built_in = db.Column(db.Boolean, default=False)  # Built-in providers like AD, JIRA
    configuration_schema = db.Column(db.Text)  # JSON schema for configuration
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    integrations = db.relationship('Integration', backref='provider', lazy='dynamic')
    
    def __repr__(self):
        return f'<IntegrationProvider {self.name}>'


class Integration(db.Model):
    """Configured integrations with external systems"""
    __tablename__ = 'integrations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Provider relationship
    provider_id = db.Column(db.Integer, db.ForeignKey('integration_providers.id'), nullable=False)
    
    # Configuration
    configuration = db.Column(db.Text)  # JSON configuration
    credentials = db.Column(db.Text)   # Encrypted credentials
    
    # Status and monitoring
    is_enabled = db.Column(db.Boolean, default=True)
    last_sync_at = db.Column(db.DateTime)
    last_error = db.Column(db.Text)
    sync_frequency = db.Column(db.Integer, default=60)  # minutes
    
    # Audit
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    created_by = db.relationship('User', backref='created_integrations')
    sync_logs = db.relationship('IntegrationSyncLog', backref='integration', 
                               lazy='dynamic', cascade='all, delete-orphan')
    mappings = db.relationship('IntegrationMapping', backref='integration', 
                              lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def config_dict(self):
        """Get configuration as dictionary"""
        if self.configuration:
            return json.loads(self.configuration)
        return {}
    
    @config_dict.setter
    def config_dict(self, value):
        """Set configuration from dictionary"""
        self.configuration = json.dumps(value)
    
    @property
    def credentials_dict(self):
        """Get credentials as dictionary (encrypted)"""
        if self.credentials:
            return json.loads(self.credentials)
        return {}
    
    @credentials_dict.setter
    def credentials_dict(self, value):
        """Set credentials from dictionary (will be encrypted)"""
        self.credentials = json.dumps(value)
    
    @property
    def status(self):
        """Get integration status"""
        if not self.is_enabled:
            return 'DISABLED'
        elif self.last_error:
            return 'ERROR'
        elif self.last_sync_at:
            return 'ACTIVE'
        else:
            return 'PENDING'
    
    def __repr__(self):
        return f'<Integration {self.name}>'


class IntegrationMapping(db.Model):
    """Field mappings between local and external systems"""
    __tablename__ = 'integration_mappings'
    
    id = db.Column(db.Integer, primary_key=True)
    integration_id = db.Column(db.Integer, db.ForeignKey('integrations.id'), nullable=False)
    
    # Mapping details
    local_entity = db.Column(db.String(100), nullable=False)  # 'user', 'workorder', 'incident'
    local_field = db.Column(db.String(100), nullable=False)
    external_entity = db.Column(db.String(100), nullable=False)
    external_field = db.Column(db.String(100), nullable=False)
    
    # Transformation
    transformation_type = db.Column(db.String(50), default='DIRECT')  # 'DIRECT', 'LOOKUP', 'FORMULA'
    transformation_config = db.Column(db.Text)  # JSON config for transformations
    
    # Sync direction
    sync_direction = db.Column(db.String(20), default='BIDIRECTIONAL')  # 'INBOUND', 'OUTBOUND', 'BIDIRECTIONAL'
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<IntegrationMapping {self.local_entity}.{self.local_field} -> {self.external_entity}.{self.external_field}>'


class IntegrationSyncLog(db.Model):
    """Log entries for integration synchronization"""
    __tablename__ = 'integration_sync_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    integration_id = db.Column(db.Integer, db.ForeignKey('integrations.id'), nullable=False)
    
    # Sync details
    sync_type = db.Column(db.String(50), nullable=False)  # 'MANUAL', 'SCHEDULED', 'WEBHOOK'
    operation = db.Column(db.String(50), nullable=False)  # 'CREATE', 'UPDATE', 'DELETE', 'SYNC'
    entity_type = db.Column(db.String(100))  # 'user', 'workorder', etc.
    entity_id = db.Column(db.String(100))    # External system ID
    
    # Status
    status = db.Column(db.String(20), nullable=False)  # 'SUCCESS', 'ERROR', 'WARNING'
    message = db.Column(db.Text)
    error_details = db.Column(db.Text)
    
    # Performance
    duration_ms = db.Column(db.Integer)
    records_processed = db.Column(db.Integer, default=0)
    records_success = db.Column(db.Integer, default=0)
    records_error = db.Column(db.Integer, default=0)
    
    # Audit
    triggered_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    triggered_by = db.relationship('User', backref='integration_sync_logs')
    
    def __repr__(self):
        return f'<IntegrationSyncLog {self.integration.name} - {self.operation} - {self.status}>'


class IntegrationWebhook(db.Model):
    """Webhook endpoints for real-time integration"""
    __tablename__ = 'integration_webhooks'
    
    id = db.Column(db.Integer, primary_key=True)
    integration_id = db.Column(db.Integer, db.ForeignKey('integrations.id'), nullable=False)
    
    # Webhook configuration
    webhook_url = db.Column(db.String(500), nullable=False)
    secret_key = db.Column(db.String(255))  # For webhook validation
    events = db.Column(db.Text)  # JSON array of events to trigger webhook
    
    # HTTP configuration
    http_method = db.Column(db.String(10), default='POST')
    headers = db.Column(db.Text)  # JSON object of HTTP headers
    payload_template = db.Column(db.Text)  # Template for webhook payload
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_triggered_at = db.Column(db.DateTime)
    last_error = db.Column(db.Text)
    
    # Audit
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    integration = db.relationship('Integration', backref='webhooks')
    created_by = db.relationship('User', backref='created_webhooks')
    
    @property
    def events_list(self):
        """Get events as list"""
        if self.events:
            return json.loads(self.events)
        return []
    
    @events_list.setter
    def events_list(self, value):
        """Set events from list"""
        self.events = json.dumps(value)
    
    @property
    def headers_dict(self):
        """Get headers as dictionary"""
        if self.headers:
            return json.loads(self.headers)
        return {}
    
    @headers_dict.setter
    def headers_dict(self, value):
        """Set headers from dictionary"""
        self.headers = json.dumps(value)
    
    def __repr__(self):
        return f'<IntegrationWebhook {self.integration.name} -> {self.webhook_url}>'
