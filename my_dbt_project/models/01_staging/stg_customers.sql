{{ config(materialized='view') }}

-- This is your first dbt model!
-- It takes raw customer data and cleans it up

SELECT
    -- Primary key
    customer_id,

    -- Customer details
    UPPER(customer_name) as customer_name,  -- Make names uppercase
    LOWER(email) as email,                   -- Make emails lowercase
    city,
    signup_date,

    -- Metrics
    total_orders,
    total_spent,

    -- Calculated fields
    CASE
        WHEN total_spent >= 500 THEN 'High Value'
        WHEN total_spent >= 200 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment,

    -- Data quality flags
    CASE
        WHEN email IS NOT NULL AND email LIKE '%@%' THEN TRUE
        ELSE FALSE
    END as has_valid_email,

    -- Metadata
    CURRENT_TIMESTAMP() as dbt_loaded_at

FROM {{ source('raw', 'customers') }}
WHERE customer_id IS NOT NULL  -- Only keep valid customers
