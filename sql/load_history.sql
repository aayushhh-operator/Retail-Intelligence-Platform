-- Create Metadata Tables
CREATE TABLE IF NOT EXISTS metadata.pipeline_runs (
    pipeline_run_id VARCHAR(100) PRIMARY KEY,
    status VARCHAR(50),
    execution_start TIMESTAMP,
    execution_end TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metadata.load_history (
    id SERIAL PRIMARY KEY,
    pipeline_run_id VARCHAR(100),
    dataset VARCHAR(100),
    rows_read INTEGER,
    rows_loaded INTEGER,
    rows_failed INTEGER,
    load_strategy VARCHAR(50),
    status VARCHAR(50),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pipeline_run_id) REFERENCES metadata.pipeline_runs(pipeline_run_id) ON DELETE CASCADE
);
