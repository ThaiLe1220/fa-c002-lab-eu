# FA-C002 Lab - Mobile Analytics AI Platform

AI chatbot for AdMob/Adjust analytics. Queries batch data (Snowflake), streaming alerts (Kafka), and business rules (RAG).

**Score:** ~80 pts (core complete) | **Demo:** 2026-01-24

---

## Quick Start

```bash
# 1. Start services
cd kafka && docker-compose up -d
cd ../airflow && docker-compose up -d

# 2. Generate alerts
uv run python kafka/producer.py --batch 30 --interval 0

# 3. Run agent
uv run streamlit run agent/app.py
```

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [01_PROGRESS.md](docs/01_PROGRESS.md) | Current status, what works |
| [02_DEMO_CHECKLIST.md](docs/02_DEMO_CHECKLIST.md) | Step-by-step demo commands |
| [03_DATA_PIPELINE.md](docs/03_DATA_PIPELINE.md) | Data flow, dbt models, reasoning |
| [04_AGENT.md](docs/04_AGENT.md) | AI agent, tools, RAG |
| [05_EXTRA_FEATURES.md](docs/05_EXTRA_FEATURES.md) | Optional features (TODO) |

---

## Architecture

```
User → AI Agent → ┌── query_snowflake ────────► Snowflake (batch)
                  ├── query_realtime_alerts ──► PostgreSQL (streaming)
                  └── search_business_documents ► FAISS (RAG)
```

**Data Flow:**
```
AdMob/Adjust APIs → Python Scripts → Snowflake RAW → dbt → ANALYTICS
Kafka Producer → Kafka → Consumer → PostgreSQL alerts
Business Rules Doc → FAISS Vector Store → RAG Search
```

---

## Key Commands

```bash
# dbt
cd my_dbt_project && dbt build

# Agent
uv run python -m agent.agent -q "What's our total revenue?"
uv run python -m agent.agent --interactive

# RAG demo (explains chunking + embedding)
uv run python agent/rag_demo.py

# CI status
gh run list --limit 3
```

---

## Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Streamlit | http://localhost:8501 | - |
| Airflow | http://localhost:8080 | admin / admin |
| Kafka | localhost:29092 | - |
| PostgreSQL (streaming) | localhost:5433 | postgres / postgres |

---

## File Structure

```
fa-c002-lab/
├── my_dbt_project/models/     # dbt models (staging → mart)
├── kafka/                     # Kafka + PostgreSQL for streaming
├── airflow/                   # Airflow for orchestration
├── agent/                     # AI agent (LangGraph)
│   └── tools/                 # 3 tools (Snowflake, Kafka, RAG)
├── docs/                      # Documentation
│   └── business_rules/        # RAG documents
├── scripts/                   # Data collection
└── .github/workflows/         # CI/CD
```

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Data Warehouse | Snowflake |
| Transformation | dbt |
| Streaming | Kafka (KRaft) |
| Orchestration | Airflow |
| AI Agent | LangGraph + OpenAI |
| Vector Store | FAISS |
| UI | Streamlit |
| CI/CD | GitHub Actions |
