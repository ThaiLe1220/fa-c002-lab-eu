# AI Agent Guide

How the AI Agent works, from high level to low level.

---

## Part 1: High Level - What It Does

### Purpose

The agent answers business questions about mobile app performance by querying Snowflake data.

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
│   2. Generates SQL query                                     │
│   3. Executes query on Snowflake                            │
│   4. Interprets results with business context               │
│   5. Returns actionable answer                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        ANSWER                                │
│  "ai.video.template.videogenerator has D0 ROAS of 2.86%     │
│   (losing money). Recommend pausing ad spend."               │
└─────────────────────────────────────────────────────────────┘
```

### Key Capabilities

| Capability | Example |
|------------|---------|
| Query data | "What's total revenue?" |
| Calculate metrics | "What's our D0 ROAS?" |
| Compare periods | "Compare this week vs last week" |
| Drill down | "Which app? Which country?" |
| Recommend actions | "Should I turn off this app?" |
| Remember context | "What about its CPI?" (follows up) |

### Business Context

The agent knows:
- **Metric definitions**: ROAS, CPI, eCPM, IMPDAU, LTV
- **Thresholds**: ROAS < 80% = losing money
- **Data structure**: 59 apps, 240 countries, 29 days of data
- **User**: Chi Linh (Business Controller) who sets targets and tracks profitability

---

## Part 2: Mid Level - How Components Connect

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI                             │
│                     (agent/app.py)                           │
│                                                              │
│   - Chat interface                                           │
│   - Message history                                          │
│   - Quick question buttons                                   │
└─────────────────────────────────────────────────────────────┘
                              │
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
│                              │                              │
│                              ▼                              │
│                       ┌─────────────┐                       │
│                       │     END     │                       │
│                       └─────────────┘                       │
│                                                              │
│   + Memory (conversation history per thread)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM PROMPT                             │
│                   (agent/prompts.py)                         │
│                                                              │
│   - Role: "You are a data analyst for Ameno Technologies"   │
│   - Schema: Tables, columns, relationships                   │
│   - Metrics: ROAS, CPI, eCPM formulas                       │
│   - Thresholds: ROAS < 80% = losing money                   │
│   - Guidelines: Format numbers, suggest actions              │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ calls
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   SNOWFLAKE TOOL                             │
│            (agent/tools/snowflake_tools.py)                  │
│                                                              │
│   @tool                                                      │
│   def query_snowflake(sql_query: str) -> str:               │
│       # Connect to Snowflake                                 │
│       # Execute SQL                                          │
│       # Return formatted results                             │
│                                                              │
│   Uses: scripts/utils/snowflake_client.py                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ queries
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      SNOWFLAKE                               │
│                   DB_T34.ANALYTICS                           │
│                                                              │
│   - fct_app_daily_performance (140K rows)                   │
│   - dim_apps (59 apps)                                       │
│   - dim_dates (29 days)                                      │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
agent/
├── __init__.py              # Package marker
├── config.py                # OpenAI API key, model settings
├── prompts.py               # System prompt with business context
├── agent.py                 # LangGraph state machine + chat()
├── app.py                   # Streamlit UI
└── tools/
    ├── __init__.py
    └── snowflake_tools.py   # query_snowflake() tool
```

### Data Flow

1. **User types question** in Streamlit UI
2. **UI calls `chat(message, thread_id)`** in agent.py
3. **Agent invokes LLM** with system prompt + conversation history
4. **LLM decides** to call `query_snowflake` tool with generated SQL
5. **Tool executes SQL** on Snowflake, returns results
6. **LLM interprets results** with business context
7. **Agent returns response** to UI
8. **UI displays response** to user

---

## Part 3: Low Level - Code Walkthrough

### 3.1 Configuration (agent/config.py)

```python
# Load API key from .secret/.env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = 0  # Deterministic responses
```

**Key points:**
- Uses gpt-4o-mini (cheap, fast, good enough)
- Temperature 0 for consistent SQL generation
- API key loaded from `.secret/.env`

### 3.2 Snowflake Tool (agent/tools/snowflake_tools.py)

```python
@tool
def query_snowflake(sql_query: str) -> str:
    """
    Execute a SQL query against Snowflake analytics tables.

    [Docstring includes schema info for LLM to understand]
    """
    client = get_snowflake_client(schema="ANALYTICS")
    df = client.execute_query(sql_query)
    return df.to_string(index=False)
```

**Key points:**
- `@tool` decorator makes it callable by LangGraph
- Docstring is crucial - LLM reads it to understand how to use the tool
- Returns formatted string (not DataFrame) for LLM to interpret
- Uses existing `snowflake_client.py` for connection

### 3.3 System Prompt (agent/prompts.py)

```python
SYSTEM_PROMPT = """
You are a data analyst assistant for Ameno Technologies...

## Your Role
- Answer questions about app revenue, costs, and profitability
- Calculate business metrics (ROAS, CPI, eCPM, etc.)

## Data Context
- Date range: Dec 25, 2025 to Jan 22, 2026
- Apps: 59 apps
- Tables: fct_app_daily_performance, dim_apps, dim_dates

## Key Metrics
- d0_roas = ad_revenue_d0 / network_cost
- cpi = network_cost / installs

## Thresholds
- D0 ROAS > 100%: Profitable
- D0 ROAS < 80%: Losing money, needs action
"""
```

**Key points:**
- Tells LLM its role and capabilities
- Provides schema context so LLM can write correct SQL
- Includes metric formulas for calculations
- Includes business thresholds for interpretation

### 3.4 LangGraph Agent (agent/agent.py)

```python
# 1. Create LLM with tools
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
tools = [query_snowflake]
llm_with_tools = llm.bind_tools(tools)

# 2. Define state (conversation history)
class AgentState(MessagesState):
    pass

# 3. Define agent node (calls LLM)
def call_model(state: AgentState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 4. Define routing (continue to tools or end?)
def should_continue(state: AgentState):
    if state["messages"][-1].tool_calls:
        return "tools"  # LLM wants to call a tool
    return "__end__"    # LLM is done, return response

# 5. Build graph
graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")  # After tool, go back to agent

# 6. Compile with memory
memory = MemorySaver()
agent = graph.compile(checkpointer=memory)
```

**Key points:**
- `MessagesState` tracks conversation history
- `should_continue` decides: call tool or return answer
- Loop: agent → tools → agent (until done)
- `MemorySaver` enables conversation memory across calls

### 3.5 Chat Function (agent/agent.py)

```python
def chat(message: str, thread_id: str = "default") -> str:
    """Send message, get response. Thread ID enables memory."""
    config = {"configurable": {"thread_id": thread_id}}

    result = agent.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )

    return result["messages"][-1].content
```

**Key points:**
- `thread_id` groups conversations (same thread = shared memory)
- Returns just the final response content

### 3.6 Streamlit UI (agent/app.py)

```python
# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask about app performance..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get agent response
    response = chat(prompt, st.session_state.thread_id)

    # Add agent response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
```

**Key points:**
- `st.session_state` persists data across reruns
- `st.chat_message` displays messages with proper styling
- `st.chat_input` provides the input box
- Calls `chat()` from agent.py

---

## Part 4: How to Run

### Prerequisites

```bash
# 1. OpenAI API key in .secret/.env
OPENAI_API_KEY=sk-your-key-here

# 2. Snowflake RSA key at ~/.snowflake/keys/rsa_key.p8
```

### Commands

```bash
# Activate environment
cd /Users/lehongthai/code_personal/fa-c002-lab
source .venv/bin/activate

# Option 1: CLI mode (for testing)
uv run python -m agent.agent --interactive

# Option 2: Single query
uv run python -m agent.agent --query "What's our ROAS?"

# Option 3: Streamlit UI (for demo)
uv run streamlit run agent/app.py
```

### Example Session

```
You: What's our total revenue?

Agent:
1. **Total Revenue:** $251,878.48
2. **Total Cost:** $245,940.12
3. **D0 ROAS:** 74.99% (losing money)

Insight: ROAS below 80% indicates we're losing money on user acquisition.

You: Which apps are causing this?

Agent:
Apps with D0 ROAS < 80%:
| App Name | Cost | D0 ROAS |
|----------|------|---------|
| ai.video.template.videogenerator | $418 | 2.86% |
| Video AI Generator | $59,718 | 67.56% |
...

Recommendation: Consider pausing ad spend on worst performers.
```

---

## Part 5: How It Handles Different Questions

### Simple Query
```
User: "How many apps do we have?"

Agent thinking:
1. Need to count distinct apps
2. Generate SQL: SELECT COUNT(DISTINCT app_key) FROM dim_apps
3. Execute → 59
4. Answer: "We have 59 apps."
```

### Calculation Query
```
User: "What's our D0 ROAS?"

Agent thinking:
1. ROAS = revenue / cost
2. Generate SQL: SELECT SUM(ad_revenue_d0) / NULLIF(SUM(network_cost), 0)
3. Execute → 0.7499
4. Interpret: 74.99% is below 80% threshold
5. Answer: "D0 ROAS is 74.99% (losing money)"
```

### Follow-up Query (uses memory)
```
User: "What about for Thailand specifically?"

Agent thinking:
1. Previous question was about ROAS
2. Now filter by country_code = 'TH'
3. Generate SQL with WHERE country_code = 'TH'
4. Execute → 0.617
5. Answer: "Thailand D0 ROAS is 61.7% (also losing money)"
```

### Comparison Query
```
User: "Compare this week vs last week"

Agent thinking:
1. Need two date ranges
2. Generate SQL with CTEs for each period
3. Execute → revenue up 70%, ROAS up 9 points
4. Answer with change analysis
```

---

## Part 6: Troubleshooting

### "OPENAI_API_KEY not found"
```bash
# Check .secret/.env exists and has key
cat .secret/.env | grep OPENAI
```

### "Snowflake connection failed"
```bash
# Check RSA key exists
ls ~/.snowflake/keys/rsa_key.p8

# Test connection
uv run python -c "from scripts.utils.snowflake_client import get_snowflake_client; c = get_snowflake_client(); c.connect(); print('OK')"
```

### "Agent gives wrong SQL"
- Check `agent/prompts.py` has correct schema
- Check `agent/tools/snowflake_tools.py` docstring matches actual tables

### "Slow responses"
- Normal: 3-8 seconds (Snowflake query + LLM)
- If >15s: Check Snowflake warehouse is running

---

## Part 7: Key Files Reference

| File | Purpose | Key Function |
|------|---------|--------------|
| `agent/config.py` | Settings | Load API keys |
| `agent/prompts.py` | Business context | SYSTEM_PROMPT |
| `agent/tools/snowflake_tools.py` | Data access | query_snowflake() |
| `agent/agent.py` | Core logic | chat(), create_agent() |
| `agent/app.py` | UI | Streamlit interface |
| `scripts/utils/snowflake_client.py` | DB connection | SnowflakeClient |

---

## Revision History

| Date | Change |
|------|--------|
| 2026-01-24 | Initial creation |
