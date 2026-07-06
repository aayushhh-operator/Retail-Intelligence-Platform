"""Reusable logging configuration for local and orchestrated execution."""

from __future__ import annotations

import logging
from logging import Logger
from pathlib import Path

from config.pipeline_run import get_pipeline_run_id, set_pipeline_run_id
from config.settings import settings


class PipelineRunFilter(logging.Filter):
    """Attach the active pipeline run identifier to each log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Populate the pipeline_run_id field expected by the formatter."""
        record.pipeline_run_id = get_pipeline_run_id()
        return True


def configure_logging(
    logger_name: str = "retail_intelligence",
    pipeline_run_id: str | None = None,
) -> Logger:
    """Configure console and file logging for pipeline-compatible execution."""
    if pipeline_run_id:
        set_pipeline_run_id(pipeline_run_id)

    log_level = getattr(logging, settings.logging.level.upper(), logging.INFO)
    log_dir = Path(settings.directories.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / settings.logging.log_file

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | %(name)s | "
            "%(pipeline_run_id)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    pipeline_filter = PipelineRunFilter()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(pipeline_filter)

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(pipeline_filter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
