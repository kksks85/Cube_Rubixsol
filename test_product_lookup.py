#!/usr/bin/env python3
"""
Test the UAV Service Product Lookup API
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import Product

def test_product_lookup():
    """Test product lookup functionality"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Testing Product Lookup API...")
            
            # Get a test serial number
            test_product = Product.query.filter(Product.serial_number.isnot(None)).first()
            
            if not test_product:
                print("❌ No products with serial numbers found!")
                return False
            
            print(f"📦 Testing with: {test_product.serial_number} - {test_product.product_name}")
            
            # Test the lookup logic directly
            serial_number = test_product.serial_number
            
            # Search for product by serial number
            product = Product.query.filter_by(serial_number=serial_number).first()
            
            if not product:
                print(f"❌ Product not found for serial: {serial_number}")
                return False
            
            print(f"✓ Product found: {product.product_name}")
            
            # Test owner company access
            try:
                owner_company_name = 'Unknown'
                if product.owner_company:
                    owner_company_name = product.owner_company.name
                    print(f"✓ Owner company: {owner_company_name}")
                else:
                    print("⚠️  No owner company linked")
            except Exception as e:
                print(f"❌ Error accessing owner_company: {str(e)}")
                return False
            
            # Test category access
            try:
                category_name = 'Unknown'
                if product.category:
                    category_name = product.category.name
                    print(f"✓ Category: {category_name}")
                else:
                    print("⚠️  No category linked")
            except Exception as e:
                print(f"❌ Error accessing category: {str(e)}")
                return False
            
            # Test response data structure
            response_data = {
                'success': True,
                'product_name': product.product_name or 'Unknown Product',
                'owner_company': owner_company_name,
                'last_service_date': None,  # We'll test this separately
                'product_code': product.product_code or '',
                'category': category_name
            }
            
            print("✅ API Response Data:")
            for key, value in response_data.items():
                print(f"   {key}: {value}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in product lookup test: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🧪 UAV Service Product Lookup API Test")
    print("=" * 50)
    
    success = test_product_lookup()
    
    if success:
        print("✅ Product lookup test completed successfully!")
    else:
        print("❌ Product lookup test failed!")
        sys.exit(1)
