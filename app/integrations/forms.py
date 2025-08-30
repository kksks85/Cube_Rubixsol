"""
Integration Forms
Forms for managing third-party integrations
"""

from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SelectField, BooleanField, 
                     IntegerField, PasswordField, HiddenField, FieldList, FormField)
from wtforms.validators import DataRequired, Length, URL, Optional, NumberRange
from wtforms.widgets import TextArea


class IntegrationProviderForm(FlaskForm):
    """Form for creating/editing integration providers"""
    name = StringField('Provider Name', validators=[DataRequired(), Length(1, 100)])
    display_name = StringField('Display Name', validators=[DataRequired(), Length(1, 100)])
    provider_type = SelectField('Provider Type', 
                               choices=[('REST', 'REST API'), ('SOAP', 'SOAP Web Service'), 
                                       ('LDAP', 'LDAP/Active Directory'), ('DATABASE', 'Database Connection')],
                               validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 500)])
    configuration_schema = TextAreaField('Configuration Schema (JSON)', 
                                       validators=[Optional()],
                                       widget=TextArea(),
                                       render_kw={"rows": 10, "placeholder": "Enter JSON schema for configuration fields"})
    is_active = BooleanField('Active', default=True)
    is_built_in = BooleanField('Built-in Provider', default=False)


class IntegrationForm(FlaskForm):
    """Form for creating/editing integrations"""
    name = StringField('Integration Name', validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 500)])
    provider_id = SelectField('Provider', coerce=int, validators=[DataRequired()])
    
    # Connection Configuration
    endpoint_url = StringField('Endpoint URL', validators=[Optional(), URL()],
                              render_kw={"placeholder": "https://api.example.com"})
    base_url = StringField('Base URL', validators=[Optional(), URL()])
    
    # Authentication Configuration
    auth_method = SelectField('Authentication Method', 
                             choices=[('none', 'None'), ('basic', 'Basic Auth'), 
                                    ('bearer', 'Bearer Token'), ('api_key', 'API Key'),
                                    ('oauth2', 'OAuth 2.0')],
                             default='none')
    username = StringField('Username', validators=[Optional(), Length(0, 100)])
    password = PasswordField('Password', validators=[Optional()])
    api_token = StringField('API Token', validators=[Optional(), Length(0, 255)])
    api_key = StringField('API Key', validators=[Optional(), Length(0, 255)])
    token = StringField('Access Token', validators=[Optional(), Length(0, 500)])
    client_id = StringField('Client ID', validators=[Optional(), Length(0, 255)])
    client_secret = StringField('Client Secret', validators=[Optional(), Length(0, 255)])
    
    # Advanced configuration
    configuration = TextAreaField('Additional Configuration (JSON)', 
                                 validators=[Optional()],
                                 widget=TextArea(),
                                 render_kw={"rows": 8, "placeholder": "Enter JSON configuration"})
    
    # Sync settings
    sync_frequency = IntegerField('Sync Frequency (minutes)', 
                                 validators=[Optional(), NumberRange(min=1, max=10080)], 
                                 default=60)
    auto_sync = BooleanField('Enable Auto Sync', default=True)
    is_enabled = BooleanField('Enabled', default=True)


class ActiveDirectoryForm(FlaskForm):
    """Specialized form for Active Directory integration"""
    name = StringField('Integration Name', validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 500)])
    sync_frequency = IntegerField('Sync Frequency (minutes)', 
                                 validators=[Optional(), NumberRange(min=15, max=10080)], 
                                 default=60)
    
    # LDAP Server Configuration
    server = StringField('LDAP Server', validators=[DataRequired(), Length(1, 200)],
                        render_kw={"placeholder": "ldap.company.com or 192.168.1.100"})
    port = IntegerField('Port', validators=[DataRequired(), NumberRange(min=1, max=65535)], 
                       default=389)
    use_ssl = BooleanField('Use SSL', default=False)
    start_tls = BooleanField('Start TLS', default=False)
    
    # Authentication
    bind_dn = StringField('Bind DN', validators=[DataRequired(), Length(1, 200)],
                         render_kw={"placeholder": "CN=admin,DC=company,DC=com"})
    bind_password = PasswordField('Bind Password', validators=[DataRequired()])
    
    # Search Configuration
    base_dn = StringField('Base DN', validators=[DataRequired(), Length(1, 200)],
                         render_kw={"placeholder": "DC=company,DC=com"})
    user_search_base = StringField('User Search Base', validators=[Optional(), Length(0, 200)],
                                  render_kw={"placeholder": "OU=Users,DC=company,DC=com"})
    group_search_base = StringField('Group Search Base', validators=[Optional(), Length(0, 200)],
                                   render_kw={"placeholder": "OU=Groups,DC=company,DC=com"})
    user_filter = StringField('User Filter', validators=[Optional(), Length(0, 200)],
                             default="(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))")
    group_filter = StringField('Group Filter', validators=[Optional(), Length(0, 200)],
                              default="(objectClass=group)")
    
    # Sync Options
    sync_users = BooleanField('Sync Users', default=True)
    sync_groups = BooleanField('Sync Groups', default=True)
    auto_sync = BooleanField('Enable Auto Sync', default=True)
    create_missing_users = BooleanField('Create Missing Users', default=True)
    update_existing_users = BooleanField('Update Existing Users', default=True)
    
    is_enabled = BooleanField('Enabled', default=True)


class JiraForm(FlaskForm):
    """Specialized form for JIRA integration"""
    name = StringField('Integration Name', validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 500)])
    sync_frequency = IntegerField('Sync Frequency (minutes)', 
                                 validators=[Optional(), NumberRange(min=15, max=10080)], 
                                 default=60)
    
    # JIRA Configuration
    base_url = StringField('JIRA URL', validators=[DataRequired(), URL()],
                          render_kw={"placeholder": "https://your-company.atlassian.net"})
    username = StringField('Username/Email', validators=[DataRequired(), Length(1, 100)])
    api_token = StringField('API Token', validators=[DataRequired(), Length(1, 255)],
                           render_kw={"placeholder": "Get from JIRA Account Settings"})
    
    # Project settings
    project_key = StringField('Default Project Key', validators=[Optional(), Length(0, 20)],
                                 render_kw={"placeholder": "e.g., CUBE"})
    issue_type = SelectField('Default Issue Type', 
                            choices=[('Task', 'Task'), ('Bug', 'Bug'), ('Story', 'Story'), 
                                   ('Epic', 'Epic'), ('Sub-task', 'Sub-task')],
                            default='Task')
    default_assignee = StringField('Default Assignee', validators=[Optional(), Length(0, 100)],
                                  render_kw={"placeholder": "username or email"})
    issue_type_mapping = TextAreaField('Issue Type Mapping (JSON)', 
                                      validators=[Optional()],
                                      default='{"workorder": "Task", "incident": "Bug", "request": "Story"}',
                                      render_kw={"rows": 4, "placeholder": "Map local types to JIRA issue types"})
    
    # Field mapping
    priority_mapping = TextAreaField('Priority Mapping (JSON)', 
                                    validators=[Optional()],
                                    default='{"LOW": "Low", "MEDIUM": "Medium", "HIGH": "High", "URGENT": "Highest"}',
                                    render_kw={"rows": 3, "placeholder": "Map local priorities to JIRA priorities"})
    
    # Sync settings
    create_jira_issues = BooleanField('Create JIRA Issues from Work Orders', default=True)
    update_jira_issues = BooleanField('Update JIRA Issues when Work Orders change', default=True)
    sync_wo_comments = BooleanField('Sync Work Order Comments to JIRA', default=True)
    sync_jira_updates = BooleanField('Sync JIRA Updates back to Work Orders', default=True)
    sync_jira_comments = BooleanField('Sync JIRA Comments back to Work Orders', default=True)
    sync_status_changes = BooleanField('Sync Status Changes', default=True)
    sync_attachments = BooleanField('Sync Attachments', default=False)
    auto_sync = BooleanField('Enable Automatic Synchronization', default=True)
    
    # Webhook configuration
    webhook_secret = StringField('Webhook Secret', validators=[Optional(), Length(0, 255)],
                                render_kw={"placeholder": "Optional webhook secret"})
    
    is_enabled = BooleanField('Enabled', default=True)


class IntegrationMappingForm(FlaskForm):
    """Form for field mapping configuration"""
    local_entity = SelectField('Local Entity', 
                              choices=[('user', 'User'), ('workorder', 'Work Order'), 
                                      ('incident', 'UAV Service Incident'), ('product', 'Product')],
                              validators=[DataRequired()])
    local_field = StringField('Local Field', validators=[DataRequired(), Length(1, 100)])
    external_entity = StringField('External Entity', validators=[DataRequired(), Length(1, 100)])
    external_field = StringField('External Field', validators=[DataRequired(), Length(1, 100)])
    
    transformation_type = SelectField('Transformation', 
                                     choices=[('DIRECT', 'Direct Mapping'), 
                                             ('LOOKUP', 'Lookup Table'), 
                                             ('FORMULA', 'Formula/Script')],
                                     default='DIRECT')
    transformation_config = TextAreaField('Transformation Config (JSON)', 
                                         validators=[Optional()],
                                         render_kw={"rows": 4})
    
    sync_direction = SelectField('Sync Direction',
                                choices=[('INBOUND', 'External → Local'), 
                                        ('OUTBOUND', 'Local → External'), 
                                        ('BIDIRECTIONAL', 'Both Directions')],
                                default='BIDIRECTIONAL')
    is_active = BooleanField('Active', default=True)


class IntegrationWebhookForm(FlaskForm):
    """Form for webhook configuration"""
    webhook_url = StringField('Webhook URL', validators=[DataRequired(), URL()])
    secret_key = StringField('Secret Key', validators=[Optional(), Length(0, 255)],
                            render_kw={"placeholder": "Optional secret for validation"})
    
    # Events
    events = TextAreaField('Events (JSON Array)', 
                          validators=[Optional()],
                          default='["workorder.created", "workorder.updated", "incident.created", "incident.updated"]',
                          render_kw={"rows": 3, "placeholder": "List of events to trigger webhook"})
    
    http_method = SelectField('HTTP Method', 
                             choices=[('POST', 'POST'), ('PUT', 'PUT'), ('PATCH', 'PATCH')],
                             default='POST')
    
    headers = TextAreaField('HTTP Headers (JSON)', 
                           validators=[Optional()],
                           default='{"Content-Type": "application/json"}',
                           render_kw={"rows": 3, "placeholder": "Additional HTTP headers"})
    
    payload_template = TextAreaField('Payload Template', 
                                    validators=[Optional()],
                                    render_kw={"rows": 8, "placeholder": "Custom payload template (uses Jinja2 syntax)"})
    
    is_active = BooleanField('Active', default=True)


class IntegrationTestForm(FlaskForm):
    """Form for testing integration connections"""
    integration_id = HiddenField()
    test_type = SelectField('Test Type',
                           choices=[('connection', 'Test Connection'), 
                                   ('auth', 'Test Authentication'),
                                   ('sync', 'Test Data Sync')],
                           default='connection')
    test_entity = StringField('Test Entity ID', validators=[Optional()],
                             render_kw={"placeholder": "Optional: specific entity to test"})


class BulkSyncForm(FlaskForm):
    """Form for bulk synchronization operations"""
    integration_id = HiddenField()
    sync_type = SelectField('Sync Type',
                           choices=[('users', 'Sync Users'), 
                                   ('workorders', 'Sync Work Orders'),
                                   ('incidents', 'Sync Incidents'),
                                   ('all', 'Sync All Entities')],
                           validators=[DataRequired()])
    force_update = BooleanField('Force Update Existing Records', default=False)
    dry_run = BooleanField('Dry Run (Preview Only)', default=True)
