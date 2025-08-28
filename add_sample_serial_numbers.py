#!/usr/bin/env python3
"""
Add Sample Serial Numbers
Adds sample serial numbers to some UAV products for demonstration
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import Product

def add_sample_serial_numbers():
    """Add sample serial numbers to UAV products"""
    app = create_app()
    
    with app.app_context():
        try:
            print("📋 Adding sample serial numbers to UAV products...")
            
            # Sample serial numbers for different products
            serial_updates = [
                ("DJI-MAVIC3", "DJI-MV3-2025-001"),
                ("PARROT-ANAFI", "PRT-AF-2025-002"),
                ("SKYDIO-2PLUS", "SKY-2P-2025-003"),
                ("AUTEL-EVO2", "AUT-EV2-2025-004"),
                ("DJI-MAV3ENT", "DJI-M3E-2025-005"),
                ("DJI-MAT30T", "DJI-M30-2025-006"),
                ("PARROT-ANAFI-AI", "PRT-AAI-2025-007"),
                ("SKYDIO-X2D", "SKY-X2D-2025-008")
            ]
            
            updated_count = 0
            
            for product_code, serial_number in serial_updates:
                product = Product.query.filter_by(product_code=product_code).first()
                if product:
                    product.serial_number = serial_number
                    updated_count += 1
                    print(f"✓ {product.product_name} → {serial_number}")
                else:
                    print(f"⚠️ Product not found: {product_code}")
            
            db.session.commit()
            print(f"\n✅ Successfully added serial numbers to {updated_count} products!")
            
            # Show products with and without serial numbers
            products_with_serial = Product.query.filter(Product.serial_number.isnot(None)).count()
            products_without_serial = Product.query.filter(Product.serial_number.is_(None)).count()
            
            print(f"📊 Summary:")
            print(f"   - Products with serial numbers: {products_with_serial}")
            print(f"   - Products without serial numbers: {products_without_serial}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding serial numbers: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("🔄 Adding sample serial numbers to UAV products")
    success = add_sample_serial_numbers()
    
    if success:
        print("✅ Sample serial numbers added successfully!")
    else:
        print("❌ Failed to add sample serial numbers!")
        sys.exit(1)
