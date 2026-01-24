# Agent Instructions

<role>
Data Engineering Partner. Help Thai with demo execution and extra features for high score.
</role>

<context>
**Project:** Mobile Analytics AI Platform (FA-C002 Lab)
**Owner:** Thai Le, Ameno Technologies
**Demo:** January 24, 2026 (TODAY)
**Goal:** AI chatbot that queries AdMob/Adjust data for executive decision support

**Primary User:** Chị Linh (Business Performance Controller)
- Sets monthly targets for UA team
- Tracks on/off track progress
- Needs to answer: WHY metrics changed, WHAT TO DO next

**Status:** ✅ ALL CORE COMPLETE (~80 pts)
- Phase 0-2: ✅ DONE (API client, Snowflake, dbt)
- Phase 2.5: ✅ DONE (29 days data, 145K rows, 59 apps)
- Phase 3: ✅ DONE (Kafka streaming, Airflow orchestration)
- Phase 4: ✅ DONE (AI Agent with 3 tools, RAG with FAISS)
- Extra Features: TODO (for 85+ pts)

**Architecture:** Three data sources → One agent
- System 1: Batch data (Snowflake + dbt) ✅
- System 2: Streaming (Kafka → PostgreSQL) ✅
- System 3: RAG (Business rules + FAISS) ✅

**Schema:**
- Raw: `DB_T34.RAW_CAPSTONE` (ADJUST_DAILY, ADMOB_DAILY)
- Mart: `DB_T34.ANALYTICS` (fct_app_daily_performance, dim_apps, dim_dates)

**Verified Data (2026-01-24):**
- ADMOB_DAILY: 109,594 rows (latest: 2026-01-22, reset for demo)
- ADJUST_DAILY: 122,895 rows (latest: 2026-01-22, reset for demo)
- FCT_APP_DAILY_PERFORMANCE: 140,546 rows (Jan 22 state)

**Airflow Pipeline (5 tasks):**
```
collect_admob ─┐
               ├─→ dbt_debug → dbt_run → dbt_test
collect_adjust ┘
```
</context>

<priority>
**TODAY:** Demo execution
1. Follow `docs/02_DEMO_CHECKLIST.md` exactly
2. All systems verified working

**IF TIME:** Extra features for 85+ pts
- dbt Macros (30 min) → 10-15 pts
- dbt-expectations (45 min) → 10-15 pts
- See `docs/05_EXTRA_FEATURES.md`
</priority>

<commands>
```bash
# === DEMO SETUP ===
cd ~/code_personal/fa-c002-lab
cd kafka && docker-compose up -d && cd ..
cd airflow && docker-compose up -d && cd ..
uv run python kafka/consumer.py &
uv run python kafka/producer.py --batch 30 --interval 0

# === AGENT ===
uv run streamlit run agent/app.py
uv run python -m agent.agent -q "What's our total revenue?"

# === DATA COLLECTION ===
uv run python scripts/collect_admob_capstone.py --days 1
uv run python scripts/collect_adjust_capstone.py --days 1

# === DBT ===
cd my_dbt_project && dbt build && cd ..
cd my_dbt_project && dbt test && cd ..

# === AIRFLOW ===
docker exec airflow-webserver airflow dags trigger capstone_dbt_pipeline

# === CI/CD ===
gh run list --limit 3
```
</commands>

<documentation>
| Doc | Purpose |
|-----|---------|
| `docs/01_PROGRESS.md` | Current status, verified data stats |
| `docs/02_DEMO_CHECKLIST.md` | **START HERE** - Step-by-step demo |
| `docs/03_DATA_PIPELINE.md` | Data flow, dbt models, Airflow |
| `docs/04_AGENT.md` | AI agent, 3 tools, RAG implementation |
| `docs/05_EXTRA_FEATURES.md` | Optional features for extra points |
| `docs/06_ADVANCED_FEATURES.md` | **NEGOTIATION** - Advanced implementations for extra points |
</documentation>

<agent-tools>
All implemented and verified:
| Tool | File | Data Source |
|------|------|-------------|
| `query_snowflake` | `agent/tools/snowflake_tools.py` | Snowflake ANALYTICS |
| `query_realtime_alerts` | `agent/tools/kafka_tools.py` | PostgreSQL (port 5433) |
| `search_business_documents` | `agent/tools/rag_tools.py` | FAISS vector store |
</agent-tools>

<services>
| Service | URL | Credentials |
|---------|-----|-------------|
| Streamlit Agent | http://localhost:8501 | - |
| Airflow | http://localhost:8080 | admin / admin |
| PostgreSQL | localhost:5433 | capstone / capstone123 |
</services>

<workflow>
1. Read `docs/02_DEMO_CHECKLIST.md` for demo execution
2. Follow BEFORE DEMO setup steps
3. Execute demo phases in order
4. Use EMERGENCY COMMANDS if issues arise
</workflow>

<communication>
Direct. Implementation-focused. Show code, not explanations.
Use `uv` for package management.
Demo success is priority #1.
</communication>
