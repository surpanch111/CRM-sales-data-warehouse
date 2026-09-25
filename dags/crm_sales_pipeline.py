from datetime import datetime, timedelta
from pathlib import Path

from etl.extract import main as extract_main
from etl.load_staging import main as load_main
from etl.transform_warehouse import main as transform_main
from etl.quality_checks import main as quality_main
from etl.init_db import main as init_main

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from airflow.sdk.definitions.taskgroup import TaskGroup
from etl.dbt_runner import run_dbt_models, run_dbt_tests

PROJECT_ROOT = Path("/usr/local/airflow")

default_args = {
    "owner": "shaan",
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="crm_sales_warehouse_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="0 0 * * *",
    catchup=False,
    tags=["crm", "etl", "warehouse"],
) as dag:

    init_warehouse = PythonOperator(
        task_id="init_warehouse",
        python_callable=init_main,
    )

    with TaskGroup(group_id="extraction") as extraction_group:

        extract_data = PythonOperator(
            task_id="extract_data",
            python_callable=extract_main,
        )

    with TaskGroup(group_id="loading") as loading_group:

        load_staging = PythonOperator(
            task_id="load_staging",
            python_callable=load_main,
        )

    with TaskGroup(group_id="transformation") as transformation_group:

        transform_warehouse = PythonOperator(
            task_id="transform_warehouse",
            python_callable=transform_main,
        )

        dbt_run = PythonOperator(
            task_id="dbt_run",
            python_callable=run_dbt_models,
        )

        dbt_test = PythonOperator(
            task_id="dbt_test",
            python_callable=run_dbt_tests,
        )

        transform_warehouse >> dbt_run >> dbt_test

    with TaskGroup(group_id="validation") as validation_group:

        quality_checks = PythonOperator(
            task_id="quality_checks",
            python_callable=quality_main,
        )

    init_warehouse >> extraction_group >> loading_group >> transformation_group >> validation_group