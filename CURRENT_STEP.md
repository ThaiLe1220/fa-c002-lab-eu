# Current Step: Phase 2.5 Extension - Full Portfolio + LTV Curve

**Started:** 2026-01-17
**Status:** ✅ COMPLETE (2026-01-18)

---

## Objective

Extend dbt pipeline from 3 filtered apps to **full portfolio** (45+ apps) with **D0-D7 cohort metrics** for LTV curve analysis.

---

## What Changed

| Before (Midtest) | After (Capstone) |
|------------------|------------------|
| 3 filtered apps | 45 Adjust apps, 55 AdMob apps |
| D0 metrics only | D0, D1, D3, D7 cohorts |
| ~1,500 rows/day | ~4,000 rows/day |
| Limited countries | 240 countries |

---

## Data Source Architecture

```
ADJUST (1 API key = ALL apps)          ADMOB (3 publisher tokens)
┌─────────────────────────────┐        ┌─────────────────────────────┐
│ 45 apps                     │        │ pub-4738... → 44 apps       │
│ 240 countries               │        │ pub-3717... → 34 apps       │
│ D0, D1, D3, D7 cohorts      │        │ pub-4109... → 10 apps       │
│ Cost, installs, DAUs        │        │ = 55 unique apps total      │
└─────────────────────────────┘        │ Revenue (source of truth)   │
              │                        └─────────────────────────────┘
              │                                      │
              └──────────────┬───────────────────────┘
                             ▼
                    FULL OUTER JOIN
                    (42 apps in both)
```

---

## LTV Curve: Why D0-D7

```
Revenue Timeline for Mobile Apps:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
D0 (Install day)  ████████████████████████████  70-80%
D1                ████████                       +8%
D3                ████                           +5%
D7                ██                             +3%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
D7 cumulative = ~95% of lifetime value

Business Use:
- D0 ROAS > 100% → Scale immediately
- D0 ROAS 80-100% → Check D7, may recover
- D0 ROAS < 80% → Likely unprofitable
```

---

## New Columns Added

| Column | Source | Purpose | Status |
|--------|--------|---------|--------|
| `ad_revenue_d0` | Adjust | Day 0 revenue | ✅ In dbt |
| `ad_impressions_d0` | Adjust | Day 0 impressions | ✅ In dbt |
| `ad_revenue_d1` | Adjust | Cumulative through D1 | ✅ In dbt (NULL until collected) |
| `ad_impressions_d1` | Adjust | Cumulative through D1 | ✅ In dbt (NULL until collected) |
| `ad_revenue_d3` | Adjust | Cumulative through D3 | ✅ In dbt (NULL until collected) |
| `ad_impressions_d3` | Adjust | Cumulative through D3 | ✅ In dbt (NULL until collected) |
| `ad_revenue_d7` | Adjust | Cumulative through D7 | ✅ In dbt (NULL until collected) |
| `ad_impressions_d7` | Adjust | Cumulative through D7 | ✅ In dbt (NULL until collected) |
| `network_cost` | Adjust | UA spend | ✅ In dbt |
| `paid_impressions` | Adjust | UA impressions | ✅ In dbt |
| `subscrevnt_revenue` | Adjust | IAP revenue | ✅ In dbt |

---

## Tasks

All tasks completed:

- [x] Update `collect_adjust_capstone.py` - add D1, D3, D7 metrics
- [x] Update `collect_adjust_capstone.py` - remove TARGET_APPS filter
- [x] Update `stg_adjust_capstone.sql` - add D1, D3, D7 columns
- [x] Update `int_app_daily_metrics.sql` - add new columns
- [x] Update `fct_app_daily_performance.sql` - add new columns
- [x] Update `schema.yml` files - document new columns
- [x] Update `collect_admob_capstone.py` - remove TARGET_APPS filter
- [x] Add D1, D3, D7 columns to Snowflake ADJUST_DAILY table
- [x] Clear and reload Snowflake with full portfolio data
- [x] Run `dbt build --full-refresh`
- [x] Verify data in Snowflake

---

## Final Verification (2026-01-18)

### Raw Layer
```
ADJUST_DAILY: 4,177 rows, 45 apps
ADMOB_DAILY:  3,803 rows, 55 apps
```

### Fact Table
```
fct_app_daily_performance: 4,793 rows, 58 apps
(FULL OUTER JOIN captures apps from both sources)
```

### D0-D7 Cohort Data
```
Has D0 revenue: 2,035 rows (42.5%)
Has D1 revenue: 649 rows (13.5%)
Has D3 revenue: 649 rows (13.5%)
Has D7 revenue: 649 rows (13.5%)
```

### Revenue Summary
```
AdMob Revenue: $8,640
D0 Revenue:    $6,314
D7 Revenue:    $6,250
Network Cost:  $9,184
D0 ROAS:       68.7%
```

---

## Pipeline Verification

The dbt transformation handles data differences correctly:

| Issue | How Handled |
|-------|-------------|
| Date format (YYYYMMDD vs YYYY-MM-DD) | `TO_DATE()` in staging |
| Country case (us vs US) | `UPPER()` in join |
| Platform case (ios vs iOS) | `UPPER()` in staging |
| Revenue micros | `/ 1000000` in staging |
| Missing apps | `FULL OUTER JOIN` keeps both |

---

## Next Steps

### Phase 2.5.1: Backfill + Idempotency (Pre-requisite for Phase 4)

**Why:** Current data is only 1 day (Jan 17). Need 4 months for realistic agent demo.

**Target:** Dec 25, 2025 → Jan 22, 2026 (29 days, ~230K rows)

**Credit cost:** ~0.1 credits (have 9.98 remaining, ~300 full refreshes possible)

---

**Demo Timeline:**

```
NOW (Jan 23)                         DEMO DAY (Jan 24, 1pm)
─────────────────────────────────────────────────────────────
Backfill: Sep 24 → Jan 22            Morning (~9am): Collect Jan 23
Test with Jan 22 data only           Run dbt --full-refresh
DON'T touch Jan 23 data              Demo with fresh "yesterday" data
```

---

**Tasks:**
- [ ] Add delete-insert pattern to `collect_adjust_capstone.py`
- [ ] Add delete-insert pattern to `collect_admob_capstone.py`
- [ ] Truncate raw tables (clean slate)
- [ ] Run full backfill: Sep 24, 2025 → Jan 22, 2026
- [ ] Run `dbt build --full-refresh`
- [ ] Verify data range in Snowflake
- [ ] Test idempotency: re-run Jan 20-22, verify no duplicates

**Idempotency pattern to implement:**
```python
# Before write_pandas(), add:
cursor.execute(f"""
    DELETE FROM {table_name}
    WHERE DAY BETWEEN '{start_date}' AND '{end_date}'
""")
```

**Execution order (revised - two-phase approach):**

```
Phase 1: Fetch to local CSV (safe, resumable)
──────────────────────────────────────────────
Step 1: ✅ Implement delete-insert in both scripts
Step 2: ✅ TRUNCATE raw tables (clean slate)
Step 3: Add --fetch-only flag to collection scripts
Step 4: Run Adjust fetch day-by-day → data/capstone/adjust_YYYY-MM-DD.csv
Step 5: Run AdMob fetch day-by-day → data/capstone/admob_YYYY-MM-DD.csv
        (~1-2 hrs total, resumable if fails)

Phase 2: Bulk upload to Snowflake (fast)
──────────────────────────────────────────────
Step 6: Bulk upload all CSVs to Snowflake (~5 min)
Step 7: dbt build --full-refresh
Step 8: Verify data range in Snowflake

Phase 3: Test idempotency
──────────────────────────────────────────────
Step 9: Record baseline row counts for Jan 20-22
Step 10: Re-run collection for Jan 20-22
Step 11: Verify row counts unchanged → idempotency proven
```

**Why two-phase:**
- API calls are slow and can timeout
- CSV first = no data loss if API fails mid-way
- Can resume from last successful day
- Bulk upload is fast and atomic

**Demo day commands (Jan 24 morning):**
```bash
python scripts/collect_adjust_capstone.py --start 2026-01-23 --end 2026-01-23
python scripts/collect_admob_capstone.py --start 2026-01-23 --end 2026-01-23
dbt build --full-refresh
```

---

## Data Usage Guide

### Query data (for AI Agent)

```sql
-- Example: Top apps by revenue last 7 days
SELECT a.app_name, SUM(f.ad_revenue) as revenue, SUM(f.network_cost) as cost
FROM fct_app_daily_performance f
JOIN dim_apps a ON f.app_key = a.app_key
JOIN dim_dates d ON f.date_key = d.date_key
WHERE d.date >= DATEADD(day, -7, CURRENT_DATE())
GROUP BY a.app_name
ORDER BY revenue DESC;
```

Agent just needs a Snowflake tool that executes SQL → returns results → LLM formats answer.

### Retry/Rerun any date (safe - idempotent)

```bash
# Rerun single day
python scripts/collect_adjust_capstone.py --start 2026-01-22 --end 2026-01-22
python scripts/collect_admob_capstone.py --start 2026-01-22 --end 2026-01-22
dbt build --full-refresh

# Rerun date range
python scripts/collect_adjust_capstone.py --start 2026-01-15 --end 2026-01-22
python scripts/collect_admob_capstone.py --start 2026-01-15 --end 2026-01-22
dbt build --full-refresh
```

- Delete-insert pattern = no duplicates
- Run same date 10 times → same result
- Airflow DAG just calls these scripts daily

---

### Then: Phase 4 - AI Agent

See `docs/PROJECT_PLAN.md` for Phase 4 checklist.
