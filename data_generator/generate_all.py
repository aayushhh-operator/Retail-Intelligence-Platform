"""Generate all Phase 1 synthetic source datasets."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_generator import config
from data_generator.customer_generator import (CUSTOMER_FIELDS,
                                               generate_customers)
from data_generator.inventory_generator import (INVENTORY_FIELDS,
                                                generate_inventory)
from data_generator.order_generator import (ORDER_FIELDS,
                                            build_product_popularity,
                                            generate_orders)
from data_generator.payment_generator import PAYMENT_FIELDS, generate_payments
from data_generator.product_generator import PRODUCT_FIELDS, generate_products
from data_generator.review_generator import REVIEW_FIELDS, generate_reviews
from data_generator.shipping_generator import (SHIPPING_FIELDS,
                                               generate_shipping)
from data_generator.utils import seed_random, write_csv, write_json
from data_generator.website_events_generator import generate_website_events


def _save_dataset(
    file_name: str, rows: list[dict[str, object]], fields: tuple[str, ...]
) -> None:
    """Save one generated dataset to the configured source directory."""
    output_path = config.OUTPUT_DIRECTORY / file_name
    print(f"Saving {file_name}...")
    row_count = write_csv(output_path, rows, fields)
    print(f"{row_count} rows written to {output_path}.")


def _save_json_dataset(file_name: str, rows: list[dict[str, object]]) -> None:
    """Save one generated JSON dataset to the configured source directory."""
    output_path = config.OUTPUT_DIRECTORY / file_name
    print(f"Saving {file_name}...")
    row_count = write_json(output_path, rows)
    print(f"{row_count} rows written to {output_path}.")


def main() -> None:
    """Generate every configured synthetic retail source dataset."""
    rng = seed_random()
    config.OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    print("Generating Customers...")
    customers = generate_customers(rng)
    print(f"{len(customers)} rows generated.")

    print("Generating Products...")
    products = generate_products(rng)
    print(f"{len(products)} rows generated.")

    print("Generating Orders...")
    product_popularity = build_product_popularity(rng, products)
    orders = generate_orders(rng, customers, products, product_popularity)
    print(f"{len(orders)} rows generated.")

    print("Generating Payments...")
    payments = generate_payments(rng, orders)
    print(f"{len(payments)} rows generated.")

    print("Generating Shipping...")
    shipping = generate_shipping(rng, orders)
    print(f"{len(shipping)} rows generated.")

    print("Generating Reviews...")
    reviews = generate_reviews(rng, orders, shipping)
    print(f"{len(reviews)} rows generated.")

    print("Generating Inventory...")
    inventory = generate_inventory(rng, products, product_popularity)
    print(f"{len(inventory)} rows generated.")

    print("Generating Website Events...")
    website_events = generate_website_events(rng)
    print(f"{len(website_events)} rows generated.")

    _save_dataset("customers.csv", customers, CUSTOMER_FIELDS)
    _save_dataset("products.csv", products, PRODUCT_FIELDS)
    _save_dataset("inventory.csv", inventory, INVENTORY_FIELDS)
    _save_dataset("orders.csv", orders, ORDER_FIELDS)
    _save_dataset("payments.csv", payments, PAYMENT_FIELDS)
    _save_dataset("reviews.csv", reviews, REVIEW_FIELDS)
    _save_dataset("shipping.csv", shipping, SHIPPING_FIELDS)
    _save_json_dataset("website_events.json", website_events)

    print("Done.")


if __name__ == "__main__":
    main()
