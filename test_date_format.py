#!/usr/bin/env python3
"""
Test date format fix for service forms
"""

from app import create_app
from app.service.forms import ServiceIncidentForm, ServiceIncidentUpdateForm
from datetime import datetime
from flask import Flask

def test_date_forms():
    """Test the date field rendering in service forms"""
    
    app = create_app()
    
    with app.app_context():
        with app.test_request_context():
            print("Testing ServiceIncidentForm...")
            form1 = ServiceIncidentForm()
            print(f"estimated_completion_date field type: {type(form1.estimated_completion_date)}")
            print(f"estimated_completion_date widget: {form1.estimated_completion_date.widget}")
            
            print("\nTesting ServiceIncidentUpdateForm...")
            form2 = ServiceIncidentUpdateForm()
            print(f"estimated_completion_date field type: {type(form2.estimated_completion_date)}")
            print(f"estimated_completion_date widget: {form2.estimated_completion_date.widget}")
            
            # Test date format handling
            test_date = datetime(2025, 8, 26, 15, 30)
            form1.estimated_completion_date.data = test_date
            
            print(f"\nTest date: {test_date}")
            print(f"Form field data: {form1.estimated_completion_date.data}")
            
            print("\nDate format test completed successfully!")

if __name__ == '__main__':
    test_date_forms()
