"""Processed data and transformation report exporters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config.pipeline_run import get_pipeline_run_id
from transform.metrics import TransformationMetrics
from transform.utils import write_csv, write_json


def export_processed_dataset(
    output_dir: Path,
    dataset: str,
    rows: list[dict[str, Any]],
    fieldnames: list[str],
) -> Path:
    """Write a processed dataset as CSV."""
    output_path = output_dir / f"{dataset}.csv"
    write_csv(output_path, rows, fieldnames)
    return output_path


def export_dataset_report(report_dir: Path, metrics: TransformationMetrics) -> Path:
    """Write one dataset transformation report."""
    path = report_dir / f"{metrics.dataset}.json"
    write_json(path, {"pipeline_run_id": get_pipeline_run_id(), **metrics.to_dict()})
    return path


def export_summary(report_dir: Path, metrics: list[TransformationMetrics]) -> Path:
    """Write the overall transformation summary."""
    path = report_dir / "transformation_summary.json"
    successful = sum(1 for item in metrics if item.status == "SUCCESS")
    failed = sum(1 for item in metrics if item.status == "FAILED")
    payload = {
        "pipeline_run_id": get_pipeline_run_id(),
        "datasets": len(metrics),
        "successful": successful,
        "failed": failed,
        "rows_read": sum(item.rows_read for item in metrics),
        "rows_dropped": sum(item.rows_dropped for item in metrics),
        "rows_repaired": sum(item.rows_repaired for item in metrics),
        "rows_imputed": sum(item.rows_imputed for item in metrics),
        "rows_standardized": sum(item.rows_standardized for item in metrics),
        "rows_output": sum(item.rows_output for item in metrics),
        "dataset_metrics": [item.to_dict() for item in metrics],
    }
    write_json(path, payload)
    return path

