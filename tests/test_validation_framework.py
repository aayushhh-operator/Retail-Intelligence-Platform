"""Tests for Phase 3 data validation framework."""

from __future__ import annotations

import json
from pathlib import Path

from config.pipeline_run import set_pipeline_run_id
from validate.business_rule_validator import BusinessRuleValidator
from validate.report_generator import ValidationReportGenerator
from validate.schema_validator import SchemaValidator
from validate.statistics import generate_statistics
from validate.validator import (ValidationIssue, calculate_quality_score,
                                quality_status)


def test_email_validator_detects_invalid_email() -> None:
    """Customer validation should detect invalid email formats."""
    rows = [
        {
            "customer_id": "CUS000001",
            "first_name": "A",
            "last_name": "B",
            "email": "not-an-email",
            "phone": "+911234567890",
            "zipcode": "400001",
            "signup_date": "2024-01-01",
        }
    ]

    results = BusinessRuleValidator().validate("customers", rows, {})

    assert any(
        result.rule_name == "valid_email" and not result.passed for result in results
    )


def test_price_validator_detects_negative_product_price() -> None:
    """Product validation should reject non-positive prices."""
    rows = [{"id": 1, "price": -1, "rating.rate": 4.2, "category": "electronics"}]

    results = BusinessRuleValidator().validate("products", rows, {})

    assert any(
        result.rule_name == "positive_price" and result.affected_rows == 1
        for result in results
    )


def test_date_validator_detects_future_order_date() -> None:
    """Order validation should detect future order dates."""
    rows = [
        {
            "order_id": "ORD000001",
            "customer_id": "CUS000001",
            "product_id": "1",
            "quantity": 1,
            "total_amount": 10,
            "order_date": "2999-01-01",
        }
    ]
    context = {"customers": {"CUS000001"}, "products": {"1"}}

    results = BusinessRuleValidator().validate("orders", rows, context)

    assert any(
        result.rule_name == "order_date_not_future" and not result.passed
        for result in results
    )


def test_schema_validator_detects_missing_required_column() -> None:
    """Schema validation should report missing expected columns."""
    rows = [{"customer_id": "CUS000001"}]

    results = SchemaValidator().validate("customers", rows)

    required_result = next(
        result for result in results if result.rule_name == "required_columns"
    )
    assert not required_result.passed
    assert "email" in required_result.affected_columns


def test_quality_score_and_status() -> None:
    """Quality scoring should map issue impact to expected statuses."""
    issues = [
        ValidationIssue(
            rule_name="positive_quantity",
            severity="ERROR",
            message="bad quantity",
            affected_rows=5,
        )
    ]

    score = calculate_quality_score(100, issues)

    assert score == 95.0
    assert quality_status(score) == "WARNING"


def test_statistics_generation() -> None:
    """Profiling should calculate row, column, missing, and numeric statistics."""
    stats = generate_statistics(
        [
            {"amount": "10", "status": "Paid"},
            {"amount": "20", "status": ""},
        ]
    )

    assert stats["rows"] == 2
    assert stats["columns"] == 2
    assert stats["columns_profile"]["status"]["missing_count"] == 1
    assert stats["columns_profile"]["amount"]["mean"] == 15.0


def test_report_generation_includes_dashboard_json(tmp_path: Path) -> None:
    """Report generation should create dashboard-ready quality JSON."""
    set_pipeline_run_id("RUN_20260706_143522")
    reports = [
        {
            "pipeline_run_id": "RUN_20260706_143522",
            "dataset": "customers",
            "rows": 10,
            "columns": 3,
            "errors": 0,
            "warnings": 1,
            "quality_score": 98.2,
            "status": "PASS",
            "execution_time_seconds": 0.01,
            "statistics": {},
            "detected_issues": [],
        }
    ]
    generator = ValidationReportGenerator(tmp_path)

    paths = generator.write_all(
        reports,
        {"decision": "Proceed to Transformation", "reason": "test"},
    )

    dashboard = json.loads(paths["dashboard"].read_text(encoding="utf-8"))
    assert dashboard["pipeline_run_id"] == "RUN_20260706_143522"
    assert dashboard["datasets"][0]["name"] == "customers"
    assert paths["summary"].is_file()
    assert paths["csv"].is_file()
    assert paths["html"].is_file()
