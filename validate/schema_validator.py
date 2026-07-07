"""Configurable schema validation rules."""

from __future__ import annotations

from typing import Any

from validate.utils import is_blank, parse_date, to_float
from validate.validator import RuleResult

EXPECTED_SCHEMAS: dict[str, dict[str, str]] = {
    "customers": {
        "customer_id": "string",
        "first_name": "string",
        "last_name": "string",
        "full_name": "string",
        "email": "string",
        "phone": "string",
        "gender": "string",
        "date_of_birth": "date",
        "city": "string",
        "state": "string",
        "country": "string",
        "zipcode": "string",
        "signup_date": "date",
        "is_active": "boolean",
        "customer_segment": "string",
    },
    "products": {
        "id": "number",
        "title": "string",
        "price": "number",
        "description": "string",
        "category": "string",
        "image": "string",
        "rating.rate": "number",
        "rating.count": "number",
    },
    "inventory": {
        "inventory_id": "string",
        "product_id": "string",
        "warehouse": "string",
        "current_stock": "number",
        "reorder_level": "number",
        "last_updated": "date",
        "warehouse_city": "string",
    },
    "orders": {
        "order_id": "string",
        "customer_id": "string",
        "order_date": "date",
        "product_id": "string",
        "quantity": "number",
        "unit_price": "number",
        "discount": "number",
        "tax": "number",
        "shipping_cost": "number",
        "payment_id": "string",
        "shipping_id": "string",
        "order_status": "string",
        "total_amount": "number",
    },
    "payments": {
        "payment_id": "string",
        "order_id": "string",
        "payment_method": "string",
        "payment_status": "string",
        "transaction_time": "timestamp",
        "amount": "number",
    },
    "shipping": {
        "shipping_id": "string",
        "order_id": "string",
        "carrier": "string",
        "tracking_number": "string",
        "dispatch_date": "date",
        "delivery_date": "date",
        "shipping_status": "string",
        "delivery_city": "string",
    },
    "reviews": {
        "review_id": "string",
        "customer_id": "string",
        "product_id": "string",
        "rating": "number",
        "review_title": "string",
        "review_text": "string",
        "review_date": "date",
        "verified_purchase": "boolean",
    },
}


class SchemaValidator:
    """Validate required columns, unexpected columns, and simple datatypes."""

    def validate(
        self, dataset_name: str, rows: list[dict[str, Any]]
    ) -> list[RuleResult]:
        """Run schema validation for a dataset."""
        expected_schema = EXPECTED_SCHEMAS.get(dataset_name, {})
        if not expected_schema:
            return []

        actual_columns = sorted({column for row in rows for column in row.keys()})
        expected_columns = set(expected_schema)
        actual_set = set(actual_columns)
        missing = sorted(expected_columns - actual_set)
        unexpected = sorted(actual_set - expected_columns)

        results = [
            RuleResult(
                "required_columns",
                not missing,
                "ERROR",
                len(rows) if missing else 0,
                (
                    f"Missing required columns: {', '.join(missing)}"
                    if missing
                    else "All required columns present"
                ),
                missing,
            ),
            RuleResult(
                "unexpected_columns",
                not unexpected,
                "WARNING",
                len(rows) if unexpected else 0,
                (
                    f"Unexpected columns: {', '.join(unexpected)}"
                    if unexpected
                    else "No unexpected columns"
                ),
                unexpected,
            ),
        ]

        for column, expected_type in expected_schema.items():
            if column not in actual_set:
                continue
            invalid_count = sum(
                1 for row in rows if not _matches_type(row.get(column), expected_type)
            )
            results.append(
                RuleResult(
                    f"datatype_{column}",
                    invalid_count == 0,
                    "ERROR",
                    invalid_count,
                    f"{column} has {invalid_count} values that are not {expected_type}",
                    [column],
                )
            )

        return results


def _matches_type(value: Any, expected_type: str) -> bool:
    """Return whether a value matches a simple expected type."""
    if is_blank(value):
        return True
    if expected_type == "number":
        return to_float(value) is not None
    if expected_type == "date":
        return parse_date(value) is not None
    if expected_type == "timestamp":
        return parse_date(value) is not None
    if expected_type == "boolean":
        return str(value).lower() in {"true", "false", "0", "1"}
    return isinstance(value, str) or value is not None
