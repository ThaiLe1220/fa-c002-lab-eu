{{ config(materialized='view') }}

SELECT
    RAW_RECORD_ID AS raw_record_id,
    BATCH_ID AS batch_id,
    LOADED_AT AS loaded_at,
    TO_DATE(DATE, 'YYYYMMDD') AS date,
    APP_STORE_ID AS app_store_id,
    APP_NAME AS app_name,
    COUNTRY_CODE AS country_code,
    UPPER(PLATFORM) AS platform,

    -- Revenue metrics (source of truth)
    CAST(ESTIMATED_EARNINGS AS DECIMAL(18,6)) / 1000000 AS estimated_earnings,
    CAST(AD_IMPRESSIONS AS INTEGER) AS ad_impressions,
    CAST(AD_CLICKS AS INTEGER) AS ad_clicks,
    CAST(AD_REQUESTS AS INTEGER) AS ad_requests,
    CAST(MATCHED_REQUESTS AS INTEGER) AS matched_requests,
    CAST(OBSERVED_ECPM AS DECIMAL(18,6)) / 1000000 AS observed_ecpm

FROM {{ source('raw_capstone', 'admob_daily') }}
