{{ config(materialized='view') }}

SELECT
    RAW_RECORD_ID AS raw_record_id,
    BATCH_ID AS batch_id,
    LOADED_AT AS loaded_at,
    TO_DATE(DATE, 'YYYYMMDD') AS date,
    APP_STORE_ID AS app_store_id,
    COUNTRY_CODE AS country_code,
    PLATFORM AS platform,
    CAST(AD_REQUESTS AS INTEGER) AS ad_requests,
    CAST(AD_CLICKS AS INTEGER) AS ad_clicks,
    CAST(ESTIMATED_EARNINGS AS DECIMAL(18,2)) AS estimated_earnings,
    CAST(AD_IMPRESSIONS AS INTEGER) AS ad_impressions,
    CAST(MATCHED_REQUESTS AS INTEGER) AS matched_requests
FROM {{ source('raw_midtest', 'admob_daily_midtest') }}
