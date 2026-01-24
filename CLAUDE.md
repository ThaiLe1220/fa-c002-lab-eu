# Agent Instructions

<role>
Data Engineering Partner. Help Thai complete the capstone project. Focus on practical implementation - core checkboxes (Kafka, Airflow, RAG) and extra features for high score.
</role>

<context>
**Project:** Mobile Analytics AI Platform (FA-C002 Lab)
**Owner:** Thai Le, Ameno Technologies
**Demo:** January 24, 2026
**Goal:** AI chatbot that queries AdMob/Adjust data for executive decision support

**Primary User:** Chị Linh (Business Performance Controller)
- Sets monthly targets for UA team
- Tracks on/off track progress
- Needs to answer: WHY metrics changed, WHAT TO DO next

**Status:**
- Phases 0-2: DONE (API client, Snowflake, dbt) - Midterm 75/100
- Phase 2.5: DONE (29 days data, 140K rows, 59 apps)
- Phase 4 (Agent Core): DONE (Snowflake tool, 9/10 questions pass)
- Phase 3 (Kafka + Airflow): **IN PROGRESS** - BLOCKING
- Phase 4 (RAG): **TO DO** - BLOCKING
- Extra Features: **TO DO**

**Current Score:** ~55 pts | **Target:** 85+ pts

**Architecture:** Three independent systems → One agent
- System 1: Batch data (Snowflake + dbt) - DONE
- System 2: Streaming (Kafka → PostgreSQL) - TO DO (checkbox)
  - Fake alerts (SPEND_SPIKE, ROAS_DROP, etc.) - NOT related to batch data
  - Producer → Kafka → Consumer → PostgreSQL → Agent queries
- System 3: RAG (PDF docs + FAISS) - TO DO (checkbox)

**Schema:**
- Raw: `DB_T34.RAW_CAPSTONE` (ADJUST_DAILY, ADMOB_DAILY)
- Mart: `DB_T34.ANALYTICS` (fct_app_daily_performance, dim_apps, dim_dates)

**Business Context:**
- D0 (Day 0) metrics are critical - 70-80% of revenue comes from install day
- Key metrics: ROAS, CPI, eCPM, IMPDAU, d0_revenue_pct
- AdMob = source of truth for revenue; Adjust = attribution + cost
</context>

<priority>
**BLOCKING (must do for core points):**
1. Kafka Setup (45 min) → 7.5 pts
2. Airflow Setup (45 min) → 7.5 pts
3. Basic RAG with FAISS (60 min) → 10 pts
4. Kafka Agent Tool (15 min) → 5 pts

**QUICK WINS (extra points):**
5. dbt Macros (30 min) → 10-15 pts
6. dbt-expectations (30 min) → 10-15 pts
7. Document Prompts (20 min) → 5-10 pts

**NICE TO HAVE (if time permits):**
8. Hybrid RAG (1-2 hrs) → 15-20 pts
9. Multi-Model Routing (2-3 hrs) → 15-20 pts

See `docs/IMPLEMENTATION_PRIORITY.md` for detailed reasoning.
</priority>

<commands>
```bash
# Activate environment
source .venv/bin/activate

# AI Agent
uv run python -m agent.agent
uv run streamlit run agent/app.py

# Data collection
python scripts/collect_adjust_capstone.py --days 1
python scripts/collect_admob_capstone.py --days 1

# dbt pipeline
cd my_dbt_project && dbt build

# Kafka (after setup)
cd kafka && docker-compose up -d
uv run python kafka/producer.py

# Airflow (after setup)
cd airflow && docker-compose up -d
```
</commands>

<documentation>
**Start here:**
| Doc | Purpose |
|-----|---------|
| `CURRENT_STEP.md` | What to do NOW, execution checklist |
| `docs/IMPLEMENTATION_PRIORITY.md` | Detailed execution order with reasoning |
| `docs/EXTRA_FEATURES_PLAN.md` | Extra features with code examples |

**Reference:**
| Doc | Purpose |
|-----|---------|
| `docs/PROJECT_PLAN.md` | Phases, 3 systems architecture |
| `docs/AI_AGENT_SPEC.md` | Chị Linh's workflow, requirements |
| `docs/AGENT_GUIDE.md` | How agent works (high to low level) |
| `docs/ARCHITECTURE.md` | Technical - Star schema, dbt layers |
| `docs/DATA_SCHEMA.md` | Snowflake tables, SQL queries |
| `docs/PHASE4_IMPLEMENTATION.md` | Agent implementation details |
</documentation>

<course-materials>
Base path: `/Users/lehongthai/code_personal/fa-c002-hub/content/`

**Kafka + Airflow (Priority - Blocking):**
- `M03/W01/M03W01L03__lab_capstone_kafka_setup.md` — Kafka Docker (KRaft mode)
- `M03/W02/M03W02L03__lab_capstone_airflow_setup.md` — Airflow Docker
- `M03/W03/M03W03L03__lab_capstone_dbt_dag.md` — dbt DAG (3 tasks)

**RAG (Priority - Blocking):**
- `M04/W03/M04W03L04__lab_rag_system.md` — RAG system (Pinecone, but FAISS acceptable)

**Already Used:**
- `M04/W01/M04W01L03__lab_ai_agents_with_langgraph.md` — LangGraph agent
- `M04/W02/M04W02L03__lab_snowflake_tools.md` — Query tools

**Grading:**
- `/Users/lehongthai/code_personal/fa-c002-hub/capstone/capstone_project_grading.md`
- `/Users/lehongthai/code_personal/fa-c002-hub/capstone/capstone_demo_guide.md`
</course-materials>

<agent-files>
Already implemented:
- `agent/config.py` — OpenAI configuration
- `agent/prompts.py` — System prompt with business context
- `agent/agent.py` — LangGraph state machine
- `agent/app.py` — Streamlit UI
- `agent/tools/snowflake_tools.py` — Snowflake query tool

To implement:
- `agent/tools/kafka_tools.py` — Kafka streaming tool
- `agent/tools/rag_tools.py` — RAG document tool
</agent-files>

<workflow>
1. Read `CURRENT_STEP.md` for execution checklist
2. Follow `docs/IMPLEMENTATION_PRIORITY.md` order
3. Check course materials before implementing
4. Use code from `docs/EXTRA_FEATURES_PLAN.md`
5. Test each component before moving on
6. Update checklist in `CURRENT_STEP.md` as you go
</workflow>

<communication>
Direct. Implementation-focused. Show code, not explanations.

Use `uv` for package management (NOT pip).

When stuck, check course materials first. Web search if materials missing.

Core checkboxes first, then extra features.
</communication>
