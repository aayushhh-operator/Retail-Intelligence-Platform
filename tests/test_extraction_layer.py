"""Tests for Phase 2 ingestion primitives."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from config.pipeline_run import set_pipeline_run_id
from extract.api_extractor import APIExtractor
from extract.csv_extractor import CSVExtractor
from extract.extractor import SourceConfig
from extract.json_extractor import JSONExtractor
from extract.metadata import ExtractionMetadata, write_manifest, write_metadata
from extract.registry import build_default_registry
from extract.utils import sha256_checksum


class NullLogger:
    """Minimal logger used by extractor unit tests."""

    def info(self, *_args: object) -> None:
        """Ignore info logs during tests."""

    def exception(self, *_args: object) -> None:
        """Ignore exception logs during tests."""


def test_checksum_generation(tmp_path: Path) -> None:
    """SHA256 checksums should be stable for file contents."""
    path = tmp_path / "sample.txt"
    path.write_text("retail", encoding="utf-8")

    assert sha256_checksum(path) == sha256_checksum(path)


def test_csv_extraction(tmp_path: Path) -> None:
    """CSV extraction should copy source data and collect row metadata."""
    set_pipeline_run_id("RUN_20260706_143522")
    source = tmp_path / "customers.csv"
    source.write_text("customer_id,email\nCUS000001,a@example.com\n", encoding="utf-8")
    extractor = CSVExtractor(
        SourceConfig("customers", "CSV", str(source), "customers.csv"),
        tmp_path / "raw",
        NullLogger(),  # type: ignore[arg-type]
    )

    metadata = extractor.run()

    assert metadata.status == "success"
    assert metadata.pipeline_run_id == "RUN_20260706_143522"
    assert metadata.rows == 1
    assert metadata.columns == ["customer_id", "email"]
    assert (tmp_path / "raw" / "customers.csv").read_text(
        encoding="utf-8"
    ) == source.read_text(encoding="utf-8")


def test_json_extraction(tmp_path: Path) -> None:
    """JSON extraction should preserve source JSON and inspect top-level columns."""
    source = tmp_path / "website_events.json"
    source.write_text(json.dumps([{"event_id": "EVT1", "page": "/"}]), encoding="utf-8")
    extractor = JSONExtractor(
        SourceConfig("website_events", "JSON", str(source), "website_events.json"),
        tmp_path / "raw",
        NullLogger(),  # type: ignore[arg-type]
    )

    metadata = extractor.run()

    assert metadata.status == "success"
    assert metadata.rows == 1
    assert metadata.columns == ["event_id", "page"]


def test_api_extraction(tmp_path: Path) -> None:
    """API extraction should save raw API JSON responses."""
    payload = b'[{"id": 1, "title": "Bag"}]'
    extractor = APIExtractor(
        SourceConfig(
            "products", "API", "https://example.test/products", "products.json"
        ),
        tmp_path / "raw",
        NullLogger(),  # type: ignore[arg-type]
    )

    with patch.object(APIExtractor, "extract", return_value=payload):
        metadata = extractor.run()

    assert metadata.status == "success"
    assert metadata.rows == 1
    assert metadata.columns == ["id", "title"]
    assert (tmp_path / "raw" / "products.json").read_bytes() == payload


def test_metadata_and_manifest_include_pipeline_run_id(tmp_path: Path) -> None:
    """Metadata files and manifests should carry the pipeline run identifier."""
    metadata = ExtractionMetadata(
        pipeline_run_id="RUN_20260706_143522",
        dataset_name="customers",
        source_type="CSV",
        original_path="data/source/customers.csv",
        destination_path="data/raw/customers.csv",
        rows=1,
        columns=["customer_id"],
        file_size_bytes=10,
        extraction_timestamp="2026-07-06T14:35:22",
        execution_time_seconds=0.01,
        checksum="abc",
        status="success",
    )

    metadata_path = write_metadata(metadata, tmp_path / "metadata")
    manifest_path = write_manifest(
        "RUN_20260706_143522", [metadata], tmp_path / "ingestion_manifest.json"
    )

    assert (
        json.loads(metadata_path.read_text(encoding="utf-8"))["pipeline_run_id"]
        == "RUN_20260706_143522"
    )
    assert (
        json.loads(manifest_path.read_text(encoding="utf-8"))["pipeline_run_id"]
        == "RUN_20260706_143522"
    )


def test_registry_supports_expected_source_types() -> None:
    """The default registry should expose CSV, JSON, and API extractors."""
    registry = build_default_registry()

    assert registry.supported_types() == ("API", "CSV", "JSON")
