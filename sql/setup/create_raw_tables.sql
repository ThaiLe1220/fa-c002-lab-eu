-- ============================================================================
-- RAW Schema Table Definitions for Mobile Analytics Pipeline
-- ============================================================================
-- Purpose: Create tables to receive data from AdMob and Adjust APIs
-- Target: Snowflake DB_T34.RAW schema
-- Pattern: Following M01W03 lab structure for batch + incremental pipelines
-- ============================================================================

USE DATABASE DB_T34;
USE SCHEMA RAW;

-- ============================================================================
-- TABLE 1: ADMOB_DAILY (Batch Pipeline)
-- ============================================================================
-- Source: AdMob API (daily granularity)
-- Volume: ~13,500 rows/day
-- Load Pattern: Daily batch loads
-- Demo: 7 days = 94,000 rows
-- ============================================================================

CREATE TABLE IF NOT EXISTS RAW.ADMOB_DAILY (
    -- Primary Key Components
    date DATE NOT NULL,
    app_id VARCHAR(100) NOT NULL,
    country_code VARCHAR(2) NOT NULL,
    platform VARCHAR(20) NOT NULL,
    ad_format VARCHAR(50) NOT NULL,
    ad_unit_id VARCHAR(100) NOT NULL,

    -- Ad Performance Metrics
    ad_impressions INTEGER,
    ad_clicks INTEGER,
    ad_requests INTEGER,
    matched_requests INTEGER,

    -- Revenue Metrics
    estimated_earnings DECIMAL(10, 4),
    observed_ecpm DECIMAL(10, 4),

    -- Metadata
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    batch_id VARCHAR(50),

    -- Primary Key
    PRIMARY KEY (date, app_id, country_code, platform, ad_format, ad_unit_id)
);

COMMENT ON TABLE RAW.ADMOB_DAILY IS 'AdMob daily ad performance data - Batch pipeline (~13.5K rows/day)';

-- ============================================================================
-- TABLE 2: ADJUST_HOURLY (Incremental Pipeline)
-- ============================================================================
-- Source: Adjust API (hourly granularity)
-- Volume: ~936 rows/day (~39 rows/hour)
-- Load Pattern: Hourly incremental loads
-- Demo: Last hour = ~39 rows
-- ============================================================================

CREATE TABLE IF NOT EXISTS RAW.ADJUST_HOURLY (
    -- Primary Key Components
    hour_timestamp TIMESTAMP_NTZ NOT NULL,
    app_name VARCHAR(200) NOT NULL,
    store_id VARCHAR(100) NOT NULL,
    country_code VARCHAR(2) NOT NULL,
    os_name VARCHAR(20) NOT NULL,

    -- User Acquisition Metrics
    installs INTEGER,
    clicks INTEGER,

    -- User Engagement Metrics
    daus DECIMAL(10, 2),

    -- Ad Revenue Metrics (Day 0)
    ad_revenue DECIMAL(10, 4),
    ad_impressions INTEGER,
    ad_revenue_total_d0 DECIMAL(10, 4),
    ad_impressions_total_d0 INTEGER,

    -- Marketing Cost Metrics
    network_cost DECIMAL(10, 4),
    network_cost_diff DECIMAL(10, 4),

    -- Metadata
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    -- Primary Key
    PRIMARY KEY (hour_timestamp, app_name, store_id, country_code, os_name)
);

COMMENT ON TABLE RAW.ADJUST_HOURLY IS 'Adjust hourly performance data - Incremental pipeline (~39 rows/hour)';

-- ============================================================================
-- TABLE 3: ADJUST_COHORTS (Daily Cohort Retention)
-- ============================================================================
-- Source: Adjust API (daily cohort data)
-- Volume: ~2,200 rows/day
-- Load Pattern: Daily batch with cohort retention metrics
-- ============================================================================

CREATE TABLE IF NOT EXISTS RAW.ADJUST_COHORTS (
    -- Primary Key Components
    cohort_date DATE NOT NULL,
    app_name VARCHAR(200) NOT NULL,
    store_id VARCHAR(100) NOT NULL,
    country_code VARCHAR(2) NOT NULL,

    -- Cohort Size
    cohort_size_d0 INTEGER,

    -- Retention Metrics
    cohort_size_d1 INTEGER,
    cohort_size_d7 INTEGER,
    cohort_size_d30 INTEGER,

    -- Calculated Retention Rates (derived in dbt)
    retention_d1_pct DECIMAL(5, 4),
    retention_d7_pct DECIMAL(5, 4),
    retention_d30_pct DECIMAL(5, 4),

    -- Metadata
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    -- Primary Key
    PRIMARY KEY (cohort_date, app_name, store_id, country_code)
);

COMMENT ON TABLE RAW.ADJUST_COHORTS IS 'Adjust daily cohort retention data - D0/D1/D7/D30 retention';

-- ============================================================================
-- Verify Tables Created
-- ============================================================================

SELECT
    table_name,
    table_type,
    row_count,
    bytes,
    comment
FROM DB_T34.INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'RAW'
  AND table_name IN ('ADMOB_DAILY', 'ADJUST_HOURLY', 'ADJUST_COHORTS')
ORDER BY table_name;
