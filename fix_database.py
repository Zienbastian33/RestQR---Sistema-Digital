"""
Script to fix database issues:
1. Add image_url column if missing
2. Clear existing menu items
3. Repopulate with items including images
"""
from app import create_app, db
from app.models import MenuItem
import sqlite3

def fix_database():
    app = create_app()
    with app.app_context():
        print("Starting database fix...")
        
        # Step 1: Add image_url column if it doesn't exist
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(menu_item)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'image_url' not in columns:
            print("Adding image_url column...")
            cursor.execute("ALTER TABLE menu_item ADD COLUMN image_url VARCHAR(256)")
            conn.commit()
            print("✓ Column added successfully!")
        else:
            print("✓ Column image_url already exists")
        
        conn.close()
        
        # Step 2: Clear existing menu items
        print("\nClearing existing menu items...")
        MenuItem.query.delete()
        db.session.commit()
        print("✓ Existing items cleared")
        
        # Step 3: Add new menu items with images
        print("\nAdding menu items with images...")
        menu_items = [
            # Handrolls
            MenuItem(name='California Roll', description='Kanikama, palta, queso crema', price=3990, category='Handrolls', image_url='img/californiaroll.webp'),
            MenuItem(name='Sake Roll', description='Salmón, palta', price=4290, category='Handrolls', image_url='img/sakeroll.webp'),
            MenuItem(name='Ebi Roll', description='Camarón, palta, queso crema', price=4190, category='Handrolls', image_url='img/ebiroll.webp'),
            
            # Sushi
            MenuItem(name='Nigiri Salmón', description='2 unidades de salmón fresco', price=3590, category='Sushi', image_url='img/sushi_salmon.jpeg'),
            MenuItem(name='Nigiri Atún', description='2 unidades de atún fresco', price=3790, category='Sushi', image_url='img/sushi_atun.jpeg'),
            MenuItem(name='Nigiri Pollo', description='2 unidades de pollo teriyaki', price=3290, category='Sushi', image_url='img/sushi_pollo.jpeg'),
            
            # Bebidas
            MenuItem(name='Coca-Cola', description='350ml', price=1500, category='Bebidas', image_url='img/bebida1.jpeg'),
            MenuItem(name='Ramune', description='Gaseosa japonesa 200ml', price=2500, category='Bebidas', image_url='img/bebida2.jpeg'),
            MenuItem(name='Sprite', description='350ml', price=1500, category='Bebidas', image_url='img/bebida3.jpeg'),
            
            # Extras
            MenuItem(name='Gyoza', description='5 empanaditas japonesas', price=4500, category='Extras', image_url='img/extra_gyoza.jpeg'),
            MenuItem(name='Arrollado Primavera', description='2 unidades vegetarianas', price=3900, category='Extras', image_url='img/extra_arrollado.jpeg'),
            MenuItem(name='Nigiri Extra', description='2 unidades variadas', price=2900, category='Extras', image_url='img/extra_nigiri.webp'),
        ]
        
        for item in menu_items:
            db.session.add(item)
        
        db.session.commit()
        print(f"✓ Added {len(menu_items)} menu items")
        
        # Step 4: Verify
        print("\nVerifying database...")
        items = MenuItem.query.all()
        print(f"✓ Total items in database: {len(items)}")
        
        items_with_images = MenuItem.query.filter(MenuItem.image_url.isnot(None)).count()
        print(f"✓ Items with images: {items_with_images}")
        
        print("\n✅ Database fix completed successfully!")

if __name__ == '__main__':
    fix_database()
