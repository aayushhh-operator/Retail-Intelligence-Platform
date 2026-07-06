"""JSON dataset validator."""

from __future__ import annotations

from typing import Any

from validate.base_validator import BaseValidator, require_dataset
from validate.utils import normalize_records, read_json_payload


class JSONValidator(BaseValidator):
    """Validate raw JSON or NDJSON datasets."""

    def load(self) -> list[dict[str, Any]]:
        """Load JSON records from raw storage."""
        require_dataset(self.dataset_config.path)
        return normalize_records(read_json_payload(self.dataset_config.path))

