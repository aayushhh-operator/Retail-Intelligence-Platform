"""Reusable normalization transformations."""

from __future__ import annotations

import re
from typing import Any


def normalize_phone(value: Any) -> str:
    """Normalize phone numbers to a digit-oriented format."""
    if value is None:
        return ""
    text = str(value)
    prefix = "+" if text.strip().startswith("+") else ""
    digits = re.sub(r"\D", "", text)
    return f"{prefix}{digits}" if digits else ""


def normalize_zipcode(value: Any) -> str:
    """Normalize ZIP/postal code values."""
    if value is None:
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits[:6]


def normalize_country(value: Any) -> str:
    """Normalize country names."""
    if value is None or str(value).strip() == "":
        return ""
    lowered = str(value).strip().lower()
    if lowered in {"in", "india", "bharat"}:
        return "India"
    return str(value).strip().title()


def normalize_category(value: Any) -> str:
    """Normalize category display values."""
    if value is None:
        return ""
    mapping = {
        "electronics": "Electronics",
        "jewelery": "Jewelry",
        "men's clothing": "Mens Clothing",
        "women's clothing": "Womens Clothing",
    }
    text = str(value).strip()
    return mapping.get(text.lower(), text.title())
