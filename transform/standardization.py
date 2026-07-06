"""Standardization transformations for strings, dates, booleans, and numerics."""

from __future__ import annotations

from typing import Any

from transform.utils import iso_date, to_float, to_int


def title_case(value: Any) -> str:
    """Convert a string to title case."""
    if value is None:
        return ""
    return str(value).strip().title()


def boolean_value(value: Any) -> bool | None:
    """Convert common boolean representations."""
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    return None


def money(value: Any) -> float | None:
    """Normalize currency-like values to two decimal floats."""
    number = to_float(value)
    return round(number, 2) if number is not None else None


def integer(value: Any) -> int | None:
    """Normalize integer-like values."""
    return to_int(value)


def standard_date(value: Any) -> str:
    """Normalize date values to YYYY-MM-DD."""
    return iso_date(value)

