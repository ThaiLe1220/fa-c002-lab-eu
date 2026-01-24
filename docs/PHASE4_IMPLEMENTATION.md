# Phase 4: AI Agent Implementation Plan

Comprehensive implementation guide for the AI Agent phase.

**Start Date:** 2026-01-23
**Demo Date:** 2026-01-24, 1:00 PM
**Status:** COMPLETE (All 3 tools: Snowflake + Kafka + RAG)

---

## Executive Summary

Build an AI chatbot that queries Snowflake data to answer Chi Linh's business questions. The agent translates natural language → SQL → formatted insights.

```
┌─────────────────────────────────────────────────────────────┐
│                      USER (Chi Linh)                         │
│              "Which app spent most this week?"               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     AI AGENT (LangGraph)                     │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ System Prompt: Metric definitions, thresholds, context  ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Snowflake   │  │ Kafka       │  │ RAG         │         │
│  │ Tool (CORE) │  │ Tool (opt)  │  │ Tool (opt)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT UI                              │
│                  Chat interface for demo                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 1: Core Requirements

### 1.1 Must Have (Demo Blockers)

| Component | Description | Points |
|-----------|-------------|--------|
| Snowflake Tool | Execute SQL on fact table, return results | 10 |
| LangGraph Agent | State graph with tool calling + memory | - |
| System Prompt | Metric definitions, Chi Linh's thresholds | - |
| Streamlit UI | Chat interface for demo | - |

### 1.2 Additional Tools (Checkboxes) - COMPLETE

| Component | Description | Points | Status |
|-----------|-------------|--------|--------|
| Kafka Tool | Query streaming alerts from PostgreSQL | 5 | DONE |
| RAG Tool | Search business rules via FAISS | 5 | DONE |
| Compare Tool | Compare two time periods | Extra | Not needed |
| Drill-down Tool | Breakdown by dimension | Extra | Not needed |

### 1.3 Out of Scope

- Real-time alerting (Phase 4 of agent capabilities)
- Production deployment
- Authentication/authorization
- Forecasting/predictions

---

## Part 2: Technical Architecture

### 2.1 File Structure - IMPLEMENTED

```
agent/
├── __init__.py
├── config.py                 # Environment config, loads from .env
├── agent.py                  # LangGraph state graph with 3 tools
├── prompts.py                # System prompt with 3-tool guidance
├── app.py                    # Streamlit UI
├── rag_demo.py               # Interactive RAG explanation demo
├── vector_store/             # FAISS index (auto-generated)
└── tools/
    ├── __init__.py
    ├── snowflake_tools.py    # query_snowflake - batch data
    ├── kafka_tools.py        # query_realtime_alerts - streaming
    └── rag_tools.py          # search_business_documents - RAG
```

### 2.2 Dependencies

```toml
# Add to pyproject.toml
openai = ">=1.0.0"
langchain = ">=0.1.0"
langgraph = ">=0.1.0"
langchain-openai = ">=0.1.0"
streamlit = ">=1.28.0"
```

### 2.3 Environment Variables

```bash
# Add to .secret/.env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0
OPENAI_MAX_TOKENS=2000
```

### 2.4 Snowflake Tool Design

**Philosophy:** Single flexible SQL tool. Agent generates SQL based on natural language.

```python
@tool
def query_snowflake(sql_query: str) -> str:
    """
    Execute a SQL query against the Snowflake analytics schema.

    Available tables:
    - fct_app_daily_performance: Daily metrics by app, country, platform
    - dim_apps: App metadata (app_key, app_store_id, app_name)
    - dim_dates: Date dimension (date_key, date, year, month, day_of_week)

    Key columns in fct_app_daily_performance:
    - ad_revenue: AdMob revenue (source of truth)
    - ad_revenue_d0, ad_revenue_d7: Cohort revenue for LTV
    - network_cost: UA spend
    - installs, daus: User metrics
    - country_code, platform: Dimensions

    Common metrics to calculate:
    - d0_roas = ad_revenue_d0 / network_cost
    - cpi = network_cost / installs
    - ecpm = ad_revenue * 1000 / ad_impressions

    Args:
        sql_query: Valid Snowflake SQL query

    Returns:
        Query results as formatted string
    """
    # Execute and return results
```

**Why single tool:**
- More flexible - agent can answer any question
- Simpler implementation - one function to maintain
- Better for demo - shows SQL generation capability

### 2.5 Agent State Graph

```python
from langgraph.graph import StateGraph, MessagesState

# State includes conversation history
class AgentState(MessagesState):
    pass

# Nodes
def call_model(state: AgentState):
    """LLM decides to respond or call tool"""

def call_tool(state: AgentState):
    """Execute the tool and return result"""

# Graph
graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", call_tool)
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, ["tools", END])
graph.add_edge("tools", "agent")
```

### 2.6 System Prompt Structure

```python
SYSTEM_PROMPT = """
You are a data analyst assistant for Ameno Technologies mobile app business.
You help Chi Linh (Business Performance Controller) analyze app performance.

## Your Capabilities
- Query Snowflake data warehouse using SQL
- Calculate business metrics (ROAS, CPI, eCPM, etc.)
- Explain metric changes with drill-down analysis
- Compare time periods

## Data Context
- Data range: Dec 25, 2025 to Jan 22, 2026 (29 days)
- Apps: 59 apps in portfolio
- Countries: 240 countries
- Grain: One row per app × date × country × platform

## Key Tables
{table_schemas}

## Metric Definitions
{metric_definitions}

## Chi Linh's Thresholds
- D0 ROAS > 100%: Profitable, can scale
- D0 ROAS 80-100%: Marginal, check D7 ROAS
- D0 ROAS < 80%: Losing money, needs action
- CPI increase > 30%: Check auction, creative fatigue
- eCPM drop > 15%: Check ad network issues

## Response Guidelines
1. Always show the SQL query you're executing
2. Format numbers with appropriate precision (currency: $X.XX, percentages: X.X%)
3. When explaining changes, identify the largest contributing factor
4. Suggest actionable next steps when issues are found

## Drill-Down Hierarchy
When analyzing issues, follow this order:
Total → App → Country → (Ad Source - not available)
"""
```

---

## Part 3: Implementation Tasks

### Phase 4.1: Snowflake Tool (Priority 1) - COMPLETE

- [x] Create `agent/tools/snowflake_tools.py`
- [x] Implement `query_snowflake()` function using existing `snowflake_client`
- [x] Add proper error handling (connection, SQL errors)
- [x] Test with 5 sample queries
- [x] Verify results match direct Snowflake query

**Verification:**
```bash
# Test query tool directly
uv run python agent/tools/snowflake_tools.py
```

### Phase 4.2: LangGraph Agent (Priority 2) - COMPLETE

- [x] Create `agent/config.py` with environment setup
- [x] Create `agent/prompts.py` with system prompt
- [x] Create `agent/agent.py` with StateGraph
- [x] Bind Snowflake tool to agent
- [x] Add conversation memory
- [x] Test with CLI interface

**Verification:**
```bash
# Test agent via CLI
uv run python -m agent.agent --interactive
```

### Phase 4.3: Streamlit UI (Priority 3) - COMPLETE

- [x] Create `agent/app.py` with Streamlit chat
- [x] Add conversation history display
- [ ] Add "Show SQL" toggle (nice to have)
- [x] Style for demo presentation
- [x] Test full flow

**Verification:**
```bash
# Run Streamlit
uv run streamlit run agent/app.py
```

### Phase 4.4: Optional Checkboxes - COMPLETE

**Kafka Tool - DONE:**
- [x] Create `kafka/docker-compose.yml` (Kafka KRaft + PostgreSQL)
- [x] Create `kafka/producer.py` with fake alerts (--batch mode)
- [x] Create `kafka/consumer.py` to write to PostgreSQL
- [x] Create `agent/tools/kafka_tools.py` (query_realtime_alerts)
- [x] Add to agent tools

**RAG Tool - DONE:**
- [x] Create `docs/business_rules/ameno_business_rules.md` (ROAS thresholds, CPI benchmarks)
- [x] Create FAISS vector store with OpenAI embeddings
- [x] Create `agent/tools/rag_tools.py` (search_business_documents)
- [x] Create `agent/rag_demo.py` for demo explanation
- [x] Add to agent tools

---

## Part 4: Verification Strategy

### 4.1 Chi Linh's 10 Questions Test

Each question from AI_AGENT_SPEC.md with expected SQL and answer format.

#### Question 1: "Which app spends most, and is it profitable?"

**Expected SQL:**
```sql
SELECT
    a.app_name,
    SUM(f.network_cost) as total_cost,
    SUM(f.ad_revenue_d0) as total_revenue_d0,
    SUM(f.ad_revenue_d0) / NULLIF(SUM(f.network_cost), 0) as d0_roas
FROM analytics.fct_app_daily_performance f
JOIN analytics.dim_apps a ON f.app_key = a.app_key
GROUP BY a.app_name
ORDER BY total_cost DESC
LIMIT 5
```

**Expected Answer Format:**
```
Top spending apps this period:

1. [App Name] - $X,XXX spent
   - D0 ROAS: XX% (profitable/losing)
   - Revenue: $X,XXX

2. [App Name] - $X,XXX spent
   ...

Summary: X apps profitable, Y apps losing money.
```

**Verification:** Run SQL directly in Snowflake, compare to agent answer.

---

#### Question 2: "Why did metrics change vs yesterday?"

**Expected SQL:**
```sql
WITH yesterday AS (
    SELECT SUM(ad_revenue_d0) as rev, SUM(network_cost) as cost
    FROM analytics.fct_app_daily_performance f
    JOIN analytics.dim_dates d ON f.date_key = d.date_key
    WHERE d.date = CURRENT_DATE - 2
),
day_before AS (
    SELECT SUM(ad_revenue_d0) as rev, SUM(network_cost) as cost
    FROM analytics.fct_app_daily_performance f
    JOIN analytics.dim_dates d ON f.date_key = d.date_key
    WHERE d.date = CURRENT_DATE - 3
)
SELECT
    y.rev as yesterday_rev,
    db.rev as day_before_rev,
    (y.rev - db.rev) / NULLIF(db.rev, 0) * 100 as rev_change_pct,
    y.cost as yesterday_cost,
    db.cost as day_before_cost,
    (y.cost - db.cost) / NULLIF(db.cost, 0) * 100 as cost_change_pct
FROM yesterday y, day_before db
```

**Expected Answer Format:**
```
Comparing [Date] vs [Date-1]:

Revenue: $X,XXX → $X,XXX (±X%)
Cost: $X,XXX → $X,XXX (±X%)
ROAS: XX% → XX% (±X%)

Main factors:
1. [Factor] changed by X%
2. [Factor] changed by X%

Recommendation: [Action]
```

---

#### Question 3: "What's D0 ROAS by country?"

**Expected SQL:**
```sql
SELECT
    country_code,
    SUM(network_cost) as cost,
    SUM(ad_revenue_d0) as revenue,
    SUM(ad_revenue_d0) / NULLIF(SUM(network_cost), 0) as d0_roas
FROM analytics.fct_app_daily_performance
WHERE network_cost > 0
GROUP BY country_code
ORDER BY cost DESC
LIMIT 10
```

---

#### Question 4: "Revenue breakdown by country?"

**Expected SQL:**
```sql
SELECT
    country_code,
    SUM(ad_revenue) as total_revenue,
    SUM(ad_revenue) / SUM(SUM(ad_revenue)) OVER () * 100 as pct_of_total
FROM analytics.fct_app_daily_performance
GROUP BY country_code
ORDER BY total_revenue DESC
LIMIT 10
```

---

#### Question 5: "Does data match? Adjust vs AdMob diff?"

**Expected SQL:**
```sql
SELECT
    SUM(ad_revenue) as admob_revenue,
    SUM(ad_revenue_adjust) as adjust_revenue,
    ABS(SUM(ad_revenue_adjust) - SUM(ad_revenue)) / NULLIF(SUM(ad_revenue), 0) * 100 as diff_pct
FROM analytics.fct_app_daily_performance
```

---

### 4.2 Accuracy Test Matrix - TESTED 2026-01-24

| Question | SQL Correct | Numbers Match | Format Good | Pass |
|----------|-------------|---------------|-------------|------|
| Q1: Top spending app | [x] | [x] | [x] | [x] |
| Q2: Why metrics changed | [x] | [x] | [x] | [x] |
| Q3: ROAS by country | [x] | [x] | [x] | [x] |
| Q4: Revenue breakdown | [x] | [x] | [x] | [x] |
| Q5: Data reconciliation | [x] | [x] | [x] | [x] |
| Q6: CPI analysis | [x] | [~] | [x] | [~] |
| Q7: Installs over time | [x] | [x] | [x] | [x] |
| Q8: Break-even analysis | [x] | [x] | [x] | [x] |
| Q9: App profitability | [x] | [x] | [x] | [x] |
| Q10: Country comparison | [x] | [x] | [x] | [x] |

**Result: 9/10 passed** (Q6 partial due to data gaps, not agent issue)

**Sample Actual Results:**
- Q1: "Video AI Generator - $59,718 spent, D0 ROAS 67.56% (losing money)"
- Q5: "AdMob vs Adjust diff: 1.3% (healthy)"
- Q10: "Thailand ROAS 61.7%, Vietnam ROAS 62.7% - both losing money"

### 4.3 Response Time Test - TESTED 2026-01-24

| Operation | Target | Actual | Pass |
|-----------|--------|--------|------|
| Simple query (COUNT) | < 5s | ~3s | [x] |
| Aggregation query | < 10s | ~5s | [x] |
| Multi-table JOIN | < 15s | ~6s | [x] |
| Full conversation | < 20s | ~8s | [x] |

### 4.4 Edge Case Tests - TESTED 2026-01-24

| Scenario | Expected Behavior | Pass |
|----------|-------------------|------|
| Empty result | "No data found for..." | [x] |
| SQL error | Graceful error message | [x] |
| Invalid date range | Explain valid range | [x] |
| Ambiguous question | Ask for clarification | [x] |
| Non-data question | "I can only help with data queries" | [x] |

**Additional Tests Passed:**
- Conversation memory (follow-up questions work)
- Actionable recommendations ("which app to turn off")
- Simulation ("if CPI reduces 20%, ROAS becomes 93.73%")
- Full demo scenario (overview → drill-down → detail)

---

## Part 5: Demo Script

### 5.1 Demo Flow (10 minutes)

**Opening (1 min):**
- "This is the AI Agent for Ameno Technologies mobile analytics"
- "It helps Chi Linh, our Business Controller, analyze app performance"

**Demo Question 1: Basic Query (2 min)**
```
User: "What's our total revenue and cost for the last week?"

Agent shows:
1. SQL query being executed
2. Results: Revenue $XX,XXX, Cost $XX,XXX
3. Calculated ROAS: XX%
```

**Demo Question 2: Drill-Down (2 min)**
```
User: "Which apps are losing money?"

Agent shows:
1. Query for ROAS < 100%
2. List of unprofitable apps
3. Recommendation to investigate
```

**Demo Question 3: Root Cause (2 min)**
```
User: "Why is [App Name] losing money?"

Agent shows:
1. Break-even analysis
2. CPI vs max acceptable CPI
3. Specific recommendation
```

**Demo Question 4: Comparison (2 min)**
```
User: "Compare Thailand vs Vietnam performance"

Agent shows:
1. Side-by-side metrics
2. Key differences highlighted
3. Which country to prioritize
```

**Closing (1 min):**
- Show conversation memory works
- Mention optional: Kafka streaming, RAG documents

### 5.2 Backup Questions

If primary questions fail, use these:
1. "How many apps do we have?"
2. "What's the average CPI?"
3. "Show me top 5 countries by revenue"

### 5.3 Known Limitations to Mention

- Data through Jan 22 (yesterday's data collected fresh)
- No ad source breakdown (Adjust API limitation)
- Read-only analysis (no actions)

---

## Part 6: Execution Timeline

### Day 1: Jan 23 (Today)

| Time | Task | Duration |
|------|------|----------|
| Now | Create agent/ directory structure | 15 min |
| +15m | Implement snowflake_tools.py | 45 min |
| +1h | Test tool with 5 queries | 30 min |
| +1.5h | Implement agent.py with LangGraph | 1h |
| +2.5h | Create system prompt | 30 min |
| +3h | Test agent via CLI | 30 min |
| +3.5h | Implement Streamlit UI | 1h |
| +4.5h | End-to-end testing | 30 min |
| +5h | **CHECKPOINT: Core agent working** | - |
| +5h | Optional: Kafka checkbox | 1h |
| +6h | Optional: RAG checkbox | 1h |
| EOD | Final testing, polish | 30 min |

### Day 2: Jan 24 (Demo Day)

| Time | Task |
|------|------|
| 9:00 AM | Collect Jan 23 data |
| 9:30 AM | Run dbt build --full-refresh |
| 10:00 AM | Test agent with fresh data |
| 10:30 AM | Fix any issues |
| 11:00 AM | Practice demo script |
| 12:00 PM | Final check |
| **1:00 PM** | **DEMO** |

---

## Part 7: Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OpenAI API rate limit | Use GPT-3.5-turbo, add retry logic |
| Snowflake connection fails | Test connection first, have backup screenshots |
| Agent generates wrong SQL | Add SQL validation, show query to user |
| Demo question fails | Have 3 backup questions ready |
| Streamlit crashes | Can demo via CLI as backup |

---

## Quick Start Commands

```bash
# 1. Setup
cd /Users/lehongthai/code_personal/fa-c002-lab
source .venv/bin/activate

# 2. Install new dependencies
pip install openai langchain langgraph langchain-openai streamlit

# 3. Test Snowflake tool
python -c "from agent.tools.snowflake_tools import query_snowflake; print(query_snowflake('SELECT COUNT(*) FROM analytics.fct_app_daily_performance'))"

# 4. Test agent CLI
python agent/agent.py --interactive

# 5. Run Streamlit
streamlit run agent/app.py

# 6. Demo day data refresh
python scripts/collect_adjust_capstone.py --start 2026-01-23 --end 2026-01-23
python scripts/collect_admob_capstone.py --start 2026-01-23 --end 2026-01-23
dbt build --full-refresh
```

---

## Related Documents

- `AI_AGENT_SPEC.md` - Chi Linh's requirements and questions
- `DASHBOARD_SPEC.md` - Agent capabilities by phase
- `METRICS.md` - All metric formulas
- `DATA_SCHEMA.md` - Table schemas and SQL examples
- `ARCHITECTURE.md` - System architecture

---

## Revision History

| Date | Change |
|------|--------|
| 2026-01-24 | RAG tool complete, all 3 tools working |
| 2026-01-24 | Kafka tool complete |
| 2026-01-23 | Initial creation, core agent complete |
