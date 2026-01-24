# Mobile Analytics AI Platform

Data & AI Engineering Capstone - Foundry AI Academy

## Overview

Executive Decision Support Agent for Ameno Technologies. AI chatbot that queries real mobile app revenue data (AdMob + Adjust) to answer business questions for executives without SQL knowledge.

**Primary User:** Chi Linh (Business Performance Controller)
**Demo:** January 24, 2026

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AI AGENT                                │
│              LangGraph + Memory + Business Context              │
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│  │ Snowflake   │   │   Kafka     │   │    RAG      │          │
│  │   Tool      │   │   Tool      │   │   Tool      │          │
│  │   DONE      │   │   TO DO     │   │   TO DO     │          │
│  └─────────────┘   └─────────────┘   └─────────────┘          │
└─────────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   SYSTEM 1    │   │   SYSTEM 2    │   │   SYSTEM 3    │
│  Batch Data   │   │  Streaming    │   │  Documents    │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ Real AdMob/   │   │ Simulated     │   │ PDF docs      │
│ Adjust data   │   │ metrics       │   │ FAISS store   │
│ Snowflake     │   │ Local Kafka   │   │               │
│ dbt transform │   │               │   │               │
│ DONE          │   │ TO DO         │   │ TO DO         │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Project Status

| Phase | Description | Status | Points |
|-------|-------------|--------|--------|
| Phase 0 | API Client + CSV | DONE | - |
| Phase 1-2 | Snowflake + dbt | DONE | 30 |
| Phase 2.5 | Full Portfolio (29 days, 140K rows) | DONE | - |
| Phase 4 | AI Agent (Snowflake Tool) | DONE | 10 |
| Phase 3 | Kafka + Airflow | **IN PROGRESS** | 15 |
| Phase 4 | RAG Tool | **TO DO** | 10 |
| Extra | dbt Macros, Data Quality, etc. | **TO DO** | 20-40 |

**Current:** ~55 pts | **Target:** 85+ pts | **Midterm:** 75/100

## Quick Start

```bash
# Activate environment
cd /Users/lehongthai/code_personal/fa-c002-lab
source .venv/bin/activate

# Run AI Agent (Streamlit)
uv run streamlit run agent/app.py

# Run AI Agent (CLI)
uv run python -m agent.agent

# dbt pipeline
cd my_dbt_project && dbt build
```

## Data Stats

| Metric | Value |
|--------|-------|
| Date Range | Dec 25, 2025 → Jan 22, 2026 |
| Apps | 59 |
| Fact Rows | 140,546 |
| Total Revenue | $251,878 |
| Total Cost | $245,940 |

## Key Metrics

| Metric | Formula | Business Use |
|--------|---------|--------------|
| **D0 ROAS** | ad_revenue_d0 / network_cost | Immediate profitability |
| **D7 ROAS** | ad_revenue_d7 / network_cost | Near-complete LTV |
| **CPI** | network_cost / installs | Cost per install |
| **eCPM** | (ad_revenue / impressions) × 1000 | Ad efficiency |

## Project Structure

```
fa-c002-lab/
├── agent/                    # AI Agent [DONE]
│   ├── config.py             # OpenAI config
│   ├── prompts.py            # System prompt
│   ├── agent.py              # LangGraph agent
│   ├── app.py                # Streamlit UI
│   └── tools/
│       ├── snowflake_tools.py  # [DONE]
│       ├── kafka_tools.py      # [TO DO]
│       └── rag_tools.py        # [TO DO]
├── kafka/                    # Streaming [TO DO]
│   ├── docker-compose.yml
│   ├── producer.py
│   └── consumer.py
├── airflow/                  # Orchestration [TO DO]
│   ├── docker-compose.yml
│   └── dags/
│       └── dbt_pipeline.py
├── my_dbt_project/           # dbt models [DONE]
│   ├── models/
│   │   ├── 01_staging/
│   │   ├── 02_intermediate/
│   │   └── 03_mart/
│   └── macros/
├── scripts/                  # Data collection [DONE]
│   ├── collect_adjust_capstone.py
│   └── collect_admob_capstone.py
└── docs/                     # Documentation
    ├── PROJECT_PLAN.md
    ├── IMPLEMENTATION_PRIORITY.md  # Execution plan
    ├── EXTRA_FEATURES_PLAN.md      # Extra features
    ├── AGENT_GUIDE.md              # How agent works
    └── ...
```

## Documentation

| Doc | Purpose |
|-----|---------|
| [CURRENT_STEP.md](CURRENT_STEP.md) | What to do NOW |
| [IMPLEMENTATION_PRIORITY.md](docs/IMPLEMENTATION_PRIORITY.md) | Detailed execution plan |
| [EXTRA_FEATURES_PLAN.md](docs/EXTRA_FEATURES_PLAN.md) | Extra features with code |
| [PROJECT_PLAN.md](docs/PROJECT_PLAN.md) | Phases and status |
| [AGENT_GUIDE.md](docs/AGENT_GUIDE.md) | How agent works (high to low) |
| [AI_AGENT_SPEC.md](docs/AI_AGENT_SPEC.md) | User context (Chi Linh) |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture |
| [DATA_SCHEMA.md](docs/DATA_SCHEMA.md) | Snowflake tables |

## Tech Stack

- **Python 3.12** + **uv** - Package management
- **dbt** - SQL transformations
- **Snowflake** - Data warehouse (`DB_T34`)
- **LangGraph** - AI agent framework
- **OpenAI GPT-4o-mini** - LLM
- **Streamlit** - UI
- **Kafka** - Streaming (checkbox)
- **Airflow** - Orchestration (checkbox)
- **FAISS** - Vector store for RAG

## CI/CD

- **GitHub Actions** - dbt CI (SQLFluff + dbt test)
- See `.github/workflows/dbt_ci.yml`

---

**Last Updated:** January 24, 2026
