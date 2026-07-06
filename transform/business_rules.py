"""Configurable business rule transformations."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from transform.config import BusinessRuleConfig
from transform.metrics import TransformationMetrics
from transform.utils import parse_date, to_float, to_int


def apply_business_rules(
    dataset: str,
    rows: list[dict[str, Any]],
    config: BusinessRuleConfig,
    metrics: TransformationMetrics,
) -> list[dict[str, Any]]:
    """Apply dataset-specific business rules."""
    handler = {
        "customers": _customers,
        "products": _products,
        "orders": _orders,
        "inventory": _inventory,
        "reviews": _reviews,
        "payments": _payments,
        "shipping": _shipping,
    }.get(dataset)
    if handler is None:
        return rows
    return handler(rows, config, metrics)


def _customers(rows: list[dict[str, Any]], _config: BusinessRuleConfig, metrics: TransformationMetrics) -> list[dict[str, Any]]:
    output = [row for row in rows if row.get("customer_id") and row.get("first_name") and row.get("last_name")]
    metrics.rows_dropped += len(rows) - len(output)
    return output


def _products(rows: list[dict[str, Any]], config: BusinessRuleConfig, metrics: TransformationMetrics) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        price = to_float(row.get("selling_price") or row.get("price"))
        cost = to_float(row.get("cost_price"))
        if price is None or price <= 0:
            metrics.rows_dropped += 1
            continue
        if cost is not None and price < cost:
            if config.product_low_margin_strategy == "repair":
                row["selling_price"] = round(cost * 1.15, 2)
                row["low_margin_flag"] = False
                metrics.rows_repaired += 1
            else:
                row["low_margin_flag"] = True
        else:
            row["low_margin_flag"] = False
        output.append(row)
    return output


def _orders(rows: list[dict[str, Any]], _config: BusinessRuleConfig, metrics: TransformationMetrics) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        quantity = to_int(row.get("quantity"))
        amount = to_float(row.get("total_amount"))
        unit_price = to_float(row.get("unit_price"))
        if not row.get("customer_id") or not row.get("product_id") or quantity is None or quantity <= 0:
            metrics.rows_dropped += 1
            continue
        if amount is None or amount <= 0 or unit_price is None or unit_price <= 0:
            metrics.rows_dropped += 1
            continue
        output.append(row)
    return output


def _inventory(rows: list[dict[str, Any]], config: BusinessRuleConfig, metrics: TransformationMetrics) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        stock = to_int(row.get("current_stock"))
        if stock is None:
            row["current_stock"] = 0
            metrics.rows_imputed += 1
        elif stock < 0:
            if config.inventory_negative_stock_strategy == "zero":
                row["current_stock"] = 0
                metrics.rows_repaired += 1
            else:
                metrics.rows_dropped += 1
                continue
        output.append(row)
    return output


def _reviews(rows: list[dict[str, Any]], config: BusinessRuleConfig, metrics: TransformationMetrics) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        rating = to_int(row.get("rating"))
        if rating is None:
            metrics.rows_dropped += 1
            continue
        if rating < 1 or rating > 5:
            if config.review_rating_strategy == "clamp":
                row["rating"] = min(5, max(1, rating))
                metrics.rows_repaired += 1
            else:
                metrics.rows_dropped += 1
                continue
        output.append(row)
    return output


def _payments(rows: list[dict[str, Any]], _config: BusinessRuleConfig, metrics: TransformationMetrics) -> list[dict[str, Any]]:
    output = [row for row in rows if to_float(row.get("amount")) is not None and to_float(row.get("amount")) > 0]
    metrics.rows_dropped += len(rows) - len(output)
    return output


def _shipping(rows: list[dict[str, Any]], config: BusinessRuleConfig, metrics: TransformationMetrics) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        dispatch = parse_date(row.get("dispatch_date"))
        delivery = parse_date(row.get("delivery_date"))
        if dispatch and delivery and delivery < dispatch:
            if config.shipping_date_strategy == "repair":
                row["delivery_date"] = (dispatch + timedelta(days=1)).isoformat()
                metrics.rows_repaired += 1
            else:
                metrics.rows_dropped += 1
                continue
        output.append(row)
    return output

