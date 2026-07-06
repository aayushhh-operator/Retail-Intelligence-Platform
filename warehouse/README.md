# Warehouse Loader

This directory contains the Phase 5 PostgreSQL Data Warehouse Loading Framework.

## Architecture
- **Schemas**: `staging`, `warehouse`, `metadata`
- **Tables**: `customers`, `products`, `orders`, `payments`, `shipping`, `inventory`, `reviews`, `website_events`
- **Transactions**: Each dataset is loaded in a separate transaction. Failures are rolled back without affecting other datasets.
- **Load Strategy**: Configurable, defaults to Replace (Truncate & Load).

## Manual Configuration Required

1. **Environment Variables**: You must add the following variables to `.env`:
   ```
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   DATABASE_NAME=RetailIntelligencePlatform
   DATABASE_USER=postgres
   DATABASE_PASSWORD=postgres
   ```
2. **Configuration Files**: No configuration files require manual editing beyond `.env`.
3. **Values**: Make sure `.env` points to your running PostgreSQL instance.
4. **PostgreSQL Extensions**: No special extensions required.
5. **Python Packages**: If `requirements.txt` has changed (e.g. adding `psycopg2-binary`, `SQLAlchemy`, `pandas`), ensure you have run `pip install -r requirements.txt`.
6. **SQL Scripts**: You do not need to run any SQL manually. The loader creates schemas, tables, constraints, and indexes automatically.
7. **Initialization**: The PostgreSQL database `RetailIntelligencePlatform` MUST exist prior to running this. Ensure you created it manually using `CREATE DATABASE "RetailIntelligencePlatform" ...`.
8. **Execution**: Run the loader from the root directory using:
   ```bash
   python warehouse/warehouse_manager.py
   ```
9. **Expected Outputs**: 
   - Schemas created (if not exist).
   - Tables created (if not exist).
   - Data successfully loaded from `data/processed/` into PostgreSQL tables.
   - Output logs indicating successful load for all 8 datasets.
   - Metadata recorded in the `metadata.load_history` and `metadata.pipeline_runs` tables.
   - `warehouse_metadata.json` generated in `logs/metadata/`.
10. **Troubleshooting**: 
    - *Connection Refused*: Ensure PostgreSQL is running on the host and port specified in `.env`.
    - *Role Does Not Exist*: Ensure `DATABASE_USER` exists.
    - *Database Does Not Exist*: Ensure you manually created the `RetailIntelligencePlatform` database.
