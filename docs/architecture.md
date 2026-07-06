# Architecture

## High-Level Architecture

Retail Intelligence Platform is organized as a layered data platform. Each layer owns one responsibility and passes well-defined outputs to the next layer.

```text
Data Sources -> Extraction -> Raw Storage -> Validation -> Transformation
    -> PostgreSQL Warehouse -> Business Analytics -> Dashboard -> AI Assistant
```

Phase 0 only creates the project foundation. Runtime behavior will be implemented in later phases.

## Module Purposes

| Module | Purpose |
| --- | --- |
| `config/` | Centralizes environment settings, constants, and logging configuration. |
| `data_generator/` | Generates synthetic upstream retail datasets for Phase 1. |
| `data/source/` | Planned landing area for independent source files or generated source extracts. |
| `data/raw/` | Planned immutable raw data storage. |
| `data/processed/` | Planned curated intermediate data outputs. |
| `data/exports/` | Planned export location for reports or downstream files. |
| `extract/` | Source extraction logic for CSV, JSON, NDJSON, and API ingestion. |
| `validate/` | Planned schema checks, data quality rules, and validation reports. |
| `transform/` | Planned cleaning, standardization, enrichment, and conformance logic. |
| `load/` | Planned database loading routines. |
| `warehouse/` | Planned warehouse models, metadata, and storage abstractions. |
| `sql/` | Planned SQL migrations, DDL, analytical queries, and warehouse scripts. |
| `airflow/` | Planned DAGs and orchestration configuration. |
| `spark/` | Planned PySpark jobs for scalable transformations. |
| `dashboard/` | Planned business analytics dashboard application. |
| `ai/` | Planned assistant for natural-language analytics and pipeline diagnostics. |
| `tests/` | Unit and integration tests. |
| `docs/` | Architecture, scope, and roadmap documentation. |
| `scripts/` | Setup and maintenance utilities. |

## Future Data Flow

1. Source systems provide retail entities such as orders, customers, products, payments, inventory, and events.
2. The extraction layer lands source-aligned data in raw storage.
3. Validation checks schema, completeness, uniqueness, referential expectations, and accepted value ranges.
4. Transformation standardizes names, types, dates, currencies, and business definitions.
5. Loading routines persist curated outputs into PostgreSQL.
6. Warehouse models expose facts and dimensions for analytics.
7. Dashboard and AI layers consume the warehouse, not raw files.

## Layer Responsibilities

Extraction is responsible for acquiring data and preserving source intent. It should not enforce business transformations. Phase 2 persists raw copies, checksums, metadata, and an ingestion manifest.

Raw storage is responsible for retaining source-aligned records for auditability and replay.

Validation is responsible for deciding whether data is fit to move forward and for producing actionable quality reports. Phase 3 reads only from raw storage, profiles datasets, calculates quality scores, writes validation reports, and emits dashboard-ready data quality JSON.

Transformation is responsible for business-ready cleaning, enrichment, standardization, and preparation for warehouse loading.

Loading is responsible for durable persistence, idempotency, and database write patterns.

The warehouse layer is responsible for analytical structures, naming conventions, constraints, and serving stable business entities.

The dashboard layer is responsible for human-facing analytics and visualization.

The AI layer is responsible for natural-language interaction, SQL assistance, and future pipeline failure explanations.

## Component Communication

Early phases use local files and Python interfaces. Later phases will introduce PostgreSQL, Airflow orchestration, and Spark execution. Components should communicate through explicit contracts such as file locations, schemas, database tables, and configuration objects rather than hidden global state.

Every pipeline execution has a shared `pipeline_run_id` such as `RUN_20260706_143522`. Logs, ingestion metadata, and manifests include this identifier so future validation, transformation, warehouse, dashboard, and AI outputs can be traced back to the same execution.

## Modular Design Rationale

The project is intentionally modular because data platforms usually grow across teams and runtime environments. Clear module boundaries reduce coupling, simplify testing, and allow individual layers to be replaced or scaled without rewriting the full pipeline.

## Validation vs. Transformation

Validation and transformation are separated because they solve different problems. Validation determines whether data meets expectations. Transformation changes data into a business-ready shape. Keeping these concerns separate improves auditability, makes failures easier to diagnose, and prevents quality rules from being hidden inside transformation code.

## Warehouse Layer Rationale

The warehouse layer provides stable analytical structures for downstream consumers. It protects dashboards, reports, and AI workflows from changes in source data shape and pipeline internals.

## Dashboard Layer Rationale

The dashboard layer is separated from pipeline code so visualization concerns do not leak into ingestion or warehouse logic. It should consume trusted warehouse outputs.

## AI Layer Rationale

The AI layer is separated because natural-language analytics and failure explanation require different dependencies, prompts, permissions, and safety checks than deterministic data processing. It will be integrated only after the core data platform is reliable.
