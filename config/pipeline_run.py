"""Pipeline run identity helpers shared across pipeline phases."""

from __future__ import annotations

from contextvars import ContextVar
from datetime import datetime

_PIPELINE_RUN_ID: ContextVar[str] = ContextVar("pipeline_run_id", default="")


def generate_pipeline_run_id(created_at: datetime | None = None) -> str:
    """Create a run identifier such as RUN_20260706_143522."""
    timestamp = created_at or datetime.now()
    return f"RUN_{timestamp:%Y%m%d_%H%M%S}"


def set_pipeline_run_id(pipeline_run_id: str | None = None) -> str:
    """Set and return the active pipeline run identifier."""
    active_run_id = pipeline_run_id or generate_pipeline_run_id()
    _PIPELINE_RUN_ID.set(active_run_id)
    return active_run_id


def get_pipeline_run_id() -> str:
    """Return the active pipeline run identifier, creating one if needed."""
    pipeline_run_id = _PIPELINE_RUN_ID.get()
    if pipeline_run_id:
        return pipeline_run_id
    return set_pipeline_run_id()
