# Data Schema

## Migration Status

**Current:** dbt models use `RAW_MIDTEST` schema (midterm)
**Target:** dbt models use `RAW_CAPSTONE` schema with D0 metrics

### What's Missing

| Column | Source | Status |
|--------|--------|--------|
| ad_revenue_d0 | Adjust API | In RAW_CAPSTONE, not in dbt |
| ad_impressions_d0 | Adjust API | In RAW_CAPSTONE, not in dbt |
| network_cost | Adjust API | In RAW_CAPSTONE, not in dbt |
| paid_impressions | Adjust API | In RAW_CAPSTONE, not in dbt |
| subscrevnt_revenue | Adjust API | In RAW_CAPSTONE, not in dbt |

### Migration Steps

1. **Create new staging models** pointing to RAW_CAPSTONE
   - `stg_admob_capstone.sql` → RAW_CAPSTONE.ADMOB_DAILY
   - `stg_adjust_capstone.sql` → RAW_CAPSTONE.ADJUST_DAILY

2. **Update intermediate model** to include new columns
   - Add D0 metrics from Adjust
   - Add network_cost, paid_impressions, subscrevnt_revenue

3. **Update fact table** with calculated fields
   - d0_revenue_pct = ad_revenue_d0 / ad_revenue
   - roas = ad_revenue / network_cost

4. **Run dbt build** and verify data flows correctly

5. **Deprecate midtest models** (keep for reference)

**Prerequisite for:** AI Agent integration (Phase 4)

---

## CSV File Formats

### AdMob CSV

**File pattern:** `admob_pub-{PUBLISHER_ID}_{START}_{END}.csv`

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| DISPLAY_NAME | String | `AI Video Generator: Flix AI` | App name |
| APP_STORE_ID | String | `video.ai.videogenerator` | Package ID (join key) |
| DATE | Date | `2025-09-19` | YYYY-MM-DD |
| COUNTRY | String | `AE`, `US`, `IN` | ISO 2-letter |
| PLATFORM | String | `Android`, `iOS` | OS |
| ESTIMATED_EARNINGS | Float | `2.98` | Revenue USD |
| IMPRESSIONS | Integer | `638` | Ads shown |

**Granularity:** app + country + platform + date

### Adjust CSV

**File pattern:** `adjust_{START}_{END}.csv`

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| app | String | `AI GPT Generator` | App name |
| store_id | String | `ai.video.generator` | Package ID (join key) |
| day | Date | `2025-09-19` | YYYY-MM-DD |
| country_code | String | `in`, `bd` | ISO 2-letter (lowercase) |
| country | String | `India` | Full name |
| os_name | String | `android`, `ios` | OS (lowercase) |
| installs | Integer | `23320` | New downloads |
| daus | Float | `39308.0` | Daily active users |
| ad_revenue | Float | `648.51` | Ad revenue USD |
| ad_impressions | Integer | `315232` | Impressions |
| ad_revenue_total_d0 | Float | `473.92` | Day 0 revenue |
| ad_impressions_total_d0 | Integer | `237762` | Day 0 impressions |
| network_cost | Float | `663.29` | Marketing spend |

**Granularity:** app + country + OS + date

---

## Snowflake Tables

### Fact Table: fct_app_daily_performance

```sql
SELECT
    performance_key,      -- MD5 surrogate key
    app_key,              -- FK to dim_apps
    date_key,             -- FK to dim_dates
    country_code,         -- Degenerate dimension
    platform,             -- Degenerate dimension

    -- AdMob metrics
    ad_revenue,
    ad_impressions,
    ad_clicks,
    ad_ctr,               -- Calculated: clicks/impressions

    -- Adjust metrics
    installs,
    clicks,
    daus,

    -- D0 metrics (critical for ROAS)
    ad_revenue_d0,
    ad_impressions_d0,
    d0_revenue_pct,       -- Calculated: d0/total

    -- Cost & revenue
    network_cost,
    paid_impressions,
    subscrevnt_revenue,
    total_revenue,        -- Calculated: ad + subs

    -- Derived metrics
    revenue_per_install,
    revenue_per_click,

    dbt_updated_at
FROM analytics.fct_app_daily_performance
```

### Dimension: dim_apps

```sql
SELECT
    app_key,        -- MD5 surrogate key
    app_store_id,   -- Natural key (package ID)
    app_name        -- Display name
FROM analytics.dim_apps
```

### Dimension: dim_dates

```sql
SELECT
    date_key,       -- MD5 surrogate key
    date,           -- Natural key
    year,
    month,
    day,
    day_of_week,
    day_name
FROM analytics.dim_dates
```

---

## Example Queries

### Total Revenue This Week

```sql
SELECT SUM(ad_revenue) as total_revenue
FROM analytics.fct_app_daily_performance f
JOIN analytics.dim_dates d ON f.date_key = d.date_key
WHERE d.date >= DATEADD(day, -7, CURRENT_DATE())
```

### Top 5 Apps by Revenue

```sql
SELECT a.app_name, SUM(f.ad_revenue) as revenue
FROM analytics.fct_app_daily_performance f
JOIN analytics.dim_apps a ON f.app_key = a.app_key
GROUP BY a.app_name
ORDER BY revenue DESC
LIMIT 5
```

### iOS vs Android

```sql
SELECT
    platform,
    SUM(ad_revenue) as revenue,
    SUM(installs) as installs
FROM analytics.fct_app_daily_performance
GROUP BY platform
```

### D0 Performance by App

```sql
SELECT
    a.app_name,
    SUM(f.ad_revenue_d0) as d0_revenue,
    SUM(f.ad_revenue) as total_revenue,
    ROUND(SUM(f.ad_revenue_d0) / NULLIF(SUM(f.ad_revenue), 0) * 100, 1) as d0_pct
FROM analytics.fct_app_daily_performance f
JOIN analytics.dim_apps a ON f.app_key = a.app_key
WHERE f.ad_revenue > 0
GROUP BY a.app_name
ORDER BY d0_pct DESC
```

### Marketing ROI

```sql
SELECT
    a.app_name,
    SUM(f.ad_revenue) as revenue,
    SUM(f.network_cost) as spend,
    ROUND(SUM(f.ad_revenue) / NULLIF(SUM(f.network_cost), 0), 2) as roas
FROM analytics.fct_app_daily_performance f
JOIN analytics.dim_apps a ON f.app_key = a.app_key
WHERE f.network_cost > 0
GROUP BY a.app_name
ORDER BY roas DESC
```

### Country Performance

```sql
SELECT
    country_code,
    SUM(ad_revenue) as revenue,
    SUM(installs) as installs,
    ROUND(SUM(ad_revenue) / NULLIF(SUM(installs), 0), 2) as revenue_per_install
FROM analytics.fct_app_daily_performance
GROUP BY country_code
ORDER BY revenue DESC
LIMIT 10
```

---

## Joining AdMob + Adjust

### Match Keys

```python
AdMob.APP_STORE_ID == Adjust.store_id
AdMob.DATE == Adjust.day
AdMob.COUNTRY == Adjust.country_code  # (case-insensitive)
AdMob.PLATFORM == Adjust.os_name      # (lowercase in Adjust)
```

### Expected Variance

```
AdMob.ESTIMATED_EARNINGS ~ Adjust.ad_revenue   # 2-5% variance normal
AdMob.IMPRESSIONS ~ Adjust.ad_impressions      # 2-5% variance normal
```

**Discrepancy reasons:** Time zones, attribution windows, network delays

---

## Key Metrics Reference

| Metric | Formula | Business Use |
|--------|---------|--------------|
| **CPI** | network_cost / installs | Cost per install |
| **ARPDAU** | ad_revenue / daus | Revenue per DAU |
| **eCPM** | (revenue / impressions) * 1000 | Revenue per 1K impressions |
| **D0 Revenue %** | ad_revenue_d0 / ad_revenue | Same-day payback |
| **ROAS** | ad_revenue / network_cost | Return on ad spend |
| **CTR** | clicks / impressions | Click-through rate |
