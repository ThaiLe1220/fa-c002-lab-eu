# Data Pipeline

Data flow, transformations, and reasoning.

---

## Data Sources

### 1. AdMob (Google)
- **Purpose:** Revenue metrics (source of truth)
- **API:** Google AdMob Reporting API
- **Collection:** `scripts/collect_admob_capstone.py`
- **Target:** `DB_T34.RAW_CAPSTONE.ADMOB_DAILY`

**Key Fields:**
| Field | Description |
|-------|-------------|
| estimated_earnings | Revenue in micros (divide by 1M) |
| ad_impressions | Total ad impressions |
| ad_clicks | Total ad clicks |
| observed_ecpm | eCPM in micros |

### 2. Adjust
- **Purpose:** Attribution + UA cost + Cohort metrics
- **API:** Adjust Reporting API
- **Collection:** `scripts/collect_adjust_capstone.py`
- **Target:** `DB_T34.RAW_CAPSTONE.ADJUST_DAILY`

**Key Fields:**
| Field | Description |
|-------|-------------|
| installs | New installs |
| network_cost | UA spend |
| ad_revenue_total_d0 | D0 ad revenue (install day) |
| ad_revenue_total_d7 | Cumulative D7 ad revenue |

---

## Why Two Sources?

| Metric | AdMob | Adjust | Use |
|--------|-------|--------|-----|
| Revenue | Source of truth | For reconciliation | AdMob |
| Installs | N/A | Source of truth | Adjust |
| UA Cost | N/A | Source of truth | Adjust |
| D0/D7 Cohort | N/A | Source of truth | Adjust |

**Reasoning:**
- AdMob reports actual earnings from Google (what you get paid)
- Adjust reports attributed revenue per install cohort (for LTV analysis)
- They don't always match due to attribution windows and timing

---

## dbt Model Lineage

```
RAW_CAPSTONE (Snowflake)
├── admob_daily
└── adjust_daily
       │
       ▼
01_STAGING (views)
├── stg_admob_capstone     # Clean + cast types
└── stg_adjust_capstone    # Clean + cast types
       │
       ▼
02_INTERMEDIATE (incremental)
└── int_app_daily_metrics  # FULL OUTER JOIN on app+date+country+platform
       │
       ▼
03_MART (tables)
├── fct_app_daily_performance  # Fact table with keys
├── dim_apps                   # App dimension
└── dim_dates                  # Date dimension
```

---

## Model Details

### stg_admob_capstone (view)
**File:** `my_dbt_project/models/01_staging/stg_admob_capstone.sql`

**Transformations:**
```sql
-- Date conversion (YYYYMMDD string → date)
TO_DATE(DATE, 'YYYYMMDD') AS date

-- Revenue conversion (micros → USD)
CAST(ESTIMATED_EARNINGS AS DECIMAL(18,6)) / 1000000 AS estimated_earnings

-- Platform normalization
UPPER(PLATFORM) AS platform
```

**Why view?** Source data is read-only, no need to materialize.

---

### stg_adjust_capstone (view)
**File:** `my_dbt_project/models/01_staging/stg_adjust_capstone.sql`

**Transformations:**
```sql
-- Date conversion (YYYY-MM-DD string → date)
TO_DATE(DAY, 'YYYY-MM-DD') AS date

-- Store ID rename for join
STORE_ID AS app_store_id

-- Platform normalization
UPPER(OS_NAME) AS platform
```

**Why view?** Same as admob - source data transformation only.

---

### int_app_daily_metrics (incremental)
**File:** `my_dbt_project/models/02_intermediate/int_app_daily_metrics.sql`

**Key Logic:**
```sql
-- FULL OUTER JOIN to capture all apps from both sources
FROM admob adm
FULL OUTER JOIN adjust adj
    ON adm.app_store_id = adj.app_store_id
    AND adm.date = adj.date
    AND UPPER(adm.country_code) = UPPER(adj.country_code)
    AND adm.platform = adj.platform
```

**Incremental Strategy:**
```sql
{% if is_incremental() %}
WHERE date > (SELECT MAX(date) FROM {{ this }})
{% endif %}
```

**Why FULL OUTER JOIN?**
- Some apps only in AdMob (no Adjust tracking)
- Some apps only in Adjust (no ad revenue yet)
- We want complete picture

**Why incremental?**
- Data is append-only by date
- No need to rebuild entire table on each run
- Unique key: `[app_store_id, date, country_code, platform]`

---

### fct_app_daily_performance (table)
**File:** `my_dbt_project/models/03_mart/fct_app_daily_performance.sql`

**Key Features:**
```sql
-- Surrogate key for fact table
{{ dbt_utils.generate_surrogate_key(['m.app_store_id', 'm.date', 'm.country_code', 'm.platform']) }} AS performance_key

-- Foreign keys to dimensions
a.app_key,
d.date_key,

-- Calculated CTR
{{ calculate_ctr('m.ad_clicks', 'm.ad_impressions') }} AS ad_ctr
```

**Why table?** Final output for BI/Agent queries - needs fast access.

---

### dim_apps (table)
**File:** `my_dbt_project/models/03_mart/dim_apps.sql`

```sql
SELECT DISTINCT
    {{ dbt_utils.generate_surrogate_key(['app_store_id']) }} AS app_key,
    app_store_id,
    CASE app_store_id
        WHEN 'video.ai.videogenerator' THEN 'Video AI Generator'
        ...
    END AS app_name
FROM {{ ref('int_app_daily_metrics') }}
```

**Why?** Slowly changing dimension - app names may change.

---

### dim_dates (table)
**File:** `my_dbt_project/models/03_mart/dim_dates.sql`

```sql
SELECT
    {{ dbt_utils.generate_surrogate_key(['date']) }} AS date_key,
    date,
    YEAR(date) AS year,
    MONTH(date) AS month,
    DAY(date) AS day,
    DAYOFWEEK(date) AS day_of_week,
    DAYNAME(date) AS day_name
FROM date_spine
```

**Why?** Standard date dimension for time-based analysis.

---

## Key Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| D0 ROAS | `ad_revenue_d0 / network_cost * 100` | Install day return |
| D7 ROAS | `ad_revenue_d7 / network_cost * 100` | Week 1 return |
| CPI | `network_cost / installs` | Cost per install |
| eCPM | `ad_revenue / ad_impressions * 1000` | Revenue per 1K impressions |
| CTR | `ad_clicks / ad_impressions * 100` | Click-through rate |

**Business Context:**
- D0 ROAS of 70-80% is typical for mobile games
- D0 = ~70-80% of lifetime value
- D7 = ~95% of lifetime value
- ROAS < 80% = losing money (from business rules)

---

## Incremental Proof Commands

**Before run:**
```sql
SELECT COUNT(*) as before_count, MAX(date) as max_date
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE;
```

**Run collection + dbt:**
```bash
python scripts/collect_admob_capstone.py --days 1
python scripts/collect_adjust_capstone.py --days 1
cd my_dbt_project && dbt build
```

**After run:**
```sql
-- Count change
SELECT COUNT(*) as after_count, MAX(date) as max_date
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE;

-- Show new rows (by dbt_updated_at)
SELECT performance_key, date, app_store_id, dbt_updated_at
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE
WHERE dbt_updated_at > DATEADD(minute, -10, CURRENT_TIMESTAMP())
ORDER BY dbt_updated_at DESC
LIMIT 10;
```

---

## Tests (26 total)

| Model | Tests |
|-------|-------|
| stg_admob_capstone | not_null(raw_record_id), unique(raw_record_id), not_null(date, app_store_id, estimated_earnings) |
| stg_adjust_capstone | not_null(raw_record_id), unique(raw_record_id), not_null(date, app_store_id) |
| int_app_daily_metrics | - |
| fct_app_daily_performance | - |
| dim_apps | - |
| dim_dates | - |

**Run tests:**
```bash
cd my_dbt_project && dbt test
```

---

## Streaming Data (Kafka → PostgreSQL)

Separate from dbt pipeline. For real-time alerts.

```
kafka/producer.py → Kafka Topic → kafka/consumer.py → PostgreSQL
     │                                                     │
     └── Alert types: ROAS_DROP, BUDGET_EXCEED, etc       └── alerts table
```

**Alert Schema:**
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50),
    severity VARCHAR(20),   -- critical, warning, info
    app_id VARCHAR(100),
    country_code VARCHAR(10),
    metric_value DECIMAL(18,6),
    threshold_value DECIMAL(18,6),
    message TEXT,
    created_at TIMESTAMP
);
```

**Why PostgreSQL?**
- Simple, fast for demo
- Agent queries via `query_realtime_alerts` tool
- Not for analytics (that's Snowflake)
