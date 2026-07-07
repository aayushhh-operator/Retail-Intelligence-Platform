"""Generate synthetic shipping source data."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

from data_generator import config
from data_generator.utils import create_faker, format_date, make_id

SHIPPING_FIELDS = (
    "shipping_id",
    "order_id",
    "carrier",
    "tracking_number",
    "dispatch_date",
    "delivery_date",
    "shipping_status",
    "delivery_city",
)


def generate_shipping(
    rng: random.Random,
    orders: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate shipping records and assign shipping IDs back to orders."""
    fake = create_faker()
    rows: list[dict[str, Any]] = []
    shippable_orders = orders[: min(config.NUMBER_OF_SHIPMENTS, len(orders))]
    carriers = ("BlueDart", "Delhivery", "Ecom Express", "FedEx", "DHL", "India Post")

    for index, order in enumerate(shippable_orders, start=1):
        shipping_id = make_id("SHP", index)
        order["shipping_id"] = shipping_id
        order_date = datetime.fromisoformat(str(order["order_date"])).date()
        dispatch_date = order_date + timedelta(days=rng.randint(0, 2))
        delivery_date = dispatch_date + timedelta(days=rng.randint(1, 9))

        if order["order_status"] == "Delivered":
            shipping_status = "Delivered"
        elif order["order_status"] == "Cancelled":
            shipping_status = "Cancelled"
        elif order["order_status"] == "Returned":
            shipping_status = "Returned"
        else:
            shipping_status = rng.choice(("In Transit", "Dispatched", "Pending"))

        rows.append(
            {
                "shipping_id": shipping_id,
                "order_id": order["order_id"],
                "carrier": rng.choice(carriers),
                "tracking_number": f"TRK{rng.randint(10**11, 10**12 - 1)}",
                "dispatch_date": format_date(dispatch_date),
                "delivery_date": format_date(delivery_date),
                "shipping_status": shipping_status,
                "delivery_city": fake.city(),
            }
        )

    return rows
