# Synthetic Data Generator

The `data_generator` package creates realistic Phase 1 source data for the Retail Intelligence Platform.

This package simulates operational datasets produced by a mid-sized e-commerce company. The generated files are written to `data/source/`, which represents upstream systems. Later phases will extract from this location into raw storage.

## How To Run

From the project root:

```bash
python data_generator/generate_all.py
```

The command generates:

- `customers.csv`
- `products.csv`
- `inventory.csv`
- `orders.csv`
- `payments.csv`
- `reviews.csv`
- `shipping.csv`

## Configuration

Dataset sizes, date ranges, seed values, output location, categories, price ranges, warehouse locations, and the data quality issue rate are configured in `data_generator/config.py`.

Changing values such as `NUMBER_OF_ORDERS`, `START_DATE`, `END_DATE`, or `RANDOM_SEED` changes future generated outputs. The same seed and configuration produce deterministic datasets.

## Business Assumptions

- The company sells Electronics, Fashion, Books, Home, Sports, Beauty, Toys, Kitchen, Office, and Groceries.
- Electronics and Home products have higher price ranges than Books and Groceries.
- Customers can place multiple orders.
- Popular products appear more frequently in orders.
- Orders reference customers and products.
- Payments and shipping records reference orders.
- Reviews are generated only from delivered orders.
- Inventory stock is lower for more popular products.

## Injected Data Quality Issues

The generator intentionally injects a small percentage of controlled defects for later validation and cleaning phases.

Examples include:

- Missing or invalid customer emails.
- Missing phone numbers.
- Missing customer IDs.
- Invalid zip codes.
- Negative or outlier product prices.
- Invalid product ratings.
- Future order dates.
- Duplicate order IDs.
- Negative order quantities.
- Missing product IDs.
- Invalid review ratings.

These issues are controlled by `DATA_QUALITY_ISSUE_RATE`.

## Design Notes

Each dataset has its own generator module. Shared ID formatting, date generation, CSV writing, deterministic seeding, and defect injection helpers live in `utils.py`.

No extraction, validation, transformation, database loading, dashboard, Airflow, Spark, or AI functionality is implemented in this phase.
