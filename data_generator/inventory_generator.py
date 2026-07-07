"""Generate synthetic inventory source data."""

from __future__ import annotations

import random
from typing import Any

from data_generator import config
from data_generator.utils import format_date, make_id, random_date_between

INVENTORY_FIELDS = (
    "inventory_id",
    "product_id",
    "warehouse",
    "current_stock",
    "reorder_level",
    "last_updated",
    "warehouse_city",
)


def generate_inventory(
    rng: random.Random,
    products: list[dict[str, Any]],
    product_popularity: dict[str, float],
) -> list[dict[str, Any]]:
    """Generate inventory records with lower stock for popular products."""
    product_rows = products[: config.NUMBER_OF_INVENTORY_RECORDS]
    rows: list[dict[str, Any]] = []

    for index, product in enumerate(product_rows, start=1):
        product_id = str(product["product_id"])
        popularity = product_popularity.get(product_id, 1.0)
        base_stock = rng.randint(80, 2_500)
        adjusted_stock = max(0, int(base_stock / popularity))
        warehouse, city = rng.choice(config.WAREHOUSES)

        rows.append(
            {
                "inventory_id": make_id("INV", index),
                "product_id": product_id,
                "warehouse": warehouse,
                "current_stock": adjusted_stock,
                "reorder_level": rng.randint(20, 150),
                "last_updated": format_date(
                    random_date_between(rng, config.START_DATE, config.END_DATE)
                ),
                "warehouse_city": city,
            }
        )

    return rows
