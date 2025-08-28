"""
Add condition field to inventory items

This migration adds a 'condition' column to the inventory_items table
to track whether parts are 'new' or 'faulty'.
"""

from app import create_app, db
from app.models import InventoryItem

def add_condition_field():
    """Add condition field to inventory_items table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Add condition column with default value 'new'
            with db.engine.connect() as connection:
                connection.execute(db.text("""
                    ALTER TABLE inventory_items 
                    ADD COLUMN condition VARCHAR(20) DEFAULT 'new' NOT NULL
                """))
                
                # Update all existing records to have 'new' condition
                connection.execute(db.text("""
                    UPDATE inventory_items 
                    SET condition = 'new' 
                    WHERE condition IS NULL
                """))
                
                connection.commit()
            
            print("✅ Successfully added condition field to inventory_items table")
            return True
            
        except Exception as e:
            print(f"❌ Error adding condition field: {str(e)}")
            return False

if __name__ == "__main__":
    print("Adding condition field to inventory items...")
    success = add_condition_field()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
