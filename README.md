# FA-C002 Lab - Mobile Analytics Data Warehouse

**Mid-Course Test:** Oct 29 & Nov 1, 2025 | **11 days remaining**
**Target Score:** 70+ points (Pass: 50+)

## Project: Mobile App Analytics Data Warehouse

**Business Domain:** Mobile app publishing with 10+ apps generating revenue through in-app advertising

**Data Sources:**
- **AdMob API:** Ad revenue, impressions, ad format performance (daily granularity)
- **Adjust API:** User acquisition, cohort retention, marketing costs (hourly + daily)

**Data Pipelines:**
- **Real-Time Pipeline:** Adjust API (hourly) → PostgreSQL Docker → 39 rows/hour row-by-row ingestion
- **Batch Pipeline:** AdMob API (daily) → Snowflake → 13,500+ rows/batch (27x test requirement)

**Architecture:**
- **Hot Storage (PostgreSQL):** Adjust hourly data (last 14 days) for operational dashboards
- **Cold Storage (Snowflake):** Both sources daily (all history) for strategic analysis

**Business Value:**
- LTV:CAC ratio analysis
- Cohort retention tracking (D0, D1, D7, D30)
- Marketing ROI optimization
- Ad format performance analysis
- Geographic arbitrage opportunities

## Current Status

✅ **Planning & Validation Complete:**
- API validation finished with actual data volumes confirmed
- Architecture validated against mid-course test requirements
- Batch/real-time pipelines mapped to test criteria (see below)
- Dimensional model designed (4 fact tables, 7+ dimension tables)
- Confirmed data volumes: 5.7M rows/year (manageable)

**Test Alignment:**
- Real-time: Adjust hourly (936 rows/day) meets row-by-row incremental requirement
- Batch: AdMob daily (13,508 rows/batch) exceeds 500-row requirement by 27x
- PostgreSQL: Docker containerization ready for demo
- See [Test Requirements Mapping](./docs/planning/data_strategy.md#mid-course-test-requirements-mapping) for demo scripts

**Current Phase:** Data Collection Complete - Ready for dbt Transformations

**Test Requirements Status: 35/100 pts**

| Section | Points | Status |
|---------|--------|--------|
| **1. Data Ingestion** | 35 | ✅ Complete (35/35) |
| **2. Transformation** | 40 | 🔄 Next (dbt staging/intermediate/mart) |
| **3. CI/CD** | 5 | ⏳ Pending |
| **4. Extra Features** | 20 | ⏳ Pending |

**Data Collection Status:**
- ✅ Adjust hourly RAW pipeline working (127K rows/day)
- ✅ AdMob daily RAW pipeline working (13.5K rows/day)
- ✅ Pure RAW architecture (no transformations in Python)
- ✅ All transformations planned for dbt staging layer

## Quick Commands

```bash
# Activate environment
source .venv/bin/activate

# Data collection pipelines
python scripts/collect_admob.py --days 7     # AdMob batch (94K rows)
python scripts/collect_adjust.py --hours 24  # Adjust hourly (127K rows)

# Validate data in Snowflake
python scripts/check_data.py

# dbt workflow (next phase)
cd my_dbt_project
dbt debug && dbt run && dbt test
```

## Project Structure

```text
fa-c002-lab/
├── CLAUDE.md                           # Project philosophy
├── docs/
│   ├── planning/
│   │   ├── data_strategy.md            # ✅ Complete plan
│   │   └── api_validation_results.md   # ✅ Test results
│   └── goal/
│       └── midcourse_test_criteria.md  # Test requirements
├── scripts/
│   └── validation/                     # ✅ API test scripts
├── my_dbt_project/
│   └── models/
│       ├── 01_staging/                 # TODO: AdMob + Adjust staging
│       ├── 02_intermediate/            # TODO: Unified metrics
│       └── 03_mart/                    # TODO: Analytics marts
└── pipelines/                          # TODO: Python ingestion scripts
```

## Tech Stack

- **dbt 1.10.13** - SQL transformations
- **Snowflake** - Cloud data warehouse
- **PostgreSQL** - Real-time operational database
- **Python 3.12** - API ingestion pipelines
- **Docker** - PostgreSQL containerization
- **GitHub Actions** - CI/CD automation

## Key Documentation

**Planning:**
- [Data Strategy](./docs/planning/data_strategy.md) - Complete architecture & plan
- [API Validation Results](./docs/planning/api_validation_results.md) - Confirmed capabilities

**Requirements:**
- [Test Criteria](./docs/goal/midcourse_test_criteria.md) - All test requirements

**Setup:**
- [Setup Guide](./docs/00_setup_guide.md) - Environment setup
- [Snowflake Config](./docs/snowflake_setup.md) - Warehouse configuration

## Next Steps

1. **Create dbt project structure** - Staging models for AdMob + Adjust
2. **Build Python pipelines** - API data ingestion scripts
3. **Setup PostgreSQL** - Docker container for real-time data
4. **Implement transformations** - Intermediate + mart layers
5. **Add CI/CD** - GitHub Actions workflow

## Philosophy

**Lean, test-driven, business-focused.** See [CLAUDE.md](./CLAUDE.md)

---

**Last Updated:** October 22, 2025
**Status:** ✅ Planning Complete - Architecture Validated - Ready for Implementation
