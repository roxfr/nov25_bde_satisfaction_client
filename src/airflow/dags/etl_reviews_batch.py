# File: src\airflow\dags\etl_reviews_batch.py

"""Orchestre le pipeline ETL des avis en trois tâches Airflow séquentielles."""

from datetime import datetime
from typing import Dict, Any
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models.param import Param
from etl.pipeline.reviews_etl import run_extract, run_transform, run_load


default_args: Dict[str, Any] = {
    "owner": "airflow",
    "retries": 1,
}

def extract_with_params(**context):
    max_pages = context["params"]["max_pages"]

    return run_extract(
        data_path="/opt/airflow/etl/data",
        max_pages=max_pages,
    )

dag = DAG(
    dag_id="etl_reviews_batch",
    default_args=default_args,
    description="Pipeline ETL Reviews en 3 étapes",
    start_date=datetime(2024, 1, 1),
    schedule="0 0 */3 * *",
    catchup=False,
    tags=["etl", "reviews"],
    params={
        "max_pages": Param(
            1,
            type="integer",
            minimum=1,
            maximum=10,
            description="Nombre de pages à extraire"
        )
    },
)

extract_task = PythonOperator(
    task_id="extract_reviews",
    python_callable=extract_with_params,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_reviews",
    python_callable=run_transform,
    op_kwargs={"data_path": "/opt/airflow/etl/data"},
    dag=dag,
)

load_task = PythonOperator(
    task_id="load_reviews",
    python_callable=run_load,
    op_kwargs={"data_path": "/opt/airflow/etl/data"},
    dag=dag,
)

extract_task >> transform_task >> load_task
