#!/usr/bin/env python3
"""
Test script to check the dashboard stats API endpoint
"""

from app import create_app
from app.models import UAVServiceIncident, UAVMaintenanceSchedule
from datetime import datetime, timezone

def test_dashboard_stats():
    """Test the dashboard statistics calculations"""
    app = create_app()
    
    with app.app_context():
        print("🔍 TESTING DASHBOARD STATISTICS")
        print("=" * 50)
        
        # Test 1: Total incidents
        total_incidents = UAVServiceIncident.query.count()
        print(f"📊 Total Incidents: {total_incidents}")
        
        # Test 2: Open incidents
        open_incidents = UAVServiceIncident.query.filter(
            UAVServiceIncident.workflow_status.in_(['INCIDENT_RAISED', 'DIAGNOSIS_WO', 'REPAIR_MAINTENANCE', 'QUALITY_CHECK', 'PREVENTIVE_MAINTENANCE'])
        ).count()
        print(f"🔓 Open Incidents: {open_incidents}")
        
        # Test 3: SLA status calculation
        all_incidents = UAVServiceIncident.query.filter(
            UAVServiceIncident.workflow_status != 'CLOSED'
        ).all()
        
        sla_breached = 0
        sla_critical = 0
        sla_warning = 0
        sla_on_track = 0
        
        for incident in all_incidents:
            status = incident.sla_status
            if status == 'BREACHED':
                sla_breached += 1
            elif status == 'CRITICAL':
                sla_critical += 1
            elif status == 'WARNING':
                sla_warning += 1
            else:
                sla_on_track += 1
                
        print(f"🚨 SLA Breached: {sla_breached}")
        print(f"⚠️  SLA Critical: {sla_critical}")
        print(f"🟡 SLA Warning: {sla_warning}")
        print(f"✅ SLA On Track: {sla_on_track}")
        
        # Test 4: Maintenance due
        try:
            maintenance_due = UAVMaintenanceSchedule.query.count()
            print(f"🔧 Maintenance Schedules: {maintenance_due}")
        except Exception as e:
            print(f"❌ Maintenance Schedule Error: {e}")
            
        # Test 5: Preventive maintenance incidents
        preventive_maintenance = UAVServiceIncident.query.filter_by(
            workflow_status='PREVENTIVE_MAINTENANCE'
        ).count()
        print(f"🔧 Preventive Maintenance Incidents: {preventive_maintenance}")
        
        # Test 6: Show some sample incidents with their SLA status
        print(f"\n📋 Sample Incidents and SLA Status:")
        sample_incidents = UAVServiceIncident.query.limit(5).all()
        
        for incident in sample_incidents:
            hours_elapsed = (datetime.now(timezone.utc) - incident.incident_raised_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600
            print(f"  {incident.incident_number_formatted}: {incident.workflow_status}")
            print(f"    Created: {incident.incident_raised_at}")
            print(f"    Hours elapsed: {hours_elapsed:.1f}")
            print(f"    SLA hours: {incident.sla_resolution_hours}")
            print(f"    SLA Status: {incident.sla_status}")
            print(f"    Is Breached: {incident.is_sla_breached}")
            print("")
        
        print("✅ Dashboard stats test completed!")
        
        # Return stats dict like the API does
        return {
            'total_incidents': total_incidents,
            'open_incidents': open_incidents,
            'sla_breached': sla_breached,
            'maintenance_due': preventive_maintenance  # Using preventive maintenance as fallback
        }

if __name__ == '__main__':
    stats = test_dashboard_stats()
    print(f"\n🎯 Final Stats: {stats}")
