"""
Email Polling Service
Background service that polls email servers and processes incoming emails
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from flask import Flask
from app import create_app, db
from app.models import InboundEmailRule, ProcessedEmail, UAVServiceIncident, EmailConfig
from app.email_client import EmailClient, EmailServerConfig
from app.email_management.routes import process_email_with_rules
import json
import os

class EmailPollingService:
    """Service that polls email servers for new emails"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app or create_app()
        self.running = False
        self.thread = None
        self.polling_interval = 300  # Default 5 minutes
        self.logger = logging.getLogger(__name__)
        self.email_configs = {}
        self.last_poll_time = None
        
    def start(self):
        """Start the email polling service"""
        if self.running:
            self.logger.warning("Email polling service is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.thread.start()
        self.logger.info("Email polling service started")
    
    def stop(self):
        """Stop the email polling service"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)
        self.logger.info("Email polling service stopped")
    
    def _polling_loop(self):
        """Main polling loop"""
        self.logger.info(f"Email polling started with {self.polling_interval} second interval")
        
        while self.running:
            try:
                with self.app.app_context():
                    self._load_polling_configuration()
                    processed_count = self._poll_emails()
                    self.last_poll_time = datetime.now()
                    
                    # Update polling status in database
                    self._update_polling_status(processed_count)
                    
            except Exception as e:
                self.logger.error(f"Error in polling loop: {str(e)}")
            
            # Wait for next poll, but check running status every second
            for _ in range(self.polling_interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def _load_polling_configuration(self):
        """Load email polling configuration from database"""
        try:
            # Load email server configurations
            email_configs = EmailConfig.query.filter_by(is_active=True).all()
            
            self.email_configs = {}
            for config in email_configs:
                # Check for IMAP configuration
                if config.imap_server and config.imap_username:
                    self.email_configs[f"{config.id}_imap"] = {
                        'server': config.imap_server,
                        'port': config.imap_port or 993,
                        'username': config.imap_username,
                        'password': config.imap_password,
                        'protocol': 'IMAP',
                        'use_ssl': config.imap_use_ssl,
                        'config_id': config.id
                    }
                
                # Check for POP3 configuration
                if config.pop3_server and config.pop3_username:
                    self.email_configs[f"{config.id}_pop3"] = {
                        'server': config.pop3_server,
                        'port': config.pop3_port or 995,
                        'username': config.pop3_username,
                        'password': config.pop3_password,
                        'protocol': 'POP3',
                        'use_ssl': config.pop3_use_ssl,
                        'config_id': config.id
                    }
            
            # Load polling interval from settings (if exists)
            self._load_polling_interval()
            
        except Exception as e:
            self.logger.error(f"Error loading email configuration: {str(e)}")
    
    def _load_polling_interval(self):
        """Load polling interval from configuration"""
        try:
            # First check database configuration
            from app.models import EmailPollingConfig
            polling_config = EmailPollingConfig.query.first()
            
            if polling_config and polling_config.polling_enabled:
                # Use database interval (convert minutes to seconds)
                self.polling_interval = polling_config.polling_interval_minutes * 60
                self.logger.info(f"Using database polling interval: {polling_config.polling_interval_minutes} minutes")
                return
            
            # Check if there's an environment variable
            interval = os.environ.get('EMAIL_POLLING_INTERVAL')
            if interval:
                self.polling_interval = int(interval)
            else:
                # Default intervals based on environment
                env = os.environ.get('FLASK_ENV', 'production')
                if env == 'development':
                    self.polling_interval = 60  # 1 minute for development
                else:
                    self.polling_interval = 300  # 5 minutes for production
                    
        except ValueError:
            self.logger.warning("Invalid polling interval, using default")
            self.polling_interval = 300
        except Exception as e:
            self.logger.error(f"Error loading polling interval: {str(e)}")
            self.polling_interval = 300
    
    def _poll_emails(self):
        """Poll all configured email servers for new emails"""
        if not self.email_configs:
            self.logger.debug("No email configurations found")
            return 0
        
        total_processed = 0
        
        for config_id, email_config in self.email_configs.items():
            try:
                processed_count = self._poll_single_server(email_config)
                total_processed += processed_count
                
            except Exception as e:
                self.logger.error(f"Error polling server {config_id}: {str(e)}")
        
        if total_processed > 0:
            self.logger.info(f"Processed {total_processed} new emails")
        
        return total_processed
    
    def _poll_single_server(self, email_config: Dict) -> int:
        """Poll a single email server"""
        client = EmailClient(
            server=email_config['server'],
            port=email_config['port'],
            username=email_config['username'],
            password=email_config['password'],
            protocol=email_config['protocol'],
            use_ssl=email_config['use_ssl']
        )
        
        try:
            # Fetch new emails
            new_emails = client.fetch_new_emails(limit=50)
            
            if not new_emails:
                return 0
            
            self.logger.info(f"Found {len(new_emails)} new emails from {email_config['server']}")
            
            processed_count = 0
            for email_data in new_emails:
                try:
                    if self._process_single_email(email_data, email_config):
                        processed_count += 1
                        
                        # Mark as read if using IMAP
                        if email_config['protocol'] == 'IMAP':
                            client.mark_as_read(email_data['uid'])
                            
                except Exception as e:
                    self.logger.error(f"Error processing email {email_data.get('message_id', 'unknown')}: {str(e)}")
            
            return processed_count
            
        except Exception as e:
            self.logger.error(f"Error fetching emails from {email_config['server']}: {str(e)}")
            return 0
        finally:
            client.disconnect()
    
    def _process_single_email(self, email_data: Dict, email_config: Dict) -> bool:
        """Process a single email through the rules engine"""
        try:
            # Check if email was already processed
            existing = ProcessedEmail.query.filter_by(
                email_message_id=email_data['message_id']
            ).first()
            
            if existing:
                self.logger.debug(f"Email {email_data['message_id']} already processed")
                return False
            
            # Find matching rules
            matching_rules = self._find_matching_rules(email_data)
            
            if not matching_rules:
                self.logger.debug(f"No matching rules for email: {email_data['subject']}")
                # Still log the email as processed but without rule
                self._log_processed_email(email_data, None, 'no_rule_matched')
                return False
            
            # Process with the highest priority rule
            rule = matching_rules[0]  # Already sorted by priority
            
            # Create service incident
            incident = self._create_service_incident(email_data, rule)
            
            if incident:
                # Log successful processing
                self._log_processed_email(email_data, rule, 'processed', incident.id)
                self.logger.info(f"Created incident {incident.incident_number} from email: {email_data['subject']}")
                return True
            else:
                # Log failed processing
                self._log_processed_email(email_data, rule, 'failed')
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing email: {str(e)}")
            # Log error
            self._log_processed_email(email_data, None, 'error', error_message=str(e))
            return False
    
    def _find_matching_rules(self, email_data: Dict) -> List[InboundEmailRule]:
        """Find rules that match the email"""
        import re
        import fnmatch
        
        # Get active rules ordered by priority
        rules = InboundEmailRule.query.filter_by(is_active=True).order_by(
            InboundEmailRule.priority_order.asc()
        ).all()
        
        matching_rules = []
        
        for rule in rules:
            try:
                # Check from email pattern
                if rule.from_email_pattern:
                    if not self._pattern_matches(rule.from_email_pattern, email_data.get('from', '')):
                        continue
                
                # Check to email pattern
                if rule.to_email_pattern:
                    if not self._pattern_matches(rule.to_email_pattern, email_data.get('to', '')):
                        continue
                
                # Check subject pattern
                if rule.subject_pattern:
                    if not self._pattern_matches(rule.subject_pattern, email_data.get('subject', '')):
                        continue
                
                # Check body keywords
                if rule.body_keywords and rule.body_keywords.strip() and rule.body_keywords != 'None':
                    keywords = [kw.strip() for kw in rule.body_keywords.split(',')]
                    body_text = email_data.get('body', '').lower()
                    if not any(keyword.lower() in body_text for keyword in keywords if keyword.strip()):
                        continue
                
                # Check attachment requirement
                if rule.attachment_required and not email_data.get('has_attachments', False):
                    continue
                
                matching_rules.append(rule)
                
            except Exception as e:
                self.logger.error(f"Error matching rule {rule.id}: {str(e)}")
                continue
        
        return matching_rules
    
    def _pattern_matches(self, pattern: str, text: str) -> bool:
        """Check if a pattern matches text (supports both glob and regex)"""
        if not pattern or not text:
            return not pattern  # Empty pattern matches empty text
        
        try:
            # First try as glob pattern (for patterns like *@domain.com)
            if '*' in pattern or '?' in pattern:
                import fnmatch
                return fnmatch.fnmatch(text.lower(), pattern.lower())
            
            # Try exact match
            if pattern.lower() == text.lower():
                return True
            
            # Try substring match
            if pattern.lower() in text.lower():
                return True
            
            # Finally try as regex
            import re
            return bool(re.search(pattern, text, re.IGNORECASE))
            
        except re.error:
            # If regex fails, fall back to substring match
            return pattern.lower() in text.lower()
    
    def _create_service_incident(self, email_data: Dict, rule: InboundEmailRule) -> Optional[UAVServiceIncident]:
        """Create a UAV service incident from email"""
        try:
            incident = UAVServiceIncident()
            incident.title = email_data['subject'][:200]
            incident.description = email_data['body']  # Just use the email body without metadata
            
            # Set created_by_id to admin user for email processing
            incident.created_by_id = 1  # Admin user ID
            
            # Set category to Maintenance for email incidents
            incident.incident_category = 'ROUTINE_MAINTENANCE'
            
            incident.priority = rule.default_priority or 'MEDIUM'
            incident.workflow_status = rule.default_status or 'INCIDENT_RAISED'
            
            if rule.auto_assign_to_id:
                incident.assigned_to_id = rule.auto_assign_to_id
            
            incident.customer_email = email_data['from_email']
            
            # Extract customer name
            customer_name = email_data['from_email'].split('@')[0].replace('.', ' ').replace('_', ' ').title()
            incident.customer_name = customer_name
            
            # Required fields
            incident.uav_model = 'Email Inquiry'
            incident.incident_number = incident.generate_incident_number()
            
            db.session.add(incident)
            db.session.flush()
            
            # Update rule statistics
            rule.emails_processed = (rule.emails_processed or 0) + 1
            rule.workorders_created = (rule.workorders_created or 0) + 1
            rule.last_processed_at = datetime.now()
            
            db.session.commit()
            
            return incident
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating service incident: {str(e)}")
            return None
    
    def _log_processed_email(self, email_data: Dict, rule: Optional[InboundEmailRule], 
                           status: str, incident_id: Optional[int] = None, error_message: Optional[str] = None):
        """Log processed email to database"""
        try:
            processed_email = ProcessedEmail()
            processed_email.email_uid = email_data['uid']
            processed_email.email_message_id = email_data['message_id']
            processed_email.from_email = email_data['from_email']
            processed_email.to_email = email_data['to_email']
            processed_email.subject = email_data['subject']
            processed_email.body_preview = email_data['body'][:500] if email_data['body'] else None
            processed_email.has_attachments = email_data['has_attachments']
            processed_email.attachment_count = email_data['attachment_count']
            processed_email.rule_id = rule.id if rule else None
            processed_email.processing_status = status
            processed_email.error_message = error_message
            processed_email.email_received_at = datetime.now()
            processed_email.processed_at = datetime.now()
            
            # If incident was created, link it
            if incident_id:
                processed_email.workorder_created_id = incident_id
            
            db.session.add(processed_email)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error logging processed email: {str(e)}")
    
    def _update_polling_status(self, processed_count: int):
        """Update polling status in database"""
        try:
            from app.models import EmailPollingConfig
            polling_config = EmailPollingConfig.query.first()
            
            if polling_config:
                polling_config.last_poll_time = datetime.now()
                polling_config.total_emails_processed = (polling_config.total_emails_processed or 0) + processed_count
                db.session.commit()
                
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating polling status: {str(e)}")
    
    def get_status(self) -> Dict:
        """Get service status information"""
        return {
            'running': self.running,
            'polling_interval': self.polling_interval,
            'last_poll_time': self.last_poll_time.isoformat() if self.last_poll_time else None,
            'configured_servers': len(self.email_configs),
            'thread_alive': self.thread.is_alive() if self.thread else False
        }


# Global service instance
email_polling_service = EmailPollingService()


def start_email_polling():
    """Start the email polling service"""
    email_polling_service.start()


def stop_email_polling():
    """Stop the email polling service"""
    email_polling_service.stop()


def get_polling_status():
    """Get current polling service status"""
    return email_polling_service.get_status()
