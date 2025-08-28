#!/usr/bin/env python3
"""
Add sample UAV inventory items to test the Available Inventory feature
"""

from app import create_app
from app.models import db, InventoryItem, InventoryCategory
from datetime import datetime, timezone

def add_uav_inventory_items():
    """Add sample UAV-related inventory items"""
    app = create_app()
    
    with app.app_context():
        # Check if UAV category exists, create if not
        uav_category = InventoryCategory.query.filter_by(name='UAV Parts').first()
        if not uav_category:
            uav_category = InventoryCategory(
                name='UAV Parts',
                description='Unmanned Aerial Vehicle parts and components'
            )
            db.session.add(uav_category)
            db.session.commit()
            print(f"Created UAV Parts category: {uav_category.id}")

        # Sample UAV inventory items
        inventory_items = [
            {
                'part_number': 'BAT-LIPO-22V-5000',
                'name': 'LiPo Battery 22.2V 5000mAh',
                'description': 'High-capacity lithium polymer battery for professional UAVs',
                'manufacturer': 'PowerMax',
                'model': 'PM-5000-22V',
                'quantity_in_stock': 15,
                'minimum_stock_level': 5,
                'maximum_stock_level': 30,
                'unit_cost': 89.99,
                'weight': 0.680,
                'dimensions': '165x55x38 mm',
                'compatible_uav_models': 'AeroPuma,DJI Matrice,ALL',
                'category_id': uav_category.id
            },
            {
                'part_number': 'PROP-CF-1045',
                'name': 'Carbon Fiber Propeller 10x4.5',
                'description': 'Lightweight carbon fiber propeller for enhanced performance',
                'manufacturer': 'AeroTech',
                'model': 'CF-1045-Pro',
                'quantity_in_stock': 8,
                'minimum_stock_level': 4,
                'maximum_stock_level': 20,
                'unit_cost': 24.50,
                'weight': 0.015,
                'dimensions': '254mm diameter',
                'compatible_uav_models': 'AeroPuma,Custom Build',
                'category_id': uav_category.id
            },
            {
                'part_number': 'CAM-GIMBAL-3AX',
                'name': '3-Axis Camera Gimbal',
                'description': 'Professional 3-axis stabilized camera gimbal for aerial photography',
                'manufacturer': 'SkyView',
                'model': 'SV-3AX-Pro',
                'quantity_in_stock': 3,
                'minimum_stock_level': 2,
                'maximum_stock_level': 8,
                'unit_cost': 459.00,
                'weight': 0.380,
                'dimensions': '120x85x65 mm',
                'compatible_uav_models': 'AeroPuma,DJI Phantom',
                'category_id': uav_category.id
            },
            {
                'part_number': 'FC-PIXHAWK-V5',
                'name': 'Pixhawk V5 Flight Controller',
                'description': 'Advanced flight control unit with GPS and sensors',
                'manufacturer': 'PX4',
                'model': 'Pixhawk-5',
                'quantity_in_stock': 6,
                'minimum_stock_level': 3,
                'maximum_stock_level': 12,
                'unit_cost': 199.99,
                'weight': 0.068,
                'dimensions': '85x55x15 mm',
                'compatible_uav_models': 'ALL',
                'category_id': uav_category.id
            },
            {
                'part_number': 'GPS-RTK-M8P',
                'name': 'RTK GPS Module M8P',
                'description': 'High-precision RTK GPS module for centimeter-level accuracy',
                'manufacturer': 'u-blox',
                'model': 'NEO-M8P-2',
                'quantity_in_stock': 4,
                'minimum_stock_level': 2,
                'maximum_stock_level': 10,
                'unit_cost': 129.00,
                'weight': 0.025,
                'dimensions': '22x16x2.4 mm',
                'compatible_uav_models': 'AeroPuma,Custom Build,DJI Matrice',
                'category_id': uav_category.id
            },
            {
                'part_number': 'ESC-BLHELI-30A',
                'name': 'BLHeli_32 ESC 30A',
                'description': 'Electronic speed controller for brushless motors',
                'manufacturer': 'HobbyStar',
                'model': 'HS-30A-BL32',
                'quantity_in_stock': 0,  # Out of stock to test status
                'minimum_stock_level': 8,
                'maximum_stock_level': 24,
                'unit_cost': 18.75,
                'weight': 0.008,
                'dimensions': '36x18x6 mm',
                'compatible_uav_models': 'ALL',
                'category_id': uav_category.id
            },
            {
                'part_number': 'MOTOR-BR2216-900KV',
                'name': 'Brushless Motor 2216 900KV',
                'description': 'High-efficiency brushless outrunner motor',
                'manufacturer': 'T-Motor',
                'model': 'AT2216-900',
                'quantity_in_stock': 2,  # Low stock to test status
                'minimum_stock_level': 8,
                'maximum_stock_level': 16,
                'unit_cost': 32.99,
                'weight': 0.055,
                'dimensions': '27.9x30mm',
                'compatible_uav_models': 'AeroPuma,Custom Build',
                'category_id': uav_category.id
            },
            {
                'part_number': 'FRAME-CF-450',
                'name': 'Carbon Fiber Frame 450mm',
                'description': 'Lightweight carbon fiber quadcopter frame',
                'manufacturer': 'SkyFrame',
                'model': 'SF-450-X',
                'quantity_in_stock': 50,  # Overstock to test status
                'minimum_stock_level': 5,
                'maximum_stock_level': 15,
                'unit_cost': 75.00,
                'weight': 0.180,
                'dimensions': '450x450x55 mm',
                'compatible_uav_models': 'Custom Build',
                'category_id': uav_category.id
            }
        ]

        # Add inventory items
        added_count = 0
        for item_data in inventory_items:
            # Check if item already exists
            existing_item = InventoryItem.query.filter_by(part_number=item_data['part_number']).first()
            if not existing_item:
                item = InventoryItem(**item_data)
                db.session.add(item)
                added_count += 1
                print(f"Added inventory item: {item_data['part_number']} - {item_data['name']}")
            else:
                print(f"Item already exists: {item_data['part_number']} - {item_data['name']}")

        db.session.commit()
        print(f"\nSuccessfully added {added_count} new inventory items!")
        
        # Display summary
        total_items = InventoryItem.query.count()
        uav_items = InventoryItem.query.filter_by(category_id=uav_category.id).count()
        print(f"Total inventory items in database: {total_items}")
        print(f"UAV-related items: {uav_items}")

if __name__ == '__main__':
    add_uav_inventory_items()
