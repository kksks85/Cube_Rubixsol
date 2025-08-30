"""
Database migration script for Integration models
Run this script to create the integration tables in your database.
"""

import json
from app import create_app, db
from app.integrations.models import IntegrationProvider, Integration, IntegrationMapping, IntegrationSyncLog, IntegrationWebhook

def create_integration_tables():
    """Create integration tables and populate default providers."""
    app = create_app()
    
    with app.app_context():
        # Create tables
        print("Creating integration tables...")
        db.create_all()
        
        # Create default integration providers if they don't exist
        providers_data = [
            {
                'name': 'active_directory',
                'display_name': 'Active Directory',
                'provider_type': 'LDAP',
                'description': 'Microsoft Active Directory / LDAP integration for user and group synchronization',
                'is_active': True,
                'is_built_in': True,
                'configuration_schema': json.dumps({
                    'server': {'type': 'string', 'required': True, 'description': 'LDAP server address'},
                    'port': {'type': 'integer', 'default': 389, 'description': 'LDAP server port'},
                    'use_ssl': {'type': 'boolean', 'default': False, 'description': 'Use SSL connection'},
                    'bind_dn': {'type': 'string', 'required': True, 'description': 'Bind DN for authentication'},
                    'bind_password': {'type': 'string', 'required': True, 'description': 'Bind password'},
                    'base_dn': {'type': 'string', 'required': True, 'description': 'Base DN for searches'},
                    'user_search_base': {'type': 'string', 'description': 'User search base DN'},
                    'group_search_base': {'type': 'string', 'description': 'Group search base DN'},
                    'user_filter': {'type': 'string', 'default': '(objectClass=user)', 'description': 'User search filter'},
                    'group_filter': {'type': 'string', 'default': '(objectClass=group)', 'description': 'Group search filter'}
                })
            },
            {
                'name': 'jira',
                'display_name': 'Atlassian JIRA',
                'provider_type': 'REST',
                'description': 'JIRA issue tracking system integration for work order synchronization',
                'is_active': True,
                'is_built_in': True,
                'configuration_schema': json.dumps({
                    'base_url': {'type': 'string', 'required': True, 'description': 'JIRA base URL (e.g., https://company.atlassian.net)'},
                    'username': {'type': 'string', 'required': True, 'description': 'JIRA username/email'},
                    'api_token': {'type': 'string', 'required': True, 'description': 'JIRA API token'},
                    'project_key': {'type': 'string', 'required': True, 'description': 'JIRA project key'},
                    'issue_type': {'type': 'string', 'default': 'Task', 'description': 'Default issue type for work orders'},
                    'sync_comments': {'type': 'boolean', 'default': True, 'description': 'Sync comments between systems'},
                    'sync_attachments': {'type': 'boolean', 'default': False, 'description': 'Sync file attachments'},
                    'custom_fields': {'type': 'object', 'description': 'Custom field mappings'}
                })
            },
            {
                'name': 'generic_rest',
                'display_name': 'Generic REST API',
                'provider_type': 'REST',
                'description': 'Generic REST API integration for custom third-party services',
                'is_active': True,
                'is_built_in': True,
                'configuration_schema': json.dumps({
                    'base_url': {'type': 'string', 'required': True, 'description': 'API base URL'},
                    'auth_method': {'type': 'string', 'enum': ['none', 'basic', 'bearer', 'oauth2'], 'default': 'none', 'description': 'Authentication method'},
                    'username': {'type': 'string', 'description': 'Username for basic auth'},
                    'password': {'type': 'string', 'description': 'Password for basic auth'},
                    'api_key': {'type': 'string', 'description': 'API key for token auth'},
                    'client_id': {'type': 'string', 'description': 'OAuth2 client ID'},
                    'client_secret': {'type': 'string', 'description': 'OAuth2 client secret'},
                    'oauth_url': {'type': 'string', 'description': 'OAuth2 token URL'},
                    'headers': {'type': 'object', 'description': 'Custom HTTP headers'},
                    'timeout': {'type': 'integer', 'default': 30, 'description': 'Request timeout in seconds'}
                })
            },
            {
                'name': 'generic_soap',
                'display_name': 'Generic SOAP Web Service',
                'provider_type': 'SOAP',
                'description': 'Generic SOAP web service integration',
                'is_active': True,
                'is_built_in': True,
                'configuration_schema': json.dumps({
                    'wsdl_url': {'type': 'string', 'required': True, 'description': 'WSDL URL'},
                    'service_name': {'type': 'string', 'description': 'SOAP service name'},
                    'port_name': {'type': 'string', 'description': 'SOAP port name'},
                    'username': {'type': 'string', 'description': 'Username for authentication'},
                    'password': {'type': 'string', 'description': 'Password for authentication'},
                    'timeout': {'type': 'integer', 'default': 30, 'description': 'Request timeout in seconds'}
                })
            }
        ]
        
        print("Creating default integration providers...")
        for provider_data in providers_data:
            existing_provider = IntegrationProvider.query.filter_by(name=provider_data['name']).first()
            if not existing_provider:
                provider = IntegrationProvider(**provider_data)
                db.session.add(provider)
                print(f"  Created provider: {provider_data['display_name']}")
            else:
                print(f"  Provider already exists: {provider_data['display_name']}")
        
        try:
            db.session.commit()
            print("✅ Integration tables created successfully!")
            print("✅ Default providers created successfully!")
            
            # Print summary
            provider_count = IntegrationProvider.query.count()
            print(f"\nSummary:")
            print(f"  - Integration providers: {provider_count}")
            print(f"  - Integration tables created: 5")
            print(f"    • integration_providers")
            print(f"    • integrations")
            print(f"    • integration_mappings")
            print(f"    • integration_sync_logs")
            print(f"    • integration_webhooks")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating integration tables: {str(e)}")
            raise
        
        print("\n🎉 Integration module setup complete!")
        print("You can now access the integration management at: /integrations")

if __name__ == '__main__':
    create_integration_tables()
