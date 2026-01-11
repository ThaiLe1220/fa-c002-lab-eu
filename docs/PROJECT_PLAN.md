# Capstone Project Plan

## Goal

**Executive Decision Support Agent for Ameno Technologies**

AI chatbot that queries real AdMob/Adjust data to answer business questions for executives without SQL knowledge.

---

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

---

## Course Materials Base Path

```
/Users/lehongthai/code_personal/fa-c002-hub/content
```

---

## Phase 2.5: dbt Migration (PREREQUISITE)

**Must complete before AI Agent.** Current dbt models use old `RAW_MIDTEST` schema without D0 metrics.

### Tasks

1. **Create staging models for RAW_CAPSTONE**
   - [ ] `stg_admob_capstone.sql` → RAW_CAPSTONE.ADMOB_DAILY
   - [ ] `stg_adjust_capstone.sql` → RAW_CAPSTONE.ADJUST_DAILY (with D0 columns)

2. **Update intermediate model**
   - [ ] Add: ad_revenue_d0, ad_impressions_d0, network_cost, paid_impressions, subscrevnt_revenue
   - [ ] Point to new staging models

3. **Update fact table**
   - [ ] Add D0 metrics columns
   - [ ] Add calculated: d0_revenue_pct, roas

4. **Validate**
   - [ ] `dbt build` passes
   - [ ] `dbt test` passes
   - [ ] Query fact table, verify D0 data exists

5. **Cleanup docs**
   - [ ] Remove "Migration Status" section from DATA_SCHEMA.md
   - [ ] Update this phase status to "Done"

See `docs/DATA_SCHEMA.md` → Migration Status for column details.

**Note:** Docs already describe target state. Complete code migration first, then cleanup docs.

---

## Phase 4: AI Agent (PRIORITY)

This is the core deliverable. Everything else is secondary.

### Component 1: LangGraph Agent with Memory

**What:** Conversational AI that remembers context across messages.

**Why Memory Matters:**
```
User: "Revenue for AI Video Generator?"
Agent: "$45,230 this week"
User: "Compare to last week"  ← Agent remembers which app
Agent: "Last week was $42,100, 7.4% increase"
```

**Course Materials:**
- `M04/W01/M04W01L01__AI_agents_overview.md` - Agent architecture, ReAct pattern
- `M04/W01/M04W01L02__langgraph_memory_state.md` - LangGraph checkpointers for memory
- `M04/W01/M04W01L03__lab_ai_agents_with_langgraph.md` - **START HERE** - Build your first agent

**Lab Code:**
```
fa-c002-hub/content/M04/W01/lab/
├── basic_agent.py           # Start here - minimal agent
├── persistent_agent.py      # Memory with PostgreSQL
├── streamlit_app.py         # UI reference
└── cli_interface.py         # CLI backup
```

**Implementation Pattern:**
```python
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph

checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)
graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
app = graph.compile(checkpointer=checkpointer)
```

---

### Component 2: Snowflake Query Tools

**What:** Python functions your agent calls to query the data warehouse.

**How It Works:**
1. User asks: "Total revenue this week?"
2. Agent decides to call `query_revenue` tool
3. Tool executes SQL against Snowflake
4. Tool returns result
5. Agent formats response

**Course Materials:**
- `M04/W02/M04W02L01__tools_calling_overview.md` - How LLMs call functions
- `M04/W02/M04W02L02__integrating_tools_with_agents.md` - Binding tools to agents
- `M04/W02/M04W02L03__lab_snowflake_tools.md` - **KEY LAB** - Building query tools

**Lab Code:**
```
fa-c002-hub/content/M04/W02/lab/
└── tool_calling_agent.py    # Tool integration patterns
```

**Example Tool:**
```python
@tool
def query_revenue(start_date: str, end_date: str, app_name: str = None) -> str:
    """Query ad revenue from Snowflake warehouse."""
    query = f"""
        SELECT SUM(ad_revenue) as total_revenue
        FROM analytics.fct_app_daily_performance f
        JOIN analytics.dim_dates d ON f.date_key = d.date_key
        WHERE d.date BETWEEN '{start_date}' AND '{end_date}'
        {f"AND app_name = '{app_name}'" if app_name else ""}
    """
    # Execute and return result
```

---

### Component 3: Business Query Tools

**Tools to Build:**

| Tool | Description | SQL Pattern |
|------|-------------|-------------|
| `get_revenue_summary` | Revenue for period | `SUM(ad_revenue) GROUP BY date` |
| `get_top_apps` | Ranked apps | `ORDER BY metric DESC LIMIT N` |
| `get_country_performance` | Revenue by country | `GROUP BY country_code` |
| `compare_platforms` | iOS vs Android | `GROUP BY platform` |
| `get_app_trends` | Day-over-day changes | Window functions |
| `get_marketing_roi` | Revenue vs spend | `ad_revenue - network_cost` |
| `get_d0_performance` | Day 0 payback analysis | `ad_revenue_d0 / ad_revenue` |

---

### Component 4: Streamlit UI

**What:** Web interface for executives to chat with the agent.

**Course Materials:**
- `M04/W01/M04W01L02__ai_agents_ui.md` - UI options comparison
- `M04/W01/lab/streamlit_app.py` - Reference implementation

**Implementation Pattern:**
```python
import streamlit as st
from agent import create_agent

st.title("Ameno Analytics Assistant")

if "agent" not in st.session_state:
    st.session_state.agent = create_agent()
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask about app performance..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = st.session_state.agent.invoke(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
```

---

### Component 5: RAG for Documentation

**What:** Agent answers questions about metrics and business context.

**Example:**
- "What does eCPM mean?" → Search docs for definition
- "How is revenue calculated?" → Explain AdMob vs Adjust

**Course Materials:**
- `M04/W03/M04W03L01__rag_overview.md` - RAG concepts
- `M04/W03/M04W03L01__document_processing.md` - Chunking strategies
- `M04/W03/M04W03L02__vector_databases.md` - Vector store options
- `M04/W03/M04W03L04__lab_rag_system.md` - **KEY LAB** - RAG implementation

**Lab Code:**
```
fa-c002-hub/content/M04/W03/lab/src/
├── document_loader.py   # Load and chunk docs
├── embeddings.py        # Generate embeddings
├── vector_store.py      # Store and retrieve
└── rag_chain.py         # Retrieval chain
```

---

### Component 6: System Prompt

**What:** Instructions that shape agent behavior.

**Course Materials:**
- `M04/W01/M04W01L02__prompt_engineering.md` - Prompt patterns
- `M04/W02/M04W02L01__context_engineering.md` - Context management

**Example:**
```python
SYSTEM_PROMPT = """You are an analytics assistant for Ameno Technologies.

DATA CONTEXT:
- AdMob (ad revenue) and Adjust (user metrics) data
- Aggregated daily by app, country, platform
- Revenue in USD, dates YYYY-MM-DD

RESPONSE GUIDELINES:
- Be concise but complete
- Include specific numbers
- Suggest follow-up questions
"""
```

---

## Phase 3: Kafka + Airflow

Minimal implementation for test requirement. Don't over-engineer.

### Component 1: Kafka Setup

**What:** Simulate streaming from CSV (data is daily batch).

**Course Materials:**
- `M03/W01/M03W01L02__kafka_architecture.md` - Kafka concepts
- `M03/W01/M03W01L03__lab_capstone_kafka_setup.md` - **START HERE** - Docker setup
- `M03/W01/M03W01L04__lab_capstone_python_kafka.md` - Producer/consumer code

**Lab Code:**
```
fa-c002-hub/content/M03/W01/lab/
├── docker-compose.yml       # Kafka + Zookeeper setup
├── producer.py              # Send messages to topic
└── consumer.py              # Read messages from topic
```

**Minimal Producer:**
```python
from kafka import KafkaProducer
import csv, json, time

producer = KafkaProducer(bootstrap_servers='localhost:9092')

with open('data/admob_latest.csv') as f:
    for row in csv.DictReader(f):
        producer.send('mobile-earnings', json.dumps(row).encode())
        time.sleep(0.1)  # Simulate real-time
```

---

### Component 2: Airflow Setup

**What:** Orchestrate dbt runs on schedule.

**Course Materials:**
- `M03/W02/M03W02L01__airflow_core_concepts.md` - DAGs, operators
- `M03/W02/M03W02L03__lab_capstone_airflow_setup.md` - **START HERE** - Docker setup
- `M03/W03/M03W03L03__lab_capstone_dbt_dag.md` - **KEY LAB** - dbt integration

**Lab Code:**
```
fa-c002-hub/content/M03/W02/lab/
├── docker-compose.yml       # Airflow setup
└── dags/
    └── dbt_pipeline.py      # Example DAG
```

**Minimal DAG:**
```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG('dbt_pipeline', start_date=datetime(2026, 1, 1), schedule_interval='@daily') as dag:
    dbt_run = BashOperator(task_id='dbt_run', bash_command='cd /opt/dbt && dbt run')
    dbt_test = BashOperator(task_id='dbt_test', bash_command='cd /opt/dbt && dbt test')
    dbt_run >> dbt_test
```

---

## Phase 5: Documentation & Demo

### Component 1: Agent Design Document

**Course Materials:**
- `M05/W01/M05W01L04__lab_capstone_agent_design.md` - Design doc template

**Required Sections:**
1. Problem Statement
2. Architecture Overview
3. Tool Descriptions
4. Data Flow Diagram
5. Safety Considerations

---

### Component 2: Guardrails

**Course Materials:**
- `M05/W01/M05W01L01__guardrails.md` - Input validation, output filtering
- `M05/W01/M05W01L01__human_in_the_loop.md` - Human approval patterns

---

### Component 3: Demo Preparation

**Course Materials:**
- `capstone/capstone_demo_guide.md` - Demo format
- `M05/W03/M05W03L04__lab_demo_preparation_and_final_review.md` - Practice checklist

---

## Demo Checklist

Must demonstrate live during final test:

- [ ] New data ingested (Kafka producer running)
- [ ] dbt executed via Airflow (show DAG run)
- [ ] CI/CD execution (GitHub Actions)
- [ ] Chatbot with conversation memory
- [ ] RAG document query ("What does eCPM mean?")
- [ ] Batch data query ("Revenue last week")
- [ ] Combined intelligence query

---

## Target Directory Structure

```
fa-c002-lab/
├── agent/                    # AI Agent
│   ├── agent.py              # LangGraph agent
│   ├── tools/
│   │   ├── snowflake_tools.py
│   │   └── business_tools.py
│   ├── prompts/
│   │   └── system_prompt.py
│   ├── rag/
│   │   └── retriever.py
│   └── app.py                # Streamlit UI
├── kafka/                    # Streaming
│   ├── docker-compose.yml
│   ├── producer.py
│   └── consumer.py
├── dags/                     # Airflow
│   └── dbt_pipeline.py
├── my_dbt_project/           # Existing (Done)
├── scripts/                  # Existing (Done)
└── .github/workflows/        # Existing (Done)
```

---

## Grading Breakdown (100 points)

| Section | Points | Status |
|---------|--------|--------|
| Data Ingestion & Orchestration | 15 | Phase 3 |
| Data Modeling & Transformation | 15 | Done |
| DevOps & CI | 5 | Done |
| Documentation | 5 | Phase 5 |
| AI Agent (RAG + memory) | 10 | Phase 4 |
| AI Agent (data querying) | 10 | Phase 4 |
| Extra Features | 40 | Bonus |

**Minimum to Pass:** 50 points | **Target:** 80+ points

---

## Example Business Questions

```
Revenue:
- "What's our total ad revenue this week?"
- "Which app generated the most revenue?"
- "Top 5 countries by revenue"

Day 0 Performance:
- "What's our D0 revenue percentage today?"
- "Which apps have best same-day payback?"
- "D0 performance by country"

User Acquisition:
- "How many installs last week?"
- "What's our cost per install by country?"
- "Compare iOS vs Android CPI"

Combined:
- "Explain the revenue change for AI Video Generator"
- "Why did ROAS drop in Thailand?"
```

---

## Quick Reference: What to Do Next

**If starting fresh:**
1. Read `M04/W01/M04W01L03__lab_ai_agents_with_langgraph.md`
2. Copy `basic_agent.py` from lab
3. Get one tool working (`query_revenue`)
4. Iterate from there

**Priority order:**
1. Phase 4 (AI Agent) - Production value
2. Phase 3 (Kafka + Airflow) - Test checkbox
3. Phase 5 (Docs + Demo) - Final polish
