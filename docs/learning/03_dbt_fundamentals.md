# Module 3: dbt Fundamentals

**What you learned about data transformation with dbt**

---

## 🎯 Core Concepts Learned

### 1. What is dbt?

**dbt = data build tool**

**Simple explanation you discovered:**
```
Raw Data (in Snowflake)
    ↓
dbt transforms it (using SQL)
    ↓
Clean, modeled data (back in Snowflake)
```

**What dbt does:**
- ✅ Transforms data using SQL
- ✅ Tests data quality
- ✅ Documents models
- ✅ Manages dependencies
- ✅ Versions transformations in Git

**What dbt does NOT do:**
- ❌ Extract data from sources
- ❌ Load data into warehouse
- ❌ Visualize data
- ❌ Replace your data warehouse

**Key insight:** dbt is the "T" in ELT (Extract, Load, Transform)

---

### 2. ELT vs ETL Paradigm Shift

**Old Way (ETL):**
```
Extract → Transform (on separate server) → Load to warehouse
```
- Expensive transformation servers
- Data not immediately queryable
- Hard to debug

**New Way (ELT) - What you used:**
```
Extract → Load to warehouse → Transform (in warehouse with dbt)
```
- Uses warehouse compute (already paying for it)
- All data immediately queryable
- Easy to debug (it's just SQL)

**Why dbt enables ELT:**
- Warehouses are now powerful enough
- Separation of compute/storage makes it affordable
- SQL is the transformation language

---

## 📁 dbt Project Structure You Built

### Directory Layout

```
my_dbt_project/
├── dbt_project.yml       ← Project configuration
├── models/               ← Your SQL transformations
│   ├── 01_staging/      ← Clean raw data
│   ├── 02_intermediate/ ← Business logic
│   └── 03_mart/         ← Analytics-ready
├── tests/               ← Custom data tests
├── macros/              ← Reusable SQL functions
├── seeds/               ← Small CSV files
└── snapshots/           ← Historical tracking
```

---

### Three-Layer Architecture You Implemented

**Why three layers:**

```
01_staging/
    ↓ Purpose: Clean and standardize
    ↓ Input: Raw source data
    ↓ Output: Consistent, typed data
    ↓
02_intermediate/
    ↓ Purpose: Business logic
    ↓ Input: Staging models
    ↓ Output: Joined, enriched data
    ↓
03_mart/
    ↓ Purpose: Analytics-ready
    ↓ Input: Intermediate models
    ↓ Output: Dimensional models (facts, dims)
```

**Real-world benefit:**
- ✅ Separation of concerns
- ✅ Easier to maintain
- ✅ Can reuse staging across marts
- ✅ Clear data lineage

---

## 🔧 Key dbt Components You Used

### 1. Sources - Defining Raw Data

**File:** `models/01_staging/_sources.yml`

**What you wrote:**
```yaml
sources:
  - name: raw
    database: DB_T34
    schema: RAW
    tables:
      - name: customers
```

**What this does:**
- Tells dbt where raw data lives
- Can reference with `{{ source('raw', 'customers') }}`
- Enables dependency tracking
- Enables source freshness checks

**Why use sources vs hardcoding:**
```sql
-- ❌ DON'T: Hardcode table names
FROM DB_T34.RAW.CUSTOMERS

-- ✅ DO: Use source function
FROM {{ source('raw', 'customers') }}
```

**Benefits:**
- Change database/schema in one place
- dbt tracks if source tables exist
- Can test source data quality
- Clear in documentation

---

### 2. Models - Your SQL Transformations

**File:** `models/01_staging/stg_customers.sql`

**What you wrote:**
```sql
{{ config(materialized='view') }}

SELECT
    customer_id,
    UPPER(customer_name) as customer_name,
    LOWER(email) as email,
    CASE
        WHEN total_spent >= 500 THEN 'High Value'
        WHEN total_spent >= 200 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment
FROM {{ source('raw', 'customers') }}
```

**What dbt does with this:**
1. Reads the SQL file
2. Compiles Jinja (the `{{ }}` parts)
3. Runs the SQL in Snowflake
4. Creates a VIEW called `stg_customers`
5. Stores it in `DB_T34.PUBLIC.STG_CUSTOMERS`

---

### 3. Materialization Strategies

**What you learned:**

**VIEW (what you used):**
```yaml
{{ config(materialized='view') }}
```
- ✅ Always fresh data
- ✅ No storage cost
- ❌ Query runs every time
- **Use when:** Data changes frequently, fast query

**TABLE:**
```yaml
{{ config(materialized='table') }}
```
- ✅ Fast to query
- ❌ Storage cost
- ❌ Data can be stale
- **Use when:** Slow query, data doesn't change often

**INCREMENTAL (you'll learn next):**
```yaml
{{ config(materialized='incremental') }}
```
- ✅ Only processes new data
- ✅ Handles big tables
- ❌ More complex logic
- **Use when:** Millions of rows, append-only data

**Real-world decision tree:**
```
Is data > 1M rows?
├─ YES → Use incremental
└─ NO → Is query slow?
    ├─ YES → Use table
    └─ NO → Use view (what you used)
```

---

### 4. Tests - Data Quality as Code

**File:** `models/01_staging/stg_customers.yml`

**What you wrote:**
```yaml
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

**What dbt does with tests:**
```bash
dbt test
```

**Generates SQL like:**
```sql
-- unique test
SELECT customer_id, COUNT(*)
FROM stg_customers
GROUP BY customer_id
HAVING COUNT(*) > 1  -- Fails if any duplicates

-- not_null test
SELECT *
FROM stg_customers
WHERE customer_id IS NULL  -- Fails if any nulls

-- accepted_values test
SELECT *
FROM stg_customers
WHERE customer_segment NOT IN ('High Value', 'Medium Value', 'Low Value')
```

**Why tests matter:**
- 🐛 Catch data quality issues automatically
- 📊 Document expectations
- 🔔 Alert when data breaks
- ✅ Confidence in prod

---

## 🎨 Jinja Templating You Used

### {{ }} - Execute Python/Jinja

**What you used:**
```sql
FROM {{ source('raw', 'customers') }}
```

**What it becomes:**
```sql
FROM DB_T34.RAW.CUSTOMERS
```

**Other Jinja you'll use:**
```sql
-- If/else logic
{% if target.name == 'prod' %}
    FROM prod_table
{% else %}
    FROM dev_table
{% endif %}

-- Loops
{% for column in ['name', 'email', 'city'] %}
    {{ column }},
{% endfor %}

-- Set variables
{% set payment_methods = ['credit', 'debit', 'paypal'] %}
```

**Why Jinja in SQL:**
- ✅ DRY (Don't Repeat Yourself)
- ✅ Environment-specific logic
- ✅ Generate SQL programmatically
- ✅ Reusable code patterns

---

## 🔄 dbt Workflow You Learned

### Development Cycle

```bash
# 1. Make changes to SQL file
vim models/01_staging/stg_customers.sql

# 2. Run the model
dbt run --select stg_customers

# 3. Test the model
dbt test --select stg_customers

# 4. Check results in Snowflake
# Query the table/view

# 5. Commit to Git
git add . && git commit -m "Add customer staging model"
```

**Key insight:** Fast iteration loop (edit → run → test → verify)

---

### Commands You Mastered

**dbt debug:**
```bash
dbt debug
# Tests connection, shows configuration
```

**dbt run:**
```bash
dbt run                          # Run all models
dbt run --select stg_customers   # Run specific model
dbt run --select 01_staging      # Run all staging models
dbt run --select +stg_customers  # Run upstream dependencies too
```

**dbt test:**
```bash
dbt test                         # Run all tests
dbt test --select stg_customers  # Test specific model
```

**dbt compile:**
```bash
dbt compile
# Shows compiled SQL without running it
# Good for debugging Jinja
```

---

## 💡 Key Insights You Discovered

### Insight 1: "SQL + Version Control = Magic"

**What you learned:**
- SQL transformations in Git
- Can see history of changes
- Can collaborate like software engineers
- Can review before deploying

**Real-world impact:**
```bash
git log models/01_staging/stg_customers.sql
# See who changed what and when
```

---

### Insight 2: "Tests Are Documentation"

**Your test:**
```yaml
- name: customer_segment
  tests:
    - accepted_values:
        values: ['High Value', 'Medium Value', 'Low Value']
```

**What this tells you:**
- ✅ customer_segment can only be these three values
- ✅ This is enforced automatically
- ✅ If data breaks this, tests fail

**Better than comment:**
```sql
-- customer_segment should be High/Medium/Low Value
-- (Nobody checks this)
```

---

### Insight 3: "Transformation Layers Enable Collaboration"

**What you built:**
```
01_staging/ → 02_intermediate/ → 03_mart/
```

**Why it matters:**
- Team A owns staging (data engineers)
- Team B owns marts (analytics engineers)
- Both can work independently
- Changes in staging flow through

---

## 🚫 Common Mistakes You Avoided

### Mistake 1: Complex Logic in One Model
❌ **DON'T:**
```sql
-- 500 lines of SQL with 10 joins in one file
```

✅ **DO:**
```sql
-- 01_staging/: Clean raw data (simple)
-- 02_intermediate/: Join and enrich (moderate)
-- 03_mart/: Final dimensional model (simple again)
```

**What you did:** Kept stg_customers simple (just cleaning)

---

### Mistake 2: No Tests
❌ **DON'T:** Assume data is correct

✅ **DO:** Test assumptions
```yaml
tests:
  - unique
  - not_null
  - accepted_values
```

**What you did:** 8 tests on first model ✅

---

### Mistake 3: Hardcoding Database Names
❌ **DON'T:**
```sql
FROM DB_T34.RAW.CUSTOMERS
```

✅ **DO:**
```sql
FROM {{ source('raw', 'customers') }}
```

**What you did:** Used source function ✅

---

## 📊 dbt Run Lifecycle

### What Happens When You Run `dbt run`

**Step-by-step:**

1. **Parse project:**
   - Read dbt_project.yml
   - Find all .sql files
   - Read all .yml files

2. **Compile Jinja:**
   - Replace `{{ source() }}` with actual table names
   - Process {% if %} statements
   - Generate pure SQL

3. **Build DAG:**
   - Determine dependencies
   - Order models correctly
   - Plan execution

4. **Execute:**
   - Run SQL in Snowflake
   - Create views/tables
   - Collect metrics

5. **Report:**
   - Show results (PASS/FAIL)
   - Execution time
   - Rows affected

**You saw this:**
```
1 of 1 START sql view model PUBLIC.stg_customers ....... [RUN]
1 of 1 OK created sql view model PUBLIC.stg_customers .. [SUCCESS 1] in 0.61s
```

---

## 🎯 Skills You Can Transfer

### To Other Data Platforms
- ✅ dbt works with BigQuery, Redshift, Postgres, etc.
- ✅ Same project structure
- ✅ Same commands
- ✅ Just change profiles.yml

### To Software Engineering
- ✅ Version control for data
- ✅ Testing as code
- ✅ CI/CD for analytics
- ✅ Code review for SQL

### To Analytics Engineering
- ✅ Dimensional modeling
- ✅ Incremental processing
- ✅ Data quality frameworks
- ✅ Documentation generation

---

## 🎓 Quiz Yourself

1. **What is the difference between a source and a model?**
   <details>
   <summary>Answer</summary>
   Source = raw data (already exists in warehouse). Model = transformed data (created by dbt)
   </details>

2. **When should you use a view vs a table?**
   <details>
   <summary>Answer</summary>
   View = always fresh, fast to build. Table = faster to query, uses storage. Use view for small/fast queries, table for large/slow queries.
   </details>

3. **Why test your models?**
   <details>
   <summary>Answer</summary>
   Catch data quality issues automatically, document expectations, alert when data breaks
   </details>

4. **What does {{ source('raw', 'customers') }} do?**
   <details>
   <summary>Answer</summary>
   References the customers table defined in sources.yml, compiles to actual database.schema.table
   </details>

---

## 🚀 What You Can Do Now

✅ Create dbt models with SQL
✅ Define sources for raw data
✅ Write data quality tests
✅ Use Jinja templating basics
✅ Run and test models
✅ Understand dbt execution lifecycle
✅ Apply three-layer architecture

---

## 📈 Your Progress

**What you built:**
- 1 source definition
- 1 staging model
- 8 automated tests
- Complete documentation

**What this represents:**
- Foundation for entire dbt project
- Repeatable pattern for more models
- Professional-grade data pipeline

---

**Key Takeaway:** dbt transforms SQL from ad-hoc scripts into a software engineering workflow. With version control, testing, and documentation built in, you've learned how modern data teams build reliable, scalable data pipelines. The pattern you learned (source → model → test → document) applies to every model you'll ever create.
