# Retail Intelligence Platform

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Airflow](https://img.shields.io/badge/Airflow-2.7+-017CEE?logo=Apache%20Airflow)
![Spark](https://img.shields.io/badge/Spark-PySpark-E25A1C?logo=Apache%20Spark)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?logo=streamlit)
![Groq](https://img.shields.io/badge/AI-Groq%20LLM-F55036)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

Retail Intelligence Platform is a portfolio-grade data engineering project that models the backend analytics infrastructure of a modern retail and e-commerce organization.

## Overview
This repository is the foundation for a robust backend data platform responsible for collecting, validating, cleaning, transforming, storing, and analyzing retail data.
It demonstrates how a production-oriented data engineering system can be structured using clear module boundaries and maintainable engineering practices.

## Features
- **End-to-End Orchestration**: Managed by Apache Airflow.
- **Star Schema Design**: Fully functional PostgreSQL warehouse modeling Facts and Dimensions.
- **Big Data Processing**: Apache Spark jobs for heavy aggregations and sessionization.
- **Business Intelligence**: A multi-page Streamlit dashboard for real-time KPIs and system monitoring.
- **AI Data Analyst**: Natural Language to SQL agent powered by Groq LLMs.
- **Containerized**: Deployed effortlessly via Docker and Docker Compose.

## Documentation Index
Comprehensive documentation of the architecture and modules can be found in the `docs/` directory:
- [System Architecture](docs/architecture.md)
- [ETL Data Flow](docs/data_flow.md)
- [Database Schema (Star Schema)](docs/database_schema.md)
- [Airflow Orchestration](docs/airflow.md)
- [Spark Distributed Processing](docs/spark.md)
- [Streamlit Dashboard](docs/dashboard.md)
- [AI Assistant & Agent](docs/ai_assistant.md)
- [Deployment Architecture](docs/deployment.md)
- [Developer Guide](docs/developer_guide.md)

## Architecture

Every layer is intentionally isolated so future development can evolve without turning the repository into a single monolithic script.

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
Dashboard (Streamlit)
    |
    v
AI Assistant (Groq LLM)
```

## Manual Configuration Checklist

1. **Environment Variables**: Copy `.env.example` to `.env`.
2. **Groq API Key**: You must provide `GROQ_API_KEY` in the `.env` file to enable the AI Analyst. Get one at [console.groq.com](https://console.groq.com).
3. **Dependencies**: 
   ```bash
   pip install -r requirements.txt
   ```
4. **Database**: The standard connection strings in `.env.example` will work with the provided Docker setup.

## How to Run (Docker Containerized)

The entire Retail Intelligence Platform is fully containerized! 

### 1. Start the Infrastructure
```bash
make docker-up
```
This starts:
- **`postgres`**: The Retail Intelligence data warehouse (Port 5432).
- **`airflow-webserver`**: The Airflow UI (Port 8080).
- **`airflow-scheduler`**: The Airflow task execution scheduler.

### 2. Initialize Airflow (First Run Only)
```bash
make airflow-init
```

### 3. Accessing the System
- **Airflow UI**: [http://localhost:8080](http://localhost:8080) (`admin` / `admin`). Trigger the `retail_intelligence_pipeline` DAG.
- **Streamlit Dashboard**: Run locally `streamlit run dashboard/app.py` or check docker mappings.
- **PostgreSQL**: Connect to `localhost:5432` using `postgres` / `postgres`.

### 4. Tearing Down
To stop the services and completely wipe the database:
```bash
make docker-reset
```

## Design Philosophy

This project favors explicit boundaries, small modules, environment-based configuration, and clear ownership of each data platform layer. Validation is separated from transformation because data quality rules answer a different question than business transformation logic. Warehouse concerns are isolated so storage models can evolve independently from ingestion and cleaning logic.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
