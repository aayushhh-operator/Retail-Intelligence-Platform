"""CSV source extractor implementation."""

from __future__ import annotations

from pathlib import Path

from extract.extractor import BaseExtractor, ExtractedPayload, require_existing_file
from extract.utils import copy_file, count_csv_rows, detect_csv_columns


class CSVExtractor(BaseExtractor):
    """Extract CSV files into raw storage without changing their contents."""

    def connect(self) -> None:
        """Verify that the configured CSV source file exists."""
        require_existing_file(Path(self.source_config.source))

    def extract(self) -> Path:
        """Return the source CSV path for streaming copy."""
        return Path(self.source_config.source)

    def save(self, extracted_data: Path) -> ExtractedPayload:
        """Copy the CSV file into raw storage and collect lightweight metadata."""
        destination = self.destination_path()
        copy_file(extracted_data, destination)
        return ExtractedPayload(
            destination_path=destination,
            rows=count_csv_rows(destination),
            columns=detect_csv_columns(destination),
            file_size_bytes=destination.stat().st_size,
            extra={"format": "csv", "encoding": "utf-8"},
        )

