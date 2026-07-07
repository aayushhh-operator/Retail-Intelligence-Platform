# Developer Guide

Welcome to the Retail Intelligence Platform! This guide helps you set up the environment and contribute to the project.

## Local Setup (Without Docker)

1. **Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
2. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Database**: Start a local PostgreSQL server. Ensure credentials match your `.env`.
4. **Environment Variables**: Copy `.env.example` to `.env` and fill in necessary fields.

## Development Workflow
- **Adding Airflow DAGs**: Place new DAGs in `airflow/dags/`. Avoid heavy logic in DAG files; utilize `plugins/operators/` or external Python scripts.
- **Spark Jobs**: Place new Spark jobs in `spark/jobs/`. Keep transformations inside `spark/transforms/` isolated for unit testing.
- **Dashboard Pages**: Add new Streamlit pages in `dashboard/pages/`.
- **Database Schema**: Make structural changes via SQL scripts in `sql/`.

## Testing
Unit and integration tests are located in `tests/`. Run them using `pytest`.
```bash
pytest tests/
```

## Conventions
- Follow standard Python PEP8 formatting.
- Ensure all DAGs and Tasks include appropriate logging (see `airflow.plugins.utils.airflow_logger`).
- Never perform DML directly in the AI Assistant; always keep it read-only.
