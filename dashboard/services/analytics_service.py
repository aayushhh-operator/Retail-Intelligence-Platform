"""Analytics Schema Queries."""

import pandas as pd

from dashboard.services.db_service import execute_query


def get_overview_kpis() -> dict:
    """Get high level KPIs."""
    df = execute_query(
        "SELECT SUM(total_amount) as rev, COUNT(*) as orders FROM analytics.fact_orders"
    )

    if df.empty or df.iloc[0]["rev"] is None:
        # Fallback if DB is empty
        return {"revenue": 0.0, "orders": 0, "aov": 0.0}

    rev = df.iloc[0]["rev"]
    orders = df.iloc[0]["orders"]
    aov = rev / orders if orders > 0 else 0
    return {"revenue": rev, "orders": orders, "aov": aov}


def get_sales_trend() -> pd.DataFrame:
    query = """
    SELECT d.full_date as dt, SUM(f.total_amount) as daily_revenue
    FROM analytics.fact_orders f
    JOIN analytics.dim_date d ON f.date_key = d.date_key
    GROUP BY 1 ORDER BY 1
    """
    df = execute_query(query)
    if df.empty:
        # Return mock schema
        return pd.DataFrame(columns=["dt", "daily_revenue"])
    return df


def get_sales_by_category() -> pd.DataFrame:
    query = """
    SELECT p.category, SUM(f.total_amount) as revenue
    FROM analytics.fact_orders f
    JOIN analytics.dim_product p ON f.product_key = p.product_key
    GROUP BY 1 ORDER BY 2 DESC
    """
    df = execute_query(query)
    if df.empty:
        return pd.DataFrame(columns=["category", "revenue"])
    return df


def get_sales_by_region() -> pd.DataFrame:
    # Assuming dim_customer has state/country, or we use a geography dimension if linked.
    # The fact_shipping has geography_key. Let's use fact_shipping for regions.
    query = """
    SELECT g.country, SUM(f.total_amount) as revenue
    FROM analytics.fact_orders f
    JOIN analytics.fact_shipping s ON f.order_id = s.order_id
    JOIN analytics.dim_geography g ON s.geography_key = g.geography_key
    GROUP BY 1 ORDER BY 2 DESC
    """
    df = execute_query(query)
    if df.empty:
        return pd.DataFrame(columns=["country", "revenue"])
    return df


def get_top_customers() -> pd.DataFrame:
    query = """
    SELECT c.name, SUM(f.total_amount) as lifetime_value, COUNT(f.order_id) as order_count
    FROM analytics.fact_orders f
    JOIN analytics.dim_customer c ON f.customer_key = c.customer_key
    GROUP BY 1 ORDER BY 2 DESC LIMIT 10
    """
    df = execute_query(query)
    if df.empty:
        return pd.DataFrame(columns=["name", "lifetime_value", "order_count"])
    return df


def get_product_performance() -> pd.DataFrame:
    query = """
    SELECT p.product_name, SUM(f.total_amount) as revenue, SUM(f.quantity) as units_sold
    FROM analytics.fact_orders f
    JOIN analytics.dim_product p ON f.product_key = p.product_key
    GROUP BY 1 ORDER BY 2 DESC LIMIT 15
    """
    df = execute_query(query)
    if df.empty:
        return pd.DataFrame(columns=["product_name", "revenue", "units_sold"])
    return df


def get_shipping_status() -> pd.DataFrame:
    query = """
    SELECT shipping_status, COUNT(*) as count
    FROM analytics.fact_shipping
    GROUP BY 1
    """
    df = execute_query(query)
    if df.empty:
        return pd.DataFrame(columns=["shipping_status", "count"])
    return df
