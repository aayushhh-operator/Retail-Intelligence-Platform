"""Base validator classes for dataset validation."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from config.pipeline_run import get_pipeline_run_id
from validate.business_rule_validator import BusinessRuleValidator
from validate.exceptions import ValidationError
from validate.profiler import DatasetProfiler
from validate.schema_validator import SchemaValidator
from validate.validator import (ValidationIssue, calculate_quality_score,
                                quality_status)


@dataclass(frozen=True)
class DatasetConfig:
    """Configuration for one raw dataset."""

    name: str
    path: Path
    file_type: str
    primary_key: str | None = None


class BaseValidator(ABC):
    """Base validator contract for raw datasets."""

    def __init__(
        self,
        dataset_config: DatasetConfig,
        logger: logging.Logger,
        schema_validator: SchemaValidator | None = None,
        rule_validator: BusinessRuleValidator | None = None,
        profiler: DatasetProfiler | None = None,
    ) -> None:
        self.dataset_config = dataset_config
        self.logger = logger
        self.schema_validator = schema_validator or SchemaValidator()
        self.rule_validator = rule_validator or BusinessRuleValidator()
        self.profiler = profiler or DatasetProfiler()
        self.rows: list[dict[str, Any]] = []
        self.statistics: dict[str, Any] = {}
        self.rule_results: list[dict[str, Any]] = []
        self.issues: list[ValidationIssue] = []
        self.quality_score = 0.0
        self.status = "FAIL"

    @abstractmethod
    def load(self) -> list[dict[str, Any]]:
        """Load raw records without modifying the source file."""

    def validate(self, context: dict[str, set[str]]) -> list[ValidationIssue]:
        """Run schema and business validation rules."""
        results = []
        self.logger.info("%s | schema validation started", self.dataset_config.name)
        results.extend(
            self.schema_validator.validate(self.dataset_config.name, self.rows)
        )
        self.logger.info("%s | business rules started", self.dataset_config.name)
        results.extend(
            self.rule_validator.validate(self.dataset_config.name, self.rows, context)
        )
        self.rule_results = [result.to_dict() for result in results]
        self.issues = [
            issue for result in results if (issue := result.to_issue()) is not None
        ]
        return self.issues

    def generate_statistics(self) -> dict[str, Any]:
        """Generate dataset profile statistics."""
        self.statistics = self.profiler.profile(self.rows)
        return self.statistics

    def generate_report(self, execution_time_seconds: float) -> dict[str, Any]:
        """Generate a JSON-serializable dataset validation report."""
        errors = sum(1 for issue in self.issues if issue.severity == "ERROR")
        warnings = sum(1 for issue in self.issues if issue.severity == "WARNING")
        self.quality_score = calculate_quality_score(len(self.rows), self.issues)
        self.status = quality_status(self.quality_score)
        return {
            "pipeline_run_id": get_pipeline_run_id(),
            "dataset": self.dataset_config.name,
            "file_path": str(self.dataset_config.path),
            "file_type": self.dataset_config.file_type,
            "validated_at": datetime.now().isoformat(timespec="seconds"),
            "rows": len(self.rows),
            "columns": len(self.statistics.get("column_names", [])),
            "errors": errors,
            "warnings": warnings,
            "quality_score": self.quality_score,
            "status": self.status,
            "execution_time_seconds": execution_time_seconds,
            "statistics": self.statistics,
            "validation_results": self.rule_results,
            "detected_issues": [issue.to_dict() for issue in self.issues],
        }

    def run(self, context: dict[str, set[str]]) -> dict[str, Any]:
        """Execute the full validation workflow for one dataset."""
        started_at = time.perf_counter()
        try:
            self.logger.info("%s | validation started", self.dataset_config.name)
            self.rows = self.load()
            self.generate_statistics()
            self.logger.info("%s | statistics generated", self.dataset_config.name)
            self.validate(context)
            elapsed = round(time.perf_counter() - started_at, 4)
            report = self.generate_report(elapsed)
            self.logger.info(
                "%s | validation completed status=%s score=%.2f",
                self.dataset_config.name,
                self.status,
                self.quality_score,
            )
            return report
        except Exception as exc:
            elapsed = round(time.perf_counter() - started_at, 4)
            self.logger.exception("%s | validation failed", self.dataset_config.name)
            return {
                "pipeline_run_id": get_pipeline_run_id(),
                "dataset": self.dataset_config.name,
                "file_path": str(self.dataset_config.path),
                "file_type": self.dataset_config.file_type,
                "validated_at": datetime.now().isoformat(timespec="seconds"),
                "rows": 0,
                "columns": 0,
                "errors": 1,
                "warnings": 0,
                "quality_score": 0.0,
                "status": "FAIL",
                "execution_time_seconds": elapsed,
                "statistics": {},
                "validation_results": [],
                "detected_issues": [
                    {
                        "rule_name": "dataset_load",
                        "severity": "ERROR",
                        "message": str(exc),
                        "affected_rows": 0,
                        "affected_columns": [],
                        "sample_values": [],
                    }
                ],
            }


def require_dataset(path: Path) -> None:
    """Raise if a raw dataset is missing."""
    if not path.is_file():
        raise ValidationError(f"Raw dataset does not exist: {path}")
