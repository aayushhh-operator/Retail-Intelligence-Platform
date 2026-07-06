-- Warehouse Tables
CREATE TABLE IF NOT EXISTS warehouse.customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    email VARCHAR(200),
    phone VARCHAR(50),
    gender VARCHAR(20),
    date_of_birth DATE,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    zipcode VARCHAR(20),
    signup_date TIMESTAMP,
    is_active BOOLEAN,
    customer_segment VARCHAR(50),
    customer_age INTEGER,
    customer_tenure_days INTEGER
);

CREATE TABLE IF NOT EXISTS warehouse.products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    brand VARCHAR(100),
    supplier VARCHAR(100),
    cost_price DECIMAL(10, 2),
    selling_price DECIMAL(10, 2),
    profit_margin DECIMAL(5, 2),
    weight DECIMAL(10, 2),
    rating DECIMAL(3, 2),
    launch_date DATE,
    is_active BOOLEAN,
    sku VARCHAR(100),
    low_margin_flag BOOLEAN,
    profit DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS warehouse.orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_date TIMESTAMP,
    product_id VARCHAR(50),
    quantity INTEGER,
    unit_price DECIMAL(10, 2),
    discount DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    shipping_cost DECIMAL(10, 2),
    payment_id VARCHAR(50),
    shipping_id VARCHAR(50),
    order_status VARCHAR(50),
    total_amount DECIMAL(12, 2),
    order_year INTEGER,
    order_month INTEGER,
    order_quarter INTEGER,
    discount_percentage DECIMAL(5, 2),
    order_value DECIMAL(12, 2),
    items_count INTEGER
);

CREATE TABLE IF NOT EXISTS warehouse.payments (
    payment_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    transaction_time TIMESTAMP,
    amount DECIMAL(12, 2)
);

CREATE TABLE IF NOT EXISTS warehouse.shipping (
    shipping_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    carrier VARCHAR(100),
    tracking_number VARCHAR(100),
    dispatch_date TIMESTAMP,
    delivery_date TIMESTAMP,
    shipping_status VARCHAR(50),
    delivery_city VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS warehouse.inventory (
    inventory_id VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50),
    warehouse VARCHAR(100),
    current_stock INTEGER,
    reorder_level INTEGER,
    last_updated TIMESTAMP,
    warehouse_city VARCHAR(100),
    inventory_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS warehouse.reviews (
    review_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    rating INTEGER,
    review_title VARCHAR(255),
    review_text TEXT,
    review_date TIMESTAMP,
    verified_purchase BOOLEAN,
    review_sentiment VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS warehouse.website_events (
    event_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    event_type VARCHAR(100),
    event_timestamp TIMESTAMP,
    page_url TEXT
);
