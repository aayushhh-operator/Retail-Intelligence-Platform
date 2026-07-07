"""Base extractor abstractions for the ingestion layer."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from config.pipeline_run import get_pipeline_run_id
from extract.exceptions import ExtractionError
from extract.metadata import ExtractionMetadata
from extract.utils import sha256_checksum


@dataclass(frozen=True)
class SourceConfig:
    """Configuration for one upstream source."""

    dataset_name: str
    source_type: str
    source: str
    raw_file_name: str


@dataclass(frozen=True)
class ExtractedPayload:
    """Result returned by an extractor before metadata is finalized."""

    destination_path: Path
    rows: int | None
    columns: list[str]
    file_size_bytes: int
    extra: dict[str, Any]


class BaseExtractor(ABC):
    """Base class for all source extractors."""

    def __init__(
        self,
        source_config: SourceConfig,
        raw_directory: Path,
        logger: logging.Logger,
    ) -> None:
        self.source_config = source_config
        self.raw_directory = raw_directory
        self.logger = logger

    @abstractmethod
    def connect(self) -> None:
        """Prepare the upstream source connection."""

    @abstractmethod
    def extract(self) -> Any:
        """Extract source data without validating or transforming it."""

    @abstractmethod
    def save(self, extracted_data: Any) -> ExtractedPayload:
        """Persist extracted data to raw storage."""

    def log(self, message: str) -> None:
        """Log a dataset-scoped extraction message."""
        self.logger.info("%s | %s", self.source_config.dataset_name, message)

    def run(self) -> ExtractionMetadata:
        """Execute extraction and return dataset metadata."""
        started_at = time.perf_counter()
        extracted_at = datetime.now()
        self.log("extraction started")

        try:
            self.connect()
            extracted_data = self.extract()
            payload = self.save(extracted_data)
            checksum = sha256_checksum(payload.destination_path)
            elapsed = round(time.perf_counter() - started_at, 4)
            metadata = ExtractionMetadata(
                pipeline_run_id=get_pipeline_run_id(),
                dataset_name=self.source_config.dataset_name,
                source_type=self.source_config.source_type,
                original_path=self.source_config.source,
                destination_path=str(payload.destination_path),
                rows=payload.rows,
                columns=payload.columns,
                file_size_bytes=payload.file_size_bytes,
                extraction_timestamp=extracted_at.isoformat(timespec="seconds"),
                execution_time_seconds=elapsed,
                checksum=checksum,
                status="success",
                extra=payload.extra,
            )
            self.log(f"extraction finished in {elapsed}s; rows={payload.rows}")
            return metadata
        except Exception as exc:
            elapsed = round(time.perf_counter() - started_at, 4)
            self.logger.exception(
                "%s | extraction failed after %.4fs",
                self.source_config.dataset_name,
                elapsed,
            )
            return ExtractionMetadata(
                pipeline_run_id=get_pipeline_run_id(),
                dataset_name=self.source_config.dataset_name,
                source_type=self.source_config.source_type,
                original_path=self.source_config.source,
                destination_path=str(
                    self.raw_directory / self.source_config.raw_file_name
                ),
                rows=None,
                columns=[],
                file_size_bytes=None,
                extraction_timestamp=extracted_at.isoformat(timespec="seconds"),
                execution_time_seconds=elapsed,
                checksum=None,
                status="failed",
                error_message=str(exc),
            )

    def destination_path(self) -> Path:
        """Return the configured raw destination path."""
        return self.raw_directory / self.source_config.raw_file_name


def require_existing_file(path: Path) -> None:
    """Raise a domain exception if a configured file source is missing."""
    if not path.is_file():
        raise ExtractionError(f"Source file does not exist: {path}")
