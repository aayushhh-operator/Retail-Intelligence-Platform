"""Configuration values for synthetic retail data generation."""

from __future__ import annotations

from datetime import date
from pathlib import Path

NUMBER_OF_CUSTOMERS = 1_000
NUMBER_OF_PRODUCTS = 300
NUMBER_OF_ORDERS = 5_000
NUMBER_OF_PAYMENTS = 5_000
NUMBER_OF_REVIEWS = 1_200
NUMBER_OF_SHIPMENTS = 5_000
NUMBER_OF_INVENTORY_RECORDS = 300
NUMBER_OF_WEBSITE_EVENTS = 2_000

START_DATE = date(2022, 1, 1)
END_DATE = date(2025, 12, 31)
RANDOM_SEED = 42

OUTPUT_DIRECTORY = Path("data/source")

DATA_QUALITY_ISSUE_RATE = 0.02

CATEGORIES = (
    "Electronics",
    "Fashion",
    "Books",
    "Home",
    "Sports",
    "Beauty",
    "Toys",
    "Kitchen",
    "Office",
    "Groceries",
)

CATEGORY_PRICE_RANGES = {
    "Electronics": (120.00, 2_500.00),
    "Fashion": (15.00, 350.00),
    "Books": (5.00, 80.00),
    "Home": (25.00, 900.00),
    "Sports": (12.00, 650.00),
    "Beauty": (8.00, 250.00),
    "Toys": (8.00, 180.00),
    "Kitchen": (10.00, 500.00),
    "Office": (6.00, 400.00),
    "Groceries": (2.00, 120.00),
}

WAREHOUSES = (
    ("WH-NORTH-01", "Delhi"),
    ("WH-WEST-01", "Mumbai"),
    ("WH-SOUTH-01", "Bengaluru"),
    ("WH-EAST-01", "Kolkata"),
    ("WH-CENTRAL-01", "Nagpur"),
)
