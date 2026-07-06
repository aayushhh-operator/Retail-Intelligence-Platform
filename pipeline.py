"""Top-level pipeline entry point for the Retail Intelligence Platform."""

from __future__ import annotations

from config.logging_config import configure_logging
from config.pipeline_run import set_pipeline_run_id
from extract.ingestion_manager import run_ingestion
from transform.transformation_manager import run_transformation
from validate.validation_manager import run_validation


def main() -> None:
    """Run the currently implemented pipeline phases."""
    pipeline_run_id = set_pipeline_run_id()
    logger = configure_logging(pipeline_run_id=pipeline_run_id)
    logger.info("Retail Intelligence Platform pipeline initialized.")

    run_ingestion(pipeline_run_id=pipeline_run_id)
    run_validation(pipeline_run_id=pipeline_run_id)
    run_transformation(pipeline_run_id=pipeline_run_id)
    # TODO(phase-5): Load curated data into the PostgreSQL warehouse.
    # TODO(phase-6): Build star schema facts and dimensions.
    # TODO(phase-7): Move orchestration into Airflow DAGs.
    # TODO(phase-8): Add Spark execution paths for larger workloads.
    # TODO(phase-9): Publish metrics for dashboard consumption.
    # TODO(phase-10): Expose AI assistant workflows.

    logger.info("Implemented pipeline phases completed.")


if __name__ == "__main__":
    main()
