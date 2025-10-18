# Module 4: Data Modeling & Staging Layer

**What you learned about data modeling and the staging layer**

---

## 🎯 Core Concepts Learned

### 1. The Staging Layer Purpose

**Your staging model:** `stg_customers.sql`

**What staging does:**
```
Raw Data (messy, inconsistent)
    ↓ STAGING LAYER
    ↓ - Clean
    ↓ - Standardize
    ↓ - Type properly
    ↓
Clean Data (consistent, typed, documented)
```

**Staging layer rules you applied:**
- ✅ One-to-one with source tables
- ✅ No business logic (just cleaning)
- ✅ No joins (single table transformations)
- ✅ Renamed columns for clarity
- ✅ Type casting for consistency
- ✅ Basic validation flags

---

### 2. Data Transformations You Implemented

**String Normalization:**
```sql
-- Names: Uppercase for consistency
UPPER(customer_name) as customer_name
-- "John Doe" → "JOHN DOE"

-- Emails: Lowercase for matching
LOWER(email) as email
-- "JOHN@EXAMPLE.COM" → "john@example.com"
```

**Why this matters:**
- Prevents duplicate matches due to case
- Consistent formatting for analytics
- Easier to join tables later

---

**Calculated Fields:**
```sql
CASE
    WHEN total_spent >= 500 THEN 'High Value'
    WHEN total_spent >= 200 THEN 'Medium Value'
    ELSE 'Low Value'
END as customer_segment
```

**Why in staging:**
- ✅ Adds business context early
- ✅ Reusable in downstream models
- ✅ Tested once, used everywhere

---

**Validation Flags:**
```sql
CASE
    WHEN email IS NOT NULL AND email LIKE '%@%' THEN TRUE
    ELSE FALSE
END as has_valid_email
```

**Why validation flags:**
- ✅ Data quality visibility
- ✅ Can filter downstream
- ✅ Alert on quality issues
- ✅ Document data issues

---

**Metadata Tracking:**
```sql
CURRENT_TIMESTAMP() as dbt_loaded_at
```

**Why track metadata:**
- ✅ Know when data was processed
- ✅ Debug data issues
- ✅ Audit trail
- ✅ Monitor freshness

---

## 📊 Data Quality Framework You Built

### Test Pyramid You Implemented

```
          ▲
         / \
        /   \  1. Business Rules (customer_segment values)
       /     \
      /       \  2. Relationships (future: foreign keys)
     /         \
    /           \  3. Schema (not_null, unique)
   /_____________\
```

**Your 8 tests:**

**Schema Tests (foundational):**
```yaml
- unique                 # No duplicate customer_ids
- not_null              # Required fields present
```

**Value Tests (data quality):**
```yaml
- accepted_values       # customer_segment only has valid values
```

---

### Test Coverage Strategy

**What you tested:**

1. **Uniqueness:**
   ```yaml
   - name: customer_id
     tests:
       - unique
   ```
   **Why:** Primary key must be unique

2. **Not Null:**
   ```yaml
   - name: customer_name
     tests:
       - not_null
   ```
   **Why:** Required fields must have values

3. **Accepted Values:**
   ```yaml
   - name: customer_segment
     tests:
       - accepted_values:
           values: ['High Value', 'Medium Value', 'Low Value']
   ```
   **Why:** Constrained fields must match expected values

---

### When Tests Run

**Your workflow:**
```bash
dbt run --select stg_customers   # Build model
dbt test --select stg_customers  # Validate data
```

**What happens:**
1. dbt generates test SQL
2. Runs it against your data
3. Checks if any rows returned
4. Returns returned rows = test fails
5. No rows returned = test passes

**Example test SQL (unique):**
```sql
SELECT
    customer_id,
    COUNT(*) as n_records
FROM DB_T34.PUBLIC.STG_CUSTOMERS
GROUP BY customer_id
HAVING COUNT(*) > 1
```

If this returns rows → duplicates exist → test fails ❌

---

## 🎨 Naming Conventions You Learned

### File Naming

**Pattern:** `stg_<source>_<entity>.sql`

**What you used:**
- `stg_customers.sql` ✅
  - `stg_` = staging layer
  - `customers` = source entity

**Why this pattern:**
- ✅ Know layer at a glance
- ✅ Alphabetically grouped
- ✅ Clear data lineage

---

### Column Naming

**What you did:**
```sql
customer_id        -- Not: customerId, CustomerID, cust_id
customer_name      -- Not: name, custName
has_valid_email    -- Boolean: has_, is_, can_
dbt_loaded_at      -- Metadata: prefix with source
```

**Naming principles you applied:**
- `snake_case` for columns
- Descriptive, not abbreviated
- Boolean prefix: `is_`, `has_`, `can_`
- Metadata prefix: `dbt_`, `_at`, `_date`

---

### Model Naming

**Pattern you'll follow:**

```
01_staging/
  stg_customers.sql
  stg_orders.sql
  stg_products.sql

02_intermediate/
  int_customer_orders.sql
  int_order_items.sql

03_mart/
  dim_customers.sql
  fct_orders.sql
```

**Prefixes:**
- `stg_` = staging
- `int_` = intermediate
- `dim_` = dimension table
- `fct_` = fact table

---

## 💡 Data Modeling Insights

### Insight 1: "Clean Once, Use Many Times"

**What you learned:**
```
RAW.CUSTOMERS (messy)
    ↓ Clean once in stg_customers
    ↓
STG_CUSTOMERS (clean)
    ↓ Used by multiple downstream models
    ├→ int_customer_orders
    ├→ dim_customers
    └→ customer_analytics
```

**Real-world impact:**
- Don't repeat cleaning logic
- Consistent data everywhere
- One place to fix issues

---

### Insight 2: "Validation Early, Confidence Later"

**What you did:**
```yaml
# Test in staging
tests:
  - unique
  - not_null
  - accepted_values
```

**Why test early:**
- Catch issues at source
- Don't propagate bad data
- Faster debugging
- Clear ownership (staging owner fixes)

---

### Insight 3: "Metadata is Data"

**What you added:**
```sql
CURRENT_TIMESTAMP() as dbt_loaded_at
'dbt_staging' as processing_source
```

**Why metadata matters:**
- Debug data issues
- Audit trail
- Monitor freshness
- Understand data lineage

---

## 🚫 Staging Layer Mistakes You Avoided

### Mistake 1: Business Logic in Staging
❌ **DON'T:**
```sql
-- In staging
SELECT
    c.customer_id,
    SUM(o.order_amount) as lifetime_value  -- Aggregation = business logic
FROM customers c
JOIN orders o  -- Joins = business logic
```

✅ **DO:**
```sql
-- In staging: Just clean
SELECT
    customer_id,
    UPPER(customer_name) as customer_name  -- Simple transformation
FROM customers
-- No joins, no aggregations
```

**What you did:** Kept stg_customers simple ✅

---

### Mistake 2: No Data Type Casting
❌ **DON'T:**
```sql
SELECT
    customer_id,  -- Unknown type from source
    signup_date   -- Might be string
```

✅ **DO:**
```sql
SELECT
    customer_id::INTEGER,
    signup_date::DATE
```

**What you could add:**
```sql
SELECT
    customer_id::INTEGER as customer_id,
    customer_name::VARCHAR(100) as customer_name,
    email::VARCHAR(100) as email,
    total_spent::DECIMAL(10,2) as total_spent
```

---

### Mistake 3: Inconsistent Naming
❌ **DON'T:**
```sql
-- Source has: c_custkey, CustName, CUSTOMER_EMAIL
SELECT
    c_custkey,
    CustName,
    CUSTOMER_EMAIL
-- Different cases, cryptic names
```

✅ **DO:**
```sql
SELECT
    c_custkey::INTEGER as customer_id,
    CustName::VARCHAR as customer_name,
    CUSTOMER_EMAIL::VARCHAR as email
-- Consistent snake_case, clear names
```

**What you did:** Standardized naming ✅

---

## 📊 Documentation Pattern You Learned

### Complete Model Documentation

**What you created:**
```yaml
models:
  - name: stg_customers
    description: "Cleaned and standardized customer data"
    columns:
      - name: customer_id
        description: "Unique customer identifier"
        tests:
          - unique
          - not_null
```

**Three parts:**
1. Model description (what it is)
2. Column descriptions (what they mean)
3. Tests (what's validated)

**Why this matters:**
- Self-documenting code
- Onboards new team members
- Shows up in dbt docs
- Documents business logic

---

### Documentation Best Practices

**What you applied:**

✅ **Be specific:**
```yaml
description: "Unique customer identifier from source system"
# Not just: "ID"
```

✅ **Explain transformations:**
```yaml
description: "Customer name standardized to uppercase"
# Not just: "Customer name"
```

✅ **Document test rationale:**
```yaml
description: "Must be unique (primary key)"
tests:
  - unique
```

---

## 🎯 Staging Layer Checklist

**For every staging model, you should:**

- [ ] One source table → one staging model
- [ ] Rename columns to clear, consistent names
- [ ] Cast to appropriate data types
- [ ] Add data quality flags
- [ ] Add metadata (loaded_at, source)
- [ ] Test uniqueness of IDs
- [ ] Test not null on required fields
- [ ] Test accepted values on constrained fields
- [ ] Document model and columns
- [ ] Keep it simple (no joins, no aggregations)

**Your stg_customers.sql checked all boxes!** ✅

---

## 🔍 Real-World Staging Patterns

### Pattern 1: Date Standardization

```sql
-- Source might have inconsistent dates
SELECT
    DATE(created_at) as created_date,
    DATE(updated_at) as updated_date,
    DATE(deleted_at) as deleted_date
FROM source_table
```

### Pattern 2: String Cleaning

```sql
SELECT
    TRIM(UPPER(customer_name)) as customer_name,
    TRIM(LOWER(email)) as email,
    TRIM(phone_number) as phone_number
FROM source_table
```

### Pattern 3: Null Handling

```sql
SELECT
    customer_id,
    COALESCE(customer_name, 'Unknown') as customer_name,
    COALESCE(city, 'Not Provided') as city
FROM source_table
```

### Pattern 4: Flag Creation

```sql
SELECT
    customer_id,
    CASE WHEN deleted_at IS NOT NULL THEN TRUE ELSE FALSE END as is_deleted,
    CASE WHEN email IS NOT NULL THEN TRUE ELSE FALSE END as has_email,
    CASE WHEN phone IS NOT NULL THEN TRUE ELSE FALSE END as has_phone
FROM source_table
```

---

## 🎓 Quiz Yourself

1. **What goes in the staging layer?**
   <details>
   <summary>Answer</summary>
   Cleaning, standardization, type casting, simple transformations. No joins, no aggregations, no complex business logic.
   </details>

2. **Why create validation flags?**
   <details>
   <summary>Answer</summary>
   Data quality visibility, can filter downstream, alert on issues, document problems
   </details>

3. **What's the purpose of dbt tests?**
   <details>
   <summary>Answer</summary>
   Automated data quality validation, document expectations, catch issues early
   </details>

4. **Why add metadata columns?**
   <details>
   <summary>Answer</summary>
   Debug issues, audit trail, monitor freshness, understand data lineage
   </details>

---

## 🚀 What You Can Do Now

✅ Create staging models following best practices
✅ Implement data quality tests
✅ Standardize naming conventions
✅ Add validation flags
✅ Document models and columns
✅ Apply staging layer patterns

---

## 📈 Your Data Modeling Foundation

**What you built:**
```
Source: RAW.CUSTOMERS (10 rows, messy)
    ↓
Model: STG_CUSTOMERS (10 rows, clean)
    ↓
Tests: 8 automated validations
    ↓
Documentation: Self-explanatory code
```

**This foundation enables:**
- Adding more staging models
- Building intermediate models
- Creating dimensional models
- Scaling to production

---

**Key Takeaway:** The staging layer is the foundation of your entire data pipeline. By cleaning data once and testing it thoroughly, you create a reliable base that all downstream models can trust. The patterns you learned (clean → test → document) apply to every staging model you'll ever create. You've built not just a model, but a reusable pattern for data quality.
