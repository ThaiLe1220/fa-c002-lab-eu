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

## Table Schemas

### Fact Table: `fct_app_daily_performance`

**Grain**: One row per app per day per country per platform

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| performance_key | STRING | Generated | PK - Surrogate key (MD5) |
| app_key | STRING | dim_apps | FK to apps dimension |
| date_key | STRING | dim_dates | FK to dates dimension |
| country_code | STRING | Both | Degenerate dimension |
| platform | STRING | Both | iOS/Android |
| ad_revenue | DECIMAL(18,2) | AdMob | Revenue from ads |
| ad_impressions | INTEGER | AdMob | Ad views |
| ad_clicks | INTEGER | AdMob | Ad clicks |
| ad_ctr | DECIMAL(18,2) | Calculated | CTR via calculate_ctr() macro |
| installs | INTEGER | Adjust | App installs |
| clicks | INTEGER | Adjust | User clicks |
| daus | INTEGER | Adjust | Daily active users |
| revenue_per_install | DECIMAL(18,2) | Calculated | ad_revenue / installs |
| revenue_per_click | DECIMAL(18,2) | Calculated | ad_revenue / clicks |
| dbt_updated_at | TIMESTAMP | System | Last transformation time |

### Dimension: `dim_apps`

| Column | Type | Description |
|--------|------|-------------|
| app_key | STRING | PK - MD5(app_store_id) |
| app_store_id | STRING | video.ai.videogenerator |
| app_name | STRING | Text to Video FLIX |

### Dimension: `dim_dates`

| Column | Type | Description |
|--------|------|-------------|
| date_key | STRING | PK - MD5(date) |
| date | DATE | 2024-10-22 |
| year | INTEGER | 2024 |
| month | INTEGER | 10 |
| day | INTEGER | 22 |
| day_of_week | INTEGER | 2 (Tuesday) |
| day_name | STRING | Tuesday |

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
