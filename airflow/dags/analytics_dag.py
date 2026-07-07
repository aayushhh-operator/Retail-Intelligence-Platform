"""Standalone DAG for analytics."""

import sys
from pathlib import Path

from airflow.operators.empty import EmptyOperator

from airflow import DAG

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from airflow.config.dag_settings import DEFAULT_ARGS
from airflow.plugins.operators.analytics_operator import AnalyticsOperator

with DAG(
    dag_id="analytics_dag",
    default_args=DEFAULT_ARGS,
    schedule_interval=None,
    catchup=False,
) as dag:
    start = EmptyOperator(task_id="start")
    run_task = AnalyticsOperator(task_id="run_analytics")
    end = EmptyOperator(task_id="end")

    start >> run_task >> end
