"""
Service Management System Setup Script
Creates sample service categories, incidents, and integrates with existing data
"""

from app import create_app, db
from app.models import (ServiceCategory, ServiceIncident, Product, User, 
                       InventoryItem, ServicePart, ServiceActivity, ServiceSoftwareUpdate)
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    print('Setting up Service Management System...')
    
    # Create service tables
    db.create_all()
    
    # Create default service categories if they don't exist
    if ServiceCategory.query.count() == 0:
        print('Creating service categories...')
        
        categories = [
            {
                'name': 'Motor Failure',
                'description': 'Issues with UAV motor systems including brushless motors, ESCs, and propellers',
                'category_type': 'HARDWARE',
                'severity_level': 'HIGH',
                'estimated_service_time': 4,
                'requires_parts': True,
                'requires_software_update': False,
                'requires_firmware_update': False
            },
            {
                'name': 'Flight Controller Issues',
                'description': 'Problems with flight control systems, autopilot malfunctions, and control failures',
                'category_type': 'HARDWARE',
                'severity_level': 'CRITICAL',
                'estimated_service_time': 6,
                'requires_parts': True,
                'requires_software_update': False,
                'requires_firmware_update': True
            },
            {
                'name': 'Camera System Malfunction',
                'description': 'Camera hardware failures, gimbal issues, and imaging system problems',
                'category_type': 'HARDWARE',
                'severity_level': 'MEDIUM',
                'estimated_service_time': 3,
                'requires_parts': True,
                'requires_software_update': True,
                'requires_firmware_update': False
            },
            {
                'name': 'Battery & Power Issues',
                'description': 'Battery cell failures, charging problems, and power distribution issues',
                'category_type': 'HARDWARE',
                'severity_level': 'HIGH',
                'estimated_service_time': 2,
                'requires_parts': True,
                'requires_software_update': False,
                'requires_firmware_update': False
            },
            {
                'name': 'Software Configuration Error',
                'description': 'App configuration issues, parameter setup problems, and software crashes',
                'category_type': 'SOFTWARE',
                'severity_level': 'MEDIUM',
                'estimated_service_time': 2,
                'requires_parts': False,
                'requires_software_update': True,
                'requires_firmware_update': False
            },
            {
                'name': 'Firmware Update Required',
                'description': 'Firmware bugs, outdated firmware versions, and compatibility issues',
                'category_type': 'FIRMWARE',
                'severity_level': 'MEDIUM',
                'estimated_service_time': 1,
                'requires_parts': False,
                'requires_software_update': False,
                'requires_firmware_update': True
            },
            {
                'name': 'GPS/Navigation Failure',
                'description': 'GPS signal loss, compass calibration issues, and navigation system failures',
                'category_type': 'HARDWARE',
                'severity_level': 'HIGH',
                'estimated_service_time': 3,
                'requires_parts': True,
                'requires_software_update': False,
                'requires_firmware_update': True
            },
            {
                'name': 'Communication System Failure',
                'description': 'Radio link problems, telemetry issues, and data transmission failures',
                'category_type': 'HARDWARE',
                'severity_level': 'HIGH',
                'estimated_service_time': 4,
                'requires_parts': True,
                'requires_software_update': True,
                'requires_firmware_update': False
            },
            {
                'name': 'Structural Damage',
                'description': 'Physical damage to airframe, landing gear, and protective casing',
                'category_type': 'HARDWARE',
                'severity_level': 'MEDIUM',
                'estimated_service_time': 5,
                'requires_parts': True,
                'requires_software_update': False,
                'requires_firmware_update': False
            },
            {
                'name': 'Routine Maintenance',
                'description': 'Scheduled maintenance, preventive inspections, and component replacements',
                'category_type': 'MAINTENANCE',
                'severity_level': 'LOW',
                'estimated_service_time': 2,
                'requires_parts': True,
                'requires_software_update': False,
                'requires_firmware_update': False
            },
            {
                'name': 'Safety Inspection',
                'description': 'Regulatory compliance checks, safety audits, and certification renewals',
                'category_type': 'INSPECTION',
                'severity_level': 'MEDIUM',
                'estimated_service_time': 3,
                'requires_parts': False,
                'requires_software_update': False,
                'requires_firmware_update': False
            },
            {
                'name': 'Performance Degradation',
                'description': 'Reduced flight time, decreased responsiveness, and general performance issues',
                'category_type': 'MAINTENANCE',
                'severity_level': 'MEDIUM',
                'estimated_service_time': 4,
                'requires_parts': True,
                'requires_software_update': True,
                'requires_firmware_update': False
            }
        ]
        
        category_objects = {}
        for cat_data in categories:
            category = ServiceCategory(
                name=cat_data['name'],
                description=cat_data['description'],
                category_type=cat_data['category_type'],
                severity_level=cat_data['severity_level'],
                estimated_service_time=cat_data['estimated_service_time'],
                requires_parts=cat_data['requires_parts'],
                requires_software_update=cat_data['requires_software_update'],
                requires_firmware_update=cat_data['requires_firmware_update']
            )
            db.session.add(category)
            category_objects[cat_data['name']] = category
        
        db.session.commit()
        print(f'Created {len(categories)} service categories')
        
        # Create sample service incidents if we have products and users
        products = Product.query.limit(5).all()
        users = User.query.limit(3).all()
        
        if products and users and ServiceIncident.query.count() == 0:
            print('Creating sample service incidents...')
            
            incident_data = [
                {
                    'title': 'Motor 2 Not Starting - DJI Matrice',
                    'description': 'Customer reports that motor 2 fails to start during pre-flight checks. UAV shows error code M02_FAIL on display.',
                    'symptoms': 'Motor 2 does not spin during startup sequence, error beeping pattern heard',
                    'incident_type': 'REPAIR',
                    'priority': 'HIGH',
                    'category': 'Motor Failure',
                    'customer_name': 'Aviation Solutions Ltd',
                    'customer_email': 'service@aviationsolutions.com',
                    'customer_phone': '+1-555-0123',
                    'software_version_before': 'v2.1.5',
                    'firmware_version_before': 'FC_v1.8.2',
                    'estimated_cost': 450.00
                },
                {
                    'title': 'Camera Gimbal Drift Issue',
                    'description': 'Camera gimbal slowly drifts during flight causing unstable footage. Issue started after recent firmware update.',
                    'symptoms': 'Camera slowly tilts downward during flight, vibration in footage',
                    'incident_type': 'WARRANTY',
                    'priority': 'MEDIUM',
                    'category': 'Camera System Malfunction',
                    'customer_name': 'SkyVision Media',
                    'customer_email': 'tech@skyvision.com',
                    'customer_phone': '+1-555-0234',
                    'software_version_before': 'v2.2.1',
                    'firmware_version_before': 'GMB_v1.5.3',
                    'estimated_cost': 0.00
                },
                {
                    'title': 'GPS Signal Loss in Flight',
                    'description': 'UAV loses GPS signal intermittently during flight operations, causing Return-to-Home failures.',
                    'symptoms': 'GPS signal drops to 0 satellites randomly, position hold fails',
                    'incident_type': 'REPAIR',
                    'priority': 'CRITICAL',
                    'category': 'GPS/Navigation Failure',
                    'customer_name': 'Precision Agriculture Inc',
                    'customer_email': 'support@precisionag.com',
                    'customer_phone': '+1-555-0345',
                    'software_version_before': 'v2.1.8',
                    'firmware_version_before': 'GPS_v2.1.1',
                    'estimated_cost': 680.00
                },
                {
                    'title': 'Battery Not Charging Properly',
                    'description': 'Battery pack shows charging but never reaches full capacity. Flight time reduced to 8 minutes from normal 25 minutes.',
                    'symptoms': 'Charging LED stays yellow, capacity indicator shows 60% max',
                    'incident_type': 'REPAIR',
                    'priority': 'HIGH',
                    'category': 'Battery & Power Issues',
                    'customer_name': 'Coastal Survey Services',
                    'customer_email': 'maintenance@coastalsurvey.com',
                    'customer_phone': '+1-555-0456',
                    'software_version_before': 'v2.2.0',
                    'firmware_version_before': 'BAT_v1.3.2',
                    'estimated_cost': 320.00
                },
                {
                    'title': 'Routine 100-Hour Inspection',
                    'description': 'Scheduled maintenance inspection at 100 flight hours. Customer requests full system check and component replacement as needed.',
                    'symptoms': 'No specific issues reported, routine maintenance',
                    'incident_type': 'MAINTENANCE',
                    'priority': 'LOW',
                    'category': 'Routine Maintenance',
                    'customer_name': 'Professional Drone Services',
                    'customer_email': 'ops@prodroneservices.com',
                    'customer_phone': '+1-555-0567',
                    'software_version_before': 'v2.1.9',
                    'firmware_version_before': 'FC_v1.8.4',
                    'estimated_cost': 250.00
                }
            ]
            
            for i, inc_data in enumerate(incident_data, 1):
                # Generate incident number
                incident_number = f"SVC-{datetime.now().strftime('%Y%m%d')}-{i:04d}"
                
                # Get category
                category = category_objects.get(inc_data['category'])
                
                # Create incident
                incident = ServiceIncident(
                    incident_number=incident_number,
                    title=inc_data['title'],
                    description=inc_data['description'],
                    symptoms=inc_data['symptoms'],
                    incident_type=inc_data['incident_type'],
                    priority=inc_data['priority'],
                    product_id=random.choice(products).id,
                    category_id=category.id if category else None,
                    technician_id=random.choice(users).id,
                    customer_name=inc_data['customer_name'],
                    customer_email=inc_data['customer_email'],
                    customer_phone=inc_data['customer_phone'],
                    software_version_before=inc_data['software_version_before'],
                    firmware_version_before=inc_data['firmware_version_before'],
                    estimated_cost=inc_data['estimated_cost'],
                    estimated_completion_date=datetime.now() + timedelta(days=random.randint(3, 14)),
                    received_date=datetime.now() - timedelta(days=random.randint(1, 5)),
                    created_by_id=users[0].id,
                    status='IN_PROGRESS' if i <= 3 else 'RECEIVED'
                )
                
                db.session.add(incident)
                db.session.flush()  # Get the incident ID
                
                # Add initial activity
                activity = ServiceActivity(
                    service_incident_id=incident.id,
                    user_id=users[0].id,
                    activity_type='received',
                    description=f'Service incident created: {incident.title}',
                    is_customer_visible=True
                )
                db.session.add(activity)
                
                # Add diagnosis activity for in-progress incidents
                if incident.status == 'IN_PROGRESS':
                    diagnosis_activity = ServiceActivity(
                        service_incident_id=incident.id,
                        user_id=incident.technician_id,
                        activity_type='diagnosed',
                        description='Initial diagnosis completed. Issue confirmed and repair plan established.',
                        is_customer_visible=True,
                        timestamp=incident.received_date + timedelta(hours=random.randint(2, 24))
                    )
                    db.session.add(diagnosis_activity)
                    incident.diagnosis_date = diagnosis_activity.timestamp
                    incident.diagnosis = 'Technical diagnosis completed. Root cause identified.'
                
                # Add software updates for firmware-related issues
                if category and category.requires_firmware_update and i <= 2:
                    software_update = ServiceSoftwareUpdate(
                        service_incident_id=incident.id,
                        update_type='FIRMWARE',
                        component_name='Flight Controller',
                        version_before=inc_data['firmware_version_before'],
                        version_after='FC_v1.9.1',
                        update_method='USB',
                        status='PENDING',
                        performed_by_id=incident.technician_id,
                        update_notes='Updated to latest firmware to resolve known issues'
                    )
                    db.session.add(software_update)
            
            db.session.commit()
            print(f'Created {len(incident_data)} sample service incidents')
        
        # Add service parts for incidents that require them
        inventory_items = InventoryItem.query.limit(5).all()
        service_incidents = ServiceIncident.query.filter_by(status='IN_PROGRESS').all()
        
        if inventory_items and service_incidents and ServicePart.query.count() == 0:
            print('Adding service parts to incidents...')
            
            for incident in service_incidents[:3]:  # Add parts to first 3 incidents
                if incident.service_category and incident.service_category.requires_parts:
                    # Add 1-2 parts per incident
                    for _ in range(random.randint(1, 2)):
                        inventory_item = random.choice(inventory_items)
                        service_part = ServicePart(
                            service_incident_id=incident.id,
                            inventory_item_id=inventory_item.id,
                            quantity_used=random.randint(1, 2),
                            unit_cost=inventory_item.unit_cost,
                            total_cost=inventory_item.unit_cost * random.randint(1, 2),
                            status='REQUIRED',
                            notes=f'Required for {incident.service_category.name}'
                        )
                        db.session.add(service_part)
            
            db.session.commit()
            print('Added service parts to incidents')
    
    else:
        print('Service management system already initialized.')
    
    # Show summary
    print('\n=== Service Management System Status ===')
    print(f'Service Categories: {ServiceCategory.query.count()}')
    print(f'Service Incidents: {ServiceIncident.query.count()}')
    print(f'Service Activities: {ServiceActivity.query.count()}')
    print(f'Service Parts: {ServicePart.query.count()}')
    print(f'Software Updates: {ServiceSoftwareUpdate.query.count()}')
    print('\nService Management System setup completed successfully!')
