{% macro calculate_ctr(clicks, impressions) %}
    CASE
        WHEN {{ impressions }} > 0
        THEN ({{ clicks }}::DECIMAL / {{ impressions }}) * 100
        ELSE 0
    END
{% endmacro %}
