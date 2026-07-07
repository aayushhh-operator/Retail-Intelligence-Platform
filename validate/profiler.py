"""Dataset profiler wrapper used by validators."""

from __future__ import annotations

from typing import Any

from validate.statistics import generate_statistics


class DatasetProfiler:
    """Generate dataset profiles for validation reports."""

    def profile(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        """Return profiling statistics for loaded rows."""
        return generate_statistics(rows)
