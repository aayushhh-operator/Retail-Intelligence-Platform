# Retail Intelligence Platform Architecture

This document outlines the overall architecture of the Retail Intelligence Platform.

## System Architecture

```mermaid
graph TD
    %% Data Sources
    subgraph Data Sources
        Generator[Python Data Generator]
    end

    %% Data Ingestion & Storage
    subgraph Data Layer
        DB[(PostgreSQL)]
        Lake[Local Data Lake Parquet]
    end

    %% Processing
    subgraph Processing Layer
        Airflow[Apache Airflow ETL Orchestration]
        Spark[Apache Spark / PySpark Distributed Processing]
    end

    %% Serving
    subgraph Serving Layer
        Streamlit[Streamlit Analytics Dashboard]
        AI[AI Data Analyst Agent Groq LLM]
    end

    %% Connections
    Generator -->|Raw Data| DB
    Airflow -->|Orchestrates| DB
    Airflow -->|Triggers| Spark
    Spark -->|Reads/Writes| DB
    Spark -->|Reads/Writes| Lake
    Streamlit -->|Reads Analytics| DB
    AI -->|Reads Schema & Queries| DB
    AI -->|Visualizations| Streamlit
```

## Tech Stack Overview
- **Orchestration**: Apache Airflow
- **Data Warehouse**: PostgreSQL (Star Schema)
- **Big Data Processing**: Apache Spark (PySpark)
- **Business Intelligence**: Streamlit
- **AI Analytics**: Groq API + LangChain/Custom Python Agent
- **Deployment**: Docker, Docker Compose
