# Data Transformation Framework

The `transform` package implements Phase 4 of the Retail Intelligence Platform.

It reads validated raw datasets from `data/raw/`, consumes validation results from `logs/validation/` to guide decisions, applies a full transformation pipeline to each dataset, and writes analytics-ready outputs to `data/processed/`.

This phase **never modifies or overwrites** files in `data/raw/`.

---

## How To Run

```bash
python transform/transformation_manager.py
```

Or as part of the full pipeline:

```bash
python pipeline.py
```

The manager reads every configured raw dataset, transforms it, and writes:

- `data/processed/{dataset}.csv` — cleaned, standardized, enriched dataset
- `logs/transform/dataset_reports/{dataset}.json` — per-dataset transformation report
- `logs/transform/transformation_summary.json` — overall run summary

---

## Architecture

```
transformation_manager.py       CLI entry point and orchestration
         │
         ▼
TransformationPipelineRunner    Coordinates multiple pipelines
(pipeline.py)
         │
         ▼ (per dataset)
TransformationPipeline          Single-dataset execution wrapper
(pipeline.py)
         │
         ▼
BaseTransformer (ABC)           Shared transformation steps + run()
(base_transformer.py)
         │
         ▼
Concrete Transformer            Dataset-specific load() + transform()
(registry.py)
```

### Module Responsibilities

| Module | Purpose |
|---|---|
| `transformation_manager.py` | Entry point. Wires directories, creates the runner, writes the summary report. |
| `base_transformer.py` | Abstract base class. Implements all shared pipeline steps (clean, impute, dedup, standardize, business rules, enrich, schema map). |
| `registry.py` | `TransformerRegistry` maps dataset names to concrete transformer classes. All 7 built-in transformers live here. |
| `pipeline.py` | `TransformationPipeline` (single dataset) and `TransformationPipelineRunner` (multi-dataset coordinator). |
| `config.py` | Frozen dataclasses for `DeduplicationConfig`, `BusinessRuleConfig`, `ImputationConfig`, and `TransformationConfig`. |
| `cleaning.py` | `trim_whitespace`, `clean_email`, `blank_to_none` — generic, dataset-agnostic cleaners. |
| `normalization.py` | `normalize_phone`, `normalize_zipcode`, `normalize_country`, `normalize_category`. |
| `standardization.py` | `standard_date`, `boolean_value`, `money`, `integer`, `title_case`. |
| `enrichment.py` | Derived column logic: `customer_age`, `customer_tenure_days`, `order_year/month/quarter`, `inventory_status`, `review_sentiment`, `profit`. |
| `deduplication.py` | Exact-row deduplication and primary-key deduplication with configurable keep policy. |
| `imputation.py` | Column-level imputation: `constant`, `mode`, `mean`, `median`, `drop`, `none`. |
| `business_rules.py` | Dataset-specific rules: drop invalid rows, repair prices, clamp ratings, fix date order. |
| `schema_mapper.py` | `PROCESSED_SCHEMAS` defines final column order per dataset. `apply_schema` enforces it. |
| `metrics.py` | `TransformationMetrics` dataclass tracking rows through every transformation step. |
| `exporters.py` | Writes processed CSVs and JSON reports to the correct output paths. |
| `exceptions.py` | `TransformationError` for unrecoverable failures. |
| `utils.py` | Shared I/O and parsing utilities (read_csv, read_json, write_csv, write_json, parse_date, to_float, to_int). |

---

## Transformation Workflow

For each dataset the pipeline executes these steps in order:

1. **Load validation results** — reads `logs/validation/dataset_reports/{dataset}.json` to surface quality score and status; a FAIL status logs a warning but does not abort.
2. **Load raw data** — reads from `data/raw/` without modification.
3. **Clean** — trim whitespace, convert blank strings to `None`, repair common email typos.
4. **Impute** — fill missing values per column using configured strategies.
5. **Deduplicate** — remove exact-row duplicates, then primary-key duplicates.
6. **Standardize** — normalize dates to ISO 8601, booleans to `True`/`False`, money to 2 decimal floats.
7. **Apply business rules** — drop/repair/impute based on dataset-specific rules and `BusinessRuleConfig`.
8. **Enrich** — add derived analytics columns (`customer_age`, `order_quarter`, `review_sentiment`, etc.).
9. **Apply schema** — reorder columns per `PROCESSED_SCHEMAS` and drop unexpected fields.
10. **Export** — write the processed CSV and a JSON transformation report.

---

## Handling Invalid Rows

Invalid rows identified during validation are handled according to configurable strategy in `BusinessRuleConfig`:

| Scenario | Default Strategy |
|---|---|
| Missing customer ID / name | Drop row |
| Non-positive product price | Drop row |
| Product selling price < cost | Flag with `low_margin_flag=True` |
| Negative inventory stock | Repair to 0 |
| Review rating outside 1–5 | Clamp to nearest boundary |
| Payment amount ≤ 0 | Drop row |
| Delivery date before dispatch | Repair (delivery = dispatch + 1 day) |
| Missing order customer/product | Drop row |

All strategies are configurable via `BusinessRuleConfig` without changing source code.

---

## Configuration

All thresholds and strategies are defined in `config.py` as frozen dataclasses:

```python
from transform.config import TransformationConfig, BusinessRuleConfig, ImputationConfig

config = TransformationConfig(
    business_rules=BusinessRuleConfig(
        inventory_negative_stock_strategy="zero",   # or "drop"
        review_rating_strategy="clamp",             # or "drop"
        product_low_margin_strategy="flag",         # or "repair"
        shipping_date_strategy="repair",            # or "drop"
        drop_invalid_rows=True,
        repair_emails=True,
        enforce_foreign_keys=False,
    ),
    imputation=ImputationConfig(
        strategies={
            "orders": {"discount": "constant:0", "shipping_cost": "constant:0"},
            "customers": {"phone": "constant:UNKNOWN"},
        }
    ),
)
```

---

## Validation Result Integration

Each transformer reads `logs/validation/dataset_reports/{dataset}.json` before transforming. The validation quality score and status are recorded in `TransformationMetrics` and included in every dataset transformation report. This creates a traceable link between validation findings and transformation decisions.

If a dataset has `FAIL` status, the transformer logs a warning and continues with caution — it does not abort — because the caller (usually `pipeline.py`) controls the stop decision based on the overall quality policy.

---

## Adding a Custom Transformer

1. Subclass `BaseTransformer` and implement `load()` and `transform()`.
2. Register it in a `TransformerRegistry`:

```python
from transform.registry import build_default_registry
from transform.base_transformer import BaseTransformer

class MyDatasetTransformer(BaseTransformer):
    def load(self):
        ...  # read raw file
    def transform(self, rows):
        rows = self._clean(rows)
        rows = self._deduplicate(rows)
        rows = self._standardize(rows)
        rows = self._enrich(rows)
        return rows

registry = build_default_registry()
registry.register("my_dataset", MyDatasetTransformer)
```

3. Optionally add a schema entry to `schema_mapper.PROCESSED_SCHEMAS` for column ordering.

---

## Output Schema

Processed column orders are defined in `schema_mapper.PROCESSED_SCHEMAS`. Every processed dataset includes only the columns defined there, in that order, so downstream consumers have a stable contract.

---

## Failure Policy

- A single dataset failure never aborts the full run.
- `BaseTransformer.run()` catches all exceptions, marks the dataset `FAILED`, and continues.
- Skipped datasets (missing raw file) are recorded with `SKIPPED` status.
- All failures are logged and included in `transformation_summary.json`.
