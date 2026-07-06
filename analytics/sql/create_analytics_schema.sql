-- Create the analytics schema
CREATE SCHEMA IF NOT EXISTS analytics;

-- Create metadata tables for the analytics pipeline
CREATE TABLE IF NOT EXISTS analytics.pipeline_runs (
    run_id VARCHAR(100) PRIMARY KEY,
    status VARCHAR(50),
    execution_start TIMESTAMP,
    execution_end TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics.model_refresh_log (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(100),
    table_name VARCHAR(100),
    row_count INTEGER,
    status VARCHAR(50),
    refresh_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES analytics.pipeline_runs(run_id) ON DELETE CASCADE
);
