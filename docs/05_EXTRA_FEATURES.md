# Extra Features (TODO)

Optional features for extra points. Core is complete (~80 pts).

---

## Scoring Reference

**From course materials:**
- 5 pts: Attempted (basic, some issues)
- 10 pts: Standard (works, business value)
- 15 pts: Sophisticated (best practices, scalable)
- 20 pts: Exceptional (innovative, production-ready)

---

## Feature 1: dbt Macros (10-15 pts)

### What
Reusable SQL snippets for common calculations.

### Implementation

**File:** `my_dbt_project/macros/metrics.sql`

```sql
{% macro calculate_roas(revenue_col, cost_col) %}
    CASE
        WHEN {{ cost_col }} > 0
        THEN ({{ revenue_col }} / {{ cost_col }}) * 100
        ELSE 0
    END
{% endmacro %}

{% macro calculate_cpi(cost_col, installs_col) %}
    CASE
        WHEN {{ installs_col }} > 0
        THEN {{ cost_col }} / {{ installs_col }}
        ELSE 0
    END
{% endmacro %}

{% macro calculate_ecpm(revenue_col, impressions_col) %}
    CASE
        WHEN {{ impressions_col }} > 0
        THEN ({{ revenue_col }} / {{ impressions_col }}) * 1000
        ELSE 0
    END
{% endmacro %}
```

**Usage in model:**
```sql
SELECT
    app_store_id,
    {{ calculate_roas('ad_revenue_d0', 'network_cost') }} AS d0_roas_pct,
    {{ calculate_cpi('network_cost', 'installs') }} AS cpi,
    {{ calculate_ecpm('ad_revenue', 'ad_impressions') }} AS ecpm
FROM {{ ref('int_app_daily_metrics') }}
```

### Demo
Show macro expansion in compiled SQL.

---

## Feature 2: dbt-expectations (10-15 pts)

### What
Advanced data quality tests using Great Expectations under the hood.

### Implementation

**Add to packages.yml:**
```yaml
packages:
  - package: calogica/dbt_expectations
    version: [">=0.10.0", "<0.11.0"]
```

**Add to schema.yml:**
```yaml
models:
  - name: fct_app_daily_performance
    columns:
      - name: ad_revenue
        data_tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 1000000  # No revenue > $1M per day
          - dbt_expectations.expect_column_values_to_not_be_null

      - name: d0_roas_pct
        data_tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 500  # ROAS shouldn't exceed 500%

      - name: date
        data_tests:
          - dbt_expectations.expect_column_values_to_be_of_type:
              column_type: date
          - dbt_expectations.expect_column_distinct_count_to_be_greater_than:
              value: 7  # At least a week of data
```

### Demo
Show test results with specific expectations.

---

## Feature 3: Multi-Model LLM Router (15-20 pts)

### What
Route queries to different LLMs based on complexity.

### Implementation

**File:** `agent/router.py`

```python
def classify_query(query: str) -> str:
    """Route to appropriate model."""
    analysis_keywords = ["why", "explain", "recommend", "should"]

    if any(kw in query.lower() for kw in analysis_keywords):
        return "gpt-4o"  # Complex analysis
    return "gpt-4o-mini"  # Simple queries
```

**Modify agent.py:**
```python
def get_llm(query: str):
    model = classify_query(query)
    return ChatOpenAI(model=model, api_key=OPENAI_API_KEY)
```

### Demo
Show different models being selected for different query types.

---

## Feature 4: Agentic RAG (15-20 pts)

### What
Agent that decides when to search documents vs query data.

### Current State
Already implemented with 3 tools. Could enhance with:
- Self-reflection (verify answer before responding)
- Source citation (show which chunks were used)

### Enhancement

```python
# Add to RAG tool response
def search_with_citation(query: str) -> str:
    results = vector_store.similarity_search_with_score(query, k=3)
    formatted = []
    for doc, score in results:
        formatted.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "Unknown"),
            "confidence": round(1 - score, 2)  # Higher = better
        })
    return json.dumps(formatted, indent=2)
```

---

## Feature 5: Dashboard Integration (10-15 pts)

### What
Connect Streamlit to show charts alongside chat.

### Implementation

```python
# In agent/app.py
import plotly.express as px

# After agent response, if contains data
if "revenue" in response.lower():
    df = query_snowflake_df("SELECT date, SUM(ad_revenue) as revenue FROM fct_app_daily_performance GROUP BY date")
    fig = px.line(df, x='date', y='revenue', title='Revenue Trend')
    st.plotly_chart(fig)
```

---

## Priority Order

If time permits, implement in this order:

| Priority | Feature | Points | Time |
|----------|---------|--------|------|
| 1 | dbt Macros | 10-15 | 30 min |
| 2 | dbt-expectations | 10-15 | 45 min |
| 3 | Multi-Model Router | 15-20 | 1 hr |
| 4 | Agentic RAG | 15-20 | 1 hr |
| 5 | Dashboard | 10-15 | 1 hr |

---

## Reference

See archived doc for full details: `docs/_archive/EXTRA_FEATURES_PLAN.md`
