# Demo Checklist

Step-by-step commands with verification for demo day.

---

## Pre-Demo Setup (10 min before)

### 1. Start Services

```bash
# Terminal 1: Start Kafka + PostgreSQL
cd kafka && docker-compose up -d

# Terminal 2: Start Airflow
cd airflow && docker-compose up -d

# Verify containers running
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Expected Output:**
```
NAMES                    STATUS
capstone-kafka           Up
capstone-streaming-db    Up
airflow-webserver        Up
airflow-scheduler        Up
airflow-postgres         Up
```

### 2. Generate Alerts Data

```bash
# Generate 30 alerts (batch mode, instant)
uv run python kafka/producer.py --batch 30 --interval 0
```

**Expected:** "Produced 30 alerts"

### 3. Verify PostgreSQL Has Data

```bash
# Check alerts in PostgreSQL
docker exec capstone-streaming-db psql -U postgres -d streaming -c "SELECT COUNT(*) FROM alerts;"
```

**Expected:** count = 30+

---

## Demo Flow

### Part 1: CI/CD (2 min)

**Show:**
1. Open GitHub Actions: https://github.com/ThaiLe1220/fa-c002-lab-eu/actions
2. Show latest green run
3. Click to show: SQLFluff lint + dbt test (26 tests pass)

**Talking Point:**
> "Every push triggers SQLFluff linting and dbt tests. 26 tests run against Snowflake."

---

### Part 2: Snowflake Data Verification (3 min)

**Verify fresh data exists:**

```sql
-- In Snowflake UI (DB_T34.ANALYTICS)

-- Check latest date
SELECT MAX(date) as latest_date FROM fct_app_daily_performance;
-- Expected: 2026-01-23 (yesterday)

-- Check row counts
SELECT
    (SELECT COUNT(*) FROM fct_app_daily_performance) as fact_rows,
    (SELECT COUNT(*) FROM dim_apps) as apps,
    (SELECT COUNT(*) FROM dim_dates) as dates;
-- Expected: ~16K fact rows, 59 apps, 29 dates

-- Proof: Show specific row with ID + timestamp
SELECT
    date,
    app_store_id,
    total_revenue,
    network_cost,
    d0_roas_pct,
    _loaded_at
FROM fct_app_daily_performance
WHERE date = '2026-01-23'
ORDER BY total_revenue DESC
LIMIT 3;
```

**Talking Point:**
> "Data is fresh - loaded yesterday. We can see revenue, cost, and D0 ROAS for each app."

---

### Part 3: dbt Lineage (2 min)

**Show in Snowflake or dbt docs:**

```
Raw Sources (RAW_CAPSTONE)
    ├── admob_daily
    └── adjust_daily
         ↓
Staging (01_staging)
    ├── stg_admob_capstone
    └── stg_adjust_capstone
         ↓
Intermediate (02_intermediate)
    └── int_app_daily_metrics
         ↓
Mart (03_mart)
    ├── fct_app_daily_performance
    ├── dim_apps
    └── dim_dates
```

**Command to run dbt (if needed):**
```bash
cd my_dbt_project && dbt build --select "stg_admob_capstone stg_adjust_capstone int_app_daily_metrics fct_app_daily_performance"
```

---

### Part 4: Kafka Streaming (3 min)

**Show producer generating alerts:**

```bash
# Generate 5 alerts with 2-second interval (visible)
uv run python kafka/producer.py --batch 5 --interval 2
```

**Verify in PostgreSQL:**

```bash
# Show latest alerts
docker exec capstone-streaming-db psql -U postgres -d streaming -c \
  "SELECT id, alert_type, severity, app_id, created_at FROM alerts ORDER BY created_at DESC LIMIT 5;"
```

**Expected Output:**
```
 id |   alert_type   | severity |         app_id          |       created_at
----+----------------+----------+-------------------------+------------------------
 45 | ROAS_DROP      | critical | com.example.app1        | 2026-01-24 10:30:15
 44 | BUDGET_EXCEED  | warning  | com.example.app2        | 2026-01-24 10:30:13
```

**Talking Point:**
> "Kafka produces alerts in real-time. Consumer writes to PostgreSQL. Agent can query this."

---

### Part 5: Airflow (3 min)

**Open Airflow UI:**
```
http://localhost:8080
Username: admin
Password: admin
```

**Show:**
1. DAG: `dbt_pipeline`
2. Graph view: debug -> run -> test
3. Trigger run manually (or show recent successful run)

**Talking Point:**
> "Airflow orchestrates dbt: debug checks connection, run builds models, test validates data."

---

### Part 6: AI Agent (10 min)

**Start Streamlit UI:**
```bash
uv run streamlit run agent/app.py
```

**Demo Queries (test all 3 tools):**

| Question | Expected Tool | Verification |
|----------|---------------|--------------|
| "What's our total revenue?" | query_snowflake | Shows sum from Snowflake |
| "Show me critical alerts" | query_realtime_alerts | Shows alerts from PostgreSQL |
| "What's the ROAS threshold?" | search_business_documents | Shows business rules from RAG |
| "Which apps are losing money?" | Multiple tools | Combines data + rules |

**CLI Alternative:**
```bash
# Single queries
uv run python -m agent.agent -q "What's our total revenue?"
uv run python -m agent.agent -q "Show me critical alerts"
uv run python -m agent.agent -q "What are ROAS thresholds?"

# Interactive mode
uv run python -m agent.agent --interactive
```

---

### Part 7: RAG Explanation (5 min if asked)

**Run RAG demo:**
```bash
uv run python agent/rag_demo.py
```

**Shows 5 steps:**
1. Load document
2. Chunk into pieces (~500 chars)
3. Embed with OpenAI (1536 dimensions)
4. Search with cosine similarity
5. Full pipeline demo

**Talking Point:**
> "RAG converts text to vectors. Similar questions find similar document chunks."

---

## Incremental Data Proof (if asked)

**Before incremental:**
```sql
SELECT COUNT(*) as before_count, MAX(date) as max_date
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY;
```

**Run collection:**
```bash
python scripts/collect_admob_capstone.py --days 1
```

**After incremental:**
```sql
SELECT COUNT(*) as after_count, MAX(date) as max_date
FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY;

-- Show new rows
SELECT * FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY
WHERE _loaded_at > DATEADD(minute, -5, CURRENT_TIMESTAMP())
ORDER BY _loaded_at DESC LIMIT 5;
```

---

## Emergency Recovery

### If table dropped:
```sql
-- Undrop table (Snowflake Time Travel)
UNDROP TABLE DB_T34.RAW_CAPSTONE.ADMOB_DAILY;

-- Or restore from time travel
CREATE TABLE DB_T34.RAW_CAPSTONE.ADMOB_DAILY CLONE DB_T34.RAW_CAPSTONE.ADMOB_DAILY
  AT(OFFSET => -300);  -- 5 minutes ago
```

### If Kafka/Airflow down:
```bash
# Restart services
cd kafka && docker-compose down && docker-compose up -d
cd airflow && docker-compose down && docker-compose up -d
```

### If agent fails:
```bash
# Check API key
cat .env | grep OPENAI

# Check Snowflake connection
uv run python -c "from scripts.utils.snowflake_client import get_snowflake_client; c = get_snowflake_client(); c.connect(); print('OK')"
```

---

## Quick Reference Commands

```bash
# Start everything
cd kafka && docker-compose up -d && cd ../airflow && docker-compose up -d && cd ..

# Generate alerts
uv run python kafka/producer.py --batch 30 --interval 0

# Run agent
uv run streamlit run agent/app.py

# Run dbt
cd my_dbt_project && dbt build

# Check CI
gh run list --limit 3
```
