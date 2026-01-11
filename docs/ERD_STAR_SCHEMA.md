# Data Pipeline & Star Schema Architecture

**Schema:** `DB_T34.RAW_CAPSTONE` → `DB_T34.ANALYTICS`
**Updated:** January 2026

---

## Complete Data Flow

```mermaid
graph TB
    subgraph APIs["DATA SOURCES"]
        AdMob[Google AdMob API<br/>Impressions, Clicks, Revenue]
        Adjust[Adjust API<br/>Installs, DAUs, D0 Metrics, Costs]
    end

    subgraph Python["PYTHON COLLECTION"]
        AdMobCollect[collect_admob_capstone.py<br/>Daily batch collection]
        AdjustCollect[collect_adjust_capstone.py<br/>Daily batch collection]
    end

    subgraph Raw["SNOWFLAKE RAW LAYER - DB_T34.RAW_CAPSTONE"]
        AdMobRaw[(ADMOB_DAILY<br/>RAW_RECORD_ID UUID<br/>LOADED_AT timestamp)]
        AdjustRaw[(ADJUST_DAILY<br/>RAW_RECORD_ID UUID<br/>D0 metrics, costs)]
    end

    subgraph Staging["DBT LAYER 1: STAGING - DB_T34.ANALYTICS"]
        AdMobStg[stg_admob VIEW<br/>Clean, Standardize Types<br/>Tests: unique, not_null]
        AdjustStg[stg_adjust VIEW<br/>Clean, Standardize Types<br/>D0 metrics pass-through]
    end

    subgraph Intermediate["DBT LAYER 2: INTERMEDIATE - DB_T34.ANALYTICS"]
        IntMetrics[int_app_daily_metrics<br/>INCREMENTAL TABLE<br/>FULL OUTER JOIN<br/>D0 + Cost metrics]
    end

    subgraph Mart["DBT LAYER 3: STAR SCHEMA - DB_T34.ANALYTICS"]
        DimApps[dim_apps TABLE<br/>App Dimension]
        DimDates[dim_dates TABLE<br/>Date Dimension]
        Fact[fct_app_daily_performance TABLE<br/>Fact Table - All Metrics<br/>D0, ROAS, Revenue]
    end

    AdMob --> AdMobCollect
    Adjust --> AdjustCollect

    AdMobCollect --> AdMobRaw
    AdjustCollect --> AdjustRaw

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
        decimal ad_revenue_d0 "D0 revenue - critical"
        int ad_impressions_d0 "D0 impressions"
        decimal d0_revenue_pct "Calculated: d0/total"
        decimal network_cost "Marketing spend"
        int paid_impressions "Paid UA impressions"
        decimal subscrevnt_revenue "Subscription revenue"
        decimal total_revenue "Calculated: ad + subs"
        decimal revenue_per_install "Calculated"
        decimal revenue_per_click "Calculated"
        timestamp dbt_updated_at
    }
```

---

## Schema Evolution by Layer

### RAW LAYER: `DB_T34.RAW_CAPSTONE`

```mermaid
erDiagram
    ADMOB_DAILY {
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

    ADJUST_DAILY {
        varchar RAW_RECORD_ID PK "UUID lineage"
        varchar BATCH_ID
        date DAY
        varchar STORE_ID
        varchar COUNTRY_CODE
        varchar OS_NAME
        number INSTALLS
        number CLICKS
        number DAUS
        number AD_REVENUE
        number AD_IMPRESSIONS
        number AD_REVENUE_TOTAL_D0 "D0 revenue"
        number AD_IMPRESSIONS_TOTAL_D0 "D0 impressions"
        number NETWORK_COST "Marketing spend"
        number PAID_IMPRESSIONS "Paid UA impressions"
        number SUBSCREVNT_REVENUE "Subscription revenue"
        timestamp LOADED_AT "Fresh data proof"
    }
```

---

### STAGING LAYER: `DB_T34.ANALYTICS` (Views - Clean & Standardize)

```mermaid
erDiagram
    stg_admob {
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

    stg_adjust {
        varchar raw_record_id PK "UUID preserved"
        date date "Standardized"
        varchar app_store_id "From STORE_ID"
        varchar country_code
        varchar platform "From OS_NAME"
        integer installs "Type cast"
        integer clicks "Type cast"
        integer daus "Type cast"
        decimal ad_revenue "Type cast"
        integer ad_impressions "Type cast"
        decimal ad_revenue_d0 "From AD_REVENUE_TOTAL_D0"
        integer ad_impressions_d0 "From AD_IMPRESSIONS_TOTAL_D0"
        decimal network_cost "Type cast"
        integer paid_impressions "Type cast"
        decimal subscrevnt_revenue "Type cast"
        timestamp loaded_at
    }
```

**Transformations**: Date parsing, column renaming, type casting
**Tests**: unique(raw_record_id), not_null(raw_record_id, date, app_store_id)

---

### INTERMEDIATE LAYER: `DB_T34.ANALYTICS` (Incremental Table - Join & Calculate)

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
        decimal ad_revenue_d0 "From Adjust"
        integer ad_impressions_d0 "From Adjust"
        decimal network_cost "From Adjust"
        integer paid_impressions "From Adjust"
        decimal subscrevnt_revenue "From Adjust"
        decimal revenue_per_install "Calculated"
        decimal revenue_per_click "Calculated"
        timestamp dbt_updated_at
    }
```

**Join**: FULL OUTER JOIN stg_admob ⟷ stg_adjust ON (app_store_id, date, country_code, platform)
**Incremental**: WHERE date > MAX(date)
**Unique Key**: [app_store_id, date, country_code, platform]

---

### MART LAYER: `DB_T34.ANALYTICS` (Star Schema - Analytics Ready)

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
        decimal ad_revenue_d0 "D0 revenue"
        int ad_impressions_d0 "D0 impressions"
        decimal d0_revenue_pct "ad_revenue_d0 / ad_revenue"
        decimal network_cost "Marketing spend"
        int paid_impressions "Paid UA"
        decimal subscrevnt_revenue "Subscription"
        decimal total_revenue "ad_revenue + subscrevnt_revenue"
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

## Transformation Layers Summary

| Layer | Models | Materialization | Purpose |
|-------|--------|-----------------|---------|
| **Staging** | stg_admob, stg_adjust | VIEW | Clean, standardize types, preserve UUID |
| **Intermediate** | int_app_daily_metrics | INCREMENTAL TABLE | FULL OUTER JOIN, combine sources |
| **Mart** | dim_apps, dim_dates, fct_app_daily_performance | TABLE | Star schema for analytics |

---

## Key Features

- **D0 Metrics**: Day 0 revenue/impressions for ROAS calculation (70-80% of revenue from install day)
- **Cost Tracking**: network_cost for ROI analysis
- **Revenue Streams**: ad_revenue + subscrevnt_revenue = total_revenue
- **Data Quality**: Tests for unique, not_null, relationships
- **Data Lineage**: UUID tracking from raw → staging
- **Performance**: Incremental materialization for efficiency
- **Custom Logic**: calculate_ctr() macro, d0_revenue_pct calculation
- **Star Schema**: Optimized for Snowflake analytics and AI Agent queries

---

## Key Metrics

| Metric | Formula | Business Use |
|--------|---------|--------------|
| **ROAS** | ad_revenue / network_cost | Return on ad spend |
| **D0 Revenue %** | ad_revenue_d0 / ad_revenue | Same-day payback |
| **eCPM** | (ad_revenue / ad_impressions) * 1000 | Ad efficiency |
| **CPI** | network_cost / installs | Cost per install |
| **ARPDAU** | ad_revenue / daus | Revenue per active user |
| **Total Revenue** | ad_revenue + subscrevnt_revenue | Full revenue picture |
