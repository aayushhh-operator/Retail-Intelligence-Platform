# Airflow Orchestration Layer

This directory contains the Apache Airflow DAGs, custom operators, hooks, and configurations used to orchestrate the Retail Intelligence Platform data pipeline end-to-end.

In this architecture, Airflow acts purely as an orchestrator and scheduler. It does NOT contain business logic or ETL processing logic; it simply imports and executes the existing modules (`extract`, `validate`, `transform`, `warehouse`, `analytics`) in the correct dependency order.

===========================================================
MANUAL CONFIGURATION REQUIRED
===========================================================

To fully run the Airflow pipeline from scratch, follow these instructions precisely.

### 1. Required .env Variables
Ensure your `d:/Retail Intelligence Platform/.env` file contains the following configurations. Airflow will use these to connect to your PostgreSQL database.

```env
# Airflow Environment settings
AIRFLOW_HOME=d:/Retail Intelligence Platform/airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__DAGS_FOLDER=d:/Retail Intelligence Platform/airflow/dags

# Airflow Database Backend (Where Airflow stores its own metadata)
# Using SQLite for local testing or PostgreSQL for production. Example for Postgres:
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://postgres:postgres@localhost:5432/RetailIntelligencePlatform

# Retail Database (Where our data and custom metadata logs live)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=RetailIntelligencePlatform
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres

# Pipeline Specific Flags
ENABLE_DATA_GENERATION=False
```

### 2. Missing Python Dependencies
If you have not installed Airflow yet, you must install it into your environment. Because we use PostgreSQL hooks, you'll need the postgres provider.

```bash
pip install "apache-airflow[postgres]==2.8.1" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-3.10.txt"
```
*(Adjust the python constraint version matching your Python version. Note: Airflow currently supports Python up to 3.11/3.12).*

### 3. Database Setup Steps
No manual database setup is required for our custom `airflow.dag_runs_log` and `airflow.task_runs_log` tables! Our custom `MetadataPostgresHook` will automatically initialize them on the first run.

However, you must ensure the Airflow metastore database exists if you are pointing `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` to PostgreSQL.

### 4. Initialize Airflow Database
Once Airflow is installed, run the following command to initialize Airflow's internal metadata database:

```bash
airflow db init
```

### 5. Create an Airflow Admin User
To access the web interface, create an admin user:

```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### 6. Start Airflow Webserver + Scheduler
Open two separate terminal windows.

**Terminal 1 (Webserver):**
```bash
airflow webserver --port 8080
```

**Terminal 2 (Scheduler):**
```bash
airflow scheduler
```

### 7. Trigger the DAG Manually
1. Open a browser and navigate to `http://localhost:8080`
2. Log in with `admin` / `admin`
3. You will see `retail_intelligence_pipeline` in the DAGs list. (It may be paused, click the toggle switch to unpause it).
4. Click the "Play" (Trigger DAG) button on the right side.

### 8. Expected Logs and Outputs
- **Airflow UI**: You should see tasks turn Light Green (Running) and then Dark Green (Success). If a task fails, it turns Red and will retry automatically up to 3 times with a 1-minute delay.
- **Retail DB Logging**: Query `SELECT * FROM airflow.task_runs_log;` inside pgAdmin/psql. You will see structured execution metadata showing run durations and success/failure statuses.
- **Terminal**: The scheduler terminal will output our standard Python `logging` outputs because the operators simply trigger our existing modules.

### 9. Common Troubleshooting
- **DAG not showing up in UI**: Make sure `AIRFLOW_HOME` is set correctly in your terminal before running `airflow webserver`, or verify `AIRFLOW__CORE__DAGS_FOLDER` points to the correct directory.
- **ModuleNotFoundError for 'extract'**: Ensure the `PYTHONPATH` includes `d:/Retail Intelligence Platform`. Our DAGs dynamically inject `sys.path.insert(0, PROJECT_ROOT)`, but checking `PYTHONPATH` helps if you run scripts manually.
- **psycopg2 connection error**: Ensure your Postgres database is running and the `.env` credentials are correct.
