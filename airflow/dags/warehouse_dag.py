"""Standalone DAG for warehouse."""

import sys
from pathlib import Path
from airflow import DAG
from airflow.operators.empty import EmptyOperator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from airflow.config.dag_settings import DEFAULT_ARGS
from airflow.plugins.operators.warehouse_operator import WarehouseOperator

with DAG(
    dag_id='warehouse_dag',
    default_args=DEFAULT_ARGS,
    schedule_interval=None,
    catchup=False,
) as dag:
    start = EmptyOperator(task_id='start')
    run_task = WarehouseOperator(task_id='run_warehouse')
    end = EmptyOperator(task_id='end')
    
    start >> run_task >> end
