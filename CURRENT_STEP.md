# Current Step: Phase 4 - AI Agent

**Started:** 2026-01-23
**Demo:** 2026-01-24, 1:00 PM
**Status:** IN PROGRESS

---

## Objective

Build AI chatbot that queries Snowflake data to answer Chi Linh's business questions.

---

## Previous Phase (2.5) - COMPLETE

| Metric | Value |
|--------|-------|
| Date range | Dec 25, 2025 → Jan 22, 2026 (29 days) |
| ADJUST_DAILY | 122,895 rows |
| ADMOB_DAILY | 109,594 rows |
| fct_app_daily_performance | 140,546 rows |
| dim_apps | 59 apps |
| Total revenue | $251,878 |
| Total cost | $245,940 |

---

## Phase 4 Tasks

### Priority 1: Snowflake Tool

- [ ] Create `agent/tools/snowflake_tools.py`
- [ ] Implement `query_snowflake()` function
- [ ] Test with 5 sample queries
- [ ] Verify results match direct Snowflake query

### Priority 2: LangGraph Agent

- [ ] Create `agent/config.py`
- [ ] Create `agent/prompts.py` with system prompt
- [ ] Create `agent/agent.py` with StateGraph
- [ ] Add conversation memory
- [ ] Test with CLI

### Priority 3: Streamlit UI

- [ ] Create `agent/app.py`
- [ ] Chat interface with history
- [ ] "Show SQL" toggle
- [ ] Style for demo

### Optional: Checkboxes

- [ ] Kafka tool (fake streaming data)
- [ ] RAG tool (PDF search)

---

## Verification Checklist

### Chi Linh's Questions (must pass 8/10)

| # | Question | SQL OK | Numbers OK | Pass |
|---|----------|--------|------------|------|
| 1 | Which app spends most? Profitable? | [ ] | [ ] | [ ] |
| 2 | Why did metrics change vs yesterday? | [ ] | [ ] | [ ] |
| 3 | D0 ROAS by country? | [ ] | [ ] | [ ] |
| 4 | Revenue breakdown by country? | [ ] | [ ] | [ ] |
| 5 | Adjust vs AdMob diff %? | [ ] | [ ] | [ ] |
| 6 | CPI analysis | [ ] | [ ] | [ ] |
| 7 | Installs over time by country? | [ ] | [ ] | [ ] |
| 8 | Break-even analysis? | [ ] | [ ] | [ ] |
| 9 | Can losing app become profitable? | [ ] | [ ] | [ ] |
| 10 | Top apps by metric? | [ ] | [ ] | [ ] |

### Response Time

| Operation | Target | Actual | Pass |
|-----------|--------|--------|------|
| Simple query | < 5s | | [ ] |
| Aggregation | < 10s | | [ ] |
| Full conversation | < 20s | | [ ] |

---

## Demo Day Commands (Jan 24 Morning)

```bash
# 1. Collect fresh data (Jan 23)
python scripts/collect_adjust_capstone.py --start 2026-01-23 --end 2026-01-23
python scripts/collect_admob_capstone.py --start 2026-01-23 --end 2026-01-23

# 2. Refresh dbt
cd my_dbt_project && dbt build --full-refresh

# 3. Test agent
python agent/agent.py --interactive

# 4. Run Streamlit demo
streamlit run agent/app.py
```

---

## Demo Script (10 min)

1. **Opening:** "AI Agent for Ameno Technologies mobile analytics"
2. **Q1:** "What's total revenue and cost last week?" → Show SQL + results
3. **Q2:** "Which apps are losing money?" → Drill-down
4. **Q3:** "Why is [App] losing money?" → Break-even analysis
5. **Q4:** "Compare Thailand vs Vietnam" → Side-by-side
6. **Close:** Show memory works, mention Kafka/RAG checkboxes

**Backup questions:** "How many apps?", "Average CPI?", "Top 5 countries by revenue"

---

## Quick Reference

### Key Metrics (for system prompt)

```sql
-- ROAS (profitability)
d0_roas = ad_revenue_d0 / network_cost
d7_roas = ad_revenue_d7 / network_cost

-- Cost
cpi = network_cost / installs

-- Monetization
ecpm = ad_revenue * 1000 / ad_impressions
```

### Thresholds

| Metric | Good | Marginal | Bad |
|--------|------|----------|-----|
| D0 ROAS | >100% | 80-100% | <80% |
| CPI change | stable | +15% | +30% |
| eCPM change | stable | -10% | -15% |

### Tables

```
analytics.fct_app_daily_performance  -- Main fact table
analytics.dim_apps                   -- App names
analytics.dim_dates                  -- Date dimension
```

---

## Detailed Plan

See `docs/PHASE4_IMPLEMENTATION.md` for:
- Full technical architecture
- All 10 test questions with expected SQL
- Timeline and risk mitigation
- Complete file structure

---

## Data Usage (for reference)

### Query example (agent will generate similar)

```sql
-- Top apps by revenue
SELECT a.app_name, SUM(f.ad_revenue) as revenue, SUM(f.network_cost) as cost
FROM analytics.fct_app_daily_performance f
JOIN analytics.dim_apps a ON f.app_key = a.app_key
GROUP BY a.app_name
ORDER BY revenue DESC
LIMIT 10;
```

### Retry/Rerun any date (idempotent)

```bash
python scripts/collect_adjust_capstone.py --start 2026-01-22 --end 2026-01-22
python scripts/collect_admob_capstone.py --start 2026-01-22 --end 2026-01-22
dbt build --full-refresh
```
