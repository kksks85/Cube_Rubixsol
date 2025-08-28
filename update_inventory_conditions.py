"""
Update all existing inventory items to have condition = 'new'

This script will update all existing inventory items that may not have 
the condition field set to ensure they have the default 'new' condition.
"""

from app import create_app, db
from app.models import InventoryItem

def update_inventory_conditions():
    """Update all existing inventory items to have condition = 'new'"""
    app = create_app()
    
    with app.app_context():
        try:
            # Find all inventory items that don't have a condition set or have NULL condition
            items_to_update = InventoryItem.query.filter(
                db.or_(
                    InventoryItem.condition.is_(None),
                    InventoryItem.condition == '',
                    InventoryItem.condition == 'NULL'
                )
            ).all()
            
            print(f"Found {len(items_to_update)} items without proper condition set")
            
            # Also update ALL items to ensure consistency
            all_items = InventoryItem.query.all()
            print(f"Total inventory items in database: {len(all_items)}")
            
            updated_count = 0
            
            # Update all items to have 'new' condition
            for item in all_items:
                if item.condition != 'new':
                    old_condition = item.condition
                    item.condition = 'new'
                    updated_count += 1
                    print(f"Updated item '{item.name}' (Part: {item.part_number}) from '{old_condition}' to 'new'")
            
            # If no items needed updating, still ensure all are set to 'new'
            if updated_count == 0:
                # Force update all items to 'new' for consistency
                db.session.execute(
                    db.text("UPDATE inventory_items SET condition = 'new'")
                )
                updated_count = len(all_items)
                print(f"Force updated all {updated_count} items to 'new' condition")
            
            db.session.commit()
            
            # Verify the update
            verification_count = InventoryItem.query.filter(InventoryItem.condition == 'new').count()
            total_count = InventoryItem.query.count()
            
            print(f"\n✅ Successfully updated {updated_count} inventory items")
            print(f"✅ Verification: {verification_count}/{total_count} items now have 'new' condition")
            
            if verification_count == total_count:
                print("🎉 All inventory items successfully updated to 'new' condition!")
            else:
                print(f"⚠️  Warning: {total_count - verification_count} items still don't have 'new' condition")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating inventory conditions: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("Updating all inventory items to have 'new' condition...")
    print("=" * 60)
    success = update_inventory_conditions()
    print("=" * 60)
    if success:
        print("✅ Inventory condition update completed successfully!")
    else:
        print("❌ Inventory condition update failed!")
