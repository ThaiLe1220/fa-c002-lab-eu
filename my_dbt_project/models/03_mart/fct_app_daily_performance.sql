{{ config(materialized='table') }}

WITH metrics AS (
    SELECT * FROM {{ ref('int_app_daily_metrics') }}
),

apps AS (
    SELECT * FROM {{ ref('dim_apps') }}
),

dates AS (
    SELECT * FROM {{ ref('dim_dates') }}
)

SELECT
    MD5(m.app_store_id || m.date::VARCHAR || m.country_code || m.platform) AS performance_key,
    a.app_key,
    d.date_key,
    m.country_code,
    m.platform,

    -- AdMob metrics
    m.ad_revenue,
    m.ad_impressions,
    m.ad_clicks,
    {{ calculate_ctr('m.ad_clicks', 'm.ad_impressions') }} AS ad_ctr,

    -- Adjust metrics
    m.installs,
    m.clicks,
    m.daus,

    -- Calculated metrics
    m.revenue_per_install,
    m.revenue_per_click,

    m.dbt_updated_at
FROM metrics m
LEFT JOIN apps a ON m.app_store_id = a.app_store_id
LEFT JOIN dates d ON m.date = d.date
