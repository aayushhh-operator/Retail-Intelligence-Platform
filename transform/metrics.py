"""Transformation metrics models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TransformationMetrics:
    """Metrics collected for one dataset transformation."""

    dataset: str
    rows_read: int = 0
    rows_dropped: int = 0
    rows_repaired: int = 0
    rows_imputed: int = 0
    rows_standardized: int = 0
    rows_output: int = 0
    execution_time_seconds: float = 0.0
    status: str = "SUCCESS"
    error_message: str | None = None
    validation_status: str | None = None
    validation_quality_score: float | None = None
    steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable metrics."""
        return asdict(self)

