# Staging Model Reference

## Model: stg_customers

**File:** `models/01_staging/stg_customers.sql`

```sql
{{ config(materialized='view') }}

SELECT
    customer_id,
    UPPER(customer_name) as customer_name,
    LOWER(email) as email,
    city,
    signup_date,
    total_orders,
    total_spent,
    CASE
        WHEN total_spent >= 500 THEN 'High Value'
        WHEN total_spent >= 200 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment,
    CASE
        WHEN email IS NOT NULL AND email LIKE '%@%' THEN TRUE
        ELSE FALSE
    END as has_valid_email,
    CURRENT_TIMESTAMP() as dbt_loaded_at
FROM {{ source('raw', 'customers') }}
WHERE customer_id IS NOT NULL
```

## Tests

**File:** `models/01_staging/stg_customers.yml`

```yaml
version: 2

models:
  - name: stg_customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
      - name: customer_segment
        tests:
          - accepted_values:
              values: ['High Value', 'Medium Value', 'Low Value']
```

## Commands

```bash
dbt run --select stg_customers
dbt test --select stg_customers
```

## Verify in Snowflake

```sql
SELECT * FROM DB_T34.PUBLIC.STG_CUSTOMERS;
SELECT customer_segment, COUNT(*) FROM DB_T34.PUBLIC.STG_CUSTOMERS GROUP BY 1;
```
