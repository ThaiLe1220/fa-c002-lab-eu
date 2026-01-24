# Demo Checklist - Execute From Scratch

Safe, idempotent commands. Can retry any step without breaking things.

---

## BEFORE DEMO (Run This First)

### Step 0: Go to Project Directory

```bash
cd ~/code_personal/fa-c002-lab
```

---

### Step 1: Reset & Start Docker (Safe to retry)

```bash
# Stop everything first (safe even if not running)
cd kafka && docker-compose down 2>/dev/null; cd ..
cd airflow && docker-compose down 2>/dev/null; cd ..

# Start fresh
cd kafka && docker-compose up -d && cd ..
cd airflow && docker-compose up -d && cd ..

# Wait 30 seconds for services to initialize
sleep 30
```

**VERIFY:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "capstone|airflow"
```

**Expected:** 5 containers (capstone-kafka, capstone-postgres, airflow-webserver, airflow-scheduler, airflow-postgres)

**If fails:** Run the stop/start commands again. Docker is idempotent.

---

### Step 2: Reset Alerts Table (Safe to retry)

```bash
# Drop and recreate alerts table (clean slate)
docker exec capstone-postgres psql -U capstone -d streaming -c "
DROP TABLE IF EXISTS alerts;
CREATE TABLE alerts (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    region VARCHAR(10),
    value NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity);
"
```

**VERIFY:**
```bash
docker exec capstone-postgres psql -U capstone -d streaming -c "SELECT COUNT(*) FROM alerts;"
```

**Expected:** count = 0

---

### Step 3: Start Kafka Consumer (Must run before producer)

```bash
# Start consumer in background (reads Kafka, writes to PostgreSQL)
uv run python kafka/consumer.py &

# Wait for consumer to connect
sleep 5
```

**VERIFY:**
```bash
ps aux | grep "kafka/consumer" | grep -v grep
```

**Expected:** Shows consumer process running

---

### Step 4: Generate Initial Alerts (Safe to retry - append only)

```bash
uv run python kafka/producer.py --batch 30 --interval 0
```

**VERIFY:**
```bash
docker exec capstone-postgres psql -U capstone -d streaming -c "SELECT COUNT(*) FROM alerts;"
```

**Expected:** count = 30

**If fails:** Check consumer is running, then run producer again.

---

### Step 5: Verify Snowflake Connection (Read-only, safe)

```bash
uv run python -c "
from scripts.utils.snowflake_client import get_snowflake_client
client = get_snowflake_client(schema='RAW_CAPSTONE')
conn = client.connect()
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM ADMOB_DAILY')
print(f'ADMOB_DAILY rows: {cursor.fetchone()[0]}')
cursor.execute('SELECT MAX(DATE) FROM ADMOB_DAILY')
print(f'Latest date: {cursor.fetchone()[0]}')
client.close()
print('Snowflake OK')
"
```

**Expected:** Shows row count and latest date

---

### Step 6: Verify Agent Works (Read-only, safe)

```bash
uv run python -m agent.agent -q "What is 2+2?" 2>/dev/null | tail -5
```

**Expected:** Agent responds (tests OpenAI API key)

---

## Pre-Demo Checklist

Before starting demo, confirm:
- [ ] 5 Docker containers running
- [ ] Consumer process running
- [ ] 30 alerts in PostgreSQL
- [ ] Snowflake connection works
- [ ] Agent responds

---

# DEMO EXECUTION (30 minutes)

---

## Phase 1: Real-time Pipeline (5 min)

### 1.1 Trigger CI/CD (1 min)

**SAY:** "First, I'll trigger CI/CD to run in background"

**Option A: Manual trigger from GitHub UI (easiest)**
1. Go to https://github.com/ThaiLe1220/fa-c002-lab-eu/actions
2. Click "dbt CI Pipeline"
3. Click "Run workflow" → "Run workflow"

**Option B: CLI trigger**
```bash
gh workflow run dbt_ci.yml
```

**VERIFY:**
```bash
gh run list --limit 1
```

**Expected:** Shows "in_progress" or "completed success"

**SAY:** "CI runs SQLFluff and dbt tests. Let's continue."

**If fails:** Just show last successful run: `gh run view --log | tail -20`

---

### 1.2 Kafka Demo (3 min)

**SAY:** "Now real-time streaming with Kafka"

**EXECUTE:**
```bash
uv run python kafka/producer.py --batch 5 --interval 2
```

**Shows:** 5 alerts produced with 2-second gaps

**VERIFY:**
```bash
docker exec capstone-postgres psql -U capstone -d streaming -c \
  "SELECT alert_type, severity, region, created_at FROM alerts ORDER BY created_at DESC LIMIT 5;"
```

**SAY:** "See the timestamps? Data landed in PostgreSQL via Kafka consumer."

**If fails:**
```bash
# Restart Kafka stack
cd kafka && docker-compose restart && cd ..
sleep 10
# Try producer again
uv run python kafka/producer.py --batch 5 --interval 0
```

---

### 1.3 CI Results (1 min)

**EXECUTE:**
```bash
gh run list --limit 1
```

**If completed:**
```bash
gh run view --log 2>&1 | grep -E "PASS|Completed" | tail -5
```

**SAY:** "26 dbt tests passed. SQLFluff checked code quality."

**If still running:** "CI still running, let's check later" (move on)

---

## Phase 2: Batch Pipeline (5 min)

### 2.1 Show Current Data (1 min)

**SAY:** "Let me show current data state in Snowflake"

**EXECUTE (in Snowflake UI):**
```sql
SELECT
    MAX(DATE) as latest_date,
    COUNT(*) as total_rows,
    MAX(LOADED_AT) as last_loaded
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY;
```

**Write down the values** (to compare after collection)

---

### 2.2 Run Batch Collection (2 min)

**SAY:** "Now I'll collect yesterday's data from APIs"

**EXECUTE:**
```bash
# Collect yesterday only (idempotent - delete then insert)
uv run python scripts/collect_admob_capstone.py --days 1
```

**Shows:**
```
Deleting existing data for 2026-01-23...
Loading X rows to RAW_CAPSTONE.ADMOB_DAILY...
✓ Loaded X rows
```

**EXECUTE:**
```bash
uv run python scripts/collect_adjust_capstone.py --days 1
```

**VERIFY (in Snowflake UI):**
```sql
-- Show fresh data with new timestamp
SELECT RAW_RECORD_ID, DATE, APP_STORE_ID, LOADED_AT
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY
WHERE LOADED_AT > DATEADD(minute, -5, CURRENT_TIMESTAMP())
ORDER BY LOADED_AT DESC
LIMIT 5;
```

**SAY:** "See LOADED_AT? Fresh data from API. Delete-insert ensures idempotency."

**If API fails:** "API occasionally times out. Data was collected earlier today." (show existing data)

---

### 2.3 Run dbt via Airflow (2 min)

**SAY:** "Now Airflow orchestrates dbt transformation"

**EXECUTE:** Open http://localhost:8080
- Login: admin / admin
- Find DAG: `dbt_pipeline`
- Click play button → "Trigger DAG"

**While waiting, show (in Snowflake UI):**
```sql
SELECT TABLE_NAME, ROW_COUNT
FROM DB_T34.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'ANALYTICS'
ORDER BY TABLE_NAME;
```

**SAY:** "dbt transforms raw → staging → intermediate → mart"

**After Airflow completes (or while running), show:**
```sql
SELECT
    DATE,
    APP_STORE_ID,
    AD_REVENUE,
    NETWORK_COST,
    ROUND(AD_REVENUE_D0 / NULLIF(NETWORK_COST, 0) * 100, 2) as D0_ROAS_PCT
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE
WHERE DATE = CURRENT_DATE() - 1
ORDER BY AD_REVENUE DESC
LIMIT 5;
```

**If Airflow fails:** Run dbt directly:
```bash
cd my_dbt_project && dbt build --select "stg_admob_capstone stg_adjust_capstone int_app_daily_metrics fct_app_daily_performance" && cd ..
```

---

## Phase 3: AI Agent & RAG (10 min)

### 3.1 Show RAG Source (2 min)

**SAY:** "Agent uses RAG for business rules"

**EXECUTE:**
```bash
head -40 docs/business_rules/ameno_business_rules.md
```

**SAY:** "This document has ROAS thresholds, CPI benchmarks. RAG chunks and embeds it."

**Optional - show chunking:**
```bash
uv run python agent/rag_demo.py
# Press 2 for chunking demo
```

---

### 3.2 Start Agent UI (1 min)

**EXECUTE:**
```bash
uv run streamlit run agent/app.py &
sleep 3
open http://localhost:8501
```

**If port busy:**
```bash
# Kill existing streamlit
pkill -f streamlit
uv run streamlit run agent/app.py &
```

---

### 3.3 Query: Batch Data (2 min)

**ASK AGENT:**
```
What's our total revenue yesterday?
```

**VERIFY (in Snowflake):**
```sql
SELECT SUM(AD_REVENUE) FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE
WHERE DATE = CURRENT_DATE() - 1;
```

**SAY:** "Agent queried Snowflake. Numbers match."

---

### 3.4 Query: Streaming Data (2 min)

**ASK AGENT:**
```
Show me recent alerts
```

**VERIFY:**
```bash
docker exec capstone-postgres psql -U capstone -d streaming -c \
  "SELECT alert_type, severity, region, created_at FROM alerts ORDER BY created_at DESC LIMIT 5;"
```

**SAY:** "Agent queried PostgreSQL where Kafka writes alerts."

---

### 3.5 Query: RAG (2 min)

**ASK AGENT:**
```
What is the ROAS threshold for campaigns?
```

**VERIFY:**
```bash
grep -i "roas.*threshold\|threshold.*roas\|below.*%" docs/business_rules/ameno_business_rules.md | head -3
```

**SAY:** "Agent searched vector store, found relevant business rules."

---

### 3.6 Query: Combined (1 min)

**ASK AGENT:**
```
Which apps are losing money based on our thresholds?
```

**SAY:** "Agent combined Snowflake metrics + RAG thresholds to identify issues."

---

## Phase 4: Extra & Q&A (10 min)

### 4.1 Show Incremental (2 min)

**EXECUTE:**
```bash
grep -A 5 "is_incremental" my_dbt_project/models/02_intermediate/int_app_daily_metrics.sql
```

**SAY:** "Incremental model - only processes new dates, not full rebuild."

---

### 4.2 Show dbt Tests (2 min)

**EXECUTE:**
```bash
cd my_dbt_project && dbt test --select "stg_admob_capstone" 2>&1 | tail -15 && cd ..
```

**SAY:** "Tests validate not_null, unique constraints. 26 tests total."

---

### 4.3 Q&A Answers

| Question | Answer |
|----------|--------|
| Why FAISS? | Free, local, works offline. Good for small docs. |
| Why delete-insert? | Idempotent. Safe to retry. |
| Why D0 ROAS? | 70-80% of lifetime revenue on install day. |
| API fails? | CSV backup in `data/capstone/`. |
| Table dropped? | `UNDROP TABLE` or Time Travel. |

---

## EMERGENCY COMMANDS

### Docker broken:
```bash
cd kafka && docker-compose down -v && docker-compose up -d && cd ..
cd airflow && docker-compose down -v && docker-compose up -d && cd ..
sleep 30
```

### PostgreSQL alerts missing:
```bash
# Recreate table + generate alerts
docker exec capstone-postgres psql -U capstone -d streaming -c "DROP TABLE IF EXISTS alerts; CREATE TABLE alerts (id UUID PRIMARY KEY, timestamp TIMESTAMP NOT NULL, alert_type VARCHAR(50) NOT NULL, severity VARCHAR(20) NOT NULL, message TEXT NOT NULL, region VARCHAR(10), value NUMERIC(10,2), created_at TIMESTAMP DEFAULT NOW());"
uv run python kafka/producer.py --batch 30 --interval 0
```

### Snowflake table dropped:
```sql
UNDROP TABLE DB_T34.RAW_CAPSTONE.ADMOB_DAILY;
-- Or restore from 5 min ago:
CREATE OR REPLACE TABLE DB_T34.RAW_CAPSTONE.ADMOB_DAILY
CLONE DB_T34.RAW_CAPSTONE.ADMOB_DAILY AT(OFFSET => -300);
```

### Agent won't start:
```bash
# Check API key
grep OPENAI .env

# Kill existing
pkill -f streamlit
pkill -f "agent.agent"

# Restart
uv run streamlit run agent/app.py
```

### dbt fails:
```bash
cd my_dbt_project
dbt clean  # Clear cache
dbt deps   # Reinstall packages
dbt build  # Rebuild
cd ..
```

---

## QUICK COPY-PASTE BLOCK

```bash
# === SETUP (run once before demo) ===
cd ~/code_personal/fa-c002-lab
cd kafka && docker-compose down 2>/dev/null; docker-compose up -d; cd ..
cd airflow && docker-compose down 2>/dev/null; docker-compose up -d; cd ..
sleep 30
docker exec capstone-postgres psql -U capstone -d streaming -c "DROP TABLE IF EXISTS alerts; CREATE TABLE alerts (id UUID PRIMARY KEY, timestamp TIMESTAMP NOT NULL, alert_type VARCHAR(50) NOT NULL, severity VARCHAR(20) NOT NULL, message TEXT NOT NULL, region VARCHAR(10), value NUMERIC(10,2), created_at TIMESTAMP DEFAULT NOW()); CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);"
uv run python kafka/consumer.py &  # Start consumer first!
sleep 5
uv run python kafka/producer.py --batch 30 --interval 0

# === VERIFY SETUP ===
docker ps | grep -E "capstone|airflow" | wc -l  # Should be 5
docker exec capstone-postgres psql -U capstone -d streaming -c "SELECT COUNT(*) FROM alerts;"  # Should be 30

# === PHASE 1: STREAMING ===
uv run python kafka/producer.py --batch 5 --interval 2
docker exec capstone-postgres psql -U capstone -d streaming -c "SELECT alert_type, severity, region, created_at FROM alerts ORDER BY created_at DESC LIMIT 5;"

# === PHASE 2: BATCH ===
uv run python scripts/collect_admob_capstone.py --days 1
uv run python scripts/collect_adjust_capstone.py --days 1

# === PHASE 3: AGENT ===
uv run streamlit run agent/app.py &
# Questions: "total revenue yesterday?", "recent alerts?", "ROAS threshold?"
```
