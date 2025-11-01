# Mid-Course Test Quick Guide

## Pre-Demo Setup (30 mins before)

```bash
# Start Docker PostgreSQL
docker-compose up -d

# Verify running
docker ps

# Check Snowflake connection
cd my_dbt_project
dbt debug
cd ..
```

**Note on Data Collection:**
- AdMob: `--batch` mode (all rows same timestamp) → Snowflake
- Adjust: `--realtime` mode (row by row, staggered timestamps, multithreaded) → Snowflake
- Both scripts fetch data and save to CSV locally before loading to Snowflake
- PostgreSQL is optional demo only (to show containerization capability)

---

## Demo Flow (20 minutes)

### Section 1A: Git Workflow (3 mins) - 15 pts

```bash
# Show branches
git branch -a

# Show merged PRs
gh pr list --state merged

# Show commits
git log --oneline -10
```

---

### Section 1B: Data Ingestion (5 mins) - 20 pts

**1. Batch Pipeline → Snowflake (AdMob):**
```bash
uv run python scripts/collect_admob_midtest.py --batch
uv run python scripts/collect_admob_midtest.py --realtime
```

**2. Realtime Pipeline → Snowflake (Adjust, row by row):**
```bash
uv run python scripts/collect_adjust_midtest.py --batch
uv run python scripts/collect_adjust_midtest.py --realtime

```

**3. Docker PostgreSQL (Optional - to show capability):**
```bash
# Show container running
docker ps

# Load sample data to PostgreSQL
uv run python scripts/collect_adjust_realtime.py

# Verify data
docker exec fa-c002-midtest-postgres psql -U midtest_user -d midtest_db -c "SELECT COUNT(*), MAX(loaded_at) FROM raw.adjust_realtime;"
```

---

### Section 2A: dbt Transformation (7 mins) - 30 pts

```bash
cd my_dbt_project

# Show structure
ls -R models

# Show incremental model
head -20 models/02_intermediate/int_app_daily_metrics.sql

# Show custom macro
cat macros/calculate_ctr.sql

# Show tests
grep -A 3 "data_tests" models/01_staging/schema.yml

# Run models
dbt run --select stg_admob_midtest stg_adjust_midtest int_app_daily_metrics

# Run tests
dbt test

cd ..
```

---

### Section 2B: Data Modeling (2 mins) - 10 pts

```bash
# Show ERD
cat docs/midtest/ERD_STAR_SCHEMA.md
```

---

### Section 3: CI/CD (2 mins) - 5 pts

```bash
# Show workflow file
head -30 .github/workflows/dbt_ci.yml

# Show latest run
gh run list --limit 1

# Or open GitHub Actions
open https://github.com/ThaiLe1220/fa-c002-lab/actions
```

---

### Extra Features (1 min) - 10 pts

```bash
# Show dbt_utils usage
cat my_dbt_project/packages.yml

# Show surrogate key implementation
grep -A 2 "generate_surrogate_key" my_dbt_project/models/03_mart/fct_app_daily_performance.sql
```

---

## Verification Queries

**PostgreSQL:**
```bash
docker exec fa-c002-midtest-postgres psql -U midtest_user -d midtest_db -c "SELECT day, store_id, country_code, installs, loaded_at FROM raw.adjust_realtime ORDER BY loaded_at DESC LIMIT 5;"
```

**Snowflake - Prove fresh data (UUID uniqueness + timestamp):**
```sql
SELECT
  'ADMOB' as source,
  COUNT(*) as row_count,
  COUNT(DISTINCT RAW_RECORD_ID) as unique_ids,
  MAX(LOADED_AT) as latest
FROM DB_T34.RAW_MIDTEST.ADMOB_DAILY_MIDTEST

UNION ALL

SELECT
  'ADJUST' as source,
  COUNT(*) as row_count,
  COUNT(DISTINCT RAW_RECORD_ID) as unique_ids,
  MAX(LOADED_AT) as latest
FROM DB_T34.RAW_MIDTEST.ADJUST_DAILY_MIDTEST;
```

**Snowflake - Trace ONE row through all layers (PROOF IT WORKS):**
```sql
-- Step 1: Get newest row from raw (copy RAW_RECORD_ID, APP_STORE_ID, DATE)
SELECT
  RAW_RECORD_ID,
  APP_STORE_ID,
  DATE,
  AD_IMPRESSIONS,
  ESTIMATED_EARNINGS,
  LOADED_AT
FROM DB_T34.RAW_MIDTEST.ADMOB_DAILY_MIDTEST
ORDER BY LOADED_AT DESC
LIMIT 1;

-- Step 2: Find it in staging (paste RAW_RECORD_ID from Step 1)
SELECT
  raw_record_id,
  app_store_id,
  date,
  ad_impressions,
  estimated_earnings,
  loaded_at
FROM DB_T34.PUBLIC.STG_ADMOB_MIDTEST
WHERE raw_record_id = '<paste-uuid-here>';

-- Step 3: Find it in intermediate (paste APP_STORE_ID and DATE from Step 1)
SELECT
  app_store_id,
  date,
  country_code,
  ad_impressions,
  ad_revenue,
  installs,
  daus
FROM DB_T34.PUBLIC.INT_APP_DAILY_METRICS
WHERE app_store_id = '<paste-app-store-id>'
  AND date = '<paste-date>';

-- Step 4: Find it in mart (paste APP_STORE_ID and DATE from Step 1)
SELECT
  f.performance_key,
  f.ad_impressions,
  f.ad_revenue,
  f.installs,
  f.ad_ctr,
  a.app_name,
  d.date
FROM DB_T34.PUBLIC.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.PUBLIC.DIM_APPS a ON f.app_key = a.app_key
JOIN DB_T34.PUBLIC.DIM_DATES d ON f.date_key = d.date_key
WHERE a.app_store_id = '<paste-app-store-id>'
  AND d.date = '<paste-date>';
```

---

## Cleanup (After Demo)

```bash
# Stop Docker
docker-compose down

# Or keep running
docker-compose down && docker-compose up -d
```

---

## Emergency Commands

**If Docker fails:**
```bash
docker-compose down -v
docker-compose up -d
sleep 10
uv run python scripts/collect_adjust_realtime.py
```

**If Snowflake fails:**
```bash
cd my_dbt_project
dbt debug
dbt run --select stg_admob_midtest
cd ..
```

**Check CI status:**
```bash
gh run list --limit 3
gh run view --log
```

---

**Target Score: 80/100**
