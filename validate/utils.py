"""Shared utility functions for validation."""

from __future__ import annotations

import csv
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^[+\d][\d\s().-]{6,}$")
ZIP_PATTERN = re.compile(r"^\d{5,6}$")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read CSV rows as dictionaries without modifying source data."""
    with path.open("r", encoding="utf-8", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def read_json_payload(path: Path) -> Any:
    """Read JSON or NDJSON payloads from disk."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]


def flatten_record(record: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten nested dictionaries with dotted field names."""
    flattened: dict[str, Any] = {}
    for key, value in record.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            flattened.update(flatten_record(value, name))
        else:
            flattened[name] = value
    return flattened


def normalize_records(payload: Any) -> list[dict[str, Any]]:
    """Normalize JSON payloads into a list of flattened dictionaries."""
    if isinstance(payload, list):
        return [
            flatten_record(item) if isinstance(item, dict) else {"value": item}
            for item in payload
        ]
    if isinstance(payload, dict):
        return [flatten_record(payload)]
    return [{"value": payload}]


def is_blank(value: Any) -> bool:
    """Return whether a value should be treated as blank."""
    return value is None or str(value).strip() == ""


def to_float(value: Any) -> float | None:
    """Convert a value to float when possible."""
    if is_blank(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_date(value: Any) -> date | None:
    """Parse a date or timestamp value using expected source formats."""
    if is_blank(value):
        return None
    text = str(value)
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None


def today() -> date:
    """Return the current local date."""
    return datetime.now().date()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a JSON payload with deterministic formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
