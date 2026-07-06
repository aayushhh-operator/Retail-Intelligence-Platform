"""Generic and business-specific validation rules."""

from __future__ import annotations

from collections import Counter
from datetime import timedelta
from typing import Any

from config.settings import settings
from validate.utils import EMAIL_PATTERN, PHONE_PATTERN, ZIP_PATTERN, is_blank, parse_date, to_float, today
from validate.validator import RuleResult

ALLOWED_CATEGORIES = {
    "Electronics", "Fashion", "Books", "Home", "Sports", "Beauty", "Toys",
    "Kitchen", "Office", "Groceries", "electronics", "jewelery",
    "men's clothing", "women's clothing",
}
ALLOWED_PAYMENT_METHODS = {"Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet", "Cash on Delivery"}
ALLOWED_CARRIERS = {"BlueDart", "Delhivery", "Ecom Express", "FedEx", "DHL", "India Post"}
ALLOWED_WAREHOUSES = {"WH-NORTH-01", "WH-WEST-01", "WH-SOUTH-01", "WH-EAST-01", "WH-CENTRAL-01"}


class BusinessRuleValidator:
    """Run generic and dataset-specific quality rules."""

    def validate(
        self,
        dataset_name: str,
        rows: list[dict[str, Any]],
        context: dict[str, set[str]],
    ) -> list[RuleResult]:
        """Run generic and business validation rules."""
        results = self._generic_rules(dataset_name, rows)
        dataset_method = getattr(self, f"_validate_{dataset_name}", None)
        if dataset_method:
            results.extend(dataset_method(rows, context))
        return results

    def _generic_rules(self, dataset_name: str, rows: list[dict[str, Any]]) -> list[RuleResult]:
        columns = sorted({column for row in rows for column in row.keys()})
        blank_rows = sum(1 for row in rows if any(is_blank(row.get(column)) for column in columns))
        duplicate_rows = _duplicate_row_count(rows)
        return [
            RuleResult("missing_values", blank_rows == 0, "WARNING", blank_rows, f"{blank_rows} rows contain blank values"),
            RuleResult("duplicate_rows", duplicate_rows == 0, "WARNING", duplicate_rows, f"{duplicate_rows} duplicate rows detected"),
        ]

    def _validate_customers(self, rows: list[dict[str, Any]], _context: dict[str, set[str]]) -> list[RuleResult]:
        return [
            _unique_key(rows, "customer_id"),
            _not_blank(rows, "customer_id"),
            _regex_rule(rows, "email", EMAIL_PATTERN, "valid_email"),
            _regex_rule(rows, "phone", PHONE_PATTERN, "valid_phone"),
            _regex_rule(rows, "zipcode", ZIP_PATTERN, "valid_zipcode"),
            _date_not_future(rows, "signup_date"),
            _not_blank(rows, "first_name"),
            _not_blank(rows, "last_name"),
        ]

    def _validate_products(self, rows: list[dict[str, Any]], _context: dict[str, set[str]]) -> list[RuleResult]:
        return [
            _positive_number(rows, "price"),
            _number_between(rows, "rating.rate", 1, 5, "valid_rating"),
            _allowed_values(rows, "category", ALLOWED_CATEGORIES, "valid_category"),
            _outlier_rule(rows, "price", "outlier_price"),
        ]

    def _validate_inventory(self, rows: list[dict[str, Any]], _context: dict[str, set[str]]) -> list[RuleResult]:
        return [
            _non_negative_number(rows, "current_stock"),
            _allowed_values(rows, "warehouse", ALLOWED_WAREHOUSES, "valid_warehouse"),
            _not_blank(rows, "product_id"),
        ]

    def _validate_orders(self, rows: list[dict[str, Any]], context: dict[str, set[str]]) -> list[RuleResult]:
        return [
            _unique_key(rows, "order_id"),
            _foreign_key(rows, "customer_id", context.get("customers", set()), "customer_exists"),
            _foreign_key(rows, "product_id", context.get("products", set()), "product_exists"),
            _positive_number(rows, "quantity"),
            _positive_number(rows, "total_amount"),
            _date_not_future(rows, "order_date"),
            _outlier_rule(rows, "total_amount", "outlier_order_amount"),
            _outlier_rule(rows, "quantity", "outlier_order_quantity"),
        ]

    def _validate_payments(self, rows: list[dict[str, Any]], context: dict[str, set[str]]) -> list[RuleResult]:
        return [
            _unique_key(rows, "payment_id"),
            _foreign_key(rows, "order_id", context.get("orders", set()), "order_exists"),
            _positive_number(rows, "amount"),
            _allowed_values(rows, "payment_method", ALLOWED_PAYMENT_METHODS, "valid_payment_method"),
            _date_not_future(rows, "transaction_time"),
            _outlier_rule(rows, "amount", "outlier_payment_amount"),
        ]

    def _validate_shipping(self, rows: list[dict[str, Any]], context: dict[str, set[str]]) -> list[RuleResult]:
        return [
            _unique_key(rows, "shipping_id"),
            _foreign_key(rows, "order_id", context.get("orders", set()), "order_exists"),
            _allowed_values(rows, "carrier", ALLOWED_CARRIERS, "valid_carrier"),
            _date_order_rule(rows, "dispatch_date", "delivery_date", "delivery_after_dispatch"),
        ]

    def _validate_reviews(self, rows: list[dict[str, Any]], context: dict[str, set[str]]) -> list[RuleResult]:
        return [
            _unique_key(rows, "review_id"),
            _foreign_key(rows, "customer_id", context.get("customers", set()), "customer_exists"),
            _foreign_key(rows, "product_id", context.get("products", set()), "product_exists"),
            _number_between(rows, "rating", 1, 5, "rating_between_1_and_5"),
            _review_after_purchase(rows, context),
        ]


def _duplicate_row_count(rows: list[dict[str, Any]]) -> int:
    seen: set[tuple[tuple[str, str], ...]] = set()
    duplicates = 0
    for row in rows:
        signature = tuple(sorted((key, str(value)) for key, value in row.items()))
        if signature in seen:
            duplicates += 1
        else:
            seen.add(signature)
    return duplicates


def _unique_key(rows: list[dict[str, Any]], column: str) -> RuleResult:
    values = [str(row.get(column, "")) for row in rows if not is_blank(row.get(column))]
    duplicates = sum(count - 1 for count in Counter(values).values() if count > 1)
    return RuleResult(f"unique_{column}", duplicates == 0, "ERROR", duplicates, f"{duplicates} duplicate {column} values", [column])


def _not_blank(rows: list[dict[str, Any]], column: str) -> RuleResult:
    count = sum(1 for row in rows if is_blank(row.get(column)))
    return RuleResult(f"not_blank_{column}", count == 0, "ERROR", count, f"{count} blank {column} values", [column])


def _regex_rule(rows: list[dict[str, Any]], column: str, pattern: Any, rule_name: str) -> RuleResult:
    count = sum(1 for row in rows if not is_blank(row.get(column)) and not pattern.match(str(row.get(column))))
    return RuleResult(rule_name, count == 0, "ERROR", count, f"{count} invalid {column} values", [column])


def _positive_number(rows: list[dict[str, Any]], column: str) -> RuleResult:
    count = sum(1 for row in rows if (value := to_float(row.get(column))) is None or value <= 0)
    return RuleResult(f"positive_{column}", count == 0, "ERROR", count, f"{count} non-positive {column} values", [column])


def _non_negative_number(rows: list[dict[str, Any]], column: str) -> RuleResult:
    count = sum(1 for row in rows if (value := to_float(row.get(column))) is None or value < 0)
    return RuleResult(f"non_negative_{column}", count == 0, "ERROR", count, f"{count} negative {column} values", [column])


def _number_between(rows: list[dict[str, Any]], column: str, minimum: float, maximum: float, rule_name: str) -> RuleResult:
    count = sum(1 for row in rows if (value := to_float(row.get(column))) is None or value < minimum or value > maximum)
    return RuleResult(rule_name, count == 0, "ERROR", count, f"{count} {column} values outside {minimum}-{maximum}", [column])


def _date_not_future(rows: list[dict[str, Any]], column: str) -> RuleResult:
    current_date = today()
    count = sum(1 for row in rows if (value := parse_date(row.get(column))) is None or value > current_date)
    return RuleResult(f"{column}_not_future", count == 0, "ERROR", count, f"{count} invalid or future {column} values", [column])


def _allowed_values(rows: list[dict[str, Any]], column: str, allowed: set[str], rule_name: str) -> RuleResult:
    count = sum(1 for row in rows if not is_blank(row.get(column)) and str(row.get(column)) not in allowed)
    return RuleResult(rule_name, count == 0, "WARNING", count, f"{count} unexpected {column} values", [column])


def _foreign_key(rows: list[dict[str, Any]], column: str, valid_values: set[str], rule_name: str) -> RuleResult:
    count = sum(1 for row in rows if is_blank(row.get(column)) or str(row.get(column)) not in valid_values)
    return RuleResult(rule_name, count == 0, "ERROR", count, f"{count} {column} values do not reference known records", [column])


def _date_order_rule(rows: list[dict[str, Any]], start_column: str, end_column: str, rule_name: str) -> RuleResult:
    count = 0
    for row in rows:
        start = parse_date(row.get(start_column))
        end = parse_date(row.get(end_column))
        if start is None or end is None or end < start:
            count += 1
    return RuleResult(rule_name, count == 0, "ERROR", count, f"{count} rows violate date order", [start_column, end_column])


def _review_after_purchase(rows: list[dict[str, Any]], context: dict[str, set[str]]) -> RuleResult:
    delivered_pairs = context.get("delivered_purchase_pairs", set())
    count = 0
    for row in rows:
        pair = f"{row.get('customer_id')}::{row.get('product_id')}"
        review_date = parse_date(row.get("review_date"))
        if pair not in delivered_pairs or review_date is None or review_date > today() + timedelta(days=366):
            count += 1
    return RuleResult("verified_purchase_logic", count == 0, "ERROR", count, f"{count} reviews do not align to delivered purchases", ["customer_id", "product_id", "review_date"])


def _outlier_rule(rows: list[dict[str, Any]], column: str, rule_name: str | None = None) -> RuleResult:
    """Detect numeric outliers using IQR-based fencing (Tukey method).

    The multiplier is sourced from ``settings.validation.outlier_iqr_multiplier``
    so it can be tuned per environment without changing source code.
    """
    multiplier = settings.validation.outlier_iqr_multiplier
    name = rule_name or f"outlier_{column}"
    numeric_pairs = [(i, to_float(row.get(column))) for i, row in enumerate(rows)]
    values = sorted(v for _, v in numeric_pairs if v is not None)
    if len(values) < 4:
        return RuleResult(name, True, "WARNING", 0, f"Insufficient data for outlier detection on {column}", [column])
    q1 = _percentile(values, 25)
    q3 = _percentile(values, 75)
    iqr = q3 - q1
    lower_fence = q1 - multiplier * iqr
    upper_fence = q3 + multiplier * iqr
    outlier_count = sum(1 for _, v in numeric_pairs if v is not None and (v < lower_fence or v > upper_fence))
    return RuleResult(
        name,
        outlier_count == 0,
        "WARNING",
        outlier_count,
        f"{outlier_count} outlier values in {column} (IQR fences: [{lower_fence:.2f}, {upper_fence:.2f}])",
        [column],
    )


def _percentile(sorted_values: list[float], percentile: int) -> float:
    """Return the p-th percentile using linear interpolation on a pre-sorted list."""
    n = len(sorted_values)
    idx = (percentile / 100) * (n - 1)
    lower = int(idx)
    upper = min(lower + 1, n - 1)
    fraction = idx - lower
    return sorted_values[lower] + fraction * (sorted_values[upper] - sorted_values[lower])

