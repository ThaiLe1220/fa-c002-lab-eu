{{
    config(
        materialized='incremental',
        unique_key=['app_store_id', 'date', 'country_code']
    )
}}

WITH admob AS (
    SELECT * FROM {{ ref('stg_admob_midtest') }}
),

adjust AS (
    SELECT * FROM {{ ref('stg_adjust_midtest') }}
),

joined AS (
    SELECT
        COALESCE(adm.app_store_id, adj.app_store_id) AS app_store_id,
        COALESCE(adm.date, adj.date) AS date,
        COALESCE(adm.country_code, adj.country_code) AS country_code,
        COALESCE(adm.platform, adj.platform) AS platform,

        -- AdMob metrics
        COALESCE(adm.estimated_earnings, 0) AS ad_revenue,
        COALESCE(adm.ad_impressions, 0) AS ad_impressions,
        COALESCE(adm.ad_clicks, 0) AS ad_clicks,

        -- Adjust metrics
        COALESCE(adj.installs, 0) AS installs,
        COALESCE(adj.clicks, 0) AS clicks,
        COALESCE(adj.daus, 0) AS daus,

        -- Calculated metrics
        CASE
            WHEN COALESCE(adj.installs, 0) > 0
            THEN COALESCE(adm.estimated_earnings, 0) / adj.installs
            ELSE 0
        END AS revenue_per_install,

        CASE
            WHEN COALESCE(adj.clicks, 0) > 0
            THEN COALESCE(adm.estimated_earnings, 0) / adj.clicks
            ELSE 0
        END AS revenue_per_click,

        CURRENT_TIMESTAMP() AS dbt_updated_at
    FROM admob adm
    FULL OUTER JOIN adjust adj
        ON adm.app_store_id = adj.app_store_id
        AND adm.date = adj.date
        AND adm.country_code = adj.country_code
)

SELECT * FROM joined

{% if is_incremental() %}
WHERE date > (SELECT MAX(date) FROM {{ this }})
{% endif %}
