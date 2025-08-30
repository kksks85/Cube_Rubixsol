"""
Active Directory Integration Service
Handles LDAP/AD user and group synchronization
"""

import ldap3
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE, SUBTREE
from ldap3.core.exceptions import LDAPException
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import logging

from app import db
from app.models import User, Role
from app.integrations.services import IntegrationService

logger = logging.getLogger(__name__)


class ActiveDirectoryService(IntegrationService):
    """Active Directory / LDAP integration service"""
    
    def __init__(self, integration):
        super().__init__(integration)
        self.domain_controller = self.config.get('domain_controller')
        self.domain_name = self.config.get('domain_name')
        self.base_dn = self.config.get('base_dn')
        self.bind_username = self.credentials.get('bind_username')
        self.bind_password = self.credentials.get('bind_password')
        
        # User settings
        self.user_base_dn = self.config.get('user_base_dn', self.base_dn)
        self.user_filter = self.config.get('user_filter', 
                                          "(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))")
        
        # Group settings
        self.group_base_dn = self.config.get('group_base_dn', self.base_dn)
        self.group_filter = self.config.get('group_filter', "(objectClass=group)")
        
        # Sync settings
        self.sync_users = self.config.get('sync_users', True)
        self.sync_groups = self.config.get('sync_groups', True)
        self.auto_create_users = self.config.get('auto_create_users', True)
        self.auto_disable_users = self.config.get('auto_disable_users', True)
        
        self.connection = None
    
    def _connect(self) -> Tuple[bool, str]:
        """Establish LDAP connection"""
        try:
            # Create server connection
            server = Server(self.domain_controller, get_info=ALL)
            
            # Determine authentication method
            if '@' in self.bind_username or '\\' in self.bind_username:
                # Use NTLM for domain accounts
                self.connection = Connection(
                    server, 
                    user=self.bind_username, 
                    password=self.bind_password,
                    authentication=NTLM,
                    auto_bind=True
                )
            else:
                # Use simple bind for service accounts
                bind_dn = f"cn={self.bind_username},{self.base_dn}"
                self.connection = Connection(
                    server,
                    user=bind_dn,
                    password=self.bind_password,
                    authentication=SIMPLE,
                    auto_bind=True
                )
            
            return True, "Connected successfully"
            
        except LDAPException as e:
            return False, f"LDAP connection failed: {str(e)}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def _disconnect(self):
        """Close LDAP connection"""
        if self.connection:
            self.connection.unbind()
            self.connection = None
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test Active Directory connection"""
        success, message = self._connect()
        if success:
            self._disconnect()
            return True, "Active Directory connection successful"
        return False, message
    
    def authenticate(self) -> Tuple[bool, str]:
        """Test AD authentication and permissions"""
        success, message = self._connect()
        if not success:
            return False, message
        
        try:
            # Test if we can read the base DN
            self.connection.search(
                search_base=self.base_dn,
                search_filter='(objectClass=*)',
                search_scope=SUBTREE,
                size_limit=1
            )
            
            if self.connection.result['result'] == 0:
                self._disconnect()
                return True, "Authentication successful with read permissions"
            else:
                self._disconnect()
                return False, f"Authentication failed: {self.connection.result['description']}"
                
        except Exception as e:
            self._disconnect()
            return False, f"Authentication test error: {str(e)}"
    
    def sync_data(self, entity_type: str = None, force_update: bool = False) -> Dict[str, Any]:
        """Sync users and groups from Active Directory"""
        start_time = datetime.now()
        results = {
            'success': False,
            'message': '',
            'records_processed': 0,
            'records_success': 0,
            'records_error': 0,
            'errors': []
        }
        
        # Connect to AD
        success, message = self._connect()
        if not success:
            results['message'] = f"Failed to connect to AD: {message}"
            results['errors'].append(message)
            return results
        
        try:
            if entity_type == 'users' or (entity_type is None and self.sync_users):
                user_results = self._sync_users(force_update)
                results['records_processed'] += user_results['processed']
                results['records_success'] += user_results['success']
                results['records_error'] += user_results['errors']
                results['errors'].extend(user_results['error_messages'])
            
            if entity_type == 'groups' or (entity_type is None and self.sync_groups):
                group_results = self._sync_groups(force_update)
                results['records_processed'] += group_results['processed']
                results['records_success'] += group_results['success']
                results['records_error'] += group_results['errors']
                results['errors'].extend(group_results['error_messages'])
            
            results['success'] = results['records_error'] == 0
            results['message'] = f"AD Sync completed: {results['records_success']}/{results['records_processed']} successful"
            
        except Exception as e:
            results['message'] = f"AD sync failed: {str(e)}"
            results['errors'].append(str(e))
            self.handle_error('sync_data', e, entity_type)
        
        finally:
            self._disconnect()
        
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
    
    def _sync_users(self, force_update: bool = False) -> Dict[str, Any]:
        """Sync users from Active Directory"""
        results = {
            'processed': 0,
            'success': 0,
            'errors': 0,
            'error_messages': []
        }
        
        try:
            # Search for users
            self.connection.search(
                search_base=self.user_base_dn,
                search_filter=self.user_filter,
                search_scope=SUBTREE,
                attributes=['sAMAccountName', 'mail', 'givenName', 'sn', 
                           'displayName', 'telephoneNumber', 'userAccountControl',
                           'memberOf', 'lastLogon', 'whenChanged']
            )
            
            ad_users = self.connection.entries
            results['processed'] = len(ad_users)
            
            # Get default role for new users
            default_role = Role.query.filter_by(name='user').first()
            if not default_role:
                default_role = Role.query.first()
            
            for ad_user in ad_users:
                try:
                    username = str(ad_user.sAMAccountName)
                    email = str(ad_user.mail) if ad_user.mail else f"{username}@{self.domain_name}"
                    
                    # Check if user exists
                    user = User.query.filter_by(username=username).first()
                    
                    if user:
                        # Update existing user
                        if force_update or self._should_update_user(user, ad_user):
                            user.email = email
                            user.first_name = str(ad_user.givenName) if ad_user.givenName else username
                            user.last_name = str(ad_user.sn) if ad_user.sn else ''
                            user.phone = str(ad_user.telephoneNumber) if ad_user.telephoneNumber else None
                            
                            # Check if account is disabled
                            uac = int(ad_user.userAccountControl) if ad_user.userAccountControl else 0
                            user.is_active = not (uac & 2)  # Check disabled flag
                            
                            db.session.commit()
                            results['success'] += 1
                    else:
                        # Create new user if auto-create is enabled
                        if self.auto_create_users:
                            user = User(
                                username=username,
                                email=email,
                                first_name=str(ad_user.givenName) if ad_user.givenName else username,
                                last_name=str(ad_user.sn) if ad_user.sn else '',
                                phone=str(ad_user.telephoneNumber) if ad_user.telephoneNumber else None,
                                password_hash='',  # No local password for AD users
                                role_id=default_role.id if default_role else None,
                                is_active=True
                            )
                            
                            # Check if account is disabled
                            uac = int(ad_user.userAccountControl) if ad_user.userAccountControl else 0
                            user.is_active = not (uac & 2)
                            
                            db.session.add(user)
                            db.session.commit()
                            results['success'] += 1
                        else:
                            results['success'] += 1  # Skipped but not an error
                            
                except Exception as e:
                    results['errors'] += 1
                    error_msg = f"Error processing user {username}: {str(e)}"
                    results['error_messages'].append(error_msg)
                    logger.error(error_msg)
            
            # Handle deleted users if auto-disable is enabled
            if self.auto_disable_users:
                self._disable_deleted_users([str(u.sAMAccountName) for u in ad_users])
                        
        except Exception as e:
            results['errors'] += 1
            error_msg = f"Error during user sync: {str(e)}"
            results['error_messages'].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    def _sync_groups(self, force_update: bool = False) -> Dict[str, Any]:
        """Sync groups from Active Directory"""
        results = {
            'processed': 0,
            'success': 0,
            'errors': 0,
            'error_messages': []
        }
        
        try:
            # Search for groups
            self.connection.search(
                search_base=self.group_base_dn,
                search_filter=self.group_filter,
                search_scope=SUBTREE,
                attributes=['sAMAccountName', 'description', 'member']
            )
            
            ad_groups = self.connection.entries
            results['processed'] = len(ad_groups)
            
            for ad_group in ad_groups:
                try:
                    group_name = str(ad_group.sAMAccountName)
                    description = str(ad_group.description) if ad_group.description else ''
                    
                    # Check if role exists
                    role = Role.query.filter_by(name=group_name.lower()).first()
                    
                    if not role and self.auto_create_users:
                        # Create new role for AD group
                        role = Role(
                            name=group_name.lower(),
                            description=f"AD Group: {description}" if description else f"AD Group: {group_name}"
                        )
                        db.session.add(role)
                        db.session.commit()
                    
                    results['success'] += 1
                    
                except Exception as e:
                    results['errors'] += 1
                    error_msg = f"Error processing group {group_name}: {str(e)}"
                    results['error_messages'].append(error_msg)
                    logger.error(error_msg)
                        
        except Exception as e:
            results['errors'] += 1
            error_msg = f"Error during group sync: {str(e)}"
            results['error_messages'].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    def _should_update_user(self, user: User, ad_user) -> bool:
        """Check if user should be updated based on change timestamps"""
        # Simple implementation - could be enhanced with proper timestamp comparison
        return True
    
    def _disable_deleted_users(self, active_usernames: List[str]):
        """Disable users that no longer exist in AD"""
        try:
            # Find users with AD integration that are not in the active list
            users_to_disable = User.query.filter(
                User.username.notin_(active_usernames),
                User.is_active == True
            ).all()
            
            for user in users_to_disable:
                user.is_active = False
                logger.info(f"Disabled user {user.username} - no longer in AD")
            
            if users_to_disable:
                db.session.commit()
                
        except Exception as e:
            logger.error(f"Error disabling deleted users: {str(e)}")
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Authenticate a user against Active Directory"""
        try:
            # Try to bind with user credentials
            server = Server(self.domain_controller, get_info=ALL)
            
            # Format username for domain authentication
            if '@' not in username and '\\' not in username:
                auth_username = f"{username}@{self.domain_name}"
            else:
                auth_username = username
            
            test_conn = Connection(
                server,
                user=auth_username,
                password=password,
                authentication=NTLM,
                auto_bind=True
            )
            
            test_conn.unbind()
            return True, "Authentication successful"
            
        except LDAPException as e:
            return False, f"Authentication failed: {str(e)}"
        except Exception as e:
            return False, f"Authentication error: {str(e)}"
