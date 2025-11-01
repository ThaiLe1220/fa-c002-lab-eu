{{ config(materialized='view') }}

SELECT
    RAW_RECORD_ID AS raw_record_id,
    BATCH_ID AS batch_id,
    LOADED_AT AS loaded_at,
    TO_DATE(DAY, 'YYYY-MM-DD') AS date,
    STORE_ID AS app_store_id,
    COUNTRY_CODE AS country_code,
    OS_NAME AS platform,
    CAST(INSTALLS AS INTEGER) AS installs,
    CAST(CLICKS AS INTEGER) AS clicks,
    CAST(DAUS AS INTEGER) AS daus,
    CAST(AD_REVENUE AS DECIMAL(18,2)) AS ad_revenue_adjust,
    CAST(AD_IMPRESSIONS AS INTEGER) AS ad_impressions_adjust
FROM {{ source('raw_midtest', 'adjust_daily_midtest') }}
