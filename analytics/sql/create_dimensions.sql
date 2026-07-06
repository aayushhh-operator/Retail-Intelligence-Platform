-- Create Dimension Tables

CREATE TABLE IF NOT EXISTS analytics.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL, -- natural key
    name VARCHAR(200),
    gender VARCHAR(20),
    age INTEGER,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    segment VARCHAR(50),
    signup_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL, -- natural key
    product_name VARCHAR(255),
    category VARCHAR(100),
    brand VARCHAR(100),
    price_band VARCHAR(50),
    cost_band VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INTEGER PRIMARY KEY, -- YYYYMMDD
    full_date DATE UNIQUE NOT NULL,
    day INTEGER,
    month INTEGER,
    quarter INTEGER,
    year INTEGER,
    weekday VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS analytics.dim_time (
    time_key INTEGER PRIMARY KEY, -- HHMMSS
    hour INTEGER,
    minute INTEGER,
    second INTEGER
);

CREATE TABLE IF NOT EXISTS analytics.dim_geography (
    geography_key SERIAL PRIMARY KEY,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    region VARCHAR(50), -- Derived
    UNIQUE (city, state, country)
);

CREATE TABLE IF NOT EXISTS analytics.dim_payment_method (
    payment_method_key SERIAL PRIMARY KEY,
    payment_method VARCHAR(50) UNIQUE NOT NULL,
    payment_category VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS analytics.dim_shipping_carrier (
    carrier_key SERIAL PRIMARY KEY,
    carrier_name VARCHAR(100) UNIQUE NOT NULL,
    service_type VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS analytics.dim_category (
    category_key SERIAL PRIMARY KEY,
    category VARCHAR(100) UNIQUE NOT NULL,
    sub_category VARCHAR(100)
);

-- Insert fallback Unknown records (Surrogate key -1) to gracefully handle missing/orphan facts
INSERT INTO analytics.dim_customer (customer_key, customer_id, name) VALUES (-1, 'UNKNOWN', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO analytics.dim_product (product_key, product_id, product_name) VALUES (-1, 'UNKNOWN', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO analytics.dim_geography (geography_key, city, state, country) VALUES (-1, 'Unknown', 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO analytics.dim_payment_method (payment_method_key, payment_method) VALUES (-1, 'UNKNOWN') ON CONFLICT DO NOTHING;
INSERT INTO analytics.dim_shipping_carrier (carrier_key, carrier_name) VALUES (-1, 'UNKNOWN') ON CONFLICT DO NOTHING;
INSERT INTO analytics.dim_category (category_key, category) VALUES (-1, 'UNKNOWN') ON CONFLICT DO NOTHING;
INSERT INTO analytics.dim_date (date_key, full_date, year) VALUES (-1, '1900-01-01', 1900) ON CONFLICT DO NOTHING;
INSERT INTO analytics.dim_time (time_key, hour, minute, second) VALUES (-1, 0, 0, 0) ON CONFLICT DO NOTHING;
