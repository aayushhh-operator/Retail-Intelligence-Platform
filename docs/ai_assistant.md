# AI Data Analyst Agent

This document outlines the architecture and workflow of the natural language analytics assistant integrated into the dashboard.

## Agent Architecture and Workflow

The AI agent dynamically reads PostgreSQL schemas, formulates valid read-only SQL, executes it, and generates visualizations and natural language insights.

```mermaid
sequenceDiagram
    participant User as User (Streamlit)
    participant AI as AI Agent
    participant Loader as Schema Loader
    participant Groq as Groq LLM
    participant Validator as SQL Validator
    participant DB as PostgreSQL DB
    participant Gen as Chart & Insight Gen

    User->>AI: Natural Language Query
    AI->>Loader: Fetch Live Table Schemas
    Loader-->>AI: Database Schema Context
    AI->>Groq: Prompt (Query + Schema)
    Groq-->>AI: Generated SQL Query
    AI->>Validator: Validate SQL (No DML)
    alt Invalid SQL
        Validator-->>AI: Reject (Unsafe)
        AI-->>User: Error Message
    else Valid SQL
        Validator-->>AI: Approved
        AI->>DB: Execute SQL
        DB-->>AI: Query Results
        AI->>Gen: Generate Chart & Insight
        Gen-->>AI: Markdown & Plotly
        AI-->>User: Display Insights & Chart
    end
```

## Security & Features
- **Strict Security Layer**: A Regex-based validator blocks any `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, or semicolon-chained statements. 
- **Dynamic Context**: Automatically scans `information_schema` so prompt building incorporates the live table definitions without hardcoding.
- **Fast Inference**: Utilizes the Groq LLM inference engine.
