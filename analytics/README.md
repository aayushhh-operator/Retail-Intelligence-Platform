# Analytics Layer (Star Schema)

This layer builds a dimensional modeling (Star Schema) data mart designed specifically for fast Business Intelligence querying, reporting, and KPI computations. It runs completely inside PostgreSQL as SQL transformations (ELT pattern), extracting data from the normalized `warehouse` schema into the new `analytics` schema.

## Architecture

**Source**: `warehouse` schema (Normalized)
**Target**: `analytics` schema (Dimensional Star Schema)
**Strategy**: TRUNCATE + RELOAD (Idempotent execution)

### Dimensions

- `dim_customer`: Customer details (SCD Type 1)
- `dim_product`: Product catalog attributes and price bands
- `dim_date`: Granular date attributes generated between the min and max dates found in `orders`
- `dim_time`: Fixed time dimension down to the minute
- `dim_geography`: Geographic regions mapped from customers and inventory
- `dim_payment_method`: Standardized payment methods and groupings
- `dim_shipping_carrier`: Extracted shipping carriers
- `dim_category`: Distinct product categories

### Fact Tables & Grain

The core measurable metrics are stored here. Each table has an explicit, strict grain definition:

1. **`fact_orders`**: One row per order line item. Metrics include `quantity`, `unit_price`, `discount`, `tax`, `shipping_cost`, `total_amount`.
2. **`fact_payments`**: One row per payment transaction. Metrics include `amount`.
3. **`fact_shipping`**: One row per shipment. Metrics include `delivery_duration` (days).
4. **`fact_customer_activity`**: One row per customer event/action on the website.

### Referential Integrity

In a synthetic environment, some dimensional data might be missing (e.g. a customer deleted during validation but remaining in raw events). To gracefully handle this and maintain star schema integrity, missing relationships default to a surrogate key of `-1` ("Unknown").

## How to Run

Execute the pipeline from the project root:

```bash
python analytics/analytics_manager.py
```

This will automatically drop (truncate) the existing data and rebuild the entire schema from scratch.

## Future Usage (Phase 9 - Dashboards)

These tables are structurally optimized for dashboards. Tools like Superset, Metabase, or Python-based Streamlit/Dash can connect to the `analytics` schema and run heavy aggregations (e.g., `SUM(total_amount) GROUP BY dim_geography.region`) at sub-second speeds.
