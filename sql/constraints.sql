-- Ensure constraints (like Foreign Keys and check constraints)

-- Note: In PostgreSQL, adding a constraint multiple times causes an error. 
-- Using DO block to safely add constraints if they don't exist.

DO $$
BEGIN
    -- Foreign Key constraints removed to support loading synthetic/API merged data with intentional missing referential integrity (e.g. dropped customers/products)

    -- Check Constraints
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_orders_quantity') THEN
        ALTER TABLE warehouse.orders ADD CONSTRAINT chk_orders_quantity CHECK (quantity >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_reviews_rating') THEN
        ALTER TABLE warehouse.reviews ADD CONSTRAINT chk_reviews_rating CHECK (rating >= 1 AND rating <= 5);
    END IF;

END $$;
