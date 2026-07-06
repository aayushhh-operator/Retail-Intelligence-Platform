"""Fact builder executing SQL transformations."""

import logging
from analytics.utils import AnalyticsDBManager
from analytics.config import SOURCE_SCHEMA, TARGET_SCHEMA

logger = logging.getLogger(__name__)

class FactBuilder:
    """Builds fact tables mapping natural keys to surrogate keys."""

    def __init__(self, db: AnalyticsDBManager):
        self.db = db

    def build_all(self, run_id: str) -> None:
        logger.info("Starting fact builds...")
        self.build_fact_orders(run_id)
        self.build_fact_payments(run_id)
        self.build_fact_shipping(run_id)
        self.build_fact_customer_activity(run_id)

    def _log_refresh(self, run_id: str, table: str, rows: int, status: str):
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.model_refresh_log (run_id, table_name, row_count, status)
            VALUES ('{run_id}', '{table}', {rows}, '{status}');
        """
        self.db.execute_query(query)

    def build_fact_orders(self, run_id: str) -> None:
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.fact_orders 
            (order_id, customer_key, product_key, date_key, time_key, quantity, unit_price, discount, tax, shipping_cost, total_amount)
            SELECT 
                o.order_id,
                COALESCE(c.customer_key, -1),
                COALESCE(p.product_key, -1),
                COALESCE(CAST(TO_CHAR(o.order_date, 'YYYYMMDD') AS INTEGER), -1),
                COALESCE(CAST(TO_CHAR(o.order_date, 'HH24MISS') AS INTEGER), -1),
                o.quantity,
                o.unit_price,
                o.discount,
                o.tax,
                o.shipping_cost,
                o.total_amount
            FROM {SOURCE_SCHEMA}.orders o
            LEFT JOIN {TARGET_SCHEMA}.dim_customer c ON o.customer_id = c.customer_id
            LEFT JOIN {TARGET_SCHEMA}.dim_product p ON o.product_id = p.product_id;
        """
        self.db.execute_query(query)
        self._log_refresh(run_id, "fact_orders", 0, "SUCCESS")

    def build_fact_payments(self, run_id: str) -> None:
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.fact_payments 
            (payment_id, order_id, payment_method_key, date_key, time_key, amount, payment_status)
            SELECT 
                p.payment_id,
                p.order_id,
                COALESCE(pm.payment_method_key, -1),
                COALESCE(CAST(TO_CHAR(p.transaction_time, 'YYYYMMDD') AS INTEGER), -1),
                COALESCE(CAST(TO_CHAR(p.transaction_time, 'HH24MISS') AS INTEGER), -1),
                p.amount,
                p.payment_status
            FROM {SOURCE_SCHEMA}.payments p
            LEFT JOIN {TARGET_SCHEMA}.dim_payment_method pm ON p.payment_method = pm.payment_method;
        """
        self.db.execute_query(query)
        self._log_refresh(run_id, "fact_payments", 0, "SUCCESS")

    def build_fact_shipping(self, run_id: str) -> None:
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.fact_shipping 
            (shipping_id, order_id, carrier_key, geography_key, date_key_dispatch, date_key_delivery, delivery_duration, shipping_status)
            SELECT 
                s.shipping_id,
                s.order_id,
                COALESCE(sc.carrier_key, -1),
                COALESCE(g.geography_key, -1),
                COALESCE(CAST(TO_CHAR(s.dispatch_date, 'YYYYMMDD') AS INTEGER), -1),
                COALESCE(CAST(TO_CHAR(s.delivery_date, 'YYYYMMDD') AS INTEGER), -1),
                EXTRACT(DAY FROM (s.delivery_date - s.dispatch_date)),
                s.shipping_status
            FROM {SOURCE_SCHEMA}.shipping s
            LEFT JOIN {TARGET_SCHEMA}.dim_shipping_carrier sc ON s.carrier = sc.carrier_name
            -- Note: We map to customer's geography via orders since shipping table doesn't have reliable full geography.
            -- This is a simplification for the BI model.
            LEFT JOIN {SOURCE_SCHEMA}.orders o ON s.order_id = o.order_id
            LEFT JOIN {SOURCE_SCHEMA}.customers c ON o.customer_id = c.customer_id
            LEFT JOIN {TARGET_SCHEMA}.dim_geography g ON (c.city = g.city AND c.state = g.state AND c.country = g.country);
        """
        self.db.execute_query(query)
        self._log_refresh(run_id, "fact_shipping", 0, "SUCCESS")

    def build_fact_customer_activity(self, run_id: str) -> None:
        query = f"""
            INSERT INTO {TARGET_SCHEMA}.fact_customer_activity 
            (event_id, customer_key, product_key, date_key, time_key, event_type, session_id)
            SELECT 
                we.event_id,
                COALESCE(c.customer_key, -1),
                -1, -- We don't have product context in website_events directly unless parsed from URL
                COALESCE(CAST(TO_CHAR(we."timestamp", 'YYYYMMDD') AS INTEGER), -1),
                COALESCE(CAST(TO_CHAR(we."timestamp", 'HH24MISS') AS INTEGER), -1),
                we.event_type,
                NULL -- session_id is no longer in warehouse due to schema mapper mappings
            FROM {SOURCE_SCHEMA}.website_events we
            LEFT JOIN {TARGET_SCHEMA}.dim_customer c ON we.customer_id = c.customer_id;
        """
        self.db.execute_query(query)
        self._log_refresh(run_id, "fact_customer_activity", 0, "SUCCESS")
