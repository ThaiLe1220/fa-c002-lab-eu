# Data Pipeline & Star Schema Architecture

## Complete Data Flow

```mermaid
graph TB
    subgraph APIs["DATA SOURCES"]
        AdMob[Google AdMob API<br/>Impressions, Clicks, Revenue]
        Adjust[Adjust API<br/>Installs, DAUs, Sessions]
    end

    subgraph Python["PYTHON COLLECTION - BOTH HAVE BATCH & REALTIME"]
        AdMobBatch[collect_admob_midtest.py --batch<br/>Same timestamp for all rows]
        AdMobRT[collect_admob_midtest.py --realtime<br/>Staggered timestamps, multithreaded]
        AdjustBatch[collect_adjust_midtest.py --batch<br/>Same timestamp for all rows]
        AdjustRT[collect_adjust_midtest.py --realtime<br/>Staggered timestamps, multithreaded]
    end

    subgraph Raw["SNOWFLAKE RAW LAYER - DB_T34.RAW_MIDTEST"]
        AdMobRaw[(ADMOB_DAILY_MIDTEST<br/>RAW_RECORD_ID UUID<br/>LOADED_AT timestamp)]
        AdjustRaw[(ADJUST_DAILY_MIDTEST<br/>RAW_RECORD_ID UUID<br/>LOADED_AT timestamp)]
    end

    subgraph Staging["DBT LAYER 1: STAGING - DB_T34.PUBLIC"]
        AdMobStg[stg_admob_midtest VIEW<br/>Clean, Standardize Types<br/>Tests: unique, not_null]
        AdjustStg[stg_adjust_midtest VIEW<br/>Clean, Standardize Types<br/>Tests: unique, not_null]
    end

    subgraph Intermediate["DBT LAYER 2: INTERMEDIATE - DB_T34.PUBLIC"]
        IntMetrics[int_app_daily_metrics<br/>INCREMENTAL TABLE<br/>FULL OUTER JOIN<br/>Calculate Metrics]
    end

    subgraph Mart["DBT LAYER 3: STAR SCHEMA - DB_T34.PUBLIC"]
        DimApps[dim_apps TABLE<br/>App Dimension]
        DimDates[dim_dates TABLE<br/>Date Dimension]
        Fact[fct_app_daily_performance TABLE<br/>Fact Table - All Metrics<br/>Custom Macro: calculate_ctr]
    end

    AdMob --> AdMobBatch
    AdMob --> AdMobRT
    Adjust --> AdjustBatch
    Adjust --> AdjustRT

    AdMobBatch --> AdMobRaw
    AdMobRT --> AdMobRaw
    AdjustBatch --> AdjustRaw
    AdjustRT --> AdjustRaw

    AdMobRaw --> AdMobStg
    AdjustRaw --> AdjustStg

    AdMobStg --> IntMetrics
    AdjustStg --> IntMetrics

    IntMetrics --> DimApps
    IntMetrics --> DimDates
    IntMetrics --> Fact

    DimApps --> Fact
    DimDates --> Fact
```

---

## Star Schema ERD

```mermaid
erDiagram
    dim_apps ||--o{ fct_app_daily_performance : "has many"
    dim_dates ||--o{ fct_app_daily_performance : "has many"

    dim_apps {
        string app_key PK "MD5 surrogate key"
        string app_store_id "Natural key"
        string app_name "Display name"
    }

    dim_dates {
        string date_key PK "MD5 surrogate key"
        date date "Natural key"
        int year
        int month
        int day
        int day_of_week
        string day_name
    }

    fct_app_daily_performance {
        string performance_key PK "MD5 surrogate key"
        string app_key FK "→ dim_apps"
        string date_key FK "→ dim_dates"
        string country_code "Degenerate dim"
        string platform "Degenerate dim"
        decimal ad_revenue "From AdMob"
        int ad_impressions "From AdMob"
        int ad_clicks "From AdMob"
        decimal ad_ctr "Custom macro"
        int installs "From Adjust"
        int clicks "From Adjust"
        int daus "From Adjust"
        decimal revenue_per_install "Calculated"
        decimal revenue_per_click "Calculated"
        timestamp dbt_updated_at
    }
```

---

## Schema Evolution by Layer

### RAW LAYER: `DB_T34.RAW_MIDTEST`

```mermaid
erDiagram
    ADMOB_DAILY_MIDTEST {
        varchar RAW_RECORD_ID PK "UUID lineage"
        varchar BATCH_ID
        varchar DATE "YYYYMMDD string"
        varchar APP_STORE_ID
        varchar COUNTRY_CODE
        varchar PLATFORM
        number ESTIMATED_EARNINGS
        number AD_IMPRESSIONS
        number AD_CLICKS
        timestamp LOADED_AT "Fresh data proof"
    }

    ADJUST_DAILY_MIDTEST {
        varchar RAW_RECORD_ID PK "UUID lineage"
        varchar BATCH_ID
        date DAY
        varchar STORE_ID
        varchar COUNTRY_CODE
        varchar OS_NAME
        number INSTALLS
        number CLICKS
        number DAUS
        timestamp LOADED_AT "Fresh data proof"
    }
```

---

### STAGING LAYER: `DB_T34.PUBLIC` (Views - Clean & Standardize)

```mermaid
erDiagram
    stg_admob_midtest {
        varchar raw_record_id PK "UUID preserved"
        date date "TO_DATE converted"
        varchar app_store_id
        varchar country_code
        varchar platform
        integer ad_impressions "Type cast"
        integer ad_clicks "Type cast"
        decimal estimated_earnings "Type cast"
        timestamp loaded_at
    }

    stg_adjust_midtest {
        varchar raw_record_id PK "UUID preserved"
        date date "Standardized"
        varchar app_store_id "From STORE_ID"
        varchar country_code
        varchar platform "From OS_NAME"
        integer installs "Type cast"
        integer clicks "Type cast"
        integer daus "Type cast"
        timestamp loaded_at
    }
```

**Transformations**: Date parsing, column renaming, type casting
**Tests**: unique(raw_record_id), not_null(raw_record_id, date, app_store_id)

---

### INTERMEDIATE LAYER: `DB_T34.PUBLIC` (Incremental Table - Join & Calculate)

```mermaid
erDiagram
    int_app_daily_metrics {
        varchar app_store_id "COALESCE both"
        date date "COALESCE both"
        varchar country_code "COALESCE both"
        varchar platform "COALESCE both"
        decimal ad_revenue "From AdMob"
        integer ad_impressions "From AdMob"
        integer ad_clicks "From AdMob"
        integer installs "From Adjust"
        integer clicks "From Adjust"
        integer daus "From Adjust"
        decimal revenue_per_install "Calculated"
        decimal revenue_per_click "Calculated"
        timestamp dbt_updated_at
    }
```

**Join**: FULL OUTER JOIN stg_admob ⟷ stg_adjust ON (app_store_id, date, country_code)
**Incremental**: WHERE date > MAX(date)
**Unique Key**: [app_store_id, date, country_code]

---

### MART LAYER: `DB_T34.PUBLIC` (Star Schema - Analytics Ready)

```mermaid
erDiagram
    dim_apps {
        string app_key PK "MD5 surrogate"
        string app_store_id
        string app_name
    }

    dim_dates {
        string date_key PK "MD5 surrogate"
        date date
        int year
        int month
        int day
        int day_of_week
        string day_name
    }

    fct_app_daily_performance {
        string performance_key PK "MD5 surrogate"
        string app_key FK
        string date_key FK
        string country_code "Degenerate"
        string platform "Degenerate"
        decimal ad_revenue
        int ad_impressions
        int ad_clicks
        decimal ad_ctr "Custom macro"
        int installs
        int clicks
        int daus
        decimal revenue_per_install
        decimal revenue_per_click
        timestamp dbt_updated_at
    }

    dim_apps ||--o{ fct_app_daily_performance : "has many"
    dim_dates ||--o{ fct_app_daily_performance : "has many"
```

**Grain**: One row per app per day per country per platform
**Surrogate Keys**: dbt_utils.generate_surrogate_key (MD5)
**Custom Macro**: calculate_ctr(clicks, impressions)
**Tests**: relationships(app_key → dim_apps), relationships(date_key → dim_dates)

---

## Transformation Layers

| Layer | Models | Materialization | Purpose |
|-------|--------|-----------------|---------|
| **Staging** | stg_admob_midtest<br/>stg_adjust_midtest | VIEW | Clean, standardize types, preserve UUID |
| **Intermediate** | int_app_daily_metrics | INCREMENTAL TABLE | FULL OUTER JOIN, calculate metrics |
| **Mart** | dim_apps<br/>dim_dates<br/>fct_app_daily_performance | TABLE | Star schema for analytics |

---

## Key Features

- **Data Collection**: Both AdMob & Adjust have --batch and --realtime modes
- **Data Quality**: 27 tests (unique, not_null, relationships)
- **Data Lineage**: UUID tracking from raw → staging
- **Performance**: Incremental materialization
- **Custom Logic**: calculate_ctr() macro
- **Star Schema**: Optimized for Snowflake analytics
