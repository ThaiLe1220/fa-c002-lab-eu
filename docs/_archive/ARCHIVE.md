# Archive

Historical documentation from completed project phases. For current docs, see parent `docs/` folder.

---

## Midterm Summary (Nov 2025)

**Score:** 75/100 | **Status:** Passed

### What Was Delivered

- PostgreSQL + Snowflake data pipelines
- dbt models with 3 layers (staging, intermediate, mart)
- Star schema with fact table and dimensions
- CI/CD with GitHub Actions (SQLFluff + dbt test)
- Data collection scripts for AdMob and Adjust APIs

### Key Metrics Implemented

- Ad revenue, impressions, clicks
- Installs, DAUs
- Revenue per install, revenue per click
- CTR calculation via custom macro

### dbt Structure

```
models/
├── 01_staging/       # stg_admob, stg_adjust
├── 02_intermediate/  # int_app_daily_metrics
└── 03_mart/          # fct_app_daily_performance, dim_apps, dim_dates
```

---

## API Validation Summary (Oct 2025)

### AdMob API Findings

- Daily granularity only (HOUR not available for this account)
- 13,508 rows/day with full dimensions
- 365+ days historical depth
- Available: APP, DATE, COUNTRY, PLATFORM, FORMAT, AD_UNIT
- Available: ESTIMATED_EARNINGS, IMPRESSIONS, CLICKS, AD_REQUESTS, OBSERVED_ECPM

### Adjust API Findings

- Hourly granularity available (936 rows/day)
- Daily granularity: 2,216 rows/day
- 365+ days historical depth
- D0 metrics available: ad_revenue_total_d0, ad_impressions_total_d0
- Cohort retention: D0, D1, D7, D30
- IAP revenue NOT tracked (SDK not configured)

### Architecture Decision

- AdMob: Source of truth for revenue (daily batch to Snowflake)
- Adjust: Source for user acquisition + D0 metrics (daily batch to Snowflake)
- PostgreSQL: Hot storage for real-time dashboards (deferred to capstone)

---

## Archived Files

The following files were consolidated into this summary:

**Midterm docs:**
- `01_sample_data.md` - Initial data exploration
- `02_first_model.md` - First dbt model setup
- `IMPLEMENTATION_PLAN.md` - Midterm implementation plan
- `MIDTEST_QUICK_GUIDE.md` - Demo preparation guide
- `midcourse_test_criteria.md` - Test requirements (75/100 achieved)

**Validation docs:**
- `api_validation_results.md` - Full API test results (now in API_REFERENCE.md)

---

## What's Next (Capstone)

- Phase 3: Kafka + Airflow
- Phase 4: AI Agent + RAG
- Phase 5: Docs + Demo

**Final Test:** January 24, 2026

See `docs/PROJECT_PLAN.md` for current status and checklist.
