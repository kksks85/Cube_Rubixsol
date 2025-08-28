# Script to add sample UAV products for each company
from app import create_app, db
from app.models import Company, Product, ProductCategory
from datetime import datetime, timedelta
import random

# Sample products for each company
company_products = {
    "DJI": [
        {
            "product_code": "DJI-M300",
            "product_name": "Mavic 3 Enterprise",
            "description": "Professional drone with 4/3 CMOS Hasselblad camera and advanced flight performance",
            "manufacturer": "DJI",
            "max_flight_time": 46,
            "max_range": 15000,
            "max_altitude": 6000,
            "max_speed": 75,
            "weight": 0.895,
            "camera_resolution": "20MP",
            "gps_enabled": True,
            "wifi_enabled": True,
            "price": 5500.00,
            "intended_use": "Commercial Survey",
            "skill_level_required": "Intermediate",
            "availability_status": "Available"
        },
        {
            "product_code": "DJI-M30T",
            "product_name": "Matrice 30T",
            "description": "Thermal imaging drone with dual cameras for industrial inspections",
            "manufacturer": "DJI",
            "max_flight_time": 41,
            "max_range": 12000,
            "max_altitude": 7000,
            "max_speed": 82,
            "weight": 3.7,
            "camera_resolution": "48MP",
            "gps_enabled": True,
            "wifi_enabled": True,
            "price": 15000.00,
            "intended_use": "Thermal Inspection",
            "skill_level_required": "Advanced",
            "availability_status": "Available"
        }
    ],
    "Parrot": [
        {
            "product_code": "PAR-ANAFI",
            "product_name": "ANAFI Ai",
            "description": "4G connected drone with AI-powered autonomous flight capabilities",
            "manufacturer": "Parrot",
            "max_flight_time": 32,
            "max_range": 10000,
            "max_altitude": 4500,
            "max_speed": 65,
            "weight": 0.89,
            "camera_resolution": "48MP",
            "gps_enabled": True,
            "cellular_enabled": True,
            "price": 4500.00,
            "intended_use": "Security Surveillance",
            "skill_level_required": "Intermediate",
            "availability_status": "Available"
        },
        {
            "product_code": "PAR-DISCO",
            "product_name": "Disco-Pro AG",
            "description": "Fixed-wing mapping drone for precision agriculture",
            "manufacturer": "Parrot",
            "max_flight_time": 90,
            "max_range": 20000,
            "max_altitude": 5000,
            "max_speed": 85,
            "weight": 1.6,
            "camera_resolution": "20MP",
            "gps_enabled": True,
            "wifi_enabled": True,
            "price": 12000.00,
            "intended_use": "Agricultural Mapping",
            "skill_level_required": "Advanced",
            "availability_status": "Available"
        }
    ],
    "Skydio": [
        {
            "product_code": "SKY-S2PLUS",
            "product_name": "Skydio 2+",
            "description": "AI-powered autonomous drone with advanced obstacle avoidance",
            "manufacturer": "Skydio",
            "max_flight_time": 27,
            "max_range": 6000,
            "max_altitude": 4500,
            "max_speed": 58,
            "weight": 0.775,
            "camera_resolution": "12.3MP",
            "gps_enabled": True,
            "wifi_enabled": True,
            "price": 1350.00,
            "intended_use": "Autonomous Filming",
            "skill_level_required": "Beginner",
            "availability_status": "Available"
        },
        {
            "product_code": "SKY-X2D",
            "product_name": "Skydio X2D",
            "description": "Military-grade autonomous drone for defense applications",
            "manufacturer": "Skydio",
            "max_flight_time": 35,
            "max_range": 10000,
            "max_altitude": 6000,
            "max_speed": 72,
            "weight": 2.2,
            "camera_resolution": "20MP",
            "gps_enabled": True,
            "cellular_enabled": True,
            "price": 25000.00,
            "intended_use": "Defense Operations",
            "skill_level_required": "Expert",
            "availability_status": "Available"
        }
    ],
    "Autel Robotics": [
        {
            "product_code": "AUT-EVO2",
            "product_name": "EVO II Pro",
            "description": "Professional drone with 6K camera and 40-minute flight time",
            "manufacturer": "Autel Robotics",
            "max_flight_time": 40,
            "max_range": 9000,
            "max_altitude": 5500,
            "max_speed": 78,
            "weight": 1.127,
            "camera_resolution": "20MP",
            "gps_enabled": True,
            "wifi_enabled": True,
            "price": 1795.00,
            "intended_use": "Professional Photography",
            "skill_level_required": "Intermediate",
            "availability_status": "Available"
        },
        {
            "product_code": "AUT-DRAGONFISH",
            "product_name": "Dragonfish Pro",
            "description": "VTOL fixed-wing drone for long-range surveying missions",
            "manufacturer": "Autel Robotics",
            "max_flight_time": 180,
            "max_range": 30000,
            "max_altitude": 4000,
            "max_speed": 108,
            "weight": 4.5,
            "camera_resolution": "20MP",
            "gps_enabled": True,
            "cellular_enabled": True,
            "price": 35000.00,
            "intended_use": "Long Range Survey",
            "skill_level_required": "Expert",
            "availability_status": "Available"
        }
    ],
    "Teledyne FLIR": [
        {
            "product_code": "FLIR-SIRAS",
            "product_name": "SIRAS Professional",
            "description": "Dual-sensor drone with RGB and thermal imaging capabilities",
            "manufacturer": "Teledyne FLIR",
            "max_flight_time": 31,
            "max_range": 7500,
            "max_altitude": 4600,
            "max_speed": 72,
            "weight": 1.37,
            "camera_resolution": "12.8MP",
            "gps_enabled": True,
            "wifi_enabled": True,
            "price": 7200.00,
            "intended_use": "Thermal Inspection",
            "skill_level_required": "Intermediate",
            "availability_status": "Available"
        },
        {
            "product_code": "FLIR-BLACKHORNET",
            "product_name": "Black Hornet 4",
            "description": "Nano reconnaissance drone for military and law enforcement",
            "manufacturer": "Teledyne FLIR",
            "max_flight_time": 25,
            "max_range": 2000,
            "max_altitude": 500,
            "max_speed": 21,
            "weight": 0.033,
            "camera_resolution": "2MP",
            "gps_enabled": True,
            "wifi_enabled": False,
            "price": 195000.00,
            "intended_use": "Military Reconnaissance",
            "skill_level_required": "Expert",
            "availability_status": "Available"
        }
    ],
    "senseFly": [
        {
            "product_code": "SF-EBEE-X",
            "product_name": "eBee X Fixed Wing",
            "description": "Professional mapping drone with RTK/PPK GNSS accuracy",
            "manufacturer": "senseFly",
            "max_flight_time": 90,
            "max_range": 25000,
            "max_altitude": 5500,
            "max_speed": 90,
            "weight": 1.6,
            "camera_resolution": "42MP",
            "gps_enabled": True,
            "wifi_enabled": True,
            "price": 15000.00,
            "intended_use": "Professional Mapping",
            "skill_level_required": "Advanced",
            "availability_status": "Available"
        },
        {
            "product_code": "SF-ALBRIS",
            "product_name": "Albris Indoor Drone",
            "description": "Collision-tolerant indoor inspection drone with thermal camera",
            "manufacturer": "senseFly",
            "max_flight_time": 15,
            "max_range": 200,
            "max_altitude": 100,
            "max_speed": 18,
            "weight": 0.49,
            "camera_resolution": "4K",
            "gps_enabled": False,
            "wifi_enabled": True,
            "price": 8500.00,
            "intended_use": "Indoor Inspection",
            "skill_level_required": "Intermediate",
            "availability_status": "Available"
        }
    ],
    "Delair": [
        {
            "product_code": "DEL-UX11",
            "product_name": "UX11 AG",
            "description": "Long-range fixed-wing drone for precision agriculture",
            "manufacturer": "Delair",
            "max_flight_time": 110,
            "max_range": 30000,
            "max_altitude": 4000,
            "max_speed": 95,
            "weight": 2.4,
            "camera_resolution": "24MP",
            "gps_enabled": True,
            "cellular_enabled": True,
            "price": 18000.00,
            "intended_use": "Agricultural Survey",
            "skill_level_required": "Advanced",
            "availability_status": "Available"
        },
        {
            "product_code": "DEL-DT26X",
            "product_name": "DT26X LiDAR",
            "description": "VTOL drone with integrated LiDAR for 3D mapping",
            "manufacturer": "Delair",
            "max_flight_time": 55,
            "max_range": 15000,
            "max_altitude": 3500,
            "max_speed": 80,
            "weight": 7.5,
            "camera_resolution": "42MP",
            "gps_enabled": True,
            "wifi_enabled": True,
            "price": 75000.00,
            "intended_use": "LiDAR Mapping",
            "skill_level_required": "Expert",
            "availability_status": "Available"
        }
    ],
    "AeroVironment": [
        {
            "product_code": "AERO-QUANTIX",
            "product_name": "Quantix Recon",
            "description": "Hybrid VTOL drone for rapid area reconnaissance",
            "manufacturer": "AeroVironment",
            "max_flight_time": 45,
            "max_range": 15000,
            "max_altitude": 4500,
            "max_speed": 85,
            "weight": 2.6,
            "camera_resolution": "61MP",
            "gps_enabled": True,
            "wifi_enabled": True,
            "price": 35000.00,
            "intended_use": "Military Reconnaissance",
            "skill_level_required": "Expert",
            "availability_status": "Available"
        },
        {
            "product_code": "AERO-PUMA",
            "product_name": "Puma 3 AE",
            "description": "All-environment unmanned aircraft system for surveillance",
            "manufacturer": "AeroVironment",
            "max_flight_time": 140,
            "max_range": 20000,
            "max_altitude": 4600,
            "max_speed": 83,
            "weight": 6.8,
            "camera_resolution": "HD",
            "gps_enabled": True,
            "cellular_enabled": True,
            "price": 250000.00,
            "intended_use": "Military Surveillance",
            "skill_level_required": "Expert",
            "availability_status": "Available"
        }
    ]
}

app = create_app()
with app.app_context():
    # First, let's create a default category if it doesn't exist
    default_category = ProductCategory.query.filter_by(name="UAV/Drone").first()
    if not default_category:
        default_category = ProductCategory(
            name="UAV/Drone",
            description="Unmanned Aerial Vehicles and Drones",
            code="UAV"
        )
        db.session.add(default_category)
        db.session.commit()
        print("Created default UAV category")

    # Add products for each company
    for company_name, products in company_products.items():
        company = Company.query.filter_by(name=company_name).first()
        if company:
            print(f"\nAdding products for {company_name}:")
            for product_data in products:
                # Check if product already exists
                existing = Product.query.filter_by(product_code=product_data["product_code"]).first()
                if not existing:
                    product = Product(
                        product_code=product_data["product_code"],
                        product_name=product_data["product_name"],
                        description=product_data["description"],
                        manufacturer=product_data["manufacturer"],
                        category_id=default_category.id,
                        owner_company_id=company.id,
                        created_by_id=1,  # Assuming admin user ID is 1
                        
                        # Flight Performance
                        max_flight_time=product_data.get("max_flight_time"),
                        max_range=product_data.get("max_range"),
                        max_altitude=product_data.get("max_altitude"),
                        max_speed=product_data.get("max_speed"),
                        
                        # Physical
                        weight=product_data.get("weight"),
                        
                        # Camera
                        camera_resolution=product_data.get("camera_resolution"),
                        
                        # Navigation
                        gps_enabled=product_data.get("gps_enabled", False),
                        wifi_enabled=product_data.get("wifi_enabled", False),
                        cellular_enabled=product_data.get("cellular_enabled", False),
                        
                        # Commercial
                        price=product_data.get("price"),
                        
                        # Operational
                        intended_use=product_data.get("intended_use"),
                        skill_level_required=product_data.get("skill_level_required"),
                        availability_status=product_data.get("availability_status", "Available"),
                        
                        # Status
                        is_active=True
                    )
                    
                    # Set some random service dates for demo purposes
                    if random.choice([True, False]):
                        product.last_serviced = datetime.now() - timedelta(days=random.randint(30, 365))
                        product.update_next_service_due()
                    
                    db.session.add(product)
                    print(f"  ✓ Added: {product_data['product_name']}")
                else:
                    print(f"  - Exists: {product_data['product_name']}")
        else:
            print(f"Company {company_name} not found!")
    
    db.session.commit()
    print(f"\n✅ Done! Added products to database.")
