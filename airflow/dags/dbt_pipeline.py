"""
Capstone Data Pipeline DAG.

Full pipeline orchestration:
1. Collect AdMob data from API → Snowflake RAW
2. Collect Adjust data from API → Snowflake RAW
3. Run dbt transformations (debug → run → test)

This demonstrates Airflow orchestrating both data ingestion AND transformation.
"""

import os
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


# Directory configuration
DBT_PROJECT_DIR = "/opt/airflow/dbt_project"
DBT_PROFILES_DIR = "/opt/airflow/.dbt"
SCRIPTS_DIR = "/opt/airflow/scripts"

# Common environment variables
COMMON_ENV = {
    "PATH": "/home/airflow/.local/bin:" + os.environ.get("PATH", ""),
    "PYTHONPATH": "/opt/airflow",
    # Snowflake connection
    "SNOWFLAKE_ACCOUNT": os.environ.get("SNOWFLAKE_ACCOUNT", ""),
    "SNOWFLAKE_USER": os.environ.get("SNOWFLAKE_USER", ""),
    "SNOWFLAKE_ROLE": os.environ.get("SNOWFLAKE_ROLE", ""),
    "SNOWFLAKE_WAREHOUSE": os.environ.get("SNOWFLAKE_WAREHOUSE", ""),
    "SNOWFLAKE_DATABASE": os.environ.get("SNOWFLAKE_DATABASE", ""),
    "SNOWFLAKE_SCHEMA": os.environ.get("SNOWFLAKE_SCHEMA", ""),
    "SNOWFLAKE_PRIVATE_KEY_PATH": os.environ.get("SNOWFLAKE_PRIVATE_KEY_PATH", ""),
}

# dbt-specific environment
DBT_ENV = {
    **COMMON_ENV,
    "DBT_PROFILES_DIR": DBT_PROFILES_DIR,
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
    tags=["capstone", "data-ingestion", "dbt", "snowflake"],
    max_active_runs=1,
    description="Full pipeline: API collection → Snowflake RAW → dbt transformations → ANALYTICS",
    default_args=default_args,
) as dag:

    # ========== DATA COLLECTION TASKS ==========

    collect_admob = BashOperator(
        task_id="collect_admob",
        bash_command=f"cd /opt/airflow && python {SCRIPTS_DIR}/collect_admob_capstone.py --days 1",
        env=COMMON_ENV,
        doc="Collect AdMob data from Google API and load to Snowflake RAW_CAPSTONE.ADMOB_DAILY",
    )

    collect_adjust = BashOperator(
        task_id="collect_adjust",
        bash_command=f"cd /opt/airflow && python {SCRIPTS_DIR}/collect_adjust_capstone.py --days 1",
        env=COMMON_ENV,
        doc="Collect Adjust data from API and load to Snowflake RAW_CAPSTONE.ADJUST_DAILY",
    )

    # ========== DBT TRANSFORMATION TASKS ==========

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt debug",
        env=DBT_ENV,
        doc="Verify dbt connection to Snowflake",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run",
        env=DBT_ENV,
        doc="Run dbt models: staging → intermediate → mart",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test",
        env=DBT_ENV,
        doc="Run dbt tests (26 tests)",
    )

    # ========== TASK DEPENDENCIES ==========
    # Data collection (parallel) → dbt pipeline (sequential)
    #
    #   collect_admob ─┐
    #                  ├─→ dbt_debug → dbt_run → dbt_test
    #   collect_adjust ┘
    #
    [collect_admob, collect_adjust] >> dbt_debug >> dbt_run >> dbt_test
