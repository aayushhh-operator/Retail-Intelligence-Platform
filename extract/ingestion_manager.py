"""Ingestion manager for Phase 2 extraction."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.logging_config import configure_logging
from config.pipeline_run import get_pipeline_run_id, set_pipeline_run_id
from config.settings import settings
from extract.metadata import ExtractionMetadata, write_manifest, write_metadata
from extract.registry import (ExtractorRegistry, build_default_registry,
                              default_sources)


def run_ingestion(
    pipeline_run_id: str | None = None,
    registry: ExtractorRegistry | None = None,
) -> list[ExtractionMetadata]:
    """Run all registered Phase 2 source ingestions."""
    active_run_id = set_pipeline_run_id(pipeline_run_id)
    logger = configure_logging(pipeline_run_id=active_run_id)
    logger.info("Pipeline started")
    logger.info("Ingestion layer started")

    active_registry = registry or build_default_registry()
    raw_directory = Path(settings.directories.raw_data_dir)
    metadata_directory = Path(settings.directories.log_dir) / "metadata"
    manifest_path = Path(settings.directories.log_dir) / "ingestion_manifest.json"
    datasets: list[ExtractionMetadata] = []

    for source_config in default_sources():
        logger.info("%s | dataset started", source_config.dataset_name)
        extractor = active_registry.create(source_config, raw_directory, logger)
        metadata = extractor.run()
        write_metadata(metadata, metadata_directory)
        datasets.append(metadata)
        logger.info(
            "%s | dataset finished with status=%s",
            source_config.dataset_name,
            metadata.status,
        )

    write_manifest(get_pipeline_run_id(), datasets, manifest_path)
    logger.info("Ingestion manifest written to %s", manifest_path)
    logger.info("Ingestion layer completed")
    logger.info("Pipeline completed")
    return datasets


def main() -> None:
    """CLI entry point for Phase 2 ingestion."""
    run_ingestion()


if __name__ == "__main__":
    main()
