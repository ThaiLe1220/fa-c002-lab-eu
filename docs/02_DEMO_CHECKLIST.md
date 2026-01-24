# Demo Checklist (30 Minutes)

**Goal:** Prove every `#live-demo` requirement with BEFORE/AFTER evidence.

---

## PRE-DEMO SETUP (10 min before)

### Step 1: Start Services

```bash
cd ~/code_personal/fa-c002-lab

# Start all services
cd kafka && docker-compose up -d && cd ..
cd airflow && docker-compose up -d && cd ..
sleep 30
```

**Verify:** `docker ps | grep -E "capstone|airflow" | wc -l` → Should be 5

---

### Step 2: Reset to Jan 22 State (CRITICAL for "new data" proof)

```bash
# Delete Jan 23 from RAW tables (so we can show FRESH ingestion during demo)
uv run python -c "
from scripts.utils.snowflake_client import get_snowflake_client
client = get_snowflake_client(schema='RAW_CAPSTONE')
conn = client.connect()
cursor = conn.cursor()
cursor.execute(\"DELETE FROM ADMOB_DAILY WHERE DATE = '20260123'\")
print(f'Deleted {cursor.rowcount} from ADMOB_DAILY')
cursor.execute(\"DELETE FROM ADJUST_DAILY WHERE DAY = '2026-01-23'\")
print(f'Deleted {cursor.rowcount} from ADJUST_DAILY')
client.close()
"

# Rebuild ANALYTICS with full-refresh (back to Jan 22)
cd my_dbt_project && dbt build --full-refresh && cd ..
```

**Verify in Snowflake:**
```sql
SELECT MAX(DATE) FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY;  -- Should be 20260122
SELECT MAX(DATE) FROM DB_T34.ANALYTICS.DIM_DATES;       -- Should be 2026-01-22
```

---

### Step 3: Reset Alerts Table

```bash
docker exec capstone-postgres psql -U capstone -d streaming -c "
DROP TABLE IF EXISTS alerts;
CREATE TABLE alerts (
    id UUID PRIMARY KEY, timestamp TIMESTAMP NOT NULL,
    alert_type VARCHAR(50) NOT NULL, severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL, region VARCHAR(10), value NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);"

# Start consumer (background)
uv run python kafka/consumer.py &
sleep 5

# Generate initial alerts
uv run python kafka/producer.py --batch 20 --interval 0
```

---

### Step 4: Clean Git State

```bash
# Remove demo comments from dim_dates.sql
cd my_dbt_project/models/03_mart
grep -v "^-- demo" dim_dates.sql > temp.sql && mv temp.sql dim_dates.sql
cd ../../..
git checkout my_dbt_project/models/03_mart/dim_dates.sql 2>/dev/null || true
```

---

### Pre-Demo Checklist

- [ ] 5 Docker containers running
- [ ] RAW latest date = Jan 22 (NOT Jan 23)
- [ ] ANALYTICS latest date = Jan 22
- [ ] Consumer running, ~20 alerts in PostgreSQL
- [ ] dim_dates.sql is clean (no demo comments)

---

## PHASE 1: Real-time Pipeline (5 min)

### 1.1 Trigger CI/CD (1 min)

```bash
echo "-- demo $(date)" >> my_dbt_project/models/03_mart/dim_dates.sql
git add my_dbt_project/ && git commit -m "demo: trigger CI" && git push
```

**SAY:** "CI running in background - SQLFluff + dbt tests. We'll check results later."

---

### 1.2 Kafka Streaming Demo (3 min)

**BEFORE - Show current state:**
```bash
docker exec capstone-postgres psql -U capstone -d streaming -c "SELECT COUNT(*) as before_count FROM alerts;"
```

**EXECUTE - Produce 5 alerts with visible timestamps:**
```bash
uv run python kafka/producer.py --batch 5 --interval 2
```

**AFTER - Prove data landed < 5 min latency:**
```bash
docker exec capstone-postgres psql -U capstone -d streaming -c "
SELECT COUNT(*) as after_count FROM alerts;
SELECT alert_type, severity, region, created_at
FROM alerts ORDER BY created_at DESC LIMIT 5;"
```

**SAY:** "Count increased. Timestamps show < 1 second latency. Kafka → Consumer → PostgreSQL working."

---

### 1.3 CI/CD Results (1 min)

```bash
gh run list --limit 1
gh run view --log 2>&1 | grep -E "PASS|Completed|SQLFluff" | tail -10
```

**SAY:** "SQLFluff passed. 26 dbt tests passed."

---

## PHASE 2: Batch Pipeline (5 min)

### 2.1 Show BEFORE State (1 min)

**In Snowflake UI - Copy these results:**
```sql
-- RAW layer state BEFORE (should show Jan 22 from pre-demo reset)
SELECT
    COUNT(*) as row_count,
    MAX(DATE) as latest_date,
    MAX(LOADED_AT) as last_loaded
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY;
```

**SAY:** "Current state: ~109K rows, latest date is **Jan 22**. No Jan 23 data yet."

---

### 2.2 Run Batch Collection (2 min)

```bash
uv run python scripts/collect_admob_capstone.py --days 1
```

**Shows:** `Loading X rows to RAW_CAPSTONE.ADMOB_DAILY... ✓ Loaded X rows`

**IMMEDIATELY in Snowflake - Prove NEW data:**
```sql
-- Show AFTER state (row count INCREASED, new date appeared)
SELECT
    COUNT(*) as row_count,
    MAX(DATE) as latest_date,
    MAX(LOADED_AT) as last_loaded
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY;

-- Show the NEW Jan 23 rows (didn't exist before!)
SELECT RAW_RECORD_ID, DATE, APP_STORE_ID, LOADED_AT
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY
WHERE DATE = '20260123'
ORDER BY LOADED_AT DESC
LIMIT 5;
```

**SAY:** "Row count increased from 109K to 113K. **New date Jan 23 appeared**. These RAW_RECORD_IDs are brand new - they didn't exist 30 seconds ago."

---

### 2.3 Run dbt via Airflow (2 min)

**BEFORE dbt - Show ANALYTICS only has Jan 22:**
```sql
SELECT MAX(d.DATE) as latest_date, COUNT(*) as row_count
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY;
```

**SAY:** "ANALYTICS has data up to Jan 22. Let's run dbt to transform the new Jan 23 data."

**Trigger Airflow:**
```bash
docker exec airflow-webserver airflow dags unpause capstone_dbt_pipeline
docker exec airflow-webserver airflow dags trigger capstone_dbt_pipeline
```

**Check status (wait ~30s):**
```bash
docker exec airflow-webserver airflow dags list-runs -d capstone_dbt_pipeline -o table
```

**AFTER dbt success - Show Jan 23 flowed through:**
```sql
-- ANALYTICS now has Jan 23!
SELECT MAX(d.DATE) as latest_date, COUNT(*) as row_count
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY;

-- Show the NEW Jan 23 rows in fact table
SELECT d.DATE, a.APP_NAME, f.AD_REVENUE, f.DBT_UPDATED_AT
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY
JOIN DB_T34.ANALYTICS.DIM_APPS a ON f.APP_KEY = a.APP_KEY
WHERE d.DATE = '2026-01-23'
ORDER BY f.AD_REVENUE DESC LIMIT 5;
```

**SAY:** "Airflow orchestrated dbt. Jan 23 data now in ANALYTICS. Incremental model - only processed new data, no full refresh."

---

## PHASE 3: AI Agent & RAG (10 min)

### 3.1 Show RAG Document (1 min)

```bash
head -50 docs/business_rules/ameno_business_rules.md
```

**SAY:** "Business rules doc with ROAS thresholds. Chunked and embedded in FAISS vector store."

---

### 3.2 Start Agent (1 min)

```bash
uv run streamlit run agent/app.py &
sleep 3
open http://localhost:8501
```

---

### 3.3 Demo: Batch Data Query (2 min)

**ASK AGENT:**
```
What's our total revenue for the latest date?
```

**VERIFY in Snowflake:**
```sql
SELECT SUM(f.AD_REVENUE) as total
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY
WHERE d.DATE = (SELECT MAX(DATE) FROM DB_T34.ANALYTICS.DIM_DATES);
```

**SAY:** "Agent queried Snowflake. Numbers match."

---

### 3.4 Demo: Real-time Data Query (2 min)

**ASK AGENT:**
```
Show me recent critical alerts
```

**VERIFY:**
```bash
docker exec capstone-postgres psql -U capstone -d streaming -c \
  "SELECT alert_type, severity, region FROM alerts WHERE severity='critical' ORDER BY created_at DESC LIMIT 5;"
```

**SAY:** "Agent queried PostgreSQL streaming data. Same alerts."

---

### 3.5 Demo: RAG Document Query (2 min)

**ASK AGENT:**
```
What is the ROAS threshold for scaling campaigns?
```

**VERIFY:**
```bash
grep -A 5 "ROAS Thresholds" docs/business_rules/ameno_business_rules.md
```

**SAY:** "Agent searched vector store. Found business rules - 80% threshold."

---

### 3.6 Demo: Combined Query + Memory (2 min)

**ASK AGENT (tests memory + combined sources):**
```
Based on our thresholds, which apps from yesterday are losing money?
```

**SAY:** "Agent combined: Snowflake metrics + RAG thresholds. Shows apps with D0 ROAS < 80%."

**FOLLOW-UP (tests conversation memory):**
```
What should we do about the worst performing one?
```

**SAY:** "Agent remembered context. Recommended action based on business rules."

---

## PHASE 4: Q&A Prep (10 min)

### Quick Answers

| Question | Answer |
|----------|--------|
| Why star schema? | Industry standard for analytics. Optimized for aggregations. |
| Why incremental? | Efficient - only process new data. See `{% if is_incremental() %}` |
| Why FAISS not Pinecone? | Free, local, works offline. Good for small docs. |
| Why delete-insert? | Idempotent. Safe to retry. No duplicates. |
| What if API fails? | Retry logic. Can re-run same day safely. |
| What if table dropped? | Snowflake Time Travel: `UNDROP TABLE` |

### Show Incremental Code

```bash
grep -A 3 "is_incremental" my_dbt_project/models/02_intermediate/int_app_daily_metrics.sql
```

### Show dbt Tests

```bash
cd my_dbt_project && dbt test --select "stg_admob_capstone" 2>&1 | tail -10
```

---

## EMERGENCY FIXES

**Kafka broken:**
```bash
cd kafka && docker-compose down -v && docker-compose up -d && cd ..
```

**Airflow broken:**
```bash
cd airflow && docker-compose down -v && docker-compose up -d && cd ..
```

**Agent won't start:**
```bash
pkill -f streamlit && uv run streamlit run agent/app.py
```

**dbt fails:**
```bash
cd my_dbt_project && dbt clean && dbt deps && dbt build
```

---

## GRADING CHECKLIST

| Requirement | Demo Proof |
|-------------|------------|
| ✅ Batch data source | AdMob API → Snowflake RAW |
| ✅ Streaming < 5 min | Kafka timestamps show < 1s |
| ✅ Airflow 3+ tasks | debug → run → test |
| ✅ `#live-demo` NEW data | BEFORE/AFTER row count + RAW_RECORD_ID |
| ✅ Star schema | dim_apps, dim_dates, fct_* |
| ✅ dbt incremental | Row count increase, no duplicates |
| ✅ dbt test | 26 tests pass |
| ✅ `#live-demo` dbt via Airflow | Trigger + success |
| ✅ CI/CD 2 checks | SQLFluff + dbt test |
| ✅ README + Architecture | README.md exists |
| ✅ Chatbot with memory | Multi-turn conversation |
| ✅ RAG documents | Business rules query |
| ✅ Batch data query | Snowflake revenue |
| ✅ Real-time query | PostgreSQL alerts |
| ✅ Combined query | Metrics + thresholds |
