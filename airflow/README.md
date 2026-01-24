# Airflow Setup for Capstone Project

Minimal Airflow setup for orchestrating dbt transformations.

## Quick Start

```bash
# Start Airflow (first time takes longer to build)
cd airflow && docker-compose up -d

# Wait for initialization (~2 minutes)
docker-compose logs -f airflow-init

# Access Airflow UI
# URL: http://localhost:8080
# Username: admin
# Password: admin
```

## Architecture

```
Airflow (LocalExecutor)
    │
    ├── postgres (metadata DB, port 5434)
    │
    ├── webserver (UI, port 8080)
    │
    └── scheduler (runs DAGs)
            │
            └── dbt_pipeline DAG
                    │
                    ├── dbt_debug (verify connection)
                    │
                    ├── dbt_run (build models)
                    │
                    └── dbt_test (run tests)
```

## DAG: capstone_dbt_pipeline

- **Schedule:** Daily at 2 AM Bangkok time
- **Tasks:**
  1. `dbt_debug` - Verify Snowflake connection
  2. `dbt_run` - Build all models (staging → marts)
  3. `dbt_test` - Run data quality tests

## Configuration

The dbt profile uses environment variables set in docker-compose.yml:
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_ROLE`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`
- `SNOWFLAKE_PRIVATE_KEY_PATH`

## Troubleshooting

```bash
# Check service status
docker-compose ps

# View scheduler logs
docker-compose logs airflow-scheduler

# View webserver logs
docker-compose logs airflow-webserver

# Restart services
docker-compose restart

# Full cleanup and restart
docker-compose down -v && docker-compose up -d
```

## Manual DAG Trigger

```bash
# Via CLI
docker-compose exec airflow-scheduler airflow dags trigger capstone_dbt_pipeline

# Or use the Airflow UI
```
