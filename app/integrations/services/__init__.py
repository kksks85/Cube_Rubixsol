"""
Integration Service Classes
Base classes and interfaces for third-party integrations
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import requests
import json
import logging
from app import db
from app.integrations.models import Integration, IntegrationSyncLog

logger = logging.getLogger(__name__)


class IntegrationService(ABC):
    """Base class for all integration services"""
    
    def __init__(self, integration: Integration):
        self.integration = integration
        self.config = integration.config_dict
        self.credentials = integration.credentials_dict
        
    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """Test the connection to the external system"""
        pass
    
    @abstractmethod
    def authenticate(self) -> Tuple[bool, str]:
        """Authenticate with the external system"""
        pass
    
    @abstractmethod
    def sync_data(self, entity_type: str = None, force_update: bool = False) -> Dict[str, Any]:
        """Sync data with the external system"""
        pass
    
    def log_sync(self, sync_type: str, operation: str, status: str, 
                 message: str = None, error_details: str = None,
                 entity_type: str = None, entity_id: str = None,
                 duration_ms: int = None, records_processed: int = 0,
                 records_success: int = 0, records_error: int = 0) -> IntegrationSyncLog:
        """Log synchronization activity"""
        
        log_entry = IntegrationSyncLog(
            integration_id=self.integration.id,
            sync_type=sync_type,
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            message=message,
            error_details=error_details,
            duration_ms=duration_ms,
            records_processed=records_processed,
            records_success=records_success,
            records_error=records_error
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        # Update integration last sync time and error status
        self.integration.last_sync_at = datetime.now(timezone.utc)
        if status == 'ERROR':
            self.integration.last_error = error_details or message
        else:
            self.integration.last_error = None
            
        db.session.commit()
        
        return log_entry
    
    def handle_error(self, operation: str, error: Exception, 
                    entity_type: str = None, entity_id: str = None):
        """Handle and log errors"""
        error_msg = str(error)
        logger.error(f"Integration {self.integration.name} error in {operation}: {error_msg}")
        
        self.log_sync(
            sync_type='ERROR',
            operation=operation,
            status='ERROR',
            message=f"Error in {operation}",
            error_details=error_msg,
            entity_type=entity_type,
            entity_id=entity_id
        )


class RESTIntegrationService(IntegrationService):
    """Service for REST API integrations"""
    
    def __init__(self, integration: Integration):
        super().__init__(integration)
        self.base_url = self.config.get('base_url', '')
        self.session = requests.Session()
        
        # Set up authentication headers
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Set up authentication for REST API"""
        auth_type = self.config.get('auth_type', 'none')
        
        if auth_type == 'basic':
            username = self.credentials.get('username')
            password = self.credentials.get('password')
            if username and password:
                self.session.auth = (username, password)
                
        elif auth_type == 'bearer':
            token = self.credentials.get('token') or self.credentials.get('api_key')
            if token:
                self.session.headers.update({'Authorization': f'Bearer {token}'})
                
        elif auth_type == 'api_key':
            api_key = self.credentials.get('api_key')
            api_key_header = self.config.get('api_key_header', 'X-API-Key')
            if api_key:
                self.session.headers.update({api_key_header: api_key})
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Add custom headers from config
        custom_headers = self.config.get('headers', {})
        if custom_headers:
            self.session.headers.update(custom_headers)
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test REST API connection"""
        try:
            test_endpoint = self.config.get('test_endpoint', '/health')
            url = f"{self.base_url.rstrip('/')}{test_endpoint}"
            
            response = self.session.get(url, timeout=30)
            
            if response.status_code < 400:
                return True, f"Connection successful (Status: {response.status_code})"
            else:
                return False, f"Connection failed with status {response.status_code}: {response.text}"
                
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection error: {str(e)}"
        except requests.exceptions.Timeout as e:
            return False, f"Connection timeout: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def authenticate(self) -> Tuple[bool, str]:
        """Test authentication with REST API"""
        try:
            auth_endpoint = self.config.get('auth_endpoint', '/auth/verify')
            url = f"{self.base_url.rstrip('/')}{auth_endpoint}"
            
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return True, "Authentication successful"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            elif response.status_code == 403:
                return False, "Authentication failed: Access denied"
            else:
                return False, f"Authentication test failed with status {response.status_code}"
                
        except Exception as e:
            return False, f"Authentication test error: {str(e)}"
    
    def sync_data(self, entity_type: str = None, force_update: bool = False) -> Dict[str, Any]:
        """Sync data via REST API"""
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
            # Implementation depends on specific API structure
            # This is a generic framework
            
            sync_endpoints = self.config.get('sync_endpoints', {})
            if entity_type and entity_type in sync_endpoints:
                endpoint = sync_endpoints[entity_type]
                results.update(self._sync_entity_type(entity_type, endpoint, force_update))
            else:
                # Sync all configured entity types
                for entity, endpoint in sync_endpoints.items():
                    entity_results = self._sync_entity_type(entity, endpoint, force_update)
                    results['records_processed'] += entity_results.get('records_processed', 0)
                    results['records_success'] += entity_results.get('records_success', 0)
                    results['records_error'] += entity_results.get('records_error', 0)
                    results['errors'].extend(entity_results.get('errors', []))
            
            results['success'] = results['records_error'] == 0
            results['message'] = f"Processed {results['records_processed']} records, {results['records_success']} successful, {results['records_error']} errors"
            
        except Exception as e:
            results['message'] = f"Sync failed: {str(e)}"
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
            entity_type=entity_type,
            duration_ms=int(duration),
            records_processed=results['records_processed'],
            records_success=results['records_success'],
            records_error=results['records_error']
        )
        
        return results
    
    def _sync_entity_type(self, entity_type: str, endpoint: str, force_update: bool) -> Dict[str, Any]:
        """Sync a specific entity type"""
        results = {
            'records_processed': 0,
            'records_success': 0,
            'records_error': 0,
            'errors': []
        }
        
        try:
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            response = self.session.get(url, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                # Process the data based on entity type
                # This is where you would implement specific logic for each entity type
                results['records_processed'] = len(data) if isinstance(data, list) else 1
                results['records_success'] = results['records_processed']
            else:
                error_msg = f"Failed to fetch {entity_type} data: {response.status_code} - {response.text}"
                results['errors'].append(error_msg)
                results['records_error'] = 1
                
        except Exception as e:
            results['errors'].append(f"Error syncing {entity_type}: {str(e)}")
            results['records_error'] = 1
        
        return results
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    params: Dict = None) -> requests.Response:
        """Make a request to the REST API"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        kwargs = {'timeout': 60}
        if params:
            kwargs['params'] = params
        if data:
            kwargs['json'] = data
            
        return self.session.request(method, url, **kwargs)


class WebServiceIntegrationService(IntegrationService):
    """Service for SOAP Web Service integrations"""
    
    def __init__(self, integration: Integration):
        super().__init__(integration)
        self.wsdl_url = self.config.get('wsdl_url')
        self.service_url = self.config.get('service_url')
        
    def test_connection(self) -> Tuple[bool, str]:
        """Test SOAP Web Service connection"""
        try:
            # Try to access WSDL
            response = requests.get(self.wsdl_url, timeout=30)
            if response.status_code == 200:
                return True, "WSDL accessible"
            else:
                return False, f"WSDL not accessible: {response.status_code}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def authenticate(self) -> Tuple[bool, str]:
        """Test SOAP authentication"""
        # Implementation depends on SOAP service authentication method
        return True, "SOAP authentication test not implemented"
    
    def sync_data(self, entity_type: str = None, force_update: bool = False) -> Dict[str, Any]:
        """Sync data via SOAP Web Service"""
        # Implementation depends on specific SOAP service
        return {
            'success': False,
            'message': 'SOAP sync not implemented',
            'records_processed': 0,
            'records_success': 0,
            'records_error': 0,
            'errors': ['SOAP sync not implemented']
        }
