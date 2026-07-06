# Retail Intelligence Platform

Retail Intelligence Platform is a portfolio-grade data engineering project that models the backend analytics infrastructure of a modern retail and e-commerce organization.

This repository is not an e-commerce website. It is the foundation for a backend data platform responsible for collecting, validating, cleaning, transforming, storing, and analyzing retail data from multiple independent sources.

## Motivation

Modern retail companies depend on reliable data platforms to understand sales, customer behavior, inventory movement, product performance, and operational health. This project is designed to demonstrate how a production-oriented data engineering system can be planned, structured, and expanded over time using clear module boundaries and maintainable engineering practices.

## Objectives

- Build an extensible Python-based data engineering platform.
- Separate extraction, validation, transformation, loading, warehousing, analytics, dashboarding, orchestration, and AI concerns.
- Model future analytical data in a PostgreSQL warehouse using dimensional modeling.
- Support future pipeline orchestration through Airflow.
- Support future distributed processing through PySpark.
- Support future analytics and assistant workflows without coupling them to core pipeline code.
- Maintain a repository structure that is readable, testable, and suitable for multiple engineers.

## Architecture

```text
Data Sources
    |
    v
Extraction
    |
    v
Raw Storage
    |
    v
Validation
    |
    v
Transformation
    |
    v
PostgreSQL Warehouse
    |
    v
Business Analytics
    |
    v
Dashboard
    |
    v
AI Assistant
```

Every layer is intentionally isolated so future development can evolve without turning the repository into a single monolithic script.

## Folder Structure

```text
.
|-- ai/                    # Planned AI assistant components
|-- airflow/               # Planned Airflow DAGs and orchestration assets
|-- config/                # Environment settings, constants, and logging config
|-- dashboard/             # Planned dashboard application
|-- data/
|   |-- exports/           # Planned generated exports
|   |-- processed/         # Planned curated local data outputs
|   |-- raw/               # Planned immutable raw data files
|   `-- source/            # Planned source input files
|-- data_generator/        # Synthetic source data generation framework
|-- docs/                  # Architecture, scope, and roadmap documentation
|-- extract/               # Planned source extraction layer
|-- load/                  # Planned warehouse loading layer
|-- logs/                  # Local runtime logs
|-- scripts/               # Project setup and maintenance scripts
|-- spark/                 # Planned PySpark jobs
|-- sql/                   # Planned SQL migrations, models, and queries
|-- tests/                 # Unit and integration tests
|-- transform/             # Planned cleaning and transformation layer
|-- validate/              # Planned data quality and validation layer
`-- warehouse/             # Planned warehouse abstractions and data models
```

## Technology Stack

- Python: core pipeline language.
- SQL: analytical querying and warehouse modeling.
- PostgreSQL: planned data warehouse.
- Pandas and NumPy: planned local data processing.
- SQLAlchemy and psycopg2: planned database access.
- Pytest: testing framework.
- Docker Compose: planned local infrastructure.
- Airflow: planned workflow orchestration.
- PySpark: planned distributed transformation jobs.
- Streamlit and Plotly: planned dashboard layer.
- LangChain and OpenAI: planned natural-language analytics assistant.

## Current Development Status

Phase 1 is complete.

Implemented so far:

- Project directory structure.
- Project metadata.
- Documentation foundation.
- Environment-driven settings module.
- Reusable logging configuration.
- Constants module.
- Placeholder pipeline entry point.
- Placeholder Docker Compose and Makefile targets.
- Configurable synthetic retail data generation.
- Source datasets for customers, products, inventory, orders, payments, reviews, and shipping.
- Controlled data quality issue injection for later validation phases.
- Reusable ingestion layer for CSV, JSON, NDJSON, and API sources.
- Pipeline run identifiers across logs, dataset metadata, and ingestion manifests.
- Raw dataset persistence, checksums, and failure-tolerant ingestion.
- Data validation and profiling framework for raw datasets.
- Validation summary, CSV report, HTML report, dataset reports, and dashboard-ready quality JSON.

Not implemented yet:

- ETL processing.
- SQL models.
- PostgreSQL services.
- Airflow DAGs.
- Spark jobs.
- Dashboard views.
- AI functionality.

## Project Phases

- Phase 0: Completed planning and scaffolding.
- Phase 1: Completed synthetic data generation.
- Phase 2: Completed extraction layer.
- Phase 3: Completed validation layer.
- Phase 4: Planned transformation layer.
- Phase 5: Planned warehouse loading.
- Phase 6: Planned dimensional data modeling.
- Phase 7: Planned Airflow orchestration.
- Phase 8: Planned PySpark integration.
- Phase 9: Planned dashboard.
- Phase 10: Planned AI assistant.
- Phase 11: Planned production polish.

## Future Roadmap

Planned capabilities include:

- Synthetic retail source data generation.
- Batch ingestion from independent source systems.
- Schema and data quality validation.
- Data cleaning and conformance.
- Star schema warehouse design.
- Fact and dimension table loading.
- Airflow DAGs for repeatable orchestration.
- PySpark jobs for larger transformation workloads.
- Business dashboards for sales and customer analytics.
- AI-assisted SQL generation and pipeline failure explanation.
- CI checks, quality gates, and production-style documentation.

## How to Run (Docker Containerized - Phase 8)

The entire Retail Intelligence Platform is now fully containerized! You can spin up the complete orchestration environment, including PostgreSQL and Apache Airflow, with a single command.

### 1. Start the Infrastructure
Use the provided Makefile shortcuts or Docker Compose directly:

```bash
make docker-up
# or: docker compose up -d
```

This starts:
- **`postgres`**: The Retail Intelligence data warehouse and Airflow metadata database (Port 5432).
- **`airflow-webserver`**: The Airflow UI (Port 8080).
- **`airflow-scheduler`**: The Airflow task execution scheduler.

### 2. Initialize Airflow (First Run Only)
If this is your first time bringing the containers up, you must initialize the Airflow database and create an admin user:

```bash
make airflow-init
# or: docker compose run --rm airflow-init
```

### 3. Accessing the System
- **Airflow UI**: Navigate to [http://localhost:8080](http://localhost:8080) and log in with `admin` / `admin`. You can manually trigger the `retail_intelligence_pipeline` DAG here.
- **PostgreSQL**: Connect to `localhost:5432` using `postgres` / `postgres`. The database name is `RetailIntelligencePlatform`.
- **Logs**: Run `make logs` to watch live logs from all containers.

### 4. How Data Flows Inside Containers
1. The project source code (`./`) is bind-mounted directly into the Airflow containers at `/opt/airflow/projects`. This means any code edits you make locally are instantly reflected in Airflow without rebuilding images.
2. When the DAG executes, Airflow simply calls our Python modules (`extract.manager`, `transform.manager`, etc.).
3. These modules connect to the `postgres` container over the `retail_network` using credentials supplied via the `.env` file to extract, transform, and load the analytical Star Schema.

### 5. Tearing Down
To stop the services and completely wipe the database (useful for testing a clean slate):
```bash
make docker-reset
```

## Design Philosophy

This project favors explicit boundaries, small modules, environment-based configuration, and clear ownership of each data platform layer. Each directory represents a future engineering responsibility rather than a place to collect unrelated scripts.

Validation is separated from transformation because data quality rules answer a different question than business transformation logic. Warehouse concerns are isolated so storage models can evolve independently from ingestion and cleaning logic.

## Coding Conventions

- Follow PEP 8.
- Keep modules focused and named by responsibility.
- Use type hints for public functions.
- Prefer environment variables over hardcoded runtime values.
- Keep TODO comments specific and phase-oriented.
- Add tests with each implemented feature in later phases.

## Planned Future ETL

The ETL pipeline will eventually extract retail data from multiple source formats, preserve raw inputs, validate records, transform data into analytical structures, and load a PostgreSQL warehouse.

Status: Planned.

## Planned Airflow Integration

Airflow will eventually orchestrate pipeline stages, retries, scheduling, alerting, and dependency management.

Status: Planned.

## Planned Spark Integration

PySpark will eventually support scalable processing for larger transaction, customer, and product datasets.

Status: Planned.

## Planned Dashboard

The dashboard will eventually expose retail metrics such as revenue trends, top products, customer retention, order growth, and sales by city.

Status: Planned.

## Planned AI Integration

The AI assistant will eventually answer natural-language questions by generating SQL, explaining query results, and helping diagnose pipeline failures.

Status: Planned.

## Contribution Guidelines

- Keep changes scoped to the active project phase.
- Do not introduce runtime services before their planned phase.
- Document architecture decisions when adding new layers.
- Add tests for new behavior.
- Keep configuration portable and environment-driven.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
