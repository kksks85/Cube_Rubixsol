#!/usr/bin/env python3
"""
Test Script: Add Sample Service Dates to UAVs
==============================================

This script adds test service dates to some UAVs to demonstrate 
the dashboard service reports functionality.
"""

from datetime import datetime, timedelta
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Product

def add_test_service_dates():
    """Add test service dates to demonstrate dashboard functionality."""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Get all products
            products = Product.query.all()
            
            if not products:
                print("No products found in database.")
                return
            
            print(f"Found {len(products)} products. Adding test service dates...")
            
            today = datetime.now().date()
            
            # Different test scenarios
            test_scenarios = [
                {
                    'last_serviced': today - timedelta(days=80),  # Due in 10 days
                    'description': 'Service due soon (10 days)'
                },
                {
                    'last_serviced': today - timedelta(days=95),  # Overdue by 5 days  
                    'description': 'Service overdue (5 days)'
                },
                {
                    'last_serviced': today - timedelta(days=100), # Overdue by 10 days
                    'description': 'Service overdue (10 days)'
                },
                {
                    'last_serviced': today - timedelta(days=60),  # Not due for 30 days
                    'description': 'Service current (30 days left)'
                },
                {
                    'last_serviced': today - timedelta(days=85),  # Due in 5 days
                    'description': 'Service due very soon (5 days)'
                }
            ]
            
            # Apply test scenarios to products
            for i, product in enumerate(products[:len(test_scenarios)]):
                scenario = test_scenarios[i]
                
                # Set last serviced date
                product.last_serviced = scenario['last_serviced']
                
                # Calculate next service due (90 days from last serviced)
                product.update_next_service_due()
                
                print(f"✓ Updated {product.product_code}: {scenario['description']}")
                print(f"  Last Serviced: {product.last_serviced}")
                print(f"  Next Due: {product.next_service_due}")
                print(f"  Status: {product.service_status}")
                print()
            
            # Commit changes
            db.session.commit()
            
            print("✅ Test service dates added successfully!")
            
            # Show summary
            today = datetime.now().date()
            one_month_from_now = today + timedelta(days=30)
            
            service_due_soon = Product.query.filter(
                Product.next_service_due.isnot(None),
                Product.next_service_due <= one_month_from_now,
                Product.next_service_due >= today
            ).count()
            
            service_overdue = Product.query.filter(
                Product.next_service_due.isnot(None),
                Product.next_service_due < today
            ).count()
            
            print(f"Dashboard will show:")
            print(f"  • UAVs service due within 30 days: {service_due_soon}")
            print(f"  • UAVs with overdue service: {service_overdue}")
            print()
            print("Visit http://127.0.0.1:5000/dashboard to see the reports!")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    print("CUBE - PRO: Adding Test Service Dates")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if add_test_service_dates():
        print("🎉 Test data added successfully!")
    else:
        print("❌ Failed to add test data.")
        sys.exit(1)
