# PySpark Distributed Processing Layer

This directory contains the Apache Spark (PySpark) implementation for the Retail Intelligence Platform. 

## Why Spark?
While standard Python (Pandas) and PostgreSQL (SQL) are excellent for many transformations and analytical queries, they can bottleneck when processing massive, high-volume datasets (like raw behavioral `website_events`) or executing complex window functions over unbounded histories. 

Spark is introduced here as an **optional acceleration layer** to compute heavy analytical workloads efficiently via distributed in-memory computing.

## When to use Spark vs Pandas/SQL
- **Use Spark**: High-volume clickstream data (`website_events`), sessionization logic, heavy multi-table joins, batch machine learning feature preparation.
- **Use Pandas**: Small dimension tables, configuration extraction, data profiling.
- **Use SQL**: In-database aggregations where the data already lives safely in a Star Schema and doesn't require complex sequential window logic.

## Architecture

```text
PostgreSQL Warehouse (JDBC)  --|
                               |--> Spark Job --> PostgreSQL Analytics Schema
Local Data Lake (Parquet)    --|
```

Every job inherits from `BaseSparkJob` which enforces a clean `load -> transform -> write` lifecycle. Transformations are strictly isolated in the `transforms/` directory to enable unit testing.

## Jobs Implemented
1. **Customer Analytics Job**: Computes CLV and purchase frequency.
2. **Sessionization Job**: Uses Spark window functions and time-gap logic to convert a flat stream of website events into unique user sessions.
3. **Order / Product / Revenue / Event Jobs**: (See `jobs/` directory for specifics).

## Airflow Integration
Spark jobs are cleanly integrated with our Airflow DAGs. Airflow serves as the orchestrator triggering `spark.jobs.job_name.main()`, but no Spark business logic leaks into the Airflow DAGs themselves.

## How to Run
You can run any Spark job directly to test its execution:
```bash
python spark/jobs/sessionization_job.py
```
*(Ensure you have Java installed, as PySpark relies on the JVM).*
