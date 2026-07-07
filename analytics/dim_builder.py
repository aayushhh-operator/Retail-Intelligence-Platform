"""Dimension builder executing SQL transformations."""

import logging

from analytics.config import SOURCE_SCHEMA, TARGET_SCHEMA
from analytics.utils import AnalyticsDBManager

logger = logging.getLogger(__name__)


class DimensionBuilder:
    """Builds dimension tables using SQL transformations."""

    def __init__(self, db: AnalyticsDBManager):
        self.db = db

    def build_all(self, run_id: str) -> None:
        """Run all dimension builds."""
        logger.info("Starting dimension builds...")
        self.build_dim_customer(run_id)
        self.build_dim_product(run_id)
        self.build_dim_geography(run_id)
        self.build_dim_payment_method(run_id)
        self.build_dim_shipping_carrier(run_id)
        self.build_dim_category(run_id)
        self.build_dim_date(run_id)
        self.build_dim_time(run_id)

    def _log_refresh(self, run_id: str, table: str, rows: int, status: str):
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.model_refresh_log (run_id, table_name, row_count, status)
            VALUES ('{run_id}', '{table}', {rows}, '{status}');
        """
        self.db.execute_query(query)

    def build_dim_customer(self, run_id: str) -> None:
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.dim_customer (customer_id, name, gender, age, city, state, country, segment, signup_date)
            SELECT DISTINCT
                customer_id, full_name, gender, customer_age, city, state, country, customer_segment, signup_date
            FROM {SOURCE_SCHEMA}.customers
            ON CONFLICT (customer_id) DO UPDATE SET
                name = EXCLUDED.name,
                gender = EXCLUDED.gender,
                age = EXCLUDED.age,
                city = EXCLUDED.city,
                state = EXCLUDED.state,
                country = EXCLUDED.country,
                segment = EXCLUDED.segment;
        """
        self.db.execute_query(query)
        self._log_refresh(run_id, "dim_customer", 0, "SUCCESS")

    def build_dim_product(self, run_id: str) -> None:
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.dim_product (product_id, product_name, category, brand, price_band, cost_band)
            SELECT DISTINCT
                product_id, 
                product_name, 
                category, 
                brand,
                CASE 
                    WHEN selling_price < 20 THEN 'Low'
                    WHEN selling_price BETWEEN 20 AND 100 THEN 'Medium'
                    ELSE 'High'
                END as price_band,
                CASE 
                    WHEN cost_price < 10 THEN 'Low'
                    WHEN cost_price BETWEEN 10 AND 50 THEN 'Medium'
                    ELSE 'High'
                END as cost_band
            FROM {SOURCE_SCHEMA}.products
            ON CONFLICT (product_id) DO UPDATE SET
                product_name = EXCLUDED.product_name,
                category = EXCLUDED.category,
                brand = EXCLUDED.brand,
                price_band = EXCLUDED.price_band,
                cost_band = EXCLUDED.cost_band;
        """
        self.db.execute_query(query)
        self._log_refresh(run_id, "dim_product", 0, "SUCCESS")

    def build_dim_geography(self, run_id: str) -> None:
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.dim_geography (city, state, country, region)
            SELECT DISTINCT city, state, country, 
                CASE 
                    WHEN country IN ('USA', 'Canada', 'Mexico') THEN 'North America'
                    WHEN country IN ('UK', 'Germany', 'France', 'Italy') THEN 'Europe'
                    ELSE 'Other'
                END as region
            FROM (
                SELECT city, state, country FROM {SOURCE_SCHEMA}.customers WHERE city IS NOT NULL
                UNION
                SELECT warehouse_city as city, NULL as state, NULL as country FROM {SOURCE_SCHEMA}.inventory WHERE warehouse_city IS NOT NULL
            ) geo
            ON CONFLICT (city, state, country) DO NOTHING;
        """
        self.db.execute_query(query)
        self._log_refresh(run_id, "dim_geography", 0, "SUCCESS")

    def build_dim_payment_method(self, run_id: str) -> None:
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.dim_payment_method (payment_method, payment_category)
            SELECT DISTINCT payment_method, 
                CASE 
                    WHEN payment_method ILIKE '%card%' THEN 'Card'
                    WHEN payment_method ILIKE '%paypal%' THEN 'Digital Wallet'
                    ELSE 'Other'
                END
            FROM {SOURCE_SCHEMA}.payments WHERE payment_method IS NOT NULL
            ON CONFLICT (payment_method) DO NOTHING;
        """
        self.db.execute_query(query)
        self._log_refresh(run_id, "dim_payment_method", 0, "SUCCESS")

    def build_dim_shipping_carrier(self, run_id: str) -> None:
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.dim_shipping_carrier (carrier_name, service_type)
            SELECT DISTINCT carrier, 'Standard'
            FROM {SOURCE_SCHEMA}.shipping WHERE carrier IS NOT NULL
            ON CONFLICT (carrier_name) DO NOTHING;
        """
        self.db.execute_query(query)
        self._log_refresh(run_id, "dim_shipping_carrier", 0, "SUCCESS")

    def build_dim_category(self, run_id: str) -> None:
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.dim_category (category, sub_category)
            SELECT DISTINCT category, NULL as sub_category
            FROM {SOURCE_SCHEMA}.products WHERE category IS NOT NULL
            ON CONFLICT (category) DO NOTHING;
        """
        self.db.execute_query(query)
        self._log_refresh(run_id, "dim_category", 0, "SUCCESS")

    def build_dim_date(self, run_id: str) -> None:
        # Dynamic bounded generation using generate_series
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.dim_date (date_key, full_date, day, month, quarter, year, weekday)
            WITH date_bounds AS (
                SELECT 
                    COALESCE(MIN(order_date::DATE), '2020-01-01'::DATE) as min_date,
                    COALESCE(MAX(order_date::DATE), '2030-12-31'::DATE) as max_date
                FROM {SOURCE_SCHEMA}.orders
            ),
            date_series AS (
                SELECT generate_series(min_date, max_date, '1 day'::interval)::DATE as d
                FROM date_bounds
            )
            SELECT 
                CAST(TO_CHAR(d, 'YYYYMMDD') AS INTEGER) as date_key,
                d as full_date,
                EXTRACT(DAY FROM d) as day,
                EXTRACT(MONTH FROM d) as month,
                EXTRACT(QUARTER FROM d) as quarter,
                EXTRACT(YEAR FROM d) as year,
                TRIM(TO_CHAR(d, 'Day')) as weekday
            FROM date_series
            ON CONFLICT (full_date) DO NOTHING;
        """
        self.db.execute_query(query)
        self._log_refresh(run_id, "dim_date", 0, "SUCCESS")

    def build_dim_time(self, run_id: str) -> None:
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.dim_time (time_key, hour, minute, second)
            WITH time_series AS (
                SELECT generate_series('2000-01-01 00:00:00'::timestamp, '2000-01-01 23:59:59'::timestamp, '1 minute'::interval) as t
            )
            SELECT 
                CAST(TO_CHAR(t, 'HH24MISS') AS INTEGER) as time_key,
                EXTRACT(HOUR FROM t) as hour,
                EXTRACT(MINUTE FROM t) as minute,
                EXTRACT(SECOND FROM t) as second
            FROM time_series
            ON CONFLICT (time_key) DO NOTHING;
        """
        # Note: The prompt requested HHMMSS. Doing 1 minute intervals limits it to 1440 rows.
        self.db.execute_query(query)
        self._log_refresh(run_id, "dim_time", 0, "SUCCESS")
