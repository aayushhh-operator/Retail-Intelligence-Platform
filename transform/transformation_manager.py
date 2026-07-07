"""Transformation manager — Phase 4 orchestration entry point.

Running this module directly:

    python transform/transformation_manager.py

will:

1. Read every validated dataset from data/raw/
2. Load validation results from logs/validation/ to guide decisions
3. Apply cleaning, imputation, deduplication, standardization,
   business rules, and enrichment
4. Write analytics-ready CSV files to data/processed/
5. Write per-dataset transformation reports to logs/transform/dataset_reports/
6. Write a transformation summary JSON to logs/transform/

This phase never modifies or overwrites files in data/raw/.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.logging_config import configure_logging
from config.pipeline_run import get_pipeline_run_id, set_pipeline_run_id
from config.settings import settings
from transform.config import TRANSFORMATION_CONFIG, TransformationConfig
from transform.exporters import export_summary
from transform.metrics import TransformationMetrics
from transform.pipeline import TransformationPipelineRunner
from transform.registry import TransformerRegistry, build_default_registry


def run_transformation(
    pipeline_run_id: str | None = None,
    registry: TransformerRegistry | None = None,
    config: TransformationConfig | None = None,
) -> list[TransformationMetrics]:
    """Execute the Phase 4 transformation pipeline.

    Parameters
    ----------
    pipeline_run_id:
        If provided, reuses an existing run identifier (e.g., from Phase 3).
        If omitted, a new identifier is generated.
    registry:
        Optional custom registry for testing or extension.  The default
        registry includes all built-in dataset transformers.
    config:
        Optional custom configuration.  Defaults to ``TRANSFORMATION_CONFIG``.

    Returns
    -------
    list[TransformationMetrics]
        One ``TransformationMetrics`` instance per dataset attempted.
    """
    active_run_id = set_pipeline_run_id(
        pipeline_run_id or _pipeline_run_id_from_validation()
    )
    logger = configure_logging(pipeline_run_id=active_run_id)
    logger.info("Transformation started pipeline_run_id=%s", active_run_id)

    raw_dir = Path(settings.directories.raw_data_dir)
    processed_dir = Path(settings.directories.processed_data_dir)
    log_dir = Path(settings.directories.log_dir)
    validation_log_dir = log_dir / "validation"
    transform_report_dir = log_dir / "transform" / "dataset_reports"
    transform_report_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    runner = TransformationPipelineRunner(
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        validation_log_dir=validation_log_dir,
        transform_report_dir=transform_report_dir,
        registry=registry or build_default_registry(),
        config=config or TRANSFORMATION_CONFIG,
        logger=logger,
    )

    all_metrics = runner.run()

    summary_path = export_summary(log_dir / "transform", all_metrics)
    logger.info("Transformation summary written to %s", summary_path)

    _log_summary(all_metrics, logger)
    logger.info("Transformation completed")
    return all_metrics


def _pipeline_run_id_from_validation() -> str | None:
    """Reuse the pipeline run ID from validation summary when available."""
    import json

    summary_path = (
        Path(settings.directories.log_dir) / "validation" / "validation_summary.json"
    )
    if not summary_path.is_file():
        return None
    try:
        return json.loads(summary_path.read_text(encoding="utf-8")).get(
            "pipeline_run_id"
        )
    except (json.JSONDecodeError, OSError):
        return None


def _log_summary(all_metrics: list[TransformationMetrics], logger: object) -> None:
    """Log a concise transformation summary."""
    successful = sum(1 for m in all_metrics if m.status == "SUCCESS")
    failed = sum(1 for m in all_metrics if m.status == "FAILED")
    skipped = sum(1 for m in all_metrics if m.status == "SKIPPED")
    rows_out = sum(m.rows_output for m in all_metrics)
    logger.info(  # type: ignore[union-attr]
        "Summary: datasets=%d successful=%d failed=%d skipped=%d rows_output=%d",
        len(all_metrics),
        successful,
        failed,
        skipped,
        rows_out,
    )
    for metrics in all_metrics:
        logger.info(  # type: ignore[union-attr]
            "  %-16s status=%-8s rows_read=%d rows_out=%d dropped=%d repaired=%d imputed=%d",
            metrics.dataset,
            metrics.status,
            metrics.rows_read,
            metrics.rows_output,
            metrics.rows_dropped,
            metrics.rows_repaired,
            metrics.rows_imputed,
        )


def main() -> None:
    """CLI entry point for Phase 4 transformation."""
    run_transformation()


if __name__ == "__main__":
    main()
