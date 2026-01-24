# AI Agent Guide

How the AI Agent works, from high level to low level.

**Status:** COMPLETE - All 3 tools implemented

---

## Part 1: High Level - What It Does

### Purpose

The agent answers business questions by querying three data sources:
1. **Snowflake** - Historical batch data (revenue, costs, metrics)
2. **PostgreSQL** - Real-time streaming alerts
3. **FAISS** - Business rules and documentation

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│            "Which app is losing money?"                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI AGENT                                │
│                                                              │
│   1. Understands the question                                │
│   2. Chooses appropriate tool(s)                            │
│   3. Executes query on data source                          │
│   4. Interprets results with business context               │
│   5. Returns actionable answer                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        ANSWER                                │
│  "ai.video.template.videogenerator has D0 ROAS of 2.86%     │
│   (losing money). Based on business rules, recommend        │
│   pausing ad spend immediately."                            │
└─────────────────────────────────────────────────────────────┘
```

### Three Tools

| Tool | Data Source | Use Case |
|------|-------------|----------|
| `query_snowflake` | Snowflake | Revenue, costs, metrics, historical data |
| `query_realtime_alerts` | PostgreSQL | Real-time alerts from Kafka pipeline |
| `search_business_documents` | FAISS | Business rules, thresholds, guidelines |

### Key Capabilities

| Capability | Example | Tool Used |
|------------|---------|-----------|
| Query data | "What's total revenue?" | Snowflake |
| Calculate metrics | "What's our D0 ROAS?" | Snowflake |
| Check alerts | "Show me critical alerts" | Kafka |
| Find rules | "What's the ROAS threshold?" | RAG |
| Combined query | "Which apps violate our rules?" | All 3 |
| Remember context | "What about its CPI?" | Memory |

### Business Context

The agent knows:
- **Metric definitions**: ROAS, CPI, eCPM, IMPDAU, LTV
- **Thresholds**: ROAS < 80% = losing money (from RAG)
- **Data structure**: 59 apps, 240 countries, 29 days of data
- **User**: Chi Linh (Business Controller) who sets targets

---

## Part 2: Mid Level - How Components Connect

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI                             │
│                     (agent/app.py)                           │
└─────────────────────────────────────────────────────────────┘
                              │ calls chat()
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LANGGRAPH AGENT                           │
│                    (agent/agent.py)                          │
│                                                              │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│   │    START    │────▶│    AGENT    │────▶│    TOOLS    │  │
│   └─────────────┘     │   (LLM)     │     │             │  │
│                       └─────────────┘     └─────────────┘  │
│                              │                   │          │
│                              │◀──────────────────┘          │
│                              ▼                              │
│                       ┌─────────────┐                       │
│                       │     END     │                       │
│                       └─────────────┘                       │
│                                                              │
│   + Memory (conversation history per thread)                 │
└─────────────────────────────────────────────────────────────┘
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM PROMPT                             │
│                   (agent/prompts.py)                         │
│                                                              │
│   - Role: "You are a data analyst for Ameno Technologies"   │
│   - 3 tools explained with when to use each                 │
│   - Thresholds: ROAS < 80% = losing money                   │
└─────────────────────────────────────────────────────────────┘
                              │ calls
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      THREE TOOLS                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ query_snowflake │  │ query_realtime  │  │ search_     │ │
│  │                 │  │ _alerts         │  │ business_   │ │
│  │ Snowflake       │  │ PostgreSQL      │  │ documents   │ │
│  │ (batch data)    │  │ (streaming)     │  │ (FAISS)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
agent/
├── __init__.py              # Package marker
├── config.py                # OpenAI API key, model settings
├── prompts.py               # System prompt with 3-tool guidance
├── agent.py                 # LangGraph state machine + chat()
├── app.py                   # Streamlit UI
├── rag_demo.py              # Interactive RAG explanation
├── vector_store/            # FAISS index (auto-generated)
└── tools/
    ├── __init__.py
    ├── snowflake_tools.py   # query_snowflake() - batch data
    ├── kafka_tools.py       # query_realtime_alerts() - streaming
    └── rag_tools.py         # search_business_documents() - RAG
```

### Data Flow

1. **User types question** in Streamlit UI
2. **UI calls `chat(message, thread_id)`** in agent.py
3. **Agent invokes LLM** with system prompt + conversation history
4. **LLM decides** which tool(s) to call based on question
5. **Tool executes** query on appropriate data source
6. **LLM interprets results** with business context
7. **Agent returns response** to UI
8. **UI displays response** to user

---

## Part 3: Low Level - Code Walkthrough

### 3.1 Configuration (agent/config.py)

```python
# Load API key from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = 0  # Deterministic responses
```

### 3.2 Three Tools

**Snowflake Tool (batch data):**
```python
@tool
def query_snowflake(sql_query: str) -> str:
    """Execute SQL on Snowflake analytics tables."""
    client = get_snowflake_client(schema="ANALYTICS")
    df = client.execute_query(sql_query)
    return df.to_string(index=False)
```

**Kafka Tool (streaming alerts):**
```python
@tool
def query_realtime_alerts(severity: str = "all", limit: int = 10) -> str:
    """Query real-time alerts from streaming pipeline."""
    conn = get_streaming_db()  # PostgreSQL port 5433
    cur = conn.cursor()
    cur.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT %s", (limit,))
    return format_alerts(cur.fetchall())
```

**RAG Tool (business documents):**
```python
@tool
def search_business_documents(query: str, num_results: int = 3) -> str:
    """Search business rules and documentation."""
    vector_store = get_vector_store()  # FAISS with OpenAI embeddings
    results = vector_store.similarity_search(query, k=num_results)
    return format_results(results)
```

### 3.3 System Prompt (agent/prompts.py)

```python
SYSTEM_PROMPT = """
You are a data analyst assistant for Ameno Technologies...

## Three Tools for Three Systems

1. **query_snowflake** - For batch analytics data
   - Use for: "What's our revenue?", "Show me top apps"

2. **query_realtime_alerts** - For streaming alerts
   - Use for: "Any alerts?", "Show critical alerts"

3. **search_business_documents** - For business rules
   - Use for: "What's the threshold for X?"

## How to Work
1. Determine which tool(s) you need
2. For data questions: use query_snowflake
3. For alert questions: use query_realtime_alerts
4. For policy/rule questions: use search_business_documents
5. For combined questions: use multiple tools
"""
```

### 3.4 LangGraph Agent (agent/agent.py)

```python
# 1. Create LLM with all 3 tools
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
tools = [query_snowflake, query_realtime_alerts, search_business_documents]
llm_with_tools = llm.bind_tools(tools)

# 2. Define state (conversation history)
class AgentState(MessagesState):
    pass

# 3. Build graph
graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")

# 4. Compile with memory
memory = MemorySaver()
agent = graph.compile(checkpointer=memory)
```

---

## Part 4: How to Run

### Prerequisites

```bash
# 1. OpenAI API key in .env
OPENAI_API_KEY=sk-your-key-here

# 2. Snowflake RSA key at ~/.snowflake/keys/rsa_key.p8

# 3. Kafka + PostgreSQL running (for streaming alerts)
cd kafka && docker-compose up -d
```

### Commands

```bash
# Option 1: CLI mode
uv run python -m agent.agent --interactive

# Option 2: Single query
uv run python -m agent.agent -q "What's our ROAS?"

# Option 3: Streamlit UI
uv run streamlit run agent/app.py

# Option 4: RAG demo (explains chunking + embedding)
uv run python agent/rag_demo.py
```

### Example Session

```
You: What's our total revenue this week?
Agent: [Uses query_snowflake]
       Total Revenue: $251,878.48
       D0 ROAS: 74.99% (losing money)

You: Are there any alerts I should know about?
Agent: [Uses query_realtime_alerts]
       3 critical alerts in the last hour:
       🔴 ROAS_DROP - Thailand region below threshold

You: What should I do about the Thailand issue?
Agent: [Uses search_business_documents + query_snowflake]
       Based on business rules, ROAS below 60% requires
       immediate action. Thailand D0 ROAS is 61.7%.
       Recommend reducing spend by 30%.
```

---

## Part 5: RAG Implementation Details

### How RAG Works

```
Document → Chunking → Embedding → FAISS Vector Store
                                        ↑
Query → Embed Query → Similarity Search─┘
                                        ↓
                                 Top K Chunks → LLM → Answer
```

### Components

| Component | Location | Description |
|-----------|----------|-------------|
| Business Rules | `docs/business_rules/ameno_business_rules.md` | ROAS thresholds, CPI benchmarks |
| Vector Store | `agent/vector_store/` | FAISS index (auto-generated) |
| RAG Tool | `agent/tools/rag_tools.py` | search_business_documents() |
| Demo Script | `agent/rag_demo.py` | Interactive explanation |

### Chunking Settings

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # ~500 characters per chunk
    chunk_overlap=50,     # 50 char overlap
    separators=["\n---\n", "\n## ", "\n### ", "\n\n", "\n", " "]
)
```

### Embedding

- Model: OpenAI `text-embedding-ada-002`
- Dimensions: 1536
- Similar text → Similar vectors (proven with cosine similarity)

---

## Part 6: Troubleshooting

### "OPENAI_API_KEY not found"
```bash
cat .env | grep OPENAI
```

### "Snowflake connection failed"
```bash
ls ~/.snowflake/keys/rsa_key.p8
uv run python -c "from scripts.utils.snowflake_client import get_snowflake_client; c = get_snowflake_client(); c.connect(); print('OK')"
```

### "Cannot connect to streaming database"
```bash
cd kafka && docker-compose up -d
docker ps | grep capstone
```

### "No business documents found"
```bash
ls docs/business_rules/
# Should show ameno_business_rules.md
```

---

## Part 7: Key Files Reference

| File | Purpose | Key Function |
|------|---------|--------------|
| `agent/config.py` | Settings | Load API keys |
| `agent/prompts.py` | Business context | SYSTEM_PROMPT |
| `agent/tools/snowflake_tools.py` | Batch data | query_snowflake() |
| `agent/tools/kafka_tools.py` | Streaming | query_realtime_alerts() |
| `agent/tools/rag_tools.py` | Documents | search_business_documents() |
| `agent/agent.py` | Core logic | chat(), create_agent() |
| `agent/app.py` | UI | Streamlit interface |
| `agent/rag_demo.py` | Demo | Interactive RAG explanation |

---

## Revision History

| Date | Change |
|------|--------|
| 2026-01-24 | Updated for all 3 tools (Snowflake, Kafka, RAG) |
| 2026-01-24 | Initial creation |
