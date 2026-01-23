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

**Target:** Sep 24, 2025 → Jan 22, 2026 (120 days, ~960K rows)

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
- [ ] Truncate raw tables
- [ ] Run backfill: Sep 24, 2025 → Jan 22, 2026
- [ ] Run `dbt build --full-refresh`
- [ ] Verify data range in Snowflake

**Idempotency pattern to implement:**
```python
# Before write_pandas(), add:
cursor.execute(f"""
    DELETE FROM {table_name}
    WHERE DAY BETWEEN '{start_date}' AND '{end_date}'
""")
```

**Demo day commands (Jan 24 morning):**
```bash
python scripts/collect_adjust_capstone.py --start 2026-01-23 --end 2026-01-23
python scripts/collect_admob_capstone.py --start 2026-01-23 --end 2026-01-23
dbt build --full-refresh
```

---

### Then: Phase 4 - AI Agent

See `docs/PROJECT_PLAN.md` for Phase 4 checklist.
