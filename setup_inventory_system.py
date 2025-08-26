#!/usr/bin/env python3
"""
Add Inventory Tables and Sample UAV Data
This script creates the inventory management tables and populates them with sample UAV parts data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import (InventoryCategory, InventoryItem, InventoryTransaction, 
                       WorkOrderPart, User)
from datetime import datetime, timezone
from decimal import Decimal

def create_inventory_tables():
    """Create inventory tables"""
    try:
        # Create all tables
        db.create_all()
        print("✅ Inventory tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def add_sample_categories():
    """Add sample inventory categories for UAV parts"""
    categories_data = [
        {
            'name': 'UAV Frames',
            'description': 'UAV chassis, frames, and structural components'
        },
        {
            'name': 'Propulsion Systems',
            'description': 'Motors, propellers, ESCs, and propulsion-related components'
        },
        {
            'name': 'Flight Controllers',
            'description': 'Autopilot systems, flight control units, and navigation equipment'
        },
        {
            'name': 'Sensors & Cameras',
            'description': 'Cameras, gimbals, LiDAR, thermal sensors, and monitoring equipment'
        },
        {
            'name': 'Power Systems',
            'description': 'Batteries, power modules, charging equipment, and power distribution'
        },
        {
            'name': 'Communication',
            'description': 'Radio systems, telemetry modules, antennas, and data links'
        },
        {
            'name': 'Landing Gear',
            'description': 'Landing gear systems, shock absorbers, and ground support equipment'
        },
        {
            'name': 'Tools & Maintenance',
            'description': 'Maintenance tools, spare parts, and repair equipment'
        }
    ]
    
    created_count = 0
    for cat_data in categories_data:
        existing = InventoryCategory.query.filter_by(name=cat_data['name']).first()
        if not existing:
            category = InventoryCategory(**cat_data)
            db.session.add(category)
            created_count += 1
    
    try:
        db.session.commit()
        print(f"✅ Created {created_count} inventory categories")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating categories: {e}")
        return False

def add_sample_uav_parts():
    """Add sample UAV parts and components"""
    
    # Get categories
    categories = {}
    for cat in InventoryCategory.query.all():
        categories[cat.name] = cat.id
    
    uav_parts_data = [
        # UAV Frames
        {
            'part_number': 'FRAME-QX450',
            'name': 'Quadcopter Frame 450mm',
            'description': 'Carbon fiber quadcopter frame with 450mm wheelbase. Lightweight and durable construction.',
            'manufacturer': 'AeroTech',
            'model': 'QX450-CF',
            'category_id': categories.get('UAV Frames'),
            'quantity_in_stock': 15,
            'minimum_stock_level': 5,
            'maximum_stock_level': 50,
            'unit_cost': Decimal('89.99'),
            'weight': Decimal('0.245'),
            'dimensions': '450x450x85 mm',
            'compatible_uav_models': 'Medium quadcopters\nPayload capacity: 1-2kg\nFlight time: 20-30 minutes'
        },
        {
            'part_number': 'FRAME-HEX680',
            'name': 'Hexacopter Frame 680mm',
            'description': 'Professional hexacopter frame for heavy-lift applications. Aluminum and carbon fiber construction.',
            'manufacturer': 'ProDrone',
            'model': 'HEX680-AL',
            'category_id': categories.get('UAV Frames'),
            'quantity_in_stock': 8,
            'minimum_stock_level': 3,
            'maximum_stock_level': 25,
            'unit_cost': Decimal('199.99'),
            'weight': Decimal('0.680'),
            'dimensions': '680x680x120 mm',
            'compatible_uav_models': 'Heavy-lift hexacopters\nPayload capacity: 3-5kg\nCommercial applications'
        },
        
        # Propulsion Systems
        {
            'part_number': 'MOTOR-2216',
            'name': 'Brushless Motor 2216 900KV',
            'description': 'High-efficiency brushless motor for medium quadcopters. 900KV rating.',
            'manufacturer': 'FlightPower',
            'model': 'FP2216-900',
            'category_id': categories.get('Propulsion Systems'),
            'quantity_in_stock': 32,
            'minimum_stock_level': 12,
            'maximum_stock_level': 80,
            'unit_cost': Decimal('24.99'),
            'weight': Decimal('0.055'),
            'dimensions': '27.5x30 mm',
            'compatible_uav_models': 'QX450 frame\n3S-4S LiPo batteries\n9-11 inch propellers'
        },
        {
            'part_number': 'ESC-30A',
            'name': 'Electronic Speed Controller 30A',
            'description': 'BLHeli_S ESC with 30A continuous current rating. Supports 2-6S LiPo.',
            'manufacturer': 'SpeedTech',
            'model': 'ST30A-BLH',
            'category_id': categories.get('Propulsion Systems'),
            'quantity_in_stock': 28,
            'minimum_stock_level': 16,
            'maximum_stock_level': 100,
            'unit_cost': Decimal('18.99'),
            'weight': Decimal('0.025'),
            'dimensions': '50x25x7 mm',
            'compatible_uav_models': 'Compatible with 2216 motors\nSupports PWM and OneShot\nBuilt-in BEC 5V/2A'
        },
        {
            'part_number': 'PROP-1045',
            'name': 'Carbon Fiber Propeller 10x4.5',
            'description': 'Balanced carbon fiber propeller. 10 inch diameter, 4.5 inch pitch.',
            'manufacturer': 'CarbonProps',
            'model': 'CP1045-CF',
            'category_id': categories.get('Propulsion Systems'),
            'quantity_in_stock': 24,
            'minimum_stock_level': 8,
            'maximum_stock_level': 60,
            'unit_cost': Decimal('12.99'),
            'weight': Decimal('0.018'),
            'dimensions': '254x114 mm',
            'compatible_uav_models': '2216 motors\nMedium quadcopters\nOptimal for 3S-4S setups'
        },
        
        # Flight Controllers
        {
            'part_number': 'FC-PIXHAWK4',
            'name': 'Pixhawk 4 Flight Controller',
            'description': 'Advanced autopilot system with ARM Cortex-M7 processor. Supports ArduPilot and PX4.',
            'manufacturer': 'DroneCode',
            'model': 'PX4-FC-V4',
            'category_id': categories.get('Flight Controllers'),
            'quantity_in_stock': 12,
            'minimum_stock_level': 4,
            'maximum_stock_level': 30,
            'unit_cost': Decimal('199.99'),
            'weight': Decimal('0.038'),
            'dimensions': '84x44x12 mm',
            'compatible_uav_models': 'All UAV types\nSupports GPS/GLONASS\nBuilt-in IMU and barometer'
        },
        {
            'part_number': 'GPS-M8N',
            'name': 'GPS Module with Compass',
            'description': 'u-blox NEO-M8N GPS module with integrated HMC5883L compass.',
            'manufacturer': 'NavSys',
            'model': 'NS-M8N-COMP',
            'category_id': categories.get('Flight Controllers'),
            'quantity_in_stock': 18,
            'minimum_stock_level': 6,
            'maximum_stock_level': 50,
            'unit_cost': Decimal('39.99'),
            'weight': Decimal('0.022'),
            'dimensions': '38x38x8.5 mm',
            'compatible_uav_models': 'Pixhawk series\nAPM flight controllers\n10Hz update rate'
        },
        
        # Sensors & Cameras
        {
            'part_number': 'CAM-4K-GIMBAL',
            'name': '4K Camera with 3-Axis Gimbal',
            'description': 'Professional 4K camera with stabilized 3-axis gimbal. 120fps at 1080p.',
            'manufacturer': 'AerialVision',
            'model': 'AV4K-3AG',
            'category_id': categories.get('Sensors & Cameras'),
            'quantity_in_stock': 6,
            'minimum_stock_level': 2,
            'maximum_stock_level': 15,
            'unit_cost': Decimal('599.99'),
            'weight': Decimal('0.420'),
            'dimensions': '140x95x85 mm',
            'compatible_uav_models': 'Medium to large UAVs\nPayload capacity: 500g+\nReal-time video transmission'
        },
        {
            'part_number': 'LIDAR-LITE-V3',
            'name': 'LiDAR Rangefinder',
            'description': 'Laser rangefinder with 40m range. I2C and PWM interfaces.',
            'manufacturer': 'RangeTech',
            'model': 'RT-LL3',
            'category_id': categories.get('Sensors & Cameras'),
            'quantity_in_stock': 14,
            'minimum_stock_level': 5,
            'maximum_stock_level': 40,
            'unit_cost': Decimal('129.99'),
            'weight': Decimal('0.022'),
            'dimensions': '40x20x13 mm',
            'compatible_uav_models': 'Terrain following\nObstacle avoidance\nPrecision landing'
        },
        
        # Power Systems
        {
            'part_number': 'BATT-4S-5000',
            'name': 'LiPo Battery 4S 5000mAh',
            'description': 'High-capacity 4S LiPo battery. 25C discharge rate, XT60 connector.',
            'manufacturer': 'PowerMax',
            'model': 'PM4S5000-25C',
            'category_id': categories.get('Power Systems'),
            'quantity_in_stock': 20,
            'minimum_stock_level': 8,
            'maximum_stock_level': 60,
            'unit_cost': Decimal('79.99'),
            'weight': Decimal('0.565'),
            'dimensions': '139x43x34 mm',
            'compatible_uav_models': 'Medium quadcopters\n15-25 minute flight time\nXT60 connector'
        },
        {
            'part_number': 'CHARGER-4CH',
            'name': 'Multi-Battery Charger 4-Channel',
            'description': 'Intelligent 4-channel LiPo charger. Supports 1-6S batteries simultaneously.',
            'manufacturer': 'ChargePro',
            'model': 'CP4CH-300W',
            'category_id': categories.get('Power Systems'),
            'quantity_in_stock': 5,
            'minimum_stock_level': 2,
            'maximum_stock_level': 15,
            'unit_cost': Decimal('149.99'),
            'weight': Decimal('1.200'),
            'dimensions': '180x140x65 mm',
            'compatible_uav_models': 'All LiPo batteries\nBalance charging\nAC/DC input'
        },
        
        # Communication
        {
            'part_number': 'RADIO-433-1W',
            'name': 'Telemetry Radio 433MHz 1W',
            'description': 'Long-range telemetry radio system. 433MHz frequency, 1W power output.',
            'manufacturer': 'CommLink',
            'model': 'CL433-1W',
            'category_id': categories.get('Communication'),
            'quantity_in_stock': 16,
            'minimum_stock_level': 6,
            'maximum_stock_level': 40,
            'unit_cost': Decimal('89.99'),
            'weight': Decimal('0.045'),
            'dimensions': '68x50x15 mm',
            'compatible_uav_models': 'Pixhawk series\n5km+ range\nMAVLink protocol'
        },
        
        # Landing Gear
        {
            'part_number': 'GEAR-RETRACT',
            'name': 'Retractable Landing Gear Set',
            'description': 'Electric retractable landing gear for medium UAVs. Carbon fiber construction.',
            'manufacturer': 'GearTech',
            'model': 'GT-RLG-450',
            'category_id': categories.get('Landing Gear'),
            'quantity_in_stock': 4,
            'minimum_stock_level': 2,
            'maximum_stock_level': 12,
            'unit_cost': Decimal('299.99'),
            'weight': Decimal('0.380'),
            'dimensions': '200x150x45 mm',
            'compatible_uav_models': '450-680mm frames\nPayload up to 3kg\nPWM control'
        },
        
        # Tools & Maintenance
        {
            'part_number': 'TOOL-HEX-SET',
            'name': 'Hex Key Tool Set',
            'description': 'Complete hex key set for UAV maintenance. Includes 1.5-6mm sizes.',
            'manufacturer': 'ToolCraft',
            'model': 'TC-HEX-UAV',
            'category_id': categories.get('Tools & Maintenance'),
            'quantity_in_stock': 10,
            'minimum_stock_level': 3,
            'maximum_stock_level': 25,
            'unit_cost': Decimal('19.99'),
            'weight': Decimal('0.150'),
            'dimensions': '150x80x25 mm',
            'compatible_uav_models': 'Universal\nAll frame types\nMagnetic tips'
        },
        {
            'part_number': 'BALANCER-PROP',
            'name': 'Propeller Balancer',
            'description': 'Precision propeller balancer for vibration-free flight. Supports 5-15 inch props.',
            'manufacturer': 'BalancePro',
            'model': 'BP-PROP-15',
            'category_id': categories.get('Tools & Maintenance'),
            'quantity_in_stock': 3,
            'minimum_stock_level': 1,
            'maximum_stock_level': 8,
            'unit_cost': Decimal('45.99'),
            'weight': Decimal('0.320'),
            'dimensions': '200x150x50 mm',
            'compatible_uav_models': '5-15 inch propellers\nAll propeller types\nPrecision balancing'
        }
    ]
    
    created_count = 0
    admin_user = User.query.filter_by(username='admin').first()
    admin_id = admin_user.id if admin_user else 1
    
    for part_data in uav_parts_data:
        existing = InventoryItem.query.filter_by(part_number=part_data['part_number']).first()
        if not existing:
            item = InventoryItem(**part_data)
            db.session.add(item)
            db.session.flush()  # Get the item ID
            
            # Create initial stock transaction
            if part_data['quantity_in_stock'] > 0:
                transaction = InventoryTransaction(
                    item_id=item.id,
                    transaction_type='IN',
                    quantity=part_data['quantity_in_stock'],
                    unit_cost=part_data['unit_cost'],
                    total_cost=part_data['unit_cost'] * part_data['quantity_in_stock'],
                    reference_type='ADJUSTMENT',
                    notes='Initial stock - Sample UAV parts inventory',
                    created_by_id=admin_id
                )
                db.session.add(transaction)
            
            created_count += 1
    
    try:
        db.session.commit()
        print(f"✅ Created {created_count} UAV inventory items with initial stock transactions")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating inventory items: {e}")
        return False

def main():
    """Main function to set up inventory system"""
    print("🚀 Setting up Inventory Management System...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        print("\n1. Creating inventory tables...")
        if not create_inventory_tables():
            return False
        
        print("\n2. Adding sample inventory categories...")
        if not add_sample_categories():
            return False
        
        print("\n3. Adding sample UAV parts and components...")
        if not add_sample_uav_parts():
            return False
        
        print("\n✅ Inventory Management System setup completed successfully!")
        print("\n📊 Summary:")
        print(f"   • Categories: {InventoryCategory.query.count()}")
        print(f"   • Inventory Items: {InventoryItem.query.count()}")
        print(f"   • Initial Transactions: {InventoryTransaction.query.count()}")
        
        print("\n🎯 Next Steps:")
        print("   1. Access the inventory module at /inventory")
        print("   2. Add more items or adjust stock levels")
        print("   3. Create work orders and request parts")
        print("   4. Monitor stock levels and set up reorder alerts")
        
        return True

if __name__ == "__main__":
    if main():
        print("\n🎉 Setup completed successfully!")
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)
