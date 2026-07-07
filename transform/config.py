"""Configuration for Phase 4 transformations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DeduplicationConfig:
    """Duplicate handling configuration."""

    keep: str = "first"


@dataclass(frozen=True)
class BusinessRuleConfig:
    """Configurable business rule behavior."""

    drop_invalid_rows: bool = True
    repair_emails: bool = True
    inventory_negative_stock_strategy: str = "zero"
    review_rating_strategy: str = "clamp"
    product_low_margin_strategy: str = "flag"
    shipping_date_strategy: str = "repair"
    enforce_foreign_keys: bool = False


@dataclass(frozen=True)
class ImputationConfig:
    """Column-level imputation strategy configuration."""

    strategies: dict[str, dict[str, str]] = field(
        default_factory=lambda: {
            "customers": {"phone": "constant:UNKNOWN", "email": "drop"},
            "orders": {"discount": "constant:0", "shipping_cost": "constant:0"},
            "payments": {"payment_status": "mode"},
            "inventory": {"current_stock": "constant:0"},
            "reviews": {"review_text": "constant:"},
        }
    )


@dataclass(frozen=True)
class TransformationConfig:
    """Top-level transformation configuration."""

    deduplication: DeduplicationConfig = DeduplicationConfig()
    business_rules: BusinessRuleConfig = BusinessRuleConfig()
    imputation: ImputationConfig = ImputationConfig()


TRANSFORMATION_CONFIG = TransformationConfig()
