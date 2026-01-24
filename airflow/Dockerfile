# Custom Airflow image with dbt-snowflake
FROM apache/airflow:2.8.1-python3.11

# Install git as root (required for dbt packages)
USER root
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

USER airflow

# Install dbt-snowflake and dependencies
RUN pip install --no-cache-dir \
    dbt-core==1.7.0 \
    dbt-snowflake==1.7.0 \
    cryptography>=41.0.0

# Install data collection dependencies
RUN pip install --no-cache-dir \
    google-api-python-client \
    google-auth \
    google-auth-oauthlib \
    pandas \
    rich \
    python-dotenv \
    snowflake-connector-python \
    requests

# Set environment variables
ENV DBT_PROFILES_DIR=/opt/airflow/.dbt
ENV PYTHONPATH=/opt/airflow
