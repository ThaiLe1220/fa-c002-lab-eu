# Current Step: Phase 3+4 - Core Checkboxes + Extra Features

**Updated:** 2026-01-24
**Demo:** 2026-01-24
**Status:** EXECUTING PRIORITY PLAN

---

## Quick Status

| Phase | Status | Points |
|-------|--------|--------|
| Phase 0-2 | DONE | 30 |
| Phase 2.5 (Data Backfill) | DONE | - |
| Phase 4 (AI Agent Core) | DONE | 10 |
| Phase 3 (Kafka) | DONE | 7.5 |
| Phase 3 (Airflow) | **TO DO** | 7.5 |
| Phase 4 (RAG Tool) | **TO DO** | 10 |
| Extra Features | **TO DO** | 20-40 |

**Current Score:** ~62.5 pts | **Target:** 85+ pts

---

## Execution Order (from IMPLEMENTATION_PRIORITY.md)

### BLOCKING - Must Do First

| # | Task | Time | Points | Status |
|---|------|------|--------|--------|
| 1 | Kafka Setup | 45 min | 7.5 | [x] DONE |
| 2 | Airflow Setup | 45 min | 7.5 | [ ] |
| 3 | Basic RAG (FAISS) | 60 min | 10 | [ ] |
| 4 | Kafka Agent Tool | 15 min | 5 | [x] DONE |

### QUICK WINS - Extra Points

| # | Task | Time | Points | Status |
|---|------|------|--------|--------|
| 5 | dbt Macros | 30 min | 10-15 | [ ] |
| 6 | dbt-expectations | 30 min | 10-15 | [ ] |
| 7 | Document Prompts | 20 min | 5-10 | [ ] |

### NICE TO HAVE - If Time Permits

| # | Task | Time | Points | Status |
|---|------|------|--------|--------|
| 8 | Hybrid RAG | 1-2 hrs | 15-20 | [ ] |
| 9 | Multi-Model Routing | 2-3 hrs | 15-20 | [ ] |

---

## Completed Work

### Phase 4: AI Agent Core - DONE

**Files Created:**
- `agent/config.py` - OpenAI configuration
- `agent/prompts.py` - System prompt with business context
- `agent/agent.py` - LangGraph state machine
- `agent/app.py` - Streamlit UI
- `agent/tools/snowflake_tools.py` - Snowflake query tool

**Test Results (9/10 Chi Linh Questions):**

| # | Question | Pass |
|---|----------|------|
| 1 | Top spending app | PASS |
| 2 | Why metrics changed | PASS |
| 3 | D0 ROAS by country | PASS |
| 4 | Revenue breakdown | PASS |
| 5 | Data reconciliation | PASS |
| 6 | CPI analysis | PARTIAL |
| 7 | Installs over time | PASS |
| 8 | Break-even analysis | PASS |
| 9 | Profitable apps | PASS |
| 10 | Country comparison | PASS |

**Response Time:** 3-8 seconds (target < 10s)

### Phase 2.5: Data Backfill - DONE

| Metric | Value |
|--------|-------|
| Date range | Dec 25, 2025 → Jan 22, 2026 (29 days) |
| ADJUST_DAILY | 122,895 rows |
| ADMOB_DAILY | 109,594 rows |
| fct_app_daily_performance | 140,546 rows |
| dim_apps | 59 apps |

---

## Next Actions

### Step 1: Kafka - DONE

**Files Created:**
- `kafka/docker-compose.yml` - Kafka + PostgreSQL (KRaft mode)
- `kafka/producer.py` - Generates fake alerts
- `kafka/consumer.py` - Writes to PostgreSQL
- `kafka/test_setup.py` - Connection tests
- `agent/tools/kafka_tools.py` - Agent tool for alerts

**Data: Alerts (unrelated to batch Snowflake data)**
- SPEND_SPIKE, ROAS_DROP, INSTALL_SURGE, ERROR_RATE
- Stored in PostgreSQL `streaming.alerts` table
- Agent queries PostgreSQL via `query_realtime_alerts` tool

### Step 2: Airflow (NOW)

```bash
mkdir -p airflow/dags
# Create docker-compose.yml
# Create dags/dbt_pipeline.py (3 tasks)
# Test: trigger DAG
```

### Step 3: RAG (AFTER Airflow)

```bash
# Create agent/tools/rag_tools.py (FAISS)
# Create docs/Business_Rules.pdf
# Test: agent queries documents
```

---

## Demo Day Prep

### Morning Checklist

```bash
# 1. Collect fresh data
python scripts/collect_adjust_capstone.py --days 1
python scripts/collect_admob_capstone.py --days 1

# 2. Run dbt
cd my_dbt_project && dbt build

# 3. Start services
cd kafka && docker-compose up -d
cd airflow && docker-compose up -d

# 4. Start Kafka producer
uv run python kafka/producer.py &

# 5. Test agent
uv run streamlit run agent/app.py
```

### Demo Flow (30 min)

| Time | Section | What to Show |
|------|---------|--------------|
| 0-5 | Real-time | Kafka producer → consumer |
| 5-10 | Batch | Airflow DAG → dbt run |
| 10-20 | AI Agent | Snowflake + Kafka + RAG queries |
| 20-30 | Extra + Q&A | Macros, tests, prompts |

---

## Reference Docs

| Doc | Purpose |
|-----|---------|
| `docs/IMPLEMENTATION_PRIORITY.md` | Detailed execution plan |
| `docs/EXTRA_FEATURES_PLAN.md` | Extra features with code |
| `docs/PHASE4_IMPLEMENTATION.md` | Agent implementation details |
| `docs/AGENT_GUIDE.md` | How agent works (high to low) |

---

## Quick Commands

```bash
# Agent
uv run python -m agent.agent
uv run streamlit run agent/app.py

# dbt
cd my_dbt_project && dbt build

# Kafka (after setup)
cd kafka && docker-compose up -d
uv run python kafka/producer.py

# Airflow (after setup)
cd airflow && docker-compose up -d
```
