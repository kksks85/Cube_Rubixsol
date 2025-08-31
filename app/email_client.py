"""
Email Client Module
Handles IMAP/POP3 connection and email fetching for the CUBE system
"""

import imaplib
import poplib
import email
from email.header import decode_header
import ssl
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from flask import current_app
import logging

class EmailClient:
    """Email client for fetching emails via IMAP or POP3"""
    
    def __init__(self, server: str, port: int, username: str, password: str, 
                 protocol: str = 'IMAP', use_ssl: bool = True):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.protocol = protocol.upper()
        self.use_ssl = use_ssl
        self.connection = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Establish connection to email server"""
        try:
            if self.protocol == 'IMAP':
                return self._connect_imap()
            elif self.protocol == 'POP3':
                return self._connect_pop3()
            else:
                raise ValueError(f"Unsupported protocol: {self.protocol}")
        except Exception as e:
            self.logger.error(f"Failed to connect to email server: {str(e)}")
            return False
    
    def _connect_imap(self) -> bool:
        """Connect using IMAP"""
        try:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                self.connection = imaplib.IMAP4(self.server, self.port)
            
            self.connection.login(self.username, self.password)
            self.connection.select('INBOX')
            self.logger.info(f"IMAP connection established to {self.server}")
            return True
        except Exception as e:
            self.logger.error(f"IMAP connection failed: {str(e)}")
            return False
    
    def _connect_pop3(self) -> bool:
        """Connect using POP3"""
        try:
            if self.use_ssl:
                self.connection = poplib.POP3_SSL(self.server, self.port)
            else:
                self.connection = poplib.POP3(self.server, self.port)
            
            self.connection.user(self.username)
            self.connection.pass_(self.password)
            self.logger.info(f"POP3 connection established to {self.server}")
            return True
        except Exception as e:
            self.logger.error(f"POP3 connection failed: {str(e)}")
            return False
    
    def fetch_new_emails(self, limit: int = 50) -> List[Dict]:
        """Fetch new/unread emails"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            if self.protocol == 'IMAP':
                return self._fetch_imap_emails(limit)
            elif self.protocol == 'POP3':
                return self._fetch_pop3_emails(limit)
        except Exception as e:
            self.logger.error(f"Error fetching emails: {str(e)}")
            return []
        
        return []
    
    def _fetch_imap_emails(self, limit: int) -> List[Dict]:
        """Fetch emails using IMAP"""
        emails = []
        
        try:
            # Search for unread emails
            status, messages = self.connection.search(None, 'UNSEEN')
            if status != 'OK':
                return emails
            
            email_ids = messages[0].split()
            
            # Limit the number of emails processed
            if len(email_ids) > limit:
                email_ids = email_ids[-limit:]  # Get latest emails
            
            for email_id in email_ids:
                try:
                    # Fetch email data
                    status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    # Extract email details
                    email_data = self._parse_email(email_message, email_id.decode())
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    self.logger.error(f"Error processing email {email_id}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in IMAP fetch: {str(e)}")
        
        return emails
    
    def _fetch_pop3_emails(self, limit: int) -> List[Dict]:
        """Fetch emails using POP3"""
        emails = []
        
        try:
            # Get number of messages
            num_messages = len(self.connection.list()[1])
            
            # Process recent messages (POP3 doesn't have unread concept)
            start_msg = max(1, num_messages - limit + 1)
            
            for i in range(start_msg, num_messages + 1):
                try:
                    # Retrieve message
                    raw_message = b'\n'.join(self.connection.retr(i)[1])
                    email_message = email.message_from_bytes(raw_message)
                    
                    # Extract email details
                    email_data = self._parse_email(email_message, str(i))
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    self.logger.error(f"Error processing POP3 message {i}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in POP3 fetch: {str(e)}")
        
        return emails
    
    def _parse_email(self, email_message, uid: str) -> Optional[Dict]:
        """Parse email message and extract relevant data"""
        try:
            # Decode subject
            subject = ""
            if email_message["Subject"]:
                subject_parts = decode_header(email_message["Subject"])
                subject = "".join([
                    part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
                    for part, encoding in subject_parts
                ])
            
            # Extract sender and recipient
            from_email_raw = email_message.get("From", "")
            to_email_raw = email_message.get("To", "")
            date_received = email_message.get("Date", "")
            message_id = email_message.get("Message-ID", f"local-{uid}")
            
            # Extract clean email addresses
            from_email = self._extract_email_address(from_email_raw)
            to_email = self._extract_email_address(to_email_raw)
            
            # Extract body
            body = self._extract_body(email_message)
            
            # Check for attachments
            attachments = self._extract_attachments(email_message)
            
            return {
                'uid': uid,
                'message_id': message_id,
                'from': from_email,  # Clean email address for rule matching
                'to': to_email,      # Clean email address for rule matching
                'from_email': from_email,  # For backward compatibility
                'to_email': to_email,      # For backward compatibility
                'from_raw': from_email_raw,    # Original header for display
                'to_raw': to_email_raw,        # Original header for display
                'subject': subject,
                'body': body,
                'date_received': date_received,
                'has_attachments': len(attachments) > 0,
                'attachment_count': len(attachments),
                'attachments': attachments
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing email: {str(e)}")
            return None
    
    def _extract_email_address(self, email_header: str) -> str:
        """Extract clean email address from email header"""
        import re
        
        if not email_header:
            return ""
        
        # Pattern to match email addresses in angle brackets: "Name" <email@domain.com>
        angle_match = re.search(r'<([^>]+)>', email_header)
        if angle_match:
            return angle_match.group(1).strip()
        
        # Pattern to match standalone email addresses
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_header)
        if email_match:
            return email_match.group(0).strip()
        
        # If no email found, return the original (might be just a name)
        return email_header.strip()
    
    def _extract_body(self, email_message) -> str:
        """Extract email body content"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        continue
                elif content_type == "text/html" and not body:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(email_message.get_payload())
        
        return body[:5000]  # Limit body length
    
    def _extract_attachments(self, email_message) -> List[Dict]:
        """Extract attachment information"""
        attachments = []
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'content_type': part.get_content_type(),
                            'size': len(part.get_payload(decode=True) or b'')
                        })
        
        return attachments
    
    def mark_as_read(self, uid: str) -> bool:
        """Mark email as read"""
        if not self.connection or self.protocol != 'IMAP':
            return False
        
        try:
            self.connection.store(uid, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            self.logger.error(f"Error marking email as read: {str(e)}")
            return False
    
    def disconnect(self):
        """Close connection to email server"""
        try:
            if self.connection:
                if self.protocol == 'IMAP':
                    self.connection.close()
                    self.connection.logout()
                elif self.protocol == 'POP3':
                    self.connection.quit()
                self.connection = None
                self.logger.info("Email connection closed")
        except Exception as e:
            self.logger.error(f"Error disconnecting: {str(e)}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test email server connection"""
        try:
            if self.connect():
                self.disconnect()
                return True, "Connection successful"
            else:
                return False, "Connection failed"
        except Exception as e:
            return False, f"Connection error: {str(e)}"


class EmailServerConfig:
    """Email server configuration management"""
    
    COMMON_SERVERS = {
        'gmail': {
            'imap': {'server': 'imap.gmail.com', 'port': 993, 'ssl': True},
            'pop3': {'server': 'pop.gmail.com', 'port': 995, 'ssl': True}
        },
        'outlook': {
            'imap': {'server': 'outlook.office365.com', 'port': 993, 'ssl': True},
            'pop3': {'server': 'outlook.office365.com', 'port': 995, 'ssl': True}
        },
        'yahoo': {
            'imap': {'server': 'imap.mail.yahoo.com', 'port': 993, 'ssl': True},
            'pop3': {'server': 'pop.mail.yahoo.com', 'port': 995, 'ssl': True}
        }
    }
    
    @classmethod
    def get_config(cls, provider: str, protocol: str = 'imap') -> Optional[Dict]:
        """Get configuration for common email providers"""
        provider = provider.lower()
        protocol = protocol.lower()
        
        if provider in cls.COMMON_SERVERS and protocol in cls.COMMON_SERVERS[provider]:
            return cls.COMMON_SERVERS[provider][protocol]
        
        return None
