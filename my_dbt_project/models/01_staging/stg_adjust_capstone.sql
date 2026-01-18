{{ config(materialized='view') }}

SELECT
    RAW_RECORD_ID AS raw_record_id,
    BATCH_ID AS batch_id,
    LOADED_AT AS loaded_at,
    TO_DATE(DAY, 'YYYY-MM-DD') AS date,
    STORE_ID AS app_store_id,
    APP AS app_name,
    COUNTRY_CODE AS country_code,
    UPPER(OS_NAME) AS platform,

    -- User acquisition metrics
    CAST(INSTALLS AS INTEGER) AS installs,
    CAST(CLICKS AS INTEGER) AS clicks,
    CAST(DAUS AS INTEGER) AS daus,

    -- Adjust revenue (for reconciliation, not source of truth)
    CAST(AD_REVENUE AS DECIMAL(18,6)) AS ad_revenue_adjust,
    CAST(AD_IMPRESSIONS AS INTEGER) AS ad_impressions_adjust,

    -- D0 metrics (critical for ROAS)
    CAST(AD_REVENUE_TOTAL_D0 AS DECIMAL(18,6)) AS ad_revenue_d0,
    CAST(AD_IMPRESSIONS_TOTAL_D0 AS INTEGER) AS ad_impressions_d0,

    -- Cost metrics
    CAST(NETWORK_COST AS DECIMAL(18,6)) AS network_cost,
    CAST(PAID_IMPRESSIONS AS INTEGER) AS paid_impressions,

    -- IAP revenue
    CAST(SUBSCREVNT_REVENUE AS DECIMAL(18,6)) AS subscrevnt_revenue

FROM {{ source('raw_capstone', 'adjust_daily') }}
