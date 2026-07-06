# Roadmap

## Phase 0: Planning

Create the project foundation, documentation, configuration modules, logging setup, metadata files, and placeholder runtime entry points.

Deliverables:

- Repository structure.
- README and documentation.
- Environment variable template.
- Settings, constants, and logging modules.
- Placeholder pipeline entry point.

## Phase 1: Data Generation

Create realistic synthetic retail datasets for customers, products, orders, payments, inventory, reviews, and shipping.

Deliverables:

- Data generation scripts.
- Source data contracts.
- Seeded generation controls.
- Tests for dataset shape and reproducibility.
- Controlled data quality issues for later validation phases.

## Phase 2: Extraction

Build source ingestion logic that lands source-aligned data into raw storage.

Deliverables:

- Extractors for source files.
- Raw file naming conventions.
- Extraction logs and run metadata.
- Shared pipeline run identifiers.
- Dataset checksums.
- Ingestion manifest.

## Phase 3: Validation

Add data quality checks before transformation.

Deliverables:

- Schema validation.
- Null, duplicate, range, and referential checks.
- Validation reports.
- Failure handling conventions.
- Data quality dashboard JSON.
- Pipeline proceed/stop recommendation.

## Phase 4: Transformation

Clean, standardize, and conform validated data.

Deliverables:

- Transformation modules.
- Standardized data types and naming.
- Processed datasets.
- Unit tests for transformation behavior.

## Phase 5: Warehouse

Introduce PostgreSQL as the analytical warehouse.

Deliverables:

- Docker Compose PostgreSQL service.
- Database connection configuration.
- Loading routines.
- Warehouse setup scripts.

## Phase 6: Data Modeling

Design dimensional models for analytics.

Deliverables:

- Dimension tables.
- Fact tables.
- Star schema documentation.
- SQL DDL and model tests.

## Phase 7: Airflow

Orchestrate the pipeline with Airflow.

Deliverables:

- DAG definitions.
- Task dependencies.
- Retry and alerting strategy.
- Local Airflow runtime configuration.

## Phase 8: PySpark

Add scalable processing paths for larger data volumes.

Deliverables:

- Spark session configuration.
- PySpark transformation jobs.
- Local Spark execution documentation.
- Tests for Spark transformations.

## Phase 9: Dashboard

Build a business analytics dashboard.

Deliverables:

- Dashboard application.
- Revenue, product, customer, and geography views.
- Warehouse-backed queries.
- Visualization documentation.

## Phase 10: AI Assistant

Add natural-language analytics and pipeline diagnostics.

Deliverables:

- SQL generation workflow.
- Query explanation workflow.
- Pipeline failure explanation workflow.
- Prompt and safety documentation.

## Phase 11: Production Polish

Harden the repository for maintainability and presentation.

Deliverables:

- CI workflow.
- Linting and formatting.
- Expanded tests.
- Operational runbooks.
- Final documentation review.
