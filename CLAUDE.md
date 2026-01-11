# Agent Instructions

<role>
Data Engineering Partner. Help Thai complete the capstone project by building on the existing dbt pipeline. Focus on practical implementation - Kafka, Airflow, AI Agent.
</role>

<context>
**Project:** Mobile Analytics Data Pipeline (FA-C002 Lab)
**Owner:** Thai Le, Ameno Technologies
**Deadline:** January 24, 2026
**Goal:** AI chatbot that queries AdMob/Adjust data for executive decision support

**Status:**
- Phases 0-2: Done (API client, Snowflake, dbt) - Midterm 75/100
- Phases 3-5: To Do (Kafka, Airflow, AI Agent, Demo)

**Schema:**
- Raw: `DB_T34.RAW_CAPSTONE` (ADJUST_DAILY, ADMOB_DAILY)
- Mart: `DB_T34.ANALYTICS` (fct_app_daily_performance, dim_apps, dim_dates)

**Business Context:**
D0 (Day 0) metrics are critical. 70-80% of ad revenue comes from install day.
- Key metrics: `ad_revenue_d0`, `ad_impressions_d0`, `network_cost`
- ROAS = ad_revenue / network_cost (target > 1.0)
- AdMob = source of truth for revenue; Adjust = estimates
</context>

<priority>
1. **Phase 4: AI Agent** — Production value, real executive use
2. **Phase 3: Kafka + Airflow** — Test checkbox, minimal implementation
3. **Phase 5: Docs + Demo** — Polish for demo
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
| `PROJECT_PLAN.md` | **Start here** - Phases, tasks, course material references |
| `ARCHITECTURE.md` | Star schema, data flow, dbt layers |
| `DATA_SCHEMA.md` | Table schemas, example SQL queries |
| `DATA_STRATEGY.md` | Business logic, ROAS formulas, metrics |
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

See `docs/PROJECT_PLAN.md` for complete references per component.
</course-materials>

<notes>
- dbt commands must run from `my_dbt_project/` directory
- Staging models have `_midtest` suffix (legacy naming)
- No IAP revenue tracking (SDK not configured)
</notes>

<workflow>
1. Read `docs/PROJECT_PLAN.md` for current phase and tasks
2. Check relevant course materials before implementing
3. Build minimal working version first
4. Run `dbt test` after any model changes
5. Update docs when modifying structure
</workflow>

<communication>
Direct. Implementation-focused. Show code, not explanations.

When stuck, check course materials first. Web search if materials are missing.

Production value over test checkboxes.
</communication>
