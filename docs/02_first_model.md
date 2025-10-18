# Your First dbt Model - Complete Success! 🎉

## What We Built

### 1. Source Definition (`_sources.yml`)
Told dbt where to find the raw data in Snowflake.

### 2. Staging Model (`stg_customers.sql`)
Cleaned and transformed the raw customer data:
- Made names UPPERCASE
- Made emails lowercase
- Added customer segmentation (High/Medium/Low Value)
- Added email validation flag
- Added processing timestamp

### 3. Model Documentation (`stg_customers.yml`)
Defined tests and documentation for the model.

---

## What dbt Did

When you ran `dbt run --select stg_customers`:

1. **Read** the source definition
2. **Connected** to Snowflake
3. **Executed** the SQL in `stg_customers.sql`
4. **Created** a VIEW called `DB_T34.PUBLIC.STG_CUSTOMERS`
5. **Logged** the results

---

## Results

### Run Results
```
✅ 1 of 1 OK created sql view model PUBLIC.stg_customers
✅ Completed successfully
```

### Test Results
```
✅ 8 of 8 TESTS PASSED
- customer_id is unique ✅
- customer_id is not null ✅
- customer_name is not null ✅
- email is not null ✅
- customer_segment has valid values ✅
- has_valid_email is not null ✅
- dbt_loaded_at is not null ✅
- unique customer_id ✅
```

---

## View the Data in Snowflake

Run this SQL in Snowflake Worksheets:

```sql
-- View the transformed data
SELECT * FROM DB_T34.PUBLIC.STG_CUSTOMERS;

-- Count by segment
SELECT
    customer_segment,
    COUNT(*) as customer_count,
    SUM(total_spent) as total_revenue
FROM DB_T34.PUBLIC.STG_CUSTOMERS
GROUP BY customer_segment
ORDER BY total_revenue DESC;

-- Check email validation
SELECT
    has_valid_email,
    COUNT(*) as count
FROM DB_T34.PUBLIC.STG_CUSTOMERS
GROUP BY has_valid_email;
```

---

## What Changed from Raw to Staging

### Original (RAW.CUSTOMERS)
```
customer_name: "John Doe"
email: "JOHN@EXAMPLE.COM"
```

### Transformed (PUBLIC.STG_CUSTOMERS)
```
customer_name: "JOHN DOE"        ← Uppercased
email: "john@example.com"        ← Lowercased
customer_segment: "Medium Value" ← NEW calculated field
has_valid_email: TRUE            ← NEW validation flag
dbt_loaded_at: 2025-10-18...    ← NEW timestamp
```

---

## Commands Used

### Run the model
```bash
cd /Users/lehongthai/code_personal/fa-c002-lab/my_dbt_project
source ../.venv/bin/activate
dbt run --select stg_customers
```

### Test the model
```bash
dbt test --select stg_customers
```

### Run and test together
```bash
dbt run --select stg_customers && dbt test --select stg_customers
```

---

## Project Structure Now

```
my_dbt_project/
└── models/
    └── 01_staging/
        ├── _sources.yml          ← Defines source tables
        ├── stg_customers.sql     ← Transformation logic
        └── stg_customers.yml     ← Tests and docs
```

---

## What You Learned

✅ **Source definitions** - How to tell dbt where raw data lives
✅ **SQL transformations** - How to clean and enrich data
✅ **Data quality tests** - How to validate your data automatically
✅ **dbt workflow** - run → test → verify

---

## Next Steps

Now you can:
1. **Add more staging models** for other raw tables
2. **Create intermediate models** with business logic
3. **Build mart models** (dimensions and facts)
4. **Generate documentation** with `dbt docs generate`

---

**Congratulations! You've successfully created your first dbt model!** 🎉
