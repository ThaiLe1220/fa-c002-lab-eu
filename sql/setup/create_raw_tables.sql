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
-- Grain: (date, app_store_id, country_code, platform) - matches Adjust grain
-- Volume: ~3,000 rows/day (splits by iOS/Android)
-- Load Pattern: Daily batch loads
-- ============================================================================

CREATE OR REPLACE TABLE RAW.ADMOB_DAILY (
    -- API columns (matches Adjust grain)
    DATE VARCHAR(50) NOT NULL,
    APP_NAME VARCHAR(200) NOT NULL,
    APP_STORE_ID VARCHAR(100) NOT NULL,
    COUNTRY_CODE VARCHAR(100) NOT NULL,
    PLATFORM VARCHAR(20) NOT NULL,
    ESTIMATED_EARNINGS VARCHAR(50),  -- Raw microsValue as string
    AD_IMPRESSIONS VARCHAR(50),
    AD_CLICKS VARCHAR(50),
    AD_REQUESTS VARCHAR(50),
    MATCHED_REQUESTS VARCHAR(50),
    OBSERVED_ECPM VARCHAR(50),  -- Raw microsValue as string

    -- Metadata (added by pipeline)
    LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    PRIMARY KEY (DATE, APP_STORE_ID, COUNTRY_CODE, PLATFORM)
);

COMMENT ON TABLE RAW.ADMOB_DAILY IS 'AdMob daily RAW data - aggregated at (date, app, country) grain';

-- ============================================================================
-- TABLE 2: ADJUST_DAILY (Incremental Pipeline)
-- ============================================================================
-- Source: Adjust API (daily granularity)
-- Grain: (day, store_id, country, os_name)
-- Volume: ~3,706 rows/day (21x reduction from hourly)
-- Load Pattern: Daily loads with daily grain
-- ============================================================================

CREATE OR REPLACE TABLE RAW.ADJUST_DAILY (
    -- API columns (daily grain)
    APP VARCHAR(200) NOT NULL,
    STORE_ID VARCHAR(100) NOT NULL,
    DAY DATE NOT NULL,
    COUNTRY_CODE VARCHAR(10) NOT NULL,
    COUNTRY VARCHAR(100) NOT NULL,
    OS_NAME VARCHAR(20) NOT NULL,
    INSTALLS INTEGER,
    CLICKS INTEGER,
    DAUS DECIMAL(10, 2),
    AD_REVENUE DECIMAL(10, 4),
    AD_IMPRESSIONS INTEGER,
    NETWORK_COST DECIMAL(10, 4),

    -- Metadata (added by pipeline)
    LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    PRIMARY KEY (DAY, STORE_ID, COUNTRY_CODE, OS_NAME)
);

COMMENT ON TABLE RAW.ADJUST_DAILY IS 'Adjust daily RAW data - aggregated at (day, store_id, country, os_name) grain';

-- ============================================================================
-- Verify Tables
-- ============================================================================

SELECT
    table_name,
    row_count,
    comment
FROM DB_T34.INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'RAW'
  AND table_name IN ('ADMOB_DAILY', 'ADJUST_DAILY')
ORDER BY table_name;
