# Demo Flow Guide

**Demo Day Script for FA-C002 Capstone**

**Based on:** Official Capstone Demo Guide (capstone_demo_guide.md)

**Date:** January 24, 2026
**Duration:** 30 minutes
**Presenter:** Thai Le

---

## Official Demo Timeline

```
┌─────────────────────────────────────────────────────────────────┐
│                       30-MINUTE DEMO                            │
├─────────────────────────────────────────────────────────────────┤
│ Phase 1: Real-time Pipeline (5 min)                             │
│ ├─ CI/CD Initiation (1 min)          ← START CI JOB FIRST      │
│ ├─ Data Flow Demo (3 min)            ← Kafka producer/consumer  │
│ └─ CI/CD Results (1 min)             ← Return to show results   │
├─────────────────────────────────────────────────────────────────┤
│ Phase 2: Batch Pipeline (5 min)                                 │
│ ├─ Airflow Setup (2 min)             ← Start Airflow            │
│ ├─ Data Processing (2 min)           ← Trigger DAG, show dbt    │
│ └─ Results Review (1 min)            ← Show completion          │
├─────────────────────────────────────────────────────────────────┤
│ Phase 3: AI Agent & RAG (10 min)                                │
│ ├─ Document Processing (2 min)       ← PDF chunking/embedding   │
│ ├─ Question Preparation (2 min)      ← Prepare demo questions   │
│ ├─ AI Agent Demo (4 min)             ← Batch + Real-time + PDF  │
│ └─ Complex Queries (2 min)           ← Combined multi-source    │
├─────────────────────────────────────────────────────────────────┤
│ Phase 4: Advanced Features & Q&A (10 min)                       │
│ ├─ Extra Features Demo (5 min)       ← Macros, tests, prompts   │
│ └─ Q&A Session (5 min)               ← Answer trainer questions │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pre-Demo Checklist (30 min before)

### 1. Environment Setup

```bash
# Navigate to project
cd /Users/lehongthai/code_personal/fa-c002-lab

# Start Kafka + PostgreSQL (streaming)
cd kafka && docker-compose up -d
cd ..

# Verify Kafka healthy
docker ps --format "table {{.Names}}\t{{.Status}}" | grep capstone
```

### 2. Generate Fresh Streaming Data

```bash
# Generate 30 alerts quickly
uv run python kafka/producer.py --batch 30 --interval 0

# Consume to PostgreSQL (new consumer group for fresh data)
uv run python -c "
from kafka import KafkaConsumer
import psycopg2, json
conn = psycopg2.connect(host='localhost', port=5433, database='streaming', user='capstone', password='capstone123')
consumer = KafkaConsumer('alerts', bootstrap_servers='localhost:29092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest', group_id='demo-$(date +%s)', consumer_timeout_ms=15000)
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

### 3. Prepare Browser Tabs

- [ ] GitHub Actions page (ready to trigger CI)
- [ ] Airflow UI: http://localhost:8080 (admin/admin)
- [ ] Terminal 1: Kafka producer
- [ ] Terminal 2: Agent queries

### 4. Prepare CLI Commands

Store these in terminal history:
```bash
# CI trigger (if manual)
# Kafka commands
uv run python kafka/producer.py
# Agent queries
uv run python -m agent.agent -q "What's total revenue this week?"
uv run python -m agent.agent -q "Show me critical alerts"
uv run python -m agent.agent -q "What are the business rules for ROAS?"
```

---

## Phase 1: Real-time Pipeline (5 min)

### Step 1.1: CI/CD Initiation (1 min)

**Action:** Start CI job FIRST (it runs in background)

```bash
# Option A: Manual trigger on GitHub Actions page
# Option B: Push a small commit
git commit --allow-empty -m "trigger ci" && git push
```

**Say:** "Let me start our CI/CD pipeline - it will run in the background while we demo other components."

### Step 1.2: Real-time Data Flow (3 min)

**Action:** Show Kafka streaming

```bash
# Terminal 1: Start producer
uv run python kafka/producer.py
```

**Show:** Alerts appearing every 10 seconds with severity colors (🔴🟡🔵)

**Say:** "Our streaming pipeline generates real-time alerts - spend spikes, ROAS drops, etc. These flow through Kafka to PostgreSQL."

**Action:** Query via agent
```bash
uv run python -m agent.agent -q "Show me recent critical alerts"
```

**Say:** "The agent can query this real-time data. Notice the timestamps - this data landed just moments ago."

### Step 1.3: CI/CD Results (1 min)

**Action:** Return to GitHub Actions page

**Show:** CI pipeline results - SQLFluff lint + dbt test

**Say:** "Our CI runs 2 automated checks: SQL linting with SQLFluff and data quality tests with dbt."

---

## Phase 2: Batch Pipeline (5 min)

### Step 2.1: Airflow Setup (2 min)

**Action:** Start Airflow (if not running)
```bash
cd airflow && docker-compose up -d
```

**Action:** Open Airflow UI http://localhost:8080

**Show:** DAG list, navigate to `capstone_dbt_pipeline`

**Say:** "Airflow orchestrates our batch pipeline. This DAG runs daily at 2 AM."

### Step 2.2: Data Processing (2 min)

**Action:** Show DAG structure - 3 tasks

**Say:** "We have 3 tasks: debug verifies Snowflake connection, run builds all dbt models, test runs data quality checks."

**Action:** Trigger DAG (or show recent successful run)

**While waiting, show dbt structure:**
```bash
ls my_dbt_project/models/
# 01_staging, 02_intermediate, 03_mart
```

**Say:** "Our dbt project follows a 3-layer architecture: staging cleans raw data, intermediate joins sources, mart produces analytics tables."

### Step 2.3: Results Review (1 min)

**Show:** Airflow task completion (green)

**Say:** "All tasks completed successfully. The data is now transformed and ready for the AI agent."

---

## Phase 3: AI Agent & RAG (10 min)

### Step 3.1: RAG Pipeline Explanation (3 min)

**Run the RAG demo script:**
```bash
uv run python agent/rag_demo.py
```

This walks through each step interactively. Press Enter between steps.

**Talking Points for Each Step:**

#### Step 1: Load Document
**Say:** "First we load our business rules document. This contains ROAS thresholds, CPI benchmarks, and decision frameworks that Chi Linh uses."

#### Step 2: Chunking
**Say:** "The document is too long for the LLM context. We split it into ~500 character chunks. Notice we split on headers and paragraphs to keep related content together. Overlap of 50 characters ensures we don't lose context at boundaries."

```
Original: 3000 words → 12 chunks of ~500 chars each
```

#### Step 3: Embedding
**Say:** "Each chunk is converted to a vector - a list of 1536 numbers. This is done by OpenAI's embedding model. Similar text produces similar vectors. 'ROAS thresholds' and 'What is ROAS?' will have vectors that are close together."

```
"ROAS > 100% is profitable" → [0.12, -0.45, 0.78, ...]
```

#### Step 4: Similarity Search
**Say:** "When the user asks a question, we embed that question too, then find the chunks with the most similar vectors. This is semantic search - it understands meaning, not just keywords."

```
Query: "What should I do if ROAS drops?"
→ Finds chunks about ROAS thresholds and scaling decisions
```

**Quick visual:**
```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Document │────▶│ Chunking │────▶│ Embedding│────▶│  Vector  │
│          │     │ (split)  │     │ (OpenAI) │     │  Store   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                        │
Query ─────────────────────────────────────────────────▶│
                                                        ▼
                                                 Top K chunks

### Step 3.2: AI Agent Demo - Three Tools (5 min)

**Tool 1: Snowflake (Batch Data)**
```bash
uv run python -m agent.agent -q "What's our total ad revenue this week?"
```
**Say:** "The agent uses query_snowflake to get historical data from our data warehouse."

**Tool 2: Kafka (Real-time Alerts)**
```bash
uv run python -m agent.agent -q "Show me any critical alerts"
```
**Say:** "The agent uses query_realtime_alerts to check the streaming pipeline."

**Tool 3: RAG (Business Rules)**
```bash
uv run python -m agent.agent -q "What are our ROAS thresholds for scaling decisions?"
```
**Say:** "The agent uses search_business_documents to find relevant business rules. This is the RAG tool we just explained."

**Combined Query (Multiple Tools):**
```bash
uv run python -m agent.agent -q "Which apps have D0 ROAS below 80% and what should we do about them?"
```
**Say:** "The agent combines warehouse data with business rules to provide actionable recommendations."

### Step 3.3: Conversation Memory (2 min)

**Action:** Show multi-turn conversation
```bash
uv run python -m agent.agent --interactive
# You: What's our top app by revenue?
# Agent: [answers]
# You: What's its D0 ROAS?
# Agent: [uses context from previous answer]
```

**Say:** "The agent maintains conversation memory - it remembers we were talking about that specific app."

---

## Phase 4: Advanced Features & Q&A (10 min)

### Extra Features Demo (5 min)

#### dbt Macros
```bash
cat my_dbt_project/macros/calculate_ctr.sql
```
**Say:** "Custom macros ensure consistent metric calculations across all models."

#### Data Quality Tests
```bash
cd my_dbt_project && dbt test --select fct_app_daily_performance
```
**Say:** "Automated tests catch data issues before they reach the agent."

#### Business Context Prompts
```bash
head -60 agent/prompts.py
```
**Say:** "The system prompt includes Ameno's specific thresholds and decision frameworks."

### Q&A Session (5 min)

**Prepared answers:**

| Question | Answer |
|----------|--------|
| How does agent choose tools? | LangGraph tool binding - LLM sees tool descriptions and decides |
| Is data real? | Batch = real AdMob/Adjust. Streaming = simulated alerts |
| Data freshness? | Batch = T-1. Streaming = real-time (~1 min latency) |
| Add new metric? | dbt macro + fact table update + prompt update (~1 hour) |

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
