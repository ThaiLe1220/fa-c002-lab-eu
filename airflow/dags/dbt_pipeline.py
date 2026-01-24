"""
dbt Pipeline DAG for Capstone Project.

Orchestrates dbt transformations for the Mobile Analytics platform.
Runs daily at 2 AM to transform raw AdMob/Adjust data into analytics models.
"""

import os
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


# dbt project configuration
DBT_PROJECT_DIR = "/opt/airflow/dbt_project"
DBT_PROFILES_DIR = "/opt/airflow/.dbt"

# Environment variables for Snowflake connection
DBT_ENV = {
    "PATH": "/home/airflow/.local/bin:" + os.environ.get("PATH", ""),
    "DBT_PROFILES_DIR": DBT_PROFILES_DIR,
    "SNOWFLAKE_ACCOUNT": os.environ.get("SNOWFLAKE_ACCOUNT", ""),
    "SNOWFLAKE_USER": os.environ.get("SNOWFLAKE_USER", ""),
    "SNOWFLAKE_ROLE": os.environ.get("SNOWFLAKE_ROLE", ""),
    "SNOWFLAKE_WAREHOUSE": os.environ.get("SNOWFLAKE_WAREHOUSE", ""),
    "SNOWFLAKE_DATABASE": os.environ.get("SNOWFLAKE_DATABASE", ""),
    "SNOWFLAKE_SCHEMA": os.environ.get("SNOWFLAKE_SCHEMA", ""),
    "SNOWFLAKE_PRIVATE_KEY_PATH": os.environ.get("SNOWFLAKE_PRIVATE_KEY_PATH", ""),
}

default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="capstone_dbt_pipeline",
    schedule=None,  # Manual trigger only (for demo)
    start_date=pendulum.datetime(2024, 1, 1, tz="Asia/Ho_Chi_Minh"),
    catchup=False,
    tags=["capstone", "dbt", "snowflake", "transformations"],
    max_active_runs=1,
    description="Runs dbt transformations to build analytics models from raw AdMob/Adjust data",
    default_args=default_args,
) as dag:

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt debug",
        env=DBT_ENV,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run",
        env=DBT_ENV,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test",
        env=DBT_ENV,
    )

    # Task dependencies: debug -> run -> test
    dbt_debug >> dbt_run >> dbt_test
