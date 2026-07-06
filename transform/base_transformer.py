"""Base transformer class for all dataset-specific transformers."""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from config.pipeline_run import get_pipeline_run_id
from transform.business_rules import apply_business_rules
from transform.cleaning import blank_to_none, clean_email, trim_whitespace
from transform.config import TRANSFORMATION_CONFIG, TransformationConfig
from transform.deduplication import remove_exact_duplicates, remove_primary_key_duplicates
from transform.enrichment import enrich
from transform.exceptions import TransformationError
from transform.imputation import impute_rows
from transform.metrics import TransformationMetrics
from transform.schema_mapper import apply_schema
from transform.standardization import boolean_value, money, standard_date


class BaseTransformer(ABC):
    """Abstract base class defining the transformation contract.

    Every concrete transformer must implement ``load()`` and ``transform()``.
    The ``run()`` method orchestrates the full transformation pipeline:

    1. Load validation results (guides drop/repair decisions)
    2. Load raw dataset
    3. Clean (trim, blank→None, email repair)
    4. Impute missing values
    5. Deduplicate
    6. Standardize field types
    7. Apply business rules
    8. Enrich with derived columns
    9. Apply final schema ordering
    10. Export processed dataset
    """

    def __init__(
        self,
        dataset: str,
        raw_path: Path,
        processed_dir: Path,
        transform_report_dir: Path,
        config: TransformationConfig | None = None,
        logger: logging.Logger | None = None,
        primary_key: str | None = None,
    ) -> None:
        self.dataset = dataset
        self.raw_path = raw_path
        self.processed_dir = processed_dir
        self.transform_report_dir = transform_report_dir
        self.config = config or TRANSFORMATION_CONFIG
        self.logger = logger or logging.getLogger(f"transform.{dataset}")
        self.primary_key = primary_key
        self.rows: list[dict[str, Any]] = []
        self.metrics = TransformationMetrics(dataset=dataset)

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def load(self) -> list[dict[str, Any]]:
        """Load the raw dataset into memory without modifying the source file."""

    @abstractmethod
    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply all dataset-specific transformations and return the result."""

    # ------------------------------------------------------------------
    # Shared transformation steps
    # ------------------------------------------------------------------

    def _load_validation_results(self, validation_log_dir: Path) -> dict[str, Any]:
        """Read per-dataset validation results to guide transformation decisions."""
        report_path = validation_log_dir / "dataset_reports" / f"{self.dataset}.json"
        if not report_path.is_file():
            self.logger.warning("%s | no validation report found at %s", self.dataset, report_path)
            return {}
        try:
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.metrics.validation_status = payload.get("status")
            self.metrics.validation_quality_score = payload.get("quality_score")
            self.logger.info(
                "%s | validation status=%s quality=%.2f",
                self.dataset,
                self.metrics.validation_status,
                self.metrics.validation_quality_score or 0.0,
            )
            return payload
        except (json.JSONDecodeError, OSError) as exc:
            self.logger.warning("%s | failed to read validation report: %s", self.dataset, exc)
            return {}

    def _clean(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply generic cleaning: trim whitespace, blank→None, email repair."""
        trim_whitespace(rows)
        blank_to_none(rows)
        if self.config.business_rules.repair_emails and any("email" in row for row in rows):
            repaired = 0
            for row in rows:
                if row.get("email") is not None:
                    cleaned, was_repaired = clean_email(row["email"])
                    row["email"] = cleaned
                    if was_repaired:
                        repaired += 1
            if repaired:
                self.metrics.rows_repaired += repaired
                self.metrics.steps.append(f"email_repair:{repaired}")
        self.metrics.steps.append("clean")
        return rows

    def _impute(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply per-column imputation strategies from config."""
        strategies = self.config.imputation.strategies.get(self.dataset, {})
        if not strategies:
            return rows
        rows, count = impute_rows(rows, strategies)
        self.metrics.rows_imputed += count
        self.metrics.steps.append(f"impute:{count}")
        return rows

    def _deduplicate(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove exact duplicates then primary-key duplicates."""
        keep = self.config.deduplication.keep
        rows, exact_dropped = remove_exact_duplicates(rows, keep=keep)
        rows, pk_dropped = remove_primary_key_duplicates(rows, self.primary_key, keep=keep)
        dropped = exact_dropped + pk_dropped
        self.metrics.rows_dropped += dropped
        self.metrics.steps.append(f"dedup:{dropped}")
        return rows

    def _standardize(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Standardize common field types: dates, booleans, money amounts."""
        standardized = 0
        date_fields = {"signup_date", "date_of_birth", "order_date", "dispatch_date", "delivery_date", "review_date", "last_updated", "launch_date"}
        boolean_fields = {"is_active", "verified_purchase"}
        money_fields = {"cost_price", "selling_price", "unit_price", "total_amount", "amount", "shipping_cost", "tax", "discount"}
        for row in rows:
            changed = False
            for field in date_fields:
                if field in row and row[field] is not None:
                    row[field] = standard_date(row[field])
                    changed = True
            for field in boolean_fields:
                if field in row:
                    row[field] = boolean_value(row[field])
                    changed = True
            for field in money_fields:
                if field in row and row[field] is not None:
                    row[field] = money(row[field])
                    changed = True
            if changed:
                standardized += 1
        self.metrics.rows_standardized += standardized
        self.metrics.steps.append(f"standardize:{standardized}")
        return rows

    def _apply_business_rules(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply dataset-specific business rules (drop/repair logic)."""
        before = len(rows)
        rows = apply_business_rules(self.dataset, rows, self.config.business_rules, self.metrics)
        self.metrics.steps.append(f"business_rules:dropped={before - len(rows)}")
        return rows

    def _enrich(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Add derived analytics columns."""
        enriched = enrich(self.dataset, rows)
        self.metrics.steps.append(f"enrich:{enriched}")
        return rows

    def _apply_schema(self, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
        """Apply final column ordering per the processed schema."""
        mapped, fieldnames = apply_schema(self.dataset, rows)
        self.metrics.steps.append("schema_map")
        return mapped, fieldnames

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def run(self, validation_log_dir: Path) -> TransformationMetrics:
        """Execute the full transformation pipeline for this dataset.

        The transformation never modifies raw source files. All output is
        written to ``processed_dir``. On any unrecoverable error the metrics
        are marked FAILED and the exception is logged but not re-raised so
        other datasets continue transforming.
        """
        started_at = time.perf_counter()
        try:
            self.logger.info("%s | transformation started", self.dataset)
            validation_report = self._load_validation_results(validation_log_dir)

            if validation_report.get("status") == "FAIL":
                self.logger.warning(
                    "%s | validation status is FAIL (score=%.2f); transformation will proceed with caution",
                    self.dataset,
                    validation_report.get("quality_score", 0.0),
                )

            rows = self.load()
            self.metrics.rows_read = len(rows)
            self.logger.info("%s | loaded %d rows", self.dataset, len(rows))
            self.metrics.steps.append(f"load:{len(rows)}")

            rows = self.transform(rows)

            self.metrics.rows_output = len(rows)
            final_rows, fieldnames = self._apply_schema(rows)

            from transform.exporters import export_dataset_report, export_processed_dataset
            output_path = export_processed_dataset(self.processed_dir, self.dataset, final_rows, fieldnames)
            self.logger.info("%s | wrote %d rows to %s", self.dataset, len(final_rows), output_path)

            self.metrics.execution_time_seconds = round(time.perf_counter() - started_at, 4)
            self.metrics.status = "SUCCESS"
            export_dataset_report(self.transform_report_dir, self.metrics)
            self.logger.info(
                "%s | transformation completed status=SUCCESS rows_out=%d",
                self.dataset,
                self.metrics.rows_output,
            )
        except Exception as exc:
            self.metrics.execution_time_seconds = round(time.perf_counter() - started_at, 4)
            self.metrics.status = "FAILED"
            self.metrics.error_message = str(exc)
            self.logger.exception("%s | transformation failed: %s", self.dataset, exc)

        return self.metrics
