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
    """Fetch products from FakeStore API so synthetic data matches extraction."""
    import urllib.request
    import json
    
    # We fetch from FakeStore API to ensure Phase 1 generated orders
    # have product_ids that match what Phase 2 will extract.
    try:
        req = urllib.request.Request(
            "https://fakestoreapi.com/products",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            
        rows: list[dict[str, Any]] = []
        for p in payload:
            selling_price = float(p["price"])
            cost_price = money(selling_price * 0.6)
            
            row = {
                "product_id": str(p["id"]),
                "product_name": p["title"],
                "category": p["category"].title(),
                "brand": "FakeStore",
                "supplier": "FakeStore Supplies",
                "cost_price": cost_price,
                "selling_price": money(selling_price),
                "profit_margin": money(0.4),
                "weight": money(1.0),
                "rating": float(p["rating"]["rate"]),
                "launch_date": format_date(random_date_between(rng, config.START_DATE, config.END_DATE)),
                "is_active": True,
                "SKU": f"FS-{p['id']:06d}",
            }
            rows.append(row)
        return rows
    except Exception as e:
        print(f"Failed to fetch FakeStore products in generator: {e}")
        return []

