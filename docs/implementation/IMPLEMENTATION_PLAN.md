# Mobile Analytics Implementation Plan

**Updated:** October 22, 2025
**Decision:** Everything goes to Snowflake (simpler architecture)

---

## What We're Building

**Goal:** Get AdMob + Adjust data into Snowflake, transform it with dbt, pass the test.

**Course Pattern (M01W03):** They taught PostgreSQL → Snowflake because they were learning staging concepts. We skip that - we go straight to Snowflake because:
- Our data sources ARE external (AdMob/Adjust APIs)
- Snowflake handles both batch and incremental perfectly
- No Docker PostgreSQL complexity
- Test requirements still satisfied

---

## Architecture Decision

### OLD PLAN (Too Complex):
```
Real-time: Adjust API → PostgreSQL (Docker) → ???
Batch: AdMob API → Snowflake
Problem: Two databases, Docker management, unclear value
```

### NEW PLAN (Simpler):
```
Pipeline 1 (Batch): AdMob API → Snowflake RAW schema
Pipeline 2 (Incremental): Adjust API → Snowflake RAW schema
Transform: dbt (RAW → STAGING → INTERMEDIATE → MART)
```

**Why This Works:**
- ✅ Batch requirement: AdMob daily loads (13,500+ rows/batch)
- ✅ Real-time requirement: Adjust hourly loads (row-by-row incremental)
- ✅ One database: Snowflake handles everything
- ✅ Industry standard: API → Cloud DWH → dbt transformations

---

## Implementation Phases

### Phase 1: Data Collection Scripts (Week 1)
**What:** Python scripts to fetch data from APIs and load to Snowflake

**Following Course Pattern (M01W03/lab/scripts/data_loader.py):**
```
scripts/
├── collect_admob.py          # Batch: AdMob daily → Snowflake
├── collect_adjust.py         # Incremental: Adjust hourly → Snowflake
└── utils/
    └── snowflake_client.py   # Reusable Snowflake connection
```

**Pipeline 1: AdMob Batch Collection**
- Script: `collect_admob.py`
- Source: AdMob API (daily granularity)
- Destination: Snowflake `RAW.ADMOB_DAILY` table
- Pattern: Fetch entire day's data, load as batch
- Row count: ~13,500 rows per day
- Demo: Load last 7 days = 7 batches = ~94,000 rows

**Pipeline 2: Adjust Incremental Collection**
- Script: `collect_adjust.py`
- Source: Adjust API (hourly granularity)
- Destination: Snowflake `RAW.ADJUST_HOURLY` table
- Pattern: Fetch last hour, append new rows incrementally
- Row count: ~39 rows per hour (936/day)
- Demo: Run script, show fresh timestamps

**Key Features (From Course Pattern):**
- Environment variables for credentials (`.env` file)
- Connection testing functions
- Error handling with clear messages
- Row count validation
- Timestamp conversion handling
- Rich console output for demo clarity

**Expected Files:**
```python
# collect_admob.py structure (following course pattern)
def get_snowflake_connection():
    """Connect to Snowflake using key-pair auth (from dbt profile)"""
    pass

def fetch_admob_data(start_date, end_date):
    """Fetch from AdMob API for date range"""
    pass

def load_to_snowflake(df, table_name):
    """Load dataframe to Snowflake table"""
    pass

def main():
    """Batch load: fetch last N days, load to RAW.ADMOB_DAILY"""
    pass
```

**Environment Setup:**
```bash
# .env file
ADMOB_ACCOUNT_ID=pub-xxxxx
ADMOB_API_KEY=your_api_key

ADJUST_API_TOKEN=your_adjust_token
ADJUST_APP_TOKENS=comma,separated,tokens

# Snowflake (from dbt profiles.yml)
SNOWFLAKE_ACCOUNT=LNB11254
SNOWFLAKE_USER=T34
SNOWFLAKE_PRIVATE_KEY_PATH=/Users/lehongthai/.snowflake/keys/rsa_key.p8
SNOWFLAKE_WAREHOUSE=WH_T34
SNOWFLAKE_DATABASE=DB_T34
SNOWFLAKE_SCHEMA=RAW
SNOWFLAKE_ROLE=RL_T34
```

---

### Phase 2: Snowflake RAW Schema Setup (Week 1)
**What:** Create tables in Snowflake to receive raw data

**RAW Schema Tables:**
```sql
-- RAW.ADMOB_DAILY (batch loads)
CREATE TABLE IF NOT EXISTS RAW.ADMOB_DAILY (
    date DATE NOT NULL,
    app_id VARCHAR(100) NOT NULL,
    country_code VARCHAR(2) NOT NULL,
    ad_format VARCHAR(50),
    ad_impressions INTEGER,
    ad_revenue_usd DECIMAL(10,4),
    estimated_earnings DECIMAL(10,4),
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (date, app_id, country_code, ad_format)
);

-- RAW.ADJUST_HOURLY (incremental loads)
CREATE TABLE IF NOT EXISTS RAW.ADJUST_HOURLY (
    hour_timestamp TIMESTAMP_NTZ NOT NULL,
    app_token VARCHAR(50) NOT NULL,
    country_code VARCHAR(2) NOT NULL,
    tracker_name VARCHAR(100),
    installs INTEGER,
    clicks INTEGER,
    cost_usd DECIMAL(10,4),
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (hour_timestamp, app_token, country_code, tracker_name)
);

-- RAW.ADJUST_COHORTS (daily cohort retention data)
CREATE TABLE IF NOT EXISTS RAW.ADJUST_COHORTS (
    cohort_date DATE NOT NULL,
    app_token VARCHAR(50) NOT NULL,
    country_code VARCHAR(2) NOT NULL,
    installs INTEGER,
    retention_d0 DECIMAL(5,4),
    retention_d1 DECIMAL(5,4),
    retention_d7 DECIMAL(5,4),
    retention_d30 DECIMAL(5,4),
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (cohort_date, app_token, country_code)
);
```

**Test During Demo:**
```sql
-- Show batch data loaded today
SELECT DATE(loaded_at) as load_date,
       COUNT(*) as row_count,
       MIN(date) as earliest_data,
       MAX(date) as latest_data
FROM RAW.ADMOB_DAILY
WHERE loaded_at >= CURRENT_DATE
GROUP BY DATE(loaded_at);

-- Show incremental data loaded in last hour
SELECT DATE_TRUNC('HOUR', loaded_at) as load_hour,
       COUNT(*) as row_count
FROM RAW.ADJUST_HOURLY
WHERE loaded_at >= DATEADD('HOUR', -1, CURRENT_TIMESTAMP())
GROUP BY DATE_TRUNC('HOUR', loaded_at);
```

---

### Phase 3: dbt Transformations (Week 2)
**What:** Transform raw data into analytics-ready dimensional model

**Following Course Pattern (M02W03):**
- Multi-layer architecture (staging → intermediate → mart)
- Incremental models for fact tables
- Tests and documentation
- CI/CD with GitHub Actions

**dbt Project Structure:**
```
models/
├── staging/
│   ├── stg_admob_daily.sql          # Clean + type cast AdMob
│   ├── stg_adjust_hourly.sql        # Clean + type cast Adjust hourly
│   └── stg_adjust_cohorts.sql       # Clean + type cast cohorts
├── intermediate/
│   ├── int_daily_metrics.sql        # Daily grain aggregations
│   └── int_app_country_metrics.sql  # App-country combinations
└── mart/
    ├── dim_app.sql                  # App dimension
    ├── dim_country.sql              # Country dimension
    ├── dim_date.sql                 # Date dimension
    ├── fact_daily_performance.sql   # Main fact table
    └── fact_cohort_retention.sql    # Cohort analysis
```

**Key Transformations:**
- **Staging:** Raw → clean (type casting, null handling, column renaming)
- **Intermediate:** Business logic (ROAS = revenue/cost, eCPM calculations)
- **Mart:** Analytics-ready (star schema with proper keys)

**Incremental Strategy (M02W03 Advanced Pattern):**
```sql
-- fact_daily_performance.sql
{{ config(
    materialized='incremental',
    unique_key=['date', 'app_id', 'country_code'],
    on_schema_change='sync_all_columns'
) }}

SELECT ...
FROM {{ ref('int_daily_metrics') }}
{% if is_incremental() %}
WHERE date > (SELECT MAX(date) FROM {{ this }})
{% endif %}
```

---

### Phase 4: Testing & CI/CD (Week 2)
**What:** Automated quality checks on every commit

**Following Course Pattern (M02W03L04):**
- dbt tests (not_null, unique, relationships)
- SQLFluff linting
- GitHub Actions CI pipeline

**dbt Tests:**
```yaml
# models/staging/schema.yml
models:
  - name: stg_admob_daily
    columns:
      - name: date
        tests:
          - not_null
      - name: ad_revenue_usd
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 10000
```

**GitHub Actions:**
```yaml
# .github/workflows/dbt_ci.yml
name: dbt CI
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
      - name: Setup Python
      - name: Install dependencies
      - name: Run SQLFluff lint
      - name: Run dbt tests
```

---

## Mid-Course Test Demo Flow

**20-Minute Demo Structure:**

### Part 1: Show Data Collection (5 min)
```bash
# Terminal 1: Batch pipeline
python scripts/collect_admob.py --days 7
# Output shows 7 batches loaded (~94K rows total)

# Terminal 2: Incremental pipeline
python scripts/collect_adjust.py --hours 1
# Output shows row-by-row insertion (~39 rows)
```

### Part 2: Validate in Snowflake (3 min)
```sql
-- Prove batch loaded (>500 rows per batch)
SELECT date, COUNT(*) as rows_per_batch
FROM RAW.ADMOB_DAILY
WHERE loaded_at >= CURRENT_DATE
GROUP BY date
ORDER BY date DESC;

-- Prove incremental loaded (fresh timestamps)
SELECT hour_timestamp, loaded_at, COUNT(*) as row_count
FROM RAW.ADJUST_HOURLY
WHERE loaded_at >= DATEADD('HOUR', -1, CURRENT_TIMESTAMP())
GROUP BY hour_timestamp, loaded_at
ORDER BY loaded_at DESC;
```

### Part 3: Show dbt Transformations (8 min)
```bash
# Run dbt
dbt run
dbt test

# Show dimensional model
dbt docs generate
dbt docs serve
```

### Part 4: Show CI/CD (4 min)
- Pull request with GitHub Actions passing
- SQLFluff checks passed
- dbt tests passed

---

## What You Need to Build (Priority Order)

### Week 1 Focus:
1. ✅ **Snowflake connection working** (you have this!)
2. **Create RAW schema tables** (3 tables: admob_daily, adjust_hourly, adjust_cohorts)
3. **Build `collect_admob.py`** (batch pipeline - easier first)
4. **Build `collect_adjust.py`** (incremental pipeline)
5. **Test both scripts** with mock or real API data

### Week 2 Focus:
6. **dbt staging models** (clean raw data)
7. **dbt intermediate models** (business logic)
8. **dbt mart models** (dimensional model)
9. **dbt tests** (data quality)
10. **GitHub Actions CI** (automated testing)

---

## Questions to Answer Before Starting

**Q1: API Credentials Ready?**
- AdMob API: Do you have account ID + API key?
- Adjust API: Do you have app tokens + API token?
- **If NO:** We'll use mock data to build pipeline structure first

**Q2: Starting Point?**
- Option A: Build with mock data first (faster, test-friendly)
- Option B: Real API integration immediately (realistic, but depends on credentials)

**Q3: Test Demo Date?**
- October 29 & November 1 (11 days remaining)
- Timeline: Week 1 = data collection, Week 2 = transformations + CI/CD

---

## Success Criteria

**By End of Week 1:**
- [ ] RAW schema tables created in Snowflake
- [ ] Batch script loads 13,500+ rows per batch
- [ ] Incremental script loads ~40 rows per hour
- [ ] Both scripts show fresh `loaded_at` timestamps
- [ ] Can run demo showing both pipelines

**By End of Week 2:**
- [ ] dbt project with 3-layer architecture (staging → intermediate → mart)
- [ ] Star schema with 3+ dimensions, 2+ fact tables
- [ ] Incremental models working
- [ ] dbt tests passing (10+ tests minimum)
- [ ] GitHub Actions CI running
- [ ] 20-minute demo rehearsed and ready

**Test Score Breakdown:**
- Data Ingestion (35 pts): ✅ Both pipelines working
- Transformation (40 pts): ✅ dbt multi-layer + incremental + tests
- CI/CD (5 pts): ✅ GitHub Actions
- Extra (20 pts): Advanced dbt features, custom macros, documentation

**Target:** 80+ points (Pass: 50+, Good: 70+)

---

## Next Steps

**Tell me:**
1. **Mock data or real APIs?** (I recommend mock first to build structure)
2. **Start with which pipeline?** (I recommend AdMob batch - simpler)
3. **Any questions on this plan?**

Then we'll build it step by step!
