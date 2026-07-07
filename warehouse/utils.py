"""Utility functions for the warehouse framework."""

import json
from pathlib import Path
from typing import Any


def write_json(path: Path, data: Any) -> None:
    """Write data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
