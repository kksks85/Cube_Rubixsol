#!/usr/bin/env python3
"""
Test Script - Verify Serial Number Field
Tests the new serial_number field functionality
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import Product

def test_serial_number_field():
    """Test the serial number field functionality"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Testing serial number field functionality...")
            
            # Get a sample product
            product = Product.query.first()
            if not product:
                print("❌ No products found in database")
                return False
            
            print(f"✓ Found product: {product.product_name} ({product.product_code})")
            print(f"✓ Current serial number: {product.serial_number or 'Not assigned'}")
            
            # Test setting a serial number
            test_serial = "UAV-TEST-2025-001"
            original_serial = product.serial_number
            
            product.serial_number = test_serial
            db.session.commit()
            
            # Verify the change
            updated_product = Product.query.filter_by(id=product.id).first()
            if updated_product.serial_number == test_serial:
                print(f"✓ Successfully set serial number: {test_serial}")
            else:
                print("❌ Failed to set serial number")
                return False
            
            # Test uniqueness constraint (should fail)
            try:
                other_product = Product.query.filter(Product.id != product.id).first()
                if other_product:
                    other_product.serial_number = test_serial
                    db.session.commit()
                    print("❌ Uniqueness constraint not working!")
                    return False
            except Exception as e:
                print("✓ Uniqueness constraint working correctly")
                db.session.rollback()
            
            # Restore original serial number
            product.serial_number = original_serial
            db.session.commit()
            print(f"✓ Restored original serial number: {original_serial or 'Not assigned'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing serial number field: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("🧪 Running test: Serial Number Field")
    success = test_serial_number_field()
    
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
        sys.exit(1)
