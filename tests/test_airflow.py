"""Tests for Phase 7 Airflow Layer."""

import pytest
from airflow.models import DagBag

def test_no_import_errors():
    """Verify that all DAGs in the airflow/dags folder load without errors."""
    dag_bag = DagBag(dag_folder='airflow/dags', include_examples=False)
    assert len(dag_bag.import_errors) == 0, f"DAG import failures: {dag_bag.import_errors}"

def test_retail_pipeline_dag_structure():
    """Test the structure of the main retail pipeline DAG."""
    dag_bag = DagBag(dag_folder='airflow/dags', include_examples=False)
    dag = dag_bag.get_dag(dag_id='retail_intelligence_pipeline')
    assert dag is not None
    
    # Check tasks exist
    tasks = {task.task_id: task for task in dag.tasks}
    assert 'extract_data' in tasks
    assert 'validate_data' in tasks
    assert 'transform_data' in tasks
    assert 'load_warehouse' in tasks
    assert 'build_analytics' in tasks
    
    # Check dependencies (simplified)
    extract_task = tasks['extract_data']
    assert 'validate_data' in [t.task_id for t in extract_task.downstream_list]
