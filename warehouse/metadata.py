"""Metadata recording utility."""

from datetime import datetime
from typing import Any, Dict, List

from warehouse.config import METADATA_DIR
from warehouse.utils import write_json


class WarehouseMetadata:
    """Generates JSON warehouse metadata."""

    def __init__(self):
        self.execution_time: str = datetime.now().isoformat()
        self.datasets_loaded: List[str] = []
        self.tables: List[str] = []
        self.row_counts: Dict[str, int] = {}
        self.statistics: Dict[str, Any] = {"total_rows_loaded": 0, "failed_datasets": 0}

    def record_success(self, dataset: str, rows: int) -> None:
        """Record a successful dataset load."""
        self.datasets_loaded.append(dataset)
        self.tables.append(dataset)
        self.row_counts[dataset] = rows
        self.statistics["total_rows_loaded"] += rows

    def record_failure(self, dataset: str) -> None:
        """Record a failed dataset load."""
        self.statistics["failed_datasets"] += 1

    def save(self) -> None:
        """Save the metadata to a JSON file."""
        payload = {
            "execution_time": self.execution_time,
            "datasets_loaded": self.datasets_loaded,
            "tables": self.tables,
            "row_counts": self.row_counts,
            "statistics": self.statistics,
        }
        write_json(METADATA_DIR / "warehouse_metadata.json", payload)
