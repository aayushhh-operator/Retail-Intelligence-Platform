"""Validation registry and raw dataset definitions."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Type

from config.settings import settings
from validate.base_validator import BaseValidator, DatasetConfig
from validate.csv_validator import CSVValidator
from validate.json_validator import JSONValidator

ValidatorClass = Type[BaseValidator]


class ValidationRegistry:
    """Map file types to validator implementations."""

    def __init__(self) -> None:
        self._validators: dict[str, ValidatorClass] = {}

    def register(self, file_type: str, validator_class: ValidatorClass) -> None:
        """Register a validator class."""
        self._validators[file_type.upper()] = validator_class

    def create(
        self, dataset_config: DatasetConfig, logger: logging.Logger
    ) -> BaseValidator:
        """Create a validator instance for a dataset config."""
        return self._validators[dataset_config.file_type.upper()](
            dataset_config, logger
        )

    def supported_types(self) -> tuple[str, ...]:
        """Return supported file types."""
        return tuple(sorted(self._validators))


def build_default_registry() -> ValidationRegistry:
    """Build the default validation registry."""
    registry = ValidationRegistry()
    registry.register("CSV", CSVValidator)
    registry.register("JSON", JSONValidator)
    return registry


def default_datasets() -> list[DatasetConfig]:
    """Return raw dataset definitions for Phase 3 validation."""
    raw_dir = Path(settings.directories.raw_data_dir)
    return [
        DatasetConfig("customers", raw_dir / "customers.csv", "CSV", "customer_id"),
        DatasetConfig("inventory", raw_dir / "inventory.csv", "CSV", "inventory_id"),
        DatasetConfig("orders", raw_dir / "orders.csv", "CSV", "order_id"),
        DatasetConfig("payments", raw_dir / "payments.csv", "CSV", "payment_id"),
        DatasetConfig("products", raw_dir / "products.csv", "CSV", "id"),
        DatasetConfig("reviews", raw_dir / "reviews.csv", "CSV", "review_id"),
        DatasetConfig("shipping", raw_dir / "shipping.csv", "CSV", "shipping_id"),
        DatasetConfig("website_events", raw_dir / "website_events.json", "JSON", None),
    ]
