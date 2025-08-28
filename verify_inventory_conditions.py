"""
Verify inventory condition updates

This script will check a sample of inventory items to confirm 
they all have the correct 'new' condition set.
"""

from app import create_app, db
from app.models import InventoryItem

def verify_inventory_conditions():
    """Verify that all inventory items have the correct condition"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get total count
            total_items = InventoryItem.query.count()
            print(f"Total inventory items: {total_items}")
            
            # Count by condition
            new_items = InventoryItem.query.filter(InventoryItem.condition == 'new').count()
            faulty_items = InventoryItem.query.filter(InventoryItem.condition == 'faulty').count()
            other_items = InventoryItem.query.filter(
                ~InventoryItem.condition.in_(['new', 'faulty'])
            ).count()
            
            print(f"\nCondition breakdown:")
            print(f"  - New: {new_items}")
            print(f"  - Faulty: {faulty_items}")
            print(f"  - Other/NULL: {other_items}")
            
            # Show sample items
            print(f"\nSample of inventory items:")
            sample_items = InventoryItem.query.limit(10).all()
            for item in sample_items:
                print(f"  - {item.part_number}: {item.name} -> Condition: '{item.condition}'")
            
            if new_items == total_items:
                print(f"\n✅ SUCCESS: All {total_items} inventory items have 'new' condition!")
            else:
                print(f"\n⚠️  Issue: {total_items - new_items} items don't have 'new' condition")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying inventory conditions: {str(e)}")
            return False

if __name__ == "__main__":
    print("Verifying inventory condition updates...")
    print("=" * 50)
    verify_inventory_conditions()
    print("=" * 50)
