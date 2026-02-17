# File: src\airflow\dags\etl_reviews_batch.py

"""Orchestre le pipeline ETL des avis en trois tâches Airflow séquentielles."""

from datetime import datetime
from typing import Dict, Any
from airflow import DAG
from airflow.operators.python import PythonOperator
from etl.pipeline.reviews_etl import run_extract, run_transform, run_load

default_args: Dict[str, Any] = {
    "owner": "airflow",
    "retries": 1,
}

# Crée et configure le DAG du pipeline ETL des avis
dag = DAG(
    dag_id="etl_reviews_batch",
    default_args=default_args,
    description="Pipeline ETL Reviews en 3 étapes",
    start_date=datetime(2024, 1, 1),
    schedule="0 0 */3 * *",  # Toutes les 3 heures
    catchup=False,
    tags=["etl", "reviews"],
)

# Tâche d'extraction
extract_task = PythonOperator(
    task_id="extract_reviews",
    python_callable=run_extract,
    op_kwargs={
        "data_path": "/opt/airflow/etl/data",
        "max_pages": 1
    },
    dag=dag
)

# Tâche de transformation
transform_task = PythonOperator(
    task_id="transform_reviews",
    python_callable=run_transform,
    op_kwargs={"data_path": "/opt/airflow/etl/data"},
    dag=dag
)

# Tâche de chargement
load_task = PythonOperator(
    task_id="load_reviews",
    python_callable=run_load,
    op_kwargs={"data_path": "/opt/airflow/etl/data"},
    dag=dag
)

extract_task >> transform_task >> load_task
