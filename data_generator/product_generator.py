"""Generate synthetic product catalog source data."""

from __future__ import annotations

import random
from typing import Any

from data_generator import config
from data_generator.utils import choose_issue_indexes, create_faker, format_date, make_id, money, random_date_between

PRODUCT_FIELDS = (
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
    "SKU",
)

BRANDS_BY_CATEGORY = {
    "Electronics": ("Auralink", "VoltEdge", "PixelWave", "NexaTech"),
    "Fashion": ("UrbanThread", "ModeCraft", "LumaWear", "Northloom"),
    "Books": ("PageHouse", "InkRoad", "ChapterWorks", "BlueShelf"),
    "Home": ("CasaNova", "HearthLine", "Nestora", "RoomWise"),
    "Sports": ("PeakMotion", "StridePro", "ArenaFit", "PulseGear"),
    "Beauty": ("GlowTheory", "PurePetal", "VelvetSkin", "AuraLabs"),
    "Toys": ("PlayForge", "TinyTrail", "WonderNest", "BrightBlocks"),
    "Kitchen": ("CookWell", "PantryPro", "SteelNest", "ChefAxis"),
    "Office": ("DeskMaven", "PaperGrid", "WorkNest", "InkPilot"),
    "Groceries": ("DailyHarvest", "FreshCart", "GreenBasket", "GrainCo"),
}


def generate_products(rng: random.Random) -> list[dict[str, Any]]:
    """Generate products with category-sensitive pricing and controlled defects."""
    fake = create_faker()
    rows: list[dict[str, Any]] = []
    issue_indexes = choose_issue_indexes(rng, config.NUMBER_OF_PRODUCTS)

    for index in range(1, config.NUMBER_OF_PRODUCTS + 1):
        category = rng.choice(config.CATEGORIES)
        price_low, price_high = config.CATEGORY_PRICE_RANGES[category]
        selling_price = money(rng.uniform(price_low, price_high))
        cost_price = money(selling_price * rng.uniform(0.45, 0.82))
        profit_margin = money((selling_price - cost_price) / selling_price)
        brand = rng.choice(BRANDS_BY_CATEGORY[category])

        row = {
            "product_id": make_id("PRD", index),
            "product_name": f"{brand} {fake.word().title()} {category[:-1] if category.endswith('s') else category}",
            "category": category,
            "brand": brand,
            "supplier": f"{fake.company()} Supplies",
            "cost_price": cost_price,
            "selling_price": selling_price,
            "profit_margin": profit_margin,
            "weight": money(rng.uniform(0.05, 15.0)),
            "rating": round(rng.uniform(2.8, 5.0), 1),
            "launch_date": format_date(random_date_between(rng, config.START_DATE, config.END_DATE)),
            "is_active": rng.choice((True, True, True, False)),
            "SKU": f"{category[:3].upper()}-{brand[:3].upper()}-{index:06d}",
        }

        if index - 1 in issue_indexes:
            issue_type = rng.choice(("negative_price", "missing_product_id", "outlier_price", "invalid_rating"))
            if issue_type == "negative_price":
                row["selling_price"] = money(-abs(float(row["selling_price"])))
            elif issue_type == "missing_product_id":
                row["product_id"] = ""
            elif issue_type == "outlier_price":
                row["selling_price"] = money(float(row["selling_price"]) * 50)
            elif issue_type == "invalid_rating":
                row["rating"] = 7.5

        rows.append(row)

    return rows

