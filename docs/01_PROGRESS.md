# Project Progress

**Last Updated:** 2026-01-24 (Verified)
**Demo:** Saturday 2026-01-24

---

## Score Summary

| Phase | Points | Status |
|-------|--------|--------|
| Phase 0-2 (Midterm) | 30 | ✅ DONE |
| Phase 2.5 (Data Backfill) | - | ✅ DONE |
| Phase 3 (Kafka) | 7.5 | ✅ DONE |
| Phase 3 (Airflow) | 7.5 | ✅ DONE |
| Phase 4 (AI Agent) | 10 | ✅ DONE |
| Phase 4 (RAG) | 10 | ✅ DONE |
| Extra Features | 10-30 | TODO |

**Current:** ~80 pts | **Target:** 85+

---

## What Works (Verified 2026-01-24)

### 1. CI/CD Pipeline
- **File:** `.github/workflows/dbt_ci.yml`
- **Trigger:** Push/PR to main/develop (*.sql or my_dbt_project/**)
- **Steps:** SQLFluff lint + dbt test (26 tests pass)
- **Last Run:** 2026-01-24 04:04 - SUCCESS

### 2. dbt Models (Snowflake)
- **Location:** `my_dbt_project/models/`
- **Schema:** `DB_T34.ANALYTICS`

| Layer | Models | Status |
|-------|--------|--------|
| 01_staging | stg_admob_capstone, stg_adjust_capstone | ✅ WORKS |
| 02_intermediate | int_app_daily_metrics | ✅ WORKS |
| 03_mart | fct_app_daily_performance, dim_apps, dim_dates | ✅ WORKS |

**Verified Data (2026-01-24):**
| Table | Rows | Latest Date |
|-------|------|-------------|
| RAW_CAPSTONE.ADMOB_DAILY | 113,412 | 2026-01-23 |
| RAW_CAPSTONE.ADJUST_DAILY | 127,246 | 2026-01-23 |
| ANALYTICS.FCT_APP_DAILY_PERFORMANCE | 145,500 | 2026-01-23 |

### 3. Kafka Streaming
- **Location:** `kafka/`
- **Components:**
  - `docker-compose.yml` - Kafka (KRaft) + PostgreSQL
  - `producer.py` - Generates alerts (--batch mode)
  - `consumer.py` - Writes to PostgreSQL alerts table
- **Verified:** Producer → Kafka → Consumer → PostgreSQL working

### 4. Airflow Orchestration
- **Location:** `airflow/`
- **DAG:** `capstone_dbt_pipeline` (manual trigger)
- **Tasks:** dbt_debug (4s) → dbt_run (24s) → dbt_test (3s)
- **Verified:** Full DAG run SUCCESS in ~31 seconds

### 5. AI Agent (3 Tools)
- **Location:** `agent/`
- **Tools:**

| Tool | Data Source | Verified |
|------|-------------|----------|
| `query_snowflake` | Snowflake ANALYTICS | ✅ Returns revenue, metrics |
| `query_realtime_alerts` | PostgreSQL alerts | ✅ Returns recent alerts |
| `search_business_documents` | FAISS vector store | ✅ Returns ROAS thresholds |

**Verified queries:**
- "What's our total revenue?" → $8,761.55 (latest date)
- "Show me recent alerts" → Returns alerts with severity, region
- "What is the ROAS threshold?" → Returns 80% threshold from RAG

---

## Known Limitations (Not Issues)

1. **Airflow schedule** - Set to `None` (manual trigger for demo control)
2. **Kafka producer** - Uses batch mode for demo predictability
3. **Vector store** - Cold start ~5s on first query (normal behavior)

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
