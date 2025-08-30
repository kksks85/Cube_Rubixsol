"""
JIRA Integration Service
Handles synchronization with Atlassian JIRA
"""

import requests
import json
from base64 import b64encode
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import logging

from app import db
from app.models import WorkOrder, UAVServiceIncident, User, Priority
from app.integrations.services import IntegrationService

logger = logging.getLogger(__name__)


class JIRAService(IntegrationService):
    """JIRA integration service for issue tracking"""
    
    def __init__(self, integration):
        super().__init__(integration)
        self.jira_url = self.config.get('jira_url', '').rstrip('/')
        self.username = self.credentials.get('username')
        self.api_token = self.credentials.get('api_token')
        self.default_project = self.config.get('default_project')
        
        # Mappings
        self.issue_type_mapping = json.loads(self.config.get('issue_type_mapping', '{}'))
        self.priority_mapping = json.loads(self.config.get('priority_mapping', '{}'))
        
        # Sync settings
        self.auto_create_issues = self.config.get('auto_create_issues', True)
        self.sync_comments = self.config.get('sync_comments', True)
        self.sync_status_changes = self.config.get('sync_status_changes', True)
        
        # Set up session
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Set up JIRA authentication"""
        if self.username and self.api_token:
            # Use basic auth with API token
            auth_string = f"{self.username}:{self.api_token}"
            encoded_auth = b64encode(auth_string.encode()).decode()
            self.session.headers.update({
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test JIRA connection"""
        try:
            url = f"{self.jira_url}/rest/api/3/myself"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                user_info = response.json()
                return True, f"Connected as {user_info.get('displayName', 'Unknown User')}"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            elif response.status_code == 403:
                return False, "Authentication failed: Access denied"
            else:
                return False, f"Connection failed: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection error: {str(e)}"
        except requests.exceptions.Timeout as e:
            return False, f"Connection timeout: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def authenticate(self) -> Tuple[bool, str]:
        """Test JIRA authentication"""
        return self.test_connection()
    
    def sync_data(self, entity_type: str = None, force_update: bool = False) -> Dict[str, Any]:
        """Sync data with JIRA"""
        start_time = datetime.now()
        results = {
            'success': False,
            'message': '',
            'records_processed': 0,
            'records_success': 0,
            'records_error': 0,
            'errors': []
        }
        
        try:
            if entity_type == 'workorders' or entity_type is None:
                wo_results = self._sync_workorders(force_update)
                results['records_processed'] += wo_results['processed']
                results['records_success'] += wo_results['success']
                results['records_error'] += wo_results['errors']
                results['errors'].extend(wo_results['error_messages'])
            
            if entity_type == 'incidents' or entity_type is None:
                incident_results = self._sync_incidents(force_update)
                results['records_processed'] += incident_results['processed']
                results['records_success'] += incident_results['success']
                results['records_error'] += incident_results['errors']
                results['errors'].extend(incident_results['error_messages'])
            
            results['success'] = results['records_error'] == 0
            results['message'] = f"JIRA sync completed: {results['records_success']}/{results['records_processed']} successful"
            
        except Exception as e:
            results['message'] = f"JIRA sync failed: {str(e)}"
            results['errors'].append(str(e))
            self.handle_error('sync_data', e, entity_type)
        
        # Log the sync operation
        duration = (datetime.now() - start_time).total_seconds() * 1000
        self.log_sync(
            sync_type='SCHEDULED',
            operation='SYNC',
            status='SUCCESS' if results['success'] else 'ERROR',
            message=results['message'],
            error_details='; '.join(results['errors']) if results['errors'] else None,
            entity_type=entity_type or 'all',
            duration_ms=int(duration),
            records_processed=results['records_processed'],
            records_success=results['records_success'],
            records_error=results['records_error']
        )
        
        return results
    
    def _sync_workorders(self, force_update: bool = False) -> Dict[str, Any]:
        """Sync work orders with JIRA issues"""
        results = {
            'processed': 0,
            'success': 0,
            'errors': 0,
            'error_messages': []
        }
        
        try:
            # Get work orders that need to be synced
            workorders = WorkOrder.query.filter_by().all()  # Add your filter criteria
            results['processed'] = len(workorders)
            
            for workorder in workorders:
                try:
                    if self.auto_create_issues:
                        issue_result = self._create_or_update_jira_issue(workorder, 'workorder', force_update)
                        if issue_result['success']:
                            results['success'] += 1
                        else:
                            results['errors'] += 1
                            results['error_messages'].extend(issue_result['errors'])
                    else:
                        results['success'] += 1  # Skipped but not an error
                        
                except Exception as e:
                    results['errors'] += 1
                    error_msg = f"Error processing work order {workorder.id}: {str(e)}"
                    results['error_messages'].append(error_msg)
                    logger.error(error_msg)
                        
        except Exception as e:
            results['errors'] += 1
            error_msg = f"Error during work order sync: {str(e)}"
            results['error_messages'].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    def _sync_incidents(self, force_update: bool = False) -> Dict[str, Any]:
        """Sync UAV service incidents with JIRA issues"""
        results = {
            'processed': 0,
            'success': 0,
            'errors': 0,
            'error_messages': []
        }
        
        try:
            # Get incidents that need to be synced
            incidents = UAVServiceIncident.query.filter_by().all()  # Add your filter criteria
            results['processed'] = len(incidents)
            
            for incident in incidents:
                try:
                    if self.auto_create_issues:
                        issue_result = self._create_or_update_jira_issue(incident, 'incident', force_update)
                        if issue_result['success']:
                            results['success'] += 1
                        else:
                            results['errors'] += 1
                            results['error_messages'].extend(issue_result['errors'])
                    else:
                        results['success'] += 1  # Skipped but not an error
                        
                except Exception as e:
                    results['errors'] += 1
                    error_msg = f"Error processing incident {incident.id}: {str(e)}"
                    results['error_messages'].append(error_msg)
                    logger.error(error_msg)
                        
        except Exception as e:
            results['errors'] += 1
            error_msg = f"Error during incident sync: {str(e)}"
            results['error_messages'].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    def _create_or_update_jira_issue(self, entity, entity_type: str, force_update: bool = False) -> Dict[str, Any]:
        """Create or update a JIRA issue for an entity"""
        result = {
            'success': False,
            'jira_key': None,
            'errors': []
        }
        
        try:
            # Check if JIRA issue already exists
            jira_key = self._get_existing_jira_key(entity, entity_type)
            
            if jira_key and not force_update:
                # Issue exists and no force update
                result['success'] = True
                result['jira_key'] = jira_key
                return result
            
            # Prepare issue data
            issue_data = self._prepare_issue_data(entity, entity_type)
            
            if jira_key:
                # Update existing issue
                url = f"{self.jira_url}/rest/api/3/issue/{jira_key}"
                response = self.session.put(url, json={'fields': issue_data}, timeout=30)
                
                if response.status_code == 204:
                    result['success'] = True
                    result['jira_key'] = jira_key
                else:
                    result['errors'].append(f"Failed to update JIRA issue {jira_key}: {response.text}")
            else:
                # Create new issue
                create_data = {
                    'fields': issue_data
                }
                
                url = f"{self.jira_url}/rest/api/3/issue"
                response = self.session.post(url, json=create_data, timeout=30)
                
                if response.status_code == 201:
                    issue_info = response.json()
                    jira_key = issue_info['key']
                    result['success'] = True
                    result['jira_key'] = jira_key
                    
                    # Store JIRA key in entity (you may need to add a field for this)
                    self._store_jira_key(entity, entity_type, jira_key)
                else:
                    result['errors'].append(f"Failed to create JIRA issue: {response.text}")
                    
        except Exception as e:
            result['errors'].append(f"Error creating/updating JIRA issue: {str(e)}")
        
        return result
    
    def _prepare_issue_data(self, entity, entity_type: str) -> Dict[str, Any]:
        """Prepare JIRA issue data from entity"""
        issue_data = {
            'project': {'key': self.default_project}
        }
        
        if entity_type == 'workorder':
            # Map work order to JIRA issue
            issue_data.update({
                'summary': entity.title,
                'description': entity.description,
                'issuetype': {'name': self.issue_type_mapping.get('workorder', 'Task')},
            })
            
            # Map priority
            if hasattr(entity, 'priority') and entity.priority:
                jira_priority = self.priority_mapping.get(entity.priority.name, 'Medium')
                issue_data['priority'] = {'name': jira_priority}
            
            # Add assignee if available
            if entity.assigned_to_id and entity.assignee:
                # You may need to map local users to JIRA users
                issue_data['assignee'] = {'emailAddress': entity.assignee.email}
                
        elif entity_type == 'incident':
            # Map UAV service incident to JIRA issue
            issue_data.update({
                'summary': entity.title,
                'description': entity.description,
                'issuetype': {'name': self.issue_type_mapping.get('incident', 'Bug')},
            })
            
            # Map priority
            jira_priority = self.priority_mapping.get(entity.priority, 'Medium')
            issue_data['priority'] = {'name': jira_priority}
            
            # Add custom fields for UAV-specific data
            if hasattr(entity, 'uav_model') and entity.uav_model:
                issue_data['customfield_10001'] = entity.uav_model  # Example custom field
        
        return issue_data
    
    def _get_existing_jira_key(self, entity, entity_type: str) -> Optional[str]:
        """Get existing JIRA key for an entity"""
        # This would depend on how you store JIRA keys
        # You might add a jira_key field to your models
        # For now, return None to always create new issues
        return None
    
    def _store_jira_key(self, entity, entity_type: str, jira_key: str):
        """Store JIRA key in entity"""
        # Implementation depends on your data model
        # You might add a jira_key field to store this
        pass
    
    def create_jira_issue(self, title: str, description: str, issue_type: str = 'Task', 
                         priority: str = 'Medium', assignee: str = None) -> Tuple[bool, str, str]:
        """Create a JIRA issue manually"""
        try:
            issue_data = {
                'fields': {
                    'project': {'key': self.default_project},
                    'summary': title,
                    'description': description,
                    'issuetype': {'name': issue_type},
                    'priority': {'name': priority}
                }
            }
            
            if assignee:
                issue_data['fields']['assignee'] = {'emailAddress': assignee}
            
            url = f"{self.jira_url}/rest/api/3/issue"
            response = self.session.post(url, json=issue_data, timeout=30)
            
            if response.status_code == 201:
                issue_info = response.json()
                jira_key = issue_info['key']
                jira_url = f"{self.jira_url}/browse/{jira_key}"
                return True, jira_key, jira_url
            else:
                return False, '', f"Failed to create issue: {response.text}"
                
        except Exception as e:
            return False, '', f"Error creating JIRA issue: {str(e)}"
    
    def get_jira_issue(self, issue_key: str) -> Tuple[bool, Dict[str, Any], str]:
        """Get JIRA issue details"""
        try:
            url = f"{self.jira_url}/rest/api/3/issue/{issue_key}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                issue_data = response.json()
                return True, issue_data, ''
            else:
                return False, {}, f"Failed to get issue: {response.text}"
                
        except Exception as e:
            return False, {}, f"Error getting JIRA issue: {str(e)}"
    
    def add_comment_to_issue(self, issue_key: str, comment: str) -> Tuple[bool, str]:
        """Add comment to JIRA issue"""
        try:
            comment_data = {
                'body': {
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {
                            'type': 'paragraph',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': comment
                                }
                            ]
                        }
                    ]
                }
            }
            
            url = f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment"
            response = self.session.post(url, json=comment_data, timeout=30)
            
            if response.status_code == 201:
                return True, "Comment added successfully"
            else:
                return False, f"Failed to add comment: {response.text}"
                
        except Exception as e:
            return False, f"Error adding comment: {str(e)}"
