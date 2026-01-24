{{ config(materialized='table') }}

WITH date_spine AS (
    SELECT DISTINCT
        date
    FROM {{ ref('int_app_daily_metrics') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['date']) }} AS date_key,
    date,
    YEAR(date) AS year,
    MONTH(date) AS month,
    DAY(date) AS day,
    DAYOFWEEK(date) AS day_of_week,
    DAYNAME(date) AS day_name
FROM date_spine
-- demo run Sat Jan 24 11:04:00 +07 2026
