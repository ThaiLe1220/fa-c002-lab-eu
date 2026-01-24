# Implementation Priority Guide

**Status: CORE COMPLETE - All checkboxes done**

**Created:** January 24, 2026
**Updated:** January 24, 2026 (All core work complete)
**Deadline:** January 24, 2026 (DEMO DAY)
**Current Score:** ~80 pts
**Target Score:** 85+ pts

---

## Executive Summary

### Current Status - ALL CORE DONE

| Category | Status | Points |
|----------|--------|--------|
| **Kafka Streaming** | DONE | 7.5 pts |
| **Airflow Orchestration** | DONE | 7.5 pts |
| **AI Agent Core** | DONE | 10 pts |
| **RAG Tool** | DONE | 10 pts |
| **Extra Features** | TO DO | 20+ pts |

### What's Complete

```
CORE CHECKBOXES - ALL DONE ✓
==============================
[x] Kafka Setup        → kafka/docker-compose.yml, producer.py, consumer.py
[x] Airflow Setup      → airflow/docker-compose.yml, dags/dbt_pipeline.py
[x] Kafka Agent Tool   → agent/tools/kafka_tools.py (query_realtime_alerts)
[x] RAG Tool           → agent/tools/rag_tools.py (search_business_documents)
[x] AI Agent           → agent/agent.py (3 tools bound)

REMAINING - EXTRA POINTS
========================
[ ] dbt Macros         → 30 min    → 10-15 pts
[ ] dbt-expectations   → 30 min    → 10-15 pts
```

---

## Completed Implementation

### 1. Kafka Streaming - DONE

**Files Created:**
| File | Description |
|------|-------------|
| `kafka/docker-compose.yml` | Kafka (KRaft mode) + PostgreSQL (port 5433) |
| `kafka/producer.py` | Generates alerts with `--batch N --interval 0` support |
| `kafka/consumer.py` | Writes to PostgreSQL with timeout handling |
| `kafka/test_setup.py` | Connection verification |

**Alert Types:**
- SPEND_SPIKE, ROAS_DROP, INSTALL_SURGE, ERROR_RATE
- Severities: critical, warning, info
- Regions: US, TH, VN, JP, ID

**Commands:**
```bash
# Start services
cd kafka && docker-compose up -d

# Generate 20 alerts quickly
uv run python kafka/producer.py --batch 20 --interval 0

# Start consumer (writes to PostgreSQL)
uv run python kafka/consumer.py
```

---

### 2. Airflow Orchestration - DONE

**Files Created:**
| File | Description |
|------|-------------|
| `airflow/docker-compose.yml` | Airflow (LocalExecutor) + PostgreSQL (port 5434) |
| `airflow/Dockerfile` | Custom image with dbt-snowflake |
| `airflow/profiles.yml` | dbt profile for Docker |
| `airflow/dags/dbt_pipeline.py` | 3 tasks: debug → run → test |

**DAG Structure:**
```
dbt_debug → dbt_run → dbt_test
```

**Commands:**
```bash
# Start Airflow
cd airflow && docker-compose up -d

# Access UI
open http://localhost:8080  # admin / admin
```

---

### 3. AI Agent - DONE

**Files Created:**
| File | Description |
|------|-------------|
| `agent/config.py` | OpenAI configuration (loads from .env) |
| `agent/prompts.py` | System prompt with 3-tool guidance |
| `agent/agent.py` | LangGraph state machine with memory |
| `agent/app.py` | Streamlit UI |

**Three Tools:**
| Tool | Purpose |
|------|---------|
| `query_snowflake` | Batch data from Snowflake |
| `query_realtime_alerts` | Streaming alerts from PostgreSQL |
| `search_business_documents` | Business rules via FAISS |

**Commands:**
```bash
# CLI mode
uv run python -m agent.agent -q "What's total revenue?"

# Interactive mode
uv run python -m agent.agent --interactive

# Streamlit UI
uv run streamlit run agent/app.py
```

---

### 4. RAG Tool - DONE

**Files Created:**
| File | Description |
|------|-------------|
| `docs/business_rules/ameno_business_rules.md` | ROAS thresholds, CPI benchmarks, alert definitions |
| `agent/tools/rag_tools.py` | FAISS vector store + search tool |
| `agent/rag_demo.py` | Interactive demo explaining chunking + embedding |
| `agent/vector_store/` | FAISS index (auto-generated) |

**How It Works:**
```
Document (4,477 chars) → Chunking (17 chunks) → Embedding (1536 dims) → FAISS
                                                                         ↑
Query → Embed → Similarity Search ──────────────────────────────────────┘
```

**Commands:**
```bash
# Test RAG tool
uv run python -m agent.agent -q "What are ROAS thresholds for scaling?"

# Run RAG demo (explains each step)
uv run python agent/rag_demo.py
```

---

## Remaining Work - Extra Features

### Priority 1: dbt Macros (10-15 pts)

**What to Add:**
```sql
-- macros/calculate_roas.sql
{% macro calculate_roas(revenue_col, cost_col) %}
CASE WHEN {{ cost_col }} > 0
     THEN ({{ revenue_col }}::DECIMAL / {{ cost_col }}) * 100
     ELSE NULL END
{% endmacro %}

-- macros/calculate_cpi.sql
{% macro calculate_cpi(cost_col, installs_col) %}
CASE WHEN {{ installs_col }} > 0
     THEN {{ cost_col }}::DECIMAL / {{ installs_col }}
     ELSE NULL END
{% endmacro %}
```

### Priority 2: dbt-expectations (10-15 pts)

**What to Add:**
```yaml
# packages.yml
packages:
  - package: calogica/dbt_expectations
    version: 0.10.4

# models/schema.yml
tests:
  - dbt_expectations.expect_column_values_to_be_between:
      min_value: 0
      max_value: 100000
```

---

## Demo Day Checklist

### Morning Prep (30 min before)

```bash
# 1. Start Kafka
cd kafka && docker-compose up -d

# 2. Start Airflow
cd ../airflow && docker-compose up -d

# 3. Generate fresh alerts
cd .. && uv run python kafka/producer.py --batch 30 --interval 0

# 4. Test all 3 agent tools
uv run python -m agent.agent -q "What's total revenue?"
uv run python -m agent.agent -q "Show me recent alerts"
uv run python -m agent.agent -q "What are ROAS thresholds?"
```

### Demo Script

| Time | Phase | What to Show |
|------|-------|--------------|
| 0-5 | CI/CD + Kafka | Start CI, show Kafka producer/consumer |
| 5-10 | Airflow + dbt | Show DAG, trigger run |
| 10-20 | AI Agent + RAG | Query all 3 tools, run rag_demo.py |
| 20-30 | Extra + Q&A | Show macros/tests, answer questions |

### Key Commands for Demo

```bash
# Kafka producer (visual)
uv run python kafka/producer.py

# Agent queries
uv run python -m agent.agent -q "What's our total ad revenue this week?"
uv run python -m agent.agent -q "Show me critical alerts"
uv run python -m agent.agent -q "What are ROAS thresholds for scaling?"

# Combined query
uv run python -m agent.agent -q "Which apps have ROAS below 80% and what should we do?"

# RAG demo (explains chunking + embedding)
uv run python agent/rag_demo.py

# Interactive mode
uv run python -m agent.agent --interactive

# Streamlit UI
uv run streamlit run agent/app.py
```

---

## Revision History

| Date | Change |
|------|--------|
| Jan 24, 2026 | All core complete: Kafka, Airflow, Agent, RAG |
| Jan 24, 2026 | Initial priority guide |
