"""Validation manager for Phase 3 data quality checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.logging_config import configure_logging
from config.pipeline_run import get_pipeline_run_id, set_pipeline_run_id
from config.settings import settings
from validate.report_generator import ValidationReportGenerator
from validate.validation_registry import ValidationRegistry, build_default_registry, default_datasets


def run_validation(
    pipeline_run_id: str | None = None,
    registry: ValidationRegistry | None = None,
) -> list[dict[str, Any]]:
    """Run validation for all configured raw datasets."""
    active_run_id = set_pipeline_run_id(pipeline_run_id or _pipeline_run_id_from_manifest())
    logger = configure_logging(pipeline_run_id=active_run_id)
    logger.info("Validation started")
    active_registry = registry or build_default_registry()
    context = _build_context()
    reports: list[dict[str, Any]] = []

    for dataset_config in default_datasets():
        logger.info("%s | dataset validation started", dataset_config.name)
        validator = active_registry.create(dataset_config, logger)
        report = validator.run(context)
        reports.append(report)

    recommendation = _pipeline_recommendation(reports)
    report_generator = ValidationReportGenerator(Path(settings.directories.log_dir) / "validation")
    paths = report_generator.write_all(reports, recommendation)
    logger.info("Validation reports generated: %s", paths)
    logger.info("Validation completed")
    return reports


def _pipeline_run_id_from_manifest() -> str | None:
    """Reuse ingestion run ID when validation is run standalone after ingestion."""
    manifest_path = Path(settings.directories.log_dir) / "ingestion_manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8")).get("pipeline_run_id")
    except json.JSONDecodeError:
        return None


def _build_context() -> dict[str, set[str]]:
    """Build cross-dataset lookup sets for foreign-key checks."""
    raw_dir = Path(settings.directories.raw_data_dir)
    context: dict[str, set[str]] = {}
    context["customers"] = _csv_values(raw_dir / "customers.csv", "customer_id")
    context["orders"] = _csv_values(raw_dir / "orders.csv", "order_id")
    context["products"] = _product_ids(raw_dir / "products.json")
    context["delivered_purchase_pairs"] = _delivered_purchase_pairs(raw_dir)
    return context


def _csv_values(path: Path, column: str) -> set[str]:
    """Load one column from a CSV file into a set."""
    if not path.is_file():
        return set()
    import csv

    with path.open("r", encoding="utf-8", newline="") as file_obj:
        return {row[column] for row in csv.DictReader(file_obj) if row.get(column)}


def _product_ids(path: Path) -> set[str]:
    """Load product IDs from raw JSON products."""
    if not path.is_file():
        return set()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        return set()
    return {str(item.get("id")) for item in payload if isinstance(item, dict) and item.get("id") is not None}


def _delivered_purchase_pairs(raw_dir: Path) -> set[str]:
    """Return customer/product pairs from delivered orders."""
    orders_path = raw_dir / "orders.csv"
    if not orders_path.is_file():
        return set()
    import csv

    pairs: set[str] = set()
    with orders_path.open("r", encoding="utf-8", newline="") as file_obj:
        for row in csv.DictReader(file_obj):
            if row.get("order_status") == "Delivered":
                pairs.add(f"{row.get('customer_id')}::{row.get('product_id')}")
    return pairs


def _pipeline_recommendation(reports: list[dict[str, Any]]) -> dict[str, str]:
    """Generate proceed/stop recommendation from dataset quality."""
    failed = [report["dataset"] for report in reports if report["status"] == "FAIL"]
    overall = round(sum(float(report["quality_score"]) for report in reports) / len(reports), 2) if reports else 0.0
    if failed or overall < 90:
        return {
            "decision": "Stop Pipeline",
            "reason": f"Quality score too low or failed datasets present. Overall={overall}; failed={', '.join(failed) or 'none'}.",
        }
    return {
        "decision": "Proceed to Transformation",
        "reason": f"Overall quality is {overall} and no dataset failed validation.",
    }


def main() -> None:
    """CLI entry point for Phase 3 validation."""
    run_validation()


if __name__ == "__main__":
    main()

