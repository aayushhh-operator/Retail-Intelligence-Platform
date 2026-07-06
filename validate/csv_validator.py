"""CSV dataset validator."""

from __future__ import annotations

from typing import Any

from validate.base_validator import BaseValidator, require_dataset
from validate.utils import read_csv_rows


class CSVValidator(BaseValidator):
    """Validate raw CSV datasets."""

    def load(self) -> list[dict[str, Any]]:
        """Load CSV records from raw storage."""
        require_dataset(self.dataset_config.path)
        return read_csv_rows(self.dataset_config.path)

