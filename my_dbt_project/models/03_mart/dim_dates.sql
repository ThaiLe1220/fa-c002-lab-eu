{{ config(materialized='table') }}

WITH date_spine AS (
    SELECT DISTINCT
        date
    FROM {{ ref('int_app_daily_metrics') }}
)

SELECT
    MD5(date::VARCHAR) AS date_key,
    TRY_TO_DATE(date) AS date,
    YEAR(TRY_TO_DATE(date)) AS year,
    MONTH(TRY_TO_DATE(date)) AS month,
    DAY(TRY_TO_DATE(date)) AS day,
    DAYOFWEEK(TRY_TO_DATE(date)) AS day_of_week,
    DAYNAME(TRY_TO_DATE(date)) AS day_name
FROM date_spine
