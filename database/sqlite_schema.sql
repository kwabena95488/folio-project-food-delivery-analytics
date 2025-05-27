-- SQLite Food Delivery Database Schema
-- Optimized for analytics and performance

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;

-- Drop tables if they exist (for clean recreation)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS customers;

-- Customers table with enhanced fields for analytics
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    preferred_cuisine VARCHAR(50),
    loyalty_tier VARCHAR(20) DEFAULT 'Bronze'
);

-- Restaurants table with additional analytics fields
CREATE TABLE restaurants (
    restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    address_line1 VARCHAR(100) NOT NULL,
    address_line2 VARCHAR(100),
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    cuisine_type VARCHAR(50),
    rating DECIMAL(3,2) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT 1,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivery_radius_miles DECIMAL(4,2) DEFAULT 5.0,
    avg_prep_time_minutes INTEGER DEFAULT 30
);

-- Menu items table with enhanced categorization
CREATE TABLE menu_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    category VARCHAR(50),
    is_available BOOLEAN DEFAULT 1,
    calories INTEGER,
    prep_time_minutes INTEGER,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    cost_to_make DECIMAL(8,2),
    is_popular BOOLEAN DEFAULT 0,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

-- Orders table with comprehensive tracking
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    restaurant_id INTEGER NOT NULL,
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(20) DEFAULT 'pending',
    delivery_fee DECIMAL(5,2) DEFAULT 0.0,
    tax_amount DECIMAL(8,2) DEFAULT 0.0,
    tip_amount DECIMAL(8,2) DEFAULT 0.0,
    delivery_time_minutes INTEGER,
    payment_method VARCHAR(20),
    order_source VARCHAR(20) DEFAULT 'app',
    discount_amount DECIMAL(8,2) DEFAULT 0.0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

-- Order items table (junction table) with enhanced tracking
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    special_instructions TEXT,
    item_rating INTEGER CHECK (item_rating BETWEEN 1 AND 5),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);

-- Performance Indexes for common query patterns
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_customers_registration ON customers(registration_date);
CREATE INDEX idx_customers_loyalty ON customers(loyalty_tier);

CREATE INDEX idx_restaurants_city ON restaurants(city);
CREATE INDEX idx_restaurants_cuisine ON restaurants(cuisine_type);
CREATE INDEX idx_restaurants_rating ON restaurants(rating);
CREATE INDEX idx_restaurants_active ON restaurants(is_active);

CREATE INDEX idx_menu_items_restaurant ON menu_items(restaurant_id);
CREATE INDEX idx_menu_items_category ON menu_items(category);
CREATE INDEX idx_menu_items_price ON menu_items(price);
CREATE INDEX idx_menu_items_available ON menu_items(is_available);
CREATE INDEX idx_menu_items_popular ON menu_items(is_popular);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_restaurant ON orders(restaurant_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_amount ON orders(total_amount);
CREATE INDEX idx_orders_payment ON orders(payment_method);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_item ON order_items(item_id);
CREATE INDEX idx_order_items_rating ON order_items(item_rating);

-- Composite indexes for advanced analytics
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX idx_orders_restaurant_date ON orders(restaurant_id, order_date);
CREATE INDEX idx_orders_date_status ON orders(order_date, status);
CREATE INDEX idx_menu_items_restaurant_category ON menu_items(restaurant_id, category);
CREATE INDEX idx_order_items_order_item ON order_items(order_id, item_id);

-- Analytical Views for common business intelligence queries

-- Customer Summary View
CREATE VIEW customer_summary AS
SELECT 
    c.customer_id,
    c.name,
    c.email,
    c.loyalty_tier,
    c.registration_date,
    COUNT(o.order_id) as total_orders,
    COALESCE(SUM(o.total_amount), 0) as total_spent,
    COALESCE(AVG(o.total_amount), 0) as avg_order_value,
    MIN(o.order_date) as first_order_date,
    MAX(o.order_date) as last_order_date,
    CASE 
        WHEN MAX(o.order_date) >= date('now', '-30 days') THEN 'Active'
        WHEN MAX(o.order_date) >= date('now', '-90 days') THEN 'At Risk'
        WHEN MAX(o.order_date) IS NOT NULL THEN 'Churned'
        ELSE 'Never Ordered'
    END as customer_status,
    JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) as days_since_last_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.loyalty_tier, c.registration_date;

-- Restaurant Performance View
CREATE VIEW restaurant_performance AS
SELECT 
    r.restaurant_id,
    r.name as restaurant_name,
    r.city,
    r.cuisine_type,
    r.rating,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    COALESCE(SUM(o.total_amount), 0) as total_revenue,
    COALESCE(AVG(o.total_amount), 0) as avg_order_value,
    COALESCE(AVG(o.delivery_time_minutes), 0) as avg_delivery_time,
    COUNT(DISTINCT DATE(o.order_date)) as active_days,
    COALESCE(SUM(o.total_amount) / NULLIF(COUNT(DISTINCT o.customer_id), 0), 0) as revenue_per_customer
FROM restaurants r
LEFT JOIN orders o ON r.restaurant_id = o.restaurant_id
WHERE r.is_active = 1
GROUP BY r.restaurant_id, r.name, r.city, r.cuisine_type, r.rating;

-- Menu Item Analytics View
CREATE VIEW menu_item_analytics AS
SELECT 
    mi.item_id,
    mi.item_name,
    mi.price,
    mi.category,
    mi.calories,
    mi.cost_to_make,
    r.name as restaurant_name,
    r.cuisine_type,
    COUNT(oi.order_item_id) as times_ordered,
    COALESCE(SUM(oi.quantity), 0) as total_quantity_sold,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_revenue,
    COALESCE(AVG(oi.quantity), 0) as avg_quantity_per_order,
    COALESCE(AVG(oi.item_rating), 0) as avg_rating,
    CASE 
        WHEN mi.cost_to_make > 0 THEN 
            (mi.price - mi.cost_to_make) / mi.price * 100
        ELSE NULL 
    END as profit_margin_percent
FROM menu_items mi
JOIN restaurants r ON mi.restaurant_id = r.restaurant_id
LEFT JOIN order_items oi ON mi.item_id = oi.item_id
WHERE mi.is_available = 1
GROUP BY mi.item_id, mi.item_name, mi.price, mi.category, mi.calories, 
         mi.cost_to_make, r.name, r.cuisine_type;

-- Daily Revenue Summary View
CREATE VIEW daily_revenue_summary AS
SELECT 
    DATE(order_date) as order_date,
    COUNT(*) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT restaurant_id) as active_restaurants,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    SUM(delivery_fee) as total_delivery_fees,
    SUM(tip_amount) as total_tips,
    AVG(delivery_time_minutes) as avg_delivery_time
FROM orders
WHERE status = 'completed'
GROUP BY DATE(order_date)
ORDER BY order_date;

-- Peak Hours Analysis View
CREATE VIEW peak_hours_analysis AS
SELECT 
    strftime('%H', order_date) as hour_of_day,
    strftime('%w', order_date) as day_of_week,
    COUNT(*) as order_count,
    SUM(total_amount) as hourly_revenue,
    AVG(total_amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(delivery_time_minutes) as avg_delivery_time
FROM orders
WHERE status = 'completed'
GROUP BY strftime('%H', order_date), strftime('%w', order_date)
ORDER BY hour_of_day, day_of_week; 