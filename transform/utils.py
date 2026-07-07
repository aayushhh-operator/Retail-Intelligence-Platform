"""Shared transformation utilities."""

from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> list[dict[str, Any]]:
    """Read CSV data into dictionaries."""
    with path.open("r", encoding="utf-8", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def read_json(path: Path) -> list[dict[str, Any]]:
    """Read JSON or NDJSON and normalize to list of dictionaries."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = [json.loads(line) for line in text.splitlines() if line.strip()]
    if isinstance(payload, list):
        return [
            _flatten(item) if isinstance(item, dict) else {"value": item}
            for item in payload
        ]
    if isinstance(payload, dict):
        return [_flatten(payload)]
    return [{"value": payload}]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    """Write processed rows to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON report data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def parse_date(value: Any) -> date | None:
    """Parse common source date and timestamp formats."""
    if value is None or str(value).strip() == "":
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None


def to_float(value: Any) -> float | None:
    """Convert a value to float when possible."""
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_int(value: Any) -> int | None:
    """Convert a value to int when possible."""
    number = to_float(value)
    if number is None:
        return None
    return int(number)


def iso_date(value: Any) -> str:
    """Return YYYY-MM-DD when date parsing succeeds."""
    parsed = parse_date(value)
    return parsed.isoformat() if parsed else ""


def today() -> date:
    """Return current local date."""
    return datetime.now().date()


def _flatten(record: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten nested dictionaries using dotted names."""
    flattened: dict[str, Any] = {}
    for key, value in record.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            flattened.update(_flatten(value, name))
        else:
            flattened[name] = value
    return flattened
