"""Processed schema mapping and column ordering."""

from __future__ import annotations

from typing import Any

PROCESSED_SCHEMAS: dict[str, list[str]] = {
    "customers": [
        "customer_id",
        "first_name",
        "last_name",
        "full_name",
        "email",
        "phone",
        "gender",
        "date_of_birth",
        "city",
        "state",
        "country",
        "zipcode",
        "signup_date",
        "is_active",
        "customer_segment",
        "customer_age",
        "customer_tenure_days",
    ],
    "products": [
        "product_id",
        "product_name",
        "category",
        "brand",
        "supplier",
        "cost_price",
        "selling_price",
        "profit_margin",
        "weight",
        "rating",
        "launch_date",
        "is_active",
        "sku",
        "low_margin_flag",
        "profit",
    ],
    "inventory": [
        "inventory_id",
        "product_id",
        "warehouse",
        "current_stock",
        "reorder_level",
        "last_updated",
        "warehouse_city",
        "inventory_status",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "order_date",
        "product_id",
        "quantity",
        "unit_price",
        "discount",
        "tax",
        "shipping_cost",
        "payment_id",
        "shipping_id",
        "order_status",
        "total_amount",
        "order_year",
        "order_month",
        "order_quarter",
        "discount_percentage",
        "order_value",
        "items_count",
    ],
    "payments": [
        "payment_id",
        "order_id",
        "payment_method",
        "payment_status",
        "transaction_time",
        "amount",
    ],
    "shipping": [
        "shipping_id",
        "order_id",
        "carrier",
        "tracking_number",
        "dispatch_date",
        "delivery_date",
        "shipping_status",
        "delivery_city",
    ],
    "reviews": [
        "review_id",
        "customer_id",
        "product_id",
        "rating",
        "review_title",
        "review_text",
        "review_date",
        "verified_purchase",
        "review_sentiment",
    ],
    "website_events": [
        "event_id",
        "customer_id",
        "event_type",
        "event_timestamp",
        "page_url",
    ],
}


def map_product_api_row(row: dict[str, Any]) -> dict[str, Any]:
    """Map Fake Store API product fields to the platform product schema."""
    return {
        "product_id": str(row.get("id", "")),
        "product_name": row.get("title", ""),
        "category": row.get("category", ""),
        "brand": "Fake Store",
        "supplier": "Fake Store API",
        "cost_price": None,
        "selling_price": row.get("price"),
        "profit_margin": None,
        "weight": None,
        "rating": row.get("rating.rate"),
        "launch_date": None,
        "is_active": True,
        "sku": f"API-{row.get('id', '')}",
    }


def apply_schema(
    dataset: str, rows: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[str]]:
    """Apply processed column order and remove unexpected fields."""
    schema = PROCESSED_SCHEMAS.get(dataset)
    if not schema:
        schema = sorted({key for row in rows for key in row.keys()})
    mapped = [{column: row.get(column) for column in schema} for row in rows]
    return mapped, schema
