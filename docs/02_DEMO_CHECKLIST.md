# Demo Checklist - 30 Minutes

Step-by-step commands with verification. Each step has EXECUTE and VERIFY.

**Demo Date:** 2026-01-24
**Time Budget:** 30 minutes total

---

## Pre-Demo Setup (10 min before demo)

### 1. Open Required Windows

```
Window 1: Terminal (for commands)
Window 2: Snowflake UI (logged in, DB_T34.ANALYTICS)
Window 3: Browser - GitHub Actions page
Window 4: Browser - Airflow UI (will open later)
```

### 2. Start Docker Services

**EXECUTE:**
```bash
cd ~/code_personal/fa-c002-lab
cd kafka && docker-compose up -d && cd ..
cd airflow && docker-compose up -d && cd ..
```

**VERIFY:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "capstone|airflow"
```

**Expected:** 5 containers running (kafka, streaming-db, webserver, scheduler, postgres)

### 3. Generate Initial Alerts

**EXECUTE:**
```bash
uv run python kafka/producer.py --batch 20 --interval 0
```

**VERIFY:**
```bash
docker exec capstone-streaming-db psql -U postgres -d streaming -c "SELECT COUNT(*) FROM alerts;"
```

**Expected:** count >= 20

---

## Phase 1: Real-time Pipeline (5 min)

### Step 1.1: Start CI/CD (1 min)

**SAY:** "Let me trigger the CI/CD pipeline first, it will run in background"

**EXECUTE:** (In GitHub - push a small change or use workflow dispatch)
```bash
# Option A: Manual trigger in GitHub Actions UI
# Option B: Small commit
echo "# Demo $(date)" >> DEMO_RUN.md && git add DEMO_RUN.md && git commit -m "demo: trigger CI" && git push && rm DEMO_RUN.md
```

**VERIFY:**
```bash
gh run list --limit 1
```

**Expected:** Shows "in_progress" status

**SAY:** "CI is running SQLFluff lint and dbt tests. Let's continue while it runs."

---

### Step 1.2: Kafka Data Flow Demo (3 min)

**SAY:** "Now I'll show real-time data flow with Kafka"

#### Show Producer

**EXECUTE:**
```bash
uv run python kafka/producer.py --batch 5 --interval 2
```

**Expected output:** Shows 5 alerts being produced with 2-second intervals

#### Verify in PostgreSQL

**VERIFY:**
```bash
docker exec capstone-streaming-db psql -U postgres -d streaming -c \
  "SELECT id, alert_type, severity, app_id, created_at FROM alerts ORDER BY created_at DESC LIMIT 5;"
```

**Expected:** Shows 5 recent alerts with timestamps from just now

**SAY:** "Producer sends alerts to Kafka topic, consumer writes to PostgreSQL. These timestamps prove the data just landed."

---

### Step 1.3: CI/CD Results (1 min)

**SAY:** "Let's check if CI completed"

**VERIFY:**
```bash
gh run list --limit 1
gh run view --log 2>&1 | grep -E "(PASS|ERROR|success|fail)" | tail -10
```

**Expected:** Shows "success" and "26 data tests PASS"

**SAY:** "CI runs SQLFluff for code quality and dbt test for data quality. All 26 tests passed."

---

## Phase 2: Batch Pipeline (5 min)

### Step 2.1: Show Current Data State (1 min)

**SAY:** "First, let me show the current data in Snowflake"

**VERIFY (in Snowflake UI):**
```sql
-- Current state before collection
SELECT
    MAX(date) as latest_date,
    COUNT(*) as total_rows,
    MAX(loaded_at) as last_loaded
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY;
```

**Write down:** latest_date = _____, total_rows = _____

---

### Step 2.2: Run Batch Collection (2 min)

**SAY:** "Now I'll collect yesterday's fresh data from AdMob and Adjust APIs"

**EXECUTE:**
```bash
# Collect yesterday only (--days 1)
uv run python scripts/collect_admob_capstone.py --days 1
```

**Expected output:**
```
Deleting existing data for 2026-01-23 to 2026-01-23...
  Deleted X existing rows
Loading Y rows to RAW_CAPSTONE.ADMOB_DAILY...
✓ Loaded Y rows to Snowflake
```

**EXECUTE:**
```bash
uv run python scripts/collect_adjust_capstone.py --days 1
```

**VERIFY (in Snowflake UI):**
```sql
-- Proof: New data with fresh timestamp
SELECT
    raw_record_id,
    date,
    app_store_id,
    loaded_at
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY
WHERE loaded_at > DATEADD(minute, -5, CURRENT_TIMESTAMP())
ORDER BY loaded_at DESC
LIMIT 5;
```

**SAY:** "See the loaded_at timestamp? This data was just collected from the API. The delete-insert pattern ensures idempotency."

---

### Step 2.3: Run dbt via Airflow (2 min)

**SAY:** "Now Airflow will orchestrate dbt transformation"

**EXECUTE:** Open http://localhost:8080 (admin/admin)

1. Find DAG: `dbt_pipeline`
2. Click "Trigger DAG"
3. Watch tasks: debug → run → test

**VERIFY (in Snowflake UI while waiting):**
```sql
-- Show dbt model structure
SELECT
    table_schema,
    table_name,
    row_count,
    last_altered
FROM DB_T34.information_schema.tables
WHERE table_schema = 'ANALYTICS'
ORDER BY table_name;
```

**SAY:** "dbt transforms raw data through staging → intermediate → mart layers"

**VERIFY (after Airflow completes):**
```sql
-- Fresh data in fact table
SELECT
    date,
    app_store_id,
    ad_revenue,
    network_cost,
    CASE WHEN network_cost > 0
         THEN ROUND(ad_revenue_d0 / network_cost * 100, 2)
         ELSE 0 END as d0_roas_pct,
    dbt_updated_at
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE
WHERE date = CURRENT_DATE() - 1
ORDER BY ad_revenue DESC
LIMIT 5;
```

**SAY:** "Fact table now has yesterday's data with calculated metrics like D0 ROAS"

---

## Phase 3: AI Agent & RAG (10 min)

### Step 3.1: Show RAG Document (2 min)

**SAY:** "The agent uses RAG to answer questions about business rules"

**EXECUTE:**
```bash
cat docs/business_rules/ameno_business_rules.md | head -50
```

**SAY:** "This document contains our business rules - ROAS thresholds, CPI benchmarks, etc."

**EXECUTE (optional - show chunking):**
```bash
uv run python agent/rag_demo.py
# Select option 2 (Show Chunking)
```

**SAY:** "RAG chunks the document into ~500 char pieces, embeds them as vectors, and searches by similarity"

---

### Step 3.2: Start Agent (1 min)

**EXECUTE:**
```bash
uv run streamlit run agent/app.py
```

**Opens:** http://localhost:8501

---

### Step 3.3: Demo Query - Batch Data (2 min)

**SAY:** "Let me ask about revenue from Snowflake"

**ASK AGENT:**
```
What's our total revenue yesterday?
```

**VERIFY (in Snowflake UI):**
```sql
SELECT SUM(ad_revenue) as total_revenue
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE
WHERE date = CURRENT_DATE() - 1;
```

**SAY:** "Agent queried Snowflake and returned the same number"

---

### Step 3.4: Demo Query - Streaming Data (2 min)

**SAY:** "Now let me check real-time alerts from Kafka pipeline"

**ASK AGENT:**
```
Show me critical alerts
```

**VERIFY:**
```bash
docker exec capstone-streaming-db psql -U postgres -d streaming -c \
  "SELECT alert_type, severity, app_id, created_at FROM alerts WHERE severity='critical' ORDER BY created_at DESC LIMIT 5;"
```

**SAY:** "Agent queried PostgreSQL where Kafka consumer writes alerts"

---

### Step 3.5: Demo Query - RAG (2 min)

**SAY:** "Now a question about business rules from the document"

**ASK AGENT:**
```
What's the ROAS threshold for pausing campaigns?
```

**VERIFY:**
```bash
grep -i "roas" docs/business_rules/ameno_business_rules.md | head -5
```

**SAY:** "Agent searched the vector store and found the relevant chunk from our business rules document"

---

### Step 3.6: Demo Query - Combined (1 min)

**SAY:** "Finally, a complex query combining all sources"

**ASK AGENT:**
```
Which apps are losing money based on our business rules?
```

**SAY:** "Agent used Snowflake for metrics, RAG for thresholds, and combined them to identify underperforming apps"

---

## Phase 4: Extra Features & Q&A (10 min)

### Step 4.1: Show Incremental Strategy (2 min)

**SAY:** "Our dbt models use incremental materialization"

**EXECUTE:**
```bash
grep -A5 "is_incremental" my_dbt_project/models/02_intermediate/int_app_daily_metrics.sql
```

**Shows:**
```sql
{% if is_incremental() %}
WHERE date > (SELECT MAX(date) FROM {{ this }})
{% endif %}
```

**SAY:** "Only new dates are processed, not the full table rebuild"

---

### Step 4.2: Show dbt Tests (2 min)

**SAY:** "We have 26 data quality tests"

**EXECUTE:**
```bash
cd my_dbt_project && dbt test --select "stg_admob_capstone" 2>&1 | tail -20
```

**SAY:** "Tests check not_null, unique constraints on key columns"

---

### Step 4.3: Q&A Preparation (1 min)

**Common questions and answers:**

| Question | Answer |
|----------|--------|
| "Why FAISS not Pinecone?" | Free, local, no API needed. Works for small docs. |
| "Why delete-insert?" | Idempotent. Can re-run safely. |
| "Why D0 ROAS?" | 70-80% of lifetime revenue comes on install day |
| "What if API fails?" | CSV backup saved locally before Snowflake load |

---

## Emergency Recovery Commands

### If table dropped:
```sql
UNDROP TABLE DB_T34.RAW_CAPSTONE.ADMOB_DAILY;
```

### If data looks wrong:
```sql
-- Restore from 5 minutes ago
CREATE OR REPLACE TABLE DB_T34.RAW_CAPSTONE.ADMOB_DAILY
  CLONE DB_T34.RAW_CAPSTONE.ADMOB_DAILY AT(OFFSET => -300);
```

### If Docker down:
```bash
cd kafka && docker-compose down && docker-compose up -d && cd ..
cd airflow && docker-compose down && docker-compose up -d && cd ..
```

### If agent fails:
```bash
# Check API key
cat .env | grep OPENAI

# Test Snowflake connection
uv run python -c "from scripts.utils.snowflake_client import get_snowflake_client; c = get_snowflake_client(); c.connect(); print('OK')"
```

---

## Quick Command Reference

```bash
# === PRE-DEMO ===
cd kafka && docker-compose up -d && cd ../airflow && docker-compose up -d && cd ..
uv run python kafka/producer.py --batch 20 --interval 0

# === PHASE 1: STREAMING ===
uv run python kafka/producer.py --batch 5 --interval 2
docker exec capstone-streaming-db psql -U postgres -d streaming -c "SELECT * FROM alerts ORDER BY created_at DESC LIMIT 5;"

# === PHASE 2: BATCH ===
uv run python scripts/collect_admob_capstone.py --days 1
uv run python scripts/collect_adjust_capstone.py --days 1
# Airflow: http://localhost:8080 → Trigger dbt_pipeline

# === PHASE 3: AGENT ===
uv run streamlit run agent/app.py
# Questions: "total revenue?", "critical alerts?", "ROAS threshold?"

# === VERIFY ===
gh run list --limit 1
docker ps | grep -E "capstone|airflow"
```

---

## Timing Checklist

| Phase | Time | Checkpoint |
|-------|------|------------|
| Pre-demo | -10 min | Docker running, alerts generated |
| Phase 1 | 0-5 min | CI triggered, Kafka demo done |
| Phase 2 | 5-10 min | Collection done, Airflow triggered |
| Phase 3 | 10-20 min | All 3 agent queries demoed |
| Phase 4 | 20-30 min | Q&A, wrap up |
