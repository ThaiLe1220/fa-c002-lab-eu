# Extra Features Implementation Plan

Comprehensive plan for maximizing capstone score through strategic feature implementation.

**Created:** January 24, 2026
**Target Score:** 80+ points (currently ~55 pts)

---

## Table of Contents

1. [Current State Assessment](#1-current-state-assessment)
2. [Core Requirements Gap Analysis](#2-core-requirements-gap-analysis)
3. [Extra Features Deep Dive](#3-extra-features-deep-dive)
4. [Implementation Priority Matrix](#4-implementation-priority-matrix)
5. [Technical Specifications](#5-technical-specifications)
6. [Integration Architecture](#6-integration-architecture)
7. [Demo Strategy](#7-demo-strategy)

---

## 1. Current State Assessment

### What We Have (Working)

| Component | Status | Files | Points |
|-----------|--------|-------|--------|
| **dbt Pipeline** | Done | `my_dbt_project/models/` | 15 pts |
| **Snowflake Tool** | Done | `agent/tools/snowflake_tools.py` | 10 pts |
| **Agent Core** | Done | `agent/agent.py` | - |
| **System Prompt** | Done | `agent/prompts.py` | - |
| **Conversation Memory** | Done | LangGraph MemorySaver | - |
| **Streamlit UI** | Done | `agent/app.py` | - |
| **GitHub Actions CI** | Done | `.github/workflows/dbt_ci.yml` | 5 pts |
| **Documentation** | Partial | `docs/*.md` | 3 pts |

**Current Score Estimate:** ~55 pts (passes, but not high score)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CURRENT AGENT ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────────┘

User Query
    │
    ▼
┌─────────────────┐     ┌─────────────────┐
│   agent.py      │────▶│   prompts.py    │
│   (LangGraph)   │     │   (System Ctx)  │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  gpt-4o-mini    │────▶│ query_snowflake │
│  (Single Model) │     │    (Tool)       │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Snowflake     │
                        │   ANALYTICS     │
                        └─────────────────┘
```

### Test Results (9/10 Chi Linh Questions)

| Question | Status | Notes |
|----------|--------|-------|
| Q1: Top spending app | PASS | Video AI Generator, $59K |
| Q2: Why metrics changed | PASS | Correct date ranges |
| Q3: D0 ROAS by country | PASS | Full breakdown |
| Q4: Revenue breakdown | PASS | AdMob vs Adjust |
| Q5: Data reconciliation | PASS | 1.3% diff |
| Q6: CPI analysis | PARTIAL | Data gaps in some countries |
| Q7: Installs over time | PASS | By country detail |
| Q8: Break-even analysis | PASS | D7 ROAS projection |
| Q9: Profitable apps | PASS | ROAS > 100% filter |
| Q10: Country comparison | PASS | TH vs VN |

---

## 2. Core Requirements Gap Analysis

### Grading Criteria (from course materials)

**Core Functionality (60 pts):**

| Section | Requirement | Our Status | Gap |
|---------|-------------|------------|-----|
| **Data Ingestion (15)** | | | |
| | 1 batch source | Done | 0 |
| | 1 streaming < 5min (Kafka) | **MISSING** | -5 |
| | Airflow 3+ tasks | **MISSING** | -5 |
| | `#live-demo` new data | Can do | 0 |
| **Data Modeling (15)** | | | |
| | Dimensional model | Done | 0 |
| | dbt incremental | Done | 0 |
| | dbt test | Done | 0 |
| | `#live-demo` dbt via Airflow | **MISSING** | -5 |
| **DevOps CI (5)** | 2+ checks | Done | 0 |
| **Documentation (5)** | README + diagram | Done | 0 |
| **AI Agent RAG (10)** | | | |
| | Chatbot + memory | Done | 0 |
| | RAG for PDF | **MISSING** | -5 |
| | `#live-demo` doc query | **MISSING** | 0 |
| **AI Agent Data (10)** | | | |
| | Batch query | Done | 0 |
| | Real-time query | **MISSING** | -5 |
| | Combine PDF + warehouse | **MISSING** | 0 |

**Core Gap: ~25 pts** (Kafka, Airflow, RAG are blocking full core points)

### Must-Do Checkboxes

These are **required** for full core points:

1. **Kafka** - Streaming pipeline (5 pts)
2. **Airflow** - Orchestrator with 3 tasks (5 pts)
3. **RAG** - PDF document querying (5 pts)
4. **Kafka Tool** - Agent queries streaming data (5 pts)

---

## 3. Extra Features Deep Dive

**Scoring Scale (per feature, max 20 pts):**
- 🌱 5 pts: Attempted (basic, some issues)
- ⭐ 10 pts: Standard (works, business value)
- 🌟 15 pts: Sophisticated (best practices, scalable)
- 🏆 20 pts: Exceptional (innovative, production-ready)

### Feature 1: Multi-Model LLM Orchestration

**Potential: 🌟-🏆 (15-20 pts)**

#### What It Is

Route different queries to different models based on complexity, cost, and capability.

```
User Query
    │
    ▼
┌─────────────────┐
│  Query Router   │  ← Classifies query type
│  (Lightweight)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│GPT-4o │ │Claude │  ← Different models for different tasks
│ mini  │ │ Opus  │
└───────┘ └───────┘
   SQL      Analysis
```

#### Industry Evidence

> "Most enterprises adopt a 'good-enough by default, best-in-class on demand' strategy for their LLM consumption, dynamically routing requests to different models."
> — [LLM Orchestration 2025](https://orq.ai/blog/llm-orchestration)

> "Hybrid routing can reduce costs by 10-15× compared to all-API baselines."
> — [ZenML Blog](https://www.zenml.io/blog/best-llm-orchestration-frameworks)

#### Implementation Design

```python
# agent/router.py
from enum import Enum

class QueryType(Enum):
    SQL_GENERATION = "sql"      # GPT-4o-mini (fast, cheap)
    BUSINESS_ANALYSIS = "analysis"  # Claude/GPT-4 (deep reasoning)
    SIMPLE_LOOKUP = "lookup"    # GPT-4o-mini
    COMPLEX_COMPARISON = "compare"  # Claude/GPT-4

def classify_query(query: str) -> QueryType:
    """
    Classify query to determine optimal model.
    Uses lightweight LLM or keyword matching.
    """
    # Keywords for routing
    sql_keywords = ["total", "sum", "count", "list", "show", "what is"]
    analysis_keywords = ["why", "explain", "recommend", "should", "analyze"]

    query_lower = query.lower()

    if any(kw in query_lower for kw in analysis_keywords):
        return QueryType.BUSINESS_ANALYSIS
    return QueryType.SQL_GENERATION

def get_model_for_query(query_type: QueryType) -> str:
    """Return appropriate model based on query type."""
    model_map = {
        QueryType.SQL_GENERATION: "gpt-4o-mini",  # $0.15/1M tokens
        QueryType.BUSINESS_ANALYSIS: "claude-opus-4-5-20251101",  # Deep analysis
        QueryType.SIMPLE_LOOKUP: "gpt-4o-mini",
        QueryType.COMPLEX_COMPARISON: "gpt-4o",
    }
    return model_map[query_type]
```

#### Integration with Existing Code

```python
# Modified agent/agent.py
from agent.router import classify_query, get_model_for_query, QueryType

def call_model(state: AgentState):
    """Call the appropriate LLM based on query type."""
    messages = state["messages"]
    user_query = messages[-1].content if messages else ""

    # Route to appropriate model
    query_type = classify_query(user_query)
    model_name = get_model_for_query(query_type)

    # Use different LLM based on routing
    if query_type == QueryType.BUSINESS_ANALYSIS:
        llm = ChatAnthropic(model=model_name)
    else:
        llm = ChatOpenAI(model=model_name)

    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}
```

#### Why This Scores High

| Criteria | Score | Justification |
|----------|-------|---------------|
| Creativity | High | Novel approach not in course |
| Complexity | High | Multi-model orchestration |
| Impact | High | Cost savings, better answers |
| Production-ready | Yes | Real pattern used at scale |

---

### Feature 2: Hybrid Search RAG

**Potential: 🌟 (15 pts)**

#### What It Is

Combine keyword search (BM25) + semantic search (vector embeddings) for better document retrieval.

```
Query: "What is our D0 ROAS target?"
                │
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
┌─────────┐           ┌─────────┐
│  BM25   │           │  FAISS  │
│(Keyword)│           │(Semantic)│
└────┬────┘           └────┬────┘
     │                     │
     │   ["D0", "ROAS"]    │   [meaning of profitability]
     │                     │
     └──────────┬──────────┘
                │
                ▼
        ┌─────────────┐
        │     RRF     │  ← Reciprocal Rank Fusion
        │   Merger    │
        └─────────────┘
                │
                ▼
        Top K Results
```

#### Industry Evidence

> "I Built a Hybrid Search System That Beats Standard RAG by 35%... it's the difference between users finding what they need and giving up in frustration."
> — [Medium Article](https://medium.com/@hitendra.patel2986/i-built-a-hybrid-search-system-that-beats-standard-rag-by-35-1968791ae539)

> "For enterprise implementation: Implement Hybrid Search. This is the most cost-effective optimization, immediately solving the issue of failed proper noun retrieval."
> — [SynthiMind 2025](https://synthimind.net/blog/rag-optimization-strategies-2025/)

#### Implementation Design

```python
# agent/tools/rag_tools.py
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool
from typing import Annotated

# Initialize retrievers (done once at startup)
def create_hybrid_retriever(documents: list):
    """Create hybrid retriever combining BM25 + FAISS."""

    # Keyword retriever (BM25)
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = 5

    # Semantic retriever (FAISS)
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)
    faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # Ensemble with RRF
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever],
        weights=[0.4, 0.6]  # 40% keyword, 60% semantic
    )

    return ensemble_retriever

@tool
def query_documents(
    question: Annotated[str, "Question to answer from documents"]
) -> str:
    """
    Search business documents using hybrid search (keyword + semantic).

    Use this for questions about:
    - Company policies and guidelines
    - Metric definitions and thresholds
    - Business rules and processes

    Args:
        question: The question to answer

    Returns:
        Relevant document excerpts
    """
    global hybrid_retriever

    docs = hybrid_retriever.get_relevant_documents(question)

    if not docs:
        return "No relevant documents found."

    result = "Relevant excerpts:\n\n"
    for i, doc in enumerate(docs[:3], 1):
        result += f"**Source {i}:**\n{doc.page_content}\n\n"

    return result
```

#### Documents to Include

For demo, create/use these PDFs:

1. **Business_Rules.pdf** - Metric thresholds, ROAS targets
2. **UA_Guidelines.pdf** - When to scale/cut campaigns
3. **Data_Dictionary.pdf** - Column definitions, formulas

#### Why This Scores High

| Criteria | Score | Justification |
|----------|-------|---------------|
| Creativity | Medium | Known technique, well-implemented |
| Complexity | High | Dual retrieval + fusion |
| Impact | High | 35% better recall (provable) |
| Production-ready | Yes | Industry standard |

---

### Feature 3: Advanced Prompt Engineering (Business Context)

**Potential: ⭐-🌟 (10-15 pts)**

#### What It Is

Encode deep domain expertise into prompts — thresholds, formulas, drill-down hierarchy, actionable recommendations.

#### What We Already Have

```python
# Current prompts.py (already implemented)
SYSTEM_PROMPT = """
## Chi Linh's Key Thresholds
- D0 ROAS > 100%: Profitable, can scale
- D0 ROAS 80-100%: Marginal, check D7 ROAS for recovery
- D0 ROAS < 80%: Losing money, needs immediate attention

## Drill-Down Hierarchy
1. Total (all apps, all countries)
2. By App - "Which app is causing this?"
3. By Country - "Which country within that app?"
"""
```

#### Enhancement Opportunities

```python
# Enhanced prompts.py
BUSINESS_CONTEXT = """
## Decision Framework

### When to SCALE (increase spend):
- D0 ROAS > 120% AND installs > 100/day
- CPI trending down for 3+ days
- Country has consistent performance

### When to CUT (reduce spend):
- D0 ROAS < 70% for 3+ days
- CPI increased > 50% week-over-week
- No recovery signal in D7 ROAS

### When to INVESTIGATE:
- Revenue dropped > 20% day-over-day
- eCPM dropped > 15% (check ad network)
- Installs dropped but cost stayed same

## Simulation Capabilities
When asked "what if" questions:
- Calculate projected metrics with changed inputs
- Show break-even scenarios
- Compare against historical benchmarks

## Response Templates

### For "Why" Questions:
1. State the observation (what changed)
2. Show the data (metrics)
3. Identify the driver (which app/country)
4. Provide hypothesis
5. Suggest next steps

### For "What to do" Questions:
1. Assess current state vs thresholds
2. Identify options (scale/maintain/cut)
3. Recommend action with reasoning
4. Note risks and monitoring needs
"""
```

#### Industry Evidence

> "A semantic layer is 'essentially an instruction manual that explains to the LLM all the details about what is in the data and how to use it.'"
> — [HelioCampus](https://www.heliocampus.com/resources/blogs/ai-data-analytics)

> "Context-aware approaches can achieve 88% accuracy vs 23% without context."
> — [AWS Blog](https://aws.amazon.com/blogs/machine-learning/generating-value-from-enterprise-data-best-practices-for-text2sql-and-generative-ai/)

---

### Feature 4: Custom dbt Macros

**Potential: ⭐-🌟 (10-15 pts)**

#### What It Is

Reusable Jinja templates for DRY transformations across models.

#### Current State

```sql
-- my_dbt_project/macros/calculate_ctr.sql (existing)
{% macro calculate_ctr(clicks, impressions) %}
    CASE
        WHEN {{ impressions }} > 0
        THEN ({{ clicks }}::DECIMAL / {{ impressions }}) * 100
        ELSE 0
    END
{% endmacro %}
```

#### New Macros to Add

```sql
-- macros/calculate_roas.sql
{% macro calculate_roas(revenue_col, cost_col, multiplier=100) %}
{#
    Calculate ROAS (Return on Ad Spend).

    Args:
        revenue_col: Column with revenue
        cost_col: Column with cost/spend
        multiplier: 100 for percentage, 1 for decimal

    Example:
        {{ calculate_roas('ad_revenue_d0', 'network_cost') }}
#}
    CASE
        WHEN {{ cost_col }} > 0
        THEN ({{ revenue_col }}::DECIMAL / {{ cost_col }}) * {{ multiplier }}
        ELSE NULL
    END
{% endmacro %}


-- macros/calculate_cpi.sql
{% macro calculate_cpi(cost_col, installs_col) %}
{#
    Calculate CPI (Cost Per Install).

    Args:
        cost_col: Column with UA spend
        installs_col: Column with install count

    Example:
        {{ calculate_cpi('network_cost', 'installs') }}
#}
    CASE
        WHEN {{ installs_col }} > 0
        THEN {{ cost_col }}::DECIMAL / {{ installs_col }}
        ELSE NULL
    END
{% endmacro %}


-- macros/calculate_ecpm.sql
{% macro calculate_ecpm(revenue_col, impressions_col) %}
{#
    Calculate eCPM (Revenue per 1000 impressions).

    Args:
        revenue_col: Column with ad revenue
        impressions_col: Column with impression count

    Example:
        {{ calculate_ecpm('ad_revenue', 'ad_impressions') }}
#}
    CASE
        WHEN {{ impressions_col }} > 0
        THEN ({{ revenue_col }}::DECIMAL * 1000) / {{ impressions_col }}
        ELSE NULL
    END
{% endmacro %}


-- macros/safe_divide.sql
{% macro safe_divide(numerator, denominator, default=0) %}
{#
    Null-safe division.

    Args:
        numerator: Numerator column/value
        denominator: Denominator column/value
        default: Value to return if division not possible

    Example:
        {{ safe_divide('revenue', 'cost', default='NULL') }}
#}
    CASE
        WHEN {{ denominator }} IS NOT NULL AND {{ denominator }} != 0
        THEN {{ numerator }}::DECIMAL / {{ denominator }}
        ELSE {{ default }}
    END
{% endmacro %}
```

#### Usage in Models

```sql
-- models/03_mart/fct_app_daily_performance.sql (updated)
SELECT
    ...
    -- Use macros instead of inline CASE statements
    {{ calculate_roas('m.ad_revenue_d0', 'm.network_cost') }} AS d0_roas_pct,
    {{ calculate_roas('m.ad_revenue_d7', 'm.network_cost') }} AS d7_roas_pct,
    {{ calculate_cpi('m.network_cost', 'm.installs') }} AS cpi,
    {{ calculate_ecpm('m.ad_revenue', 'm.ad_impressions') }} AS ecpm,
    {{ calculate_ctr('m.ad_clicks', 'm.ad_impressions') }} AS ad_ctr,
FROM metrics m
```

#### Industry Evidence

> "Key benefits include standardization (macros ensure that the same logic is applied consistently everywhere) and reusability (instead of writing the same 10 lines of SQL in 20 different models, you write it once in a macro)."
> — [Dagster Guide](https://dagster.io/guides/ultimate-guide-to-dbt-macros-in-2025-syntax-examples-pro-tips)

---

### Feature 5: Data Quality Framework

**Potential: ⭐-🌟 (10-15 pts)**

#### What It Is

Extended dbt tests using dbt-expectations for business rule validation.

#### Implementation

```yaml
# packages.yml (add)
packages:
  - package: metaplane/dbt_expectations
    version: 0.10.9
```

```yaml
# models/03_mart/schema.yml (enhanced)
version: 2

models:
  - name: fct_app_daily_performance
    description: "Fact table with data quality gates"

    # Table-level tests
    tests:
      # Ensure we have recent data
      - dbt_expectations.expect_grouped_row_values_to_have_recent_data:
          group_by: [app_key]
          timestamp_column: dbt_updated_at
          datepart: day
          interval: 2
          severity: warn

      # Row count sanity check
      - dbt_expectations.expect_table_row_count_to_be_between:
          min_value: 100000
          max_value: 500000
          severity: warn

    columns:
      - name: ad_revenue
        description: "AdMob revenue (source of truth)"
        data_tests:
          - not_null
          # Revenue should be non-negative
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 100000
              severity: error

      - name: network_cost
        description: "UA spend"
        data_tests:
          # Cost should be non-negative
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 50000
              severity: error

      - name: installs
        description: "New installs"
        data_tests:
          - not_null
          # Installs should be reasonable
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 100000
              severity: warn

      - name: country_code
        description: "ISO country code"
        data_tests:
          - not_null
          # Should be valid 2-letter codes
          - dbt_expectations.expect_column_value_lengths_to_equal:
              value: 2
```

#### Industry Evidence

> "dbt-expectations lets you gate your pipelines with Great Expectations-style assertions that extend beyond the capabilities of dbt's built-in tests."
> — [Datafold](https://www.datafold.com/blog/dbt-expectations)

---

### Feature 6: Advanced Error Handling & Observability

**Potential: ⭐-🌟 (10-15 pts)**

#### What It Is

Retry logic, fallback strategies, structured logging for AI agents.

#### Implementation

```python
# agent/resilience.py
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from functools import wraps
import time

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

class AgentObservability:
    """Track agent performance and errors."""

    def __init__(self):
        self.queries = []
        self.errors = []
        self.latencies = []

    def log_query(self, query: str, response: str, latency: float, model: str):
        """Log a successful query."""
        entry = {
            "timestamp": time.time(),
            "query": query[:100],  # Truncate for logging
            "response_length": len(response),
            "latency_ms": latency * 1000,
            "model": model
        }
        self.queries.append(entry)
        logger.info(f"Query completed | model={model} | latency={latency*1000:.0f}ms")

    def log_error(self, query: str, error: Exception, retry_count: int):
        """Log an error."""
        entry = {
            "timestamp": time.time(),
            "query": query[:100],
            "error": str(error),
            "retry_count": retry_count
        }
        self.errors.append(entry)
        logger.error(f"Query error | retry={retry_count} | error={str(error)[:50]}")

    def get_stats(self) -> dict:
        """Get performance statistics."""
        if not self.latencies:
            return {"total_queries": 0}

        return {
            "total_queries": len(self.queries),
            "total_errors": len(self.errors),
            "avg_latency_ms": sum(self.latencies) / len(self.latencies),
            "error_rate": len(self.errors) / (len(self.queries) + len(self.errors))
        }

# Global observability instance
obs = AgentObservability()

# Retry decorator for Snowflake queries
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
def query_with_retry(client, sql: str) -> any:
    """Execute query with retry logic."""
    return client.execute_query(sql)

# Fallback decorator
def with_fallback(fallback_fn):
    """Decorator to provide fallback behavior."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Primary failed, using fallback: {e}")
                return fallback_fn(*args, **kwargs)
        return wrapper
    return decorator
```

#### Integration

```python
# Updated agent/tools/snowflake_tools.py
from agent.resilience import query_with_retry, obs
import time

@tool
def query_snowflake(sql_query: Annotated[str, "Valid Snowflake SQL query"]) -> str:
    """Execute SQL with retry and observability."""
    start_time = time.time()

    try:
        client = get_snowflake_client(schema="ANALYTICS")

        try:
            # Use retry-enabled query
            df = query_with_retry(client, sql_query)

            latency = time.time() - start_time
            result = format_results(df)

            # Log success
            obs.log_query(sql_query, result, latency, "snowflake")

            return result

        finally:
            client.close()

    except Exception as e:
        obs.log_error(sql_query, e, retry_count=3)
        return f"Query failed after retries: {str(e)}"
```

#### Industry Evidence

> "Error recovery in AI agent systems is about architecting for resilience in a probabilistic, dynamic environment. Building recovery paths, validation checkpoints, and escalation protocols is what separates prototypes from production-grade AI systems."
> — [GoCodeo](https://www.gocodeo.com/post/error-recovery-and-fallback-strategies-in-ai-agent-development)

---

## 4. Implementation Priority Matrix

### Effort vs. Impact Analysis

```
                    HIGH IMPACT
                        │
     ┌──────────────────┼──────────────────┐
     │                  │                  │
     │  Multi-Model     │   Hybrid RAG     │
     │  Orchestration   │                  │
     │  (15-20 pts)     │   (15 pts)       │
     │                  │                  │
LOW  ├──────────────────┼──────────────────┤ HIGH
EFFORT│                  │                  │ EFFORT
     │  dbt Macros      │   Error          │
     │  (10-15 pts)     │   Handling       │
     │                  │   (10-15 pts)    │
     │  Data Quality    │                  │
     │  (10-15 pts)     │   Prompt Eng     │
     │                  │   (10-15 pts)    │
     └──────────────────┼──────────────────┘
                        │
                    LOW IMPACT
```

### Recommended Implementation Order

| Priority | Feature | Effort | Points | Cumulative |
|----------|---------|--------|--------|------------|
| 1 | **dbt Macros** | 30 min | 10-15 | 10-15 |
| 2 | **Data Quality (dbt-expectations)** | 45 min | 10-15 | 20-30 |
| 3 | **Enhanced Prompts** | 30 min | 5-10 | 25-40 |
| 4 | **Multi-Model Routing** | 2 hrs | 15-20 | 40-60* |
| 5 | **Hybrid RAG** | 2 hrs | 15 | 55-75* |
| 6 | **Error Handling** | 1 hr | 10 | 65-85* |

*Max 40 pts for extra features, but strong implementations can push boundaries.

### My Recommendation

**Go for Option A (Maximum Innovation):**

1. **Multi-Model Orchestration** (20 pts target)
   - Shows innovation beyond course material
   - Demonstrates cost-awareness
   - Production-ready pattern

2. **Enhanced Prompt Engineering** (15 pts target)
   - Already partially done
   - Document thoroughly
   - Show Chi Linh workflow

**Plus quick wins:**
- dbt Macros (10 pts)
- Data Quality tests (10 pts)

**Total Extra Feature Target: 35-40 pts**

---

## 5. Technical Specifications

### Dependencies to Add

```toml
# pyproject.toml additions
dependencies = [
    # ... existing ...
    "langchain-anthropic>=0.3.0",  # For Claude
    "faiss-cpu>=1.7.4",            # For vector search
    "rank-bm25>=0.2.2",            # For keyword search
    "tenacity>=8.2.0",             # For retry logic
    "pypdf>=3.0.0",                # For PDF loading
]
```

```yaml
# my_dbt_project/packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1
  - package: metaplane/dbt_expectations
    version: 0.10.9
```

### File Structure (New Files)

```
agent/
├── __init__.py
├── config.py
├── prompts.py          # Enhanced with business context
├── agent.py            # Modified for multi-model
├── router.py           # NEW: Query classification
├── resilience.py       # NEW: Retry + observability
├── app.py
└── tools/
    ├── __init__.py
    ├── snowflake_tools.py
    ├── rag_tools.py    # NEW: Hybrid search
    └── kafka_tools.py  # NEW: Streaming queries

my_dbt_project/
├── macros/
│   ├── calculate_ctr.sql
│   ├── calculate_roas.sql    # NEW
│   ├── calculate_cpi.sql     # NEW
│   ├── calculate_ecpm.sql    # NEW
│   └── safe_divide.sql       # NEW
└── models/
    └── 03_mart/
        └── schema.yml        # Enhanced with dbt-expectations

docs/
├── Business_Rules.pdf        # NEW: For RAG demo
└── UA_Guidelines.pdf         # NEW: For RAG demo
```

---

## 6. Integration Architecture

### Enhanced Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ENHANCED AGENT ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────────┘

User Query
    │
    ▼
┌─────────────────┐
│  Query Router   │  ← Classifies: SQL vs Analysis vs Docs
│  (router.py)    │
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    │         │            │
    ▼         ▼            ▼
┌───────┐ ┌───────┐  ┌──────────┐
│GPT-4o │ │Claude │  │  Hybrid  │
│ mini  │ │ Opus  │  │   RAG    │
└───┬───┘ └───┬───┘  └────┬─────┘
    │         │           │
    ▼         ▼           ▼
┌───────┐ ┌───────┐  ┌──────────┐
│  SQL  │ │Analysis│ │BM25+FAISS│
│ Tool  │ │ Tool  │  │ Retriever│
└───┬───┘ └───────┘  └────┬─────┘
    │                     │
    ▼                     ▼
┌─────────┐          ┌─────────┐
│Snowflake│          │  PDFs   │
│ANALYTICS│          │  Docs   │
└─────────┘          └─────────┘
         │                │
         └───────┬────────┘
                 │
                 ▼
         ┌─────────────┐
         │ Observability│
         │ (resilience) │
         └─────────────┘
                 │
                 ▼
            Response
```

### Data Flow

```
1. User asks: "Why did ROAS drop for Video AI Generator last week?"

2. Router classifies: BUSINESS_ANALYSIS (needs reasoning)

3. Agent uses Claude Opus for deep analysis

4. Claude calls tools:
   - query_snowflake() → Get ROAS data by day
   - query_snowflake() → Get breakdown by country
   - query_documents() → Check ROAS thresholds from docs

5. Claude synthesizes:
   - "ROAS dropped from 85% to 62% between Jan 15-22"
   - "Main driver: Thailand CPI increased 45%"
   - "Per guidelines, this triggers INVESTIGATE status"
   - "Recommendation: Check creative fatigue, consider refresh"

6. Observability logs: query, model used, latency, success
```

---

## 7. Demo Strategy

### Demo Script (10 minutes for Extra Features)

**Minute 0-2: Multi-Model Routing**
```
Demo: "Show me total revenue for January"
→ Routes to GPT-4o-mini (fast SQL)
→ Shows routing decision in logs

Demo: "Why is Video AI Generator losing money?"
→ Routes to Claude (analysis)
→ Shows different model being used
```

**Minute 2-4: Hybrid RAG**
```
Demo: "What are Chi Linh's ROAS thresholds?"
→ Searches Business_Rules.pdf
→ Shows BM25 + FAISS working together
→ Returns: "D0 ROAS > 100% = profitable..."
```

**Minute 4-6: Business Context**
```
Demo: "Should we scale Video AI Generator in Thailand?"
→ Agent queries data
→ Applies thresholds from prompt
→ Returns recommendation with reasoning
```

**Minute 6-8: Data Quality**
```
Demo: Run `dbt test` showing dbt-expectations
→ Show passing quality gates
→ Explain what each test validates
```

**Minute 8-10: Q&A / Deep Dive**
- Show observability stats
- Explain cost savings from routing
- Show dbt macros in action

### Talking Points for Graders

1. **Innovation**: "Multi-model routing isn't in the course - I implemented it based on industry best practices for cost optimization."

2. **Production-Ready**: "The retry logic and observability are patterns used at scale companies."

3. **Business Value**: "Hybrid search solves real problem - exact metric names like 'D0 ROAS' were being missed by pure semantic search."

4. **Deep Understanding**: "I encoded Chi Linh's actual decision framework into the prompts, so the agent gives actionable recommendations, not just data."

---

## Sources

### Multi-Model Orchestration
- [LLM Orchestration 2025 - orq.ai](https://orq.ai/blog/llm-orchestration)
- [ZenML Best Frameworks](https://www.zenml.io/blog/best-llm-orchestration-frameworks)
- [GitHub: langgraph-model-router](https://github.com/johnsosoka/langgraph-model-router)
- [LangChain Multi-Source Router](https://docs.langchain.com/oss/python/langchain/multi-agent/router-knowledge-base)

### Hybrid Search RAG
- [35% Improvement with Hybrid Search](https://medium.com/@hitendra.patel2986/i-built-a-hybrid-search-system-that-beats-standard-rag-by-35-1968791ae539)
- [LangChain BM25 Docs](https://docs.langchain.com/oss/python/integrations/retrievers/bm25)
- [Hybrid Retrieval Implementation](https://www.chitika.com/hybrid-retrieval-rag/)

### Prompt Engineering
- [AWS Text-to-SQL Best Practices](https://aws.amazon.com/blogs/machine-learning/generating-value-from-enterprise-data-best-practices-for-text2sql-and-generative-ai/)
- [HelioCampus Semantic Layers](https://www.heliocampus.com/resources/blogs/ai-data-analytics)

### dbt Best Practices
- [Ultimate Guide to dbt Macros 2025](https://dagster.io/guides/ultimate-guide-to-dbt-macros-in-2025-syntax-examples-pro-tips)
- [dbt-expectations Package](https://hub.getdbt.com/metaplane/dbt_expectations/latest/)
- [Datafold dbt-expectations Guide](https://www.datafold.com/blog/dbt-expectations)

### Error Handling & Observability
- [AI Agent Error Recovery](https://www.gocodeo.com/post/error-recovery-and-fallback-strategies-in-ai-agent-development)
- [AI Observability Guide 2025](https://www.vellum.ai/blog/understanding-your-agents-behavior-in-production)
- [Mastering Retry Logic 2025](https://sparkco.ai/blog/mastering-retry-logic-agents-a-deep-dive-into-2025-best-practices)

---

## Next Steps

1. **Review this plan** - Confirm priorities
2. **Implement core checkboxes first** - Kafka, Airflow, basic RAG (required)
3. **Implement extra features** - Start with dbt macros (quick win)
4. **Test end-to-end** - Run demo script
5. **Document everything** - Update README

**Estimated Total Time:** 4-6 hours for everything
**Target Score:** 85-95 points
