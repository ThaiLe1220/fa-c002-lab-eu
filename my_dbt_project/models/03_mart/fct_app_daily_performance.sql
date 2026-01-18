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
    {{ dbt_utils.generate_surrogate_key(['m.app_store_id', 'm.date', 'm.country_code', 'm.platform']) }} AS performance_key,
    a.app_key,
    d.date_key,
    m.country_code,
    m.platform,

    -- AdMob metrics (source of truth for revenue)
    m.ad_revenue,
    m.ad_impressions,
    m.ad_clicks,
    m.ad_requests,
    m.matched_requests,
    m.observed_ecpm,
    {{ calculate_ctr('m.ad_clicks', 'm.ad_impressions') }} AS ad_ctr,

    -- Adjust metrics (for reconciliation)
    m.ad_revenue_adjust,
    m.ad_impressions_adjust,

    -- User acquisition metrics
    m.installs,
    m.clicks,
    m.daus,

    -- Cohort metrics (D0, D1, D3, D7 for LTV curve)
    m.ad_revenue_d0,
    m.ad_impressions_d0,
    m.ad_revenue_d1,
    m.ad_impressions_d1,
    m.ad_revenue_d3,
    m.ad_impressions_d3,
    m.ad_revenue_d7,
    m.ad_impressions_d7,

    -- Cost metrics
    m.network_cost,
    m.paid_impressions,

    -- IAP revenue
    m.subscrevnt_revenue,

    m.dbt_updated_at
FROM metrics m
LEFT JOIN apps a ON m.app_store_id = a.app_store_id
LEFT JOIN dates d ON m.date = d.date
