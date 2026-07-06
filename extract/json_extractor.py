"""JSON and NDJSON source extractor implementation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from extract.extractor import BaseExtractor, ExtractedPayload, require_existing_file
from extract.utils import copy_file


class JSONExtractor(BaseExtractor):
    """Extract JSON-like files into raw storage without content changes."""

    def connect(self) -> None:
        """Verify that the configured JSON source file exists."""
        require_existing_file(Path(self.source_config.source))

    def extract(self) -> Path:
        """Return the source JSON path for raw copy."""
        return Path(self.source_config.source)

    def save(self, extracted_data: Path) -> ExtractedPayload:
        """Copy the JSON file into raw storage and collect metadata."""
        destination = self.destination_path()
        copy_file(extracted_data, destination)
        rows, columns, json_format = inspect_json(destination)
        return ExtractedPayload(
            destination_path=destination,
            rows=rows,
            columns=columns,
            file_size_bytes=destination.stat().st_size,
            extra={"format": json_format, "nested_json_supported": True},
        )


def inspect_json(path: Path) -> tuple[int | None, list[str], str]:
    """Inspect JSON or NDJSON shape without validating business content."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return 0, [], "json"

    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError:
        rows = 0
        columns: set[str] = set()
        with path.open("r", encoding="utf-8") as file_obj:
            for line in file_obj:
                if not line.strip():
                    continue
                rows += 1
                item = json.loads(line)
                if isinstance(item, dict):
                    columns.update(item.keys())
        return rows, sorted(columns), "ndjson"

    if isinstance(payload, list):
        columns = sorted({key for item in payload if isinstance(item, dict) for key in item})
        return len(payload), columns, "json"
    if isinstance(payload, dict):
        return 1, sorted(payload.keys()), "json"
    return 1, [], "json"

