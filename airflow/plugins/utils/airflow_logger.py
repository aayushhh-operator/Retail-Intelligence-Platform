"""Airflow custom logging utilities for PostgreSQL metadata tracking."""

import logging
from datetime import datetime
from airflow.plugins.hooks.postgres_hook import MetadataPostgresHook

logger = logging.getLogger(__name__)

def log_dag_run_start(context):
    dag_id = context['dag'].dag_id
    run_id = context['run_id']
    execution_date = context['execution_date']
    
    query = """
        INSERT INTO airflow.dag_runs_log (run_id, dag_id, execution_date, status, duration)
        VALUES (%s, %s, %s, 'RUNNING', 0.0)
        ON CONFLICT (run_id) DO NOTHING;
    """
    try:
        MetadataPostgresHook.initialize_metadata_tables()
        MetadataPostgresHook.execute(query, (run_id, dag_id, execution_date))
    except Exception as e:
        logger.error(f"Failed to log dag start metadata: {e}")

def log_dag_run_success(context):
    run_id = context['run_id']
    query = """
        UPDATE airflow.dag_runs_log
        SET status = 'SUCCESS'
        WHERE run_id = %s;
    """
    try:
        MetadataPostgresHook.execute(query, (run_id,))
    except Exception as e:
        logger.error(f"Failed to log dag success metadata: {e}")

def log_dag_run_failure(context):
    run_id = context['run_id']
    error = str(context.get('exception', 'Unknown DAG Failure'))
    query = """
        UPDATE airflow.dag_runs_log
        SET status = 'FAILED', error_message = %s
        WHERE run_id = %s;
    """
    try:
        MetadataPostgresHook.execute(query, (error, run_id))
    except Exception as e:
        logger.error(f"Failed to log dag failure metadata: {e}")

def log_task_start(context):
    dag_id = context['dag'].dag_id
    task_id = context['task'].task_id
    run_id = context['run_id']
    execution_date = context['execution_date']
    
    query = """
        INSERT INTO airflow.task_runs_log (run_id, dag_id, task_id, execution_date, status, duration)
        VALUES (%s, %s, %s, %s, 'RUNNING', 0.0);
    """
    try:
        MetadataPostgresHook.initialize_metadata_tables()
        MetadataPostgresHook.execute(query, (run_id, dag_id, task_id, execution_date))
    except Exception as e:
        logger.error(f"Failed to log task start metadata: {e}")

def log_task_success(context):
    run_id = context['run_id']
    task_id = context['task'].task_id
    
    query = """
        UPDATE airflow.task_runs_log
        SET status = 'SUCCESS'
        WHERE run_id = %s AND task_id = %s AND status = 'RUNNING';
    """
    try:
        MetadataPostgresHook.execute(query, (run_id, task_id))
    except Exception as e:
        logger.error(f"Failed to log task success metadata: {e}")

def log_task_failure(context):
    run_id = context['run_id']
    task_id = context['task'].task_id
    error = str(context.get('exception', 'Unknown Task Failure'))
    
    query = """
        UPDATE airflow.task_runs_log
        SET status = 'FAILED', error_message = %s
        WHERE run_id = %s AND task_id = %s AND status = 'RUNNING';
    """
    try:
        MetadataPostgresHook.execute(query, (error, run_id, task_id))
    except Exception as e:
        logger.error(f"Failed to log task failure metadata: {e}")
