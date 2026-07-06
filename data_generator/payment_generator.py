"""Generate synthetic payment source data."""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from data_generator import config
from data_generator.utils import format_date, make_id, money, random_datetime_after

PAYMENT_FIELDS = (
    "payment_id",
    "order_id",
    "payment_method",
    "payment_status",
    "transaction_time",
    "amount",
)


def generate_payments(
    rng: random.Random,
    orders: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate payment records and assign payment IDs back to orders."""
    rows: list[dict[str, Any]] = []
    payable_orders = orders[: min(config.NUMBER_OF_PAYMENTS, len(orders))]
    payment_methods = ("Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet", "Cash on Delivery")
    payment_statuses = ("Paid", "Paid", "Paid", "Failed", "Refunded")

    for index, order in enumerate(payable_orders, start=1):
        payment_id = make_id("PAY", index)
        order["payment_id"] = payment_id
        order_date = datetime.fromisoformat(str(order["order_date"])).date()
        status = rng.choice(payment_statuses)

        rows.append(
            {
                "payment_id": payment_id,
                "order_id": order["order_id"],
                "payment_method": rng.choice(payment_methods),
                "payment_status": status,
                "transaction_time": format_date(random_datetime_after(rng, order_date, max_hours=6)),
                "amount": money(float(order["total_amount"])),
            }
        )

    return rows

