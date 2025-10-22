# Next Steps - Mobile Analytics Data Warehouse

**Status:** 🚀 Building Data Collection Pipeline
**Date:** October 22, 2025
**Test Date:** October 29 & November 1 (11 days remaining)

---

## Current Focus: Data Collection Pipeline

**Goal:** Get AdMob + Adjust data flowing into Snowflake RAW schema

**Architecture Decision:** Everything goes to Snowflake (no PostgreSQL Docker complexity)
- ✅ Simpler: One database instead of two
- ✅ Test-compliant: Still satisfies batch + incremental requirements
- ✅ Industry-standard: API → Cloud DWH → dbt pattern

**See:** `docs/implementation/IMPLEMENTATION_PLAN.md` for complete details

---

## What We've Completed

✅ **Planning & Validation Complete (Oct 19-22)**
- API validation: AdMob (daily 13.5K rows) + Adjust (hourly 936 rows)
- Architecture validated: Everything to Snowflake RAW schema
- Test requirements mapped: Batch (AdMob) + Incremental (Adjust)
- Dimensional model designed: 4 fact tables, 7+ dimensions
- Snowflake connection working: JWT authentication configured

✅ **Architecture Simplified (Oct 22)**
- Decision: Skip PostgreSQL Docker, use Snowflake for everything
- Batch pipeline: AdMob daily → Snowflake RAW.ADMOB_DAILY
- Incremental pipeline: Adjust hourly → Snowflake RAW.ADJUST_HOURLY
- Passes test: 13,500+ rows/batch (27x requirement), row-by-row incremental

---

## Week 1: Data Collection Pipeline (Oct 22-27)

### Day 1-2: RAW Schema + Batch Pipeline
**Priority:** Get AdMob batch pipeline working first (simpler than incremental)

**Tasks:**
1. **Create Snowflake RAW schema tables**
   ```sql
   -- Location: sql/setup/create_raw_tables.sql
   -- Tables: ADMOB_DAILY, ADJUST_HOURLY, ADJUST_COHORTS
   ```

2. **Build batch collection script**
   ```python
   # Location: scripts/collect_admob.py
   # Pattern: Follow M01W03/lab/scripts/data_loader.py structure
   # Function: AdMob API → pandas → Snowflake RAW.ADMOB_DAILY
   # Demo: Load last 7 days = 7 batches = ~94K rows
   ```

3. **Environment setup**
   ```bash
   # Location: .env (gitignored)
   # Variables: AdMob credentials + Snowflake (from dbt profile)
   ```

4. **Test batch pipeline**
   - Run script with --days 7 flag
   - Verify 13,500+ rows per batch in Snowflake
   - Check loaded_at timestamps are fresh
   - Validate data quality (no nulls in key fields)

**Success Criteria:**
- [ ] RAW.ADMOB_DAILY table created
- [ ] Script loads 13,500+ rows per batch
- [ ] Can demonstrate 7 batches loaded (~94K total rows)
- [ ] Fresh loaded_at timestamps prove data collected during demo

### Day 3-4: Incremental Pipeline
**Priority:** Get Adjust hourly pipeline working (row-by-row incremental)

**Tasks:**
1. **Build incremental collection script**
   ```python
   # Location: scripts/collect_adjust.py
   # Pattern: Follow batch script but fetch last 1 hour
   # Function: Adjust API → pandas → Snowflake RAW.ADJUST_HOURLY
   # Demo: Load last hour = ~39 rows row-by-row
   ```

2. **Add cohort collection**
   ```python
   # Location: scripts/collect_adjust_cohorts.py (optional but valuable)
   # Function: Cohort retention data → RAW.ADJUST_COHORTS
   ```

3. **Test incremental pipeline**
   - Run script with --hours 1 flag
   - Verify ~39 rows loaded with fresh timestamps
   - Run again, verify no duplicates (primary key handling)
   - Check incremental logic works (WHERE loaded_at > last_run)

**Success Criteria:**
- [ ] RAW.ADJUST_HOURLY table created
- [ ] Script loads ~39 rows per hour incrementally
- [ ] Fresh loaded_at timestamps within last 5 minutes
- [ ] No duplicate rows on repeated runs

### Day 5: Utilities + Documentation
**Priority:** Reusable code + clear demo instructions

**Tasks:**
1. **Create reusable utilities**
   ```python
   # Location: scripts/utils/snowflake_client.py
   # Function: Shared Snowflake connection, load functions
   ```

2. **Add error handling**
   - API rate limits
   - Network timeouts
   - Snowflake connection failures
   - Data validation (row counts, null checks)

3. **Write demo scripts**
   ```bash
   # Location: scripts/demo/run_batch_pipeline.sh
   # Purpose: One command to run entire batch demo
   ```

4. **Document usage**
   ```markdown
   # Location: scripts/README.md
   # Content: How to run each script, what to expect, troubleshooting
   ```

**Success Criteria:**
- [ ] Utilities reduce code duplication
- [ ] Error messages are clear and actionable
- [ ] Demo can run with single command
- [ ] Documentation covers setup + usage + troubleshooting

---

## Week 2: dbt Transformations (Oct 28 - Nov 1)

### Day 6-7: dbt Staging + Intermediate Models
**Priority:** Transform RAW → clean data with business logic

**Tasks:**
1. **Staging models** (clean + type cast)
   - `models/staging/stg_admob_daily.sql`
   - `models/staging/stg_adjust_hourly.sql`
   - `models/staging/stg_adjust_cohorts.sql`

2. **Intermediate models** (business logic)
   - `models/intermediate/int_daily_metrics.sql`
   - Calculate: ROAS, eCPM, CPI, IMPDAU_D0

3. **Run dbt**
   ```bash
   dbt run
   dbt test
   ```

**Success Criteria:**
- [ ] Staging models clean raw data (3 models)
- [ ] Intermediate models calculate business metrics
- [ ] dbt run completes successfully
- [ ] dbt test passes (10+ tests)

### Day 8: dbt Mart Models (Dimensional Model)
**Priority:** Star schema for analytics

**Tasks:**
1. **Dimension tables**
   - `models/mart/dim_app.sql`
   - `models/mart/dim_country.sql`
   - `models/mart/dim_date.sql`

2. **Fact tables**
   - `models/mart/fact_daily_performance.sql` (incremental)
   - `models/mart/fact_cohort_retention.sql`

3. **Configure incremental**
   ```sql
   {{ config(
       materialized='incremental',
       unique_key=['date', 'app_id', 'country_code']
   ) }}
   ```

**Success Criteria:**
- [ ] Star schema with 3+ dimensions, 2+ fact tables
- [ ] Incremental models working (only process new data)
- [ ] Relationships tested (foreign keys valid)

### Day 9: CI/CD + Testing
**Priority:** Automated quality checks

**Tasks:**
1. **dbt tests** (data quality)
   - not_null on key fields
   - unique on primary keys
   - relationships (foreign keys)
   - accepted_range on metrics

2. **GitHub Actions**
   ```yaml
   # Location: .github/workflows/dbt_ci.yml
   # Pattern: Follow M02W03L04 lab example
   # Runs: SQLFluff lint + dbt test on every PR
   ```

3. **SQLFluff config**
   ```ini
   # Location: .sqlfluff
   # Dialect: snowflake
   # Rules: Basic SQL style enforcement
   ```

**Success Criteria:**
- [ ] 10+ dbt tests defined and passing
- [ ] GitHub Actions CI running on PRs
- [ ] SQLFluff linting passing

### Day 10: Documentation + ERD
**Priority:** Complete project deliverables

**Tasks:**
1. **ERD diagram**
   - Tool: dbdiagram.io or dbt docs
   - Show: Fact/dimension relationships

2. **dbt documentation**
   ```bash
   dbt docs generate
   dbt docs serve
   ```

3. **Update README**
   - Show test score breakdown
   - Demo instructions
   - Architecture diagram

**Success Criteria:**
- [ ] ERD shows dimensional model clearly
- [ ] dbt docs generated with descriptions
- [ ] README has complete demo instructions

### Day 11: Test Day Prep
**Priority:** Rehearse 20-minute demo

**Demo Flow:**
1. **Data Collection (5 min)**
   - Run batch pipeline: `python scripts/collect_admob.py --days 7`
   - Run incremental: `python scripts/collect_adjust.py --hours 1`
   - Show Snowflake: Batch 13,500+ rows, incremental ~39 rows

2. **Transformations (8 min)**
   - Run dbt: `dbt run && dbt test`
   - Show models: Staging → Intermediate → Mart
   - Show incremental: Only new data processed

3. **CI/CD (4 min)**
   - Show GitHub Actions: PR with passing checks
   - Show tests: Data quality validated

4. **Documentation (3 min)**
   - Show ERD: Dimensional model
   - Show dbt docs: Model descriptions

**Success Criteria:**
- [ ] Demo runs smoothly in <20 minutes
- [ ] All test requirements demonstrated
- [ ] Confident explaining architecture decisions

---

## Test Score Targets

**Current Plan Scores:**

| Category | Requirements | Our Implementation | Points |
|----------|-------------|-------------------|--------|
| **Data Ingestion (35 pts)** | | | |
| Git workflow | Feature branches, PRs | ✅ Already using | 5 |
| Batch pipeline | ≥500 rows/batch | ✅ AdMob 13,500+ rows | 10 |
| Real-time pipeline | Row-by-row incremental | ✅ Adjust hourly ~39 rows | 10 |
| Database | PostgreSQL Docker | ❌ Skip (using Snowflake) | 0 |
| Python quality | Error handling, logging | ✅ Following course pattern | 10 |
| **Transformation (40 pts)** | | | |
| 3-layer dbt | Staging/Intermediate/Mart | ✅ Full 3-layer architecture | 15 |
| Incremental models | Performance optimization | ✅ Fact tables incremental | 5 |
| Custom macros | Business logic reuse | ✅ ROAS, eCPM calculations | 5 |
| ERD diagram | Dimensional model | ✅ Star schema visualization | 5 |
| dbt tests | Data quality | ✅ 10+ tests planned | 10 |
| **CI/CD (5 pts)** | | | |
| GitHub Actions | Automated testing | ✅ SQLFluff + dbt tests | 5 |
| **Extra Features (20 pts)** | | | |
| Advanced testing | Custom tests | ⚡ Add if time | 5 |
| Documentation | dbt docs | ✅ Complete documentation | 5 |
| Advanced features | Custom logic | ⚡ Add if time | 10 |

**Projected Score:** 80-85 points (Target: 70+, Pass: 50+)

**Risk Mitigation:**
- Skip PostgreSQL Docker (0 pts) but save 1-2 days
- Those days go to polishing dbt transformations (+10 pts)
- Net gain: -5 pts Docker, +10 pts quality = +5 overall

---

## Files to Create (Priority Order)

**Week 1 (Data Collection):**
1. `sql/setup/create_raw_tables.sql` - Snowflake table definitions
2. `scripts/collect_admob.py` - Batch pipeline
3. `scripts/collect_adjust.py` - Incremental pipeline
4. `scripts/utils/snowflake_client.py` - Reusable connection
5. `.env` - Credentials (gitignored)
6. `scripts/README.md` - Usage documentation

**Week 2 (Transformations):**
7. `models/staging/stg_*.sql` - 3 staging models
8. `models/intermediate/int_*.sql` - 2 intermediate models
9. `models/mart/dim_*.sql` - 3 dimension models
10. `models/mart/fact_*.sql` - 2 fact models
11. `models/schema.yml` - dbt tests + documentation
12. `.github/workflows/dbt_ci.yml` - CI/CD pipeline
13. `.sqlfluff` - SQL linting config

---

## Quick Commands Reference

**Data Collection:**
```bash
# Batch pipeline (AdMob daily)
python scripts/collect_admob.py --days 7

# Incremental pipeline (Adjust hourly)
python scripts/collect_adjust.py --hours 1

# Validate in Snowflake
snowsql -q "SELECT COUNT(*) FROM RAW.ADMOB_DAILY WHERE loaded_at >= CURRENT_DATE"
```

**dbt Workflow:**
```bash
# Test connection
dbt debug

# Run transformations
dbt run

# Run tests
dbt test

# Generate docs
dbt docs generate
dbt docs serve
```

**CI/CD:**
```bash
# Lint SQL
sqlfluff lint models/

# Create PR
git checkout -b feature/add-staging-models
git commit -m "feat: Add staging models for AdMob + Adjust"
git push origin feature/add-staging-models
# GitHub Actions runs automatically
```

---

## Key Decisions Log

**October 22, 2025:**
- ✅ **Architecture:** Skip PostgreSQL Docker, use Snowflake for everything
- ✅ **Rationale:** Simpler (one DB), still passes test, industry-standard
- ✅ **Trade-off:** -5 pts Docker, but +2 days for quality = better overall score

**October 19, 2025:**
- ✅ **Data Sources:** AdMob + Adjust APIs validated and working
- ✅ **Granularity:** Daily (AdMob) + Hourly (Adjust) confirmed
- ✅ **Volume:** 5.7M rows/year manageable in Snowflake

---

## Questions Resolved

**Q: PostgreSQL or Snowflake?**
A: Snowflake only. Simpler, still passes test, saves time.

**Q: Mock data or real APIs?**
A: Start with real APIs (already validated and working).

**Q: Which pipeline first?**
A: AdMob batch (simpler) → then Adjust incremental.

**Q: How to handle API failures?**
A: Error handling + retry logic + logging in collection scripts.

---

**Next Action:** Create `sql/setup/create_raw_tables.sql` and define RAW schema tables
**First Command:** `mkdir -p sql/setup && touch sql/setup/create_raw_tables.sql`
