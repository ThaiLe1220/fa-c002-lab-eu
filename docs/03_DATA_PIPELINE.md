# Data Pipeline

Data flow, transformations, and reasoning.

**Verified 2026-01-24:**
| Table | Schema | Rows | Latest Date |
|-------|--------|------|-------------|
| ADMOB_DAILY | RAW_CAPSTONE | 113,412 | 2026-01-23 |
| ADJUST_DAILY | RAW_CAPSTONE | 127,246 | 2026-01-23 |
| FCT_APP_DAILY_PERFORMANCE | ANALYTICS | 145,500 | 2026-01-23 |

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

**Note:** Fact table uses surrogate keys (DATE_KEY, APP_KEY). Join with dimensions for readable values.

**Before run:**
```sql
-- Check current state
SELECT COUNT(*) as row_count, MAX(d.DATE) as max_date
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY;
```

**Run collection + dbt:**
```bash
uv run python scripts/collect_admob_capstone.py --days 1
uv run python scripts/collect_adjust_capstone.py --days 1
cd my_dbt_project && dbt build
```

**After run:**
```sql
-- Count change
SELECT COUNT(*) as row_count, MAX(d.DATE) as max_date
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY;

-- Show new rows (by dbt_updated_at)
SELECT d.DATE, a.APP_NAME, f.AD_REVENUE, f.DBT_UPDATED_AT
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY
JOIN DB_T34.ANALYTICS.DIM_APPS a ON f.APP_KEY = a.APP_KEY
WHERE f.DBT_UPDATED_AT > DATEADD(minute, -10, CURRENT_TIMESTAMP())
ORDER BY f.DBT_UPDATED_AT DESC
LIMIT 10;

-- Summary by date (verify incremental)
SELECT d.DATE, COUNT(*) as rows, SUM(f.AD_REVENUE) as revenue
FROM DB_T34.ANALYTICS.FCT_APP_DAILY_PERFORMANCE f
JOIN DB_T34.ANALYTICS.DIM_DATES d ON f.DATE_KEY = d.DATE_KEY
GROUP BY d.DATE
ORDER BY d.DATE DESC
LIMIT 5;
```

---

## Tests (26 total - Verified)

| Model | Tests | Status |
|-------|-------|--------|
| stg_admob_capstone | not_null(raw_record_id, date, app_store_id, estimated_earnings), unique(raw_record_id) | 5 PASS |
| stg_adjust_capstone | not_null(raw_record_id, date, app_store_id), unique(raw_record_id) | 4 PASS |
| int_app_daily_metrics | not_null(date, app_store_id), unique combination | 4 PASS |
| fct_app_daily_performance | not_null keys, unique performance_key | 5 PASS |
| dim_apps | not_null(app_key, app_store_id), unique keys | 4 PASS |
| dim_dates | not_null(date_key, date), unique keys | 4 PASS |

**Run tests:**
```bash
cd my_dbt_project && dbt test
# Expected output: Done. PASS=26 WARN=0 ERROR=0 SKIP=0 TOTAL=26
```

**Run specific model tests:**
```bash
cd my_dbt_project && dbt test --select "stg_admob_capstone"
# Expected: 5 tests pass
```

---

## Airflow Orchestration

**DAG:** `capstone_dbt_pipeline`
**Location:** `airflow/dags/dbt_pipeline.py`

```
dbt_debug (4s) → dbt_run (24s) → dbt_test (3s)
```

**Configuration:**
- Schedule: `None` (manual trigger for demo)
- Timezone: `Asia/Ho_Chi_Minh`
- Retries: 2
- Retry delay: 5 minutes

**Trigger via CLI:**
```bash
# Unpause and trigger
docker exec airflow-webserver airflow dags unpause capstone_dbt_pipeline
docker exec airflow-webserver airflow dags trigger capstone_dbt_pipeline

# Check status
docker exec airflow-webserver airflow dags list-runs -d capstone_dbt_pipeline -o table
```

**Trigger via UI:**
1. Open http://localhost:8080
2. Login: admin / admin
3. Find `capstone_dbt_pipeline`
4. Click play button → "Trigger DAG"

**Verified run time:** ~31 seconds total (all tasks SUCCESS)

---

## Streaming Data (Kafka → PostgreSQL)

Separate from dbt pipeline. For real-time alerts.

```
kafka/producer.py → Kafka Topic → kafka/consumer.py → PostgreSQL
     │                                                     │
     └── Alert types: ROAS_DROP, SPEND_SPIKE, etc         └── alerts table
```

**Alert Schema (Verified):**
```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    alert_type VARCHAR(50) NOT NULL,  -- ROAS_DROP, SPEND_SPIKE, ERROR_RATE, etc.
    severity VARCHAR(20) NOT NULL,     -- critical, warning, info
    message TEXT NOT NULL,
    region VARCHAR(10),                -- VN, US, JP, etc.
    value NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity);
```

**Connection Details:**
- Host: `localhost` (or `capstone-postgres` from Docker)
- Port: `5433`
- Database: `streaming`
- User: `capstone`
- Password: `capstone123`

**Why PostgreSQL?**
- Simple, fast for demo
- Agent queries via `query_realtime_alerts` tool
- Not for analytics (that's Snowflake)
