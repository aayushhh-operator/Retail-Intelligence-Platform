"""Derived-column enrichment transformations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from transform.utils import parse_date, to_float, to_int


def enrich(dataset: str, rows: list[dict[str, Any]]) -> int:
    """Add analytics-ready derived columns."""
    handler = {
        "customers": _customers,
        "orders": _orders,
        "inventory": _inventory,
        "reviews": _reviews,
        "products": _products,
    }.get(dataset)
    if handler is None:
        return 0
    return handler(rows)


def _customers(rows: list[dict[str, Any]]) -> int:
    today = datetime.now().date()
    for row in rows:
        birth_date = parse_date(row.get("date_of_birth"))
        signup_date = parse_date(row.get("signup_date"))
        row["customer_age"] = today.year - birth_date.year if birth_date else None
        row["customer_tenure_days"] = (today - signup_date).days if signup_date else None
    return len(rows)


def _orders(rows: list[dict[str, Any]]) -> int:
    for row in rows:
        order_date = parse_date(row.get("order_date"))
        total = to_float(row.get("total_amount")) or 0.0
        discount = to_float(row.get("discount")) or 0.0
        quantity = to_int(row.get("quantity")) or 0
        if order_date:
            row["order_year"] = order_date.year
            row["order_month"] = order_date.month
            row["order_quarter"] = (order_date.month - 1) // 3 + 1
        row["discount_percentage"] = round(discount * 100, 2)
        row["order_value"] = round(total, 2)
        row["items_count"] = quantity
    return len(rows)


def _inventory(rows: list[dict[str, Any]]) -> int:
    for row in rows:
        stock = to_int(row.get("current_stock")) or 0
        reorder = to_int(row.get("reorder_level")) or 0
        row["inventory_status"] = "Reorder" if stock <= reorder else "Healthy"
    return len(rows)


def _reviews(rows: list[dict[str, Any]]) -> int:
    for row in rows:
        rating = to_int(row.get("rating")) or 0
        if rating >= 4:
            sentiment = "Positive"
        elif rating == 3:
            sentiment = "Neutral"
        else:
            sentiment = "Negative"
        row["review_sentiment"] = sentiment
    return len(rows)


def _products(rows: list[dict[str, Any]]) -> int:
    for row in rows:
        selling = to_float(row.get("selling_price") or row.get("price")) or 0.0
        cost = to_float(row.get("cost_price"))
        if cost is not None:
            row["profit"] = round(selling - cost, 2)
        else:
            row["profit"] = None
    return len(rows)

