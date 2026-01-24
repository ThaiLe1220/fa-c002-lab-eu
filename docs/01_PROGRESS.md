# Project Progress

**Last Updated:** 2026-01-24
**Demo:** Saturday 2026-01-24

---

## Score Summary

| Phase | Points | Status |
|-------|--------|--------|
| Phase 0-2 (Midterm) | 30 | DONE |
| Phase 2.5 (Data Backfill) | - | DONE |
| Phase 3 (Kafka) | 7.5 | DONE |
| Phase 3 (Airflow) | 7.5 | DONE |
| Phase 4 (AI Agent) | 10 | DONE |
| Phase 4 (RAG) | 10 | DONE |
| Extra Features | 10-30 | TODO |

**Current:** ~80 pts | **Target:** 85+

---

## What Works

### 1. CI/CD Pipeline
- **File:** `.github/workflows/dbt_ci.yml`
- **Trigger:** Push/PR to main/develop (*.sql or my_dbt_project/**)
- **Steps:** SQLFluff lint + dbt test (26 tests pass)
- **Last Run:** 2026-01-24 - SUCCESS

### 2. dbt Models (Snowflake)
- **Location:** `my_dbt_project/models/`
- **Schema:** `DB_T34.ANALYTICS`

| Layer | Models | Status |
|-------|--------|--------|
| 01_staging | stg_admob_capstone, stg_adjust_capstone | WORKS |
| 02_intermediate | int_app_daily_metrics | WORKS |
| 03_mart | fct_app_daily_performance, dim_apps, dim_dates | WORKS |

**Data:** 59 apps, 240 countries, 29 days (Dec 26, 2025 - Jan 23, 2026)

### 3. Kafka Streaming
- **Location:** `kafka/`
- **Components:**
  - `docker-compose.yml` - Kafka (KRaft) + PostgreSQL
  - `producer.py` - Generates alerts (--batch mode)
  - `consumer.py` - Writes to PostgreSQL

### 4. Airflow Orchestration
- **Location:** `airflow/`
- **Components:**
  - `docker-compose.yml` - Airflow (LocalExecutor)
  - `dags/dbt_pipeline.py` - debug -> run -> test

### 5. AI Agent (3 Tools)
- **Location:** `agent/`
- **Tools:**

| Tool | File | Data Source |
|------|------|-------------|
| `query_snowflake` | `tools/snowflake_tools.py` | Snowflake (batch) |
| `query_realtime_alerts` | `tools/kafka_tools.py` | PostgreSQL (streaming) |
| `search_business_documents` | `tools/rag_tools.py` | FAISS (RAG) |

---

## What Doesn't Work / Known Issues

1. **Airflow dbt integration** - Runs but needs manual trigger (no auto-schedule in demo)
2. **Real-time Kafka** - Uses batch mode for demo (--batch flag)
3. **Vector store** - Regenerates on first run (cold start ~5s)

---

## File Structure (Key Files Only)

```
fa-c002-lab/
├── .github/workflows/dbt_ci.yml    # CI/CD
├── my_dbt_project/
│   └── models/
│       ├── 01_staging/             # stg_admob_capstone, stg_adjust_capstone
│       ├── 02_intermediate/        # int_app_daily_metrics
│       └── 03_mart/                # fct_*, dim_*
├── kafka/
│   ├── docker-compose.yml          # Kafka + PostgreSQL
│   ├── producer.py                 # Alert generator
│   └── consumer.py                 # Writes to DB
├── airflow/
│   ├── docker-compose.yml          # Airflow
│   └── dags/dbt_pipeline.py        # dbt DAG
├── agent/
│   ├── agent.py                    # LangGraph agent
│   ├── prompts.py                  # System prompt
│   ├── app.py                      # Streamlit UI
│   ├── rag_demo.py                 # RAG explanation demo
│   └── tools/
│       ├── snowflake_tools.py      # query_snowflake
│       ├── kafka_tools.py          # query_realtime_alerts
│       └── rag_tools.py            # search_business_documents
├── docs/
│   └── business_rules/             # RAG documents
└── scripts/
    ├── collect_admob_capstone.py   # Data collection
    └── collect_adjust_capstone.py
```

---

## Commit History (Recent)

```
1ef9b55 feat: implement RAG tool and fix CI pipeline
f54642a docs: update all docs and create DEMO_FLOW.md
c9eb8a8 feat: implement Airflow for dbt orchestration
4b85158 fix: improve Kafka producer and consumer for batch processing
```
