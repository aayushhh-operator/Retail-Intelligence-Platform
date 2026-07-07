"""Configurable imputation strategies."""

from __future__ import annotations

from collections import Counter
from statistics import median
from typing import Any

from transform.utils import to_float


def impute_rows(
    rows: list[dict[str, Any]], strategies: dict[str, str]
) -> tuple[list[dict[str, Any]], int]:
    """Apply configured column imputation strategies."""
    imputed_rows = 0
    for column, strategy in strategies.items():
        replacement = _replacement(rows, column, strategy)
        if strategy == "drop":
            before = len(rows)
            rows = [row for row in rows if row.get(column) not in {None, ""}]
            imputed_rows += before - len(rows)
            continue
        if strategy == "none":
            continue
        for row in rows:
            if row.get(column) in {None, ""}:
                row[column] = replacement
                imputed_rows += 1
    return rows, imputed_rows


def _replacement(rows: list[dict[str, Any]], column: str, strategy: str) -> Any:
    """Calculate an imputation replacement value."""
    values = [row.get(column) for row in rows if row.get(column) not in {None, ""}]
    if strategy.startswith("constant:"):
        return strategy.split(":", 1)[1]
    if not values:
        return None
    if strategy == "mode":
        return Counter(str(value) for value in values).most_common(1)[0][0]
    numeric = [number for value in values if (number := to_float(value)) is not None]
    if strategy == "mean" and numeric:
        return sum(numeric) / len(numeric)
    if strategy == "median" and numeric:
        return median(numeric)
    return None
