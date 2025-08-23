#!/usr/bin/env python3
"""
Database initialization script for the Product Master module.
Creates sample UAV products, companies, and categories.
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models import Product, Company, ProductCategory, User

def init_product_categories():
    """Initialize default product categories."""
    categories = [
        {
            'name': 'Consumer Drones',
            'description': 'Entry-level drones for recreational use and basic photography'
        },
        {
            'name': 'Professional Photography',
            'description': 'High-end drones for professional photography and videography'
        },
        {
            'name': 'Commercial Survey',
            'description': 'Drones designed for mapping, surveying, and inspection tasks'
        },
        {
            'name': 'Agricultural Drones',
            'description': 'Specialized drones for precision agriculture and crop monitoring'
        },
        {
            'name': 'Industrial Inspection',
            'description': 'Heavy-duty drones for industrial inspection and maintenance'
        },
        {
            'name': 'Military/Defense',
            'description': 'Military-grade UAVs for defense and surveillance applications'
        },
        {
            'name': 'Racing Drones',
            'description': 'High-speed drones designed for competitive racing'
        },
        {
            'name': 'Cargo/Delivery',
            'description': 'Large payload drones for cargo transport and delivery services'
        }
    ]
    
    for cat_data in categories:
        category = ProductCategory.query.filter_by(name=cat_data['name']).first()
        if not category:
            category = ProductCategory(
                name=cat_data['name'],
                description=cat_data['description']
            )
            db.session.add(category)
            print(f"Created category: {cat_data['name']}")
    
    db.session.commit()
    return ProductCategory.query.all()

def init_companies():
    """Initialize sample companies."""
    companies_data = [
        {
            'name': 'DJI Technology Co., Ltd.',
            'registration_number': 'DJI-CN-2006',
            'email': 'contact@dji.com',
            'phone': '+86-755-2645-2345',
            'website': 'https://www.dji.com',
            'address_line1': '14th Floor, West Wing, Skyworth Semiconductor Design Building',
            'address_line2': 'No.18 Gaoxin South 4th Ave',
            'city': 'Shenzhen',
            'state': 'Guangdong',
            'postal_code': '518057',
            'country': 'China'
        },
        {
            'name': 'Parrot SA',
            'registration_number': 'PARROT-FR-1994',
            'email': 'info@parrot.com',
            'phone': '+33-1-48-03-60-60',
            'website': 'https://www.parrot.com',
            'address_line1': '174 Quai de Jemmapes',
            'city': 'Paris',
            'postal_code': '75010',
            'country': 'France'
        },
        {
            'name': 'Skydio Inc.',
            'registration_number': 'SKYDIO-US-2014',
            'email': 'contact@skydio.com',
            'phone': '+1-650-555-0123',
            'website': 'https://www.skydio.com',
            'address_line1': '275 Battery Street',
            'address_line2': 'Suite 400',
            'city': 'San Francisco',
            'state': 'California',
            'postal_code': '94111',
            'country': 'United States'
        },
        {
            'name': 'Autel Robotics',
            'registration_number': 'AUTEL-US-2014',
            'email': 'info@autelrobotics.com',
            'phone': '+1-855-528-8351',
            'website': 'https://www.autelrobotics.com',
            'address_line1': '18851 NE 29th Ave',
            'address_line2': 'Suite 700',
            'city': 'Aventura',
            'state': 'Florida',
            'postal_code': '33180',
            'country': 'United States'
        },
        {
            'name': 'Yuneec International',
            'registration_number': 'YUNEEC-CN-1999',
            'email': 'contact@yuneec.com',
            'phone': '+86-512-5718-9826',
            'website': 'https://www.yuneec.com',
            'address_line1': 'No. 188 Xingshan Road',
            'city': 'Kunshan',
            'state': 'Jiangsu',
            'postal_code': '215300',
            'country': 'China'
        }
    ]
    
    for company_data in companies_data:
        company = Company.query.filter_by(name=company_data['name']).first()
        if not company:
            company = Company(**company_data)
            db.session.add(company)
            print(f"Created company: {company_data['name']}")
    
    db.session.commit()
    return Company.query.all()

def init_sample_products(categories, companies):
    """Initialize sample UAV products."""
    # Get the first admin user to use as creator
    admin_user = User.query.filter_by(email='admin@workflowpro.com').first()
    if not admin_user:
        # Try to find any admin user
        admin_user = User.query.filter_by(username='admin').first()
    
    if not admin_user:
        print("Warning: No admin user found. Creating sample admin user for product creation.")
        admin_user = User(
            username='products_admin',
            email='products@workflowpro.com',
            first_name='System',
            last_name='Administrator',
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
    else:
        print(f"Using existing user '{admin_user.username}' for product creation.")
    
    products_data = [
        {
            'product_code': 'DJI-MAVIC3',
            'product_name': 'DJI Mavic 3',
            'description': 'Professional drone with Hasselblad camera and omnidirectional obstacle sensing',
            'company_name': 'DJI Technology Co., Ltd.',
            'category_name': 'Professional Photography',
            'manufacturer': 'DJI',
            'model_year': 2021,
            'price': 2199.00,
            'max_flight_time': 46,
            'max_range': 15000,
            'max_altitude': 6000,
            'max_speed': 68,
            'weight': 895,
            'dimensions_length': 347.5,
            'dimensions_width': 283,
            'dimensions_height': 107.7,
            'camera_resolution': '20MP, 5.1K Video',
            'payload_capacity': 0,
            'battery_type': 'Li-Po 3S',
            'battery_capacity': 5000,
            'charging_time': 96,
            'gps_enabled': True,
            'control_range': 15000,
            'autopilot_features': 'ActiveTrack 5.0, Point of Interest 3.0, Waypoints 2.0',
            'wifi_enabled': True,
            'bluetooth_enabled': True,
            'cellular_enabled': False,
            'operating_temperature_min': -10,
            'operating_temperature_max': 40,
            'wind_resistance': 12,
            'water_resistance_rating': 'IP54',
            'certification_level': 'CE, FCC, IC',
            'flight_zone_restrictions': 'Standard GEO zones, Airport restrictions',
            'intended_use': 'Professional photography, videography, mapping',
            'skill_level_required': 'intermediate',
            'warranty_period': 12,
            'availability_status': 'available',
            'requires_license': False,
            'is_active': True
        },
        {
            'product_code': 'PARROT-ANAFI',
            'product_name': 'Parrot ANAFI USA',
            'description': 'Secure drone platform designed for government and enterprise use',
            'company_name': 'Parrot SA',
            'category_name': 'Commercial Survey',
            'manufacturer': 'Parrot',
            'model_year': 2020,
            'price': 7000.00,
            'max_flight_time': 32,
            'max_range': 5000,
            'max_altitude': 4500,
            'max_speed': 55,
            'weight': 500,
            'dimensions_length': 244,
            'dimensions_width': 67,
            'dimensions_height': 65,
            'camera_resolution': '21MP, 4K Video',
            'payload_capacity': 0,
            'battery_type': 'Li-Po 3S',
            'battery_capacity': 2700,
            'charging_time': 120,
            'gps_enabled': True,
            'control_range': 5000,
            'autopilot_features': 'Flight Plan, Follow Me, SmartDronies',
            'wifi_enabled': True,
            'bluetooth_enabled': True,
            'cellular_enabled': True,
            'operating_temperature_min': -10,
            'operating_temperature_max': 50,
            'wind_resistance': 14,
            'water_resistance_rating': 'IP53',
            'certification_level': 'NDAA Compliant, Blue UAS',
            'flight_zone_restrictions': 'Configurable geofencing',
            'intended_use': 'Government surveillance, enterprise inspection',
            'skill_level_required': 'advanced',
            'warranty_period': 24,
            'availability_status': 'available',
            'requires_license': True,
            'is_active': True
        },
        {
            'product_code': 'SKYDIO-S2',
            'product_name': 'Skydio 2+',
            'description': 'Autonomous drone with advanced AI and obstacle avoidance',
            'company_name': 'Skydio Inc.',
            'category_name': 'Professional Photography',
            'manufacturer': 'Skydio',
            'model_year': 2020,
            'price': 1099.00,
            'max_flight_time': 27,
            'max_range': 3500,
            'max_altitude': 4000,
            'max_speed': 58,
            'weight': 775,
            'dimensions_length': 273,
            'dimensions_width': 273,
            'dimensions_height': 89,
            'camera_resolution': '12.3MP, 4K60 Video',
            'payload_capacity': 0,
            'battery_type': 'Li-Po 3S',
            'battery_capacity': 4280,
            'charging_time': 180,
            'gps_enabled': True,
            'control_range': 3500,
            'autopilot_features': 'Full autonomy, 360° obstacle avoidance, Subject tracking',
            'wifi_enabled': True,
            'bluetooth_enabled': True,
            'cellular_enabled': False,
            'operating_temperature_min': -10,
            'operating_temperature_max': 40,
            'wind_resistance': 11,
            'water_resistance_rating': 'IP44',
            'certification_level': 'FCC, IC',
            'flight_zone_restrictions': 'Standard FAA regulations',
            'intended_use': 'Autonomous filming, inspection, security',
            'skill_level_required': 'beginner',
            'warranty_period': 12,
            'availability_status': 'available',
            'requires_license': False,
            'is_active': True
        },
        {
            'product_code': 'AUTEL-EVO2',
            'product_name': 'Autel EVO II Pro',
            'description': 'Professional drone with 6K camera and 40-minute flight time',
            'company_name': 'Autel Robotics',
            'category_name': 'Professional Photography',
            'manufacturer': 'Autel',
            'model_year': 2021,
            'price': 1795.00,
            'max_flight_time': 40,
            'max_range': 9000,
            'max_altitude': 7000,
            'max_speed': 72,
            'weight': 1127,
            'dimensions_length': 357,
            'dimensions_width': 269,
            'dimensions_height': 132,
            'camera_resolution': '20MP, 6K Video',
            'payload_capacity': 0,
            'battery_type': 'Li-Po 4S',
            'battery_capacity': 7100,
            'charging_time': 120,
            'gps_enabled': True,
            'control_range': 9000,
            'autopilot_features': 'Dynamic Track 2.0, Orbit, Waypoint',
            'wifi_enabled': True,
            'bluetooth_enabled': True,
            'cellular_enabled': False,
            'operating_temperature_min': -10,
            'operating_temperature_max': 45,
            'wind_resistance': 10,
            'water_resistance_rating': 'IP43',
            'certification_level': 'CE, FCC',
            'flight_zone_restrictions': 'Standard airspace restrictions',
            'intended_use': 'Professional photography, surveying, inspection',
            'skill_level_required': 'intermediate',
            'warranty_period': 12,
            'availability_status': 'available',
            'requires_license': False,
            'is_active': True
        },
        {
            'product_code': 'YUNEEC-H520',
            'product_name': 'Yuneec Typhoon H520',
            'description': 'Commercial hexacopter for professional applications',
            'company_name': 'Yuneec International',
            'category_name': 'Commercial Survey',
            'manufacturer': 'Yuneec',
            'model_year': 2019,
            'price': 3500.00,
            'max_flight_time': 28,
            'max_range': 2000,
            'max_altitude': 2500,
            'max_speed': 50,
            'weight': 1950,
            'dimensions_length': 520,
            'dimensions_width': 450,
            'dimensions_height': 300,
            'camera_resolution': '20MP, 4K Video',
            'payload_capacity': 400,
            'battery_type': 'Li-Po 4S',
            'battery_capacity': 5400,
            'charging_time': 150,
            'gps_enabled': True,
            'control_range': 2000,
            'autopilot_features': 'Mission Planning, Orbit Mode, Point of Interest',
            'wifi_enabled': True,
            'bluetooth_enabled': False,
            'cellular_enabled': False,
            'operating_temperature_min': -10,
            'operating_temperature_max': 40,
            'wind_resistance': 14,
            'water_resistance_rating': 'IP45',
            'certification_level': 'CE, FCC, IC',
            'flight_zone_restrictions': 'Professional use zones',
            'intended_use': 'Professional mapping, inspection, surveillance',
            'skill_level_required': 'advanced',
            'warranty_period': 24,
            'availability_status': 'available',
            'requires_license': True,
            'is_active': True
        }
    ]
    
    # Create company and category lookup dictionaries
    company_lookup = {c.name: c for c in companies}
    category_lookup = {c.name: c for c in categories}
    
    for product_data in products_data:
        product = Product.query.filter_by(product_code=product_data['product_code']).first()
        if not product:
            # Get company and category objects
            company = company_lookup.get(product_data.pop('company_name'))
            category = category_lookup.get(product_data.pop('category_name'))
            
            if company and category:
                product = Product(
                    owner_company_id=company.id,
                    category_id=category.id,
                    created_by_id=admin_user.id,
                    **product_data
                )
                db.session.add(product)
                print(f"Created product: {product.product_name}")
    
    db.session.commit()

def main():
    """Main initialization function."""
    app = create_app()
    
    with app.app_context():
        print("Initializing Product Master module...")
        
        # Create all tables
        db.create_all()
        print("Database tables created.")
        
        # Initialize categories
        print("\nCreating product categories...")
        categories = init_product_categories()
        
        # Initialize companies
        print("\nCreating companies...")
        companies = init_companies()
        
        # Initialize sample products
        print("\nCreating sample products...")
        init_sample_products(categories, companies)
        
        print(f"\nInitialization complete!")
        print(f"Created {len(categories)} categories")
        print(f"Created {len(companies)} companies")
        print(f"Created {Product.query.count()} products")

if __name__ == '__main__':
    main()
