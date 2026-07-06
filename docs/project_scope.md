# Project Scope

## Problem Statement

Retail organizations need reliable analytical infrastructure to convert operational data into trusted business insights. Raw retail data often arrives from separate systems with inconsistent formats, missing values, duplicate records, and unclear ownership. This project will model the backend platform needed to turn those inputs into analytics-ready data.

## Business Scenario

The platform represents the internal data engineering system of a modern e-commerce company. It will eventually support analytical workflows across sales, customers, products, geography, orders, and pipeline operations.

The project is not a storefront or customer-facing application. It is a backend data platform for analytics, monitoring, and decision support.

## Expected Users

- Data engineers maintaining ingestion, validation, transformation, and loading jobs.
- Analytics engineers defining warehouse models and business metrics.
- Data analysts answering retail performance questions.
- Business stakeholders reviewing dashboards.
- Future AI assistant users asking natural-language questions about trusted warehouse data.

## Business Questions

The future platform is expected to answer questions such as:

- Which products are top sellers by revenue and units sold?
- How is revenue trending by day, week, month, and quarter?
- Which cities or regions generate the most sales?
- How quickly are orders growing over time?
- Which products have declining performance?
- What is customer retention by cohort?
- Which customers place repeat orders?
- Which payment methods are most common?
- Which pipeline runs failed and why?
- Which validation checks are most frequently violated?
- What SQL query can answer a business user's natural-language question?

## In Scope For Future Phases

- Source extraction.
- Raw data storage.
- Data validation and quality reporting.
- Data cleaning and transformation.
- PostgreSQL warehouse loading.
- Star schema modeling.
- Airflow orchestration.
- PySpark transformation jobs.
- Dashboard analytics.
- AI-assisted SQL and pipeline diagnostics.

## Completed In Phase 1

- Configurable synthetic retail data generation.
- Source CSV creation in `data/source/`.
- Realistic retail entities for customers, products, inventory, orders, payments, reviews, and shipping.
- Controlled data quality defects for future validation and cleaning work.

## Completed In Phase 2

- CSV, JSON, NDJSON, and API ingestion framework.
- Raw file persistence in `data/raw/`.
- Product ingestion from the Fake Store API.
- Dataset metadata files in `logs/metadata/`.
- SHA256 checksums for extracted datasets.
- Ingestion manifest at `logs/ingestion_manifest.json`.
- Shared `pipeline_run_id` in logs, metadata, and manifest output.
- Failure-tolerant extraction where one failed source does not stop the full ingestion run.

## Completed In Phase 3

- Raw dataset validation from `data/raw/`.
- Schema validation, generic quality rules, and business-specific rules.
- Dataset profiling statistics.
- Dataset quality scores and PASS/WARNING/FAIL statuses.
- Validation summary, CSV report, HTML report, and per-dataset JSON reports.
- Dashboard-ready data quality JSON for future observability views.
- Pipeline proceed/stop recommendation based on validation outcomes.

## Out Of Scope For Phase 0

- Implementing extraction logic.
- Generating datasets.
- Writing ETL logic.
- Creating SQL models.
- Running PostgreSQL.
- Building Airflow DAGs.
- Building Spark jobs.
- Creating dashboards.
- Implementing AI features.
- Writing business logic.

## Success Criteria

Phase 0 is successful when the repository clearly communicates the intended architecture, project scope, future milestones, and code organization without implementing later-phase functionality prematurely.
