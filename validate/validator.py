"""Validation result models and scoring helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from config.settings import settings


@dataclass(frozen=True)
class ValidationIssue:
    """One validation issue produced by a rule."""

    rule_name: str
    severity: str
    message: str
    affected_rows: int
    affected_columns: list[str] = field(default_factory=list)
    sample_values: list[Any] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable issue."""
        return asdict(self)


@dataclass(frozen=True)
class RuleResult:
    """Result returned by one validation rule."""

    rule_name: str
    passed: bool
    severity: str
    affected_rows: int
    message: str
    affected_columns: list[str] = field(default_factory=list)
    sample_values: list[Any] = field(default_factory=list)

    def to_issue(self) -> ValidationIssue | None:
        """Convert a failed rule to a validation issue."""
        if self.passed:
            return None
        return ValidationIssue(
            rule_name=self.rule_name,
            severity=self.severity,
            message=self.message,
            affected_rows=self.affected_rows,
            affected_columns=self.affected_columns,
            sample_values=self.sample_values,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable result."""
        return asdict(self)


def quality_status(score: float) -> str:
    """Map a quality score to PASS, WARNING, or FAIL using configurable thresholds."""
    pass_threshold = settings.validation.pass_threshold
    warning_threshold = settings.validation.warning_threshold
    if score > pass_threshold:
        return "PASS"
    if score >= warning_threshold:
        return "WARNING"
    return "FAIL"


def calculate_quality_score(row_count: int, issues: list[ValidationIssue]) -> float:
    """Calculate a dataset quality score from issue impact.

    Error severity counts as full impact. Warning severity counts as half impact.
    The denominator scales with row count and number of failed rules so large
    datasets are not overly punished for a small number of bad records.
    """
    if row_count <= 0:
        return 0.0 if issues else 100.0

    weighted_impact = 0.0
    for issue in issues:
        multiplier = 1.0 if issue.severity == "ERROR" else 0.5
        weighted_impact += min(issue.affected_rows, row_count) * multiplier

    denominator = row_count * max(1, len(issues))
    score = max(0.0, 100.0 - (weighted_impact / denominator * 100.0))
    return round(score, 2)

