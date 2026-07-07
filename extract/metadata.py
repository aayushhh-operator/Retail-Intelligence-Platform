"""Metadata models and serialization helpers for ingestion runs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from extract.utils import ensure_directory


@dataclass(frozen=True)
class ExtractionMetadata:
    """Operational metadata for one extracted dataset."""

    pipeline_run_id: str
    dataset_name: str
    source_type: str
    original_path: str
    destination_path: str
    rows: int | None
    columns: list[str]
    file_size_bytes: int | None
    extraction_timestamp: str
    execution_time_seconds: float
    checksum: str | None
    status: str
    error_message: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable metadata."""
        return asdict(self)


def write_metadata(metadata: ExtractionMetadata, metadata_dir: Path) -> Path:
    """Write one dataset metadata file and return its path."""
    ensure_directory(metadata_dir)
    path = metadata_dir / f"{metadata.dataset_name}_metadata.json"
    path.write_text(
        json.dumps(metadata.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path


def write_manifest(
    pipeline_run_id: str,
    datasets: list[ExtractionMetadata],
    manifest_path: Path,
) -> Path:
    """Write the ingestion manifest for a complete pipeline run."""
    ensure_directory(manifest_path.parent)
    payload = {
        "pipeline_run_id": pipeline_run_id,
        "datasets": [dataset.to_dict() for dataset in datasets],
    }
    payload["summary"] = {
        "total_datasets": len(datasets),
        "succeeded": sum(1 for dataset in datasets if dataset.status == "success"),
        "failed": sum(1 for dataset in datasets if dataset.status == "failed"),
    }
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return manifest_path
