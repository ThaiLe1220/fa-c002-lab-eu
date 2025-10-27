# Next Steps - Mobile Analytics Data Warehouse

**Status:** ✅ Data Collection Complete → 🔄 dbt Transformations Next
**Date:** October 27, 2025
**Test Date:** November 1, 2025

---

## What We've Completed

✅ **Data Collection Pipeline (Oct 27) - 35/100 pts**
- **AdMob daily pipeline:** 16,151 rows loaded (pure RAW)
- **Adjust hourly pipeline:** 127,797 rows loaded (pure RAW)
- **Pure RAW architecture:** No transformations in Python, exact API responses
- **Snowflake RAW tables:** ADMOB_DAILY, ADJUST_HOURLY created and populated
- **Validation script:** `check_data.py` shows random samples from both tables

**See:** `docs/progress/01_data_collection_pipeline.md` for complete details

✅ **Planning & Validation (Oct 19-22)**
- API validation: AdMob (daily 13.5K rows) + Adjust (hourly 936 rows)
- Architecture validated: Everything to Snowflake RAW schema
- Test requirements mapped: Batch (AdMob) + Incremental (Adjust)
- Dimensional model designed: 4 fact tables, 7+ dimensions
- Snowflake connection working: JWT authentication configured

✅ **Architecture Decisions**
- **Pure RAW:** Python stores exact API responses, dbt does all transformations
- **Snowflake-only:** Skip PostgreSQL Docker (simpler, industry-standard)
- **Orchestration:** GitHub Actions scheduled workflows (documented)

---

## Next: dbt Transformations (40 pts)

### 1. Staging Layer - Clean & Standardize RAW Data

**`models/staging/stg_admob__daily_performance.sql`:**
- Convert date string `20251024` → DATE type
- Divide microsValues by 1,000,000 for dollars
- Cast string integers → INTEGER type
- Remove duplicates

**`models/staging/stg_adjust__daily_metrics.sql`:**
- Aggregate hourly → daily grain (SUM metrics by day, app, country)
- Rename: `store_id` → `app_id`, `day` → `date`
- Standardize country codes

**Success Criteria:**
- [ ] Both staging models created
- [ ] dbt run completes successfully
- [ ] Data types correct (DATE, INTEGER, DECIMAL)

---

### 2. Intermediate Layer - Business Logic

**`models/intermediate/int_daily_unified.sql`:**
- Join AdMob + Adjust by (app, date, country)
- Calculate business metrics:
  - `roas_d0` = ad_revenue / network_cost
  - `ecpm` = (ad_revenue / ad_impressions) * 1000
  - `cpi` = network_cost / installs
  - `impdau_d0` = ad_impressions / daus
- Left join (keep all AdMob revenue even if Adjust missing)

**Success Criteria:**
- [ ] Unified daily metrics table created
- [ ] Business calculations correct
- [ ] Joins working properly

---

### 3. Mart Layer - Dimensional Model (Star Schema)

**Dimensions:**
- `models/mart/dim_date.sql` - Calendar table
- `models/mart/dim_app.sql` - App master list
- `models/mart/dim_country.sql` - Country reference

**Facts:**
- `models/mart/fct_daily_performance.sql` - Main fact table (incremental)

**Incremental Configuration:**
```sql
{{ config(
    materialized='incremental',
    unique_key=['date', 'app_id', 'country_code']
) }}
```

**Success Criteria:**
- [ ] Star schema with 3+ dimensions, 1+ fact table
- [ ] Incremental models working (only process new data)
- [ ] Relationships valid (foreign keys exist)

---

### 4. Testing & Quality (10 pts)

**dbt Tests Required:**
- **Uniqueness:** Primary keys must be unique
- **Not Null:** Critical columns cannot be null
- **Relationships:** Foreign keys must exist in dimension tables
- **Accepted Range:** Metrics within valid ranges
- **Custom Tests:** Business logic validation

**Target:** 10+ tests minimum

**Success Criteria:**
- [ ] Tests defined in `models/schema.yml`
- [ ] dbt test passes all tests
- [ ] Critical data quality validated

---

### 5. CI/CD Pipeline (5 pts)

**`.github/workflows/dbt_ci.yml`:**
- Trigger: On pull request
- Steps: Install dependencies → SQLFluff lint → dbt test

**SQLFluff Configuration (`.sqlfluff`):**
- Dialect: snowflake
- Basic SQL style enforcement

**Success Criteria:**
- [ ] GitHub Actions workflow created
- [ ] SQLFluff linting passing
- [ ] dbt tests running in CI

---

### 6. Documentation & ERD (Extra 10 pts)

**ERD Diagram:**
- Tool: dbdiagram.io or dbt docs
- Show: Fact/dimension relationships clearly

**dbt Documentation:**
```bash
dbt docs generate
dbt docs serve
```

**Success Criteria:**
- [ ] ERD shows dimensional model
- [ ] dbt docs generated with descriptions
- [ ] README updated with architecture overview

---

### 7. Demo Preparation

**20-Minute Demo Flow:**

**1. Data Collection (5 min):**
```bash
python scripts/collect_admob.py --days 1
python scripts/collect_adjust.py --hours 1
python scripts/check_data.py
```

**2. Transformations (8 min):**
```bash
dbt run
dbt test
dbt docs serve
```

**3. CI/CD (4 min):**
- Show GitHub Actions: PR with passing checks
- Show tests: Data quality validated

**4. Documentation (3 min):**
- Show ERD: Dimensional model
- Show dbt docs: Model descriptions

**Success Criteria:**
- [ ] Demo runs smoothly in <20 minutes
- [ ] All test requirements demonstrated
- [ ] Can explain architecture decisions

---

## Test Score Projection

| Category | Points | Status | Implementation |
|----------|--------|--------|----------------|
| **Data Ingestion** | 35 | ✅ Complete | Batch (AdMob) + Incremental (Adjust) |
| **Transformation** | 40 | 🔄 Next | 3-layer dbt + incremental + tests |
| **CI/CD** | 5 | ⏳ Pending | GitHub Actions with dbt test |
| **Extra Features** | 20 | ⏳ Pending | Advanced dbt, custom macros, docs |

**Current:** 35/100 pts
**Target:** 70+ pts (Pass: 50+)
**Projected:** 80-85 pts

---

## Files to Create

**dbt Models:**
1. `models/staging/stg_admob__daily_performance.sql`
2. `models/staging/stg_adjust__daily_metrics.sql`
3. `models/intermediate/int_daily_unified.sql`
4. `models/mart/dim_date.sql`
5. `models/mart/dim_app.sql`
6. `models/mart/dim_country.sql`
7. `models/mart/fct_daily_performance.sql`
8. `models/schema.yml` - dbt tests + documentation

**CI/CD:**
9. `.github/workflows/dbt_ci.yml`
10. `.sqlfluff`

**Documentation:**
11. ERD diagram
12. README updates

---

## Quick Commands

**Data Collection:**
```bash
python scripts/collect_admob.py --days 7
python scripts/collect_adjust.py --hours 24
python scripts/check_data.py
```

**dbt Workflow:**
```bash
dbt debug          # Test connection
dbt run            # Run all models
dbt test           # Run all tests
dbt docs generate  # Generate documentation
dbt docs serve     # View documentation
```

**Development:**
```bash
dbt run --select stg_admob__daily_performance  # Run one model
dbt test --select stg_admob__daily_performance # Test one model
sqlfluff lint models/staging/                   # Lint specific folder
```

---

**Next Action:** Create `models/staging/stg_admob__daily_performance.sql`
