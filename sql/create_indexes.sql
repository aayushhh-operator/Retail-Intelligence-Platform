-- Create performance indexes
-- IF NOT EXISTS handles idempotency

CREATE INDEX IF NOT EXISTS idx_customers_customer_id ON warehouse.customers(customer_id);
CREATE INDEX IF NOT EXISTS idx_products_product_id ON warehouse.products(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON warehouse.orders(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_payment_id ON warehouse.payments(payment_id);
CREATE INDEX IF NOT EXISTS idx_shipping_shipping_id ON warehouse.shipping(shipping_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON warehouse.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_products_category ON warehouse.products(category);
CREATE INDEX IF NOT EXISTS idx_reviews_review_date ON warehouse.reviews(review_date);
