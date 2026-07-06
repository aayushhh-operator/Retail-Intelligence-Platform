# Data Validation Framework

The `validate` package implements Phase 3 of the Retail Intelligence Platform.

It reads raw datasets from `data/raw/`, profiles them, validates schemas, runs generic and business-specific data quality rules, calculates quality scores, and writes reports under `logs/validation/`.

This phase never cleans, transforms, rewrites, or loads data. It only measures data quality and recommends whether downstream processing should proceed.

## Architecture

- `base_validator.py`: common OOP validator workflow.
- `csv_validator.py`: raw CSV validation.
- `json_validator.py`: raw JSON and NDJSON validation.
- `schema_validator.py`: required columns, unexpected columns, and datatype checks.
- `business_rule_validator.py`: generic and dataset-specific rules.
- `statistics.py`: profiling metrics.
- `profiler.py`: profiling wrapper.
- `report_generator.py`: JSON, CSV, HTML, and dashboard report generation.
- `validation_registry.py`: dataset and validator registration.
- `validation_manager.py`: orchestration entry point.

## How To Run

```bash
python validate/validation_manager.py
```

The manager validates every configured raw dataset and writes:

- `logs/validation/validation_summary.json`
- `logs/validation/validation_report.csv`
- `logs/validation/validation_report.html`
- `logs/validation/data_quality_dashboard.json`
- `logs/validation/dataset_reports/*.json`

## Quality Scoring

Each failed rule contributes impact based on affected rows.

- Error severity counts as full impact.
- Warning severity counts as half impact.
- The final score is capped between 0 and 100.

Statuses:

- `PASS`: quality score greater than 95.
- `WARNING`: quality score from 90 through 95.
- `FAIL`: quality score below 90.

## Data Quality Dashboard JSON

`data_quality_dashboard.json` is designed for Phase 9 dashboard consumption. It contains the pipeline run ID, overall quality, and per-dataset quality scores so future dashboards can visualize quality trends without re-running validations.

## Rule Categories

Generic rules include missing values, duplicate rows, schema checks, datatype checks, and blank values.

Business rules include:

- customer email, phone, ZIP, uniqueness, and signup date checks
- product category, price, and rating checks
- order customer/product references, quantities, amounts, and dates
- payment order references, methods, amounts, and dates
- shipping carrier and date sequence checks
- review rating and verified purchase checks
- inventory stock and warehouse checks

## Adding Custom Rules

Add reusable rule functions to `business_rule_validator.py`, then call them from the dataset-specific validation method. Add schema changes in `schema_validator.py` and register new datasets in `validation_registry.py`.

