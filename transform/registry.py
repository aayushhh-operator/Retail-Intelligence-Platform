"""Transformer registry for mapping datasets to their transformer classes."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any, Type

from transform.base_transformer import BaseTransformer
from transform.config import TRANSFORMATION_CONFIG, TransformationConfig
from transform.normalization import (
    normalize_category,
    normalize_country,
    normalize_phone,
    normalize_zipcode,
)
from transform.standardization import integer, title_case


# ---------------------------------------------------------------------------
# Concrete dataset transformers
# ---------------------------------------------------------------------------


class CustomersTransformer(BaseTransformer):
    """Transformer for the customers raw dataset."""

    def load(self) -> list[dict[str, Any]]:
        with self.raw_path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = self._clean(rows)
        rows = self._impute(rows)
        rows = self._deduplicate(rows)
        rows = self._standardize(rows)
        for row in rows:
            if row.get("phone") is not None:
                row["phone"] = normalize_phone(row["phone"])
            if row.get("zipcode") is not None:
                row["zipcode"] = normalize_zipcode(row["zipcode"])
            if row.get("country") is not None:
                row["country"] = normalize_country(row["country"])
            if row.get("first_name") is not None:
                row["first_name"] = title_case(row["first_name"])
            if row.get("last_name") is not None:
                row["last_name"] = title_case(row["last_name"])
            if row.get("first_name") and row.get("last_name"):
                row["full_name"] = f"{row['first_name']} {row['last_name']}"
        rows = self._apply_business_rules(rows)
        rows = self._enrich(rows)
        return rows


class ProductsTransformer(BaseTransformer):
    """Transformer for the products raw dataset (CSV)."""

    def load(self) -> list[dict[str, Any]]:
        with self.raw_path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = self._clean(rows)
        rows = self._impute(rows)
        rows = self._deduplicate(rows)
        rows = self._standardize(rows)
        for row in rows:
            if row.get("category") is not None:
                row["category"] = normalize_category(row["category"])
            # Map FakeStore API fields to platform schema
            if "id" in row and "product_id" not in row:
                row["product_id"] = str(row.get("id", ""))
            if "title" in row and "product_name" not in row:
                row["product_name"] = row.get("title", "")
            if "price" in row and "selling_price" not in row:
                row["selling_price"] = row.get("price")
        rows = self._apply_business_rules(rows)
        rows = self._enrich(rows)
        return rows


class InventoryTransformer(BaseTransformer):
    """Transformer for the inventory raw dataset."""

    def load(self) -> list[dict[str, Any]]:
        with self.raw_path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = self._clean(rows)
        rows = self._impute(rows)
        rows = self._deduplicate(rows)
        rows = self._standardize(rows)
        rows = self._apply_business_rules(rows)
        rows = self._enrich(rows)
        return rows


class OrdersTransformer(BaseTransformer):
    """Transformer for the orders raw dataset."""

    def load(self) -> list[dict[str, Any]]:
        with self.raw_path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = self._clean(rows)
        rows = self._impute(rows)
        rows = self._deduplicate(rows)
        rows = self._standardize(rows)
        for row in rows:
            if row.get("quantity") is not None:
                row["quantity"] = integer(row["quantity"])
        rows = self._apply_business_rules(rows)
        rows = self._enrich(rows)
        return rows


class PaymentsTransformer(BaseTransformer):
    """Transformer for the payments raw dataset."""

    def load(self) -> list[dict[str, Any]]:
        with self.raw_path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = self._clean(rows)
        rows = self._impute(rows)
        rows = self._deduplicate(rows)
        rows = self._standardize(rows)
        rows = self._apply_business_rules(rows)
        return rows


class ShippingTransformer(BaseTransformer):
    """Transformer for the shipping raw dataset."""

    def load(self) -> list[dict[str, Any]]:
        with self.raw_path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = self._clean(rows)
        rows = self._impute(rows)
        rows = self._deduplicate(rows)
        rows = self._standardize(rows)
        rows = self._apply_business_rules(rows)
        return rows


class ReviewsTransformer(BaseTransformer):
    """Transformer for the reviews raw dataset."""

    def load(self) -> list[dict[str, Any]]:
        with self.raw_path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = self._clean(rows)
        rows = self._impute(rows)
        rows = self._deduplicate(rows)
        rows = self._standardize(rows)
        rows = self._apply_business_rules(rows)
        rows = self._enrich(rows)
        return rows


class WebsiteEventsTransformer(BaseTransformer):
    """Transformer for the website events raw dataset."""

    def load(self) -> list[dict[str, Any]]:
        text = self.raw_path.read_text(encoding="utf-8").strip()
        if not text:
            return []
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = [json.loads(line) for line in text.splitlines() if line.strip()]
        if isinstance(payload, list):
            return [_flatten_dict(item) if isinstance(item, dict) else {"value": item} for item in payload]
        return [_flatten_dict(payload)] if isinstance(payload, dict) else []

    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for row in rows:
            if "timestamp" in row and "event_timestamp" not in row:
                row["event_timestamp"] = row.pop("timestamp")
            if "url" in row and "page_url" not in row:
                row["page_url"] = row.pop("url")
        rows = self._clean(rows)
        rows = self._impute(rows)
        rows = self._deduplicate(rows)
        rows = self._standardize(rows)
        rows = self._apply_business_rules(rows)
        return rows


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TransformerClass = Type[BaseTransformer]

_DATASET_TRANSFORMER_MAP: dict[str, TransformerClass] = {
    "customers": CustomersTransformer,
    "products": ProductsTransformer,
    "inventory": InventoryTransformer,
    "orders": OrdersTransformer,
    "payments": PaymentsTransformer,
    "shipping": ShippingTransformer,
    "reviews": ReviewsTransformer,
    "website_events": WebsiteEventsTransformer,
}


class TransformerRegistry:
    """Registry that maps dataset names to concrete transformer classes.

    New datasets can be registered at runtime without modifying this file,
    which satisfies the Open/Closed principle.
    """

    def __init__(self) -> None:
        self._registry: dict[str, TransformerClass] = dict(_DATASET_TRANSFORMER_MAP)

    def register(self, dataset: str, transformer_class: TransformerClass) -> None:
        """Register a custom transformer for a dataset name."""
        self._registry[dataset] = transformer_class

    def get(self, dataset: str) -> TransformerClass | None:
        """Return the transformer class for a dataset, or None if unregistered."""
        return self._registry.get(dataset)

    def supported_datasets(self) -> tuple[str, ...]:
        """Return the names of all registered datasets."""
        return tuple(sorted(self._registry))

    def create(
        self,
        dataset: str,
        raw_path: Path,
        processed_dir: Path,
        transform_report_dir: Path,
        config: TransformationConfig | None = None,
        logger: logging.Logger | None = None,
        primary_key: str | None = None,
    ) -> BaseTransformer:
        """Instantiate a transformer for a named dataset.

        Raises:
            KeyError: If the dataset has no registered transformer.
        """
        transformer_class = self._registry.get(dataset)
        if transformer_class is None:
            raise KeyError(f"No transformer registered for dataset '{dataset}'")
        return transformer_class(
            dataset=dataset,
            raw_path=raw_path,
            processed_dir=processed_dir,
            transform_report_dir=transform_report_dir,
            config=config or TRANSFORMATION_CONFIG,
            logger=logger or logging.getLogger(f"transform.{dataset}"),
            primary_key=primary_key,
        )


def build_default_registry() -> TransformerRegistry:
    """Return a registry pre-loaded with all built-in dataset transformers."""
    return TransformerRegistry()


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _flatten_dict(record: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten nested dictionaries using dotted-key names."""
    flattened: dict[str, Any] = {}
    for key, value in record.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            flattened.update(_flatten_dict(value, name))
        else:
            flattened[name] = value
    return flattened
