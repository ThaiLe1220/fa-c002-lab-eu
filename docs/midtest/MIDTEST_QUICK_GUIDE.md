# Mid-Course Test Demo Guide

**Duration**: 20 minutes

---

## 1. Git Workflow (2 min)

### Terminal Commands
```bash
# Show branch structure
git branch
git log --oneline -10

# Show feature branch commits
git log --graph --oneline --all -15
```

### What to Say
- "Feature branch workflow for all development"
- "Clean commit history with meaningful messages"
- "Ready for pull request workflow"

**Snowflake Check**: None needed

---

## 2. Data Collection (3 min)

### Terminal Commands
```bash
# Show collection scripts exist
ls -la scripts/collect_*midtest.py

# Run realtime collection (demo mode - 10-20 rows)
python scripts/collect_admob_midtest.py --realtime
python scripts/collect_adjust_midtest.py --realtime
```

### Snowflake Validation
```sql
USE ROLE RL_T34;
USE WAREHOUSE WH_T34;
USE SCHEMA DB_T34.RAW_MIDTEST;

-- Show fresh data just loaded
SELECT COUNT(*), MAX(LOADED_AT) AS latest_load
FROM ADMOB_DAILY_MIDTEST;

SELECT COUNT(*), MAX(LOADED_AT) AS latest_load
FROM ADJUST_DAILY_MIDTEST;
```

### What to Say
- "Two data sources: AdMob (revenue) and Adjust (user metrics)"
- "Realtime mode shows staggered loaded_at timestamps"
- "UUID tracking for data lineage"
- "Data altered ±50% for demo repeatability"

---

## 3. dbt Pipeline (10 min)

### Terminal Commands
```bash
# Show project structure
tree my_dbt_project/models -L 2

# Run models
dbt run

# Run tests
dbt test
```

### Snowflake Validation (after dbt run)
```sql
USE SCHEMA DB_T34.PUBLIC;

-- 1. Check staging views
SELECT COUNT(*) FROM STG_ADMOB_MIDTEST;
SELECT COUNT(*) FROM STG_ADJUST_MIDTEST;

-- 2. Check intermediate incremental
SELECT COUNT(*), MIN(DATE), MAX(DATE)
FROM INT_APP_DAILY_METRICS;

-- 3. Check dimensions
SELECT * FROM DIM_APPS;  -- 3 apps
SELECT * FROM DIM_DATES ORDER BY DATE;  -- 7 dates

-- 4. Check fact table (star schema)
SELECT COUNT(*) FROM FCT_APP_DAILY_PERFORMANCE;

-- 5. Show business query (revenue by app)
SELECT
    a.app_name,
    SUM(f.ad_revenue) AS total_revenue,
    SUM(f.installs) AS total_installs,
    AVG(f.ad_ctr) AS avg_ctr
FROM FCT_APP_DAILY_PERFORMANCE f
JOIN DIM_APPS a ON f.app_key = a.app_key
GROUP BY a.app_name
ORDER BY total_revenue DESC;
```

### What to Say

**3-Layer Architecture**:
- "Staging: Clean raw data from AdMob and Adjust"
- "Intermediate: Join sources, incremental processing"
- "Mart: Star schema for analytics"

**Incremental Model**:
- "INT_APP_DAILY_METRICS uses incremental materialization"
- "unique_key on [app_store_id, date, country_code]"
- "Only processes new dates, not full refresh"

**Star Schema**:
- "1 fact table: FCT_APP_DAILY_PERFORMANCE"
- "2 dimensions: DIM_APPS, DIM_DATES"
- "Surrogate keys with dbt_utils"
- "Relationship tests validate foreign keys"

**Custom Macro**:
- "calculate_ctr macro for Click-Through Rate"
- "Reusable logic across models"

**Data Quality**:
- "27 passing tests"
- "not_null, unique, relationships tests"
- "Modern data_tests syntax (dbt 1.10+)"

---

## 4. CI/CD (2 min)

### Terminal Commands
```bash
# Show GitHub Actions workflow
cat .github/workflows/dbt_ci.yml

# Show SQLFluff config
cat .sqlfluff
```

### What to Say
- "3 automated checks: SQLFluff linting + dbt run + dbt test"
- "Runs on push/PR to main and develop branches"
- "SQLFluff enforces Snowflake SQL standards"

**Snowflake Check**: None needed

---

## 5. ERD (1 min)

### Terminal Commands
```bash
# Open ERD in browser
open docs/midtest/ERD_STAR_SCHEMA.md
```

### What to Say
- "Star schema dimensional modeling"
- "Fact table at center with metrics"
- "Dimensions for apps and dates"
- "Surrogate keys for stable relationships"
- "Supports revenue, install, and performance analysis"

---

## 6. Quick Validation Summary (2 min)

### Terminal Commands
```bash
# Show all deliverables
cat docs/midtest/PROGRESS.md
```

### Snowflake Final Check
```sql
-- Show row counts match expectations
SELECT 'DIM_APPS' AS table_name, COUNT(*) AS rows FROM DIM_APPS
UNION ALL
SELECT 'DIM_DATES', COUNT(*) FROM DIM_DATES
UNION ALL
SELECT 'INT_APP_DAILY_METRICS', COUNT(*) FROM INT_APP_DAILY_METRICS
UNION ALL
SELECT 'FCT_APP_DAILY_PERFORMANCE', COUNT(*) FROM FCT_APP_DAILY_PERFORMANCE;
```

---

## Key Points to Emphasize

✅ **3-layer architecture** (staging → intermediate → mart)
✅ **Incremental model** with unique_key
✅ **Star schema** with proper dimensional modeling
✅ **27 passing tests** ensuring data quality
✅ **Custom macro** (calculate_ctr)
✅ **Course-aligned patterns** (dbt_utils, modern syntax)
✅ **CI/CD pipeline** with SQLFluff + dbt run + dbt test

---

## Scoring Breakdown

| Section | Points | Evidence |
|---------|--------|----------|
| Data Ingestion | 20/35 | Git workflow + Python pipelines + Snowflake |
| Data Transformation | 40/40 | 6 models + 27 tests + incremental + macro + ERD |
| CI/CD | 5/5 | GitHub Actions with 3 checks |
| Documentation | 10/10 | ERD + methodology explained |
| **TOTAL** | **75/100** | **PASS + GRADUATION TRACK** |

---

## Troubleshooting

**If dbt run fails**:
```bash
dbt run --full-refresh  # Rebuild incremental models
```

**If data collection fails**:
- Check .secret/.env has ADJUST_TOKEN
- Check .secret/token_*.pickle exists for AdMob
- Verify Snowflake connection works

**If Snowflake queries fail**:
```sql
-- Verify you're in correct schema
USE ROLE RL_T34;
USE WAREHOUSE WH_T34;
USE SCHEMA DB_T34.PUBLIC;
```

---

## Quick Pre-Demo Checklist

- [ ] Snowflake accessible
- [ ] GitHub repository accessible
- [ ] Terminal ready with commands
- [ ] ERD diagram open in browser
- [ ] Confidence HIGH!

**Status**: READY TO SHIP! 🚀
