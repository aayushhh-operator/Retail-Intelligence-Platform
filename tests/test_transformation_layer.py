"""Tests for Phase 4 data transformation framework."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

import pytest

from config.pipeline_run import set_pipeline_run_id
from transform.base_transformer import BaseTransformer
from transform.business_rules import apply_business_rules
from transform.cleaning import blank_to_none, clean_email, trim_whitespace
from transform.config import (BusinessRuleConfig, ImputationConfig,
                              TransformationConfig)
from transform.deduplication import (remove_exact_duplicates,
                                     remove_primary_key_duplicates)
from transform.enrichment import enrich
from transform.imputation import impute_rows
from transform.metrics import TransformationMetrics
from transform.normalization import (normalize_category, normalize_country,
                                     normalize_phone, normalize_zipcode)
from transform.registry import build_default_registry
from transform.standardization import (boolean_value, money, standard_date,
                                       title_case)

# ---------------------------------------------------------------------------
# Cleaning tests
# ---------------------------------------------------------------------------


def test_trim_whitespace_removes_leading_trailing_spaces() -> None:
    rows = [{"name": "  Alice  ", "city": " London "}]
    affected = trim_whitespace(rows)
    assert rows[0]["name"] == "Alice"
    assert rows[0]["city"] == "London"
    assert affected == 1


def test_blank_to_none_converts_empty_strings() -> None:
    rows = [{"email": "", "phone": "123"}]
    blank_to_none(rows)
    assert rows[0]["email"] is None
    assert rows[0]["phone"] == "123"


def test_clean_email_repairs_common_typos() -> None:
    email, repaired = clean_email("user@gmail.con")
    assert email == "user@gmail.com"
    assert repaired is True


def test_clean_email_leaves_valid_address_unchanged() -> None:
    email, repaired = clean_email("user@example.com")
    assert email == "user@example.com"
    assert repaired is False


# ---------------------------------------------------------------------------
# Normalization tests
# ---------------------------------------------------------------------------


def test_normalize_phone_strips_non_digits_preserves_plus() -> None:
    assert normalize_phone("+91 98765-43210") == "+919876543210"


def test_normalize_zipcode_removes_non_digits() -> None:
    assert normalize_zipcode("400-001") == "400001"


def test_normalize_country_maps_india_variants() -> None:
    assert normalize_country("india") == "India"
    assert normalize_country("bharat") == "India"
    assert normalize_country("IN") == "India"


def test_normalize_category_maps_fake_store_categories() -> None:
    assert normalize_category("jewelery") == "Jewelry"
    assert normalize_category("men's clothing") == "Mens Clothing"


# ---------------------------------------------------------------------------
# Standardization tests
# ---------------------------------------------------------------------------


def test_standard_date_returns_iso_format() -> None:
    assert standard_date("2024-01-15") == "2024-01-15"
    assert standard_date("2024-01-15 10:30:00") == "2024-01-15"


def test_boolean_value_handles_multiple_representations() -> None:
    assert boolean_value("true") is True
    assert boolean_value("1") is True
    assert boolean_value("false") is False
    assert boolean_value("0") is False
    assert boolean_value("yes") is True
    assert boolean_value("no") is False


def test_money_rounds_to_two_decimal_places() -> None:
    assert money("19.999") == 20.0
    assert money("10.5") == 10.5


def test_title_case_converts_correctly() -> None:
    assert title_case("  alice smith  ") == "Alice Smith"


# ---------------------------------------------------------------------------
# Deduplication tests
# ---------------------------------------------------------------------------


def test_remove_exact_duplicates_removes_identical_rows() -> None:
    rows = [
        {"id": "1", "name": "A"},
        {"id": "1", "name": "A"},
        {"id": "2", "name": "B"},
    ]
    result, dropped = remove_exact_duplicates(rows)
    assert len(result) == 2
    assert dropped == 1


def test_remove_primary_key_duplicates_keeps_first() -> None:
    rows = [{"id": "1", "name": "First"}, {"id": "1", "name": "Second"}]
    result, dropped = remove_primary_key_duplicates(rows, "id", keep="first")
    assert len(result) == 1
    assert result[0]["name"] == "First"
    assert dropped == 1


def test_remove_primary_key_duplicates_keeps_last() -> None:
    rows = [{"id": "1", "name": "First"}, {"id": "1", "name": "Second"}]
    result, dropped = remove_primary_key_duplicates(rows, "id", keep="last")
    assert result[0]["name"] == "Second"


# ---------------------------------------------------------------------------
# Imputation tests
# ---------------------------------------------------------------------------


def test_impute_constant_fills_missing_values() -> None:
    rows = [{"amount": None}, {"amount": "10"}]
    result, count = impute_rows(rows, {"amount": "constant:0"})
    assert result[0]["amount"] == "0"
    assert count == 1


def test_impute_drop_removes_rows_with_missing_column() -> None:
    rows = [{"email": None}, {"email": "test@example.com"}]
    result, count = impute_rows(rows, {"email": "drop"})
    assert len(result) == 1
    assert count == 1


def test_impute_mode_uses_most_frequent_value() -> None:
    rows = [{"status": "Paid"}, {"status": "Paid"}, {"status": None}]
    result, count = impute_rows(rows, {"status": "mode"})
    assert result[2]["status"] == "Paid"
    assert count == 1


# ---------------------------------------------------------------------------
# Enrichment tests
# ---------------------------------------------------------------------------


def test_enrich_customers_adds_derived_columns() -> None:
    rows = [{"date_of_birth": "1990-01-01", "signup_date": "2022-06-01"}]
    enrich("customers", rows)
    assert "customer_age" in rows[0]
    assert "customer_tenure_days" in rows[0]
    assert isinstance(rows[0]["customer_age"], int)
    assert rows[0]["customer_age"] >= 30


def test_enrich_orders_adds_date_parts() -> None:
    rows = [
        {
            "order_date": "2024-03-15",
            "total_amount": "150.00",
            "discount": "0.1",
            "quantity": "3",
        }
    ]
    enrich("orders", rows)
    assert rows[0]["order_year"] == 2024
    assert rows[0]["order_month"] == 3
    assert rows[0]["order_quarter"] == 1


def test_enrich_reviews_adds_sentiment() -> None:
    rows = [{"rating": "5"}, {"rating": "3"}, {"rating": "1"}]
    enrich("reviews", rows)
    assert rows[0]["review_sentiment"] == "Positive"
    assert rows[1]["review_sentiment"] == "Neutral"
    assert rows[2]["review_sentiment"] == "Negative"


def test_enrich_inventory_adds_status() -> None:
    rows = [
        {"current_stock": "5", "reorder_level": "10"},
        {"current_stock": "50", "reorder_level": "10"},
    ]
    enrich("inventory", rows)
    assert rows[0]["inventory_status"] == "Reorder"
    assert rows[1]["inventory_status"] == "Healthy"


# ---------------------------------------------------------------------------
# Business rules tests
# ---------------------------------------------------------------------------


def test_business_rules_drops_orders_with_zero_quantity() -> None:
    rows = [
        {
            "customer_id": "C1",
            "product_id": "P1",
            "quantity": "0",
            "total_amount": "50",
            "unit_price": "50",
        },
        {
            "customer_id": "C1",
            "product_id": "P1",
            "quantity": "2",
            "total_amount": "100",
            "unit_price": "50",
        },
    ]
    metrics = TransformationMetrics(dataset="orders")
    result = apply_business_rules("orders", rows, BusinessRuleConfig(), metrics)
    assert len(result) == 1
    assert metrics.rows_dropped == 1


def test_business_rules_clamps_review_rating_out_of_range() -> None:
    rows = [{"rating": "6"}]
    metrics = TransformationMetrics(dataset="reviews")
    config = BusinessRuleConfig(review_rating_strategy="clamp")
    result = apply_business_rules("reviews", rows, config, metrics)
    assert result[0]["rating"] == 5
    assert metrics.rows_repaired == 1


def test_business_rules_repairs_negative_inventory_stock() -> None:
    rows = [{"current_stock": "-5"}]
    metrics = TransformationMetrics(dataset="inventory")
    config = BusinessRuleConfig(inventory_negative_stock_strategy="zero")
    result = apply_business_rules("inventory", rows, config, metrics)
    assert result[0]["current_stock"] == 0
    assert metrics.rows_repaired == 1


def test_business_rules_flags_low_margin_products() -> None:
    rows = [{"selling_price": "10", "cost_price": "15", "product_id": "P1"}]
    metrics = TransformationMetrics(dataset="products")
    config = BusinessRuleConfig(product_low_margin_strategy="flag")
    result = apply_business_rules("products", rows, config, metrics)
    assert result[0]["low_margin_flag"] is True


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


def test_registry_contains_all_builtin_datasets() -> None:
    registry = build_default_registry()
    supported = registry.supported_datasets()
    expected = {
        "customers",
        "products",
        "inventory",
        "orders",
        "payments",
        "shipping",
        "reviews",
    }
    assert expected.issubset(set(supported))


def test_registry_raises_for_unknown_dataset(tmp_path: Path) -> None:
    registry = build_default_registry()
    with pytest.raises(KeyError, match="unknown_dataset"):
        registry.create(
            dataset="unknown_dataset",
            raw_path=tmp_path / "dummy.csv",
            processed_dir=tmp_path,
            transform_report_dir=tmp_path,
        )


# ---------------------------------------------------------------------------
# BaseTransformer integration tests
# ---------------------------------------------------------------------------


def _make_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write test rows to a CSV file."""
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


class _SimpleTransformer(BaseTransformer):
    """Minimal concrete transformer for testing BaseTransformer."""

    def load(self) -> list[dict[str, Any]]:
        with self.raw_path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = self._clean(rows)
        rows = self._deduplicate(rows)
        return rows


def test_base_transformer_run_produces_output_file(tmp_path: Path) -> None:
    """A successful transformer run should write a processed CSV."""
    set_pipeline_run_id("RUN_TEST_001")
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    validation_dir = tmp_path / "validation" / "dataset_reports"
    validation_dir.mkdir(parents=True)

    raw_file = raw_dir / "test_data.csv"
    _make_csv(raw_file, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])

    transformer = _SimpleTransformer(
        dataset="test_data",
        raw_path=raw_file,
        processed_dir=processed_dir,
        transform_report_dir=report_dir,
    )
    metrics = transformer.run(validation_log_dir=tmp_path / "validation")
    assert metrics.status == "SUCCESS"
    assert metrics.rows_read == 2
    assert metrics.rows_output == 2
    assert (processed_dir / "test_data.csv").is_file()


def test_base_transformer_run_marks_failed_on_missing_file(tmp_path: Path) -> None:
    """A missing raw file should result in FAILED status, not a crash."""

    class _BrokenTransformer(BaseTransformer):
        def load(self) -> list[dict[str, Any]]:
            raise FileNotFoundError("raw file missing")

        def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
            return rows

    transformer = _BrokenTransformer(
        dataset="missing_data",
        raw_path=tmp_path / "nonexistent.csv",
        processed_dir=tmp_path / "processed",
        transform_report_dir=tmp_path / "reports",
    )
    metrics = transformer.run(validation_log_dir=tmp_path / "validation")
    assert metrics.status == "FAILED"
    assert "raw file missing" in (metrics.error_message or "")


def test_base_transformer_reads_validation_results(tmp_path: Path) -> None:
    """Transformer should load validation quality score from the report."""
    set_pipeline_run_id("RUN_TEST_002")
    validation_dir = tmp_path / "validation" / "dataset_reports"
    validation_dir.mkdir(parents=True)
    report = {"dataset": "customers", "status": "WARNING", "quality_score": 92.5}
    (validation_dir / "customers.json").write_text(json.dumps(report), encoding="utf-8")

    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    report_dir = tmp_path / "reports"
    report_dir.mkdir()

    raw_file = raw_dir / "customers.csv"
    _make_csv(
        raw_file, [{"customer_id": "C1", "first_name": "Alice", "last_name": "Smith"}]
    )

    registry = build_default_registry()
    transformer = registry.create(
        dataset="customers",
        raw_path=raw_file,
        processed_dir=processed_dir,
        transform_report_dir=report_dir,
        primary_key="customer_id",
    )
    metrics = transformer.run(validation_log_dir=tmp_path / "validation")
    assert metrics.validation_status == "WARNING"
    assert metrics.validation_quality_score == 92.5
