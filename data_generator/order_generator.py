"""Generate synthetic retail order source data."""

from __future__ import annotations

import random
from datetime import timedelta
from typing import Any

from data_generator import config
from data_generator.utils import choose_issue_indexes, format_date, make_id, money, random_date_between, weighted_choice

ORDER_FIELDS = (
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
)

STATUS_WEIGHTS = {
    "Delivered": 0.70,
    "Shipped": 0.12,
    "Processing": 0.08,
    "Cancelled": 0.06,
    "Returned": 0.04,
}


def build_product_popularity(rng: random.Random, products: list[dict[str, Any]]) -> dict[str, float]:
    """Create stable product popularity weights for realistic repeat purchases."""
    return {
        str(product["product_id"]): rng.uniform(0.5, 5.0)
        for product in products
        if product.get("product_id")
    }


def generate_orders(
    rng: random.Random,
    customers: list[dict[str, Any]],
    products: list[dict[str, Any]],
    product_popularity: dict[str, float],
) -> list[dict[str, Any]]:
    """Generate order records with realistic purchasing behavior."""
    customer_ids = [str(row["customer_id"]) for row in customers if row.get("customer_id")]
    active_products = [row for row in products if row.get("product_id")]
    product_ids = [str(row["product_id"]) for row in active_products]
    product_weights = [product_popularity.get(product_id, 1.0) for product_id in product_ids]
    product_by_id = {str(row["product_id"]): row for row in active_products}
    statuses = tuple(STATUS_WEIGHTS.keys())
    status_weights = tuple(STATUS_WEIGHTS.values())
    issue_indexes = choose_issue_indexes(rng, config.NUMBER_OF_ORDERS)
    rows: list[dict[str, Any]] = []

    for index in range(1, config.NUMBER_OF_ORDERS + 1):
        product_id = weighted_choice(rng, product_ids, product_weights)
        product = product_by_id[product_id]
        quantity = rng.choices((1, 2, 3, 4, 5), weights=(0.55, 0.22, 0.12, 0.07, 0.04), k=1)[0]
        unit_price = float(product["selling_price"])
        discount = round(rng.uniform(0, 0.40), 2)
        tax = money(unit_price * quantity * 0.18)
        shipping_cost = _shipping_cost_for_category(rng, str(product["category"]))
        subtotal = unit_price * quantity
        total_amount = money(subtotal - (subtotal * discount) + tax + shipping_cost)
        order_date = random_date_between(rng, config.START_DATE, config.END_DATE)

        row = {
            "order_id": make_id("ORD", index),
            "customer_id": rng.choice(customer_ids),
            "order_date": format_date(order_date),
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": money(unit_price),
            "discount": discount,
            "tax": tax,
            "shipping_cost": shipping_cost,
            "payment_id": "",
            "shipping_id": "",
            "order_status": weighted_choice(rng, statuses, status_weights),
            "total_amount": total_amount,
        }

        if index - 1 in issue_indexes:
            issue_type = rng.choice(("future_date", "duplicate_id", "negative_quantity", "missing_product_id"))
            if issue_type == "future_date":
                row["order_date"] = format_date(config.END_DATE + timedelta(days=rng.randint(1, 365)))
            elif issue_type == "duplicate_id" and rows:
                row["order_id"] = rows[-1]["order_id"]
            elif issue_type == "negative_quantity":
                row["quantity"] = -abs(int(row["quantity"]))
            elif issue_type == "missing_product_id":
                row["product_id"] = ""

        rows.append(row)

    return rows


def _shipping_cost_for_category(rng: random.Random, category: str) -> float:
    """Return category-sensitive shipping cost."""
    if category in {"Electronics", "Home", "Kitchen"}:
        return money(rng.uniform(8.0, 35.0))
    if category in {"Books", "Beauty", "Groceries"}:
        return money(rng.uniform(2.0, 12.0))
    return money(rng.uniform(4.0, 20.0))

