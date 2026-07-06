-- TRUNCATE + RELOAD strategy
-- Clears all data from the star schema tables for a fresh reload.

TRUNCATE TABLE analytics.fact_orders CASCADE;
TRUNCATE TABLE analytics.fact_payments CASCADE;
TRUNCATE TABLE analytics.fact_shipping CASCADE;
TRUNCATE TABLE analytics.fact_customer_activity CASCADE;

-- We don't truncate dimensions if they are SCD or used heavily, but for a full TRUNCATE + RELOAD we can clear them.
-- Exception: We keep the -1 Unknown records by using a DELETE statement instead of TRUNCATE.
DELETE FROM analytics.dim_customer WHERE customer_key != -1;
DELETE FROM analytics.dim_product WHERE product_key != -1;
DELETE FROM analytics.dim_geography WHERE geography_key != -1;
DELETE FROM analytics.dim_payment_method WHERE payment_method_key != -1;
DELETE FROM analytics.dim_shipping_carrier WHERE carrier_key != -1;
DELETE FROM analytics.dim_category WHERE category_key != -1;

-- Dimensions like date/time are static, but just in case, leave them intact or conditionally rebuild.
-- We'll rebuild dates dynamically in Python.
