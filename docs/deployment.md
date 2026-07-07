# Deployment & Infrastructure

This document outlines the deployment architecture using Docker and Docker Compose.

## Container Architecture

```mermaid
graph TD
    subgraph Docker Network [Retail-Intelligence-Platform Docker Network]
        direction TB
        Airflow[Airflow Orchestrator Container]
        SparkWorker[Spark Worker Container]
        DB[(PostgreSQL Database Container)]
        Streamlit[Streamlit Dashboard Container]
    end
    
    Airflow -->|ETL Execution| DB
    Airflow -.->|Trigger| SparkWorker
    SparkWorker -->|Aggregations| DB
    Streamlit -->|Queries| DB
    User[End User] -->|Web UI| Streamlit
    User -->|Airflow Web UI| Airflow
```

## Setup Instructions

1. **Prerequisites**: Ensure Docker and Docker Compose are installed.
2. **Environment File**: Configure your `.env` file from the provided `.env.example`. Make sure your `GROQ_API_KEY` is present.
3. **Build and Run**:
   ```bash
   docker-compose up --build -d
   ```
4. **Accessing Services**:
   - Streamlit Dashboard: `http://localhost:8501`
   - Airflow UI: `http://localhost:8080`
   - PostgreSQL: `localhost:5432`

## Persistence
Database data is mapped to a local volume to persist between restarts. Logs and raw data exports are also mapped to host volumes to ensure easy debugging.
