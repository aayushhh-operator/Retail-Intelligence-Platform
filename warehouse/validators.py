"""Validators for ensuring data matches expectations before loading."""

import pandas as pd
from typing import List, Dict
from warehouse.exceptions import SchemaValidationError

# Expected schemas mapping dataset names to expected columns
EXPECTED_SCHEMAS: Dict[str, List[str]] = {
    "customers": ["customer_id", "first_name", "last_name", "full_name", "email", "phone", "gender", "date_of_birth", "city", "state", "country", "zipcode", "signup_date", "is_active", "customer_segment", "customer_age", "customer_tenure_days"],
    "products": ["product_id", "product_name", "category", "brand", "supplier", "cost_price", "selling_price", "profit_margin", "weight", "rating", "launch_date", "is_active", "sku", "low_margin_flag", "profit"],
    "inventory": ["inventory_id", "product_id", "warehouse", "current_stock", "reorder_level", "last_updated", "warehouse_city", "inventory_status"],
    "orders": ["order_id", "customer_id", "order_date", "product_id", "quantity", "unit_price", "discount", "tax", "shipping_cost", "payment_id", "shipping_id", "order_status", "total_amount", "order_year", "order_month", "order_quarter", "discount_percentage", "order_value", "items_count"],
    "payments": ["payment_id", "order_id", "payment_method", "payment_status", "transaction_time", "amount"],
    "reviews": ["review_id", "customer_id", "product_id", "rating", "review_title", "review_text", "review_date", "verified_purchase", "review_sentiment"],
    "shipping": ["shipping_id", "order_id", "carrier", "tracking_number", "dispatch_date", "delivery_date", "shipping_status", "delivery_city"],
    "website_events": ["event_id", "customer_id", "event_type", "event_timestamp", "page_url"]
}

class DatasetValidator:
    """Validates the schema of processed datasets before load."""
    
    @staticmethod
    def validate_schema(dataset_name: str, df: pd.DataFrame) -> None:
        """Verify the dataframe has all expected columns for a dataset."""
        if dataset_name not in EXPECTED_SCHEMAS:
            return  # Allow loading unknown datasets implicitly if not strictly defined
        
        expected_columns = EXPECTED_SCHEMAS[dataset_name]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            raise SchemaValidationError(f"Dataset '{dataset_name}' is missing columns: {missing_columns}")
