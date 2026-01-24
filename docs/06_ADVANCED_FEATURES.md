# Advanced Features & Implementation Highlights

**Purpose:** Document features that exceed basic capstone requirements.

---

## 1. Multi-Source Integration Pattern (Data Pipeline Enhancement)

**What:** Two batch data sources (AdMob + Adjust) joined with FULL OUTER JOIN.

**Evidence:** `my_dbt_project/models/02_intermediate/int_app_daily_metrics.sql`

```sql
FROM admob adm
FULL OUTER JOIN adjust adj
    ON adm.app_store_id = adj.app_store_id
    AND adm.date = adj.date
    AND UPPER(adm.country_code) = UPPER(adj.country_code)
    AND adm.platform = adj.platform
```

**Why this is advanced:**
- Basic requirement: "at least 1 batch data source"
- Our implementation: TWO batch sources with different schemas
- FULL OUTER JOIN captures apps that exist in only one source
- COALESCE pattern handles NULL values from either side
- Data reconciliation: AdMob = source of truth, Adjust = for comparison

**Business reasoning:**
- AdMob reports actual revenue (what Google pays us)
- Adjust reports attributed revenue (for LTV analysis)
- They don't always match - we need both for complete picture

---

## 2. Real Production API Integration (Data Pipeline Enhancement)

**What:** Direct API integration with Google AdMob and Adjust APIs.

**Evidence:**
- `scripts/collect_admob_capstone.py` (13,009 bytes)
- `scripts/collect_adjust_capstone.py` (8,733 bytes)

**Why this is advanced:**
- Basic requirement: "batch data source (e.g., CSV files, database dumps)"
- Our implementation: Real REST APIs with OAuth2 (AdMob) and API keys (Adjust)
- Handles pagination, rate limiting, error handling
- Date-based incremental collection (not full dumps)

**Technical details:**
- AdMob: Google API Client with service account authentication
- Adjust: REST API with bearer token authentication
- Both: Parameterized date ranges, retry logic, data validation

---

## 3. Custom dbt Macro (Data Architecture)

**What:** Reusable macro for CTR calculation with division-by-zero handling.

**Evidence:** `my_dbt_project/macros/calculate_ctr.sql`

```sql
{% macro calculate_ctr(clicks, impressions) %}
    CASE
        WHEN {{ impressions }} > 0
        THEN ({{ clicks }}::DECIMAL / {{ impressions }}) * 100
        ELSE 0
    END
{% endmacro %}
```

**Why this is advanced:**
- Basic requirement: None (macros not required)
- Our implementation: Reusable macro with safe division
- Used in `fct_app_daily_performance.sql` for CTR calculation
- Pattern can be extended for other metrics (ROAS, CPI, eCPM)

**Usage:**
```sql
{{ calculate_ctr('m.ad_clicks', 'm.ad_impressions') }} AS ad_ctr
```

---

## 4. Extended Airflow Pipeline (Data Pipeline Enhancement)

**What:** 5-task pipeline including data collection, not just dbt.

**Evidence:** `airflow/dags/dbt_pipeline.py`

```
collect_admob ─┐
               ├─→ dbt_debug → dbt_run → dbt_test
collect_adjust ┘
```

**Why this is advanced:**
- Basic requirement: "at least 3 tasks"
- Our implementation: 5 tasks with parallel data collection
- Full end-to-end orchestration: API → RAW → ANALYTICS
- Data collection runs in parallel, then dbt runs sequentially

**Task breakdown:**
| Task | Duration | Function |
|------|----------|----------|
| collect_admob | ~15s | AdMob API → Snowflake RAW |
| collect_adjust | ~15s | Adjust API → Snowflake RAW |
| dbt_debug | ~4s | Verify Snowflake connection |
| dbt_run | ~21s | Run all dbt models |
| dbt_test | ~2s | Run 26 data quality tests |

---

## 5. Custom Prompt Engineering (AI/ML Enhancement)

**What:** 70-line system prompt with role, context, tools guidance, and business logic.

**Evidence:** `agent/prompts.py`

**Components:**

### A. Role Definition
```python
"You are a data analyst assistant for Ameno Technologies, a mobile app company.
You help Chi Linh (Business Performance Controller) analyze app performance data."
```

### B. Three-Tool Guidance
```python
"1. query_snowflake - For batch analytics data (historical)
2. query_realtime_alerts - For streaming alerts (real-time)
3. search_business_documents - For company policies and rules (RAG)"
```

### C. Business Thresholds Embedded
```python
"- D0 ROAS > 100%: Profitable, can scale
- D0 ROAS 80-100%: Marginal, check D7 ROAS for recovery
- D0 ROAS < 80%: Losing money, needs immediate attention"
```

### D. Drill-Down Hierarchy
```python
"1. Total (all apps, all countries) - 'What's the overall picture?'
2. By App - 'Which app is causing this?'
3. By Country - 'Which country within that app?'"
```

### E. Response Format Guidelines
```python
"1. Direct answer to the question
2. Key numbers/metrics
3. Insight or recommendation (if applicable)"
```

**Why this is advanced:**
- Basic requirement: "functional chatbot"
- Our implementation: Domain-specific prompt with business context
- Guides LLM to use correct tools for different question types
- Embeds company decision frameworks directly in prompt

---

## 6. Comprehensive Schema Context for LLM (AI/ML Enhancement)

**What:** 100+ lines of schema documentation embedded in the Snowflake tool.

**Evidence:** `agent/tools/snowflake_tools.py` - `SCHEMA_CONTEXT` variable

**Components:**
- Table descriptions with grain (one row per app × date × country × platform)
- Column definitions with business meaning
- Metric formulas (ROAS, CPI, eCPM, IMPDAU)
- ROAS query guidance with HAVING clause and NULLS LAST
- Example queries for common patterns

**Why this is advanced:**
- Basic requirement: "chatbot can answer questions about warehouse data"
- Our implementation: LLM has full schema context to write correct SQL
- Includes business logic (e.g., "ad_revenue_d0 = ~70-80% of LTV")
- Handles edge cases (e.g., apps without cost data returning NULL ROAS)

---

## 7. Production Business Rules RAG (AI/ML Enhancement)

**What:** 175-line business rules document from actual company operations.

**Evidence:** `docs/business_rules/ameno_business_rules.md`

**Content:**
| Section | Lines | Purpose |
|---------|-------|---------|
| ROAS Decision Framework | 30 | When to scale/pause campaigns |
| CPI Guidelines | 25 | Cost benchmarks by platform/region |
| eCPM Guidelines | 25 | Revenue benchmarks by ad format |
| IMPDAU Guidelines | 15 | Monetization intensity targets |
| Alert Severity Definitions | 20 | Critical/Warning/Info thresholds |
| Monthly Reporting Requirements | 20 | Chi Linh's actual reports |
| Seasonal Patterns | 20 | Q4 high, Q1 low patterns |

**Why this is advanced:**
- Basic requirement: "basic RAG capabilities for PDF/document processing"
- Our implementation: Real company business rules, not toy examples
- Covers complete decision framework for mobile app monetization
- Used by actual Business Performance Controller (Chi Linh)

---

## 8. Cohort Analytics (Data Architecture)

**What:** D0, D1, D3, D7 revenue and impression tracking for LTV analysis.

**Evidence:** `my_dbt_project/models/02_intermediate/int_app_daily_metrics.sql`

```sql
-- Cohort metrics (D0, D1, D3, D7 for LTV curve)
COALESCE(adj.ad_revenue_d0, 0) AS ad_revenue_d0,
COALESCE(adj.ad_impressions_d0, 0) AS ad_impressions_d0,
COALESCE(adj.ad_revenue_d1, 0) AS ad_revenue_d1,
...
COALESCE(adj.ad_revenue_d7, 0) AS ad_revenue_d7,
```

**Why this is advanced:**
- Basic requirement: None (cohort analysis not required)
- Our implementation: Full cohort tracking for LTV prediction
- Industry standard: D0 = ~70-80% of lifetime value, D7 = ~95%
- Enables ROAS calculation at different time horizons

**Business use:**
- D0 ROAS tells you immediate profitability
- D7 ROAS tells you if marginal campaigns will recover
- Essential for UA (User Acquisition) budget decisions

---

## 9. Real Business Context (Overall)

**What:** Project built for actual company use case, not academic exercise.

**Evidence:**
- Company: Ameno Technologies (Vietnamese mobile gaming company)
- User: Chi Linh (Business Performance Controller)
- Data: 59 real apps, 240 countries, 145K+ rows
- Queries: Actual business questions ("Which apps are losing money?")

**Why this matters:**
- Demonstrates practical application of all technologies
- Business rules reflect real decision-making processes
- Data volume and complexity match production scenarios
- Agent answers serve actual business needs

---

## Summary: Points Justification

| Feature | Category | Reasoning | Est. Points |
|---------|----------|-----------|-------------|
| Multi-source Integration | Data Pipeline | 2 APIs, FULL OUTER JOIN, reconciliation | 5-10 |
| Production API Integration | Data Pipeline | Real OAuth2/REST APIs, not CSV | 5 |
| Custom dbt Macro | Data Architecture | Reusable, safe division handling | 5 |
| 5 Airflow Tasks | Data Pipeline | Exceeds 3 minimum, includes collection | 5 |
| Custom Prompt Engineering | AI/ML | Role, tools, thresholds, hierarchy | 5-10 |
| Schema Context for LLM | AI/ML | 100+ lines, query guidance | 5 |
| Business Rules RAG | AI/ML | 175 lines of real company rules | 5 |
| Cohort Analytics | Data Architecture | D0-D7 tracking for LTV | 5 |

**Conservative estimate:** 15-20 extra points
**With good presentation:** 20-25 extra points

---

## Suggested Pitch to Graders

> "This capstone project goes beyond the basic requirements in several ways:
>
> 1. **Multi-source integration**: Instead of one batch source, we integrate TWO production APIs (AdMob and Adjust) with different schemas, using FULL OUTER JOIN for complete coverage.
>
> 2. **Real production data**: We use actual company data from Ameno Technologies - 59 apps, 240 countries, 145K+ rows - not toy examples.
>
> 3. **Extended Airflow pipeline**: 5 tasks including parallel data collection, exceeding the 3-task minimum.
>
> 4. **Custom prompt engineering**: Domain-specific system prompt with embedded business logic, thresholds, and decision frameworks.
>
> 5. **Comprehensive RAG**: 175 lines of real business rules used by our Business Performance Controller for actual decisions.
>
> 6. **Cohort analytics**: D0/D1/D3/D7 revenue tracking for LTV analysis - industry standard for mobile app monetization.
>
> The entire system serves a real business user (Chi Linh) with real queries about app profitability and UA optimization."
