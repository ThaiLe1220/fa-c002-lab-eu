# Current Step: Demo Preparation

**Updated:** 2026-01-24
**Demo:** 2026-01-24
**Status:** ALL CORE COMPLETE - Ready for demo

---

## Quick Status

| Phase | Status | Points |
|-------|--------|--------|
| Phase 0-2 | DONE | 30 |
| Phase 2.5 (Data Backfill) | DONE | - |
| Phase 4 (AI Agent Core) | DONE | 10 |
| Phase 3 (Kafka) | DONE | 7.5 |
| Phase 3 (Airflow) | DONE | 7.5 |
| Phase 4 (RAG Tool) | DONE | 10 |
| Extra Features | TO DO | 20-40 |

**Current Score:** ~80 pts | **Target:** 85+ pts

---

## All Core Checkboxes Complete

| # | Task | Points | Status |
|---|------|--------|--------|
| 1 | Kafka Setup | 7.5 | DONE |
| 2 | Airflow Setup | 7.5 | DONE |
| 3 | AI Agent Core | 10 | DONE |
| 4 | RAG Tool | 10 | DONE |

### Extra Points (Optional)

| # | Task | Points | Status |
|---|------|--------|--------|
| 5 | dbt Macros | 10-15 | TO DO |
| 6 | dbt-expectations | 10-15 | TO DO |

---

## What's Implemented

### AI Agent - 3 Tools

| Tool | File | Data Source |
|------|------|-------------|
| `query_snowflake` | `agent/tools/snowflake_tools.py` | Snowflake (batch) |
| `query_realtime_alerts` | `agent/tools/kafka_tools.py` | PostgreSQL (streaming) |
| `search_business_documents` | `agent/tools/rag_tools.py` | FAISS (RAG) |

### Kafka Streaming

| File | Description |
|------|-------------|
| `kafka/docker-compose.yml` | Kafka (KRaft) + PostgreSQL |
| `kafka/producer.py` | Generates alerts (--batch mode) |
| `kafka/consumer.py` | Writes to PostgreSQL |

### Airflow Orchestration

| File | Description |
|------|-------------|
| `airflow/docker-compose.yml` | Airflow + PostgreSQL |
| `airflow/dags/dbt_pipeline.py` | debug → run → test |

### RAG

| File | Description |
|------|-------------|
| `docs/business_rules/ameno_business_rules.md` | Business rules document |
| `agent/tools/rag_tools.py` | FAISS vector store + search |
| `agent/rag_demo.py` | Interactive demo for explanation |

---

## Demo Day Commands

### Start Services

```bash
# Start Kafka + PostgreSQL
cd kafka && docker-compose up -d

# Start Airflow
cd ../airflow && docker-compose up -d

# Generate fresh alerts
cd .. && uv run python kafka/producer.py --batch 30 --interval 0
```

### Test Agent

```bash
# All 3 tools
uv run python -m agent.agent -q "What's our total revenue?"
uv run python -m agent.agent -q "Show me critical alerts"
uv run python -m agent.agent -q "What are ROAS thresholds?"

# Combined query
uv run python -m agent.agent -q "Which apps violate our business rules?"

# Interactive mode
uv run python -m agent.agent --interactive

# Streamlit UI
uv run streamlit run agent/app.py
```

### RAG Demo (Explains Chunking + Embedding)

```bash
uv run python agent/rag_demo.py
```

---

## Demo Flow (30 min)

| Time | Phase | What to Show |
|------|-------|--------------|
| 0-5 | CI/CD + Kafka | Start CI, show Kafka producer/consumer |
| 5-10 | Airflow + dbt | Show DAG, trigger run |
| 10-20 | AI Agent + RAG | Query all 3 tools, run rag_demo.py |
| 20-30 | Extra + Q&A | Macros/tests if done, answer questions |

---

## Key Talking Points

1. **Three Systems → One Agent**
   - Batch (Snowflake) for historical analysis
   - Streaming (Kafka) for real-time alerts
   - RAG (FAISS) for business rules

2. **RAG Explanation (when asked)**
   - Chunking: Split document into ~500 char pieces
   - Embedding: Convert text to 1536-dim vectors (OpenAI)
   - Search: Find similar vectors for query
   - Run `uv run python agent/rag_demo.py` to show step by step

3. **Business Value**
   - Chi Linh can self-serve analytics
   - No SQL knowledge required
   - Answers in seconds, not hours

---

## Reference Docs

| Doc | Purpose |
|-----|---------|
| `docs/PROJECT_PLAN.md` | Overall status |
| `docs/DEMO_FLOW.md` | Demo script |
| `docs/AGENT_GUIDE.md` | How agent works |
| `docs/IMPLEMENTATION_PRIORITY.md` | Implementation details |
