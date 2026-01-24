# AI Agent

How the agent works, tools, and RAG implementation.

---

## Overview

The agent answers business questions using 3 data sources:

```
User Question
     │
     ▼
┌─────────────────────────────────────────┐
│            LangGraph Agent              │
│                                         │
│  System Prompt → LLM → Tool Selection   │
│                                         │
└─────────────────────────────────────────┘
     │
     ├── query_snowflake ────────► Snowflake (batch data)
     ├── query_realtime_alerts ──► PostgreSQL (streaming)
     └── search_business_documents ► FAISS (RAG)
     │
     ▼
   Answer
```

---

## Files

| File | Purpose |
|------|---------|
| `agent/agent.py` | LangGraph state machine |
| `agent/prompts.py` | System prompt |
| `agent/config.py` | API keys, model settings |
| `agent/app.py` | Streamlit UI |
| `agent/rag_demo.py` | RAG explanation demo |
| `agent/tools/snowflake_tools.py` | Snowflake queries |
| `agent/tools/kafka_tools.py` | PostgreSQL alerts |
| `agent/tools/rag_tools.py` | RAG search |

---

## Tools

### 1. query_snowflake

**File:** `agent/tools/snowflake_tools.py`

**Use for:**
- Revenue questions: "What's total revenue?"
- Cost questions: "How much did we spend?"
- Metric questions: "What's our D0 ROAS?"
- Historical data: "Show me last week's performance"

**How it works:**
```python
@tool
def query_snowflake(sql_query: str) -> str:
    """Execute SQL on Snowflake ANALYTICS schema."""
    client = get_snowflake_client(schema="ANALYTICS")
    df = client.execute_query(sql_query)
    return df.to_string(index=False)
```

**Example:**
```sql
SELECT SUM(ad_revenue) as total_revenue
FROM fct_app_daily_performance
WHERE date >= '2026-01-01'
```

---

### 2. query_realtime_alerts

**File:** `agent/tools/kafka_tools.py`

**Use for:**
- Alert questions: "Any alerts?"
- Critical issues: "Show me critical alerts"
- Recent problems: "What happened in the last hour?"

**How it works:**
```python
@tool
def query_realtime_alerts(severity: str = "all", limit: int = 10) -> str:
    """Query alerts from streaming pipeline."""
    conn = psycopg2.connect(
        host="localhost", port=5433,
        database="streaming", user="postgres", password="postgres"
    )
    cur.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT %s", (limit,))
    return format_alerts(cur.fetchall())
```

**Alert types:**
- `ROAS_DROP` - ROAS below threshold
- `BUDGET_EXCEED` - Budget overspent
- `CPI_SPIKE` - CPI too high
- `INSTALL_DROP` - Installs dropping

---

### 3. search_business_documents

**File:** `agent/tools/rag_tools.py`

**Use for:**
- Rules: "What's the ROAS threshold?"
- Guidelines: "How do we handle CPI spikes?"
- Definitions: "What is D0 ROAS?"

**How it works:**
```python
@tool
def search_business_documents(query: str, num_results: int = 3) -> str:
    """Search business rules using RAG."""
    vector_store = get_vector_store()  # FAISS
    results = vector_store.similarity_search(query, k=num_results)
    return format_results(results)
```

**Document source:** `docs/business_rules/ameno_business_rules.md`

---

## RAG Implementation

### Pipeline

```
Document → Chunk → Embed → FAISS Index
                              ↑
Query → Embed Query → Search ─┘
                              ↓
                        Top K Results → LLM → Answer
```

### Chunking

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # ~500 characters per chunk
    chunk_overlap=50,     # 50 char overlap
    separators=["\n---\n", "\n## ", "\n### ", "\n\n", "\n", " "]
)
```

**Why 500 chars?**
- Small enough to be specific
- Large enough to have context
- Fits well with embedding model

### Embedding

- **Model:** OpenAI `text-embedding-ada-002`
- **Dimensions:** 1536
- **How:** Text → API call → Vector

**Similarity proof:**
```python
# Similar texts have high cosine similarity
"ROAS threshold is 80%" vs "80% is the ROAS threshold" → 0.92

# Different texts have low similarity
"ROAS threshold is 80%" vs "The weather is nice" → 0.69
```

### Vector Store

- **Engine:** FAISS (Facebook AI Similarity Search)
- **Location:** `agent/vector_store/` (auto-generated)
- **Persistence:** Saved locally, reloads on restart

**Why FAISS?**
- Free, no external service needed
- Fast for small documents
- Works offline

---

## System Prompt

**File:** `agent/prompts.py`

Key sections:
1. **Role:** "You are a data analyst for Ameno Technologies"
2. **User context:** Chi Linh, Business Controller
3. **Three tools:** When to use each
4. **Thresholds:** ROAS < 80% = losing money
5. **Table schemas:** Available tables in Snowflake

---

## LangGraph Architecture

**File:** `agent/agent.py`

```python
# State machine
graph = StateGraph(AgentState)
graph.add_node("agent", call_model)    # LLM decision
graph.add_node("tools", ToolNode)      # Tool execution
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue)  # tool call or end
graph.add_edge("tools", "agent")       # return to LLM

# Memory (conversation history)
memory = MemorySaver()
agent = graph.compile(checkpointer=memory)
```

**Flow:**
1. User message → Agent node
2. Agent decides: call tool or respond
3. If tool: execute → return to agent
4. If respond: end

---

## Running the Agent

### Streamlit UI
```bash
uv run streamlit run agent/app.py
# Opens http://localhost:8501
```

### CLI - Single Query
```bash
uv run python -m agent.agent -q "What's our total revenue?"
```

### CLI - Interactive
```bash
uv run python -m agent.agent --interactive
```

### RAG Demo (for explanation)
```bash
uv run python agent/rag_demo.py
```

---

## Example Session

```
You: What's our total revenue this week?
Agent: [Uses query_snowflake]
       Total Revenue: $251,878.48
       D0 ROAS: 74.99%

You: Any critical alerts?
Agent: [Uses query_realtime_alerts]
       3 critical alerts:
       - ROAS_DROP: Thailand below 60%
       - BUDGET_EXCEED: US campaign over budget

You: What should I do about Thailand?
Agent: [Uses search_business_documents + query_snowflake]
       Based on business rules, ROAS below 60% requires
       immediate action. Recommend reducing spend by 30%.
```

---

## Configuration

**File:** `.env`

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4o
```

**Snowflake:** Uses RSA key at `~/.snowflake/keys/rsa_key.p8`

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| OPENAI_API_KEY not found | `cat .env \| grep OPENAI` |
| Snowflake connection failed | `ls ~/.snowflake/keys/rsa_key.p8` |
| Streaming DB not found | `docker ps \| grep capstone` |
| No business docs | `ls docs/business_rules/` |
