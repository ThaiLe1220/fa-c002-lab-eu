{{ config(materialized='table') }}

SELECT DISTINCT
    MD5(app_store_id) AS app_key,
    app_store_id,
    CASE app_store_id
        WHEN 'video.ai.videogenerator' THEN 'Video AI Generator'
        WHEN 'ai.video.generator.text.video' THEN 'AI Video Text Generator'
        WHEN 'text.to.video.aivideo.generator' THEN 'Text to Video AI'
        ELSE app_store_id
    END AS app_name
FROM {{ ref('int_app_daily_metrics') }}
