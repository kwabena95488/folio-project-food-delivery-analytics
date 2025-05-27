#!/usr/bin/env python3
"""
Food Delivery Database Setup Script
Creates SQLite database with realistic sample data for analytics
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FoodDeliveryDBSetup:
    def __init__(self, db_path="database/food_delivery.db"):
        """Initialize database setup with path"""
        self.db_path = db_path
        self.fake = Faker()
        Faker.seed(42)  # For reproducible data
        random.seed(42)
        np.random.seed(42)
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
    def create_database(self):
        """Create database and execute schema"""
        print("🔄 Creating SQLite database...")
        
        # Read and execute schema
        schema_path = "database/sqlite_schema.sql"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Execute schema (split by semicolon for multiple statements)
        for statement in schema_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        conn.close()
        print("✅ Database schema created successfully")
        
    def generate_customers(self, num_customers=500):
        """Generate realistic customer data"""
        print(f"🔄 Generating {num_customers} customers...")
        
        customers = []
        loyalty_tiers = ['Bronze', 'Silver', 'Gold', 'Platinum']
        cuisines = ['Italian', 'Chinese', 'Mexican', 'Indian', 'American', 'Thai', 'Japanese']
        
        for i in range(num_customers):
            # Generate registration date (last 2 years)
            reg_date = self.fake.date_time_between(
                start_date='-2y', 
                end_date='now'
            )
            
            customer = {
                'name': self.fake.name(),
                'address': self.fake.address().replace('\n', ', '),
                'email': self.fake.unique.email(),
                'phone': self.fake.phone_number()[:20],
                'registration_date': reg_date,
                'is_active': random.choice([1, 1, 1, 0]),  # 75% active
                'preferred_cuisine': random.choice(cuisines),
                'loyalty_tier': np.random.choice(
                    loyalty_tiers, 
                    p=[0.5, 0.3, 0.15, 0.05]  # Weighted distribution
                )
            }
            customers.append(customer)
        
        return pd.DataFrame(customers)
    
    def generate_restaurants(self, num_restaurants=25):
        """Generate realistic restaurant data"""
        print(f"🔄 Generating {num_restaurants} restaurants...")
        
        restaurants = []
        cuisines = ['Italian', 'Chinese', 'Mexican', 'Indian', 'American', 'Thai', 'Japanese', 'Mediterranean', 'Korean', 'Vietnamese']
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
        states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'TX', 'CA', 'TX', 'CA']
        
        restaurant_names = [
            "Mama's Kitchen", "Dragon Palace", "Taco Fiesta", "Spice Garden", "Burger Haven",
            "Noodle House", "Sushi Express", "Pizza Corner", "Curry Delight", "BBQ Pit",
            "Fresh Salads", "Pasta Paradise", "Wok This Way", "Grill Master", "Sweet Treats",
            "Ocean Breeze", "Mountain View", "City Lights", "Garden Fresh", "Fire & Ice",
            "Golden Spoon", "Silver Fork", "Copper Pot", "Iron Chef", "Crystal Palace"
        ]
        
        for i in range(num_restaurants):
            city_idx = i % len(cities)
            
            restaurant = {
                'name': restaurant_names[i] if i < len(restaurant_names) else f"{self.fake.company()} Restaurant",
                'address_line1': self.fake.street_address(),
                'address_line2': self.fake.secondary_address() if random.random() < 0.3 else None,
                'city': cities[city_idx],
                'state': states[city_idx],
                'zip_code': self.fake.zipcode()[:10],
                'cuisine_type': random.choice(cuisines),
                'rating': round(random.uniform(3.0, 5.0), 2),
                'is_active': 1,
                'created_date': self.fake.date_time_between(start_date='-3y', end_date='-6m'),
                'delivery_radius_miles': round(random.uniform(2.0, 8.0), 2),
                'avg_prep_time_minutes': random.randint(15, 45)
            }
            restaurants.append(restaurant)
        
        return pd.DataFrame(restaurants)
    
    def generate_menu_items(self, restaurants_df):
        """Generate realistic menu items for each restaurant"""
        print("🔄 Generating menu items...")
        
        menu_items = []
        
        # Menu items by cuisine type
        cuisine_items = {
            'Italian': [
                ('Margherita Pizza', 'Classic pizza with tomato, mozzarella, and basil', 'Pizza', 450),
                ('Pepperoni Pizza', 'Pizza with pepperoni and mozzarella cheese', 'Pizza', 520),
                ('Spaghetti Carbonara', 'Pasta with eggs, cheese, and pancetta', 'Pasta', 380),
                ('Chicken Parmigiana', 'Breaded chicken with marinara and mozzarella', 'Main', 650),
                ('Caesar Salad', 'Romaine lettuce with Caesar dressing', 'Salad', 280),
                ('Tiramisu', 'Classic Italian dessert', 'Dessert', 320)
            ],
            'Chinese': [
                ('Sweet and Sour Chicken', 'Battered chicken with sweet and sour sauce', 'Main', 480),
                ('Beef and Broccoli', 'Stir-fried beef with broccoli', 'Main', 420),
                ('Fried Rice', 'Wok-fried rice with vegetables and egg', 'Rice', 350),
                ('Spring Rolls', 'Crispy vegetable spring rolls', 'Appetizer', 180),
                ('Hot and Sour Soup', 'Traditional Chinese soup', 'Soup', 120),
                ('Kung Pao Chicken', 'Spicy chicken with peanuts', 'Main', 450)
            ],
            'Mexican': [
                ('Chicken Tacos', 'Soft tacos with grilled chicken', 'Tacos', 320),
                ('Beef Burrito', 'Large burrito with seasoned beef', 'Burrito', 580),
                ('Guacamole and Chips', 'Fresh guacamole with tortilla chips', 'Appetizer', 250),
                ('Quesadilla', 'Grilled tortilla with cheese', 'Main', 420),
                ('Churros', 'Fried dough with cinnamon sugar', 'Dessert', 280),
                ('Chicken Fajitas', 'Sizzling chicken with peppers', 'Main', 480)
            ],
            'Indian': [
                ('Chicken Tikka Masala', 'Creamy tomato curry with chicken', 'Curry', 520),
                ('Biryani', 'Fragrant rice with spices and meat', 'Rice', 480),
                ('Naan Bread', 'Traditional Indian flatbread', 'Bread', 180),
                ('Samosas', 'Fried pastries with spiced filling', 'Appetizer', 220),
                ('Dal Curry', 'Lentil curry with spices', 'Curry', 280),
                ('Mango Lassi', 'Yogurt drink with mango', 'Beverage', 150)
            ],
            'American': [
                ('Classic Burger', 'Beef patty with lettuce, tomato, onion', 'Burger', 650),
                ('BBQ Ribs', 'Slow-cooked ribs with BBQ sauce', 'Main', 780),
                ('Buffalo Wings', 'Spicy chicken wings', 'Appetizer', 420),
                ('Mac and Cheese', 'Creamy macaroni and cheese', 'Side', 380),
                ('Apple Pie', 'Classic American dessert', 'Dessert', 320),
                ('Grilled Chicken Salad', 'Mixed greens with grilled chicken', 'Salad', 350)
            ],
            'Thai': [
                ('Pad Thai', 'Stir-fried noodles with tamarind sauce', 'Noodles', 420),
                ('Green Curry', 'Spicy coconut curry', 'Curry', 380),
                ('Tom Yum Soup', 'Spicy and sour soup', 'Soup', 180),
                ('Mango Sticky Rice', 'Sweet dessert with mango', 'Dessert', 280),
                ('Thai Basil Chicken', 'Stir-fried chicken with basil', 'Main', 450),
                ('Papaya Salad', 'Spicy green papaya salad', 'Salad', 220)
            ],
            'Japanese': [
                ('California Roll', 'Sushi roll with crab and avocado', 'Sushi', 280),
                ('Chicken Teriyaki', 'Grilled chicken with teriyaki sauce', 'Main', 420),
                ('Miso Soup', 'Traditional soybean soup', 'Soup', 80),
                ('Tempura', 'Battered and fried vegetables', 'Appetizer', 320),
                ('Ramen', 'Japanese noodle soup', 'Noodles', 450),
                ('Mochi Ice Cream', 'Sweet rice cake with ice cream', 'Dessert', 180)
            ]
        }
        
        # Default items for cuisines not in the list
        default_items = [
            ('House Special', 'Chef\'s signature dish', 'Main', 480),
            ('Soup of the Day', 'Daily fresh soup', 'Soup', 150),
            ('Garden Salad', 'Fresh mixed greens', 'Salad', 220),
            ('Grilled Chicken', 'Simply grilled chicken breast', 'Main', 380),
            ('Dessert Special', 'Chef\'s dessert creation', 'Dessert', 250)
        ]
        
        for _, restaurant in restaurants_df.iterrows():
            cuisine = restaurant['cuisine_type']
            items = cuisine_items.get(cuisine, default_items)
            
            # Add 6-12 items per restaurant
            num_items = random.randint(6, 12)
            selected_items = random.sample(items, min(len(items), num_items))
            
            # Add some random items if needed
            while len(selected_items) < num_items:
                selected_items.append(random.choice(default_items))
            
            for item_name, description, category, base_calories in selected_items:
                # Add some price variation
                base_price = random.uniform(8.99, 24.99)
                cost_to_make = base_price * random.uniform(0.25, 0.45)  # 25-45% cost ratio
                
                # Convert created_date to datetime if it's a string
                if isinstance(restaurant['created_date'], str):
                    base_date = datetime.fromisoformat(restaurant['created_date'].replace('Z', '+00:00'))
                else:
                    base_date = restaurant['created_date']
                
                menu_item = {
                    'restaurant_id': restaurant['restaurant_id'],
                    'item_name': item_name,
                    'description': description,
                    'price': round(base_price, 2),
                    'category': category,
                    'is_available': random.choice([1, 1, 1, 1, 0]),  # 80% available
                    'calories': base_calories + random.randint(-50, 100),
                    'prep_time_minutes': random.randint(10, 30),
                    'created_date': base_date + timedelta(days=random.randint(1, 30)),
                    'cost_to_make': round(cost_to_make, 2),
                    'is_popular': random.choice([0, 0, 0, 1])  # 25% popular
                }
                menu_items.append(menu_item)
        
        return pd.DataFrame(menu_items)
    
    def generate_orders_and_items(self, customers_df, restaurants_df, menu_items_df, num_orders=2000):
        """Generate realistic orders and order items"""
        print(f"🔄 Generating {num_orders} orders with items...")
        
        orders = []
        order_items = []
        
        # Order statuses with probabilities
        statuses = ['completed', 'completed', 'completed', 'completed', 'cancelled', 'pending']
        payment_methods = ['credit_card', 'debit_card', 'paypal', 'cash', 'apple_pay']
        order_sources = ['app', 'website', 'phone']
        
        for order_id in range(1, num_orders + 1):
            # Random customer and restaurant
            customer = customers_df.sample(1).iloc[0]
            restaurant = restaurants_df.sample(1).iloc[0]
            
            # Order date (last 6 months, with more recent orders)
            days_ago = np.random.exponential(30)  # Exponential distribution favors recent orders
            days_ago = min(days_ago, 180)  # Cap at 6 months
            order_date = datetime.now() - timedelta(days=days_ago)
            
            # Add some hourly patterns (peak lunch and dinner)
            hour_weights = [0.5, 0.3, 0.2, 0.2, 0.3, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0,  # 0-11
                           3.5, 2.5, 1.8, 1.5, 1.8, 2.5, 3.8, 4.0, 3.2, 2.0, 1.2, 0.8]   # 12-23
            hour = np.random.choice(24, p=np.array(hour_weights)/sum(hour_weights))
            order_date = order_date.replace(hour=hour, minute=random.randint(0, 59))
            
            status = random.choice(statuses)
            
            # Get available menu items for this restaurant
            restaurant_items = menu_items_df[
                (menu_items_df['restaurant_id'] == restaurant['restaurant_id']) & 
                (menu_items_df['is_available'] == 1)
            ]
            
            if len(restaurant_items) == 0:
                continue
            
            # Generate order items (1-5 items per order)
            num_items = np.random.choice([1, 2, 3, 4, 5], p=[0.3, 0.35, 0.2, 0.1, 0.05])
            selected_items = restaurant_items.sample(min(num_items, len(restaurant_items)))
            
            subtotal = 0
            current_order_items = []
            
            for _, item in selected_items.iterrows():
                quantity = np.random.choice([1, 2, 3], p=[0.7, 0.25, 0.05])
                unit_price = item['price']
                item_total = quantity * unit_price
                subtotal += item_total
                
                order_item = {
                    'order_id': order_id,
                    'item_id': item['item_id'],
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'special_instructions': self.fake.sentence() if random.random() < 0.1 else None,
                    'item_rating': random.randint(3, 5) if status == 'completed' and random.random() < 0.7 else None
                }
                current_order_items.append(order_item)
            
            # Calculate order totals
            delivery_fee = round(random.uniform(1.99, 4.99), 2)
            tax_rate = 0.08  # 8% tax
            tax_amount = round(subtotal * tax_rate, 2)
            tip_amount = round(subtotal * random.uniform(0.1, 0.25), 2) if status == 'completed' else 0
            discount_amount = round(subtotal * random.uniform(0, 0.15), 2) if random.random() < 0.2 else 0
            
            total_amount = subtotal + delivery_fee + tax_amount + tip_amount - discount_amount
            
            order = {
                'order_id': order_id,
                'customer_id': customer['customer_id'],
                'restaurant_id': restaurant['restaurant_id'],
                'order_date': order_date,
                'total_amount': round(total_amount, 2),
                'status': status,
                'delivery_fee': delivery_fee,
                'tax_amount': tax_amount,
                'tip_amount': tip_amount,
                'delivery_time_minutes': random.randint(20, 60) if status == 'completed' else None,
                'payment_method': random.choice(payment_methods),
                'order_source': random.choice(order_sources),
                'discount_amount': discount_amount
            }
            
            orders.append(order)
            order_items.extend(current_order_items)
        
        return pd.DataFrame(orders), pd.DataFrame(order_items)
    
    def populate_database(self):
        """Populate database with all sample data"""
        print("🔄 Populating database with sample data...")
        
        # Generate data
        customers_df = self.generate_customers()
        restaurants_df = self.generate_restaurants()
        
        # Insert customers and restaurants first to get IDs
        conn = sqlite3.connect(self.db_path)
        
        customers_df.to_sql('customers', conn, if_exists='append', index=False)
        restaurants_df.to_sql('restaurants', conn, if_exists='append', index=False)
        
        # Get the inserted data with IDs
        customers_df = pd.read_sql('SELECT * FROM customers', conn)
        restaurants_df = pd.read_sql('SELECT * FROM restaurants', conn)
        
        # Generate menu items
        menu_items_df = self.generate_menu_items(restaurants_df)
        menu_items_df.to_sql('menu_items', conn, if_exists='append', index=False)
        menu_items_df = pd.read_sql('SELECT * FROM menu_items', conn)
        
        # Generate orders and order items
        orders_df, order_items_df = self.generate_orders_and_items(
            customers_df, restaurants_df, menu_items_df
        )
        
        orders_df.to_sql('orders', conn, if_exists='append', index=False)
        order_items_df.to_sql('order_items', conn, if_exists='append', index=False)
        
        conn.close()
        
        print("✅ Database populated successfully")
        print(f"   📊 {len(customers_df)} customers")
        print(f"   🏪 {len(restaurants_df)} restaurants") 
        print(f"   🍕 {len(menu_items_df)} menu items")
        print(f"   📦 {len(orders_df)} orders")
        print(f"   🛒 {len(order_items_df)} order items")
    
    def setup_complete_database(self):
        """Complete database setup process"""
        print("🚀 Starting Food Delivery Database Setup...")
        
        # Remove existing database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print("🗑️  Removed existing database")
        
        # Create database and schema
        self.create_database()
        
        # Populate with sample data
        self.populate_database()
        
        # Verify setup
        self.verify_setup()
        
        print("🎉 Database setup completed successfully!")
        print(f"📍 Database location: {os.path.abspath(self.db_path)}")
    
    def verify_setup(self):
        """Verify database setup"""
        print("🔍 Verifying database setup...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check table counts
        tables = ['customers', 'restaurants', 'menu_items', 'orders', 'order_items']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {table}: {count} records")
        
        # Test views
        cursor.execute("SELECT COUNT(*) FROM customer_summary")
        customer_summary_count = cursor.fetchone()[0]
        print(f"   ✅ customer_summary view: {customer_summary_count} records")
        
        conn.close()

def main():
    """Main setup function"""
    setup = FoodDeliveryDBSetup()
    setup.setup_complete_database()

if __name__ == "__main__":
    main() 