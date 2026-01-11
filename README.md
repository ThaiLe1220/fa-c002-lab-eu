# Mobile Analytics AI Platform

Data & AI Engineering Capstone - Foundry AI Academy

## Overview

End-to-end data platform transforming real mobile app revenue data (AdMob + Adjust) into intelligent business insights through modern data stack and AI agent.

**Goal:** Executive Decision Support Agent for Ameno Technologies

## Project Status

| Phase | Description | Status | Points |
|-------|-------------|--------|--------|
| Phase 0 | API Client + CSV | Done | - |
| Phase 1-2 | Snowflake + dbt | Done | 30 |
| Phase 2.5 | dbt Migration (D0 metrics) | **Next** | - |
| Phase 3 | Kafka + Airflow | To Do | 15 |
| Phase 4 | AI Agent + RAG | Priority | 20 |
| Phase 5 | Docs + Demo | To Do | 10 |

**Midterm:** 75/100 | **Final Test:** January 24, 2026

## Quick Start

```bash
# Activate environment
cd /Users/lehongthai/code_personal/fa-c002-lab
source .venv/bin/activate

# Data collection (Adjust + AdMob to Snowflake)
python scripts/collect_adjust_capstone.py --days 3
python scripts/collect_admob_capstone.py --days 3

# dbt pipeline
cd my_dbt_project && dbt build
```

## Architecture

```
DATA SOURCES              STORAGE                 TRANSFORMATION          OUTPUT
┌─────────────┐          ┌─────────────┐         ┌─────────────┐        ┌─────────────┐
│  AdMob API  │─────────▶│  Snowflake  │────────▶│  dbt Models │───────▶│  AI Agent   │
│ Adjust API  │          │ RAW_CAPSTONE│         │  Star Schema│        │  Streamlit  │
└─────────────┘          └─────────────┘         └─────────────┘        └─────────────┘
       │                                                                        │
       ▼                                                                        ▼
┌─────────────┐                                                        ┌─────────────┐
│   Kafka     │                                                        │  Executives │
│ (Real-time) │                                                        │  Dashboard  │
└─────────────┘                                                        └─────────────┘
       │                        ┌─────────────┐
       └───────────────────────▶│   Airflow   │
                                │(Orchestrate)│
                                └─────────────┘
```

## Data Sources

| Source | Schema | Volume | Key Metrics |
|--------|--------|--------|-------------|
| Adjust | `RAW_CAPSTONE.ADJUST_DAILY` | ~4K rows/day | installs, daus, ad_revenue, network_cost, D0 metrics |
| AdMob | `RAW_CAPSTONE.ADMOB_DAILY` | ~1.5K rows/day | estimated_earnings, impressions, eCPM |

## Project Structure

```
fa-c002-lab/
├── README.md                    # This file
├── CLAUDE.md                    # AI assistant context
├── scripts/
│   ├── collect_adjust_capstone.py
│   └── collect_admob_capstone.py
├── my_dbt_project/
│   └── models/
│       ├── 01_staging/          # stg_adjust, stg_admob
│       ├── 02_intermediate/     # int_app_daily_metrics
│       └── 03_mart/             # fct_app_daily_performance, dim_apps, dim_dates
├── agent/                       # [To Do] AI Agent
├── kafka/                       # [To Do] Streaming
├── dags/                        # [To Do] Airflow DAGs
└── docs/
    ├── ARCHITECTURE.md          # Star schema, data flow
    ├── DATA_SCHEMA.md           # Schema details, queries
    ├── SETUP.md                 # Environment setup
    ├── PROJECT_PLAN.md          # Capstone phases, checklist
    ├── DATA_STRATEGY.md         # Business logic, ROAS formulas
    └── API_REFERENCE.md         # API capabilities
```

## Key Metrics

| Metric | Formula | Business Use |
|--------|---------|--------------|
| **ROAS** | ad_revenue / network_cost | Return on ad spend |
| **D0 Revenue %** | ad_revenue_d0 / ad_revenue | Same-day payback |
| **eCPM** | (ad_revenue / impressions) * 1000 | Ad efficiency |
| **CPI** | network_cost / installs | Cost per install |
| **ARPDAU** | ad_revenue / daus | Revenue per active user |

**Business Context:** 70-80% of revenue comes from Day 0 (install day). D0 metrics are critical for ROAS analysis.

## Documentation

| # | Doc | Purpose |
|---|-----|---------|
| 1 | [PROJECT_PLAN.md](docs/PROJECT_PLAN.md) | **Start here.** Phases, status, course material references |
| 2 | [DATA_SCHEMA.md](docs/DATA_SCHEMA.md) | Tables, schemas, example SQL queries |
| 3 | [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Star schema, dbt layers, data flow |
| 4 | [API_REFERENCE.md](docs/API_REFERENCE.md) | AdMob/Adjust API capabilities and limits |
| 5 | [DATA_STRATEGY.md](docs/DATA_STRATEGY.md) | Business logic, ROAS formulas, metrics |
| 6 | [SETUP.md](docs/SETUP.md) | Environment setup (reference when needed) |

## Tech Stack

- **dbt** - SQL transformations
- **Snowflake** - Data warehouse (`DB_T34`)
- **Python** - API collection, AI agent
- **LangGraph** - AI agent framework
- **Kafka** - Real-time streaming
- **Airflow** - Orchestration
- **Streamlit** - UI
- **GitHub Actions** - CI/CD

---

**Last Updated:** January 2026
