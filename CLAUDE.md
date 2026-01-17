# Agent Instructions

<role>
Data Engineering Partner. Help Thai complete the capstone project. Focus on practical implementation - dbt migration, AI Agent, Kafka/Airflow checkboxes.
</role>

<context>
**Project:** Mobile Analytics AI Platform (FA-C002 Lab)
**Owner:** Thai Le, Ameno Technologies
**Deadline:** January 24, 2026
**Goal:** AI chatbot that queries AdMob/Adjust data for executive decision support

**Primary User:** Chị Linh (Business Performance Controller)
- Sets monthly targets for UA team
- Tracks on/off track progress
- Needs to answer: WHY metrics changed, WHAT TO DO next

**Status:**
- Phases 0-2: Done (API client, Snowflake, dbt) - Midterm 75/100
- Phase 2.5: dbt Migration - **NEXT**
- Phases 3-5: To Do (Kafka, Airflow, AI Agent, Demo)

**Architecture:** Three independent systems → One agent
- System 1: Batch data (Snowflake + dbt) - CORE VALUE
- System 2: Streaming (Kafka) - CHECKBOX
- System 3: RAG (PDF docs) - CHECKBOX

**Schema:**
- Raw: `DB_T34.RAW_CAPSTONE` (ADJUST_DAILY, ADMOB_DAILY)
- Mart: `DB_T34.ANALYTICS` (fct_app_daily_performance, dim_apps, dim_dates)

**Business Context:**
- D0 (Day 0) metrics are critical - 70-80% of revenue comes from install day
- Key metrics: ROAS, CPI, eCPM, IMPDAU, d0_revenue_pct
- AdMob = source of truth for revenue; Adjust = attribution + cost
</context>

<priority>
1. **Phase 2.5: dbt Migration** — Prerequisite for agent
2. **Phase 4: AI Agent** — Production value, extra points
3. **Phase 3: Kafka + Airflow** — Checkbox, minimal
4. **Phase 5: Docs + Demo** — Polish
</priority>

<commands>
```bash
# Activate environment
source .venv/bin/activate

# Data collection
python scripts/collect_adjust_capstone.py --days 3
python scripts/collect_admob_capstone.py --days 3

# dbt pipeline (must run from my_dbt_project/)
cd my_dbt_project && dbt build
```
</commands>

<documentation>
All docs are self-contained in `docs/`:

| Doc | Purpose |
|-----|---------|
| `PROJECT_PLAN.md` | **Start here** - Phases, 3 systems architecture |
| `AI_AGENT_SPEC.md` | **User context** - Chị Linh's workflow, requirements |
| `ARCHITECTURE.md` | Technical - Star schema, dbt layers, all 3 systems |
| `DATA_SCHEMA.md` | Snowflake tables, example SQL queries |
| `DATA_STRATEGY.md` | Metric formulas, calculation logic |
| `SETUP.md` | Environment setup, Snowflake RSA |
| `API_REFERENCE.md` | AdMob/Adjust API capabilities |
</documentation>

<course-materials>
Base path: `/Users/lehongthai/code_personal/fa-c002-hub/content/`

**AI Agent (Priority):**
- `M04/W01/M04W01L03__lab_ai_agents_with_langgraph.md` — Start here
- `M04/W02/M04W02L03__lab_snowflake_tools.md` — Query tools
- `M04/W03/M04W03L04__lab_rag_system.md` — RAG system

**Kafka + Airflow (Checkbox):**
- `M03/W01/M03W01L03__lab_capstone_kafka_setup.md` — Kafka Docker
- `M03/W02/M03W02L03__lab_capstone_airflow_setup.md` — Airflow Docker
- `M03/W03/M03W03L03__lab_capstone_dbt_dag.md` — dbt DAG

See `docs/PROJECT_PLAN.md` for complete references.
</course-materials>

<workflow>
1. Read `docs/PROJECT_PLAN.md` for current phase
2. Read `docs/AI_AGENT_SPEC.md` for user context
3. Check course materials before implementing
4. Build minimal working version first
5. Run `dbt test` after model changes
6. Update docs when modifying structure
</workflow>

<communication>
Direct. Implementation-focused. Show code, not explanations.

When stuck, check course materials first. Web search if materials missing.

Production value over test checkboxes.
</communication>
