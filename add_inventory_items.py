# Script to add UAV inventory items (spare parts) for each product
from app import create_app, db
from app.models import Product, InventoryCategory, InventoryItem
from datetime import datetime, timedelta
import random

# Define inventory categories for UAV parts
inventory_categories = [
    {"name": "Propellers & Rotors", "description": "Propellers, rotor blades, and related hardware"},
    {"name": "Batteries & Power", "description": "Batteries, chargers, and power management systems"},
    {"name": "Cameras & Gimbals", "description": "Camera modules, gimbal systems, and imaging components"},
    {"name": "Flight Controllers", "description": "Flight control boards, autopilot systems, and navigation"},
    {"name": "Motors & ESCs", "description": "Motors, electronic speed controllers, and drive systems"},
    {"name": "Landing Gear", "description": "Landing gear, skids, and ground contact equipment"},
    {"name": "Communication", "description": "Radio modules, antennas, and communication systems"},
    {"name": "Sensors", "description": "GPS modules, IMU sensors, and measurement devices"},
    {"name": "Frame & Body", "description": "Frame parts, body panels, and structural components"},
]

# Common UAV part templates by category
part_templates = {
    "Propellers & Rotors": [
        {"name": "Carbon Fiber Propeller Set", "desc": "High-performance carbon fiber propeller pair", "cost": 45.00, "stock": 25, "min_stock": 5},
        {"name": "Quick-Release Propeller", "desc": "Tool-free quick-release propeller system", "cost": 35.00, "stock": 30, "min_stock": 8},
        {"name": "Folding Propeller Blade", "desc": "Foldable propeller for compact storage", "cost": 55.00, "stock": 20, "min_stock": 4},
    ],
    "Batteries & Power": [
        {"name": "LiPo Battery Pack", "desc": "High-capacity lithium polymer battery", "cost": 120.00, "stock": 15, "min_stock": 3},
        {"name": "Smart Charging Hub", "desc": "Multi-battery intelligent charging station", "cost": 85.00, "stock": 10, "min_stock": 2},
        {"name": "Battery Power Indicator", "desc": "LED battery level indicator module", "cost": 25.00, "stock": 40, "min_stock": 10},
    ],
    "Cameras & Gimbals": [
        {"name": "Gimbal Motor Assembly", "desc": "3-axis gimbal motor replacement unit", "cost": 180.00, "stock": 8, "min_stock": 2},
        {"name": "Camera Lens Filter", "desc": "UV/ND filter for camera protection", "cost": 30.00, "stock": 35, "min_stock": 8},
        {"name": "Gimbal Control Board", "desc": "Electronic control board for gimbal system", "cost": 95.00, "stock": 12, "min_stock": 3},
    ],
    "Flight Controllers": [
        {"name": "Flight Control Module", "desc": "Main flight control computer board", "cost": 220.00, "stock": 6, "min_stock": 2},
        {"name": "IMU Sensor Board", "desc": "Inertial measurement unit sensor", "cost": 65.00, "stock": 18, "min_stock": 4},
        {"name": "Barometer Module", "desc": "Atmospheric pressure sensor for altitude", "cost": 40.00, "stock": 22, "min_stock": 5},
    ],
    "Motors & ESCs": [
        {"name": "Brushless Motor", "desc": "High-efficiency brushless drive motor", "cost": 75.00, "stock": 20, "min_stock": 4},
        {"name": "Electronic Speed Controller", "desc": "ESC for motor speed control", "cost": 55.00, "stock": 25, "min_stock": 6},
        {"name": "Motor Mount Hardware", "desc": "Screws and brackets for motor mounting", "cost": 15.00, "stock": 50, "min_stock": 12},
    ],
    "Landing Gear": [
        {"name": "Retractable Landing Gear", "desc": "Electric retractable landing gear set", "cost": 165.00, "stock": 8, "min_stock": 2},
        {"name": "Landing Skid Set", "desc": "Fixed landing skids for stable landing", "cost": 25.00, "stock": 30, "min_stock": 6},
        {"name": "Shock Absorber Strut", "desc": "Dampening strut for landing impact", "cost": 45.00, "stock": 18, "min_stock": 4},
    ],
    "Communication": [
        {"name": "Radio Telemetry Module", "desc": "Long-range radio communication module", "cost": 85.00, "stock": 15, "min_stock": 3},
        {"name": "Antenna System", "desc": "Omnidirectional communication antenna", "cost": 35.00, "stock": 28, "min_stock": 6},
        {"name": "Video Transmitter", "desc": "Real-time video transmission module", "cost": 125.00, "stock": 12, "min_stock": 3},
    ],
    "Sensors": [
        {"name": "GPS Module", "desc": "High-precision GPS navigation module", "cost": 65.00, "stock": 20, "min_stock": 4},
        {"name": "Ultrasonic Distance Sensor", "desc": "Ground proximity detection sensor", "cost": 28.00, "stock": 25, "min_stock": 6},
        {"name": "Optical Flow Sensor", "desc": "Visual positioning sensor for indoor flight", "cost": 95.00, "stock": 15, "min_stock": 3},
    ],
    "Frame & Body": [
        {"name": "Carbon Fiber Frame Arm", "desc": "Replacement carbon fiber frame arm", "cost": 45.00, "stock": 16, "min_stock": 4},
        {"name": "Body Shell Panel", "desc": "Protective body shell cover panel", "cost": 35.00, "stock": 20, "min_stock": 5},
        {"name": "Mounting Bracket Set", "desc": "Universal mounting brackets and hardware", "cost": 20.00, "stock": 35, "min_stock": 8},
    ],
}

app = create_app()
with app.app_context():
    print("Creating inventory categories and items for UAV products...")
    
    # First, create inventory categories
    created_categories = {}
    for cat_data in inventory_categories:
        existing_cat = InventoryCategory.query.filter_by(name=cat_data["name"]).first()
        if not existing_cat:
            category = InventoryCategory(
                name=cat_data["name"],
                description=cat_data["description"]
            )
            db.session.add(category)
            db.session.flush()  # Get the ID
            created_categories[cat_data["name"]] = category
            print(f"✓ Created category: {cat_data['name']}")
        else:
            created_categories[cat_data["name"]] = existing_cat
            print(f"- Category exists: {cat_data['name']}")
    
    db.session.commit()
    
    # Get all products
    products = Product.query.all()
    print(f"\nFound {len(products)} products to create inventory for...")
    
    # Create inventory items for each product
    for product in products:
        print(f"\n📦 Creating inventory items for: {product.product_name}")
        
        # For each category, create 3 parts specific to this product
        for category_name, category_obj in created_categories.items():
            if category_name in part_templates:
                templates = part_templates[category_name]
                
                for i, template in enumerate(templates):
                    # Create unique part number
                    part_number = f"{product.product_code}-{category_name.upper().replace(' ', '').replace('&', '')[:4]}-{i+1:02d}"
                    
                    # Check if part already exists
                    existing_part = InventoryItem.query.filter_by(part_number=part_number).first()
                    if not existing_part:
                        # Create product-specific part name
                        part_name = f"{product.manufacturer} {template['name']}"
                        
                        # Add some randomization to stock and costs
                        base_cost = template['cost']
                        cost_variation = random.uniform(0.8, 1.2)  # ±20% variation
                        actual_cost = round(base_cost * cost_variation, 2)
                        
                        stock_variation = random.randint(-5, 10)
                        actual_stock = max(0, template['stock'] + stock_variation)
                        
                        inventory_item = InventoryItem(
                            part_number=part_number,
                            name=part_name,
                            description=f"{template['desc']} - Compatible with {product.product_name}",
                            manufacturer=product.manufacturer,
                            model=product.product_code,
                            quantity_in_stock=actual_stock,
                            minimum_stock_level=template['min_stock'],
                            maximum_stock_level=template['stock'] + 20,
                            unit_cost=actual_cost,
                            compatible_uav_models=product.product_name,
                            category_id=category_obj.id,
                            is_active=True,
                            weight=round(random.uniform(0.01, 2.5), 3),  # Random weight 10g to 2.5kg
                            dimensions=f"{random.randint(2,15)}x{random.randint(2,10)}x{random.randint(1,5)} cm"
                        )
                        
                        # Sometimes set a last restocked date
                        if random.choice([True, False]):
                            days_ago = random.randint(1, 90)
                            inventory_item.last_restocked = datetime.now() - timedelta(days=days_ago)
                        
                        db.session.add(inventory_item)
                        print(f"  ✓ {category_name}: {part_name} (Stock: {actual_stock}, Cost: ${actual_cost})")
                    else:
                        print(f"  - Exists: {part_number}")
    
    db.session.commit()
    
    # Print summary
    total_items = InventoryItem.query.count()
    total_categories = InventoryCategory.query.count()
    low_stock_items = InventoryItem.query.filter(InventoryItem.quantity_in_stock <= InventoryItem.minimum_stock_level).count()
    
    print(f"\n✅ Inventory setup complete!")
    print(f"📊 Summary:")
    print(f"   - Total Categories: {total_categories}")
    print(f"   - Total Items: {total_items}")
    print(f"   - Low Stock Items: {low_stock_items}")
    print(f"   - Total Inventory Value: ${InventoryItem.query.with_entities(db.func.sum(InventoryItem.quantity_in_stock * InventoryItem.unit_cost)).scalar() or 0:.2f}")
