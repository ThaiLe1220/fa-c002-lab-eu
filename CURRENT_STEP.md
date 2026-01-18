# Current Step: Phase 2.5 - dbt Migration

**Started:** 2026-01-17
**Status:** ✅ COMPLETE (2026-01-17)

**Result:** dbt build PASS=32, ERROR=0

---

## Objective

Migrate dbt models from `RAW_MIDTEST` → `RAW_CAPSTONE` and add D0 metrics.

---

## Current State

```
RAW_CAPSTONE                    dbt Models (PUBLIC schema)
├── ADMOB_DAILY ────────────→  stg_admob_capstone ✅
└── ADJUST_DAILY ───────────→  stg_adjust_capstone ✅
                                        ↓
                               int_app_daily_metrics ✅
                                        ↓
                              ┌─────────┼─────────┐
                              ↓         ↓         ↓
                          dim_apps  dim_dates  fct_app_daily_performance ✅
                              ↓         ↓         ↓
                              └─────────┴─────────┘
                                   ANALYTICS
```

---

## New Columns Added ✅

| Column | Source | Purpose | Status |
|--------|--------|---------|--------|
| `network_cost` | ADJUST | UA spend | ✅ |
| `ad_revenue_d0` | ADJUST | D0 revenue (70-80% of total) | ✅ |
| `ad_impressions_d0` | ADJUST | D0 impressions | ✅ |
| `paid_impressions` | ADJUST | UA impressions for IPM | ✅ |
| `subscrevnt_revenue` | ADJUST | IAP revenue | ✅ |
| `observed_ecpm` | ADMOB | Pre-calculated eCPM | ✅ |
| `ad_revenue_adjust` | ADJUST | For reconciliation | ✅ |
| `ad_impressions_adjust` | ADJUST | For reconciliation | ✅ |

---

## Tasks

- [x] 1. Update `sources.yml` - add `raw_capstone` source ✅
- [x] 2. Create `stg_admob_capstone.sql` ✅
- [x] 3. Create `stg_adjust_capstone.sql` (with D0 columns) ✅
- [x] 4. Update `int_app_daily_metrics.sql` - use capstone staging + add columns ✅
- [x] 5. Update `fct_app_daily_performance.sql` - add all metrics ✅
- [x] 6. Update `schema.yml` files - document new columns ✅
- [x] 7. Run `dbt build` and verify ✅ (PASS=32, ERROR=0)
- [ ] 8. (Optional) Deprecate midtest models

---

## Files to Modify

```
my_dbt_project/models/
├── 01_staging/
│   ├── sources.yml          # ADD raw_capstone source
│   ├── schema.yml           # ADD new model definitions
│   ├── stg_admob_capstone.sql   # CREATE
│   └── stg_adjust_capstone.sql  # CREATE
├── 02_intermediate/
│   ├── schema.yml           # UPDATE columns
│   └── int_app_daily_metrics.sql  # UPDATE
└── 03_mart/
    ├── schema.yml           # UPDATE columns
    └── fct_app_daily_performance.sql  # UPDATE
```

---

## RAW_CAPSTONE Table Schemas

### ADMOB_DAILY
```sql
RAW_RECORD_ID, BATCH_ID, LOADED_AT,
DATE, APP_STORE_ID, APP_NAME, COUNTRY_CODE, PLATFORM,
ESTIMATED_EARNINGS, AD_IMPRESSIONS, AD_CLICKS,
AD_REQUESTS, MATCHED_REQUESTS, OBSERVED_ECPM
```

### ADJUST_DAILY
```sql
RAW_RECORD_ID, BATCH_ID, LOADED_AT,
DAY, STORE_ID, APP, COUNTRY_CODE, COUNTRY, OS_NAME,
INSTALLS, CLICKS, DAUS, AD_REVENUE, AD_IMPRESSIONS,
NETWORK_COST, AD_REVENUE_TOTAL_D0, AD_IMPRESSIONS_TOTAL_D0,
PAID_IMPRESSIONS, SUBSCREVNT_REVENUE
```

---

## Verification & Testing

### Pre-flight Check (before starting)

```bash
# 1. Verify dbt connection
cd /Users/lehongthai/code_personal/fa-c002-lab
source .venv/bin/activate
cd my_dbt_project && dbt debug

# 2. List current models (should show 6)
dbt ls --resource-type model

# 3. Check RAW_CAPSTONE has data (run in Snowflake)
# SELECT COUNT(*) FROM DB_T34.RAW_CAPSTONE.ADMOB_DAILY;
# SELECT COUNT(*) FROM DB_T34.RAW_CAPSTONE.ADJUST_DAILY;
```

**Status:** ✅ dbt 1.10.13, connection OK, 6 models found

### After Each Task

| Task | Verify Command |
|------|----------------|
| 1. sources.yml | `dbt ls --resource-type source` |
| 2-3. staging | `dbt run --select stg_admob_capstone stg_adjust_capstone` |
| 4. intermediate | `dbt run --select int_app_daily_metrics` |
| 5. mart | `dbt run --select fct_app_daily_performance` |
| 6. schema | `dbt test --select staging intermediate mart` |

### Full Build Test

```bash
# Run all models
dbt build

# Expected output:
# - 8 models (6 existing + 2 new staging)
# - All tests pass
# - No errors
```

### Data Validation (Snowflake)

```sql
-- 1. Check staging has data
SELECT COUNT(*) as rows, MIN(date) as min_date, MAX(date) as max_date
FROM DB_T34.ANALYTICS.STG_ADMOB_CAPSTONE;

SELECT COUNT(*) as rows, MIN(date) as min_date, MAX(date) as max_date
FROM DB_T34.ANALYTICS.STG_ADJUST_CAPSTONE;

-- 2. Check new columns in fact table
SELECT
    date_key,
    country_code,
    ad_revenue,
    network_cost,
    ad_revenue_d0,
    ad_impressions_d0,
    paid_impressions,
    subscrevnt_revenue
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE
LIMIT 5;

-- 3. Calculate D0 ROAS (main metric)
SELECT
    d.date,
    SUM(f.ad_revenue_d0) as total_d0_rev,
    SUM(f.network_cost) as total_cost,
    SUM(f.ad_revenue_d0) / NULLIF(SUM(f.network_cost), 0) as d0_roas
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.date_key = d.date_key
GROUP BY d.date
ORDER BY d.date DESC
LIMIT 7;

-- 4. Data reconciliation (AdMob vs Adjust)
SELECT
    d.date,
    SUM(f.ad_revenue) as admob_rev,
    SUM(f.ad_revenue_adjust) as adjust_rev,
    ABS(SUM(f.ad_revenue) - SUM(f.ad_revenue_adjust)) / NULLIF(SUM(f.ad_revenue), 0) * 100 as diff_pct
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.date_key = d.date_key
GROUP BY d.date
ORDER BY d.date DESC
LIMIT 7;
```

### Success Criteria

- [x] `dbt build` completes with no errors ✅
- [x] All tests pass (32/32) ✅
- [x] Fact table has new columns: `network_cost`, `ad_revenue_d0`, `ad_impressions_d0`, `paid_impressions`, `subscrevnt_revenue` ✅
- [ ] D0 ROAS can be calculated (verify in Snowflake)
- [ ] Data variance between AdMob/Adjust < 10% (verify in Snowflake)

---

## Notes

- Keep midtest models for now (don't break existing)
- Collection scripts already load to RAW_CAPSTONE
- AdMob = source of truth for revenue
- Adjust = source of truth for attribution + cost
