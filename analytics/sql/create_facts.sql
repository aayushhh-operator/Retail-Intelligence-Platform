-- Create Fact Tables

CREATE TABLE IF NOT EXISTS analytics.fact_orders (
    order_id VARCHAR(50), -- Degenerate dimension
    customer_key INTEGER REFERENCES analytics.dim_customer(customer_key),
    product_key INTEGER REFERENCES analytics.dim_product(product_key),
    date_key INTEGER REFERENCES analytics.dim_date(date_key),
    time_key INTEGER REFERENCES analytics.dim_time(time_key),
    quantity INTEGER,
    unit_price DECIMAL(10, 2),
    discount DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    shipping_cost DECIMAL(10, 2),
    total_amount DECIMAL(12, 2)
);

CREATE TABLE IF NOT EXISTS analytics.fact_payments (
    payment_id VARCHAR(50),
    order_id VARCHAR(50),
    payment_method_key INTEGER REFERENCES analytics.dim_payment_method(payment_method_key),
    date_key INTEGER REFERENCES analytics.dim_date(date_key),
    time_key INTEGER REFERENCES analytics.dim_time(time_key),
    amount DECIMAL(12, 2),
    payment_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS analytics.fact_shipping (
    shipping_id VARCHAR(50),
    order_id VARCHAR(50),
    carrier_key INTEGER REFERENCES analytics.dim_shipping_carrier(carrier_key),
    geography_key INTEGER REFERENCES analytics.dim_geography(geography_key),
    date_key_dispatch INTEGER REFERENCES analytics.dim_date(date_key),
    date_key_delivery INTEGER REFERENCES analytics.dim_date(date_key),
    delivery_duration INTEGER,
    shipping_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS analytics.fact_customer_activity (
    event_id VARCHAR(50),
    customer_key INTEGER REFERENCES analytics.dim_customer(customer_key),
    product_key INTEGER REFERENCES analytics.dim_product(product_key),
    date_key INTEGER REFERENCES analytics.dim_date(date_key),
    time_key INTEGER REFERENCES analytics.dim_time(time_key),
    event_type VARCHAR(100),
    session_id VARCHAR(100)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_fact_orders_cust ON analytics.fact_orders(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_orders_prod ON analytics.fact_orders(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_orders_date ON analytics.fact_orders(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_payments_order ON analytics.fact_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_fact_payments_date ON analytics.fact_payments(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_shipping_order ON analytics.fact_shipping(order_id);
CREATE INDEX IF NOT EXISTS idx_fact_shipping_dispatch ON analytics.fact_shipping(date_key_dispatch);

CREATE INDEX IF NOT EXISTS idx_fact_cust_act_cust ON analytics.fact_customer_activity(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_cust_act_date ON analytics.fact_customer_activity(date_key);
