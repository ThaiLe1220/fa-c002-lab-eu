# Demo Flow Guide

**Demo Day Script for FA-C002 Capstone**

**Date:** January 24, 2026
**Duration:** 30 minutes
**Presenter:** Thai Le

---

## Pre-Demo Checklist (30 min before)

### 1. Start Services

```bash
# Navigate to project
cd /Users/lehongthai/code_personal/fa-c002-lab

# Start Kafka + PostgreSQL (streaming)
cd kafka && docker-compose up -d
cd ..

# Start Airflow
cd airflow && docker-compose up -d
cd ..

# Verify all healthy
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected output:
```
NAMES               STATUS
capstone-kafka      Up X minutes (healthy)
capstone-postgres   Up X minutes (healthy)
airflow-webserver   Up X minutes (healthy)
airflow-scheduler   Up X minutes
airflow-postgres    Up X minutes (healthy)
```

### 2. Generate Fresh Streaming Data

```bash
# Generate 30 alerts quickly
uv run python kafka/producer.py --batch 30 --interval 0

# Consume to PostgreSQL
uv run python -c "
from kafka import KafkaConsumer
import psycopg2, json
conn = psycopg2.connect(host='localhost', port=5433, database='streaming', user='capstone', password='capstone123')
consumer = KafkaConsumer('alerts', bootstrap_servers='localhost:29092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest', group_id='demo-consumer', consumer_timeout_ms=15000)
count = 0
for msg in consumer:
    cur = conn.cursor()
    cur.execute('INSERT INTO alerts (id,timestamp,alert_type,severity,message,region,value) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING',
        (msg.value['id'],msg.value['timestamp'],msg.value['alert_type'],msg.value['severity'],msg.value['message'],msg.value.get('region'),msg.value.get('value')))
    conn.commit()
    count += 1
print(f'Consumed {count} alerts')
"
```

### 3. Verify Data

```bash
# Check streaming alerts count
uv run python -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5433, database='streaming', user='capstone', password='capstone123')
cur = conn.cursor()
cur.execute('SELECT COUNT(*), MAX(created_at) FROM alerts')
count, latest = cur.fetchone()
print(f'Alerts: {count} | Latest: {latest}')
cur.execute('SELECT severity, COUNT(*) FROM alerts GROUP BY severity')
for row in cur.fetchall(): print(f'  {row[0]}: {row[1]}')
"

# Check Snowflake data (via agent)
uv run python -m agent.agent -q "How many rows in the fact table?"
```

### 4. Open Browser Tabs

- [ ] Airflow UI: http://localhost:8080 (admin/admin)
- [ ] Terminal for agent queries
- [ ] Terminal for Kafka producer (live streaming)

---

## Demo Script (30 minutes)

### Part 1: Real-Time Pipeline (5 min)

**Story:** "First, let me show you our real-time monitoring system."

#### 1.1 Show Kafka Architecture
```
"We have a streaming pipeline that monitors app performance in real-time:
Producer → Kafka → Consumer → PostgreSQL → Agent queries"
```

#### 1.2 Start Live Producer
```bash
# In visible terminal
uv run python kafka/producer.py
```

**Show:** Alerts appearing every 10 seconds with severity colors.

#### 1.3 Query via Agent
```bash
uv run python -m agent.agent -q "Show me any critical alerts"
```

**Talking Point:**
> "The agent can query real-time alerts. Notice how it returns the most recent critical events - spend spikes, ROAS drops, etc."

---

### Part 2: Batch Pipeline - Airflow (5 min)

**Story:** "Now let's look at our batch data pipeline orchestrated by Airflow."

#### 2.1 Show Airflow DAG
- Open http://localhost:8080
- Navigate to `capstone_dbt_pipeline` DAG
- Show the 3 tasks: `dbt_debug` → `dbt_run` → `dbt_test`

**Talking Point:**
> "Our dbt transformations run daily at 2 AM. The pipeline has 3 tasks: verify connection, build models, run tests."

#### 2.2 Trigger DAG (Optional)
- Click "Trigger DAG" button
- Show tasks executing in sequence

**Talking Point:**
> "Each task depends on the previous one. If debug fails, we don't waste time running models."

---

### Part 3: AI Agent - Core Queries (10 min)

**Story:** "This is the main value - Chi Linh can ask questions in plain English."

#### 3.1 Revenue Analysis
```bash
uv run python -m agent.agent -q "What's our total ad revenue this week?"
```

**Talking Point:**
> "The agent translates natural language to SQL and queries our Snowflake data warehouse."

#### 3.2 App Performance
```bash
uv run python -m agent.agent -q "Which apps have the highest D0 ROAS?"
```

#### 3.3 Trend Analysis
```bash
uv run python -m agent.agent -q "Compare last week's revenue to this week"
```

#### 3.4 Drill Down
```bash
uv run python -m agent.agent -q "Break down revenue by country for our top app"
```

**Talking Point:**
> "Notice the agent understands business context - D0 ROAS, LTV metrics, attribution data."

#### 3.5 Combined Query (Batch + Streaming)
```bash
uv run python -m agent.agent -q "What's our top performing app and are there any alerts for it?"
```

**Talking Point:**
> "The agent can combine batch analytics with real-time alerts in a single response."

---

### Part 4: Extra Features (5 min)

#### 4.1 dbt Macros
```bash
cd my_dbt_project
cat macros/calculate_ctr.sql
```

**Talking Point:**
> "We use custom macros for consistent metric calculations across all models."

#### 4.2 Data Quality
```bash
dbt test --select fct_app_daily_performance
```

**Talking Point:**
> "Automated tests ensure data quality - null checks, range validations, freshness."

#### 4.3 Business Context Prompts
```bash
cat agent/prompts.py | head -50
```

**Talking Point:**
> "The system prompt includes Ameno's specific thresholds and business rules."

---

### Part 5: Q&A (5 min)

**Prepared answers for common questions:**

**Q: How does the agent know which tool to use?**
> "LangGraph's tool binding lets the LLM see all available tools and their descriptions. It decides based on the question context."

**Q: Is the data real?**
> "Batch data is real - actual AdMob and Adjust data from our apps. Streaming alerts are simulated for demo purposes."

**Q: How long to add a new metric?**
> "Add a dbt macro, update the fact table, update the agent prompt - usually under an hour."

**Q: What about data freshness?**
> "Batch data is T-1 (yesterday). Streaming alerts are real-time with ~1 minute latency."

---

## Demo Commands Quick Reference

```bash
# Agent queries
uv run python -m agent.agent -q "QUERY HERE"

# Interactive mode
uv run python -m agent.agent --interactive

# Streamlit UI
uv run streamlit run agent/app.py

# Generate alerts
uv run python kafka/producer.py --batch 10 --interval 0

# Check services
docker ps --format "table {{.Names}}\t{{.Status}}"

# dbt commands
cd my_dbt_project && dbt build
cd my_dbt_project && dbt test
```

---

## Backup Plans

### If Kafka won't start:
- Skip streaming demo
- Show alerts already in PostgreSQL
- Focus on batch queries

### If Airflow is slow:
- Show DAG structure without triggering
- Explain it runs on schedule

### If Agent errors:
- Check OpenAI API key
- Restart with: `export OPENAI_API_KEY=xxx`
- Use pre-prepared screenshots

### If Snowflake is slow:
- Have cached query results ready
- Focus on architecture explanation

---

## Key Talking Points

1. **Three Systems, One Agent**
   - Batch (Snowflake) for historical analysis
   - Streaming (Kafka) for real-time alerts
   - RAG (docs) for business rules

2. **Business Value**
   - Chi Linh can self-serve analytics
   - No SQL knowledge required
   - Answers in seconds, not hours

3. **Production Ready**
   - Idempotent data loading
   - Automated tests
   - Docker-based infrastructure

4. **Extensible**
   - Add new metrics via dbt macros
   - Add new documents via RAG
   - Add new alert types easily

---

## Post-Demo

- [ ] Stop Kafka producer
- [ ] Save any interesting queries
- [ ] Note questions for improvement
- [ ] Celebrate!
