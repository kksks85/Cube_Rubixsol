#!/usr/bin/env python3
"""
Email Polling Service Startup Script
Initializes and starts the email polling service when the Flask app starts
"""

import os
import sys
import atexit
import logging
from flask import Flask

def setup_email_polling(app: Flask):
    """Set up email polling service with the Flask app"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('email_polling.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('email_polling_startup')
    
    try:
        # Import email polling service
        from app.email_polling_service import email_polling_service
        from app.models import EmailPollingConfig
        
        # Check if auto-start is enabled
        with app.app_context():
            config = EmailPollingConfig.get_config()
            
            if config.polling_enabled:
                # Start the email polling service
                email_polling_service.start()
                logger.info("Email polling service started automatically")
                
                # Register cleanup on app shutdown
                def cleanup_polling():
                    try:
                        email_polling_service.stop()
                        logger.info("Email polling service stopped during shutdown")
                    except Exception as e:
                        logger.error(f"Error stopping email polling service: {e}")
                
                atexit.register(cleanup_polling)
            else:
                logger.info("Email polling is disabled in configuration")
                
    except ImportError as e:
        logger.error(f"Failed to import email polling modules: {e}")
    except Exception as e:
        logger.error(f"Error setting up email polling: {e}")


def init_email_polling_on_startup():
    """Initialize email polling when called from run.py"""
    try:
        from app import create_app
        app = create_app()
        setup_email_polling(app)
        return True
    except Exception as e:
        print(f"Error initializing email polling: {e}")
        return False


if __name__ == "__main__":
    # Can be run standalone for testing
    print("🚀 Email Polling Service Startup")
    print("=" * 40)
    
    if init_email_polling_on_startup():
        print("✅ Email polling service initialized successfully")
    else:
        print("❌ Failed to initialize email polling service")
