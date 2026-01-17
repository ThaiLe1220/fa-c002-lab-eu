# Capstone Project Plan

## Goal

**Executive Decision Support Agent for Ameno Technologies**

AI chatbot that queries real AdMob/Adjust data to answer business questions for executives without SQL knowledge.

**Primary User:** Chị Linh (Business Performance Controller) - See `AI_AGENT_SPEC.md` for detailed user context.

---

## System Architecture Overview

**Three Independent Systems → One Agent**

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI AGENT (Orchestrator)                     │
│              LangGraph + Memory + Business Context              │
└─────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  BATCH DATA   │   │  STREAMING    │   │     RAG       │
│  (Snowflake)  │   │  (Kafka)      │   │   (Docs)      │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ Real data     │   │ Fake data     │   │ Any PDF       │
│ dbt transform │   │ Local Docker  │   │ Vector store  │
│ BUSINESS VALUE│   │ CHECKBOX      │   │ CHECKBOX      │
└───────────────┘   └───────────────┘   └───────────────┘
```

**Key Insight:** Kafka and RAG are independent checkbox items. They don't need to integrate with the main batch flow. Use fake/fabricated data. The agent ties them together at demo time.

---

## Project Status

| Phase | Description | Status | Points |
|-------|-------------|--------|--------|
| Phase 0 | API Client + CSV | Done | - |
| Phase 1-2 | Snowflake + dbt | Done | 30 |
| Phase 2.5 | dbt Migration (D0 metrics) | **Next** | - |
| Phase 3 | Kafka + Airflow (checkbox) | To Do | 15 |
| Phase 4 | AI Agent | Priority | 20 |
| Phase 5 | Docs + Demo | To Do | 10 |

**Midterm:** 75/100 | **Final Test:** January 24, 2026

---

## Grading Breakdown

| Section | Points | System |
|---------|--------|--------|
| Data Ingestion & Orchestration | 15 | Kafka + Airflow (checkbox) |
| Data Modeling & Transformation | 15 | dbt (core) |
| DevOps & CI | 5 | GitHub Actions |
| Documentation | 5 | README + diagrams |
| AI Agent (RAG + memory) | 10 | RAG checkbox + Agent |
| AI Agent (data querying) | 10 | Snowflake tools (core) |
| **Extra Features** | **40** | **Advanced agent + business context** |

**Pass:** 50 points | **Target:** 80+ points

---

## Phase 2.5: dbt Migration (PREREQUISITE)

**Must complete before AI Agent.** Current dbt models use old `RAW_MIDTEST` schema.

### Tasks

1. **Create staging models for RAW_CAPSTONE**
   - [ ] `stg_admob_capstone.sql` → RAW_CAPSTONE.ADMOB_DAILY
   - [ ] `stg_adjust_capstone.sql` → RAW_CAPSTONE.ADJUST_DAILY

2. **Update intermediate model**
   - [ ] Add: ad_revenue_d0, ad_impressions_d0, network_cost, paid_impressions, subscrevnt_revenue
   - [ ] Point to new staging models

3. **Update fact table**
   - [ ] Add D0 metrics columns
   - [ ] Add calculated: d0_revenue_pct

4. **Validate**
   - [ ] `dbt build` passes
   - [ ] `dbt test` passes
   - [ ] Query fact table, verify D0 data exists

### Architecture Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Schema | Star + flat view | Industry standard + AI Agent convenience |
| Layers | 3 (staging/int/mart) | Clear separation, good debugging |
| Materialization | Keep incremental | Required by grading rubric |
| Metrics | Raw in table, aggregate at query | Flexibility for different aggregation levels |

See `ARCHITECTURE.md` for detailed technical documentation.

---

## Phase 3: Kafka + Airflow (CHECKBOX)

**Minimal implementation. Independent from main flow.**

### Kafka (Streaming Checkbox)

- Local Docker setup
- Fake data producer (simulated metrics)
- Consumer that stores to local DB or prints
- Agent tool to query "latest streaming data"

**NOT required:** Push to Snowflake, integrate with batch flow

### Airflow (Orchestration Checkbox)

- Local Docker setup
- 3 tasks minimum: collect → dbt run → dbt test
- Scheduled daily

### Course Materials

```
/Users/lehongthai/code_personal/fa-c002-hub/content/
├── M03/W01/M03W01L03__lab_capstone_kafka_setup.md
├── M03/W02/M03W02L03__lab_capstone_airflow_setup.md
└── M03/W03/M03W03L03__lab_capstone_dbt_dag.md
```

---

## Phase 4: AI Agent (PRIORITY)

**This is where business value and extra points come from.**

### System 1: Batch Data Querying (Core - 10 pts)

Agent queries Snowflake fact table for business metrics.

**Tools to build:**
- `query_revenue` - Revenue by app/country/date
- `query_roas` - ROAS calculations
- `query_comparison` - Compare periods/apps/countries

**Success:** Answer chị Linh's questions accurately.

### System 2: RAG Document Query (Checkbox - 5 pts)

Agent answers questions from PDF documents.

**Minimal setup:**
- Any PDF (business docs, metric definitions)
- Local vector store (Chroma/FAISS)
- Retrieval tool

**NOT required:** Complex chunking, production RAG

### System 3: Streaming Query (Checkbox - 5 pts)

Agent queries "real-time" data from Kafka.

**Minimal setup:**
- Query latest message from Kafka topic
- Return fake metric data
- Show it works

### Agent Orchestration (Extra Points - up to 40 pts)

**Where we shine:**
- Business context (chị Linh's workflow, decision framework)
- Memory (conversation context)
- Multi-tool orchestration
- Intelligent responses (WHY + WHAT TO DO)

See `AI_AGENT_SPEC.md` for detailed requirements.

### Course Materials

```
/Users/lehongthai/code_personal/fa-c002-hub/content/
├── M04/W01/M04W01L03__lab_ai_agents_with_langgraph.md  # START HERE
├── M04/W02/M04W02L03__lab_snowflake_tools.md           # Query tools
└── M04/W03/M04W03L04__lab_rag_system.md                # RAG system
```

---

## Phase 5: Documentation & Demo

### Required Docs

- [ ] README.md with architecture diagram
- [ ] Clear setup instructions
- [ ] Demo script

### Demo Checklist

Must demonstrate live:

- [ ] Kafka producer running (show streaming)
- [ ] Airflow DAG execution (show dbt run)
- [ ] GitHub Actions passing
- [ ] Agent with conversation memory
- [ ] RAG document query
- [ ] Batch data query
- [ ] Combined query (bonus)

---

## Target Directory Structure

```
fa-c002-lab/
├── agent/                    # AI Agent (Phase 4)
│   ├── agent.py              # LangGraph agent
│   ├── tools/
│   │   ├── snowflake_tools.py
│   │   ├── kafka_tools.py
│   │   └── rag_tools.py
│   ├── prompts/
│   │   └── system_prompt.py
│   └── app.py                # Streamlit UI
├── kafka/                    # Streaming (Phase 3 - independent)
│   ├── docker-compose.yml
│   ├── producer.py
│   └── consumer.py
├── dags/                     # Airflow (Phase 3)
│   └── dbt_pipeline.py
├── my_dbt_project/           # dbt (Phase 2.5)
│   └── models/
│       ├── 01_staging/
│       ├── 02_intermediate/
│       └── 03_mart/
├── scripts/                  # Data collection (Done)
└── docs/                     # Documentation
    ├── PROJECT_PLAN.md       # This file
    ├── AI_AGENT_SPEC.md      # User context, requirements
    ├── ARCHITECTURE.md       # Technical architecture
    ├── DATA_SCHEMA.md        # Snowflake schemas
    ├── DATA_STRATEGY.md      # Metric formulas
    └── ...
```

---

## Quick Reference

**Priority order:**
1. Phase 2.5 (dbt migration) - Prerequisite
2. Phase 4 (AI Agent) - Business value + extra points
3. Phase 3 (Kafka + Airflow) - Checkbox
4. Phase 5 (Docs + Demo) - Polish

**Key docs:**
- `AI_AGENT_SPEC.md` - Who is the user, what do they need
- `DATA_STRATEGY.md` - How to calculate metrics
- `ARCHITECTURE.md` - How the system works

**Course materials base:**
```
/Users/lehongthai/code_personal/fa-c002-hub/content/
```
