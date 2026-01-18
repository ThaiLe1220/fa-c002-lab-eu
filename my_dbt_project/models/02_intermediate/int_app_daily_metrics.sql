{{
    config(
        materialized='incremental',
        unique_key=['app_store_id', 'date', 'country_code', 'platform']
    )
}}

WITH admob AS (
    SELECT * FROM {{ ref('stg_admob_capstone') }}
),

adjust AS (
    SELECT * FROM {{ ref('stg_adjust_capstone') }}
),

joined AS (
    SELECT
        COALESCE(adm.app_store_id, adj.app_store_id) AS app_store_id,
        COALESCE(adm.date, adj.date) AS date,
        COALESCE(UPPER(adm.country_code), UPPER(adj.country_code)) AS country_code,
        COALESCE(adm.platform, adj.platform) AS platform,

        -- AdMob metrics (source of truth for revenue)
        COALESCE(adm.estimated_earnings, 0) AS ad_revenue,
        COALESCE(adm.ad_impressions, 0) AS ad_impressions,
        COALESCE(adm.ad_clicks, 0) AS ad_clicks,
        COALESCE(adm.ad_requests, 0) AS ad_requests,
        COALESCE(adm.matched_requests, 0) AS matched_requests,
        COALESCE(adm.observed_ecpm, 0) AS observed_ecpm,

        -- Adjust metrics (for reconciliation)
        COALESCE(adj.ad_revenue_adjust, 0) AS ad_revenue_adjust,
        COALESCE(adj.ad_impressions_adjust, 0) AS ad_impressions_adjust,

        -- User acquisition metrics
        COALESCE(adj.installs, 0) AS installs,
        COALESCE(adj.clicks, 0) AS clicks,
        COALESCE(adj.daus, 0) AS daus,

        -- D0 metrics (critical for ROAS calculation)
        COALESCE(adj.ad_revenue_d0, 0) AS ad_revenue_d0,
        COALESCE(adj.ad_impressions_d0, 0) AS ad_impressions_d0,

        -- Cost metrics
        COALESCE(adj.network_cost, 0) AS network_cost,
        COALESCE(adj.paid_impressions, 0) AS paid_impressions,

        -- IAP revenue
        COALESCE(adj.subscrevnt_revenue, 0) AS subscrevnt_revenue,

        CURRENT_TIMESTAMP() AS dbt_updated_at

    FROM admob adm
    FULL OUTER JOIN adjust adj
        ON adm.app_store_id = adj.app_store_id
        AND adm.date = adj.date
        AND UPPER(adm.country_code) = UPPER(adj.country_code)
        AND adm.platform = adj.platform
)

SELECT * FROM joined

{% if is_incremental() %}
WHERE date > (SELECT MAX(date) FROM {{ this }})
{% endif %}
