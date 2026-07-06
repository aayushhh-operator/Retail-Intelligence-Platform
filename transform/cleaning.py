"""Reusable cleaning transformations."""

from __future__ import annotations

import re
from typing import Any

EMAIL_FIXES = {
    "gmail.con": "gmail.com",
    "gamil.com": "gmail.com",
    "yahoo.con": "yahoo.com",
    "outlook.con": "outlook.com",
}


def trim_whitespace(rows: list[dict[str, Any]]) -> int:
    """Trim string values in place and return affected row count."""
    affected = 0
    for row in rows:
        changed = False
        for key, value in list(row.items()):
            if isinstance(value, str):
                trimmed = value.strip()
                if trimmed != value:
                    row[key] = trimmed
                    changed = True
        if changed:
            affected += 1
    return affected


def clean_email(value: Any) -> tuple[str, bool]:
    """Normalize and repair obvious email mistakes."""
    if value is None:
        return "", False
    email = str(value).strip().lower()
    repaired = False
    for bad, good in EMAIL_FIXES.items():
        if email.endswith(bad):
            email = email[: -len(bad)] + good
            repaired = True
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return email, repaired
    return email, repaired


def blank_to_none(rows: list[dict[str, Any]]) -> int:
    """Convert blank strings to None for consistent downstream handling."""
    affected = 0
    for row in rows:
        changed = False
        for key, value in list(row.items()):
            if isinstance(value, str) and value.strip() == "":
                row[key] = None
                changed = True
        if changed:
            affected += 1
    return affected

