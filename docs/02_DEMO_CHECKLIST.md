# Demo Checklist (30 Minutes)

**Goal:** Prove every `#live-demo` requirement with BEFORE/AFTER evidence.
**Last Verified:** 2026-01-24 12:51 (ALL PASS)

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

**Verify:**
```bash
docker ps | grep -E "capstone|airflow" | wc -l
```
→ Should be **5**

---

### Step 2: Reset to Jan 22 State (CRITICAL for "new data" proof)

```bash
cd ~/code_personal/fa-c002-lab

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

**Verify (run from ~/code_personal/fa-c002-lab):**
```bash
uv run python -c "
from scripts.utils.snowflake_client import get_snowflake_client
client = get_snowflake_client(schema='RAW_CAPSTONE')
conn = client.connect()
cursor = conn.cursor()
cursor.execute('SELECT MAX(DATE) FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY')
print(f'RAW ADMOB MAX(DATE): {cursor.fetchone()[0]}')
cursor.execute('SELECT MAX(DATE) FROM DB_T34.ANALYTICS.DIM_DATES')
print(f'ANALYTICS DIM_DATES MAX(DATE): {cursor.fetchone()[0]}')
client.close()
"
```
→ Should show **20260122** and **2026-01-22**

---

### Step 3: Reset Alerts Table

```bash
cd ~/code_personal/fa-c002-lab

docker exec capstone-postgres psql -U capstone -d streaming -c "
DROP TABLE IF EXISTS alerts;
CREATE TABLE alerts (
    id UUID PRIMARY KEY, timestamp TIMESTAMP NOT NULL,
    alert_type VARCHAR(50) NOT NULL, severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL, region VARCHAR(10), value NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);"

# Kill any existing consumer, then start fresh
pkill -f "kafka/consumer.py" 2>/dev/null || true
uv run python kafka/consumer.py &
sleep 5

# Generate initial alerts
uv run python kafka/producer.py --batch 20 --interval 0
```

**Verify:**
```bash
docker exec capstone-postgres psql -U capstone -d streaming -c "SELECT COUNT(*) FROM alerts;"
```
→ Should show **~20** alerts

---

### Step 4: Clean Git State

```bash
cd ~/code_personal/fa-c002-lab

# Check if dim_dates.sql has demo comments
grep "^-- demo" my_dbt_project/models/03_mart/dim_dates.sql || echo "Clean"

# If not clean, remove demo comments
cd my_dbt_project/models/03_mart
grep -v "^-- demo" dim_dates.sql > temp.sql && mv temp.sql dim_dates.sql
cd ../../..
```

---

### Pre-Demo Checklist

- [ ] 5 Docker containers running
- [ ] RAW latest date = 20260122 (Jan 22)
- [ ] ANALYTICS latest date = 2026-01-22
- [ ] Consumer running, ~20 alerts in PostgreSQL
- [ ] dim_dates.sql is clean (no demo comments)

---

## PHASE 1: Real-time Pipeline (5 min)

### 1.1 Trigger CI/CD (1 min)

```bash
cd ~/code_personal/fa-c002-lab
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
cd ~/code_personal/fa-c002-lab
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
# Get latest run
gh run list --limit 1

# Get run ID from above, then check log (replace ID)
gh run view <run-id> --log 2>&1 | grep -E "PASS|Completed|sqlfluff|All Finished" | tail -10
```

**SAY:** "SQLFluff passed. 26 dbt tests passed."

---

## PHASE 2: Batch Pipeline via Airflow (5 min)

**KEY POINT:** Airflow orchestrates the FULL pipeline (5 tasks):
```
collect_admob → collect_adjust → dbt_debug → dbt_run → dbt_test
```

### 2.1 Show BEFORE State (1 min)

```bash
cd ~/code_personal/fa-c002-lab
uv run python -c "
from scripts.utils.snowflake_client import get_snowflake_client
client = get_snowflake_client(schema='RAW_CAPSTONE')
conn = client.connect()
cursor = conn.cursor()

print('=== BEFORE STATE ===')
print()
print('RAW LAYER:')
cursor.execute('SELECT COUNT(*), MAX(DATE) FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY')
row = cursor.fetchone()
print(f'  ADMOB_DAILY: {row[0]:,} rows, max date: {row[1]}')

cursor.execute('SELECT COUNT(*), MAX(DAY) FROM DB_T34.RAW_CAPSTONE.ADJUST_DAILY')
row = cursor.fetchone()
print(f'  ADJUST_DAILY: {row[0]:,} rows, max date: {row[1]}')

print()
print('ANALYTICS LAYER:')
cursor.execute('SELECT MAX(DATE) FROM DB_T34.ANALYTICS.DIM_DATES')
print(f'  DIM_DATES max date: {cursor.fetchone()[0]}')

cursor.execute('''
SELECT COUNT(*), MAX(d.DATE)
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY
''')
row = cursor.fetchone()
print(f'  FCT rows: {row[0]:,}, max date: {row[1]}')

client.close()
"
```

**SAY:** "Current state: RAW and ANALYTICS both at **Jan 22**. No Jan 23 data yet."

---

### 2.2 Trigger Full Pipeline via Airflow (3 min)

**Trigger the 5-task pipeline:**
```bash
docker exec airflow-webserver airflow dags unpause capstone_dbt_pipeline
docker exec airflow-webserver airflow dags trigger capstone_dbt_pipeline
```

**SAY:** "Airflow is now running 5 tasks: collect_admob, collect_adjust (API calls), then dbt_debug, dbt_run, dbt_test."

**Wait and check status (~90s for full pipeline):**
```bash
sleep 90
docker exec airflow-webserver airflow tasks states-for-dag-run capstone_dbt_pipeline $(docker exec airflow-webserver airflow dags list-runs -d capstone_dbt_pipeline -o plain | head -1 | awk '{print $2}')
```

**Expected output - ALL 5 TASKS SUCCESS:**
```
collect_admob  | success
collect_adjust | success
dbt_debug      | success
dbt_run        | success
dbt_test       | success
```

---

### 2.3 Verify AFTER State (1 min)

```bash
cd ~/code_personal/fa-c002-lab
uv run python -c "
from scripts.utils.snowflake_client import get_snowflake_client
client = get_snowflake_client(schema='RAW_CAPSTONE')
conn = client.connect()
cursor = conn.cursor()

print('=== AFTER STATE ===')
print()
print('RAW LAYER:')
cursor.execute('SELECT COUNT(*), MAX(DATE) FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY')
row = cursor.fetchone()
print(f'  ADMOB_DAILY: {row[0]:,} rows, max date: {row[1]}')

cursor.execute('SELECT COUNT(*), MAX(DAY) FROM DB_T34.RAW_CAPSTONE.ADJUST_DAILY')
row = cursor.fetchone()
print(f'  ADJUST_DAILY: {row[0]:,} rows, max date: {row[1]}')

print()
print('ANALYTICS LAYER:')
cursor.execute('SELECT MAX(DATE) FROM DB_T34.ANALYTICS.DIM_DATES')
print(f'  DIM_DATES max date: {cursor.fetchone()[0]}')

cursor.execute('''
SELECT COUNT(*), MAX(d.DATE)
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY
''')
row = cursor.fetchone()
print(f'  FCT rows: {row[0]:,}, max date: {row[1]}')

client.close()
"
```

**SAY:** "Airflow orchestrated the FULL pipeline. Both RAW and ANALYTICS now have **Jan 23** data. Row counts increased."

---

## PHASE 3: AI Agent & RAG (10 min)

### 3.1 Show RAG Document (1 min)

```bash
head -50 ~/code_personal/fa-c002-lab/docs/business_rules/ameno_business_rules.md
```

**SAY:** "Business rules doc with ROAS thresholds. Chunked and embedded in FAISS vector store."

---

### 3.2 Start Agent (1 min)

```bash
cd ~/code_personal/fa-c002-lab
pkill -f streamlit 2>/dev/null || true
uv run streamlit run agent/app.py &
sleep 3
open http://localhost:8501
```

---

### 3.3 Demo: Batch Data Query (2 min)

**ASK AGENT (in Streamlit UI or CLI):**
```
What's our total revenue for the latest date?
```

**CLI Alternative:**
```bash
cd ~/code_personal/fa-c002-lab
uv run python -m agent.agent -q "What's our total revenue for the latest date?"
```

**VERIFY in terminal:**
```bash
uv run python -c "
from scripts.utils.snowflake_client import get_snowflake_client
client = get_snowflake_client(schema='ANALYTICS')
conn = client.connect()
cursor = conn.cursor()
cursor.execute('''
SELECT SUM(f.AD_REVENUE) as total
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY
WHERE d.DATE = (SELECT MAX(DATE) FROM DB_T34.ANALYTICS.DIM_DATES)
''')
print(f'Verified total revenue: \${cursor.fetchone()[0]:,.2f}')
client.close()
"
```

**SAY:** "Agent queried Snowflake. Numbers match."

---

### 3.4 Demo: Real-time Data Query (2 min)

**ASK AGENT:**
```
Show me recent critical alerts
```

**CLI Alternative:**
```bash
cd ~/code_personal/fa-c002-lab
uv run python -m agent.agent -q "Show me recent critical alerts"
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

**CLI Alternative:**
```bash
cd ~/code_personal/fa-c002-lab
uv run python -m agent.agent -q "What is the ROAS threshold for scaling campaigns?"
```

**VERIFY:**
```bash
grep -A 5 "ROAS Thresholds" ~/code_personal/fa-c002-lab/docs/business_rules/ameno_business_rules.md
```

**SAY:** "Agent searched vector store. Found business rules - 80% threshold."

---

### 3.6 Demo: Combined Query + Memory (2 min)

**ASK AGENT (tests combined sources):**
```
Based on our thresholds, which apps from yesterday are losing money?
```

**CLI Alternative:**
```bash
cd ~/code_personal/fa-c002-lab
uv run python -m agent.agent -q "Based on our thresholds, which apps from yesterday are losing money?"
```

**SAY:** "Agent combined: Snowflake metrics + RAG thresholds. Shows apps with D0 ROAS < 80%."

**FOLLOW-UP (tests conversation memory - USE STREAMLIT UI):**
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
grep -A 3 "is_incremental" ~/code_personal/fa-c002-lab/my_dbt_project/models/02_intermediate/int_app_daily_metrics.sql
```

### Show dbt Tests

```bash
cd ~/code_personal/fa-c002-lab/my_dbt_project && dbt test --select "stg_admob_capstone" 2>&1 | tail -10
```

---

## EMERGENCY FIXES

**Kafka broken:**
```bash
cd ~/code_personal/fa-c002-lab
cd kafka && docker-compose down -v && docker-compose up -d && cd ..
```

**Airflow broken:**
```bash
cd ~/code_personal/fa-c002-lab
cd airflow && docker-compose down -v && docker-compose up -d && cd ..
```

**Agent won't start:**
```bash
pkill -f streamlit && cd ~/code_personal/fa-c002-lab && uv run streamlit run agent/app.py
```

**dbt fails:**
```bash
cd ~/code_personal/fa-c002-lab/my_dbt_project && dbt clean && dbt deps && dbt build
```

---

## VERIFIED RESULTS (2026-01-24 13:24)

| Metric | BEFORE | AFTER |
|--------|--------|-------|
| RAW_CAPSTONE.ADMOB_DAILY rows | 109,594 | 113,412 |
| RAW_CAPSTONE.ADMOB_DAILY max date | 20260122 | 20260123 |
| RAW_CAPSTONE.ADJUST_DAILY rows | 122,895 | 127,251 |
| RAW_CAPSTONE.ADJUST_DAILY max date | 2026-01-22 | 2026-01-23 |
| ANALYTICS.FCT rows | 140,546 | 145,503 |
| ANALYTICS max date | 2026-01-22 | 2026-01-23 |
| PostgreSQL alerts | ~20 | ~25+ |

**Airflow Pipeline Tasks (all success):**
- collect_admob (15s)
- collect_adjust (15s)
- dbt_debug (4s)
- dbt_run (21s)
- dbt_test (2s)

---

## GRADING CHECKLIST

| Requirement | Demo Proof |
|-------------|------------|
| ✅ Batch data source | AdMob + Adjust APIs → Snowflake RAW |
| ✅ Streaming < 5 min | Kafka timestamps show < 1s |
| ✅ Airflow 3+ tasks | **5 tasks**: collect_admob, collect_adjust, dbt_debug, dbt_run, dbt_test |
| ✅ `#live-demo` NEW data | BEFORE/AFTER row count + dates |
| ✅ Star schema | dim_apps, dim_dates, fct_* |
| ✅ dbt incremental | Row count increase, no duplicates |
| ✅ dbt test | 26 tests pass |
| ✅ `#live-demo` dbt via Airflow | Trigger + all 5 tasks success |
| ✅ CI/CD 2 checks | SQLFluff + dbt test |
| ✅ README + Architecture | README.md exists |
| ✅ Chatbot with memory | Multi-turn conversation |
| ✅ RAG documents | Business rules query |
| ✅ Batch data query | Snowflake revenue |
| ✅ Real-time query | PostgreSQL alerts |
| ✅ Combined query | Metrics + thresholds |
