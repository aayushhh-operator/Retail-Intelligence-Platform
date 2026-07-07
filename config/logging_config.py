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

    pipeline_filter = PipelineRunFilter()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(pipeline_run_id)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(pipeline_filter)
    logger.addHandler(console_handler)

    # Base Application Log (Rotating)
    from logging.handlers import RotatingFileHandler

    app_log_path = log_dir / "retail_intelligence.log"
    app_handler = RotatingFileHandler(
        app_log_path, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    app_handler.setLevel(log_level)
    app_handler.setFormatter(formatter)
    app_handler.addFilter(pipeline_filter)
    logger.addHandler(app_handler)

    # Dedicated Pipeline Log (Rotating)
    if "pipeline" in logger_name.lower() or pipeline_run_id:
        pipeline_log_path = log_dir / "pipeline.log"
        pipeline_handler = RotatingFileHandler(
            pipeline_log_path, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        pipeline_handler.setLevel(log_level)
        pipeline_handler.setFormatter(formatter)
        pipeline_handler.addFilter(pipeline_filter)
        logger.addHandler(pipeline_handler)

    # Dedicated AI Log (Rotating)
    if "ai" in logger_name.lower():
        ai_log_path = log_dir / "ai.log"
        ai_handler = RotatingFileHandler(
            ai_log_path, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        ai_handler.setLevel(logging.DEBUG)  # Always keep debug for AI
        ai_handler.setFormatter(formatter)
        ai_handler.addFilter(pipeline_filter)
        logger.addHandler(ai_handler)

    return logger
