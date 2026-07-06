"""Extractor registry and source definitions for Phase 2 ingestion."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Type

from config.settings import settings
from extract.api_extractor import APIExtractor
from extract.csv_extractor import CSVExtractor
from extract.extractor import BaseExtractor, SourceConfig
from extract.json_extractor import JSONExtractor

ExtractorClass = Type[BaseExtractor]


class ExtractorRegistry:
    """Registry mapping source types to extractor implementations."""

    def __init__(self) -> None:
        self._extractors: dict[str, ExtractorClass] = {}

    def register(self, source_type: str, extractor_class: ExtractorClass) -> None:
        """Register an extractor class for a source type."""
        self._extractors[source_type.upper()] = extractor_class

    def create(
        self,
        source_config: SourceConfig,
        raw_directory: Path,
        logger: logging.Logger,
    ) -> BaseExtractor:
        """Create an extractor instance for a source config."""
        extractor_class = self._extractors[source_config.source_type.upper()]
        return extractor_class(source_config, raw_directory, logger)

    def supported_types(self) -> tuple[str, ...]:
        """Return registered source types."""
        return tuple(sorted(self._extractors))


def build_default_registry() -> ExtractorRegistry:
    """Build the default registry for CSV, JSON, and API extraction."""
    registry = ExtractorRegistry()
    registry.register("CSV", CSVExtractor)
    registry.register("JSON", JSONExtractor)
    registry.register("API", APIExtractor)
    return registry


def default_sources() -> list[SourceConfig]:
    """Return Phase 2 source definitions."""
    source_dir = Path(settings.directories.source_data_dir)
    return [
        SourceConfig("customers", "CSV", str(source_dir / "customers.csv"), "customers.csv"),
        SourceConfig("inventory", "CSV", str(source_dir / "inventory.csv"), "inventory.csv"),
        SourceConfig("orders", "CSV", str(source_dir / "orders.csv"), "orders.csv"),
        SourceConfig("payments", "CSV", str(source_dir / "payments.csv"), "payments.csv"),
        SourceConfig("reviews", "CSV", str(source_dir / "reviews.csv"), "reviews.csv"),
        SourceConfig("shipping", "CSV", str(source_dir / "shipping.csv"), "shipping.csv"),
        SourceConfig("products", "API", "https://fakestoreapi.com/products", "products.json"),
        SourceConfig("website_events", "JSON", str(source_dir / "website_events.json"), "website_events.json"),
    ]

