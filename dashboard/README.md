# Streamlit Analytics Dashboard

This directory contains the Streamlit-based web application that acts as the front-end Business Intelligence and observability layer for the Retail Intelligence Platform.

## Overview

The dashboard connects to our PostgreSQL database (`analytics` schema, `warehouse` schema, and `airflow` metadata schema) to provide business KPIs and pipeline monitoring in a single unified view.

It is strictly a **data consumption layer**. No heavy transformations or ETL logic occur here.

## Pages
1. **Overview**: High-level business KPIs.
2. **Sales Analysis**: Deep dive into revenue and category performance.
3. **Customer Insights**: Segmentation and Customer Lifetime Value (CLV).
4. **Product Performance**: Inventory and top sellers.
5. **Operations Monitoring**: Supply chain and warehouse status.
6. **Pipeline Health**: Airflow orchestration observability, showing DAG and Task execution success rates.
7. **Spark Analytics**: Visualization of heavy Spark workloads (like sessionization and event funnels).

## How to Run

If you are running this locally (outside of docker), ensure your virtual environment is active and your `.env` file is properly configured with your PostgreSQL credentials.

```bash
streamlit run dashboard/app.py
```

## Performance Considerations
- The app utilizes `@st.cache_resource` for database engine creation.
- Large datasets should be pre-aggregated in the backend (via SQL views, DBT, or Spark). The dashboard should never pull millions of rows into memory to plot them; it should push the `GROUP BY` logic down to the database using the `services/` layer.
- Ensure the database server has adequate resources to handle analytical queries.
