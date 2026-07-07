"""Dataset profiling statistics for validation reports."""

from __future__ import annotations

from collections import Counter
from sys import getsizeof
from typing import Any

from validate.utils import is_blank, to_float


def generate_statistics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate profiling statistics for a dataset."""
    columns = sorted({column for row in rows for column in row.keys()})
    row_count = len(rows)
    duplicate_count = _duplicate_rows(rows)

    profile: dict[str, Any] = {
        "rows": row_count,
        "columns": len(columns),
        "column_names": columns,
        "memory_usage_bytes": getsizeof(rows) + sum(getsizeof(row) for row in rows),
        "duplicate_rows": duplicate_count,
        "duplicate_percentage": (
            round((duplicate_count / row_count * 100), 2) if row_count else 0.0
        ),
        "columns_profile": {},
    }

    for column in columns:
        values = [row.get(column) for row in rows]
        non_blank = [value for value in values if not is_blank(value)]
        numeric_values = [
            number for value in non_blank if (number := to_float(value)) is not None
        ]
        counter = Counter(str(value) for value in non_blank)
        column_profile: dict[str, Any] = {
            "missing_count": row_count - len(non_blank),
            "missing_percentage": (
                round(((row_count - len(non_blank)) / row_count * 100), 2)
                if row_count
                else 0.0
            ),
            "unique_values": len(counter),
            "top_categories": counter.most_common(5),
        }
        if numeric_values:
            column_profile.update(_numeric_stats(numeric_values))
        profile["columns_profile"][column] = column_profile

    return profile


def _duplicate_rows(rows: list[dict[str, Any]]) -> int:
    """Return duplicate row count based on complete row content."""
    seen: set[tuple[tuple[str, str], ...]] = set()
    duplicates = 0
    for row in rows:
        signature = tuple(sorted((key, str(value)) for key, value in row.items()))
        if signature in seen:
            duplicates += 1
        else:
            seen.add(signature)
    return duplicates


def _numeric_stats(values: list[float]) -> dict[str, Any]:
    """Return descriptive numeric statistics."""
    sorted_values = sorted(values)
    value_count = len(sorted_values)
    average = sum(sorted_values) / value_count
    midpoint = value_count // 2
    if value_count % 2:
        median_value = sorted_values[midpoint]
    else:
        median_value = (sorted_values[midpoint - 1] + sorted_values[midpoint]) / 2

    counts = Counter(sorted_values)
    highest_frequency = max(counts.values())
    mode_value = next(
        value for value, count in counts.items() if count == highest_frequency
    )
    variance = (
        sum((value - average) ** 2 for value in sorted_values) / (value_count - 1)
        if value_count > 1
        else 0.0
    )

    return {
        "min": min(sorted_values),
        "max": max(sorted_values),
        "mean": round(average, 4),
        "median": round(median_value, 4),
        "mode": mode_value,
        "standard_deviation": round(variance**0.5, 4),
    }
