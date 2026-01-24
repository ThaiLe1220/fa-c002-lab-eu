# Demo Checklist (30 Minutes)

**Goal:** Prove every `#live-demo` requirement with BEFORE/AFTER evidence.

---

## PRE-DEMO SETUP (5 min before)

```bash
cd ~/code_personal/fa-c002-lab

# Start all services
cd kafka && docker-compose up -d && cd ..
cd airflow && docker-compose up -d && cd ..
sleep 30

# Reset alerts table
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

**Verify:** `docker ps | grep -E "capstone|airflow" | wc -l` → Should be 5

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
-- RAW layer state BEFORE
SELECT
    COUNT(*) as row_count,
    MAX(DATE) as latest_date,
    MAX(LOADED_AT) as last_loaded
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY;
```

**SAY:** "Current state: X rows, latest date is Jan 22, loaded at [timestamp]."

---

### 2.2 Run Batch Collection (2 min)

```bash
uv run python scripts/collect_admob_capstone.py --days 1
```

**Shows:** `Deleting... Loading X rows... ✓ Loaded`

**IMMEDIATELY in Snowflake - Prove NEW data:**
```sql
-- Show AFTER state
SELECT
    COUNT(*) as row_count,
    MAX(DATE) as latest_date,
    MAX(LOADED_AT) as last_loaded
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY;

-- Show SPECIFIC new rows (bulletproof proof)
SELECT RAW_RECORD_ID, DATE, APP_STORE_ID, LOADED_AT
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY
WHERE LOADED_AT > DATEADD(minute, -2, CURRENT_TIMESTAMP())
LIMIT 5;
```

**SAY:** "Row count changed. New date Jan 23. LOADED_AT is NOW. These RAW_RECORD_IDs are brand new."

---

### 2.3 Run dbt via Airflow (2 min)

**Trigger:**
```bash
docker exec airflow-webserver airflow dags unpause capstone_dbt_pipeline
docker exec airflow-webserver airflow dags trigger capstone_dbt_pipeline
```

**While waiting, show in Snowflake:**
```sql
-- BEFORE dbt run
SELECT COUNT(*) as before_count FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE;
```

**Check Airflow status:**
```bash
docker exec airflow-webserver airflow dags list-runs -d capstone_dbt_pipeline -o table
```

**After success, show in Snowflake:**
```sql
-- AFTER dbt run (incremental proof)
SELECT COUNT(*) as after_count FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE;

-- Show new data with DBT_UPDATED_AT
SELECT d.DATE, a.APP_NAME, f.AD_REVENUE, f.DBT_UPDATED_AT
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY
JOIN DB_T34.ANALYTICS.DIM_APPS a ON f.APP_KEY = a.APP_KEY
WHERE f.DBT_UPDATED_AT > DATEADD(minute, -5, CURRENT_TIMESTAMP())
ORDER BY f.DBT_UPDATED_AT DESC LIMIT 5;
```

**SAY:** "Airflow orchestrated dbt. Row count increased. Incremental - not full refresh. No duplicates."

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
