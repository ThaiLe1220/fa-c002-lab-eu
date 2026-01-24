# Custom Airflow image with dbt-snowflake
FROM apache/airflow:2.8.1-python3.11

USER airflow

# Install dbt-snowflake and dependencies
RUN pip install --no-cache-dir \
    dbt-core==1.7.0 \
    dbt-snowflake==1.7.0 \
    cryptography>=41.0.0

# Set dbt profiles directory
ENV DBT_PROFILES_DIR=/opt/airflow/.dbt
