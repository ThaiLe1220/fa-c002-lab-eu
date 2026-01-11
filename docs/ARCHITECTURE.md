# Architecture

## Data Pipeline Overview

```
PYTHON COLLECTION           SNOWFLAKE RAW              DBT TRANSFORMATION         STAR SCHEMA
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│ collect_admob   │───────▶│ ADMOB_DAILY     │───────▶│ stg_admob       │───┐    │ dim_apps        │
│ collect_adjust  │───────▶│ ADJUST_DAILY    │───────▶│ stg_adjust      │───┼───▶│ dim_dates       │
└─────────────────┘        └─────────────────┘        └─────────────────┘   │    │ fct_performance │
                                                              │             │    └─────────────────┘
                                                              ▼             │
                                                      ┌─────────────────┐   │
                                                      │ int_app_daily   │───┘
                                                      │ _metrics        │
                                                      └─────────────────┘
```

**Schema:** `DB_T34.RAW_CAPSTONE` (raw) -> `DB_T34.ANALYTICS` (mart)

---

## Star Schema ERD

```
                    ┌─────────────────────────────────────────┐
                    │         fct_app_daily_performance       │
                    ├─────────────────────────────────────────┤
                    │ performance_key (PK)                    │
┌──────────────┐    │ app_key (FK) ─────────────────────────┐ │    ┌──────────────┐
│   dim_apps   │    │ date_key (FK) ───────────────────────┐│ │    │  dim_dates   │
├──────────────┤    │ country_code                         ││ │    ├──────────────┤
│ app_key (PK) │◀───│ platform                             ││ │───▶│ date_key (PK)│
│ app_store_id │    │ ad_revenue                           ││ │    │ date         │
│ app_name     │    │ ad_impressions                       ││ │    │ year         │
└──────────────┘    │ ad_clicks                            ││ │    │ month        │
                    │ ad_ctr                               ││ │    │ day          │
                    │ installs                             ││ │    │ day_of_week  │
                    │ clicks                               ││ │    │ day_name     │
                    │ daus                                 ││ │    └──────────────┘
                    │ ad_revenue_d0                        ││ │
                    │ ad_impressions_d0                    ││ │
                    │ d0_revenue_pct                       ││ │
                    │ network_cost                         ││ │
                    │ paid_impressions                     ││ │
                    │ subscrevnt_revenue                   ││ │
                    │ total_revenue                        ││ │
                    │ revenue_per_install                  ││ │
                    │ revenue_per_click                    ││ │
                    │ dbt_updated_at                       │└─┘
                    └─────────────────────────────────────────┘
```

**Grain:** One row per app per day per country per platform

---

## dbt Transformation Layers

### Layer 1: Staging (Views)

Clean and standardize raw data.

| Model | Source | Purpose |
|-------|--------|---------|
| `stg_admob` | RAW_CAPSTONE.ADMOB_DAILY | Type casting, date parsing |
| `stg_adjust` | RAW_CAPSTONE.ADJUST_DAILY | Column renaming, standardization |

**Tests:** unique(raw_record_id), not_null(raw_record_id, date, app_store_id)

### Layer 2: Intermediate (Incremental Table)

Join both sources.

| Model | Purpose |
|-------|---------|
| `int_app_daily_metrics` | FULL OUTER JOIN stg_admob + stg_adjust |

**Join Key:** (app_store_id, date, country_code, platform)
**Incremental:** WHERE date > MAX(date)

### Layer 3: Mart (Tables)

Analytics-ready star schema.

| Model | Type | Purpose |
|-------|------|---------|
| `dim_apps` | Dimension | App metadata |
| `dim_dates` | Dimension | Date attributes |
| `fct_app_daily_performance` | Fact | All metrics |

**Surrogate Keys:** MD5 hash via dbt_utils.generate_surrogate_key

---

## Raw Layer Schema

### ADMOB_DAILY

```sql
CREATE TABLE RAW_CAPSTONE.ADMOB_DAILY (
    RAW_RECORD_ID VARCHAR PRIMARY KEY,  -- UUID lineage
    BATCH_ID VARCHAR,
    DATE VARCHAR,                        -- YYYYMMDD string
    APP_STORE_ID VARCHAR,
    COUNTRY_CODE VARCHAR,
    PLATFORM VARCHAR,
    ESTIMATED_EARNINGS NUMBER,
    AD_IMPRESSIONS NUMBER,
    AD_CLICKS NUMBER,
    LOADED_AT TIMESTAMP
);
```

### ADJUST_DAILY

```sql
CREATE TABLE RAW_CAPSTONE.ADJUST_DAILY (
    RAW_RECORD_ID VARCHAR PRIMARY KEY,  -- UUID lineage
    BATCH_ID VARCHAR,
    DAY DATE,
    STORE_ID VARCHAR,
    COUNTRY_CODE VARCHAR,
    OS_NAME VARCHAR,
    INSTALLS NUMBER,
    CLICKS NUMBER,
    DAUS NUMBER,
    AD_REVENUE NUMBER,
    AD_IMPRESSIONS NUMBER,
    AD_REVENUE_TOTAL_D0 NUMBER,         -- Day 0 revenue
    AD_IMPRESSIONS_TOTAL_D0 NUMBER,     -- Day 0 impressions
    NETWORK_COST NUMBER,                 -- Marketing spend
    PAID_IMPRESSIONS NUMBER,
    SUBSCREVNT_REVENUE NUMBER,
    LOADED_AT TIMESTAMP
);
```

---

## Key Features

| Feature | Implementation |
|---------|----------------|
| D0 Metrics | Day 0 revenue/impressions for ROAS (70-80% of total) |
| Cost Tracking | network_cost for ROI analysis |
| Revenue Streams | ad_revenue + subscrevnt_revenue = total_revenue |
| Data Quality | dbt tests for unique, not_null, relationships |
| Data Lineage | UUID tracking from raw to staging |
| Performance | Incremental materialization |
| Custom Logic | calculate_ctr() macro, d0_revenue_pct |

---

## Data Volume

| Table | Daily Volume | 90-Day Projection |
|-------|--------------|-------------------|
| ADMOB_DAILY | ~1,500 rows | ~135K rows |
| ADJUST_DAILY | ~4,000 rows | ~360K rows |
| fct_app_daily_performance | ~4,000 rows | ~360K rows |

**Total Snowflake:** ~5.7M rows/year (manageable)
