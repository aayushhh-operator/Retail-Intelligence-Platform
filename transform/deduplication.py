"""Deduplication utilities."""

from __future__ import annotations

from typing import Any


def remove_exact_duplicates(
    rows: list[dict[str, Any]], keep: str = "first"
) -> tuple[list[dict[str, Any]], int]:
    """Remove exact duplicate rows."""
    ordered = rows if keep == "first" else list(reversed(rows))
    seen: set[tuple[tuple[str, str], ...]] = set()
    output: list[dict[str, Any]] = []
    for row in ordered:
        signature = tuple(sorted((key, str(value)) for key, value in row.items()))
        if signature in seen:
            continue
        seen.add(signature)
        output.append(row)
    if keep != "first":
        output.reverse()
    return output, len(rows) - len(output)


def remove_primary_key_duplicates(
    rows: list[dict[str, Any]],
    primary_key: str | None,
    keep: str = "first",
) -> tuple[list[dict[str, Any]], int]:
    """Remove duplicate primary keys using first or last record policy."""
    if not primary_key:
        return rows, 0
    ordered = rows if keep == "first" else list(reversed(rows))
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    for row in ordered:
        value = row.get(primary_key)
        if value is None or str(value) == "":
            output.append(row)
            continue
        key = str(value)
        if key in seen:
            continue
        seen.add(key)
        output.append(row)
    if keep != "first":
        output.reverse()
    return output, len(rows) - len(output)
