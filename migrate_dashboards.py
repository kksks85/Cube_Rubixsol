"""
Database migration script to add dashboard management tables
Run this script to add the new dashboard functionality to your existing database.
"""

from app import create_app, db
from app.models import Dashboard, DashboardWidget, UserDashboardPreference, Report
import sys
import traceback

def migrate_dashboard_tables():
    """Create dashboard management tables"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating dashboard management tables...")
            
            # Create all tables (will only create new ones)
            db.create_all()
            
            print("✅ Dashboard tables created successfully!")
            print("📊 New tables added:")
            print("   - dashboards")
            print("   - dashboard_widgets") 
            print("   - user_dashboard_preferences")
            print("   - reports")
            
            # Create a sample dashboard for the admin user
            from app.models import User
            admin_user = User.query.filter_by(username='admin').first()
            
            if admin_user:
                # Check if sample dashboard already exists
                sample_dashboard = Dashboard.query.filter_by(name='Sample Dashboard').first()
                
                if not sample_dashboard:
                    print("\n🎯 Creating sample dashboard...")
                    
                    # Create sample dashboard
                    sample_dashboard = Dashboard(
                        name='Sample Dashboard',
                        description='A sample dashboard to get you started',
                        is_public=True,
                        created_by_id=admin_user.id
                    )
                    db.session.add(sample_dashboard)
                    db.session.flush()  # Get the ID
                    
                    # Create sample widgets
                    kpi_widget = DashboardWidget(
                        dashboard_id=sample_dashboard.id,
                        widget_type='kpi',
                        title='Total Work Orders',
                        position_x=0,
                        position_y=0,
                        width=3,
                        height=2
                    )
                    
                    chart_widget = DashboardWidget(
                        dashboard_id=sample_dashboard.id,
                        widget_type='chart',
                        title='Monthly Trends',
                        position_x=3,
                        position_y=0,
                        width=6,
                        height=3
                    )
                    
                    quick_actions_widget = DashboardWidget(
                        dashboard_id=sample_dashboard.id,
                        widget_type='quick_action',
                        title='Quick Actions',
                        position_x=9,
                        position_y=0,
                        width=3,
                        height=3
                    )
                    
                    db.session.add_all([kpi_widget, chart_widget, quick_actions_widget])
                    
                    # Create sample reports
                    sample_report = Report(
                        name='Work Order Summary',
                        description='Overview of work order statistics',
                        report_type='chart',
                        is_public=True,
                        created_by_id=admin_user.id
                    )
                    
                    db.session.add(sample_report)
                    db.session.commit()
                    
                    print("✅ Sample dashboard created!")
                    print(f"   Dashboard ID: {sample_dashboard.id}")
                    print(f"   Widgets created: 3")
                    print(f"   Sample report created: 1")
                else:
                    print("ℹ️  Sample dashboard already exists")
            
            print("\n🎉 Dashboard migration completed successfully!")
            print("\n📝 Next steps:")
            print("   1. Start your application")
            print("   2. Go to /dashboards to manage dashboards")
            print("   3. Create custom dashboards and widgets")
            print("   4. Set up reports for dashboard widgets")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            print("\n🔍 Full error details:")
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("🚀 Starting dashboard migration...")
    print("=" * 50)
    
    success = migrate_dashboard_tables()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("❌ Migration failed!")
        sys.exit(1)
