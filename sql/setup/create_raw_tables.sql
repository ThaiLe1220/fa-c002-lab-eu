-- ============================================================================
-- RAW Schema Tables - Pure RAW (exact API columns, no transformations)
-- ============================================================================
-- Purpose: Store exact API responses from AdMob and Adjust
-- Target: Snowflake DB_T34.RAW schema
-- Philosophy: RAW = untouched API data, transformations happen in dbt
-- ============================================================================

USE DATABASE DB_T34;
USE SCHEMA RAW;

-- ============================================================================
-- TABLE 1: ADMOB_DAILY (Batch Pipeline)
-- ============================================================================
-- Source: AdMob API (daily granularity)
-- Volume: ~13,500 rows/day
-- Load Pattern: Daily batch loads
-- ============================================================================

CREATE OR REPLACE TABLE RAW.ADMOB_DAILY (
    -- API columns (exact from AdMob API - raw values as strings)
    date VARCHAR(50) NOT NULL,
    app_id VARCHAR(200) NOT NULL,
    country_code VARCHAR(100) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    ad_format VARCHAR(50) NOT NULL,
    ad_unit_id VARCHAR(200) NOT NULL,
    ad_impressions VARCHAR(50),
    ad_clicks VARCHAR(50),
    ad_requests VARCHAR(50),
    matched_requests VARCHAR(50),
    estimated_earnings VARCHAR(50),  -- Raw microsValue as string
    observed_ecpm VARCHAR(50),        -- Raw microsValue as string

    -- Metadata (added by pipeline)
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    batch_id VARCHAR(50),

    PRIMARY KEY (date, app_id, country_code, platform, ad_format, ad_unit_id)
);

COMMENT ON TABLE RAW.ADMOB_DAILY IS 'AdMob daily RAW data - exact API response (flattened)';

-- ============================================================================
-- TABLE 2: ADJUST_HOURLY (Incremental Pipeline)
-- ============================================================================
-- Source: Adjust API (hourly granularity)
-- Volume: ~127K rows/day
-- Load Pattern: Daily loads with hourly grain
-- ============================================================================

CREATE OR REPLACE TABLE RAW.ADJUST_HOURLY (
    -- API columns (exact from Adjust CSV API)
    app VARCHAR(200) NOT NULL,
    store_id VARCHAR(100) NOT NULL,
    day DATE NOT NULL,
    hour TIMESTAMP_NTZ NOT NULL,
    country VARCHAR(100) NOT NULL,
    os_name VARCHAR(20) NOT NULL,
    installs INTEGER,
    clicks INTEGER,
    daus DECIMAL(10, 2),
    ad_revenue DECIMAL(10, 4),
    ad_impressions INTEGER,
    ad_revenue_total_d0 DECIMAL(10, 4),
    ad_impressions_total_d0 INTEGER,
    network_cost DECIMAL(10, 4),
    network_cost_diff DECIMAL(10, 4),

    -- Metadata (added by pipeline)
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    PRIMARY KEY (hour, app, store_id, country, os_name)
);

COMMENT ON TABLE RAW.ADJUST_HOURLY IS 'Adjust hourly RAW data - exact API response';

-- ============================================================================
-- TABLE 3: ADJUST_COHORTS (Optional - for future use)
-- ============================================================================
-- Source: Adjust API (daily cohort data)
-- Volume: TBD
-- Status: Not implemented yet (bonus feature)
-- ============================================================================

CREATE OR REPLACE TABLE RAW.ADJUST_COHORTS (
    cohort_date DATE NOT NULL,
    app_name VARCHAR(200) NOT NULL,
    store_id VARCHAR(100) NOT NULL,
    country_code VARCHAR(100) NOT NULL,
    cohort_size_d0 INTEGER,
    cohort_size_d1 INTEGER,
    cohort_size_d7 INTEGER,
    cohort_size_d30 INTEGER,
    retention_d1_pct DECIMAL(5, 4),
    retention_d7_pct DECIMAL(5, 4),
    retention_d30_pct DECIMAL(5, 4),
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    PRIMARY KEY (cohort_date, app_name, store_id, country_code)
);

COMMENT ON TABLE RAW.ADJUST_COHORTS IS 'Adjust cohort retention - for future LTV analysis (optional)';

-- ============================================================================
-- Verify Tables
-- ============================================================================

SELECT
    table_name,
    row_count,
    comment
FROM DB_T34.INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'RAW'
  AND table_name IN ('ADMOB_DAILY', 'ADJUST_HOURLY', 'ADJUST_COHORTS')
ORDER BY table_name;
