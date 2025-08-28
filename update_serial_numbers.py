#!/usr/bin/env python3
"""
Update Serial Numbers on Existing Products
Adds serial numbers to products that don't have them yet
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import Product

def update_serial_numbers():
    """Update serial numbers for existing products"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Updating serial numbers on existing products...")
            
            # Get products without serial numbers
            products_without_serial = Product.query.filter(Product.serial_number.is_(None)).all()
            
            print(f"📊 Found {len(products_without_serial)} products without serial numbers")
            
            if not products_without_serial:
                print("✅ All products already have serial numbers!")
                return True
            
            # Generate serial numbers for products without them
            updated_count = 0
            
            for product in products_without_serial:
                # Generate a serial number based on company and product code
                company_prefix = product.owner_company.name[:3].upper() if product.owner_company else "UAV"
                
                # Create a unique serial number
                # Format: COMPANY-PRODUCTCODE-YEAR-SEQUENCE
                year = "2025"
                sequence = str(product.id).zfill(3)  # Use product ID as sequence, padded to 3 digits
                
                # Clean product code (remove special characters)
                clean_product_code = ''.join(c for c in product.product_code if c.isalnum())[:8]
                
                serial_number = f"{company_prefix}-{clean_product_code}-{year}-{sequence}"
                
                # Ensure uniqueness (in case of conflicts)
                counter = 1
                original_serial = serial_number
                while Product.query.filter_by(serial_number=serial_number).first():
                    serial_number = f"{original_serial}-{counter}"
                    counter += 1
                
                # Assign the serial number
                product.serial_number = serial_number
                updated_count += 1
                
                print(f"✓ {product.product_name} ({product.product_code}) → {serial_number}")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n✅ Successfully updated {updated_count} products with serial numbers!")
            
            # Show final summary
            total_products = Product.query.count()
            products_with_serial = Product.query.filter(Product.serial_number.isnot(None)).count()
            products_without_serial = Product.query.filter(Product.serial_number.is_(None)).count()
            
            print(f"\n📊 Final Summary:")
            print(f"   - Total products: {total_products}")
            print(f"   - Products with serial numbers: {products_with_serial}")
            print(f"   - Products without serial numbers: {products_without_serial}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating serial numbers: {str(e)}")
            db.session.rollback()
            return False

def list_all_serial_numbers():
    """List all products with their serial numbers"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n📋 Current Serial Numbers:")
            print("=" * 80)
            
            products = Product.query.order_by(Product.product_code).all()
            
            for product in products:
                company_name = product.owner_company.name if product.owner_company else "Unknown"
                serial_status = product.serial_number if product.serial_number else "NOT ASSIGNED"
                
                print(f"{product.product_code:<15} | {product.product_name:<25} | {company_name:<15} | {serial_status}")
            
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ Error listing serial numbers: {str(e)}")

if __name__ == '__main__':
    print("🔧 Updating Serial Numbers on Existing Products")
    print("=" * 50)
    
    # First show current status
    list_all_serial_numbers()
    
    # Update serial numbers
    success = update_serial_numbers()
    
    if success:
        # Show updated status
        list_all_serial_numbers()
        print("✅ Serial number update completed successfully!")
    else:
        print("❌ Serial number update failed!")
        sys.exit(1)
