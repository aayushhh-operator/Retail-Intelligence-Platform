"""Generate synthetic product review source data."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

from data_generator import config
from data_generator.utils import choose_issue_indexes, create_faker, format_date, make_id

REVIEW_FIELDS = (
    "review_id",
    "customer_id",
    "product_id",
    "rating",
    "review_title",
    "review_text",
    "review_date",
    "verified_purchase",
)


def generate_reviews(
    rng: random.Random,
    orders: list[dict[str, Any]],
    shipping: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate reviews for a subset of delivered purchases."""
    fake = create_faker()
    delivery_by_order = {
        str(row["order_id"]): datetime.fromisoformat(str(row["delivery_date"])).date()
        for row in shipping
        if row["shipping_status"] == "Delivered"
    }
    completed_orders = [
        row
        for row in orders
        if row["order_status"] == "Delivered"
        and row.get("product_id")
        and str(row["order_id"]) in delivery_by_order
    ]
    review_count = min(config.NUMBER_OF_REVIEWS, len(completed_orders))
    selected_orders = rng.sample(completed_orders, review_count) if review_count else []
    issue_indexes = choose_issue_indexes(rng, review_count) if review_count else set()
    rows: list[dict[str, Any]] = []

    for index, order in enumerate(selected_orders, start=1):
        delivery_date = delivery_by_order[str(order["order_id"])]
        review_date = delivery_date + timedelta(days=rng.randint(1, 45))
        rating = rng.choices((1, 2, 3, 4, 5), weights=(0.04, 0.06, 0.15, 0.35, 0.40), k=1)[0]
        row = {
            "review_id": make_id("REV", index),
            "customer_id": order["customer_id"],
            "product_id": order["product_id"],
            "rating": rating,
            "review_title": fake.sentence(nb_words=5).rstrip("."),
            "review_text": fake.paragraph(nb_sentences=2),
            "review_date": format_date(review_date),
            "verified_purchase": True,
        }

        if index - 1 in issue_indexes:
            row["rating"] = rng.choice((0, 6, 9))

        rows.append(row)

    return rows

